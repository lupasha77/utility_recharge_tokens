// src/components/accounts/AccountStatement.tsx
import { useEffect, useState } from 'react';
import UtilityDashboard from './UtilityDashboardComponent';
import {
  Button,
  Card,
  Title,
  Stack,
  Table,
  Alert,
  Badge,
  Select,
  Text,
  Group,
} from '@mantine/core';
import { DatePickerInput } from '@mantine/dates';
import { FileDown, AlertCircle } from 'lucide-react';
import { api } from '../../utils/api/axios';
import { isAxiosError } from 'axios';
import { useAuth } from '../../components/context/useAuthHook';

const AccountStatementPage = () => {
  const { isLoggedIn } = useAuth();
  const [dateRange, setDateRange] = useState<[Date | null, Date | null]>([null, null]);
  const [downloadFormat, setDownloadFormat] = useState("csv");
  
  interface Transaction {
    id: string;
    date: string;
    type: 'water' | 'energy' | 'gas';
    units: number;
    amount: number;
    status: string;
  }

  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [totalSpent, setTotalSpent] = useState(0);
  const [noTransactions, setNoTransactions] = useState(false);
  
  useEffect(() => {
    if (!isLoggedIn) {
      setError('User authentication required. Please log in.');
    }
  }, [isLoggedIn]);

  const handleFetchStatement = async () => {
    if (!dateRange[0] || !dateRange[1]) {
      setError('Please select both start and end dates.');
      return;
    }

    setLoading(true);
    setError(null);
    setNoTransactions(false);

    try {
      const response = await api.get('/transactions/account-statement/view', {
        params: {
          start_date: dateRange[0]?.toISOString() || '',
          end_date: dateRange[1]?.toISOString() || '',
        },
      });

      if (response.data.transactions.length === 0) {
        setNoTransactions(true);
        setTransactions([]);
        setTotalSpent(0);
      } else {
        setTransactions(response.data.transactions);
        setTotalSpent(response.data.summary.total_spent);
      }
    } catch (err: unknown) {
      console.error('API Error:', err);
      setError(isAxiosError(err) ? err.response?.data?.message : 'Failed to fetch account statement');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadStatement = async () => {
    if (!dateRange[0] || !dateRange[1]) {
      setError('Please select both start and end dates.');
      return;
    }
    
    try {
      const response = await api.get('/transactions/account-statement/download', {
        params: {
          start_date: dateRange[0]?.toISOString(),
          end_date: dateRange[1]?.toISOString(),
          format: downloadFormat,
        },
        responseType: 'blob',
      });

      const blob = new Blob([response.data], { 
        type: downloadFormat === 'pdf' ? 'application/pdf' : 'text/csv' 
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `account_statement_${dateRange[0]?.toISOString().slice(0, 10)}_${dateRange[1]?.toISOString().slice(0, 10)}.${downloadFormat}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Download Error:', err);
      setError('Failed to download statement');
    }
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '1rem' }}>
      <Card shadow="sm" padding="lg" radius="md" withBorder>
        <Title order={2} mb="md">Account Statement</Title>
        <Stack gap="md">
          <DatePickerInput
            type="range"
            label="Pick dates range"
            value={dateRange}
            onChange={setDateRange}
            style={{ width: '300px' }}
          />
          <Button onClick={handleFetchStatement} loading={loading}>
            View Statement
          </Button>

          {error && (
            <Alert icon={<AlertCircle size={16} />} title="Error" color="red" mt="md">
              {error}
            </Alert>
          )}
        </Stack>

        {noTransactions ? (
          <Alert title="No Transactions" color="blue" mt="md">
            No transactions were recorded during the selected period.
          </Alert>
        ) : transactions.length > 0 && (
          <Group>
            <UtilityDashboard transactions={transactions} />
            <Card shadow="sm" padding="lg" radius="md" withBorder mt="md">
              <Title order={3} mb="md">Transaction History</Title>
              <Table striped highlightOnHover>
                <Table.Thead>
                  <Table.Tr>
                    <Table.Th>Date</Table.Th>
                    <Table.Th>Utility Type</Table.Th>
                    <Table.Th>Units</Table.Th>
                    <Table.Th>Amount</Table.Th>
                    <Table.Th>Status</Table.Th>
                  </Table.Tr>
                </Table.Thead>
                <Table.Tbody>
                  {transactions.map(({ id, date, type, units, amount, status }) => (
                    <Table.Tr key={id}>
                      <Table.Td>{new Date(date).toLocaleString()}</Table.Td>
                      <Table.Td><Badge variant="light">{type}</Badge></Table.Td>
                      <Table.Td>{units.toLocaleString()}</Table.Td>
                      <Table.Td>${amount.toFixed(2)}</Table.Td>
                      <Table.Td><Badge variant="dot">{status}</Badge></Table.Td>
                    </Table.Tr>
                  ))}
                </Table.Tbody>
              </Table>
            </Card>
            <Stack gap="md" mt="md">
              <Select
                label="Download Format"
                value={downloadFormat}
                onChange={(value) => setDownloadFormat(value || "csv")}
                data={[
                  { value: "csv", label: "CSV" },
                  { value: "pdf", label: "PDF" },
                ]}
              />
              <Button 
                onClick={handleDownloadStatement}
                disabled={loading || transactions.length === 0} 
                leftSection={<FileDown size={16}/>}
              >
                Download Statement
              </Button>
              <Text size="lg" >
                Total Spent: ${totalSpent.toFixed(2)}
              </Text>
            </Stack>
          </Group>
        )}
      </Card>
    </div>
  );
};

export default AccountStatementPage;