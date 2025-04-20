import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import FileUpload from '../components/FileUpload';
import ProcessingOptions from '../components/ProcessingOptions';
import ProcessingStatus from '../components/ProcessingStatus';
import AudioPlayer from '../components/AudioPlayer';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { useAuth } from '../context/AuthContext';
import SubscriptionAlert from '../components/SubscriptionAlert';

export default function Home() {
  const { user, loading } = useAuth();
  const [jobId, setJobId] = useState(null);
  const [processingStatus, setProcessingStatus] = useState(null);
  const [resultUrl, setResultUrl] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [subscriptionError, setSubscriptionError] = useState(null);
  const [processingOptions, setProcessingOptions] = useState({
    genre: 'default',
    reverbAmount: 0.3,
    compressionAmount: 0.5,
    outputFormat: 'wav'
  });
  const router = useRouter();

  const handleOptionsChange = (options) => {
    setProcessingOptions(options);
  };

  const handleUploadStart = () => {
    setIsUploading(true);
    setUploadProgress(0);
    setJobId(null);
    setProcessingStatus(null);
    setResultUrl(null);
    setSubscriptionError(null);
  };

  const handleUploadProgress = (progress) => {
    setUploadProgress(progress);
  };

  const handleUploadComplete = (response) => {
    setIsUploading(false);
    setJobId(response.job_id);
    setProcessingStatus('processing');
  };

  const handleUploadError = (error) => {
    setIsUploading(false);
    
    // Check if this is a subscription/credit error
    if (error.response?.status === 402) {
      setSubscriptionError({
        message: error.response.data.detail,
        type: error.response.headers['x-upgrade-required'] ? 'upgrade' :
              error.response.headers['x-purchase-required'] ? 'purchase' :
              error.response.headers['x-subscribe-required'] ? 'subscribe' :
              error.response.headers['x-renew-required'] ? 'renew' : 'general'
      });
    } else {
      // Handle other errors
      alert(`Error: ${error.response?.data?.detail || 'Failed to upload files'}`);
    }
  };

  const handleProcessingComplete = (status, url) => {
    setProcessingStatus(status);
    if (status === 'complete') {
      setResultUrl(url);
    }
  };

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!loading && !user && router.isReady) {
      router.push('/login');
    }
  }, [loading, user, router]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-gray-900 to-gray-800 text-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500 mx-auto"></div>
          <p className="mt-4 text-xl">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return null; // Will redirect in useEffect
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-gray-800 text-white">
      <Head>
        <title>MixMaster AI - Automated Mixing & Mastering</title>
        <meta name="description" content="Upload your vocals and beats for automated mixing and mastering" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <Header />

      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-4xl font-bold text-center mb-8 text-purple-400">
            MixMaster AI
          </h1>
          <p className="text-xl text-center mb-12 text-gray-300">
            Upload your vocals and beat, and get a professionally mixed and mastered track in minutes.
          </p>

          {/* Account Status Banner */}
          <div className="bg-gray-800 rounded-lg p-4 mb-8 flex justify-between items-center">
            <div>
              <span className="text-gray-300">Account Type: </span>
              <span className="font-bold text-purple-400">
                {user.accountType === 'free' && 'Free Tier'}
                {user.accountType === 'pay-per-use' && 'Pay Per Use'}
                {user.accountType === 'subscription' && 'Monthly Subscription'}
                {user.accountType === 'lifetime' && 'Lifetime Access'}
              </span>
              
              {user.accountType === 'free' && (
                <span className="ml-4 text-gray-300">
                  Free Credits: <span className="font-bold">{1 - (user.freeCreditsUsed || 0)} remaining</span>
                </span>
              )}
              
              {user.accountType === 'pay-per-use' && (
                <span className="ml-4 text-gray-300">
                  Credits: <span className="font-bold">{user.credits || 0} remaining</span>
                </span>
              )}
            </div>
            
            <a 
              href="/dashboard" 
              className="text-purple-400 hover:text-purple-300 transition-colors"
            >
              Dashboard
            </a>
          </div>

          {subscriptionError && (
            <SubscriptionAlert 
              error={subscriptionError} 
              onClose={() => setSubscriptionError(null)} 
            />
          )}

          {!jobId && (
            <>
              <ProcessingOptions 
                options={processingOptions} 
                onChange={handleOptionsChange} 
              />
              
              <FileUpload 
                processingOptions={processingOptions}
                onUploadStart={handleUploadStart}
                onUploadProgress={handleUploadProgress}
                onUploadComplete={handleUploadComplete}
                onUploadError={handleUploadError}
                isUploading={isUploading}
                uploadProgress={uploadProgress}
              />
            </>
          )}

          {jobId && (
            <ProcessingStatus 
              jobId={jobId}
              status={processingStatus}
              onProcessingComplete={handleProcessingComplete}
            />
          )}

          {resultUrl && (
            <div className="mt-12">
              <h2 className="text-2xl font-bold mb-4 text-center text-green-400">
                Your Track is Ready!
              </h2>
              <AudioPlayer url={resultUrl} />
            </div>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
}
