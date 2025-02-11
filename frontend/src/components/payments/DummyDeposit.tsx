import { useState, useEffect } from 'react';
import { Button, TextInput, Container, Title, Alert } from '@mantine/core';
// import { api } from '../../utils/api/axios';
import { useAuth } from '../../components/context/useAuthHook';
import { showNotification } from '@mantine/notifications';
import { Check } from 'lucide-react';

export default function DepositFundsPage() {
  const [amount, setAmount] = useState('');
  const { user, isLoggedIn } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
      if (!isLoggedIn) {
        console.error('User is not authenticated. Redirecting to login.');
        setError('User authentication required. Please log in.');
      }
    }, [isLoggedIn]);
  
  const handleDeposit = async () => {
    setIsProcessing(true);
    try {
      const accessToken = sessionStorage.getItem("accessToken");
      if (!accessToken || !user) {
        setError('Authentication required. Please log in.');
        return;
        }
      const res = await fetch('http://localhost:5000/api/wallet/deposit-funds', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${accessToken}`, },
      body: JSON.stringify({ amount: parseFloat(amount) })
      });
      const data = await res.json();
      alert(data.message);
      // Show success notification
      showNotification({
        title: 'Payment Successful!',
        message: `Token ${data.token} has been sent to ${user.email}`,
        color: 'green',
        icon: <Check />,
        autoClose: 5000,
      });
    } catch (error) {
        setError(error instanceof Error ? error.message : 'Failed to generate token. Please try again.');
      } finally {
        setIsProcessing(false);
      }
};

  return (
    <Container>
      
      
      <Title>Dummy Deposit</Title>
      <TextInput 
        label="Amount" 
        placeholder="Enter amount" 
        value={amount} 
        onChange={(e) => setAmount(e.target.value)} 
      />
      {error && <Alert color="red">{error}</Alert>}
      <Button onClick={handleDeposit} mt="md" loading={isProcessing}>Deposit Funds</Button>
    </Container>
  );
}
