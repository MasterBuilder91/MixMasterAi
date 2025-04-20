"""
MixMaster AI - Mastering Module

This module provides functions for mastering mixed tracks, including
EQ finalization, multi-band compression, stereo enhancement, and limiting.
"""

import os
import numpy as np
import librosa
import soundfile as sf
from typing import Dict, Any, Optional
import logging
from scipy import signal
import matchering

# Setup logging
logger = logging.getLogger(__name__)

def master_track(
    input_file: str,
    output_file: str,
    reference_file: Optional[str] = None,
    settings: Dict[str, Any] = None
) -> bool:
    """
    Master a mixed track to prepare it for distribution.
    
    Parameters:
    - input_file: Path to input mixed file
    - output_file: Path to output mastered file
    - reference_file: Optional path to reference track for matching
    - settings: Dictionary of mastering settings
    
    Returns:
    - bool: True if successful, False otherwise
    """
    try:
        # Load default settings if none provided
        if settings is None:
            settings = {
                "use_matchering": reference_file is not None,
                "eq_low_shelf": 1.0,    # dB
                "eq_high_shelf": 1.5,   # dB
                "multiband_low_thresh": -24.0,  # dB
                "multiband_mid_thresh": -18.0,  # dB
                "multiband_high_thresh": -24.0,  # dB
                "stereo_enhance": 0.2,  # 0-1
                "limiter_threshold": -1.0,  # dB
                "target_lufs": -14.0    # LUFS
            }
        
        # If reference file is provided and matchering is enabled, use it
        if settings["use_matchering"] and reference_file is not None:
            try:
                # Use Matchering for reference-based mastering
                matchering.process(
                    target=input_file,
                    reference=reference_file,
                    results=[
                        matchering.pcm24(output_file)
                    ]
                )
                return True
            except Exception as e:
                logger.error(f"Matchering failed: {str(e)}. Falling back to standard mastering.")
                # Fall back to standard mastering if matchering fails
        
        # Load audio file
        y, sr = librosa.load(input_file, sr=None)
        
        # Apply processing chain
        y_processed = y.copy()
        
        # Apply EQ finalization
        y_processed = apply_eq_finalization(
            y_processed, 
            sr, 
            low_shelf=settings["eq_low_shelf"],
            high_shelf=settings["eq_high_shelf"]
        )
        
        # Apply multi-band compression
        y_processed = apply_multiband_compression(
            y_processed,
            sr,
            low_thresh=settings["multiband_low_thresh"],
            mid_thresh=settings["multiband_mid_thresh"],
            high_thresh=settings["multiband_high_thresh"]
        )
        
        # Apply stereo enhancement
        if len(y_processed.shape) > 1:  # Only if stereo
            y_processed = apply_stereo_enhancement(
                y_processed,
                amount=settings["stereo_enhance"]
            )
        
        # Apply limiting and loudness normalization
        y_processed = apply_limiting_and_normalization(
            y_processed,
            sr,
            threshold=settings["limiter_threshold"],
            target_lufs=settings["target_lufs"]
        )
        
        # Save mastered audio
        sf.write(output_file, y_processed, sr)
        
        return True
    
    except Exception as e:
        logger.error(f"Error mastering track {input_file}: {str(e)}")
        return False

def apply_eq_finalization(
    y: np.ndarray,
    sr: int,
    low_shelf: float = 1.0,
    high_shelf: float = 1.5
) -> np.ndarray:
    """
    Apply final EQ adjustments for tonal balance.
    
    Parameters:
    - y: Audio signal
    - sr: Sample rate
    - low_shelf: Low shelf gain in dB
    - high_shelf: High shelf gain in dB
    
    Returns:
    - np.ndarray: EQ'd audio signal
    """
    # Process each channel if stereo
    if len(y.shape) > 1:
        for i in range(y.shape[0]):
            y[i] = apply_eq_finalization(y[i], sr, low_shelf, high_shelf)
        return y
    
    # Apply low shelf filter
    if low_shelf != 0:
        # Convert dB to gain
        gain = 10 ** (low_shelf / 20)
        # Simple implementation of shelf filter
        b, a = signal.butter(2, 200 / (sr / 2), 'lowpass')
        low_freq = signal.lfilter(b, a, y)
        y = y - low_freq + (low_freq * gain)
    
    # Apply high shelf filter
    if high_shelf != 0:
        # Convert dB to gain
        gain = 10 ** (high_shelf / 20)
        # Simple implementation of shelf filter
        b, a = signal.butter(2, 8000 / (sr / 2), 'highpass')
        high_freq = signal.lfilter(b, a, y)
        y = y - high_freq + (high_freq * gain)
    
    return y

