import React, { useState, useRef } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';

const FileUpload = ({ 
  processingOptions, 
  onUploadStart, 
  onUploadProgress, 
  onUploadComplete, 
  onUploadError,
  isUploading,
  uploadProgress
}) => {
  const [vocalFile, setVocalFile] = useState(null);
  const [beatFile, setBeatFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);
  const beatInputRef = useRef(null);
  const { user } = useAuth();

  const handleVocalChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setVocalFile(e.target.files[0]);
    }
  };

  const handleBeatChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setBeatFile(e.target.files[0]);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      // Check file types and assign accordingly
      Array.from(e.dataTransfer.files).forEach(file => {
        if (file.type.includes('audio')) {
          if (!vocalFile) {
            setVocalFile(file);
          } else if (!beatFile) {
            setBeatFile(file);
          }
        }
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!vocalFile || !beatFile) {
      alert('Please upload both vocal and beat files');
      return;
    }
    
    onUploadStart();
    
    const formData = new FormData();
    formData.append('vocals', vocalFile);
    formData.append('beat', beatFile);
    formData.append('genre', processingOptions.genre);
    formData.append('reverb_amount', processingOptions.reverbAmount);
    formData.append('compression_amount', processingOptions.compressionAmount);
    formData.append('output_format', processingOptions.outputFormat);
    
    try {
      // Get auth token
      const token = localStorage.getItem('token');
      
      const response = await axios.post('/api/processing/mix', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${token}`
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onUploadProgress(percentCompleted);
        }
      });
      
      onUploadComplete(response.data);
    } catch (error) {
      console.error('Upload error:', error);
      onUploadError(error);
    }
  };

  return (
    <div className="mt-8">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div 
          className={`border-2 border-dashed rounded-lg p-8 text-center ${
            dragActive ? 'border-purple-500 bg-purple-900/20' : 'border-gray-600'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <div className="flex flex-col md:flex-row space-y-4 md:space-y-0 md:space-x-4">
            {/* Vocal File Upload */}
            <div className="flex-1">
              <div className="mb-2 text-lg font-semibold">Vocals</div>
              <div 
                className={`border border-gray-700 rounded-lg p-4 h-32 flex flex-col items-center justify-center cursor-pointer hover:bg-gray-800 transition-colors ${
                  vocalFile ? 'bg-gray-800' : ''
                }`}
                onClick={() => fileInputRef.current.click()}
              >
                {vocalFile ? (
                  <>
                    <div className="text-green-400 mb-2">
                      <svg className="w-8 h-8 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                      </svg>
                    </div>
                    <div className="text-sm truncate max-w-full">{vocalFile.name}</div>
                  </>
                ) : (
                  <>
                    <div className="text-gray-400 mb-2">
                      <svg className="w-8 h-8 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path>
                      </svg>
                    </div>
                    <div className="text-sm text-gray-400">Click to upload vocals</div>
                  </>
                )}
                <input 
                  type="file" 
                  ref={fileInputRef}
                  onChange={handleVocalChange}
                  accept="audio/*"
                  className="hidden"
                />
              </div>
            </div>
            
            {/* Beat File Upload */}
            <div className="flex-1">
              <div className="mb-2 text-lg font-semibold">Beat</div>
              <div 
                className={`border border-gray-700 rounded-lg p-4 h-32 flex flex-col items-center justify-center cursor-pointer hover:bg-gray-800 transition-colors ${
                  beatFile ? 'bg-gray-800' : ''
                }`}
                onClick={() => beatInputRef.current.click()}
              >
                {beatFile ? (
                  <>
                    <div className="text-green-400 mb-2">
                      <svg className="w-8 h-8 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                      </svg>
                    </div>
                    <div className="text-sm truncate max-w-full">{beatFile.name}</div>
                  </>
                ) : (
                  <>
                    <div className="text-gray-400 mb-2">
                      <svg className="w-8 h-8 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3"></path>
                      </svg>
                    </div>
                    <div className="text-sm text-gray-400">Click to upload beat</div>
                  </>
                )}
                <input 
                  type="file" 
                  ref={beatInputRef}
                  onChange={handleBeatChange}
                  accept="audio/*"
                  className="hidden"
                />
              </div>
            </div>
          </div>
          
          <div className="mt-4 text-gray-400 text-sm">
            Drag and drop audio files or click to browse
          </div>
        </div>
        
        {isUploading ? (
          <div className="mt-6">
            <div className="text-center mb-2">Uploading... {uploadProgress}%</div>
            <div className="w-full bg-gray-700 rounded-full h-2.5">
              <div 
                className="bg-purple-600 h-2.5 rounded-full" 
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
          </div>
        ) : (
          <button 
            type="submit"
            disabled={!vocalFile || !beatFile}
            className={`w-full py-3 rounded-lg font-bold transition-colors ${
              !vocalFile || !beatFile 
                ? 'bg-gray-700 cursor-not-allowed' 
                : 'bg-purple-600 hover:bg-purple-700 text-white'
            }`}
          >
            Mix & Master
          </button>
        )}
      </form>
    </div>
  );
};

export default FileUpload;
