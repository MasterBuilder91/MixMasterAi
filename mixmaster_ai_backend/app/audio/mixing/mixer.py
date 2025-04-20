"""
MixMaster AI - Mixing Module

This module provides functions for mixing vocal and beat tracks together,
including level balancing, frequency masking reduction, and stereo placement.
"""

import os
import numpy as np
import librosa
import soundfile as sf
from typing import Dict, Any, Optional, Tuple
import logging
from scipy import signal

# Setup logging
logger = logging.getLogger(__name__)

def mix_tracks(
    vocal_file: str,
    beat_file: str,
    output_file: str,
    settings: Dict[str, Any] = None
) -> bool:
    """
    Mix vocal and beat tracks together.
    
    Parameters:
    - vocal_file: Path to processed vocal file
    - beat_file: Path to processed beat file
    - output_file: Path to output mixed file
    - settings: Dictionary of mixing settings
    
    Returns:
    - bool: True if successful, False otherwise
    """
    try:
        # Load default settings if none provided
        if settings is None:
            settings = {
                "vocal_level": 0.0,     # dB
                "beat_level": -3.0,     # dB
                "reduce_masking": True,
                "stereo_placement": True,
                "bus_processing": True,
                "target_lufs": -14.0    # LUFS
            }
        
        # Load audio files
        y_vocal, sr_vocal = librosa.load(vocal_file, sr=None)
        y_beat, sr_beat = librosa.load(beat_file, sr=None)
        
        # Ensure same sample rate
        if sr_vocal != sr_beat:
            logger.info(f"Resampling beat to match vocal sample rate ({sr_vocal}Hz)")
            y_beat = librosa.resample(y_beat, orig_sr=sr_beat, target_sr=sr_vocal)
            sr_beat = sr_vocal
        
        # Convert to stereo if mono
        if len(y_vocal.shape) == 1:
            y_vocal = np.stack([y_vocal, y_vocal])
        
        if len(y_beat.shape) == 1:
            y_beat = np.stack([y_beat, y_beat])
        
        # Apply level adjustments
        vocal_gain = 10 ** (settings["vocal_level"] / 20)
        beat_gain = 10 ** (settings["beat_level"] / 20)
        
        y_vocal = y_vocal * vocal_gain
        y_beat = y_beat * beat_gain
        
        # Apply frequency masking reduction if enabled
        if settings["reduce_masking"]:
            y_vocal, y_beat = reduce_frequency_masking(y_vocal, y_beat, sr_vocal)
        
        # Apply stereo placement if enabled
        if settings["stereo_placement"]:
            y_vocal, y_beat = apply_stereo_placement(y_vocal, y_beat)
        
        # Mix tracks
        y_mixed = y_vocal + y_beat
        
        # Apply bus processing if enabled
        if settings["bus_processing"]:
            y_mixed = apply_bus_processing(y_mixed, sr_vocal)
        
        # Apply final limiting and loudness normalization
        y_mixed = normalize_loudness(y_mixed, sr_vocal, target_lufs=settings["target_lufs"])
        
        # Save mixed audio
        sf.write(output_file, y_mixed.T, sr_vocal)
        
        return True
    
    except Exception as e:
        logger.error(f"Error mixing tracks: {str(e)}")
        return False

