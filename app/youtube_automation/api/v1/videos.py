"""
Video Management API Endpoints
YouTube Automation System v3.0

Copyright (c) 2025 Saeed Alaediny. All rights reserved.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from core.database import get_db
from core.auth import get_current_active_user
from models.database import User, Channel, Video, VideoStatus
from schemas.videos import (
    VideoCreate,
    VideoUpdate,
    VideoGenerateRequest,
    VideoUploadRequest,
    VideoResponse,
    VideoListResponse,
    VideoProgressResponse
)

router = APIRouter()

@router.post("/", response_model=VideoResponse, status_code=status.HTTP_201_CREATED)
async def create_video(
    video_data: VideoCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new video
    
    Args:
        video_data: Video creation data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        VideoResponse: Created video
        
    Raises:
        HTTPException: If channel not found or unauthorized
    """
    # Verify channel ownership
    channel = db.query(Channel).filter(
        Channel.id == video_data.channel_id,
        Channel.owner_id == current_user.id
    ).first()
    
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )
    
    # Create new video
    new_video = Video(
        title=video_data.title,
        description=video_data.description,
        channel_id=video_data.channel_id,
        metadata=video_data.metadata or {},
        status=VideoStatus.DRAFT,
        generation_progress=0
    )
    
    db.add(new_video)
    db.commit()
    db.refresh(new_video)
    
    return new_video

@router.get("/", response_model=VideoListResponse)
async def list_videos(
    channel_id: Optional[int] = Query(None, description="Filter by channel ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List videos
    
    Args:
        channel_id: Filter by channel ID
        status: Filter by status
        skip: Number of records to skip
        limit: Number of records to return
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        VideoListResponse: List of videos
    """
    # Build query
    query = db.query(Video).join(Channel).filter(Channel.owner_id == current_user.id)
    
    # Apply filters
    if channel_id:
        # Verify channel ownership
        channel = db.query(Channel).filter(
            Channel.id == channel_id,
            Channel.owner_id == current_user.id
        ).first()
        
        if not channel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Channel not found"
            )
        
        query = query.filter(Video.channel_id == channel_id)
    
    if status:
        try:
            video_status = VideoStatus(status)
            query = query.filter(Video.status == video_status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status}"
            )
    
    # Get total count
    total = query.count()
    
    # Get paginated results
    videos = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "videos": videos
    }

@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get video details
    
    Args:
        video_id: Video ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        VideoResponse: Video details
        
    Raises:
        HTTPException: If video not found or unauthorized
    """
    video = db.query(Video).join(Channel).filter(
        Video.id == video_id,
        Channel.owner_id == current_user.id
    ).first()
    
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    return video

@router.put("/{video_id}", response_model=VideoResponse)
async def update_video(
    video_id: int,
    video_data: VideoUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update video
    
    Args:
        video_id: Video ID
        video_data: Video update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        VideoResponse: Updated video
        
    Raises:
        HTTPException: If video not found or unauthorized
    """
    video = db.query(Video).join(Channel).filter(
        Video.id == video_id,
        Channel.owner_id == current_user.id
    ).first()
    
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    # Update fields
    update_data = video_data.dict(exclude_unset=True)
    
    # Validate status if provided
    if "status" in update_data:
        try:
            update_data["status"] = VideoStatus(update_data["status"])
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {update_data['status']}"
            )
    
    for field, value in update_data.items():
        setattr(video, field, value)
    
    video.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(video)
    
    return video

@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_video(
    video_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete video
    
    Args:
        video_id: Video ID
        current_user: Current authenticated user
        db: Database session
        
    Raises:
        HTTPException: If video not found or unauthorized
    """
    video = db.query(Video).join(Channel).filter(
        Video.id == video_id,
        Channel.owner_id == current_user.id
    ).first()
    
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    db.delete(video)
    db.commit()
    
    return None

@router.post("/{video_id}/generate", response_model=VideoProgressResponse)
async def generate_video(
    video_id: int,
    generate_data: VideoGenerateRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Generate video (async task)
    
    Args:
        video_id: Video ID
        generate_data: Video generation parameters
        background_tasks: FastAPI background tasks
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        VideoProgressResponse: Generation progress
        
    Raises:
        HTTPException: If video not found or unauthorized
    """
    video = db.query(Video).join(Channel).filter(
        Video.id == video_id,
        Channel.owner_id == current_user.id
    ).first()
    
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    # Check if video is already being generated
    if video.status == VideoStatus.GENERATING:
        return {
            "video_id": video.id,
            "status": video.status.value,
            "progress": video.generation_progress,
            "message": "Video generation in progress"
        }
    
    # Update video status
    video.status = VideoStatus.GENERATING
    video.generation_progress = 0
    db.commit()
    
    # TODO: Queue Celery task for video generation
    # For now, return a stub response
    
    return {
        "video_id": video.id,
        "status": video.status.value,
        "progress": 0,
        "message": "Video generation queued (STUB - Celery task not implemented yet)"
    }

@router.get("/{video_id}/progress", response_model=VideoProgressResponse)
async def get_video_progress(
    video_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get video generation progress
    
    Args:
        video_id: Video ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        VideoProgressResponse: Generation progress
        
    Raises:
        HTTPException: If video not found or unauthorized
    """
    video = db.query(Video).join(Channel).filter(
        Video.id == video_id,
        Channel.owner_id == current_user.id
    ).first()
    
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    return {
        "video_id": video.id,
        "status": video.status.value,
        "progress": video.generation_progress,
        "message": f"Video is {video.status.value}",
        "error": video.error_message
    }

@router.post("/{video_id}/upload", response_model=VideoResponse)
async def upload_video(
    video_id: int,
    upload_data: VideoUploadRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload video to YouTube (async task)
    
    Args:
        video_id: Video ID
        upload_data: Upload parameters
        background_tasks: FastAPI background tasks
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        VideoResponse: Updated video
        
    Raises:
        HTTPException: If video not found, unauthorized, or not generated
    """
    video = db.query(Video).join(Channel).filter(
        Video.id == video_id,
        Channel.owner_id == current_user.id
    ).first()
    
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    if video.status != VideoStatus.GENERATED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Video must be generated before uploading"
        )
    
    # Update video status
    video.status = VideoStatus.UPLOADING
    db.commit()
    db.refresh(video)
    
    # TODO: Queue Celery task for YouTube upload
    # For now, return a stub response
    
    return video

