// hooks/useMessages.ts
import { useState } from 'react';
import { Message, MessageFolder } from '../components/messages/types';
import { messageService } from '../utils/api/messageService';
import { notifications } from '@mantine/notifications';

export const useMessages = (currentUser: string) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null); 

  const fetchMessages = async (folder: MessageFolder) => {
    try {
      const data = await messageService.getMessages(folder);
      setMessages(data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch messages');
      console.error('Error fetching messages:', err);
    } finally {
      setLoading(false);
    }
  };

  const deleteMessage = async (messageId: string) => {
    try {
      await messageService.deleteMessage(messageId);
      setMessages(messages.filter(msg => msg._id !== messageId));
      notifications.show({
        title: 'Success',
        message: 'Message deleted successfully',
        color: 'green'
      });
    } catch  {
      notifications.show({
        title: 'Error',
        message: 'Failed to delete message',
        color: 'red'
      });
    }
  };

  const filterMessages = (folder: MessageFolder) => {
    return messages.filter(msg => 
      folder === 'inbox' ? msg.recipient === currentUser : msg.sender === currentUser
    );
  };
 
  return {
    messages,
    loading,
    error,
    fetchMessages,
    deleteMessage,
    filterMessages, 
  };
};