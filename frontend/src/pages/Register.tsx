import  { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Paper,
  Title,
  Text,
  TextInput,
  PasswordInput,
  Button,
  Container,
  Stack,
  Alert,
  FileInput,
  Grid
} from '@mantine/core';
import { IconUpload, IconAlertCircle, IconCheck } from '@tabler/icons-react';
import axios from 'axios';

const Register = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
    phoneNumber: '',
    address: '',
  });
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [avatar, setAvatar] = useState<File | null>(null);

  interface FormData {
    firstName: string;
    lastName: string;
    email: string;
    password: string;
    confirmPassword: string;
    phoneNumber: string;
    address: string;
  }


  const handleChange = (name: keyof FormData, value: string) => {
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    setSuccess(false);

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    try {
      const { ...formDataToSend } = formData;

      const response = await axios.post<{ userId: string }>('http://localhost:5000/api/auth/register', formDataToSend);
      if (response.status === 201) {
        setSuccess(true);
        const userId = response.data.userId;

        if (avatar) {
          const avatarFormData = new FormData();
          avatarFormData.append('file', avatar);

          await axios.post(
            `http://localhost:5000/api/files/upload-avatar/${userId}`, 
            avatarFormData,
            { headers: { 'Content-Type': 'multipart/form-data' } }
          );
        }
      }
    } catch   {
      setError('Registration failed. Please try again.');
    }
  };

  return (
    <Container size="sm" py="xl">
      <Paper radius="md" p="xl" withBorder>
        <Stack gap="lg">
          <div>
            <Title order={2} ta="center">Create an Account</Title>
            <Text c="dimmed" size="sm" ta="center" mt="sm">
              Enter your information to register
            </Text>
          </div>

          {error && (
            <Alert icon={<IconAlertCircle size="1rem" />} color="red" variant="filled">
              {error}
            </Alert>
          )}

          {success && (
            <Alert icon={<IconCheck size="1rem" />} color="green" variant="filled">
              Registration successful! Please check your email to verify your account.{' '}
              <Text component="span" c="white" style={{ cursor: 'pointer', textDecoration: 'underline' }}
                onClick={() => navigate('/login')}>
                Log in here
              </Text>
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <Stack gap="md">
              <Grid gutter="md">
                <Grid.Col span={6}>
                  <TextInput
                    required
                    label="First Name"
                    value={formData.firstName}
                    onChange={(event) => handleChange('firstName', event.currentTarget.value)}
                  />
                </Grid.Col>
                <Grid.Col span={6}>
                  <TextInput
                    required
                    label="Last Name"
                    value={formData.lastName}
                    onChange={(event) => handleChange('lastName', event.currentTarget.value)}
                  />
                </Grid.Col>
              </Grid>

              <TextInput
                required
                label="Email"
                type="email"
                value={formData.email}
                onChange={(event) => handleChange('email', event.currentTarget.value)}
              />

              <Grid gutter="md">
                <Grid.Col span={6}>
                  <PasswordInput
                    required
                    label="Password"
                    value={formData.password}
                    onChange={(event) => handleChange('password', event.currentTarget.value)}
                  />
                </Grid.Col>
                <Grid.Col span={6}>
                  <PasswordInput
                    required
                    label="Confirm Password"
                    value={formData.confirmPassword}
                    onChange={(event) => handleChange('confirmPassword', event.currentTarget.value)}
                  />
                </Grid.Col>
              </Grid>

              <TextInput
                required
                label="Phone Number"
                value={formData.phoneNumber}
                onChange={(event) => handleChange('phoneNumber', event.currentTarget.value)}
              />

              <TextInput
                required
                label="Address"
                value={formData.address}
                onChange={(event) => handleChange('address', event.currentTarget.value)}
              />

              <FileInput
                label="Profile Picture"
                placeholder="Choose file"
              leftSection={<IconUpload size="1rem" />}
                accept="image/*"
                value={avatar}
                onChange={setAvatar}
              />

              <Button
                fullWidth
                size="md"
                type="submit"
                mt="md"
              >
                Create Account
              </Button>
            </Stack>
          </form>
        </Stack>
      </Paper>
    </Container>
  );
};

export default Register;