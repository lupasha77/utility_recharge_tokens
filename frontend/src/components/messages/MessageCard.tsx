// components/messages/MessageCard.tsx
import { Card, Text, Group, ActionIcon } from '@mantine/core';
import { IconCheck, IconTrash } from '@tabler/icons-react';
import { Message } from './types';

interface MessageCardProps {
  message: Message;
  currentUser: string;
  onDelete: (messageId: string) => void;
}

export const MessageCard = ({ message, currentUser, onDelete }: MessageCardProps) => (
  <Card withBorder shadow="sm" radius="md" mb="md">
    <Group justify="space-between" mb="xs">
      <Text fw={500}>
        {message.sender === currentUser ? `To: ${message.recipient}` : `From: ${message.sender}`}
      </Text>
      <Group gap="xs">
        {message.read && <IconCheck size={16} color="green" />}
        <ActionIcon color="red" onClick={() => onDelete(message._id)}>
          <IconTrash size={16} />
        </ActionIcon>
      </Group>
    </Group>
    <Text>{message.content}</Text>
    <Text size="sm" color="dimmed" mt="sm">
      {new Date(message.timestamp).toLocaleString()}
    </Text>
  </Card>
);
