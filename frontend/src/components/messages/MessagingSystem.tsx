import { useState, useEffect, useCallback } from 'react';
import { Container, Paper, Tabs, Alert, Loader, Badge } from '@mantine/core';
import { IconInbox, IconSend, IconPencilPlus, IconAlertCircle } from '@tabler/icons-react';
import { notifications } from '@mantine/notifications';
import { messageService } from '../../utils/api/messageService';
import { MessageList } from './MessageList';
import { ComposeForm } from './MessageComposeForm';
import { useAuth } from "../context/useAuthHook";
import { 
  Message, 
  MessageFolder,
  //  MessageStatus
   } from './types';

const MessagingSystem = () => {
  const [activeTab, setActiveTab] = useState<MessageFolder>('inbox');
  const [messages, setMessages] = useState<Message[]>([]);
  const [unreadCounts, setUnreadCounts] = useState({
    inbox: 0,
    outbox: 0,
    sent: 0
  });
  const [contacts, setContacts] = useState<string[]>([]);
  const [recipient, setRecipient] = useState<string>('');
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { user, isLoggedIn } = useAuth();

  const getTotalCount = (folder: MessageFolder): number => {
    return getFilteredMessages(folder).length;
  };
  
  const fetchUnreadCounts = async () => {
    try {
      const counts = await messageService.getMessageCounts();
      setUnreadCounts(counts);
    } catch (err) {
      console.error("Error fetching message counts:", err);
    }
  };
  const updateUnreadCounts = useCallback((allMessages: Message[]) => {
    const counts = {
      inbox: allMessages.filter(msg => 
        msg.recipient === user?.email && 
        msg.status === 'sent' && 
        !msg.isRead
      ).length,
      outbox: allMessages.filter(msg => 
        msg.sender === user?.email && 
        msg.status === 'pending'
      ).length,
      sent: 0 // Usually we don't show badges for sent messages
    };
    setUnreadCounts(counts);
  }, [user?.email]);

  const fetchMessages = useCallback(async () => {
    if (!isLoggedIn || !user?.email) {
      setError("User authentication required. Please log in.");
      return;
    }

    setLoading(true);
    try {
      // Fetch all messages instead of filtering by folder
      const data = await messageService.getMessages('all');
      console.log('Received all messages:', data);
      setMessages(data);
      updateUnreadCounts(data);
      setError(null);
    } catch (err) {
      console.error("Error fetching messages:", err);
      setError("Failed to fetch messages. Please try again later.");
    } finally {
      setLoading(false);
    }
  }, [isLoggedIn, user?.email, updateUnreadCounts]);

  useEffect(() => {
    if (isLoggedIn) {
      fetchMessages();
      fetchUnreadCounts();  // Add this
    }
  }, [isLoggedIn, fetchMessages]);
  const markMessageAsRead = async (messageId: string) => {
    try {
      await messageService.markAsRead(messageId);
      setMessages(prevMessages => 
        prevMessages.map(msg => 
          msg._id === messageId 
            ? { ...msg, isRead: true, read: true } // Update both flags
            : msg
        )
      );
      // Update unread counts after marking as read
      updateUnreadCounts(messages);
    } catch (err) {
      console.error("Error marking message as read:", err);
      notifications.show({
        title: 'Error',
        message: 'Failed to mark message as read',
        color: 'red'
      });
    }
  };

  const getFilteredMessages = (folder: MessageFolder): Message[] => {
    switch (folder) {
      case 'inbox':
        return messages.filter(msg => 
          msg.recipient === user?.email && 
          msg.status === 'sent'
        );
      case 'outbox':
        return messages.filter(msg => 
          msg.sender === user?.email && 
          msg.status === 'pending'
        );
      case 'sent':
        return messages.filter(msg => 
          msg.sender === user?.email && 
          msg.status === 'sent'
        );
      default:
        return [];
    }
  };
  const fetchContacts = useCallback(async () => {
    console.log('Fetching contacts...', { userEmail: user?.email });
    try {
      const users = await messageService.getUsers();
      console.log('Fetched users:', users);
      const filteredContacts = users.filter(email => email !== user?.email);
      console.log('Filtered contacts:', filteredContacts);
      setContacts(filteredContacts);
    } catch (err) {
      console.error("Error fetching contacts:", err);
      notifications.show({
        title: 'Error',
        message: 'Failed to load contacts',
        color: 'red'
      });
    }
  }, [user?.email]);


  useEffect(() => {
    console.log('MessagingSystem mounted/updated', {
      activeTab,
      isLoggedIn,
      userEmail: user?.email,
      messagesCount: messages.length
    });
    fetchMessages();
  }, [fetchMessages, activeTab,isLoggedIn,user?.email,messages.length]);

  useEffect(() => {
    console.log('Contacts effect triggered', {
      isLoggedIn,
      userEmail: user?.email,
      contactsCount: contacts.length
    });
    if (isLoggedIn) {
      fetchContacts();
    }
  }, [fetchContacts, isLoggedIn,contacts.length,user?.email]);

  const handleDeleteMessage = async (messageId: string) => {
    console.log('Attempting to delete message:', messageId);
    try {
      await messageService.deleteMessage(messageId);
      // Immediately remove message from state
      setMessages(prevMessages => {
        const updatedMessages = prevMessages.filter(msg => msg._id !== messageId);
        // Update unread counts with new message list
        updateUnreadCounts(updatedMessages);
        return updatedMessages;
      });
      
      console.log('Message deleted successfully:', messageId);
      notifications.show({
        title: 'Success',
        message: 'Message deleted successfully',
        color: 'green'
      });
    } catch (err) {
      console.error('Delete message error:', err);
      notifications.show({
        title: 'Error',
        message: 'Failed to delete message',
        color: 'red'
      });
    }
  };

  const handleSendMessage = async () => {
    console.log('Attempting to send message:', {
      recipient,
      contentLength: content.length
    });

    if (!recipient || !content.trim()) {
      console.log('Send validation failed:', {
        hasRecipient: !!recipient,
        hasContent: !!content.trim()
      });
      notifications.show({
        title: 'Error',
        message: 'Please fill in all fields',
        color: 'red'
      });
      return;
    }

    try {
      await messageService.sendMessage(recipient, content);
      console.log('Message sent successfully');
      setContent('');
      setRecipient('');
      setActiveTab('outbox');
      await fetchMessages();
      
      notifications.show({
        title: 'Success',
        message: 'Message sent successfully',
        color: 'green'
      });
    } catch (err) {
      console.error('Send message error:', err);
      notifications.show({
        title: 'Error',
        message: 'Failed to send message',
        color: 'red'
      });
    }
  };

  

  if (loading) {
    return (
      <Container size="md" style={{ display: 'flex', justifyContent: 'center', padding: '2rem' }}>
        <Loader size="lg" />
      </Container>
    );
  }

  return (
    <Container size="md">
      <Paper shadow="sm" radius="md" p="md">
        <Tabs value={activeTab} onChange={(value) => setActiveTab(value as MessageFolder)}>
          <Tabs.List grow mb="md">
            <Tabs.Tab 
              value="inbox" 
              leftSection={<IconInbox size={16} />}
              rightSection={
                unreadCounts.inbox > 0 && (
                  <Badge size="sm" variant="filled" color="red">
                    {unreadCounts.inbox}
                  </Badge>
                )
              }
            >
              Inbox
            </Tabs.Tab>
            <Tabs.Tab 
              value="outbox" 
              leftSection={<IconSend size={16} />}
              rightSection={
                unreadCounts.outbox > 0 && (
                  <Badge size="sm" variant="filled" color="yellow">
                    {unreadCounts.outbox}
                  </Badge>
                )
              }
            >
              Outbox
            </Tabs.Tab>
            <Tabs.Tab value="sent" leftSection={<IconSend size={16} />}>
              Sent
            </Tabs.Tab>
            <Tabs.Tab value="compose" leftSection={<IconPencilPlus size={16} />}>
              Compose
            </Tabs.Tab>
          </Tabs.List>

          <Tabs.Panel value="inbox">
            <MessageList
              messages={getFilteredMessages('inbox')}
              currentUser={user?.email || ''}
              onDelete={handleDeleteMessage}
              onRead={markMessageAsRead}
              totalCount={getTotalCount('inbox')}
              folder="inbox"
            />
          </Tabs.Panel>

          <Tabs.Panel value="outbox">
            <MessageList
              messages={getFilteredMessages('outbox')}
              currentUser={user?.email || ''}
              onDelete={handleDeleteMessage}
              totalCount={getTotalCount('outbox')}
              folder="outbox"
            />
          </Tabs.Panel>

          <Tabs.Panel value="sent">
            <MessageList
              messages={getFilteredMessages('sent')}
              currentUser={user?.email || ''}
              onDelete={handleDeleteMessage}
              totalCount={getTotalCount('sent')}
              folder="sent"
            />
          </Tabs.Panel>

          <Tabs.Panel value="compose">
            <ComposeForm
              contacts={contacts}
              recipient={recipient}
              content={content}
              onRecipientChange={setRecipient}
              onContentChange={setContent}
              onSend={handleSendMessage}
              isLoading={loading}
            />
          </Tabs.Panel>
        </Tabs>

        {error && (
          <Alert icon={<IconAlertCircle size={16} />} title="Error" color="red" mt="md">
            {error}
          </Alert>
        )}
      </Paper>
    </Container>
  );
};

export default MessagingSystem;