"""
Video Generation and Upload Tasks
YouTube Automation System v3.0

Copyright (c) 2025 Saeed Alaediny. All rights reserved.
"""

from celery import Task
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from tasks.celery_app import celery_app
from core.database import SessionLocal
from models.database import Video, Channel, VideoStatus, ChannelStatus
from services.content import ContentGeneratorService
from services.video import VideoBuilderService
from services.upload import YouTubeUploaderService

logger = logging.getLogger(__name__)

class DatabaseTask(Task):
    """Base task with database session management"""
    _db = None
    
    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = SessionLocal()
        return self._db
    
    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()
            self._db = None

@celery_app.task(base=DatabaseTask, bind=True)
def generate_video_task(self, video_id: int):
    """
    Generate video content (Celery task)
    
    Args:
        video_id: Video ID
    """
    logger.info(f"Starting video generation for video_id={video_id}")
    
    try:
        # Get video from database
        video = self.db.query(Video).filter(Video.id == video_id).first()
        
        if not video:
            logger.error(f"Video not found: video_id={video_id}")
            return {"status": "error", "message": "Video not found"}
        
        # Update status
        video.status = VideoStatus.GENERATING
        video.generation_progress = 0
        self.db.commit()
        
        # Initialize services
        content_service = ContentGeneratorService()
        video_service = VideoBuilderService()
        
        # Progress callback
        def update_progress(progress: int, message: str):
            video.generation_progress = progress
            self.db.commit()
            logger.info(f"Video {video_id} progress: {progress}% - {message}")
        
        # Generate script if not exists
        if not video.script:
            logger.info(f"Generating script for video_id={video_id}")
            script_data = content_service.generate_script(
                title=video.title,
                description=video.description or "",
                duration=video.metadata.get("duration", 300) if video.metadata else 300
            )
            video.script = script_data["script"]
            self.db.commit()
        
        # Generate video
        logger.info(f"Building video for video_id={video_id}")
        video_result = video_service.generate_video(
            video_id=video.id,
            script=video.script,
            title=video.title,
            duration=video.metadata.get("duration", 300) if video.metadata else 300,
            progress_callback=update_progress
        )
        
        # Update video record
        video.video_path = video_result["video_path"]
        video.thumbnail_path = video_result["thumbnail_path"]
        video.duration = video_result["duration"]
        video.file_size = video_result["file_size"]
        video.status = VideoStatus.GENERATED
        video.generation_progress = 100
        video.updated_at = datetime.utcnow()
        self.db.commit()
        
        logger.info(f"Video generation completed: video_id={video_id}")
        
        return {
            "status": "success",
            "video_id": video_id,
            "video_path": video.video_path,
            "duration": video.duration
        }
    
    except Exception as e:
        logger.error(f"Video generation failed: video_id={video_id}, error={str(e)}", exc_info=True)
        
        # Update video status
        video = self.db.query(Video).filter(Video.id == video_id).first()
        if video:
            video.status = VideoStatus.FAILED
            video.error_message = str(e)
            self.db.commit()
        
        return {
            "status": "error",
            "video_id": video_id,
            "message": str(e)
        }

@celery_app.task(base=DatabaseTask, bind=True)
def upload_video_task(self, video_id: int, privacy_status: str = "public", notify_subscribers: bool = True):
    """
    Upload video to YouTube (Celery task)
    
    Args:
        video_id: Video ID
        privacy_status: Privacy status
        notify_subscribers: Notify subscribers
    """
    logger.info(f"Starting video upload for video_id={video_id}")
    
    try:
        # Get video from database
        video = self.db.query(Video).filter(Video.id == video_id).first()
        
        if not video:
            logger.error(f"Video not found: video_id={video_id}")
            return {"status": "error", "message": "Video not found"}
        
        if video.status != VideoStatus.GENERATED:
            logger.error(f"Video not generated: video_id={video_id}, status={video.status}")
            return {"status": "error", "message": "Video must be generated before uploading"}
        
        # Update status
        video.status = VideoStatus.UPLOADING
        self.db.commit()
        
        # Initialize uploader service
        uploader_service = YouTubeUploaderService()
        
        # Prepare metadata
        tags = video.metadata.get("tags", []) if video.metadata else []
        category_id = video.metadata.get("category_id", "22") if video.metadata else "22"
        
        # Upload video
        logger.info(f"Uploading video to YouTube: video_id={video_id}")
        upload_result = uploader_service.upload_video(
            video_path=video.video_path,
            title=video.title,
            description=video.description or "",
            tags=tags,
            category_id=category_id,
            privacy_status=privacy_status,
            thumbnail_path=video.thumbnail_path,
            notify_subscribers=notify_subscribers
        )
        
        # Update video record
        video.youtube_video_id = upload_result["youtube_video_id"]
        video.status = VideoStatus.UPLOADED
        video.published_at = datetime.utcnow()
        video.updated_at = datetime.utcnow()
        self.db.commit()
        
        logger.info(f"Video upload completed: video_id={video_id}, youtube_id={video.youtube_video_id}")
        
        return {
            "status": "success",
            "video_id": video_id,
            "youtube_video_id": video.youtube_video_id,
            "url": upload_result["url"]
        }
    
    except Exception as e:
        logger.error(f"Video upload failed: video_id={video_id}, error={str(e)}", exc_info=True)
        
        # Update video status
        video = self.db.query(Video).filter(Video.id == video_id).first()
        if video:
            video.status = VideoStatus.FAILED
            video.error_message = str(e)
            self.db.commit()
        
        return {
            "status": "error",
            "video_id": video_id,
            "message": str(e)
        }

