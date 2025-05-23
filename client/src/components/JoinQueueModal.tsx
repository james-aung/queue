import React, { useState } from 'react';
import { Dialog } from '@headlessui/react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import { Queue, QueueEntryCreate } from '../types';

interface JoinQueueModalProps {
  queue: Queue | null;
  isOpen: boolean;
  onClose: () => void;
  onJoin: (data: Omit<QueueEntryCreate, 'queue_id'>) => void;
}

export const JoinQueueModal: React.FC<JoinQueueModalProps> = ({
  queue,
  isOpen,
  onClose,
  onJoin,
}) => {
  const [formData, setFormData] = useState({
    customer_name: '',
    phone_number: '',
    party_size: 1,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onJoin(formData);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'party_size' ? parseInt(value) || 1 : value,
    }));
  };

  if (!queue) return null;

  return (
    <Dialog open={isOpen} onClose={onClose} className="relative z-50">
      <div className="fixed inset-0 bg-black/30" aria-hidden="true" />
      
      <div className="fixed inset-0 flex items-center justify-center p-4">
        <Dialog.Panel className="mx-auto max-w-md w-full rounded-lg bg-white p-6">
          <div className="flex items-center justify-between mb-4">
            <Dialog.Title className="text-lg font-semibold">
              Join Queue at {queue.business_name}
            </Dialog.Title>
            <button
              onClick={onClose}
              className="p-1 rounded-md hover:bg-gray-100"
            >
              <XMarkIcon className="h-5 w-5" />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="customer_name" className="block text-sm font-medium text-gray-700 mb-1">
                Your Name
              </label>
              <input
                type="text"
                id="customer_name"
                name="customer_name"
                value={formData.customer_name}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="John Doe"
              />
            </div>

            <div>
              <label htmlFor="phone_number" className="block text-sm font-medium text-gray-700 mb-1">
                Phone Number
              </label>
              <input
                type="tel"
                id="phone_number"
                name="phone_number"
                value={formData.phone_number}
                onChange={handleChange}
                required
                pattern="^\+?[1-9]\d{9,14}$"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="+1234567890"
              />
              <p className="mt-1 text-xs text-gray-500">
                Include country code (e.g., +1 for US)
              </p>
            </div>

            <div>
              <label htmlFor="party_size" className="block text-sm font-medium text-gray-700 mb-1">
                Party Size
              </label>
              <input
                type="number"
                id="party_size"
                name="party_size"
                value={formData.party_size}
                onChange={handleChange}
                min="1"
                max="20"
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div className="bg-gray-50 rounded-md p-3">
              <p className="text-sm text-gray-600">
                Estimated wait time: <span className="font-medium">{queue.current_size * queue.estimated_wait_minutes} minutes</span>
              </p>
              <p className="text-sm text-gray-600 mt-1">
                You'll be position #{queue.current_size + 1} in the queue
              </p>
            </div>

            <div className="flex gap-3 pt-2">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Join Queue
              </button>
            </div>
          </form>
        </Dialog.Panel>
      </div>
    </Dialog>
  );
};