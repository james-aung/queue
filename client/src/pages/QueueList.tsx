import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import type { Queue, QueueEntryCreate } from '../types';
import { queuesApi } from '../api/queues';
import { QueueCard } from '../components/QueueCard';
import { JoinQueueModal } from '../components/JoinQueueModal';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';

export const QueueList: React.FC = () => {
  const navigate = useNavigate();
  const [queues, setQueues] = useState<Queue[]>([]);
  const [filteredQueues, setFilteredQueues] = useState<Queue[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedQueue, setSelectedQueue] = useState<Queue | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    fetchQueues();
  }, []);

  useEffect(() => {
    const filtered = queues.filter(queue =>
      queue.business_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      queue.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      queue.address?.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredQueues(filtered);
  }, [queues, searchTerm]);

  const fetchQueues = async () => {
    try {
      const data = await queuesApi.listQueues();
      setQueues(data);
      setFilteredQueues(data);
    } catch (error) {
      console.error('Failed to fetch queues:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleJoinQueue = (queue: Queue) => {
    setSelectedQueue(queue);
    setIsModalOpen(true);
  };

  const handleSubmitJoin = async (data: Omit<QueueEntryCreate, 'queue_id'>) => {
    if (!selectedQueue) return;

    try {
      const entry = await queuesApi.joinQueue({
        ...data,
        queue_id: selectedQueue.id,
      });
      
      // Navigate to status page
      navigate(`/status/${entry.id}`);
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to join queue. Please try again.');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-2xl font-bold text-gray-900">Virtual Queue</h1>
          <p className="text-sm text-gray-600 mt-1">Join a queue and get notified when it's your turn</p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Bar */}
        <div className="mb-6">
          <div className="relative max-w-md">
            <input
              type="text"
              placeholder="Search queues..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <MagnifyingGlassIcon className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
          </div>
        </div>

        {/* Queue Grid */}
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading queues...</p>
          </div>
        ) : filteredQueues.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-600">
              {searchTerm ? 'No queues found matching your search.' : 'No active queues available.'}
            </p>
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {filteredQueues.map((queue) => (
              <QueueCard
                key={queue.id}
                queue={queue}
                onJoin={handleJoinQueue}
              />
            ))}
          </div>
        )}
      </main>

      {/* Join Queue Modal */}
      <JoinQueueModal
        queue={selectedQueue}
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setSelectedQueue(null);
        }}
        onJoin={handleSubmitJoin}
      />
    </div>
  );
};