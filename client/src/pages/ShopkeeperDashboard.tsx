import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authApi } from '../api/auth';
import type { User } from '../api/auth';
import { shopkeeperApi } from '../api/shopkeeper';
import type { Queue } from '../types';
import { QueueManagement } from '../components/QueueManagement';
import { CreateQueueModal } from '../components/CreateQueueModal';
import { PlusIcon, ArrowRightOnRectangleIcon } from '@heroicons/react/24/outline';

export const ShopkeeperDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState<User | null>(null);
  const [queues, setQueues] = useState<Queue[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    if (!authApi.isAuthenticated()) {
      navigate('/shopkeeper/login');
      return;
    }

    loadUserData();
  }, [navigate]);

  const loadUserData = async () => {
    try {
      const userData = await authApi.getCurrentUser();
      setUser(userData);
      await loadQueues();
    } catch (error) {
      console.error('Failed to load user data:', error);
      authApi.logout();
      navigate('/shopkeeper/login');
    } finally {
      setLoading(false);
    }
  };

  const loadQueues = async () => {
    try {
      const queuesData = await shopkeeperApi.getMyQueues();
      setQueues(queuesData);
    } catch (error) {
      console.error('Failed to load queues:', error);
    }
  };

  const handleLogout = () => {
    authApi.logout();
    navigate('/shopkeeper/login');
  };

  const handleCreateQueue = async (queueData: any) => {
    try {
      await shopkeeperApi.createQueue(queueData);
      await loadQueues();
      setShowCreateModal(false);
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to create queue');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Shopkeeper Dashboard</h1>
              <p className="text-sm text-gray-600 mt-1">Welcome back, {user?.username}</p>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowCreateModal(true)}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                <PlusIcon className="h-4 w-4 mr-2" />
                New Queue
              </button>
              <button
                onClick={handleLogout}
                className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
              >
                <ArrowRightOnRectangleIcon className="h-4 w-4 mr-2" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {queues.length === 0 ? (
          <div className="text-center py-12">
            <h3 className="mt-2 text-sm font-medium text-gray-900">No queues</h3>
            <p className="mt-1 text-sm text-gray-500">Get started by creating your first queue.</p>
            <div className="mt-6">
              <button
                type="button"
                onClick={() => setShowCreateModal(true)}
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                <PlusIcon className="h-5 w-5 mr-2" aria-hidden="true" />
                New Queue
              </button>
            </div>
          </div>
        ) : (
          <div className="space-y-8">
            {queues.map((queue) => (
              <QueueManagement 
                key={queue.id} 
                queue={queue} 
                onQueueUpdate={loadQueues}
              />
            ))}
          </div>
        )}
      </main>

      <CreateQueueModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onCreateQueue={handleCreateQueue}
      />
    </div>
  );
};