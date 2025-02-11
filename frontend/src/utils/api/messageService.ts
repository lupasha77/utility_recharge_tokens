// src/utils/api/messageService.ts
 
import { api } from './axios';
import { Message, MessageFolder } from '../../components/messages/types';

export const messageService = {
  getMessages: async (folder: MessageFolder): Promise<Message[]> => {
    try {
      const response = await api.get(`/messages/messages?folder=${folder}`);
      return response.data.map((message: Message) => {
        try {
          let parsedContent;
          try {
            // Parse the JSON string containing decryption status
            parsedContent = JSON.parse(message.content);
            return {
              ...message,
              content: parsedContent.decryptedContent,
              isDecrypted: parsedContent.isDecrypted
            };
          } catch {
            // If content is not JSON, treat as plain text
            return {
              ...message,
              content: message.content,
              isDecrypted: false
            };
          }
        } catch {
          return {
            ...message,
            content: '[Message decryption failed]',
            isDecrypted: false
          };
        }
      });
    } catch (error) {
      console.error('Error fetching messages:', error);
      throw error;
    }
  },

  getMessageCounts: async (): Promise<{ inbox: number; outbox: number; sent: number }> => {
    try {
      const response = await api.get('/messages/messages/counts');
      return response.data;
    } catch (error) {
      console.error('Error fetching message counts:', error);
      throw error;
    }
  },

  replyToMessage: async (messageId: string, content: string): Promise<Message> => {
    try {
      const response = await api.post(`/messages/messages/${messageId}/reply`, { content });
      return response.data;
    } catch (error) {
      console.error('Error sending reply:', error);
      throw error;
    }
  },

  deleteMessage: async (messageId: string): Promise<boolean> => {
    try {
      await api.delete(`/messages/messages/${messageId}`);
      return true;
    } catch (error) {
      console.error('Error deleting message:', error);
      throw error;
    }
  },

  sendMessage: async (recipient: string, content: string): Promise<Message> => {
    try {
      const response = await api.post('/messages/messages', { recipient, content });
      return response.data;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  },

  getUsers: async (): Promise<string[]> => {
    try {
      const response = await api.get('/messages/users');
      return response.data;
    } catch (error) {
      console.error('Error fetching users:', error);
      throw error;
    }
  },
  // Add to messageService
  markAsRead: async (messageId: string): Promise<void> => {
    try {
      await api.patch(`/messages/${messageId}/read`, {}, {
        headers: {
          'Content-Type': 'application/json',
          // Authorization header will be added by the interceptor
        }
      });
    } catch (error) {
      console.error('Error marking message as read:', error);
      throw error;
    }
  },
   
  markAsUnread: async (messageId: string): Promise<void> => {
    try {
      await api.patch(`/messages/${messageId}/unread`, {}, {
        headers: {
          'Content-Type': 'application/json',
          // Authorization header will be added by the interceptor
        }
      });
    } catch (error) {
      console.error('Error marking message as unread:', error);
      throw error;
    }
  }
};