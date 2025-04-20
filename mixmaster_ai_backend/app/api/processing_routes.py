"""
MixMaster AI - API Routes for Audio Processing

This module defines the API endpoints for audio processing, including
file upload, processing, and result retrieval.
"""

import os
import uuid
import shutil
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import logging

# Import processing modules
from app.audio.processing.processor import process_audio_files
from app.utils.file_utils import validate_audio_file, create_temp_directory, cleanup_temp_files

# Setup logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api", tags=["processing"])

# Define upload directory
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/tmp/mixmaster_uploads")
RESULTS_DIR = os.environ.get("RESULTS_DIR", "/tmp/mixmaster_results")

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

@router.post("/process")
async def process_audio(
    background_tasks: BackgroundTasks,
    vocal_file: UploadFile = File(...),
    beat_file: UploadFile = File(...),
    genre: Optional[str] = Form("default"),
    reverb_amount: Optional[float] = Form(0.3),
    compression_amount: Optional[float] = Form(0.5),
    output_format: Optional[str] = Form("wav"),
):
    """
    Process vocal and beat files to create a mixed and mastered track.
    
    Parameters:
    - vocal_file: Vocal stem (WAV/MP3)
    - beat_file: Instrumental beat (WAV/MP3)
    - genre: Music genre for processing presets
    - reverb_amount: Amount of reverb to apply (0.0-1.0)
    - compression_amount: Amount of compression to apply (0.0-1.0)
    - output_format: Output file format (wav/mp3)
    
    Returns:
    - job_id: Unique identifier for the processing job
    """
    # Generate a unique job ID
    job_id = str(uuid.uuid4())
    
    # Create job directories
    job_upload_dir = os.path.join(UPLOAD_DIR, job_id)
    job_results_dir = os.path.join(RESULTS_DIR, job_id)
    os.makedirs(job_upload_dir, exist_ok=True)
    os.makedirs(job_results_dir, exist_ok=True)
    
    try:
        # Save uploaded files
        vocal_path = os.path.join(job_upload_dir, vocal_file.filename)
        beat_path = os.path.join(job_upload_dir, beat_file.filename)
        
        with open(vocal_path, "wb") as f:
            shutil.copyfileobj(vocal_file.file, f)
        
        with open(beat_path, "wb") as f:
            shutil.copyfileobj(beat_file.file, f)
        
        # Validate files
        if not validate_audio_file(vocal_path):
            raise HTTPException(status_code=400, detail="Invalid vocal file format")
        
        if not validate_audio_file(beat_path):
            raise HTTPException(status_code=400, detail="Invalid beat file format")
        
        # Process files in background
        background_tasks.add_task(
            process_audio_files,
            job_id=job_id,
            vocal_path=vocal_path,
            beat_path=beat_path,
            output_dir=job_results_dir,
            genre=genre,
            reverb_amount=reverb_amount,
            compression_amount=compression_amount,
            output_format=output_format
        )
        
        return {
            "job_id": job_id,
            "status": "processing",
            "message": "Audio processing started"
        }
    
    except Exception as e:
        logger.error(f"Error processing files: {str(e)}")
        # Clean up on error
        shutil.rmtree(job_upload_dir, ignore_errors=True)
        shutil.rmtree(job_results_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"Error processing files: {str(e)}")

@router.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """
    Check the status of a processing job.
    
    Parameters:
    - job_id: Unique identifier for the processing job
    
    Returns:
    - status: Current status of the job
    """
    # Check if results exist
    job_results_dir = os.path.join(RESULTS_DIR, job_id)
    
    if not os.path.exists(job_results_dir):
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check for completion marker
    if os.path.exists(os.path.join(job_results_dir, "complete")):
        return {
            "job_id": job_id,
            "status": "complete",
            "message": "Processing complete"
        }
    
    # Check for error marker
    if os.path.exists(os.path.join(job_results_dir, "error")):
        with open(os.path.join(job_results_dir, "error"), "r") as f:
            error_message = f.read()
        return {
            "job_id": job_id,
            "status": "error",
            "message": error_message
        }
    
    # Otherwise, still processing
    return {
        "job_id": job_id,
        "status": "processing",
        "message": "Audio processing in progress"
    }

@router.get("/result/{job_id}")
async def get_job_result(job_id: str, background_tasks: BackgroundTasks):
    """
    Retrieve the processed audio file.
    
    Parameters:
    - job_id: Unique identifier for the processing job
    
    Returns:
    - File: The processed audio file
    """
    # Check if results exist
    job_results_dir = os.path.join(RESULTS_DIR, job_id)
    
    if not os.path.exists(job_results_dir):
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check for completion marker
    if not os.path.exists(os.path.join(job_results_dir, "complete")):
        raise HTTPException(status_code=400, detail="Processing not complete")
    
    # Find result file
    result_files = [f for f in os.listdir(job_results_dir) if f.endswith((".wav", ".mp3"))]
    
    if not result_files:
        raise HTTPException(status_code=404, detail="Result file not found")
    
    result_file = os.path.join(job_results_dir, result_files[0])
    
    # Schedule cleanup after a delay (e.g., 1 hour)
    background_tasks.add_task(cleanup_temp_files, job_id, delay=3600)
    
    return FileResponse(
        result_file,
        media_type="audio/wav" if result_file.endswith(".wav") else "audio/mpeg",
        filename=os.path.basename(result_file)
    )

@router.delete("/job/{job_id}")
async def delete_job(job_id: str):
    """
    Delete a processing job and its associated files.
    
    Parameters:
    - job_id: Unique identifier for the processing job
    
    Returns:
    - message: Confirmation message
    """
    # Check if job exists
    job_upload_dir = os.path.join(UPLOAD_DIR, job_id)
    job_results_dir = os.path.join(RESULTS_DIR, job_id)
    
    if not (os.path.exists(job_upload_dir) or os.path.exists(job_results_dir)):
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Delete job directories
    shutil.rmtree(job_upload_dir, ignore_errors=True)
    shutil.rmtree(job_results_dir, ignore_errors=True)
    
    return {
        "job_id": job_id,
        "message": "Job deleted successfully"
    }
