"""
Video Schemas
YouTube Automation System v3.0

Copyright (c) 2025 Saeed Alaediny. All rights reserved.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime

class VideoCreate(BaseModel):
    """Video creation schema"""
    title: str = Field(..., min_length=1, max_length=255, description="Video title")
    description: Optional[str] = Field(None, description="Video description")
    channel_id: int = Field(..., description="Channel ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Video metadata (tags, category, etc.)")

class VideoUpdate(BaseModel):
    """Video update schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    script: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    status: Optional[str] = Field(None, description="Video status")

class VideoGenerateRequest(BaseModel):
    """Video generation request schema"""
    prompt: Optional[str] = Field(None, description="Custom prompt for content generation")
    duration: Optional[int] = Field(None, ge=30, le=3600, description="Video duration in seconds")
    voice: Optional[str] = Field(None, description="TTS voice to use")

class VideoUploadRequest(BaseModel):
    """Video upload request schema"""
    privacy: str = Field(default="public", description="Video privacy (public, unlisted, private)")
    notify_subscribers: bool = Field(default=True, description="Notify subscribers")
    made_for_kids: bool = Field(default=False, description="Made for kids")

class VideoResponse(BaseModel):
    """Video response schema"""
    id: int
    title: str
    description: Optional[str]
    script: Optional[str]
    status: str
    youtube_video_id: Optional[str]
    duration: Optional[int]
    generation_progress: int
    channel_id: int
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class VideoListResponse(BaseModel):
    """Video list response schema"""
    total: int
    videos: list[VideoResponse]

class VideoProgressResponse(BaseModel):
    """Video generation progress response schema"""
    video_id: int
    status: str
    progress: int
    message: str
    error: Optional[str] = None

