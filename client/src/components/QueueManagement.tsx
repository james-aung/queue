import React, { useState, useEffect } from 'react';
import { shopkeeperApi } from '../api/shopkeeper';
import type { Queue, QueueEntry } from '../types';
import { 
  PlayIcon, 
  PauseIcon, 
  StopIcon, 
  PhoneIcon,
  CheckIcon,
  XMarkIcon,
  UsersIcon,
  ClockIcon
} from '@heroicons/react/24/outline';

interface QueueManagementProps {
  queue: Queue;
  onQueueUpdate: () => void;
}

export const QueueManagement: React.FC<QueueManagementProps> = ({ 
  queue: initialQueue, 
  onQueueUpdate 
}) => {
  const [queue, setQueue] = useState(initialQueue);
  const [entries, setEntries] = useState<QueueEntry[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setQueue(initialQueue);
    loadEntries();
  }, [initialQueue]);

  const loadEntries = async () => {
    try {
      const entriesData = await shopkeeperApi.getQueueEntries(initialQueue.id);
      setEntries(entriesData);
    } catch (error) {
      console.error('Failed to load entries:', error);
    }
  };

  const handleStatusChange = async (newStatus: 'active' | 'paused' | 'closed') => {
    setLoading(true);
    try {
      const updatedQueue = await shopkeeperApi.updateQueueStatus(queue.id, newStatus);
      setQueue(updatedQueue);
      onQueueUpdate();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to update queue status');
    } finally {
      setLoading(false);
    }
  };

  const handleCallNext = async () => {
    setLoading(true);
    try {
      await shopkeeperApi.callNext(queue.id);
      await loadEntries();
      onQueueUpdate();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to call next customer');
    } finally {
      setLoading(false);
    }
  };

  const handleMarkServed = async (entryId: number) => {
    try {
      await shopkeeperApi.markServed(entryId);
      await loadEntries();
      onQueueUpdate();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to mark as served');
    }
  };

  const handleCancelEntry = async (entryId: number) => {
    if (!window.confirm('Are you sure you want to cancel this entry?')) return;
    
    try {
      await shopkeeperApi.cancelEntry(entryId);
      await loadEntries();
      onQueueUpdate();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to cancel entry');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'paused': return 'bg-yellow-100 text-yellow-800';
      case 'closed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getEntryStatusColor = (status: string) => {
    switch (status) {
      case 'waiting': return 'bg-blue-100 text-blue-800';
      case 'called': return 'bg-yellow-100 text-yellow-800';
      case 'served': return 'bg-green-100 text-green-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const waitingEntries = entries.filter(e => e.status === 'waiting');
  const calledEntries = entries.filter(e => e.status === 'called');

  return (
    <div className="bg-white rounded-lg shadow border border-gray-200">
      <div className="p-6 border-b border-gray-200">
        <div className="flex justify-between items-start">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{queue.business_name}</h3>
            <p className="text-sm text-gray-600">{queue.name}</p>
            {queue.description && (
              <p className="text-sm text-gray-500 mt-1">{queue.description}</p>
            )}
          </div>
          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(queue.status)}`}>
            {queue.status}
          </span>
        </div>

        <div className="flex items-center space-x-6 mt-4 text-sm text-gray-600">
          <div className="flex items-center">
            <UsersIcon className="h-4 w-4 mr-1" />
            {queue.current_size} in queue
          </div>
          <div className="flex items-center">
            <ClockIcon className="h-4 w-4 mr-1" />
            ~{queue.estimated_wait_minutes} min per customer
          </div>
        </div>

        <div className="flex space-x-2 mt-4">
          {queue.status !== 'active' && (
            <button
              onClick={() => handleStatusChange('active')}
              disabled={loading}
              className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 disabled:opacity-50"
            >
              <PlayIcon className="h-4 w-4 mr-1" />
              Activate
            </button>
          )}
          
          {queue.status === 'active' && (
            <button
              onClick={() => handleStatusChange('paused')}
              disabled={loading}
              className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-white bg-yellow-600 hover:bg-yellow-700 disabled:opacity-50"
            >
              <PauseIcon className="h-4 w-4 mr-1" />
              Pause
            </button>
          )}
          
          <button
            onClick={() => handleStatusChange('closed')}
            disabled={loading}
            className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 disabled:opacity-50"
          >
            <StopIcon className="h-4 w-4 mr-1" />
            Close
          </button>

          {waitingEntries.length > 0 && queue.status === 'active' && (
            <button
              onClick={handleCallNext}
              disabled={loading}
              className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
            >
              <PhoneIcon className="h-4 w-4 mr-1" />
              Call Next
            </button>
          )}
        </div>
      </div>

      <div className="p-6">
        {calledEntries.length > 0 && (
          <div className="mb-6">
            <h4 className="text-sm font-medium text-gray-900 mb-3">Currently Called</h4>
            <div className="space-y-2">
              {calledEntries.map((entry) => (
                <div key={entry.id} className="flex items-center justify-between p-3 bg-yellow-50 border border-yellow-200 rounded-md">
                  <div>
                    <span className="font-medium">{entry.customer_name}</span>
                    <span className="text-sm text-gray-600 ml-2">
                      Party of {entry.party_size}
                    </span>
                    <span className={`ml-2 px-2 py-1 text-xs font-medium rounded-full ${getEntryStatusColor(entry.status)}`}>
                      {entry.status}
                    </span>
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleMarkServed(entry.id)}
                      className="inline-flex items-center px-2 py-1 text-xs font-medium rounded text-green-700 bg-green-100 hover:bg-green-200"
                    >
                      <CheckIcon className="h-3 w-3 mr-1" />
                      Served
                    </button>
                    <button
                      onClick={() => handleCancelEntry(entry.id)}
                      className="inline-flex items-center px-2 py-1 text-xs font-medium rounded text-red-700 bg-red-100 hover:bg-red-200"
                    >
                      <XMarkIcon className="h-3 w-3 mr-1" />
                      Cancel
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div>
          <h4 className="text-sm font-medium text-gray-900 mb-3">
            Queue ({waitingEntries.length} waiting)
          </h4>
          {waitingEntries.length === 0 ? (
            <p className="text-sm text-gray-500 text-center py-4">No customers waiting</p>
          ) : (
            <div className="space-y-2">
              {waitingEntries.map((entry) => (
                <div key={entry.id} className="flex items-center justify-between p-3 border border-gray-200 rounded-md">
                  <div>
                    <span className="text-sm font-medium">#{entry.position}</span>
                    <span className="font-medium ml-3">{entry.customer_name}</span>
                    <span className="text-sm text-gray-600 ml-2">
                      Party of {entry.party_size}
                    </span>
                    <span className="text-sm text-gray-500 ml-2">
                      {new Date(entry.joined_at).toLocaleTimeString()}
                    </span>
                  </div>
                  <button
                    onClick={() => handleCancelEntry(entry.id)}
                    className="inline-flex items-center px-2 py-1 text-xs font-medium rounded text-red-700 bg-red-100 hover:bg-red-200"
                  >
                    <XMarkIcon className="h-3 w-3 mr-1" />
                    Remove
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};