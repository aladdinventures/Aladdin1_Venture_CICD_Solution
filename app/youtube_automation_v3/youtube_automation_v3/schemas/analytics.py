"""
Analytics Schemas
YouTube Automation System v3.0

Copyright (c) 2025 Saeed Alaediny. All rights reserved.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class VideoAnalyticsResponse(BaseModel):
    """Video analytics response schema"""
    id: int
    video_id: int
    views: int
    likes: int
    dislikes: int
    comments: int
    shares: int
    watch_time: int
    average_view_duration: float
    click_through_rate: float
    engagement_rate: float
    revenue: float
    last_updated: datetime
    
    class Config:
        from_attributes = True

class ChannelAnalyticsResponse(BaseModel):
    """Channel analytics response schema"""
    channel_id: int
    total_videos: int
    total_views: int
    total_likes: int
    total_comments: int
    total_watch_time: int
    average_engagement_rate: float
    total_revenue: float
    top_performing_video: Optional[dict] = None
    recent_performance: list[dict] = []

class AnalyticsSummaryResponse(BaseModel):
    """Analytics summary response schema"""
    total_channels: int
    total_videos: int
    total_views: int
    total_revenue: float
    average_engagement_rate: float

