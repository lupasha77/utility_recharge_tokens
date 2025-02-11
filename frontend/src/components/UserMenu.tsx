import React, { useState } from 'react';
import { Avatar, Menu, Group, Text, UnstyledButton, rem, ActionIcon } from '@mantine/core';
import { IconChevronDown, IconLogout, IconUser, IconDroplet, IconBolt, IconCoin, IconFileText, IconShoppingCart } from '@tabler/icons-react';

const UserMenu: React.FC = () => {
    const [userMenuOpened, setUserMenuOpened] = useState(false);

    // Mock user data
    const user = {
        name: 'John Doe',
        email: 'john.doe@example.com',
        avatar: 'https://i.pravatar.cc/150?img=1', // Replace with your avatar URL
        waterBalance: 120, // Mock water balance
        energyBalance: 50, // Mock energy balance
        cashBalance: 1000, // Mock cash balance
    };

    return (
        <Menu
            width={260}
            position="bottom-end"
            transitionProps={{ transition: 'pop-top-right' }}
            onClose={() => setUserMenuOpened(false)}
            onOpen={() => setUserMenuOpened(true)}
            withinPortal
        >
            <Menu.Target>
                <UnstyledButton>
                    <Group spacing={7}>
                        <Avatar src={user.avatar} alt={user.name} radius="xl" size={40} />
                        <Text weight={500} size="sm" sx={{ lineHeight: 1 }} mr={3}>
                            {user.name}
                        </Text>
                        <IconChevronDown size={rem(12)} stroke={1.5} />
                    </Group>
                </UnstyledButton>
            </Menu.Target>

            <Menu.Dropdown>
                {/* User Profile Section */}
                <Menu.Label>Profile</Menu.Label>
                <Menu.Item icon={<IconUser size={14} />}>View Profile</Menu.Item>

                {/* Balances Section */}
                <Menu.Label>Balances</Menu.Label>
                <Menu.Item icon={<IconDroplet size={14} />}>
                    Water Balance: {user.waterBalance} units
                </Menu.Item>
                <Menu.Item icon={<IconBolt size={14} />}>
                    Energy Balance: {user.energyBalance} units
                </Menu.Item>
                <Menu.Item icon={<IconCoin size={14} />}>
                    Cash Balance: ${user.cashBalance}
                </Menu.Item>

                {/* Statements Section */}
                <Menu.Label>Statements</Menu.Label>
                <Menu.Item icon={<IconFileText size={14} />}>Water Usage Statement</Menu.Item>
                <Menu.Item icon={<IconFileText size={14} />}>Energy Usage Statement</Menu.Item>

                {/* Purchase Tokens Section */}
                <Menu.Label>Purchase Tokens</Menu.Label>
                <Menu.Item icon={<IconShoppingCart size={14} />}>Purchase Water Token</Menu.Item>
                <Menu.Item icon={<IconShoppingCart size={14} />}>Purchase Energy Token</Menu.Item>

                {/* Logout Section */}
                <Menu.Divider />
                <Menu.Label>Account</Menu.Label>
                <Menu.Item color="red" icon={<IconLogout size={14} />}>Logout</Menu.Item>
            </Menu.Dropdown>
        </Menu>
    );
};

export default UserMenu;