def reduce_frequency_masking(
    y_vocal: np.ndarray,
    y_beat: np.ndarray,
    sr: int
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Reduce frequency masking between vocal and beat tracks.
    
    Parameters:
    - y_vocal: Vocal audio signal
    - y_beat: Beat audio signal
    - sr: Sample rate
    
    Returns:
    - Tuple[np.ndarray, np.ndarray]: Processed vocal and beat signals
    """
    # Convert to mono for analysis
    y_vocal_mono = np.mean(y_vocal, axis=0)
    y_beat_mono = np.mean(y_beat, axis=0)
    
    # Compute STFTs
    D_vocal = librosa.stft(y_vocal_mono)
    D_beat = librosa.stft(y_beat_mono)
    
    # Compute magnitude spectrograms
    S_vocal = np.abs(D_vocal)
    S_beat = np.abs(D_beat)
    
    # Identify frequency masking
    # For each time-frequency bin, check if beat is masking vocal
    mask = S_beat > S_vocal * 2  # Beat is significantly louder
    
    # Create a filter to reduce masking
    filter_mask = np.ones_like(S_beat)
    filter_mask[mask] = 0.7  # Reduce beat by 30% where it masks vocals
    
    # Apply filter to beat STFT
    D_beat_filtered = D_beat * filter_mask
    
    # Convert back to time domain
    y_beat_filtered_mono = librosa.istft(D_beat_filtered)
    
    # Apply to stereo beat
    # This is a simplified approach - in a real implementation, 
    # we would process each channel separately
    for i in range(y_beat.shape[0]):
        y_beat[i] = librosa.istft(librosa.stft(y_beat[i]) * filter_mask)
    
    return y_vocal, y_beat

def apply_stereo_placement(
    y_vocal: np.ndarray,
    y_beat: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Apply stereo placement to vocal and beat tracks.
    
    Parameters:
    - y_vocal: Vocal audio signal
    - y_beat: Beat audio signal
    
    Returns:
    - Tuple[np.ndarray, np.ndarray]: Processed vocal and beat signals
    """
    # Center the vocals slightly
    # Calculate mid and side components
    vocal_mid = (y_vocal[0] + y_vocal[1]) / 2
    vocal_side = (y_vocal[0] - y_vocal[1]) / 2
    
    # Reduce side component to center the vocals more
    vocal_side = vocal_side * 0.8
    
    # Recombine mid and side
    y_vocal[0] = vocal_mid + vocal_side
    y_vocal[1] = vocal_mid - vocal_side
    
    # Widen the beat slightly
    # Calculate mid and side components
    beat_mid = (y_beat[0] + y_beat[1]) / 2
    beat_side = (y_beat[0] - y_beat[1]) / 2
    
    # Increase side component to widen the beat
    beat_side = beat_side * 1.2
    
    # Recombine mid and side
    y_beat[0] = beat_mid + beat_side
    y_beat[1] = beat_mid - beat_side
    
    return y_vocal, y_beat

def apply_bus_processing(
    y_mixed: np.ndarray,
    sr: int
) -> np.ndarray:
    """
    Apply processing to the mixed bus.
    
    Parameters:
    - y_mixed: Mixed audio signal
    - sr: Sample rate
    
    Returns:
    - np.ndarray: Processed mixed signal
    """
    # Apply gentle bus compression
    # Convert threshold from dB to linear
    threshold_linear = 10 ** (-10 / 20)  # -10 dB threshold
    ratio = 1.5  # Gentle ratio
    
    # Initialize gain reduction array
    gain_reduction = np.ones_like(y_mixed[0])
    
    # Calculate sample-by-sample gain reduction
    # This is a simplified model of compression
    for i in range(1, len(y_mixed[0])):
        # Calculate instantaneous level (max of both channels)
        level = max(abs(y_mixed[0, i]), abs(y_mixed[1, i]))
        
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
    
    # Apply gain reduction to both channels
    for i in range(y_mixed.shape[0]):
        y_mixed[i] = y_mixed[i] * gain_reduction
    
    # Apply gentle bus EQ
    # Slight high shelf boost
    b, a = signal.butter(2, 8000 / (sr / 2), 'highpass')
    high_freq = np.zeros_like(y_mixed)
    for i in range(y_mixed.shape[0]):
        high_freq[i] = signal.lfilter(b, a, y_mixed[i])
    
    # Add boosted high frequencies back
    gain = 10 ** (1 / 20)  # 1 dB boost
    y_mixed = y_mixed - high_freq + (high_freq * gain)
    
    return y_mixed

def normalize_loudness(
    y: np.ndarray,
    sr: int,
    target_lufs: float = -14.0
) -> np.ndarray:
    """
    Normalize loudness to target LUFS and apply limiting.
    
    Parameters:
    - y: Audio signal
    - sr: Sample rate
    - target_lufs: Target loudness in LUFS
    
    Returns:
    - np.ndarray: Normalized and limited audio signal
    """
    # Convert to mono for LUFS calculation
    y_mono = np.mean(y, axis=0)
    
    # Calculate current LUFS (simplified approximation)
    # In a real implementation, use a proper LUFS measurement library
    rms = np.sqrt(np.mean(y_mono**2))
    current_lufs = -23.0 - 10 * np.log10(np.mean(y_mono**2) + 1e-10)
    
    # Calculate gain needed
    gain_db = target_lufs - current_lufs
    gain_linear = 10 ** (gain_db / 20)
    
    # Apply gain
    y_normalized = y * gain_linear
    
    # Apply limiting to prevent clipping
    y_limited = apply_limiter(y_normalized)
    
    return y_limited

def apply_limiter(y: np.ndarray, threshold: float = 0.95) -> np.ndarray:
    """
    Apply a simple brickwall limiter to prevent clipping.
    
    Parameters:
    - y: Audio signal
    - threshold: Limiting threshold (0-1)
    
    Returns:
    - np.ndarray: Limited audio signal
    """
    # Find peaks above threshold
    max_vals = np.max(np.abs(y), axis=0)
    peaks = max_vals > threshold
    
    # Apply limiting only where needed
    if np.any(peaks):
        # Create gain reduction curve
        gain_reduction = np.ones_like(max_vals)
        gain_reduction[peaks] = threshold / max_vals[peaks]
        
        # Smooth gain reduction curve
        # Simple moving average for smoothing
        window_size = 100
        smoothed_gain = np.zeros_like(gain_reduction)
        for i in range(len(gain_reduction)):
            start = max(0, i - window_size // 2)
            end = min(len(gain_reduction), i + window_size // 2)
            smoothed_gain[i] = np.min(gain_reduction[start:end])
        
        # Apply smoothed gain reduction to both channels
        for i in range(y.shape[0]):
            y[i] = y[i] * smoothed_gain
    
    return y
