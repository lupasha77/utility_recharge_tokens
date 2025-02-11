import { ReactNode, memo } from 'react';
import { Card, Group, Text } from '@mantine/core';

interface QuickActionProps {
  icon: ReactNode;
  title: string;
  onClick: () => void;
}

export const QuickAction = memo(({ icon, title, onClick }: QuickActionProps) => (
  <Card
    withBorder
    padding="lg"
    radius="md"
    role="button"
    className="cursor-pointer transition-all hover:shadow-lg active:shadow-sm"
    onClick={onClick}
  >
    <Group gap="md">
      {icon}
      <Text size="lg" fw={500}>{title}</Text>
    </Group>
  </Card>
));
