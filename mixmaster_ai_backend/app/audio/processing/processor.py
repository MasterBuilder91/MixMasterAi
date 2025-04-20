"""
MixMaster AI - Main Audio Processor

This module ties together all the audio processing components and
provides the main processing pipeline for the MixMaster AI platform.
"""

import os
import time
import logging
from typing import Dict, Any, Optional

# Import processing modules
from app.audio.analysis.analyzer import analyze_vocal_track, analyze_beat_track, detect_genre
from app.audio.processing.vocal_processor import process_vocals
from app.audio.processing.beat_processor import process_beat
from app.audio.mixing.mixer import mix_tracks
from app.audio.mastering.mastering import master_track
from app.utils.file_utils import validate_audio_file, convert_to_wav

# Setup logging
logger = logging.getLogger(__name__)

def process_audio_files(
    job_id: str,
    vocal_path: str,
    beat_path: str,
    output_dir: str,
    genre: str = "default",
    reverb_amount: float = 0.3,
    compression_amount: float = 0.5,
    output_format: str = "wav"
) -> bool:
    """
    Process vocal and beat files through the complete pipeline.
    
    Parameters:
    - job_id: Unique job identifier
    - vocal_path: Path to vocal file
    - beat_path: Path to beat file
    - output_dir: Directory to save output files
    - genre: Music genre for processing presets
    - reverb_amount: Amount of reverb to apply (0.0-1.0)
    - compression_amount: Amount of compression to apply (0.0-1.0)
    - output_format: Output file format (wav/mp3)
    
    Returns:
    - bool: True if successful, False otherwise
    """
    try:
        logger.info(f"Starting processing job {job_id}")
        
        # Create working directory
        work_dir = os.path.join(output_dir, "work")
        os.makedirs(work_dir, exist_ok=True)
        
        # Validate input files
        if not validate_audio_file(vocal_path):
            raise ValueError(f"Invalid vocal file: {vocal_path}")
        
        if not validate_audio_file(beat_path):
            raise ValueError(f"Invalid beat file: {beat_path}")
        
        # Convert files to WAV if needed
        vocal_wav = os.path.join(work_dir, "vocal.wav")
        beat_wav = os.path.join(work_dir, "beat.wav")
        
        logger.info("Converting input files to WAV format")
        convert_to_wav(vocal_path, vocal_wav)
        convert_to_wav(beat_path, beat_wav)
        
        # Analyze files
        logger.info("Analyzing vocal track")
        vocal_analysis = analyze_vocal_track(vocal_wav)
        
        logger.info("Analyzing beat track")
        beat_analysis = analyze_beat_track(beat_wav)
        
        # Detect genre if set to auto
        if genre == "auto":
            logger.info("Auto-detecting genre")
            genre = detect_genre(beat_wav)
            logger.info(f"Detected genre: {genre}")
        
        # Load genre-specific presets
        vocal_settings = get_vocal_preset(genre, reverb_amount, compression_amount)
        beat_settings = get_beat_preset(genre)
        mix_settings = get_mix_preset(genre)
        master_settings = get_master_preset(genre)
        
        # Process vocal track
        logger.info("Processing vocal track")
        processed_vocal = os.path.join(work_dir, "vocal_processed.wav")
        if not process_vocals(vocal_wav, processed_vocal, vocal_settings):
            raise RuntimeError("Vocal processing failed")
        
        # Process beat track
        logger.info("Processing beat track")
        processed_beat = os.path.join(work_dir, "beat_processed.wav")
        if not process_beat(beat_wav, processed_beat, beat_settings):
            raise RuntimeError("Beat processing failed")
        
        # Mix tracks
        logger.info("Mixing tracks")
        mixed_track = os.path.join(work_dir, "mixed.wav")
        if not mix_tracks(processed_vocal, processed_beat, mixed_track, mix_settings):
            raise RuntimeError("Mixing failed")
        
        # Master track
        logger.info("Mastering track")
        if output_format == "wav":
            mastered_track = os.path.join(output_dir, f"mastered_{job_id}.wav")
        else:
            mastered_track = os.path.join(output_dir, f"mastered_{job_id}.mp3")
        
        if not master_track(mixed_track, mastered_track, settings=master_settings):
            raise RuntimeError("Mastering failed")
        
        # Create completion marker
        with open(os.path.join(output_dir, "complete"), "w") as f:
            f.write("Processing completed successfully")
        
        logger.info(f"Processing job {job_id} completed successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error processing job {job_id}: {str(e)}")
        
        # Create error marker
        with open(os.path.join(output_dir, "error"), "w") as f:
            f.write(f"Processing failed: {str(e)}")
        
        return False

