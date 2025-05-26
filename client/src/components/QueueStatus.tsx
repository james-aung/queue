import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import type { QueueEntry } from '../types';
import { queuesApi } from '../api/queues';
import { ClockIcon, UserGroupIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { CheckCircleIcon, BellIcon } from '@heroicons/react/24/solid';

export const QueueStatus: React.FC = () => {
  const { entryId } = useParams<{ entryId: string }>();
  const navigate = useNavigate();
  const [entry, setEntry] = useState<QueueEntry | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!entryId) return;

    const fetchEntry = async () => {
      try {
        const data = await queuesApi.getEntry(parseInt(entryId));
        setEntry(data);
      } catch (err) {
        setError('Failed to load queue status');
      } finally {
        setLoading(false);
      }
    };

    fetchEntry();
    // Poll for updates every 30 seconds
    const interval = setInterval(fetchEntry, 30000);
    return () => clearInterval(interval);
  }, [entryId]);

  const handleCancel = async () => {
    if (!entry || window.confirm('Are you sure you want to leave the queue?')) {
      try {
        await queuesApi.cancelEntry(parseInt(entryId!));
        navigate('/');
      } catch (err) {
        alert('Failed to cancel. Please try again.');
      }
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your queue status...</p>
        </div>
      </div>
    );
  }

  if (error || !entry) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600">{error || 'Entry not found'}</p>
          <button
            onClick={() => navigate('/')}
            className="mt-4 text-blue-600 hover:underline"
          >
            Back to queues
          </button>
        </div>
      </div>
    );
  }

  const getStatusIcon = () => {
    switch (entry.status) {
      case 'waiting':
        return <ClockIcon className="h-16 w-16 text-blue-600" />;
      case 'called':
        return <BellIcon className="h-16 w-16 text-green-600 animate-bounce" />;
      case 'served':
        return <CheckCircleIcon className="h-16 w-16 text-green-600" />;
      case 'cancelled':
        return <XMarkIcon className="h-16 w-16 text-gray-400" />;
    }
  };

  const getStatusMessage = () => {
    switch (entry.status) {
      case 'waiting':
        return 'You\'re in the queue!';
      case 'called':
        return 'It\'s your turn!';
      case 'served':
        return 'Thank you for visiting!';
      case 'cancelled':
        return 'You left the queue';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-md mx-auto px-4">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="text-center mb-6">
            {getStatusIcon()}
            <h1 className="text-2xl font-bold mt-4">{getStatusMessage()}</h1>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between py-3 border-b">
              <span className="text-gray-600">Your Name</span>
              <span className="font-medium">{entry.customer_name}</span>
            </div>

            <div className="flex items-center justify-between py-3 border-b">
              <span className="text-gray-600">Party Size</span>
              <span className="font-medium flex items-center">
                <UserGroupIcon className="h-4 w-4 mr-1" />
                {entry.party_size}
              </span>
            </div>

            {entry.status === 'waiting' && (
              <>
                <div className="flex items-center justify-between py-3 border-b">
                  <span className="text-gray-600">Position in Queue</span>
                  <span className="font-medium text-2xl">#{entry.position}</span>
                </div>

                <div className="flex items-center justify-between py-3 border-b">
                  <span className="text-gray-600">Estimated Wait</span>
                  <span className="font-medium flex items-center">
                    <ClockIcon className="h-4 w-4 mr-1" />
                    {entry.estimated_wait_minutes} min
                  </span>
                </div>
              </>
            )}

            {entry.status === 'called' && (
              <div className="bg-green-50 border border-green-200 rounded-md p-4 text-center">
                <p className="text-green-800 font-medium">
                  Please proceed to the counter now!
                </p>
              </div>
            )}
          </div>

          {entry.status === 'waiting' && (
            <button
              onClick={handleCancel}
              className="w-full mt-6 px-4 py-2 border border-red-600 text-red-600 rounded-md hover:bg-red-50"
            >
              Leave Queue
            </button>
          )}

          {(entry.status === 'served' || entry.status === 'cancelled') && (
            <button
              onClick={() => navigate('/')}
              className="w-full mt-6 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Join Another Queue
            </button>
          )}
        </div>

        <p className="text-center text-sm text-gray-500 mt-4">
          Queue ID: {entry.id} • Auto-refreshes every 30 seconds
        </p>
      </div>
    </div>
  );
};