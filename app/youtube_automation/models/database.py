"""
Database Models
YouTube Automation System v3.0

Copyright (c) 2025 Saeed Alaediny. All rights reserved.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum

from core.database import Base

class UserRole(str, Enum):
    """User roles"""
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"

class ChannelStatus(str, Enum):
    """Channel status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class VideoStatus(str, Enum):
    """Video status"""
    DRAFT = "draft"
    GENERATING = "generating"
    GENERATED = "generated"
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    FAILED = "failed"

class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime)
    
    # Relationships
    channels = relationship("Channel", back_populates="owner", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "role": self.role.value if self.role else None,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }

class Channel(Base):
    """Channel model"""
    __tablename__ = "channels"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    niche = Column(String(100))
    youtube_channel_id = Column(String(255), unique=True, index=True)
    status = Column(SQLEnum(ChannelStatus), default=ChannelStatus.ACTIVE, nullable=False)
    upload_schedule = Column(String(50))  # daily, weekly, etc.
    auto_upload = Column(Boolean, default=False, nullable=False)
    auto_generate = Column(Boolean, default=False, nullable=False)
    settings = Column(JSON)  # Channel-specific settings
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Foreign keys
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="channels")
    videos = relationship("Video", back_populates="channel", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "niche": self.niche,
            "youtube_channel_id": self.youtube_channel_id,
            "status": self.status.value if self.status else None,
            "upload_schedule": self.upload_schedule,
            "auto_upload": self.auto_upload,
            "auto_generate": self.auto_generate,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

class Video(Base):
    """Video model"""
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    script = Column(Text)
    status = Column(SQLEnum(VideoStatus), default=VideoStatus.DRAFT, nullable=False)
    youtube_video_id = Column(String(255), unique=True, index=True)
    video_path = Column(String(500))
    thumbnail_path = Column(String(500))
    duration = Column(Integer)  # Duration in seconds
    file_size = Column(Integer)  # File size in bytes
    metadata = Column(JSON)  # Video metadata (tags, category, etc.)
    generation_progress = Column(Integer, default=0)  # Progress percentage
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    published_at = Column(DateTime)
    
    # Foreign keys
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False)
    
    # Relationships
    channel = relationship("Channel", back_populates="videos")
    analytics = relationship("VideoAnalytics", back_populates="video", uselist=False, cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value if self.status else None,
            "youtube_video_id": self.youtube_video_id,
            "duration": self.duration,
            "generation_progress": self.generation_progress,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "published_at": self.published_at.isoformat() if self.published_at else None,
        }

class VideoAnalytics(Base):
    """Video analytics model"""
    __tablename__ = "video_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    watch_time = Column(Integer, default=0)  # Total watch time in seconds
    average_view_duration = Column(Float, default=0.0)  # Average view duration in seconds
    click_through_rate = Column(Float, default=0.0)  # CTR percentage
    engagement_rate = Column(Float, default=0.0)  # Engagement percentage
    revenue = Column(Float, default=0.0)  # Estimated revenue
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False, unique=True)
    
    # Relationships
    video = relationship("Video", back_populates="analytics")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "views": self.views,
            "likes": self.likes,
            "comments": self.comments,
            "watch_time": self.watch_time,
            "engagement_rate": self.engagement_rate,
            "revenue": self.revenue,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
        }

