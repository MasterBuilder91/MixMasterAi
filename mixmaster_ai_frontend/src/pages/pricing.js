import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import axios from 'axios';
import { loadStripe } from '@stripe/stripe-js';
import { Elements, CardElement, useStripe, useElements } from '@stripe/react-stripe-js';

// Initialize Stripe with your publishable key
const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY);

const PricingPage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-gray-800 text-white">
      <div className="container mx-auto px-4 py-16">
        <h1 className="text-4xl font-bold text-center mb-4 text-purple-400">
          MixMaster AI Pricing
        </h1>
        <p className="text-xl text-center mb-12 text-gray-300">
          Choose the plan that works best for you
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {/* Free Tier */}
          <div className="bg-gray-800 rounded-lg shadow-lg overflow-hidden">
            <div className="p-6 bg-gray-700">
              <h2 className="text-2xl font-bold text-center text-white">Free</h2>
              <div className="mt-4 text-center">
                <span className="text-4xl font-bold text-white">$0</span>
              </div>
            </div>
            <div className="p-6">
              <ul className="space-y-3">
                <li className="flex items-center">
                  <svg className="h-5 w-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                  <span>1 song free</span>
                </li>
                <li className="flex items-center">
                  <svg className="h-5 w-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                  <span>Basic mixing & mastering</span>
                </li>
                <li className="flex items-center">
                  <svg className="h-5 w-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                  <span>WAV & MP3 export</span>
                </li>
              </ul>
              <div className="mt-6">
                <button className="w-full py-2 px-4 bg-purple-600 hover:bg-purple-700 text-white font-bold rounded-lg transition-colors">
                  Get Started
                </button>
              </div>
            </div>
          </div>
          
          {/* Monthly Subscription */}
          <div className="bg-gray-800 rounded-lg shadow-lg overflow-hidden transform scale-105 border-2 border-purple-500">
            <div className="p-6 bg-purple-700">
              <h2 className="text-2xl font-bold text-center text-white">Monthly</h2>
              <div className="mt-4 text-center">
                <span className="text-4xl font-bold text-white">$40</span>
                <span className="text-white ml-1">/month</span>
              </div>
            </div>
            <div className="p-6">
              <ul className="space-y-3">
                <li className="flex items-center">
                  <svg className="h-5 w-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                  <span>Unlimited songs</span>
                </li>
                <li className="flex items-center">
                  <svg className="h-5 w-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                  <span>Advanced mixing & mastering</span>
                </li>
                <li className="flex items-center">
                  <svg className="h-5 w-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                  <span>Priority processing</span>
                </li>
                <li className="flex items-center">
                  <svg className="h-5 w-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                  <span>All export formats</span>
                </li>
              </ul>
              <div className="mt-6">
                <Elements stripe={stripePromise}>
                  <SubscriptionCheckoutButton plan="monthly" />
                </Elements>
              </div>
            </div>
          </div>
          
          {/* Lifetime Access */}
          <div className="bg-gray-800 rounded-lg shadow-lg overflow-hidden">
            <div className="p-6 bg-gray-700">
              <h2 className="text-2xl font-bold text-center text-white">Lifetime</h2>
              <div className="mt-4 text-center">
                <span className="text-4xl font-bold text-white">$500</span>
                <span className="text-white ml-1">one-time</span>
              </div>
            </div>
            <div className="p-6">
              <ul className="space-y-3">
                <li className="flex items-center">
                  <svg className="h-5 w-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                  <span>Unlimited songs forever</span>
                </li>
                <li className="flex items-center">
                  <svg className="h-5 w-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                  <span>Premium mixing & mastering</span>
                </li>
                <li className="flex items-center">
                  <svg className="h-5 w-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                  <span>Highest priority processing</span>
                </li>
                <li className="flex items-center">
                  <svg className="h-5 w-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                  <span>All future updates included</span>
                </li>
              </ul>
              <div className="mt-6">
                <Elements stripe={stripePromise}>
                  <LifetimeCheckoutButton />
                </Elements>
              </div>
            </div>
          </div>
        </div>
        
        {/* Pay Per Use Option */}
        <div className="mt-16 max-w-3xl mx-auto bg-gray-800 rounded-lg shadow-lg overflow-hidden">
          <div className="p-6 bg-gray-700">
            <h2 className="text-2xl font-bold text-center text-white">Pay Per Use</h2>
            <div className="mt-4 text-center">
              <span className="text-4xl font-bold text-white">$5</span>
              <span className="text-white ml-1">per song</span>
            </div>
          </div>
          <div className="p-6">
            <p className="text-center mb-6">
              Only pay for what you use. Purchase credits and use them whenever you need.
            </p>
            <Elements stripe={stripePromise}>
              <CreditPurchaseForm />
            </Elements>
          </div>
        </div>
      </div>
    </div>
  );
};

