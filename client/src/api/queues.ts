import apiClient from './client';
import type { Queue, QueueEntry, QueueEntryCreate } from '../types';

export const queuesApi = {
  // List all active queues
  listQueues: async (): Promise<Queue[]> => {
    const response = await apiClient.get<Queue[]>('/queues/');
    return response.data;
  },

  // Get a specific queue
  getQueue: async (queueId: number): Promise<Queue> => {
    const response = await apiClient.get<Queue>(`/queues/${queueId}`);
    return response.data;
  },

  // Join a queue
  joinQueue: async (data: QueueEntryCreate): Promise<QueueEntry> => {
    const response = await apiClient.post<QueueEntry>('/entries/join', data);
    return response.data;
  },

  // Get queue entries
  getQueueEntries: async (queueId: number): Promise<QueueEntry[]> => {
    const response = await apiClient.get<QueueEntry[]>(`/entries/queue/${queueId}`);
    return response.data;
  },

  // Get entry status
  getEntry: async (entryId: number): Promise<QueueEntry> => {
    const response = await apiClient.get<QueueEntry>(`/entries/${entryId}`);
    return response.data;
  },

  // Cancel entry
  cancelEntry: async (entryId: number): Promise<QueueEntry> => {
    const response = await apiClient.patch<QueueEntry>(`/entries/${entryId}/cancel`);
    return response.data;
  },
};