def get_vocal_preset(genre: str, reverb_amount: float, compression_amount: float) -> Dict[str, Any]:
    """
    Get vocal processing preset based on genre.
    
    Parameters:
    - genre: Music genre
    - reverb_amount: User-specified reverb amount
    - compression_amount: User-specified compression amount
    
    Returns:
    - Dict: Vocal processing settings
    """
    # Base settings
    settings = {
        "eq_low_cut": 80,
        "eq_high_cut": 18000,
        "eq_low_shelf": -3,
        "eq_high_shelf": 2,
        "eq_mid_freq": 3000,
        "eq_mid_gain": 2,
        "eq_mid_q": 1.0,
        "compression_threshold": -20,
        "compression_ratio": 4,
        "compression_attack": 5,
        "compression_release": 50,
        "de_ess": True,
        "de_ess_threshold": -10,
        "reverb_amount": reverb_amount,
        "delay_amount": 0.1,
        "stereo_width": 0.5
    }
    
    # Apply genre-specific adjustments
    if genre == "trap":
        settings.update({
            "eq_low_cut": 100,
            "eq_high_shelf": 3,
            "compression_ratio": 5,
            "compression_attack": 3,
            "delay_amount": 0.15,
        })
    elif genre == "hip_hop":
        settings.update({
            "eq_low_cut": 90,
            "eq_mid_freq": 2500,
            "compression_ratio": 4.5,
            "delay_amount": 0.12,
        })
    elif genre == "pop":
        settings.update({
            "eq_low_cut": 70,
            "eq_high_shelf": 2.5,
            "eq_mid_gain": 1.5,
            "compression_ratio": 3.5,
            "stereo_width": 0.6,
        })
    elif genre == "r_and_b":
        settings.update({
            "eq_low_cut": 60,
            "eq_mid_freq": 2000,
            "eq_mid_gain": 1,
            "compression_ratio": 3,
            "reverb_amount": reverb_amount * 1.2,  # More reverb for R&B
        })
    
    # Apply user-specified compression amount
    settings["compression_ratio"] = 2 + (compression_amount * 6)  # Scale from 2:1 to 8:1
    
    return settings

def get_beat_preset(genre: str) -> Dict[str, Any]:
    """
    Get beat processing preset based on genre.
    
    Parameters:
    - genre: Music genre
    
    Returns:
    - Dict: Beat processing settings
    """
    # Base settings
    settings = {
        "eq_low_boost": 2,
        "eq_high_cut": 16000,
        "eq_mid_scoop": -1,
        "eq_mid_freq": 800,
        "eq_mid_q": 1.0,
        "dynamics_threshold": -18,
        "dynamics_ratio": 2,
        "dynamics_attack": 10,
        "dynamics_release": 100,
        "level_target": -6
    }
    
    # Apply genre-specific adjustments
    if genre == "trap":
        settings.update({
            "eq_low_boost": 3,
            "eq_mid_freq": 600,
            "eq_mid_scoop": -2,
            "dynamics_threshold": -16,
            "level_target": -5.5,
        })
    elif genre == "hip_hop":
        settings.update({
            "eq_low_boost": 2.5,
            "eq_mid_freq": 700,
            "dynamics_threshold": -17,
            "level_target": -5.8,
        })
    elif genre == "pop":
        settings.update({
            "eq_low_boost": 1.5,
            "eq_high_cut": 17000,
            "eq_mid_scoop": -0.5,
            "dynamics_threshold": -19,
            "level_target": -6.5,
        })
    elif genre == "r_and_b":
        settings.update({
            "eq_low_boost": 2,
            "eq_mid_freq": 500,
            "eq_mid_scoop": -1.5,
            "dynamics_threshold": -20,
            "level_target": -7,
        })
    
    return settings

def get_mix_preset(genre: str) -> Dict[str, Any]:
    """
    Get mixing preset based on genre.
    
    Parameters:
    - genre: Music genre
    
    Returns:
    - Dict: Mixing settings
    """
    # Base settings
    settings = {
        "vocal_level": 0.0,
        "beat_level": -3.0,
        "reduce_masking": True,
        "stereo_placement": True,
        "bus_processing": True,
        "target_lufs": -14.0
    }
    
    # Apply genre-specific adjustments
    if genre == "trap":
        settings.update({
            "vocal_level": 0.5,
            "beat_level": -2.5,
            "target_lufs": -12.0,  # Louder for trap
        })
    elif genre == "hip_hop":
        settings.update({
            "vocal_level": 0.0,
            "beat_level": -3.0,
            "target_lufs": -13.0,
        })
    elif genre == "pop":
        settings.update({
            "vocal_level": 1.0,  # Vocals more prominent in pop
            "beat_level": -4.0,
            "target_lufs": -13.5,
        })
    elif genre == "r_and_b":
        settings.update({
            "vocal_level": 0.0,
            "beat_level": -3.5,
            "target_lufs": -14.5,  # Slightly quieter for R&B
        })
    
    return settings

def get_master_preset(genre: str) -> Dict[str, Any]:
    """
    Get mastering preset based on genre.
    
    Parameters:
    - genre: Music genre
    
    Returns:
    - Dict: Mastering settings
    """
    # Base settings
    settings = {
        "use_matchering": False,
        "eq_low_shelf": 1.0,
        "eq_high_shelf": 1.5,
        "multiband_low_thresh": -24.0,
        "multiband_mid_thresh": -18.0,
        "multiband_high_thresh": -24.0,
        "stereo_enhance": 0.2,
        "limiter_threshold": -1.0,
        "target_lufs": -14.0
    }
    
    # Apply genre-specific adjustments
    if genre == "trap":
        settings.update({
            "eq_low_shelf": 1.5,
            "multiband_low_thresh": -22.0,
            "stereo_enhance": 0.3,
            "limiter_threshold": -0.8,
            "target_lufs": -12.0,  # Louder for trap
        })
    elif genre == "hip_hop":
        settings.update({
            "eq_low_shelf": 1.2,
            "multiband_low_thresh": -23.0,
            "stereo_enhance": 0.25,
            "target_lufs": -13.0,
        })
    elif genre == "pop":
        settings.update({
            "eq_high_shelf": 2.0,
            "multiband_mid_thresh": -16.0,
            "stereo_enhance": 0.3,
            "target_lufs": -13.5,
        })
    elif genre == "r_and_b":
        settings.update({
            "eq_low_shelf": 0.8,
            "eq_high_shelf": 1.0,
            "multiband_low_thresh": -25.0,
            "stereo_enhance": 0.15,
            "target_lufs": -14.5,  # Slightly quieter for R&B
        })
    
    return settings
