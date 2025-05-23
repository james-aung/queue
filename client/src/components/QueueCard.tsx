import React from 'react';
import { Queue } from '../types';
import { ClockIcon, MapPinIcon, UsersIcon } from '@heroicons/react/24/outline';

interface QueueCardProps {
  queue: Queue;
  onJoin: (queue: Queue) => void;
}

export const QueueCard: React.FC<QueueCardProps> = ({ queue, onJoin }) => {
  const isAvailable = queue.status === 'active';
  
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{queue.business_name}</h3>
          {queue.description && (
            <p className="text-sm text-gray-600 mt-1">{queue.description}</p>
          )}
        </div>
        <span
          className={`px-2 py-1 text-xs font-medium rounded-full ${
            isAvailable
              ? 'bg-green-100 text-green-800'
              : 'bg-gray-100 text-gray-800'
          }`}
        >
          {queue.status}
        </span>
      </div>

      <div className="space-y-2 mb-4">
        {queue.address && (
          <div className="flex items-center text-sm text-gray-600">
            <MapPinIcon className="h-4 w-4 mr-2" />
            {queue.address}
          </div>
        )}
        <div className="flex items-center text-sm text-gray-600">
          <UsersIcon className="h-4 w-4 mr-2" />
          {queue.current_size} people in queue
        </div>
        <div className="flex items-center text-sm text-gray-600">
          <ClockIcon className="h-4 w-4 mr-2" />
          ~{queue.estimated_wait_minutes * queue.current_size} min wait
        </div>
      </div>

      <button
        onClick={() => onJoin(queue)}
        disabled={!isAvailable}
        className={`w-full py-2 px-4 rounded-md font-medium transition-colors ${
          isAvailable
            ? 'bg-blue-600 text-white hover:bg-blue-700'
            : 'bg-gray-300 text-gray-500 cursor-not-allowed'
        }`}
      >
        {isAvailable ? 'Join Queue' : 'Queue Closed'}
      </button>
    </div>
  );
};