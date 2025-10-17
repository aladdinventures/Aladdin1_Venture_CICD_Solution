"""
Channel Schemas
YouTube Automation System v3.0

Copyright (c) 2025 Saeed Alaediny. All rights reserved.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime

class ChannelCreate(BaseModel):
    """Channel creation schema"""
    name: str = Field(..., min_length=1, max_length=255, description="Channel name")
    description: Optional[str] = Field(None, description="Channel description")
    niche: Optional[str] = Field(None, max_length=100, description="Content niche")
    youtube_channel_id: Optional[str] = Field(None, max_length=255, description="YouTube channel ID")
    upload_schedule: Optional[str] = Field(None, max_length=50, description="Upload schedule (daily, weekly, etc.)")
    auto_upload: bool = Field(default=False, description="Enable auto-upload")
    auto_generate: bool = Field(default=False, description="Enable auto-generation")
    settings: Optional[Dict[str, Any]] = Field(None, description="Channel settings")

class ChannelUpdate(BaseModel):
    """Channel update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    niche: Optional[str] = Field(None, max_length=100)
    youtube_channel_id: Optional[str] = Field(None, max_length=255)
    upload_schedule: Optional[str] = Field(None, max_length=50)
    auto_upload: Optional[bool] = None
    auto_generate: Optional[bool] = None
    settings: Optional[Dict[str, Any]] = None
    status: Optional[str] = Field(None, description="Channel status")

class ChannelResponse(BaseModel):
    """Channel response schema"""
    id: int
    name: str
    description: Optional[str]
    niche: Optional[str]
    youtube_channel_id: Optional[str]
    status: str
    upload_schedule: Optional[str]
    auto_upload: bool
    auto_generate: bool
    created_at: datetime
    updated_at: datetime
    owner_id: int
    
    class Config:
        from_attributes = True

class ChannelListResponse(BaseModel):
    """Channel list response schema"""
    total: int
    channels: list[ChannelResponse]

