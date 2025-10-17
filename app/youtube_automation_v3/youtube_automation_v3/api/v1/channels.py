"""
Channel Management API Endpoints
YouTube Automation System v3.0

Copyright (c) 2025 Saeed Alaediny. All rights reserved.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from core.database import get_db
from core.auth import get_current_active_user
from models.database import User, Channel, ChannelStatus
from schemas.channels import (
    ChannelCreate,
    ChannelUpdate,
    ChannelResponse,
    ChannelListResponse
)

router = APIRouter()

@router.post("/", response_model=ChannelResponse, status_code=status.HTTP_201_CREATED)
async def create_channel(
    channel_data: ChannelCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new channel
    
    Args:
        channel_data: Channel creation data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        ChannelResponse: Created channel
    """
    # Create new channel
    new_channel = Channel(
        name=channel_data.name,
        description=channel_data.description,
        niche=channel_data.niche,
        youtube_channel_id=channel_data.youtube_channel_id,
        upload_schedule=channel_data.upload_schedule,
        auto_upload=channel_data.auto_upload,
        auto_generate=channel_data.auto_generate,
        settings=channel_data.settings or {},
        owner_id=current_user.id,
        status=ChannelStatus.ACTIVE
    )
    
    db.add(new_channel)
    db.commit()
    db.refresh(new_channel)
    
    return new_channel

@router.get("/", response_model=ChannelListResponse)
async def list_channels(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List user's channels
    
    Args:
        skip: Number of records to skip
        limit: Number of records to return
        status: Filter by status
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        ChannelListResponse: List of channels
    """
    query = db.query(Channel).filter(Channel.owner_id == current_user.id)
    
    # Apply status filter
    if status:
        try:
            channel_status = ChannelStatus(status)
            query = query.filter(Channel.status == channel_status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status}"
            )
    
    # Get total count
    total = query.count()
    
    # Get paginated results
    channels = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "channels": channels
    }

@router.get("/{channel_id}", response_model=ChannelResponse)
async def get_channel(
    channel_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get channel details
    
    Args:
        channel_id: Channel ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        ChannelResponse: Channel details
        
    Raises:
        HTTPException: If channel not found or unauthorized
    """
    channel = db.query(Channel).filter(
        Channel.id == channel_id,
        Channel.owner_id == current_user.id
    ).first()
    
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )
    
    return channel

@router.put("/{channel_id}", response_model=ChannelResponse)
async def update_channel(
    channel_id: int,
    channel_data: ChannelUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update channel
    
    Args:
        channel_id: Channel ID
        channel_data: Channel update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        ChannelResponse: Updated channel
        
    Raises:
        HTTPException: If channel not found or unauthorized
    """
    channel = db.query(Channel).filter(
        Channel.id == channel_id,
        Channel.owner_id == current_user.id
    ).first()
    
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )
    
    # Update fields
    update_data = channel_data.dict(exclude_unset=True)
    
    # Validate status if provided
    if "status" in update_data:
        try:
            update_data["status"] = ChannelStatus(update_data["status"])
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {update_data['status']}"
            )
    
    for field, value in update_data.items():
        setattr(channel, field, value)
    
    channel.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(channel)
    
    return channel

@router.delete("/{channel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_channel(
    channel_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete channel
    
    Args:
        channel_id: Channel ID
        current_user: Current authenticated user
        db: Database session
        
    Raises:
        HTTPException: If channel not found or unauthorized
    """
    channel = db.query(Channel).filter(
        Channel.id == channel_id,
        Channel.owner_id == current_user.id
    ).first()
    
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )
    
    db.delete(channel)
    db.commit()
    
    return None

