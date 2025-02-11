// MessageList.tsx
import { ActionIcon, Checkbox, Group, Paper, Stack, Text, Badge } from '@mantine/core';
import { IconTrash } from '@tabler/icons-react';
import { ReplyIcon } from 'lucide-react';
import { Message } from './types';
import { MessageThread } from './MessageThread';
import { useState } from 'react';

interface MessageListProps {
  messages: Message[];
  currentUser: string;
  onDelete: (id: string) => void;
  onRead?: (id: string) => void;
  totalCount: number;
  folder: 'inbox' | 'outbox' | 'sent';
}

export const MessageList = ({ 
  messages, 
  currentUser, 
  onDelete, 
  onRead,
  totalCount,
  folder 
}: MessageListProps) => {
  const [selectedMessages, setSelectedMessages] = useState<string[]>([]);
  const [expandedMessage, setExpandedMessage] = useState<string | null>(null);

  const handleSelect = (messageId: string) => {
    setSelectedMessages(prev => 
      prev.includes(messageId) 
        ? prev.filter(id => id !== messageId)
        : [...prev, messageId]
    );
  };

  const handleMessageClick = async (message: Message) => {
    // Check both isRead and read properties
    if ((!message.isRead || !message.read) && onRead) {
      await onRead(message._id);
    }
    setExpandedMessage(expandedMessage === message._id ? null : message._id);
  };

  const getFolderTitle = () => {
    const title = folder.charAt(0).toUpperCase() + folder.slice(1);
    return `${title} (${totalCount})`;
  };

  return (
    <Stack gap="md">
      <Group justify="space-between" mb="md">
        <Text size="lg" fw={500}>{getFolderTitle()}</Text>
        {selectedMessages.length > 0 && (
          <ActionIcon 
            color="red" 
            onClick={() => selectedMessages.forEach(id => onDelete(id))}
          >
            <IconTrash size={20} />
          </ActionIcon>
        )}
      </Group>

      {messages.length === 0 ? (
        <Text c="dimmed" ta="center">No messages</Text>
      ) : (
        messages.map((message) => (
          <Stack key={message._id} gap="xs">
            <Paper
            shadow="xs"
            p="md"
            style={{
              cursor: 'pointer',
              backgroundColor: (!message.isRead && !message.read) ? '#f8f9fa' : 'white'
            }}
          >
              <Group gap="xs" mb="xs">
                <Checkbox
                  checked={selectedMessages.includes(message._id)}
                  onChange={(e) => {
                    e.stopPropagation();
                    handleSelect(message._id);
                  }}
                />
                <Group style={{ flex: 1 }} justify="space-between">
                   <Group gap="md">
                    <Text fw={(!message.isRead && !message.read) ? 'bold' : 'normal'}>
                      {message.sender === currentUser ? `To: ${message.recipient}` : `From: ${message.sender}`}
                    </Text>
                  {(!message.isRead && !message.read) && <Badge color="blue">New</Badge>}
                </Group>
                  <Group gap="xs">
                    <Text size="sm" color="dimmed">
                      {new Date(message.timestamp).toLocaleString()}
                    </Text>
                    <ActionIcon
                      variant="subtle"
                      onClick={(e) => {
                        e.stopPropagation();
                        setExpandedMessage(message._id);
                      }}
                    >
                      <ReplyIcon size={16} />
                    </ActionIcon>
                    <ActionIcon
                      color="red"
                      onClick={(e) => {
                        e.stopPropagation();
                        onDelete(message._id);
                      }}
                    >
                      <IconTrash size={16} />
                    </ActionIcon>
                  </Group>
                </Group>
              </Group>
              <Text onClick={() => handleMessageClick(message)}>
                {message.content}
              </Text>
            </Paper>
            
            {expandedMessage === message._id && (
              <MessageThread 
                message={message}
                currentUser={currentUser}
                onReply={() => setExpandedMessage(null)}
              />
            )}
          </Stack>
        ))
      )}
    </Stack>
  );
};