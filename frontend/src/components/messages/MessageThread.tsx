// MessageThread.tsx
import { Paper, Stack, Text, Button, Textarea, Group } from '@mantine/core';
import { useState } from 'react';
import { Message } from './types';
import { messageService } from '../../utils/api/messageService';

interface MessageThreadProps {
  message: Message;
  currentUser: string;
  onReply: () => void;
}

export const MessageThread = ({ message, currentUser, onReply }: MessageThreadProps) => {
  const [replyContent, setReplyContent] = useState('');
  const [isReplying, setIsReplying] = useState(false);

  const handleSendReply = async () => {
    try {
      await messageService.replyToMessage(message._id, replyContent);
      setReplyContent('');
      setIsReplying(false);
      onReply();
    } catch (error) {
      console.error('Error sending reply:', error);
    }
  };

  const renderMessageContent = (content: string) => {
    try {
      // Attempt to parse the content as it might be encrypted
      const parsedContent = JSON.parse(content);
      return parsedContent.decryptedContent || content;
    } catch {
      // If parsing fails, return the original content
      return content;
    }
  };

  return (
    <Stack gap="md">
      {/* Original message */}
      <Paper shadow="xs" p="md">
        <Group justify='space-between' mb="xs">
          <Text>
            {message.sender === currentUser ? `To: ${message.recipient}` : `From: ${message.sender}`}
          </Text>
          <Text size="sm" color="dimmed">
            {new Date(message.timestamp).toLocaleString()}
          </Text>
        </Group>
        <Text>{renderMessageContent(message.content)}</Text>
      </Paper>

      {/* Replies */}
      {message.replies?.map((reply) => (
        <Paper key={reply._id} shadow="xs" p="md" ml={32}>
          <Group justify='space-between' mb="xs">
            <Text>
              {reply.sender === currentUser ? `To: ${reply.recipient}` : `From: ${reply.sender}`}
            </Text>
            <Text size="sm" color="dimmed">
              {new Date(reply.timestamp).toLocaleString()}
            </Text>
          </Group>
          <Text>{renderMessageContent(reply.content)}</Text>
        </Paper>
      ))}

      {/* Reply form */}
      {isReplying ? (
        <Paper shadow="xs" p="md">
          <Textarea
            value={replyContent}
            onChange={(e) => setReplyContent(e.currentTarget.value)}
            minRows={3}
            mb="sm"
          />
          <Group justify='flex-end'>
            <Button variant="outline" onClick={() => setIsReplying(false)}>
              Cancel
            </Button>
            <Button onClick={handleSendReply} disabled={!replyContent.trim()}>
              Send Reply
            </Button>
          </Group>
        </Paper>
      ) : (
        <Button variant="light" onClick={() => setIsReplying(true)}>
          Reply
        </Button>
      )}
    </Stack>
  );
};