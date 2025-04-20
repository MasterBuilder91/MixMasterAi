"""
MixMaster AI - Vocal Processing Module

This module provides functions for processing vocal tracks, including
EQ, compression, de-essing, and spatial effects.
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

def process_vocals(
    input_file: str,
    output_file: str,
    settings: Dict[str, Any] = None
) -> bool:
    """
    Process a vocal track with EQ, compression, and effects.
    
    Parameters:
    - input_file: Path to input vocal file
    - output_file: Path to output processed file
    - settings: Dictionary of processing settings
    
    Returns:
    - bool: True if successful, False otherwise
    """
    try:
        # Load default settings if none provided
        if settings is None:
            settings = {
                "eq_low_cut": 80,       # Hz
                "eq_high_cut": 18000,   # Hz
                "eq_low_shelf": -3,     # dB
                "eq_high_shelf": 2,     # dB
                "eq_mid_freq": 3000,    # Hz
                "eq_mid_gain": 2,       # dB
                "eq_mid_q": 1.0,        # Q factor
                "compression_threshold": -20,  # dB
                "compression_ratio": 4,  # ratio
                "compression_attack": 5,  # ms
                "compression_release": 50,  # ms
                "de_ess": True,
                "de_ess_threshold": -10,  # dB
                "reverb_amount": 0.2,    # 0-1
                "delay_amount": 0.1,     # 0-1
                "stereo_width": 0.5      # 0-1
            }
        
        # Load audio file
        y, sr = librosa.load(input_file, sr=None)
        
        # Apply processing chain
        y_processed = y.copy()
        
        # Apply EQ
        y_processed = apply_vocal_eq(
            y_processed, 
            sr, 
            low_cut=settings["eq_low_cut"],
            high_cut=settings["eq_high_cut"],
            low_shelf=settings["eq_low_shelf"],
            high_shelf=settings["eq_high_shelf"],
            mid_freq=settings["eq_mid_freq"],
            mid_gain=settings["eq_mid_gain"],
            mid_q=settings["eq_mid_q"]
        )
        
        # Apply compression
        y_processed = apply_compression(
            y_processed,
            threshold=settings["compression_threshold"],
            ratio=settings["compression_ratio"],
            attack=settings["compression_attack"],
            release=settings["compression_release"]
        )
        
        # Apply de-essing if enabled
        if settings["de_ess"]:
            y_processed = apply_de_essing(
                y_processed,
                sr,
                threshold=settings["de_ess_threshold"]
            )
        
        # Apply spatial effects
        y_processed = apply_spatial_effects(
            y_processed,
            sr,
            reverb_amount=settings["reverb_amount"],
            delay_amount=settings["delay_amount"],
            stereo_width=settings["stereo_width"]
        )
        
        # Save processed audio
        sf.write(output_file, y_processed, sr)
        
        return True
    
    except Exception as e:
        logger.error(f"Error processing vocals {input_file}: {str(e)}")
        return False

def apply_vocal_eq(
    y: np.ndarray,
    sr: int,
    low_cut: float = 80,
    high_cut: float = 18000,
    low_shelf: float = -3,
    high_shelf: float = 2,
    mid_freq: float = 3000,
    mid_gain: float = 2,
    mid_q: float = 1.0
) -> np.ndarray:
    """
    Apply EQ to vocal track.
    
    Parameters:
    - y: Audio signal
    - sr: Sample rate
    - low_cut: Low cut frequency (Hz)
    - high_cut: High cut frequency (Hz)
    - low_shelf: Low shelf gain (dB)
    - high_shelf: High shelf gain (dB)
    - mid_freq: Mid band frequency (Hz)
    - mid_gain: Mid band gain (dB)
    - mid_q: Mid band Q factor
    
    Returns:
    - np.ndarray: Processed audio signal
    """
    # Apply high-pass filter (low cut)
    if low_cut > 0:
        b, a = signal.butter(4, low_cut / (sr / 2), 'highpass')
        y = signal.lfilter(b, a, y)
    
    # Apply low-pass filter (high cut)
    if high_cut < sr / 2:
        b, a = signal.butter(4, high_cut / (sr / 2), 'lowpass')
        y = signal.lfilter(b, a, y)
    
    # Apply low shelf filter
    if low_shelf != 0:
        # Convert dB to gain
        gain = 10 ** (low_shelf / 20)
        # Simple implementation of shelf filter
        b, a = signal.butter(2, 300 / (sr / 2), 'lowpass')
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
    
    # Apply mid band EQ
    if mid_gain != 0:
        # Convert dB to gain
        gain = 10 ** (mid_gain / 20)
        # Simple implementation of peaking filter
        bandwidth = mid_freq / mid_q
        low_edge = max(20, mid_freq - bandwidth / 2)
        high_edge = min(sr / 2 - 1, mid_freq + bandwidth / 2)
        
        b, a = signal.butter(2, [low_edge / (sr / 2), high_edge / (sr / 2)], 'bandpass')
        mid_freq_band = signal.lfilter(b, a, y)
        y = y - mid_freq_band + (mid_freq_band * gain)
    
    return y

def apply_compression(
    y: np.ndarray,
    threshold: float = -20,
    ratio: float = 4,
    attack: float = 5,
    release: float = 50
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

def apply_de_essing(
    y: np.ndarray,
    sr: int,
    threshold: float = -10
) -> np.ndarray:
    """
    Apply de-essing to reduce sibilance in vocals.
    
    Parameters:
    - y: Audio signal
    - sr: Sample rate
    - threshold: Threshold in dB
    
    Returns:
    - np.ndarray: De-essed audio signal
    """
    # Convert threshold from dB to linear
    threshold_linear = 10 ** (threshold / 20)
    
    # Extract sibilance band (5-8kHz)
    b, a = signal.butter(4, [5000 / (sr / 2), 8000 / (sr / 2)], 'bandpass')
    sibilance_band = signal.lfilter(b, a, y)
    
    # Calculate envelope of sibilance band
    envelope = np.abs(sibilance_band)
    
    # Smooth envelope
    b, a = signal.butter(2, 100 / (sr / 2), 'lowpass')
    envelope_smooth = signal.lfilter(b, a, envelope)
    
    # Calculate gain reduction
    gain_reduction = np.ones_like(y)
    mask = envelope_smooth > threshold_linear
    gain_reduction[mask] = threshold_linear / envelope_smooth[mask]
    
    # Apply gain reduction to sibilance band only
    sibilance_band_reduced = sibilance_band * gain_reduction
    
    # Recombine with original signal
    y_de_essed = y - sibilance_band + sibilance_band_reduced
    
    return y_de_essed

def apply_spatial_effects(
    y: np.ndarray,
    sr: int,
    reverb_amount: float = 0.2,
    delay_amount: float = 0.1,
    stereo_width: float = 0.5
) -> np.ndarray:
    """
    Apply spatial effects like reverb, delay, and stereo widening.
    
    Parameters:
    - y: Audio signal
    - sr: Sample rate
    - reverb_amount: Amount of reverb (0-1)
    - delay_amount: Amount of delay (0-1)
    - stereo_width: Amount of stereo widening (0-1)
    
    Returns:
    - np.ndarray: Processed audio signal
    """
    # Check if input is mono or stereo
    is_mono = len(y.shape) == 1
    
    # Convert mono to stereo if needed
    if is_mono:
        y = np.stack([y, y])
    
    # Apply stereo widening
    if stereo_width > 0 and not is_mono:
        # Calculate mid and side signals
        mid = (y[0] + y[1]) / 2
        side = (y[0] - y[1]) / 2
        
        # Apply width factor to side signal
        side = side * (1 + stereo_width)
        
        # Recombine mid and side
        y[0] = mid + side
        y[1] = mid - side
    
    # Apply simple delay effect
    if delay_amount > 0:
        # Calculate delay time in samples
        delay_samples = int(sr * 0.25)  # 250ms delay
        
        # Create delayed signal
        y_delayed = np.zeros_like(y)
        y_delayed[:, delay_samples:] = y[:, :-delay_samples] * delay_amount
        
        # Mix with original
        y = y + y_delayed
    
    # Apply simple reverb effect
    if reverb_amount > 0:
        # Create a simple reverb impulse response
        reverb_time = int(sr * 1.0)  # 1 second reverb
        impulse = np.zeros(reverb_time)
        
        # Exponential decay
        decay = np.exp(-np.arange(reverb_time) / (sr * 0.5))
        impulse[0] = 1
        impulse[1:] = np.random.randn(reverb_time - 1) * decay[1:]
        
        # Apply convolution for each channel
        y_reverb = np.zeros_like(y)
        for i in range(y.shape[0]):
            y_reverb[i] = signal.convolve(y[i], impulse, mode='same') * reverb_amount
        
        # Mix with original
        y = y + y_reverb
    
    # Normalize to prevent clipping
    max_val = np.max(np.abs(y))
    if max_val > 1.0:
        y = y / max_val
    
    # Convert back to mono if input was mono
    if is_mono:
        y = (y[0] + y[1]) / 2
    
    return y
