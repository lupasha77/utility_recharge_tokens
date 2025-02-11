// src/components/messages/types.ts
export interface Message {
  _id: string;
  sender: string;
  recipient: string;
  content: string;
  timestamp: string;
  delivery_timestamp?: string;
  read: boolean;
  isRead:boolean;
  replies?: Message[];
  parent_id?: string;
  status: 'pending' | 'sent' | 'failed';
}

export type MessageFolder = 'inbox' | 'outbox' | 'sent'|'all';
 

// Add a type for the message status
export  type MessageStatus = 'read' | 'unread' | 'sent' | 'pending';