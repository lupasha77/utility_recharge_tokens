// Dashboard.tsx
import { Container, SimpleGrid, Title, Button, Stack, Text, Alert, Group, Loader } from '@mantine/core';
import { AlertCircle, History, CreditCard, Wallet, Plus } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { DashboardCard } from '../components/dashboard/DashboardCard';
import UtilityCard from '../components/dashboard/UtilityCard';
import { QuickAction } from '../components/dashboard/QuickAction';
import { useDashboardData } from '../hooks/useDashboardData';
import ErrorBoundary from '../components/errorBoundary/ErrorBoundary';
import { transformUtilityData } from '../utils/TransformUtilityData';
import { UtilityData } from '../utils/type';
import UtilityDashboardComponent from '../components/accounts/UtilityDashboardComponent';

const Dashboard = () => {
  const navigate = useNavigate();
  const { data, loading, error } = useDashboardData();

  if (loading) return <Loader size="lg" />;
  if (error) return <Alert icon={<AlertCircle size={16} />} color="red">{error}</Alert>;
  if (!data) return null;

  const quickActions = [
    { id: 'tokens', icon: <History size={32} />, title: "Tokens Statement", onClick: () => navigate('/dashboard/transactions/tokens') },
    { id: 'payment', icon: <CreditCard size={32} />, title: "Payment Methods", onClick: () => navigate('/dashboard/payment-methods') },
    { id: 'history', icon: <Wallet size={32} />, title: "Payments History", onClick: () => navigate('/dashboard/transactions/wallets') },
  ];

  // Create a Map to store unique utilities
  const uniqueUtilities = new Map(
    data.utilities.map(utility => [utility.utility_type, transformUtilityData(utility)])
  );

  return (
    <Container size="lg" py="lg">
      <Title order={2} mb="xl">Welcome, {data.profile.first_name}!</Title>

      <Group justify="space-between" mb="xl">
        <Title order={3}>Utility Usage</Title>
        <Title order={3}>{new Date().toLocaleString('default', { month: 'long', year: 'numeric' })}</Title>
      </Group>

      <DashboardCard title="Credit Balance" icon={<Wallet size={24} />} className="mb-xl">
        <Stack gap="xs">
          <Group grow>
            <Text size="xl" fw={700}>USD {data.balance.toFixed(2)}</Text>
            <Button 
              leftSection={<Plus size={16} />} 
              variant="light" 
              onClick={() => navigate("/dashboard/deposit-funds")} 
              size="md"
            >
              Add Funds
            </Button>
          </Group>
        </Stack>
      </DashboardCard>

      <SimpleGrid cols={{ base: 1, sm: 2, lg: 3 }} spacing="lg">
        {Array.from(uniqueUtilities.values()).map((utilityData: UtilityData) => (
          <ErrorBoundary key={utilityData.utility_type}>
            <UtilityCard utilityData={utilityData} />
          </ErrorBoundary>
        ))}
      </SimpleGrid>

      <Title order={3} mt="xl" mb="md">Quick Actions</Title>
      <SimpleGrid cols={{ base: 1, sm: 2, lg: 3 }} spacing="lg">
        {quickActions.map(action => (
          <QuickAction 
            key={action.id}
            icon={action.icon} 
            title={action.title} 
            onClick={action.onClick} 
          />
        ))}
      </SimpleGrid>

      <UtilityDashboardComponent balances={[]} monthlyData={[]} />
    </Container>
  );
};

export default Dashboard;