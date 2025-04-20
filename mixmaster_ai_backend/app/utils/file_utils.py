"""
MixMaster AI - Audio File Utility Functions

This module provides utility functions for handling audio files,
including validation, conversion, and temporary file management.
"""

import os
import time
import shutil
import logging
from typing import List, Optional, Tuple
import soundfile as sf
import librosa
import ffmpeg

# Setup logging
logger = logging.getLogger(__name__)

# Define constants
SUPPORTED_FORMATS = [".wav", ".mp3", ".flac", ".ogg"]
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/tmp/mixmaster_uploads")
RESULTS_DIR = os.environ.get("RESULTS_DIR", "/tmp/mixmaster_results")

def validate_audio_file(file_path: str) -> bool:
    """
    Validate if a file is a supported audio file.
    
    Parameters:
    - file_path: Path to the audio file
    
    Returns:
    - bool: True if valid, False otherwise
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return False
    
    # Check file extension
    _, ext = os.path.splitext(file_path.lower())
    if ext not in SUPPORTED_FORMATS:
        logger.error(f"Unsupported file format: {ext}")
        return False
    
    # Try to load the file with librosa to verify it's valid audio
    try:
        # Just load a small portion to verify format
        y, sr = librosa.load(file_path, sr=None, duration=0.1)
        return True
    except Exception as e:
        logger.error(f"Error validating audio file {file_path}: {str(e)}")
        return False

def create_temp_directory() -> str:
    """
    Create a temporary directory for processing.
    
    Returns:
    - str: Path to the temporary directory
    """
    temp_dir = os.path.join("/tmp", f"mixmaster_{int(time.time())}")
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir

def cleanup_temp_files(job_id: str, delay: int = 0) -> None:
    """
    Clean up temporary files after processing.
    
    Parameters:
    - job_id: Job identifier
    - delay: Delay in seconds before cleanup
    """
    if delay > 0:
        time.sleep(delay)
    
    # Remove upload and results directories
    job_upload_dir = os.path.join(UPLOAD_DIR, job_id)
    job_results_dir = os.path.join(RESULTS_DIR, job_id)
    
    if os.path.exists(job_upload_dir):
        shutil.rmtree(job_upload_dir, ignore_errors=True)
        logger.info(f"Cleaned up upload directory for job {job_id}")
    
    if os.path.exists(job_results_dir):
        shutil.rmtree(job_results_dir, ignore_errors=True)
        logger.info(f"Cleaned up results directory for job {job_id}")

def convert_to_wav(input_file: str, output_file: str, sample_rate: int = 44100) -> bool:
    """
    Convert an audio file to WAV format with specified sample rate.
    
    Parameters:
    - input_file: Path to input audio file
    - output_file: Path to output WAV file
    - sample_rate: Target sample rate
    
    Returns:
    - bool: True if successful, False otherwise
    """
    try:
        # Use ffmpeg for conversion
        (
            ffmpeg
            .input(input_file)
            .output(output_file, ar=sample_rate, format='wav')
            .run(quiet=True, overwrite_output=True)
        )
        return True
    except Exception as e:
        logger.error(f"Error converting {input_file} to WAV: {str(e)}")
        return False

def get_audio_info(file_path: str) -> Tuple[int, int, float]:
    """
    Get basic information about an audio file.
    
    Parameters:
    - file_path: Path to the audio file
    
    Returns:
    - Tuple[int, int, float]: (sample_rate, channels, duration)
    """
    try:
        y, sr = librosa.load(file_path, sr=None)
        channels = 1 if len(y.shape) == 1 else y.shape[0]
        duration = librosa.get_duration(y=y, sr=sr)
        return sr, channels, duration
    except Exception as e:
        logger.error(f"Error getting audio info for {file_path}: {str(e)}")
        return 0, 0, 0.0
