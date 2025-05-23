export interface Queue {
  id: number;
  name: string;
  business_name: string;
  description?: string;
  address?: string;
  status: 'active' | 'paused' | 'closed';
  estimated_wait_minutes: number;
  current_size: number;
  created_at: string;
  updated_at?: string;
}

export interface QueueEntry {
  id: number;
  queue_id: number;
  customer_name: string;
  phone_number: string;
  party_size: number;
  position: number;
  status: 'waiting' | 'called' | 'served' | 'cancelled';
  joined_at: string;
  called_at?: string;
  served_at?: string;
  estimated_wait_minutes: number;
}

export interface QueueEntryCreate {
  queue_id: number;
  customer_name: string;
  phone_number: string;
  party_size: number;
}