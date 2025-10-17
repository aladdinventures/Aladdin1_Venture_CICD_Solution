"""
RenovAI Canada - Lead Collection Route Handler
Copyright (c) 2025 Saeed Alaediny. All rights reserved.

This module handles lead collection and storage in Airtable.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from integrations.airtable_client import AirtableClient

router = APIRouter()

# Initialize Airtable client
airtable_client = AirtableClient()

class LeadRequest(BaseModel):
    """Request model for lead collection."""
    name: str = Field(..., min_length=2, max_length=100, description="Customer's full name")
    email: EmailStr = Field(..., description="Customer's email address")
    phone: str = Field(..., min_length=10, max_length=20, description="Customer's phone number")
    project_type: str = Field(..., description="Type of renovation project")
    size_sqft: Optional[float] = Field(None, gt=0, description="Project size in square feet")
    finish_level: Optional[str] = Field(None, description="Desired finish level")
    postal_code: Optional[str] = Field(None, description="Project location postal code")
    estimated_cost: Optional[float] = Field(None, description="Estimated cost from previous calculation")
    project_notes: Optional[str] = Field(None, max_length=1000, description="Additional notes or requirements")
    
    @validator('phone')
    def validate_phone(cls, v):
        """Basic phone number validation."""
        # Remove common separators
        cleaned = v.replace('-', '').replace(' ', '').replace('(', '').replace(')', '').replace('+', '')
        if not cleaned.isdigit() or len(cleaned) < 10:
            raise ValueError("Phone number must contain at least 10 digits")
        return v
    
    @validator('project_type')
    def validate_project_type(cls, v):
        """Validate project type."""
        valid_types = ['kitchen', 'bathroom', 'basement', 'full_home', 'addition', 'other']
        if v.lower() not in valid_types:
            raise ValueError(f"Project type must be one of: {', '.join(valid_types)}")
        return v.lower()

class LeadResponse(BaseModel):
    """Response model for lead collection."""
    success: bool
    message: str
    record_id: str
    created_at: str

@router.post("/collect-lead", response_model=LeadResponse)
async def collect_lead(request: LeadRequest):
    """
    Collect and store lead information.
    
    Args:
        request: LeadRequest containing customer information
    
    Returns:
        LeadResponse with storage confirmation
    
    Raises:
        HTTPException: If lead storage fails
    """
    try:
        # Prepare lead data for Airtable
        lead_data = {
            'Name': request.name,
            'Email': request.email,
            'Phone': request.phone,
            'Project Type': request.project_type.replace('_', ' ').title(),
            'Size (sq ft)': request.size_sqft,
            'Finish Level': request.finish_level.capitalize() if request.finish_level else None,
            'Postal Code': request.postal_code,
            'Estimated Cost': request.estimated_cost,
            'Project Notes': request.project_notes,
            'Lead Source': 'RenovAI ChatGPT Agent',
            'Status': 'New',
            'Submitted At': datetime.now().isoformat()
        }
        
        # Remove None values
        lead_data = {k: v for k, v in lead_data.items() if v is not None}
        
        # Store lead in Airtable
        result = airtable_client.create_lead(lead_data)
        
        if result['success']:
            return LeadResponse(
                success=True,
                message="Thank you! Your information has been received. Our team will contact you shortly.",
                record_id=result['record_id'],
                created_at=result['created_at']
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to store lead information"
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing lead: {str(e)}"
        )

@router.get("/leads/count")
async def get_leads_count():
    """
    Get the total number of leads stored (for testing/monitoring).
    
    Returns:
        Dictionary with lead count
    """
    try:
        all_leads = airtable_client.get_all_leads()
        return {
            "total_leads": len(all_leads),
            "storage_mode": "mock" if airtable_client.use_mock else "airtable"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving lead count: {str(e)}"
        )

