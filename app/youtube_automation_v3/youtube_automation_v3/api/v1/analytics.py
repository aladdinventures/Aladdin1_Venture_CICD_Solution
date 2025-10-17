"""
Analytics API Endpoints
YouTube Automation System v3.0

Copyright (c) 2025 Saeed Alaediny. All rights reserved.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from core.database import get_db
from core.auth import get_current_active_user
from models.database import User, Channel, Video, VideoAnalytics
from schemas.analytics import (
    VideoAnalyticsResponse,
    ChannelAnalyticsResponse,
    AnalyticsSummaryResponse
)

router = APIRouter()

@router.get("/video/{video_id}", response_model=VideoAnalyticsResponse)
async def get_video_analytics(
    video_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get video analytics
    
    Args:
        video_id: Video ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        VideoAnalyticsResponse: Video analytics
        
    Raises:
        HTTPException: If video not found or unauthorized
    """
    # Verify video ownership
    video = db.query(Video).join(Channel).filter(
        Video.id == video_id,
        Channel.owner_id == current_user.id
    ).first()
    
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    # Get or create analytics
    analytics = db.query(VideoAnalytics).filter(VideoAnalytics.video_id == video_id).first()
    
    if not analytics:
        # Create analytics record if it doesn't exist
        analytics = VideoAnalytics(video_id=video_id)
        db.add(analytics)
        db.commit()
        db.refresh(analytics)
    
    return analytics

@router.get("/channel/{channel_id}", response_model=ChannelAnalyticsResponse)
async def get_channel_analytics(
    channel_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get channel analytics
    
    Args:
        channel_id: Channel ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        ChannelAnalyticsResponse: Channel analytics
        
    Raises:
        HTTPException: If channel not found or unauthorized
    """
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
    
    # Get channel videos
    videos = db.query(Video).filter(Video.channel_id == channel_id).all()
    
    # Calculate aggregated analytics
    total_videos = len(videos)
    total_views = 0
    total_likes = 0
    total_comments = 0
    total_watch_time = 0
    total_revenue = 0.0
    engagement_rates = []
    
    top_video = None
    max_views = 0
    
    recent_performance = []
    
    for video in videos:
        analytics = db.query(VideoAnalytics).filter(VideoAnalytics.video_id == video.id).first()
        
        if analytics:
            total_views += analytics.views
            total_likes += analytics.likes
            total_comments += analytics.comments
            total_watch_time += analytics.watch_time
            total_revenue += analytics.revenue
            
            if analytics.engagement_rate > 0:
                engagement_rates.append(analytics.engagement_rate)
            
            # Track top performing video
            if analytics.views > max_views:
                max_views = analytics.views
                top_video = {
                    "video_id": video.id,
                    "title": video.title,
                    "views": analytics.views,
                    "engagement_rate": analytics.engagement_rate
                }
            
            # Recent performance (last 10 videos)
            if len(recent_performance) < 10:
                recent_performance.append({
                    "video_id": video.id,
                    "title": video.title,
                    "views": analytics.views,
                    "likes": analytics.likes,
                    "engagement_rate": analytics.engagement_rate
                })
    
    # Calculate average engagement rate
    avg_engagement = sum(engagement_rates) / len(engagement_rates) if engagement_rates else 0.0
    
    return {
        "channel_id": channel_id,
        "total_videos": total_videos,
        "total_views": total_views,
        "total_likes": total_likes,
        "total_comments": total_comments,
        "total_watch_time": total_watch_time,
        "average_engagement_rate": avg_engagement,
        "total_revenue": total_revenue,
        "top_performing_video": top_video,
        "recent_performance": recent_performance
    }

@router.get("/summary", response_model=AnalyticsSummaryResponse)
async def get_analytics_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get overall analytics summary for user
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        AnalyticsSummaryResponse: Analytics summary
    """
    # Get user's channels
    channels = db.query(Channel).filter(Channel.owner_id == current_user.id).all()
    total_channels = len(channels)
    
    # Get all videos across all channels
    channel_ids = [c.id for c in channels]
    videos = db.query(Video).filter(Video.channel_id.in_(channel_ids)).all() if channel_ids else []
    total_videos = len(videos)
    
    # Calculate aggregated metrics
    total_views = 0
    total_revenue = 0.0
    engagement_rates = []
    
    for video in videos:
        analytics = db.query(VideoAnalytics).filter(VideoAnalytics.video_id == video.id).first()
        
        if analytics:
            total_views += analytics.views
            total_revenue += analytics.revenue
            
            if analytics.engagement_rate > 0:
                engagement_rates.append(analytics.engagement_rate)
    
    # Calculate average engagement rate
    avg_engagement = sum(engagement_rates) / len(engagement_rates) if engagement_rates else 0.0
    
    return {
        "total_channels": total_channels,
        "total_videos": total_videos,
        "total_views": total_views,
        "total_revenue": total_revenue,
        "average_engagement_rate": avg_engagement
    }

