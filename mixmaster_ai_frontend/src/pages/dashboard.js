import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import axios from 'axios';
import Link from 'next/link';

const Dashboard = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [subscription, setSubscription] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const router = useRouter();

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    // Fetch user data
    const fetchUserData = async () => {
      try {
        const response = await axios.get('/api/auth/me', {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        setUser(response.data);

        // If user has a subscription, fetch details
        if (response.data.accountType === 'subscription' && response.data.subscriptionDetails) {
          try {
            const subResponse = await axios.get('/api/payments/subscription/details', {
              headers: {
                Authorization: `Bearer ${token}`
              }
            });
            setSubscription(subResponse.data);
          } catch (err) {
            console.error('Error fetching subscription details:', err);
          }
        }

        // Fetch transaction history
        try {
          const txResponse = await axios.get('/api/payments/transactions', {
            headers: {
              Authorization: `Bearer ${token}`
            }
          });
          setTransactions(txResponse.data);
        } catch (err) {
          console.error('Error fetching transactions:', err);
        }

      } catch (err) {
        setError('Failed to load user data. Please log in again.');
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        setTimeout(() => {
          router.push('/login');
        }, 2000);
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    router.push('/login');
  };

  const handleCancelSubscription = async () => {
    if (!confirm('Are you sure you want to cancel your subscription? You will still have access until the end of your billing period.')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      await axios.post('/api/payments/subscription/cancel', {}, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      // Update subscription status
      if (subscription) {
        setSubscription({
          ...subscription,
          cancelAtPeriodEnd: true
        });
      }
      
      alert('Subscription canceled successfully. You will have access until the end of your current billing period.');
    } catch (err) {
      alert('Failed to cancel subscription. Please try again.');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-gray-900 to-gray-800 text-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500 mx-auto"></div>
          <p className="mt-4 text-xl">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-gray-900 to-gray-800 text-white flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-xl mb-4">{error}</div>
          <Link href="/login" className="text-purple-400 hover:text-purple-300">
            Return to Login
          </Link>
        </div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-gray-800 text-white">
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-purple-400">Dashboard</h1>
          <div className="flex items-center">
            <span className="mr-4">Welcome, {user.name}</span>
            <button 
              onClick={handleLogout}
              className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
            >
              Logout
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Account Status Card */}
          <div className="bg-gray-800 rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-bold mb-4 text-purple-400">Account Status</h2>
            <div className="mb-4">
              <div className="text-gray-400">Account Type</div>
              <div className="text-xl font-semibold">
                {user.accountType === 'free' && 'Free Tier'}
                {user.accountType === 'pay-per-use' && 'Pay Per Use'}
                {user.accountType === 'subscription' && 'Monthly Subscription'}
                {user.accountType === 'lifetime' && 'Lifetime Access'}
              </div>
            </div>
            
            {user.accountType === 'free' && (
              <div className="mb-4">
                <div className="text-gray-400">Free Credits Used</div>
                <div className="text-xl font-semibold">
                  {user.freeCreditsUsed} / 1
                </div>
              </div>
            )}
            
            {user.accountType === 'pay-per-use' && (
              <div className="mb-4">
                <div className="text-gray-400">Available Credits</div>
                <div className="text-xl font-semibold">
                  {user.credits}
                </div>
              </div>
            )}
            
            {user.accountType === 'subscription' && subscription && (
              <div className="mb-4">
                <div className="text-gray-400">Subscription Status</div>
                <div className="text-xl font-semibold">
                  {subscription.status === 'active' ? 'Active' : 'Inactive'}
                  {subscription.cancelAtPeriodEnd && ' (Cancels at period end)'}
                </div>
                <div className="text-gray-400 mt-2">Renewal Date</div>
                <div className="text-lg">
                  {new Date(subscription.currentPeriodEnd).toLocaleDateString()}
                </div>
              </div>
            )}
            
            <div className="mt-6">
              {user.accountType === 'free' && (
                <Link href="/pricing" className="block w-full py-2 text-center bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors">
                  Upgrade Account
                </Link>
              )}
              
              {user.accountType === 'pay-per-use' && (
                <Link href="/pricing" className="block w-full py-2 text-center bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors">
                  Buy More Credits
                </Link>
              )}
              
              {user.accountType === 'subscription' && !subscription?.cancelAtPeriodEnd && (
                <button 
                  onClick={handleCancelSubscription}
                  className="block w-full py-2 text-center bg-red-600 hover:bg-red-700 rounded-lg transition-colors"
                >
                  Cancel Subscription
                </button>
              )}
            </div>
          </div>
          
          {/* Usage Stats Card */}
          <div className="bg-gray-800 rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-bold mb-4 text-purple-400">Usage Statistics</h2>
            <div className="mb-4">
              <div className="text-gray-400">Total Songs Processed</div>
              <div className="text-3xl font-semibold">{user.totalSongsProcessed}</div>
            </div>
            
            <div className="mt-6">
              <Link href="/" className="block w-full py-2 text-center bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors">
                Process New Song
              </Link>
            </div>
          </div>
          
          {/* Quick Actions Card */}
          <div className="bg-gray-800 rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-bold mb-4 text-purple-400">Quick Actions</h2>
            <div className="space-y-3">
              <Link href="/" className="block w-full py-2 text-center bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">
                Upload New Files
              </Link>
              <Link href="/pricing" className="block w-full py-2 text-center bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">
                View Pricing Plans
              </Link>
              {user.accountType !== 'lifetime' && (
                <Link href="/pricing" className="block w-full py-2 text-center bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">
                  Upgrade to Lifetime
                </Link>
              )}
            </div>
          </div>
        </div>
        
        {/* Transaction History */}
        <div className="bg-gray-800 rounded-lg shadow-lg p-6 mb-8">
          <h2 className="text-xl font-bold mb-4 text-purple-400">Transaction History</h2>
          
          {transactions.length === 0 ? (
            <p className="text-gray-400">No transactions yet.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="text-left border-b border-gray-700">
                    <th className="pb-2">Date</th>
                    <th className="pb-2">Type</th>
                    <th className="pb-2">Amount</th>
                    <th className="pb-2">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {transactions.map((tx, index) => (
                    <tr key={index} className="border-b border-gray-700">
                      <td className="py-3">{new Date(tx.timestamp).toLocaleDateString()}</td>
                      <td className="py-3">
                        {tx.type === 'credit_purchase' && 'Credit Purchase'}
                        {tx.type === 'subscription_payment' && 'Subscription Payment'}
                        {tx.type === 'lifetime_purchase' && 'Lifetime Access Purchase'}
                      </td>
                      <td className="py-3">
                        {tx.amount ? `$${(tx.amount / 100).toFixed(2)}` : '-'}
                        {tx.credits ? ` (${tx.credits} credits)` : ''}
                      </td>
                      <td className="py-3">
                        <span className="px-2 py-1 bg-green-900/50 text-green-200 rounded-full text-xs">
                          Completed
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
