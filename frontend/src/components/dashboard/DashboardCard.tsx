// src/components/dashboard/DashboardCard.tsx
import { ReactNode } from 'react';
import { Card, Text, Group } from '@mantine/core';

interface DashboardCardProps {
  icon: ReactNode;
  title: string;
  children: ReactNode;
  className?: string;
}

export const DashboardCard = ({ icon, title, children, className = '' }: DashboardCardProps) => (
  <Card withBorder shadow="sm" padding="lg" radius="md" className={className}>
    <Group gap="md" mb="xs">
      {icon}
      <Text size="lg" fw={500}>{title}</Text>
    </Group>
    {children}
  </Card>
);