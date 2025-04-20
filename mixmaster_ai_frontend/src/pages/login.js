import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import axios from 'axios';

const LoginPage = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  // Check if user was redirected after registration
  useEffect(() => {
    if (router.query.registered) {
      setSuccess('Account created successfully! Please log in.');
    }
  }, [router.query]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post('/api/auth/login', {
        email: formData.email,
        password: formData.password
      });
      
      // Store token in localStorage
      localStorage.setItem('token', response.data.access_token);
      
      // Store user data in localStorage
      localStorage.setItem('user', JSON.stringify(response.data.user));
      
      // Redirect to dashboard
      router.push('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-gray-800 text-white flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-purple-400">Log In</h1>
          <p className="text-gray-300 mt-2">Welcome back to MixMaster AI</p>
        </div>
        
        <div className="bg-gray-800 rounded-lg shadow-lg p-8">
          {error && (
            <div className="bg-red-900/50 text-red-200 p-3 rounded mb-6 text-center">
              {error}
            </div>
          )}
          
          {success && (
            <div className="bg-green-900/50 text-green-200 p-3 rounded mb-6 text-center">
              {success}
            </div>
          )}
          
          <form onSubmit={handleSubmit}>
            <div className="mb-6">
              <label htmlFor="email" className="block text-gray-300 mb-2">Email Address</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Enter your email"
              />
            </div>
            
            <div className="mb-6">
              <label htmlFor="password" className="block text-gray-300 mb-2">Password</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Enter your password"
              />
            </div>
            
            <button
              type="submit"
              disabled={loading}
              className={`w-full py-3 rounded-lg font-bold transition-colors ${
                loading 
                  ? 'bg-gray-600 cursor-not-allowed' 
                  : 'bg-purple-600 hover:bg-purple-700 text-white'
              }`}
            >
              {loading ? 'Logging In...' : 'Log In'}
            </button>
          </form>
          
          <div className="mt-6 text-center text-gray-400">
            Don't have an account?{' '}
            <Link href="/register" className="text-purple-400 hover:text-purple-300">
              Create one
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
