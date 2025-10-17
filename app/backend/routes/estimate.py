"""
RenovAI Canada - Estimation Route Handler
Copyright (c) 2025 Saeed Alaediny. All rights reserved.

This module handles renovation cost and timeline estimation requests.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator
from typing import Optional, List
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.db_helper import calculate_estimate, get_all_project_types, get_all_finish_levels

router = APIRouter()

class EstimateRequest(BaseModel):
    """Request model for renovation estimation."""
    project_type: str = Field(..., description="Type of renovation project")
    size_sqft: float = Field(..., gt=0, description="Size of the project in square feet")
    finish_level: str = Field(..., description="Quality level: basic, standard, or premium")
    postal_code: Optional[str] = Field(None, description="Postal code for location-based adjustments")
    
    @validator('project_type')
    def validate_project_type(cls, v):
        """Validate project type."""
        valid_types = ['kitchen', 'bathroom', 'basement', 'full_home', 'addition']
        if v.lower() not in valid_types:
            raise ValueError(f"Project type must be one of: {', '.join(valid_types)}")
        return v.lower()
    
    @validator('finish_level')
    def validate_finish_level(cls, v):
        """Validate finish level."""
        valid_levels = ['basic', 'standard', 'premium']
        if v.lower() not in valid_levels:
            raise ValueError(f"Finish level must be one of: {', '.join(valid_levels)}")
        return v.lower()
    
    @validator('size_sqft')
    def validate_size(cls, v):
        """Validate size is reasonable."""
        if v > 10000:
            raise ValueError("Size exceeds maximum allowed (10,000 sq ft)")
        return v

class EstimateResponse(BaseModel):
    """Response model for renovation estimation."""
    project_type: str
    size_sqft: float
    finish_level: str
    estimated_cost: float
    estimated_cost_range: dict
    estimated_timeline_weeks: int
    cost_per_sqft: float
    suggested_materials: List[str]
    description: str
    location: Optional[str] = None
    disclaimer: str = "This is an approximate estimate. Final costs may vary based on specific requirements, site conditions, and material selections. A detailed consultation is recommended for accurate pricing."

@router.post("/estimate", response_model=EstimateResponse)
async def get_estimate(request: EstimateRequest):
    """
    Calculate renovation cost and timeline estimate.
    
    Args:
        request: EstimateRequest containing project details
    
    Returns:
        EstimateResponse with calculated estimates
    
    Raises:
        HTTPException: If estimation data is not available
    """
    # Calculate estimate using database helper
    estimate = calculate_estimate(
        project_type=request.project_type,
        finish_level=request.finish_level,
        size_sqft=request.size_sqft
    )
    
    if not estimate:
        raise HTTPException(
            status_code=404,
            detail=f"No estimation data found for {request.project_type} with {request.finish_level} finish level"
        )
    
    # Add location information if provided
    if request.postal_code:
        estimate['location'] = f"Greater Vancouver Area ({request.postal_code})"
    
    # Add disclaimer
    estimate['disclaimer'] = EstimateResponse.__fields__['disclaimer'].default
    
    return estimate

@router.get("/project-types")
async def get_project_types():
    """
    Get list of available project types.
    
    Returns:
        Dictionary containing list of project types
    """
    project_types = get_all_project_types()
    return {
        "project_types": project_types,
        "count": len(project_types)
    }

@router.get("/finish-levels")
async def get_finish_levels():
    """
    Get list of available finish levels.
    
    Returns:
        Dictionary containing list of finish levels
    """
    finish_levels = get_all_finish_levels()
    return {
        "finish_levels": finish_levels,
        "count": len(finish_levels)
    }

