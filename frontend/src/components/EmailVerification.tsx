import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Container, Title, Notification, Button, Text } from '@mantine/core';
import axios from 'axios';

const EmailVerification: React.FC = () => {
  const { token } = useParams(); // Get the token from the URL
  const navigate = useNavigate();
  const [message, setMessage] = useState<string>('');
  const [isSuccess, setIsSuccess] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const verifyEmail = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/verify-email/${token}`);
        if (response.data.redirect) {
          setIsSuccess(true);
          setMessage(response.data.message);
          setTimeout(() => {
            navigate(response.data.redirect); // Redirect to the specified route
          }, 3000); // Redirect after 3 seconds
        } else {
          setIsSuccess(false);
          setMessage(response.data.message);
        }
      } catch {
        setIsSuccess(false);
        setMessage('An error occurred while verifying your email. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    verifyEmail();
  }, [token, navigate]);

  return (
    <Container size="sm">
      <Title ta="center" mt={50}>Email Verification</Title>
      {isLoading ? (
        <Text ta="center" mt={20}>Verifying your email...</Text>
      ) : (
        <>
          {isSuccess ? (
            <Notification color="green" onClose={() => setIsSuccess(false)} mt={20}>
              {message}
            </Notification>
          ) : (
            <Notification color="red" onClose={() => setIsSuccess(false)} mt={20}>
              {message}
            </Notification>
          )}
          {!isSuccess && (
            <Button fullWidth mt={20} onClick={() => navigate('/register')}>
              Go to Registration
            </Button>
          )}
        </>
      )}
    </Container>
  );
};

export default EmailVerification;