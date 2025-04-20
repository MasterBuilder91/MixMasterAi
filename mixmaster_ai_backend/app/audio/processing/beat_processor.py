"""
MixMaster AI - Beat Processing Module

This module provides functions for processing beat tracks, including
EQ, dynamics processing, and level adjustment.
"""

import os
import numpy as np
import librosa
import soundfile as sf
from typing import Dict, Any, Optional
import logging
from scipy import signal

# Setup logging
logger = logging.getLogger(__name__)

def process_beat(
    input_file: str,
    output_file: str,
    settings: Dict[str, Any] = None
) -> bool:
    """
    Process a beat track with EQ and dynamics processing.
    
    Parameters:
    - input_file: Path to input beat file
    - output_file: Path to output processed file
    - settings: Dictionary of processing settings
    
    Returns:
    - bool: True if successful, False otherwise
    """
    try:
        # Load default settings if none provided
        if settings is None:
            settings = {
                "eq_low_boost": 2,      # dB
                "eq_high_cut": 16000,   # Hz
                "eq_mid_scoop": -1,     # dB
                "eq_mid_freq": 800,     # Hz
                "eq_mid_q": 1.0,        # Q factor
                "dynamics_threshold": -18,  # dB
                "dynamics_ratio": 2,    # ratio
                "dynamics_attack": 10,  # ms
                "dynamics_release": 100,  # ms
                "level_target": -6      # dB
            }
        
        # Load audio file
        y, sr = librosa.load(input_file, sr=None)
        
        # Apply processing chain
        y_processed = y.copy()
        
        # Apply EQ
        y_processed = apply_beat_eq(
            y_processed, 
            sr, 
            low_boost=settings["eq_low_boost"],
            high_cut=settings["eq_high_cut"],
            mid_scoop=settings["eq_mid_scoop"],
            mid_freq=settings["eq_mid_freq"],
            mid_q=settings["eq_mid_q"]
        )
        
        # Apply dynamics processing
        y_processed = apply_dynamics_processing(
            y_processed,
            threshold=settings["dynamics_threshold"],
            ratio=settings["dynamics_ratio"],
            attack=settings["dynamics_attack"],
            release=settings["dynamics_release"]
        )
        
        # Apply level adjustment
        y_processed = adjust_level(
            y_processed,
            target_db=settings["level_target"]
        )
        
        # Save processed audio
        sf.write(output_file, y_processed, sr)
        
        return True
    
    except Exception as e:
        logger.error(f"Error processing beat {input_file}: {str(e)}")
        return False

def apply_beat_eq(
    y: np.ndarray,
    sr: int,
    low_boost: float = 2,
    high_cut: float = 16000,
    mid_scoop: float = -1,
    mid_freq: float = 800,
    mid_q: float = 1.0
) -> np.ndarray:
    """
    Apply EQ to beat track.
    
    Parameters:
    - y: Audio signal
    - sr: Sample rate
    - low_boost: Low frequency boost (dB)
    - high_cut: High cut frequency (Hz)
    - mid_scoop: Mid frequency cut (dB)
    - mid_freq: Mid band frequency (Hz)
    - mid_q: Mid band Q factor
    
    Returns:
    - np.ndarray: Processed audio signal
    """
    # Apply low boost
    if low_boost != 0:
        # Convert dB to gain
        gain = 10 ** (low_boost / 20)
        # Simple implementation of low shelf filter
        b, a = signal.butter(2, 200 / (sr / 2), 'lowpass')
        low_freq = signal.lfilter(b, a, y)
        y = y - low_freq + (low_freq * gain)
    
    # Apply high cut
    if high_cut < sr / 2:
        b, a = signal.butter(4, high_cut / (sr / 2), 'lowpass')
        y = signal.lfilter(b, a, y)
    
    # Apply mid scoop
    if mid_scoop != 0:
        # Convert dB to gain
        gain = 10 ** (mid_scoop / 20)
        # Simple implementation of peaking filter
        bandwidth = mid_freq / mid_q
        low_edge = max(20, mid_freq - bandwidth / 2)
        high_edge = min(sr / 2 - 1, mid_freq + bandwidth / 2)
        
        b, a = signal.butter(2, [low_edge / (sr / 2), high_edge / (sr / 2)], 'bandpass')
        mid_freq_band = signal.lfilter(b, a, y)
        y = y - mid_freq_band + (mid_freq_band * gain)
    
    return y

def apply_dynamics_processing(
    y: np.ndarray,
    threshold: float = -18,
    ratio: float = 2,
    attack: float = 10,
    release: float = 100
) -> np.ndarray:
    """
    Apply dynamics processing to beat track.
    
    Parameters:
    - y: Audio signal
    - threshold: Threshold in dB
    - ratio: Compression ratio
    - attack: Attack time in ms
    - release: Release time in ms
    
    Returns:
    - np.ndarray: Processed audio signal
    """
    # Convert threshold from dB to linear
    threshold_linear = 10 ** (threshold / 20)
    
    # Initialize gain reduction array
    gain_reduction = np.ones_like(y)
    
    # Calculate sample-by-sample gain reduction
    # This is a simplified model of compression
    for i in range(1, len(y)):
        # Calculate instantaneous level
        level = abs(y[i])
        
        # Apply compression if level exceeds threshold
        if level > threshold_linear:
            # Calculate gain reduction
            gain = (level / threshold_linear) ** (1 / ratio - 1)
            
            # Apply attack/release smoothing
            # This is a very simplified model
            if gain < gain_reduction[i-1]:
                # Attack phase
                gain_reduction[i] = gain_reduction[i-1] * 0.9 + gain * 0.1
            else:
                # Release phase
                gain_reduction[i] = gain_reduction[i-1] * 0.99 + gain * 0.01
        else:
            # No compression needed
            gain_reduction[i] = 1.0
    
    # Apply gain reduction to signal
    y_processed = y * gain_reduction
    
    return y_processed

def adjust_level(
    y: np.ndarray,
    target_db: float = -6
) -> np.ndarray:
    """
    Adjust the level of an audio signal to a target RMS level.
    
    Parameters:
    - y: Audio signal
    - target_db: Target RMS level in dB
    
    Returns:
    - np.ndarray: Level-adjusted audio signal
    """
    # Calculate current RMS level
    current_rms = np.sqrt(np.mean(y**2))
    current_db = 20 * np.log10(current_rms) if current_rms > 0 else -100
    
    # Calculate gain needed to reach target
    gain_db = target_db - current_db
    gain_linear = 10 ** (gain_db / 20)
    
    # Apply gain
    y_adjusted = y * gain_linear
    
    return y_adjusted
