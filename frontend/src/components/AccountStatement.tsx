import { useState } from "react";
import { 
  Button, 
  Container, 
  Select, 
  Table, 
  Title, 
  Text, 
  Group, 
  Paper,
  Grid,
  Card,
  Stack
} from "@mantine/core";
import { DatePickerInput } from "@mantine/dates";
import { api } from '../utils/api/axios';
import axios, { AxiosError } from 'axios';
import { Wallet, Droplets, Bolt, Flame } from 'lucide-react';

interface Transaction {
  purchaseDate: string;
  utilityType: string;
  units: number;
  totalAmount: number;
  status: string;
  rechargeToken: string;
}

interface Balances {
  cash_balance: number;
  water_units: number;
  energy_units: number;
  gas_units: number;
}


const AccountStatement = () => {
  const [format, setFormat] = useState<"csv" | "pdf">("csv");
  const [dateRange, setDateRange] = useState<[Date | null, Date | null]>([null, null]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [balances, setBalances] = useState<Balances | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [userProfile, setUserProfile] = useState<{
    username: string;
    firstName:string;
    lastName:string;
    userId: string;
    phoneNumber: string;
    address: string;
  } | null>(null);
  const [generatedAt, setGeneratedAt] = useState<string | null>(null);

  // Get auth token from sessionStorage
  const getAuthHeaders = () => {
    const token = sessionStorage.getItem('token');
    return {
      Authorization: `Bearer ${token}`
    };
  };

  const fetchTransactions = async () => {
    if (!dateRange[0] || !dateRange[1]) {
      setError("Please select a date range");
      return;
    }
  
    try {
      setLoading(true);
      setError(null);
  
      // Fetch transactions
      const response = await api.get("/transactions/account-statement/view", {
        params: {
          start_date: dateRange[0].toISOString().split("T")[0],
          end_date: dateRange[1].toISOString().split("T")[0],
        },
        headers: getAuthHeaders(),
      });
  
      if (response.data.success) {
        setTransactions(response.data.transactions);
        setBalances(response.data.balances);
        setGeneratedAt(new Date().toLocaleString()); // Store generation timestamp
      }
  
      // Fetch user profile
      const profileResponse = await api.get("/dashboard/profile", {
        headers: getAuthHeaders(),
      });
  
      if (profileResponse.data.profile) {
        setUserProfile({
          username: profileResponse.data.profile.email, // Assuming email as username
          firstName:profileResponse.data.profile.firstName,
          lastName:profileResponse.data.profile.lastName,
          userId: profileResponse.data.profile.userId, // Ensure backend provides this
          phoneNumber: profileResponse.data.profile.phoneNumber,
          address: profileResponse.data.profile.address,
        });
      }
    } catch (error) {
      console.error("Error fetching transactions:", error);
      setError("Failed to fetch transactions");
      setTransactions([]);
      setBalances(null);
      setUserProfile(null);
    } finally {
      setLoading(false);
    }
  };
  

  const handleDownload = async () => {
    if (!dateRange[0] || !dateRange[1]) {
      setError("Please select a date range");
      return;
    }

    try {
      setLoading(true);
      
      const response = await api.get("/transactions/account-statement/download", {
        params: {
          format,
          start_date: dateRange[0].toISOString().split("T")[0],
          end_date: dateRange[1].toISOString().split("T")[0],
        },
        responseType: "blob",
        headers: getAuthHeaders()
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `account_statement_${dateRange[0].toISOString().split("T")[0]}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Error downloading statement:", error);
      if (axios.isAxiosError(error)) {
        const axiosError = error as AxiosError<{ message: string }>;
        if (axiosError.response?.status === 401) {
          setError("Session expired. Please log in again.");
          // Optionally redirect to login page
          // window.location.href = '/login';
        } else {
          setError(axiosError.response?.data?.message || "Failed to download statement");
        }
      } else {
        setError("Failed to download statement");
      }
    } finally {
      setLoading(false);
    }
  };


  return (
    <Container size="lg">
      <Title order={2} mb="xl">Account Statement</Title>
      {userProfile && (
        <Paper p="md" withBorder mb="md">
            <Title order={3}>Account Holder Information</Title>
            <Text><strong>Username:</strong> {userProfile.username}</Text>
            <Text><strong>Firstname:</strong> {userProfile.firstName}</Text>
            <Text><strong>Surname:</strong> {userProfile.lastName}</Text>
            <Text><strong>User ID:</strong> {userProfile.userId}</Text>
            <Text><strong>Phone Number:</strong> {userProfile.phoneNumber}</Text>
            <Text><strong>Address:</strong> {userProfile.address}</Text>
            <Text><strong>Generated At:</strong> {generatedAt}</Text>
        </Paper>
        )}

      <Paper p="md" withBorder mb="xl">
        <Group align="flex-end">
          <DatePickerInput
            type="range"
            label="Select Date Range"
            placeholder="Pick dates"
            value={dateRange}
            onChange={setDateRange}
            required
            clearable
            style={{ flex: 1 }}
          />
          <Button 
            onClick={fetchTransactions}
            loading={loading}
            disabled={!dateRange[0] || !dateRange[1]}
          >
            View Statement
          </Button>
        </Group>
      </Paper>

      {error && (
        <Text color="red" mb="md">
          {error}
        </Text>
      )}

      {balances && (
        <Grid mb="xl">
          <Grid.Col span={{ base: 12, md: 6, lg: 3 }}>
            <Card withBorder>
              <Group>
                <Wallet size={24} />
                <Stack gap={0}>
                  <Text size="sm" c="dimmed">Cash Balance</Text>
                  <Text size="lg" fw={500}>${balances.cash_balance.toFixed(2)}</Text>
                </Stack>
              </Group>
            </Card>
          </Grid.Col>
          
          <Grid.Col span={{ base: 12, md: 6, lg: 3 }}>
            <Card withBorder>
              <Group>
                <Droplets size={24} color="blue" />
                <Stack gap={0}>
                  <Text size="sm" c="dimmed">Water Units</Text>
                  <Text size="lg" fw={500}>{balances.water_units.toFixed(2)}</Text>
                </Stack>
              </Group>
            </Card>
          </Grid.Col>

          <Grid.Col span={{ base: 12, md: 6, lg: 3 }}>
            <Card withBorder>
              <Group>
                <Bolt size={24} color="yellow" />
                <Stack gap={0}>
                  <Text size="sm" c="dimmed">Energy Units</Text>
                  <Text size="lg" fw={500}>{balances.energy_units.toFixed(2)}</Text>
                </Stack>
              </Group>
            </Card>
          </Grid.Col>

          <Grid.Col span={{ base: 12, md: 6, lg: 3 }}>
            <Card withBorder>
              <Group>
                <Flame size={24} color="red" />
                <Stack gap={0}>
                  <Text size="sm" c="dimmed">Gas Units</Text>
                  <Text size="lg" fw={500}>{balances.gas_units.toFixed(2)}</Text>
                </Stack>
              </Group>
            </Card>
          </Grid.Col>
        </Grid>
      )}

      {transactions.length > 0 && (
        <Paper p="md" withBorder>
          <Group grow mb="md">
            <Title order={3}>Transaction History</Title>
            <Group justify="flex-end">
              <Select
                label="Download Format"
                value={format}
                onChange={(value) => setFormat(value as "csv" | "pdf")}
                data={[
                  { value: "csv", label: "CSV" },
                  { value: "pdf", label: "PDF" },
                ]}
                style={{ width: 120 }}
              />
              <Button 
                onClick={handleDownload}
                loading={loading}
                variant="light"
              >
                Download
              </Button>
            </Group>
          </Group>

          <Table striped highlightOnHover withTableBorder withColumnBorders>
            <thead>
              <tr>
                <th>Date</th>
                <th>Utility Type</th>
                <th>Units</th>
                <th>Amount</th>
                <th>Status</th>
                <th>Token</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((tx, index) => (
                <tr key={index}>
                  <td>{new Date(tx.purchaseDate).toLocaleString()}</td>
                  <td style={{ textTransform: 'capitalize' }}>{tx.utilityType}</td>
                  <td>{tx.units}</td>
                  <td>${tx.totalAmount.toFixed(2)}</td>
                  <td>{tx.status}</td>
                  <td>{tx.rechargeToken}</td>
                </tr>
              ))}
            </tbody>
          </Table>
        </Paper>
      )}

      {transactions.length === 0 && dateRange[0] && dateRange[1] && !loading && !error && (
        <Paper p="xl" withBorder>
          <Text ta="center" size="lg" c="dimmed">
            No transactions found for the selected date range
          </Text>
        </Paper>
      )}
    </Container>
  );
};

export default AccountStatement;