const SubscriptionCheckoutButton = ({ plan }) => {
  const stripe = useStripe();
  const elements = useElements();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const router = useRouter();
  
  const handleSubscribe = async () => {
    if (!stripe || !elements) {
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      // Create subscription on the server
      const response = await axios.post('/api/payments/subscription/create', {
        plan: plan
      });
      
      const { clientSecret } = response.data;
      
      // Confirm the subscription with Stripe
      const result = await stripe.confirmCardPayment(clientSecret, {
        payment_method: {
          card: elements.getElement(CardElement),
          billing_details: {
            name: 'User Name', // Should be replaced with actual user name
          },
        }
      });
      
      if (result.error) {
        setError(result.error.message);
      } else {
        // Subscription successful, redirect to dashboard
        router.push('/dashboard');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div>
      <div className="mb-4">
        <CardElement className="p-3 bg-gray-700 rounded-lg" />
      </div>
      {error && (
        <div className="mb-4 text-red-500 text-sm">
          {error}
        </div>
      )}
      <button 
        onClick={handleSubscribe}
        disabled={!stripe || loading}
        className={`w-full py-2 px-4 font-bold rounded-lg transition-colors ${
          loading 
            ? 'bg-gray-600 cursor-not-allowed' 
            : 'bg-purple-600 hover:bg-purple-700 text-white'
        }`}
      >
        {loading ? 'Processing...' : 'Subscribe Now'}
      </button>
    </div>
  );
};

const LifetimeCheckoutButton = () => {
  const stripe = useStripe();
  const elements = useElements();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const router = useRouter();
  
  const handlePurchase = async () => {
    if (!stripe || !elements) {
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      // Create payment intent on the server
      const response = await axios.post('/api/payments/lifetime/purchase');
      
      const { clientSecret } = response.data;
      
      // Confirm the payment with Stripe
      const result = await stripe.confirmCardPayment(clientSecret, {
        payment_method: {
          card: elements.getElement(CardElement),
          billing_details: {
            name: 'User Name', // Should be replaced with actual user name
          },
        }
      });
      
      if (result.error) {
        setError(result.error.message);
      } else {
        // Payment successful, redirect to dashboard
        router.push('/dashboard');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div>
      <div className="mb-4">
        <CardElement className="p-3 bg-gray-700 rounded-lg" />
      </div>
      {error && (
        <div className="mb-4 text-red-500 text-sm">
          {error}
        </div>
      )}
      <button 
        onClick={handlePurchase}
        disabled={!stripe || loading}
        className={`w-full py-2 px-4 font-bold rounded-lg transition-colors ${
          loading 
            ? 'bg-gray-600 cursor-not-allowed' 
            : 'bg-purple-600 hover:bg-purple-700 text-white'
        }`}
      >
        {loading ? 'Processing...' : 'Get Lifetime Access'}
      </button>
    </div>
  );
};

const CreditPurchaseForm = () => {
  const stripe = useStripe();
  const elements = useElements();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [credits, setCredits] = useState(1);
  const router = useRouter();
  
  const handlePurchase = async () => {
    if (!stripe || !elements) {
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      // Create payment intent on the server
      const response = await axios.post('/api/payments/credits/purchase', {
        credits: credits
      });
      
      const { clientSecret } = response.data;
      
      // Confirm the payment with Stripe
      const result = await stripe.confirmCardPayment(clientSecret, {
        payment_method: {
          card: elements.getElement(CardElement),
          billing_details: {
            name: 'User Name', // Should be replaced with actual user name
          },
        }
      });
      
      if (result.error) {
        setError(result.error.message);
      } else {
        // Payment successful, redirect to dashboard
        router.push('/dashboard');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div>
      <div className="mb-4">
        <label className="block text-gray-300 mb-2">
          Number of Credits
        </label>
        <div className="flex items-center">
          <button 
            onClick={() => setCredits(Math.max(1, credits - 1))}
            className="px-3 py-1 bg-gray-700 rounded-l-lg"
          >
            -
          </button>
          <div className="px-4 py-1 bg-gray-700 text-center">
            {credits} ({(credits * 5).toFixed(2)} USD)
          </div>
          <button 
            onClick={() => setCredits(credits + 1)}
            className="px-3 py-1 bg-gray-700 rounded-r-lg"
          >
            +
          </button>
        </div>
      </div>
      
      <div className="mb-4">
        <CardElement className="p-3 bg-gray-700 rounded-lg" />
      </div>
      
      {error && (
        <div className="mb-4 text-red-500 text-sm">
          {error}
        </div>
      )}
      
      <button 
        onClick={handlePurchase}
        disabled={!stripe || loading}
        className={`w-full py-2 px-4 font-bold rounded-lg transition-colors ${
          loading 
            ? 'bg-gray-600 cursor-not-allowed' 
            : 'bg-purple-600 hover:bg-purple-700 text-white'
        }`}
      >
        {loading ? 'Processing...' : `Purchase ${credits} Credit${credits !== 1 ? 's' : ''}`}
      </button>
    </div>
  );
};

export default PricingPage;
