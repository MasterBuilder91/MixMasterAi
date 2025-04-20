"""
MixMaster AI - Audio Analysis Module

This module provides functions for analyzing audio files to extract
features and characteristics needed for mixing and mastering.
"""

import os
import numpy as np
import librosa
import logging
from typing import Dict, Any, Tuple, Optional

# Setup logging
logger = logging.getLogger(__name__)

def analyze_audio(file_path: str) -> Dict[str, Any]:
    """
    Analyze an audio file and extract key features.
    
    Parameters:
    - file_path: Path to the audio file
    
    Returns:
    - Dict: Dictionary of audio features and characteristics
    """
    try:
        # Load audio file
        y, sr = librosa.load(file_path, sr=None)
        
        # Get basic properties
        duration = librosa.get_duration(y=y, sr=sr)
        
        # Convert to mono if stereo for analysis
        if len(y.shape) > 1:
            y_mono = librosa.to_mono(y)
        else:
            y_mono = y
        
        # Calculate RMS energy
        rms = librosa.feature.rms(y=y_mono)[0]
        rms_mean = np.mean(rms)
        rms_std = np.std(rms)
        
        # Calculate spectral centroid
        centroid = librosa.feature.spectral_centroid(y=y_mono, sr=sr)[0]
        centroid_mean = np.mean(centroid)
        
        # Calculate spectral bandwidth
        bandwidth = librosa.feature.spectral_bandwidth(y=y_mono, sr=sr)[0]
        bandwidth_mean = np.mean(bandwidth)
        
        # Detect tempo
        tempo, _ = librosa.beat.beat_track(y=y_mono, sr=sr)
        
        # Calculate zero crossing rate
        zcr = librosa.feature.zero_crossing_rate(y_mono)[0]
        zcr_mean = np.mean(zcr)
        
        # Calculate peak amplitude
        peak = np.max(np.abs(y_mono))
        
        # Calculate LUFS (Loudness Units Full Scale)
        # This is a simplified approximation
        lufs = -23.0 - 10 * np.log10(np.mean(y_mono**2) + 1e-10)
        
        # Return all features
        return {
            "duration": duration,
            "sample_rate": sr,
            "rms_mean": float(rms_mean),
            "rms_std": float(rms_std),
            "centroid_mean": float(centroid_mean),
            "bandwidth_mean": float(bandwidth_mean),
            "tempo": float(tempo),
            "zcr_mean": float(zcr_mean),
            "peak_amplitude": float(peak),
            "lufs": float(lufs)
        }
    
    except Exception as e:
        logger.error(f"Error analyzing audio file {file_path}: {str(e)}")
        return {
            "error": str(e)
        }

def detect_genre(file_path: str) -> str:
    """
    Attempt to detect the genre of an audio file.
    
    Parameters:
    - file_path: Path to the audio file
    
    Returns:
    - str: Detected genre or "unknown"
    """
    # This is a placeholder for a more sophisticated genre detection system
    # In a real implementation, this would use a trained ML model
    
    try:
        # Load audio file
        y, sr = librosa.load(file_path, sr=None, duration=30)  # Analyze first 30 seconds
        
        # Convert to mono if stereo
        if len(y.shape) > 1:
            y = librosa.to_mono(y)
        
        # Extract features
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        
        # Simple rule-based genre classification
        # This is very simplistic and would be replaced with a proper ML model
        if tempo > 120:
            if np.mean(spectral_contrast[1]) > 10:
                return "trap"
            else:
                return "hip_hop"
        elif tempo > 90:
            if np.mean(mfccs[1]) > 0:
                return "pop"
            else:
                return "r_and_b"
        else:
            return "other"
    
    except Exception as e:
        logger.error(f"Error detecting genre for {file_path}: {str(e)}")
        return "unknown"

def analyze_vocal_track(file_path: str) -> Dict[str, Any]:
    """
    Analyze a vocal track to detect characteristics relevant for processing.
    
    Parameters:
    - file_path: Path to the vocal audio file
    
    Returns:
    - Dict: Dictionary of vocal characteristics
    """
    try:
        # Get general audio features
        features = analyze_audio(file_path)
        
        # Load audio for vocal-specific analysis
        y, sr = librosa.load(file_path, sr=None)
        
        # Convert to mono if stereo
        if len(y.shape) > 1:
            y = librosa.to_mono(y)
        
        # Detect presence of sibilance (simplified)
        # High frequency content in 5-8kHz range
        spec = np.abs(librosa.stft(y))
        freqs = librosa.fft_frequencies(sr=sr)
        sibilance_band = np.logical_and(freqs >= 5000, freqs <= 8000)
        sibilance_energy = np.mean(spec[sibilance_band, :])
        overall_energy = np.mean(spec)
        sibilance_ratio = sibilance_energy / overall_energy if overall_energy > 0 else 0
        
        # Detect presence of muddiness (simplified)
        # Excess energy in 200-400Hz range
        muddiness_band = np.logical_and(freqs >= 200, freqs <= 400)
        muddiness_energy = np.mean(spec[muddiness_band, :])
        muddiness_ratio = muddiness_energy / overall_energy if overall_energy > 0 else 0
        
        # Add vocal-specific features to general features
        features.update({
            "sibilance_ratio": float(sibilance_ratio),
            "muddiness_ratio": float(muddiness_ratio),
            "needs_de_essing": sibilance_ratio > 0.2,  # Threshold determined empirically
            "needs_de_mudding": muddiness_ratio > 0.3  # Threshold determined empirically
        })
        
        return features
    
    except Exception as e:
        logger.error(f"Error analyzing vocal track {file_path}: {str(e)}")
        return {
            "error": str(e)
        }

def analyze_beat_track(file_path: str) -> Dict[str, Any]:
    """
    Analyze a beat track to detect characteristics relevant for processing.
    
    Parameters:
    - file_path: Path to the beat audio file
    
    Returns:
    - Dict: Dictionary of beat characteristics
    """
    try:
        # Get general audio features
        features = analyze_audio(file_path)
        
        # Load audio for beat-specific analysis
        y, sr = librosa.load(file_path, sr=None)
        
        # Convert to mono if stereo
        if len(y.shape) > 1:
            y = librosa.to_mono(y)
        
        # Detect beat positions
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        
        # Detect bass energy
        spec = np.abs(librosa.stft(y))
        freqs = librosa.fft_frequencies(sr=sr)
        bass_band = np.logical_and(freqs >= 60, freqs <= 250)
        bass_energy = np.mean(spec[bass_band, :])
        overall_energy = np.mean(spec)
        bass_ratio = bass_energy / overall_energy if overall_energy > 0 else 0
        
        # Add beat-specific features to general features
        features.update({
            "tempo": float(tempo),
            "beat_count": len(beat_times),
            "bass_ratio": float(bass_ratio),
            "has_strong_bass": bass_ratio > 0.25  # Threshold determined empirically
        })
        
        return features
    
    except Exception as e:
        logger.error(f"Error analyzing beat track {file_path}: {str(e)}")
        return {
            "error": str(e)
        }
