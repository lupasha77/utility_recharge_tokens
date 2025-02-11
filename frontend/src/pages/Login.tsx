// src/pages/Login.tsx
import React, { useState, useEffect } from 'react';
import { Container, Title, TextInput, PasswordInput, Button, Text, Notification } from '@mantine/core';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../components/context/useAuthHook';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const { login, user } = useAuth();
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    try {
      const success = await login(formData);
      console.log('Login successful:', success);
      if (success) {
        navigate('/dashboard');
      } else {
        setError('Invalid email or password. Please try again.');
      }
    } catch (error) {
      console.error('Login failed:', error);
      setError('Login failed. Please try again.');
      if (error instanceof Error && error.message.includes('storage limitations')) {
        setError('Unable to store login data. Please clear your browser data and try again.');
      }
    }
  };

  useEffect(() => {
    if (user && user.accessToken) {
      // Only push to the login page if the token is not already in sessionStorage
      if (!sessionStorage.getItem('accessToken')) {
        sessionStorage.setItem('accessToken', user.accessToken);
      }
      navigate('/dashboard');
    }
  }, [user, navigate]);

  return (
    <Container size="sm">
      <Title ta="center" mt={50}>Login</Title>
      {error && (
        <Notification color="red" onClose={() => setError(null)}>
          {error}
        </Notification>
      )}
      <form onSubmit={handleSubmit}>
        <TextInput
          label="Email"
          name="email"
          type="email"
          value={formData.email}
          onChange={handleChange}
          required
          mt={20}
        />
        <PasswordInput
          label="Password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          required
          mt={20}
        />
        <Button fullWidth mt={30} type="submit">
          Login
        </Button>
      </form>
      <Text ta="center" mt={20}>
        Don't have an account?{' '}
        <Button variant="link" onClick={() => navigate('/register')}>
          Register here
        </Button>
      </Text>
    </Container>
  );
};

export default Login;
