import React, { memo } from 'react';
import { Container, Title, Text, Button, Stack } from '@mantine/core';
import { useNavigate } from 'react-router-dom';

const Home: React.FC = memo(() => {
  const navigate = useNavigate();
  
  const handleRegister = React.useCallback(() => {
    navigate('/register');
  }, [navigate]);
  
  const handleLogin = React.useCallback(() => {
    navigate('/login');
  }, [navigate]);

  return (
    <Container size="xs" py="xl">
      <Stack align="stretch" gap="md">
        <Title order={1} ta="center">Welcome to Token Meter Recharge</Title>
        <Text ta="center" c="dimmed">
          Manage your water and energy meters with ease. Register or log in to get started.
        </Text>
        <Button
          fullWidth
          onClick={handleRegister}
          color="blue"
        >
          Register
        </Button>
        <Button
          fullWidth
          variant="outline"
          onClick={handleLogin}
          color="blue"
        >
          Login
        </Button>
      </Stack>
    </Container>
  );
});

export default Home;