@celery_app.task(base=DatabaseTask, bind=True)
def auto_generate_videos(self):
    """
    Auto-generate videos for channels with auto_generate enabled
    """
    logger.info("Starting auto-generation task")
    
    try:
        # Find channels with auto_generate enabled
        channels = self.db.query(Channel).filter(
            Channel.auto_generate == True,
            Channel.status == ChannelStatus.ACTIVE
        ).all()
        
        logger.info(f"Found {len(channels)} channels with auto-generation enabled")
        
        generated_count = 0
        
        for channel in channels:
            try:
                # Initialize content service
                content_service = ContentGeneratorService()
                
                # Generate video content
                content = content_service.generate_complete_video_content(
                    niche=channel.niche,
                    duration=channel.settings.get("default_duration", 300) if channel.settings else 300
                )
                
                # Create video record
                new_video = Video(
                    title=content["title"],
                    description=content["description"],
                    script=content["script"],
                    channel_id=channel.id,
                    metadata={
                        "tags": content.get("tags", []),
                        "category": content.get("category", "Education"),
                        "duration": content.get("estimated_duration", 300)
                    },
                    status=VideoStatus.DRAFT
                )
                
                self.db.add(new_video)
                self.db.commit()
                self.db.refresh(new_video)
                
                # Queue video generation task
                generate_video_task.delay(new_video.id)
                
                generated_count += 1
                logger.info(f"Queued video generation for channel_id={channel.id}, video_id={new_video.id}")
            
            except Exception as e:
                logger.error(f"Failed to auto-generate for channel_id={channel.id}: {str(e)}", exc_info=True)
                continue
        
        logger.info(f"Auto-generation task completed: {generated_count} videos queued")
        
        return {
            "status": "success",
            "channels_processed": len(channels),
            "videos_queued": generated_count
        }
    
    except Exception as e:
        logger.error(f"Auto-generation task failed: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": str(e)
        }

@celery_app.task(base=DatabaseTask, bind=True)
def auto_upload_videos(self):
    """
    Auto-upload generated videos for channels with auto_upload enabled
    """
    logger.info("Starting auto-upload task")
    
    try:
        # Find channels with auto_upload enabled
        channels = self.db.query(Channel).filter(
            Channel.auto_upload == True,
            Channel.status == ChannelStatus.ACTIVE
        ).all()
        
        logger.info(f"Found {len(channels)} channels with auto-upload enabled")
        
        uploaded_count = 0
        
        for channel in channels:
            try:
                # Find generated videos for this channel
                videos = self.db.query(Video).filter(
                    Video.channel_id == channel.id,
                    Video.status == VideoStatus.GENERATED
                ).limit(1).all()  # Upload one video at a time
                
                for video in videos:
                    # Queue upload task
                    upload_video_task.delay(video.id)
                    uploaded_count += 1
                    logger.info(f"Queued video upload for channel_id={channel.id}, video_id={video.id}")
            
            except Exception as e:
                logger.error(f"Failed to auto-upload for channel_id={channel.id}: {str(e)}", exc_info=True)
                continue
        
        logger.info(f"Auto-upload task completed: {uploaded_count} videos queued")
        
        return {
            "status": "success",
            "channels_processed": len(channels),
            "videos_queued": uploaded_count
        }
    
    except Exception as e:
        logger.error(f"Auto-upload task failed: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": str(e)
        }