def apply_multiband_compression(
    y: np.ndarray,
    sr: int,
    low_thresh: float = -24.0,
    mid_thresh: float = -18.0,
    high_thresh: float = -24.0
) -> np.ndarray:
    """
    Apply multi-band compression.
    
    Parameters:
    - y: Audio signal
    - sr: Sample rate
    - low_thresh: Low band threshold in dB
    - mid_thresh: Mid band threshold in dB
    - high_thresh: High band threshold in dB
    
    Returns:
    - np.ndarray: Compressed audio signal
    """
    # Process each channel if stereo
    if len(y.shape) > 1:
        for i in range(y.shape[0]):
            y[i] = apply_multiband_compression(y[i], sr, low_thresh, mid_thresh, high_thresh)
        return y
    
    # Split into frequency bands
    # Low band (0-200Hz)
    b, a = signal.butter(4, 200 / (sr / 2), 'lowpass')
    low_band = signal.lfilter(b, a, y)
    
    # High band (5000Hz+)
    b, a = signal.butter(4, 5000 / (sr / 2), 'highpass')
    high_band = signal.lfilter(b, a, y)
    
    # Mid band (everything else)
    mid_band = y - low_band - high_band
    
    # Apply compression to each band
    low_band_compressed = apply_compression(low_band, threshold=low_thresh, ratio=3.0)
    mid_band_compressed = apply_compression(mid_band, threshold=mid_thresh, ratio=2.0)
    high_band_compressed = apply_compression(high_band, threshold=high_thresh, ratio=4.0)
    
    # Recombine bands
    y_compressed = low_band_compressed + mid_band_compressed + high_band_compressed
    
    return y_compressed

def apply_compression(
    y: np.ndarray,
    threshold: float = -20.0,
    ratio: float = 2.0,
    attack: float = 5.0,
    release: float = 50.0
) -> np.ndarray:
    """
    Apply dynamic range compression to audio signal.
    
    Parameters:
    - y: Audio signal
    - threshold: Threshold in dB
    - ratio: Compression ratio
    - attack: Attack time in ms
    - release: Release time in ms
    
    Returns:
    - np.ndarray: Compressed audio signal
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
    y_compressed = y * gain_reduction
    
    # Apply makeup gain
    # Calculate RMS of original and compressed signals
    rms_original = np.sqrt(np.mean(y**2))
    rms_compressed = np.sqrt(np.mean(y_compressed**2))
    
    # Apply makeup gain to match original RMS
    if rms_compressed > 0:
        makeup_gain = rms_original / rms_compressed
        y_compressed = y_compressed * makeup_gain
    
    return y_compressed

def apply_stereo_enhancement(
    y: np.ndarray,
    amount: float = 0.2
) -> np.ndarray:
    """
    Apply stereo enhancement.
    
    Parameters:
    - y: Stereo audio signal
    - amount: Enhancement amount (0-1)
    
    Returns:
    - np.ndarray: Enhanced stereo signal
    """
    # Calculate mid and side signals
    mid = (y[0] + y[1]) / 2
    side = (y[0] - y[1]) / 2
    
    # Enhance side signal
    side = side * (1 + amount)
    
    # Recombine mid and side
    y[0] = mid + side
    y[1] = mid - side
    
    return y

def apply_limiting_and_normalization(
    y: np.ndarray,
    sr: int,
    threshold: float = -1.0,
    target_lufs: float = -14.0
) -> np.ndarray:
    """
    Apply limiting and loudness normalization.
    
    Parameters:
    - y: Audio signal
    - sr: Sample rate
    - threshold: Limiter threshold in dB
    - target_lufs: Target loudness in LUFS
    
    Returns:
    - np.ndarray: Limited and normalized audio signal
    """
    # Convert threshold from dB to linear
    threshold_linear = 10 ** (threshold / 20)
    
    # Calculate current LUFS (simplified approximation)
    # In a real implementation, use a proper LUFS measurement library
    if len(y.shape) > 1:
        y_mono = np.mean(y, axis=0)
    else:
        y_mono = y
    
    current_lufs = -23.0 - 10 * np.log10(np.mean(y_mono**2) + 1e-10)
    
    # Calculate gain needed
    gain_db = target_lufs - current_lufs
    gain_linear = 10 ** (gain_db / 20)
    
    # Apply gain
    y_normalized = y * gain_linear
    
    # Apply limiting
    # Process each channel if stereo
    if len(y_normalized.shape) > 1:
        for i in range(y_normalized.shape[0]):
            y_normalized[i] = apply_limiter(y_normalized[i], threshold_linear)
    else:
        y_normalized = apply_limiter(y_normalized, threshold_linear)
    
    return y_normalized

def apply_limiter(
    y: np.ndarray,
    threshold: float = 0.9
) -> np.ndarray:
    """
    Apply a brickwall limiter to prevent clipping.
    
    Parameters:
    - y: Audio signal
    - threshold: Limiting threshold (0-1)
    
    Returns:
    - np.ndarray: Limited audio signal
    """
    # Find peaks above threshold
    peaks = np.abs(y) > threshold
    
    # Apply limiting only where needed
    if np.any(peaks):
        # Create gain reduction curve
        gain_reduction = np.ones_like(y)
        gain_reduction[peaks] = threshold / np.abs(y[peaks])
        
        # Smooth gain reduction curve
        # Simple moving average for smoothing
        window_size = 100
        smoothed_gain = np.zeros_like(gain_reduction)
        for i in range(len(gain_reduction)):
            start = max(0, i - window_size // 2)
            end = min(len(gain_reduction), i + window_size // 2)
            smoothed_gain[i] = np.min(gain_reduction[start:end])
        
        # Apply smoothed gain reduction
        y = y * smoothed_gain
    
    return y
