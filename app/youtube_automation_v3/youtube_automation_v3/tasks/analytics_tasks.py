"""
Analytics Synchronization Tasks
YouTube Automation System v3.0

Copyright (c) 2025 Saeed Alaediny. All rights reserved.
"""

from celery import Task
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from tasks.celery_app import celery_app
from core.database import SessionLocal
from models.database import Video, VideoAnalytics, VideoStatus
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
def sync_video_analytics(self, video_id: int):
    """
    Sync analytics for a single video
    
    Args:
        video_id: Video ID
    """
    logger.info(f"Syncing analytics for video_id={video_id}")
    
    try:
        # Get video from database
        video = self.db.query(Video).filter(Video.id == video_id).first()
        
        if not video:
            logger.error(f"Video not found: video_id={video_id}")
            return {"status": "error", "message": "Video not found"}
        
        if video.status != VideoStatus.UPLOADED or not video.youtube_video_id:
            logger.warning(f"Video not uploaded: video_id={video_id}")
            return {"status": "skipped", "message": "Video not uploaded"}
        
        # Initialize uploader service
        uploader_service = YouTubeUploaderService()
        
        # Fetch analytics from YouTube
        logger.info(f"Fetching analytics from YouTube: video_id={video_id}, youtube_id={video.youtube_video_id}")
        analytics_data = uploader_service.get_video_analytics(video.youtube_video_id)
        
        # Get or create analytics record
        analytics = self.db.query(VideoAnalytics).filter(VideoAnalytics.video_id == video_id).first()
        
        if not analytics:
            analytics = VideoAnalytics(video_id=video_id)
            self.db.add(analytics)
        
        # Update analytics
        analytics.views = analytics_data["views"]
        analytics.likes = analytics_data["likes"]
        analytics.dislikes = analytics_data["dislikes"]
        analytics.comments = analytics_data["comments"]
        analytics.shares = analytics_data["shares"]
        analytics.watch_time = analytics_data["watch_time"]
        analytics.average_view_duration = analytics_data["average_view_duration"]
        analytics.click_through_rate = analytics_data["click_through_rate"]
        analytics.engagement_rate = analytics_data["engagement_rate"]
        analytics.revenue = analytics_data["revenue"]
        analytics.last_updated = datetime.utcnow()
        
        self.db.commit()
        
        logger.info(f"Analytics synced successfully: video_id={video_id}, views={analytics.views}")
        
        return {
            "status": "success",
            "video_id": video_id,
            "views": analytics.views,
            "engagement_rate": analytics.engagement_rate
        }
    
    except Exception as e:
        logger.error(f"Analytics sync failed: video_id={video_id}, error={str(e)}", exc_info=True)
        return {
            "status": "error",
            "video_id": video_id,
            "message": str(e)
        }

@celery_app.task(base=DatabaseTask, bind=True)
def sync_all_analytics(self):
    """
    Sync analytics for all uploaded videos
    """
    logger.info("Starting analytics sync for all videos")
    
    try:
        # Find all uploaded videos
        videos = self.db.query(Video).filter(
            Video.status == VideoStatus.UPLOADED,
            Video.youtube_video_id.isnot(None)
        ).all()
        
        logger.info(f"Found {len(videos)} uploaded videos to sync")
        
        synced_count = 0
        failed_count = 0
        
        for video in videos:
            try:
                # Queue individual sync task
                result = sync_video_analytics.delay(video.id)
                synced_count += 1
            except Exception as e:
                logger.error(f"Failed to queue sync for video_id={video.id}: {str(e)}")
                failed_count += 1
        
        logger.info(f"Analytics sync completed: {synced_count} queued, {failed_count} failed")
        
        return {
            "status": "success",
            "total_videos": len(videos),
            "synced": synced_count,
            "failed": failed_count
        }
    
    except Exception as e:
        logger.error(f"Analytics sync failed: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": str(e)
        }

