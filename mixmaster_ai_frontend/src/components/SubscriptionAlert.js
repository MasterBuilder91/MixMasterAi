import React from 'react';
import Link from 'next/link';
import { useAuth } from '../context/AuthContext';

const SubscriptionAlert = ({ error, onClose }) => {
  const { user } = useAuth();
  
  if (!error) return null;
  
  let title = 'Subscription Required';
  let message = error.message || 'You need to upgrade your account to continue.';
  let actionText = 'View Plans';
  let actionLink = '/pricing';
  
  // Customize based on error type
  switch (error.type) {
    case 'upgrade':
      title = 'Upgrade Required';
      message = 'You have used your free credit. Please upgrade to continue using MixMaster AI.';
      actionText = 'View Upgrade Options';
      break;
      
    case 'purchase':
      title = 'Credits Required';
      message = 'You have no credits remaining. Please purchase more credits to continue.';
      actionText = 'Purchase Credits';
      break;
      
    case 'subscribe':
      title = 'Subscription Required';
      message = 'You need an active subscription to access this feature.';
      actionText = 'Subscribe Now';
      break;
      
    case 'renew':
      title = 'Subscription Expired';
      message = 'Your subscription has expired. Please renew to continue.';
      actionText = 'Renew Subscription';
      break;
  }
  
  return (
    <div className="bg-red-900/30 border border-red-500 rounded-lg p-4 mb-8">
      <div className="flex justify-between items-start">
        <div>
          <h3 className="text-xl font-bold text-red-400 mb-2">{title}</h3>
          <p className="text-gray-300 mb-4">{message}</p>
          
          <Link 
            href={actionLink}
            className="inline-block px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors"
          >
            {actionText}
          </Link>
        </div>
        
        <button 
          onClick={onClose}
          className="text-gray-400 hover:text-white"
          aria-label="Close"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>
    </div>
  );
};

export default SubscriptionAlert;
