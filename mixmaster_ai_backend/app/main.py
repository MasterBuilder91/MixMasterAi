"""
MixMaster AI - Main Application Entry Point

This module initializes the FastAPI application and sets up the API routes
for the MixMaster AI platform.
"""

import os
import logging
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="MixMaster AI API",
    description="API for automated mixing and mastering of vocals with beats",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import API routes
from app.api import processing_routes

# Register API routes
app.include_router(processing_routes.router)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint to verify API is running"""
    return {"status": "healthy", "version": "0.1.0"}

if __name__ == "__main__":
    # Run the API server
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
