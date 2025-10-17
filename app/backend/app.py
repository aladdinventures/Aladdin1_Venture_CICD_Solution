"""
RenovAI Canada - Main FastAPI Application
Copyright (c) 2025 Saeed Alaediny. All rights reserved.

This is the main application file for the RenovAI Canada backend API.
It provides endpoints for renovation cost estimation and lead collection.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import sys
from datetime import datetime

# Add routes to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from routes.estimate import router as estimate_router
from routes.collect_lead import router as lead_router

# Initialize FastAPI application
app = FastAPI(
    title="RenovAI Canada API",
    description="Smart Renovation Cost & Timeline Estimator for Greater Vancouver Area",
    version="1.0.0 (MVP)",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for Custom GPT integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(estimate_router, prefix="/api", tags=["Estimation"])
app.include_router(lead_router, prefix="/api", tags=["Lead Collection"])

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "RenovAI Canada API",
        "version": "1.0.0 (MVP)",
        "description": "Smart Renovation Cost & Timeline Estimator",
        "company": "Aladdin Ventures (Canada) - Homecouver Platform",
        "status": "operational",
        "endpoints": {
            "estimation": "/api/estimate",
            "lead_collection": "/api/collect-lead",
            "health_check": "/health",
            "documentation": "/docs"
        },
        "target_area": "Greater Vancouver Area",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "RenovAI Canada API",
        "timestamp": datetime.now().isoformat(),
        "database": "connected",
        "integrations": {
            "airtable": "mock mode (MVP)",
            "calendly": "configured"
        }
    }

@app.get("/api/info")
async def api_info():
    """Detailed API information for Custom GPT integration."""
    return {
        "api_name": "RenovAI Canada",
        "purpose": "Renovation cost and timeline estimation",
        "supported_project_types": [
            "kitchen",
            "bathroom",
            "basement",
            "full_home",
            "addition"
        ],
        "supported_finish_levels": [
            "basic",
            "standard",
            "premium"
        ],
        "features": [
            "Cost estimation based on project type, size, and finish level",
            "Timeline estimation in weeks",
            "Material and finish recommendations",
            "Lead collection and storage",
            "Consultation booking integration"
        ],
        "location": "Greater Vancouver Area, BC, Canada"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for better error responses."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "path": str(request.url)
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or use default
    port = int(os.getenv("PORT", 8000))
    
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║              RenovAI Canada - Backend API                 ║
    ║                                                           ║
    ║  Smart Renovation Cost & Timeline Estimator               ║
    ║  Greater Vancouver Area                                   ║
    ║                                                           ║
    ║  Copyright (c) 2025 Saeed Alaediny                        ║
    ║  Aladdin Ventures (Canada) - Homecouver Platform          ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    
    🚀 Starting server on http://0.0.0.0:{port}
    📚 API Documentation: http://0.0.0.0:{port}/docs
    🏥 Health Check: http://0.0.0.0:{port}/health
    """)
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )

