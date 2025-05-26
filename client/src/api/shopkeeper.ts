import apiClient from './client';
import type { Queue, QueueEntry } from '../types';

export interface CreateQueueData {
  name: string;
  business_name: string;
  description?: string;
  address?: string;
  estimated_wait_minutes: number;
}

export interface UpdateQueueData {
  name?: string;
  business_name?: string;
  description?: string;
  address?: string;
  status?: 'active' | 'paused' | 'closed';
  estimated_wait_minutes?: number;
}

export const shopkeeperApi = {
  // Get queues I manage - workaround: get all queues and filter by admin status
  getMyQueues: async (): Promise<Queue[]> => {
    // For now, get all queues - in a real implementation, backend should filter
    const response = await apiClient.get<Queue[]>('/queues/');
    return response.data;
  },

  // Create a new queue
  createQueue: async (data: CreateQueueData): Promise<Queue> => {
    const response = await apiClient.post<Queue>('/queues/', data);
    return response.data;
  },

  // Update a queue
  updateQueue: async (queueId: number, data: UpdateQueueData): Promise<Queue> => {
    const response = await apiClient.patch<Queue>(`/queues/${queueId}`, data);
    return response.data;
  },

  // Delete a queue
  deleteQueue: async (queueId: number): Promise<void> => {
    await apiClient.delete(`/queues/${queueId}`);
  },

  // Get queue entries for management
  getQueueEntries: async (queueId: number): Promise<QueueEntry[]> => {
    const response = await apiClient.get<QueueEntry[]>(`/entries/queue/${queueId}`);
    return response.data;
  },

  // Call next customer - workaround: find first waiting entry and call it
  callNext: async (queueId: number): Promise<QueueEntry | null> => {
    const entries = await apiClient.get<QueueEntry[]>(`/entries/queue/${queueId}`);
    const waitingEntries = entries.data.filter(e => e.status === 'waiting');
    
    if (waitingEntries.length === 0) {
      return null;
    }

    // Call the first waiting entry
    const firstWaiting = waitingEntries.sort((a, b) => a.position - b.position)[0];
    const response = await apiClient.patch<QueueEntry>(`/entries/${firstWaiting.id}/call`);
    return response.data;
  },

  // Mark customer as served
  markServed: async (entryId: number): Promise<QueueEntry> => {
    const response = await apiClient.patch<QueueEntry>(`/entries/${entryId}/serve`);
    return response.data;
  },

  // Cancel/remove entry
  cancelEntry: async (entryId: number): Promise<QueueEntry> => {
    const response = await apiClient.patch<QueueEntry>(`/entries/${entryId}/cancel`);
    return response.data;
  },

  // Update queue status - workaround: use general update endpoint
  updateQueueStatus: async (queueId: number, status: 'active' | 'paused' | 'closed'): Promise<Queue> => {
    const response = await apiClient.patch<Queue>(`/queues/${queueId}`, { status });
    return response.data;
  },
};