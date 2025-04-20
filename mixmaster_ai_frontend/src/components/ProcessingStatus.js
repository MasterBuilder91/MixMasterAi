import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';

const ProcessingStatus = ({ jobId, status, onProcessingComplete }) => {
  const [currentStatus, setCurrentStatus] = useState(status || 'processing');
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const { user } = useAuth();

  useEffect(() => {
    if (!jobId) return;
    
    let intervalId;
    
    const checkStatus = async () => {
      try {
        // Get auth token
        const token = localStorage.getItem('token');
        
        const response = await axios.get(`/api/processing/status/${jobId}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        const { status, progress, result_url } = response.data;
        
        setCurrentStatus(status);
        setProgress(progress || 0);
        
        if (status === 'complete') {
          clearInterval(intervalId);
          onProcessingComplete('complete', result_url);
          
          // Update user data if needed (e.g., increment processed songs count)
          if (user && user.accountType === 'pay-per-use') {
            // We don't need to update the UI here as the backend will handle credit deduction
            // and the user will see updated credits on next page load
          }
        } else if (status === 'error') {
          clearInterval(intervalId);
          setError(response.data.error || 'An error occurred during processing');
          onProcessingComplete('error');
        }
      } catch (error) {
        console.error('Error checking job status:', error);
        setError('Failed to check processing status');
        clearInterval(intervalId);
        onProcessingComplete('error');
      }
    };
    
    // Check immediately
    checkStatus();
    
    // Then check every 3 seconds
    intervalId = setInterval(checkStatus, 3000);
    
    return () => {
      clearInterval(intervalId);
    };
  }, [jobId, onProcessingComplete, user]);

  const getStatusText = () => {
    switch (currentStatus) {
      case 'processing':
        return 'Processing your track...';
      case 'analyzing':
        return 'Analyzing audio characteristics...';
      case 'mixing':
        return 'Mixing vocals with beat...';
      case 'mastering':
        return 'Mastering final track...';
      case 'complete':
        return 'Processing complete!';
      case 'error':
        return 'Processing failed';
      default:
        return 'Processing...';
    }
  };

  return (
    <div className="mt-8">
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-bold mb-4 text-center">
          {getStatusText()}
        </h2>
        
        {error ? (
          <div className="bg-red-900/30 border border-red-500 rounded-lg p-4 text-center">
            <p className="text-red-400">{error}</p>
          </div>
        ) : (
          <>
            <div className="w-full bg-gray-700 rounded-full h-4 mb-4">
              <div 
                className="bg-purple-600 h-4 rounded-full transition-all duration-500" 
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            
            <div className="text-center text-gray-400">
              {currentStatus === 'complete' ? (
                <span className="text-green-400">Your track is ready!</span>
              ) : (
                <span>This may take a few minutes. Please don't close this page.</span>
              )}
            </div>
            
            {/* Processing steps visualization */}
            <div className="mt-8 flex justify-between items-center">
              <div className={`flex flex-col items-center ${
                ['analyzing', 'mixing', 'mastering', 'complete'].includes(currentStatus) 
                  ? 'text-green-400' : 'text-gray-500'
              }`}>
                <div className="w-8 h-8 rounded-full border-2 flex items-center justify-center mb-2">
                  {['analyzing', 'mixing', 'mastering', 'complete'].includes(currentStatus) && (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                  )}
                </div>
                <span className="text-xs">Analysis</span>
              </div>
              
              <div className={`flex-1 h-0.5 ${
                ['mixing', 'mastering', 'complete'].includes(currentStatus) 
                  ? 'bg-green-400' : 'bg-gray-700'
              }`}></div>
              
              <div className={`flex flex-col items-center ${
                ['mixing', 'mastering', 'complete'].includes(currentStatus) 
                  ? 'text-green-400' : 'text-gray-500'
              }`}>
                <div className="w-8 h-8 rounded-full border-2 flex items-center justify-center mb-2">
                  {['mixing', 'mastering', 'complete'].includes(currentStatus) && (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                  )}
                </div>
                <span className="text-xs">Mixing</span>
              </div>
              
              <div className={`flex-1 h-0.5 ${
                ['mastering', 'complete'].includes(currentStatus) 
                  ? 'bg-green-400' : 'bg-gray-700'
              }`}></div>
              
              <div className={`flex flex-col items-center ${
                ['mastering', 'complete'].includes(currentStatus) 
                  ? 'text-green-400' : 'text-gray-500'
              }`}>
                <div className="w-8 h-8 rounded-full border-2 flex items-center justify-center mb-2">
                  {['mastering', 'complete'].includes(currentStatus) && (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                  )}
                </div>
                <span className="text-xs">Mastering</span>
              </div>
              
              <div className={`flex-1 h-0.5 ${
                currentStatus === 'complete' 
                  ? 'bg-green-400' : 'bg-gray-700'
              }`}></div>
              
              <div className={`flex flex-col items-center ${
                currentStatus === 'complete' 
                  ? 'text-green-400' : 'text-gray-500'
              }`}>
                <div className="w-8 h-8 rounded-full border-2 flex items-center justify-center mb-2">
                  {currentStatus === 'complete' && (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                  )}
                </div>
                <span className="text-xs">Complete</span>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default ProcessingStatus;
