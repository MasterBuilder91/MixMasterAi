import React, { useState, useEffect, useRef } from 'react';
import { FiPlay, FiPause, FiDownload, FiVolume2, FiVolumeX } from 'react-icons/fi';
import { Howl } from 'howler';

const AudioPlayer = ({ url }) => {
  const [playing, setPlaying] = useState(false);
  const [duration, setDuration] = useState(0);
  const [seek, setSeek] = useState(0);
  const [volume, setVolume] = useState(0.8);
  const [muted, setMuted] = useState(false);
  const [loading, setLoading] = useState(true);
  
  const soundRef = useRef(null);
  const seekBarRef = useRef(null);
  const seekIntervalRef = useRef(null);

  useEffect(() => {
    // Clean up previous sound instance
    if (soundRef.current) {
      soundRef.current.unload();
    }

    // Create new Howl instance
    soundRef.current = new Howl({
      src: [url],
      html5: true,
      onload: () => {
        setDuration(soundRef.current.duration());
        setLoading(false);
      },
      onplay: () => {
        setPlaying(true);
        startSeekInterval();
      },
      onpause: () => {
        setPlaying(false);
        clearSeekInterval();
      },
      onstop: () => {
        setPlaying(false);
        setSeek(0);
        clearSeekInterval();
      },
      onend: () => {
        setPlaying(false);
        setSeek(0);
        clearSeekInterval();
      },
      onseek: () => {
        setSeek(soundRef.current.seek());
      }
    });

    // Set initial volume
    soundRef.current.volume(volume);

    // Clean up on unmount
    return () => {
      if (soundRef.current) {
        soundRef.current.unload();
      }
      clearSeekInterval();
    };
  }, [url]);

  const startSeekInterval = () => {
    clearSeekInterval();
    seekIntervalRef.current = setInterval(() => {
      if (soundRef.current && soundRef.current.playing()) {
        setSeek(soundRef.current.seek());
      }
    }, 1000);
  };

  const clearSeekInterval = () => {
    if (seekIntervalRef.current) {
      clearInterval(seekIntervalRef.current);
      seekIntervalRef.current = null;
    }
  };

  const togglePlayPause = () => {
    if (!soundRef.current) return;
    
    if (playing) {
      soundRef.current.pause();
    } else {
      soundRef.current.play();
    }
  };

  const handleSeekChange = (e) => {
    const value = parseFloat(e.target.value);
    setSeek(value);
    if (soundRef.current) {
      soundRef.current.seek(value);
    }
  };

  const handleVolumeChange = (e) => {
    const value = parseFloat(e.target.value);
    setVolume(value);
    if (soundRef.current) {
      soundRef.current.volume(value);
    }
    if (value === 0) {
      setMuted(true);
    } else {
      setMuted(false);
    }
  };

  const toggleMute = () => {
    if (!soundRef.current) return;
    
    if (muted) {
      soundRef.current.volume(volume || 0.8);
      setMuted(false);
    } else {
      soundRef.current.volume(0);
      setMuted(true);
    }
  };

  const formatTime = (seconds) => {
    if (isNaN(seconds)) return '0:00';
    
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = url;
    link.download = 'mixmaster_track.wav';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
      <div className="flex items-center justify-between mb-4">
        <button
          onClick={togglePlayPause}
          disabled={loading}
          className={`w-12 h-12 rounded-full flex items-center justify-center transition-colors ${
            loading 
              ? 'bg-gray-700 text-gray-500 cursor-not-allowed' 
              : 'bg-purple-600 hover:bg-purple-700 text-white'
          }`}
        >
          {loading ? (
            <span className="animate-pulse">...</span>
          ) : playing ? (
            <FiPause size={20} />
          ) : (
            <FiPlay size={20} className="ml-1" />
          )}
        </button>

        <div className="flex-1 mx-4">
          <div className="flex justify-between text-sm text-gray-400 mb-1">
            <span>{formatTime(seek)}</span>
            <span>{formatTime(duration)}</span>
          </div>
          <input
            ref={seekBarRef}
            type="range"
            min="0"
            max={duration || 100}
            step="0.01"
            value={seek}
            onChange={handleSeekChange}
            className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-purple-500"
            disabled={loading}
          />
        </div>

        <div className="flex items-center">
          <button
            onClick={toggleMute}
            className="text-gray-300 hover:text-white mr-2"
          >
            {muted ? <FiVolumeX size={20} /> : <FiVolume2 size={20} />}
          </button>
          <input
            type="range"
            min="0"
            max="1"
            step="0.01"
            value={muted ? 0 : volume}
            onChange={handleVolumeChange}
            className="w-20 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-purple-500"
          />
        </div>
      </div>

      <button
        onClick={handleDownload}
        className="w-full py-2 rounded-lg flex items-center justify-center font-bold bg-green-600 hover:bg-green-700 text-white transition-colors"
      >
        <FiDownload className="mr-2" />
        Download Track
      </button>
    </div>
  );
};

export default AudioPlayer;
