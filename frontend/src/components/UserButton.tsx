import React from 'react';
import { Menu, Avatar, Text, UnstyledButton, Group } from '@mantine/core';
import { IconLogout, IconSettings, IconUser } from '@tabler/icons-react';

interface UserButtonProps {
  userName: string;
  email: string;
  avatarUrl: string;
  onLogout: () => void;
}

const UserButton: React.FC<UserButtonProps> = ({ userName, email, avatarUrl, onLogout }) => {
  return (
    <Menu shadow="md" width={200}>
      <Menu.Target>
        <UnstyledButton
          style={{
            display: 'flex',
            alignItems: 'center',
            padding: '8px 12px',
            borderRadius: '8px',
            backgroundColor: '#f1f3f5',
            cursor: 'pointer',
          }}
        >
          <Group gap="sm">
            <Avatar src={avatarUrl} radius="xl" size={40} />
            <div>
              <Text  size="sm">
                {userName}
              </Text>
              <Text size="xs" c="dimmed">
                {email}
              </Text>
            </div>
          </Group>
        </UnstyledButton>
      </Menu.Target>

      <Menu.Dropdown>
        <Menu.Item leftSection={<IconUser size={16} />} onClick={() => console.log('Go to Profile')}>
          Profile
        </Menu.Item>
        <Menu.Item leftSection={<IconSettings size={16} />} onClick={() => console.log('Open Settings')}>
          Settings
        </Menu.Item>
        <Menu.Divider />
        <Menu.Item leftSection={<IconLogout size={16} />} color="red" onClick={onLogout}>
          Logout
        </Menu.Item>
      </Menu.Dropdown>
    </Menu>
  );
};

export default UserButton;
