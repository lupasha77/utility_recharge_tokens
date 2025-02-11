import { Stack, Select, Textarea, Button } from '@mantine/core';

interface ComposeFormProps {
  contacts: string[];
  recipient: string;
  content: string;
  onRecipientChange: (value: string) => void;
  onContentChange: (value: string) => void;
  onSend: () => void;
  isLoading?: boolean;
}

export const ComposeForm = ({
  contacts,
  recipient,
  content,
  onRecipientChange,
  onContentChange,
  onSend,
  isLoading = false
}: ComposeFormProps) => {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSend();
  };

  return (
    <form onSubmit={handleSubmit}>
      <Stack gap="md">
        <Select
          label="Recipient"
          placeholder="Select recipient"
          data={contacts.map(email => ({ value: email, label: email }))}
          value={recipient}
          onChange={(value) => onRecipientChange(value || '')}
          searchable
          required
          // nothingFound="No matching users"
          error={contacts.length === 0 ? "Loading contacts..." : undefined}
        />
        <Textarea
          label="Message"
          placeholder="Type your message here..."
          value={content}
          onChange={(e) => onContentChange(e.target.value)}
          minRows={3}
          required
        />
        <Button
          type="submit"
          fullWidth
          loading={isLoading}
          disabled={!recipient || !content.trim() || isLoading}
        >
          Send Message
        </Button>
      </Stack>
    </form>
  );
};