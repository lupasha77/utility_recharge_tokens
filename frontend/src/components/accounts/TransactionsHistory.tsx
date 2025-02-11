import { useState, useCallback, useEffect } from "react";
import {
  Select,
  Button,
  Card,
  Title,
  Group,
  Stack,
  Table,
  Alert,
  Badge,
  ActionIcon,
  Tooltip,
  Text,
  Center,
  Pagination,
  Box
} from "@mantine/core";
import { DatePickerInput } from "@mantine/dates";
import { FileDown, AlertCircle, Copy } from "lucide-react";
import { api } from "../../utils/api/axios";
import { isAxiosError } from "axios";
import { useAuth } from '../../components/context/useAuthHook';

interface Transaction {
  transaction_id: string;
  date: string;
  utility_type: string;
  units: number;
  total_amount: number;
  status: string;
  recharge_token?: string;
}

interface Summary {
  [key: string]: {
    total_units: number;
    total_amount: number;
    count: number;
  };
}

const formatDate = (date: Date | null, endOfDay = false) => {
  if (!date) return "";
  const d = new Date(date);
  if (endOfDay) d.setHours(23, 59, 59, 999);
  return d.toISOString().slice(0, 19).replace('T', ' ');
};

const TransactionsPage = () => {
  const [startDate, setStartDate] = useState<Date | null>(new Date());
  const [endDate, setEndDate] = useState<Date | null>(new Date());
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [downloadFormat, setDownloadFormat] = useState("csv");
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [utilityFilter, setUtilityFilter] = useState<string>("");
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [summary, setSummary] = useState<Summary>({});
  const { isLoggedIn } = useAuth();
  const fetchTransactions = async (page = 1) => {
    if (!validateDates()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await api.get("/transactions/view", {
        params: {
          start_date: formatDate(startDate),
          end_date: formatDate(endDate, true),
          page,
          utility_type: utilityFilter || undefined,
          status: statusFilter || undefined,
        },
      });
      
      setTransactions(response.data.transactions || []);
      setTotalPages(response.data.pagination.total_pages);
      setSummary(response.data.summary || {});
    } catch (err) {
      console.error("API Error:", err);
      setError(isAxiosError(err) ? err.response?.data?.message : "Failed to fetch transactions");
    } finally {
      setLoading(false);
    }
  };

    useEffect(() => {
      if (!isLoggedIn) {
        setError('User authentication required. Please log in.');
      }
    }, [isLoggedIn]);

  const validateDates = useCallback(() => {
    if (!startDate || !endDate) {
      setError("Please select both start and end dates");
      return false;
    }
    return startDate <= endDate;
  }, [startDate, endDate]);

 
  const downloadStatement = async () => {
    if (!startDate || !endDate) return;
    setError(null);
    
    try {
      const response = await api.get("/transactions/tokens/download", {
        params: {
          start_date: formatDate(startDate),
          end_date: formatDate(endDate, true),
          format: downloadFormat
        },
        responseType: "blob"
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      // Set filename based on format
      const fileName = `transactions_${formatDate(startDate).replace(/[: ]/g, '')}_${formatDate(endDate).replace(/[: ]/g, '')}.${downloadFormat}`;
      link.setAttribute('download', fileName);
      
      // Trigger download
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download failed:', error);
      setError(isAxiosError(error) ? 
        error.response?.data?.message || 'Download failed' : 
        'Failed to download statement');
    }
  };

  return (
    <div style={{ maxWidth: "1200px", margin: "0 auto", padding: "1rem" }}>
      <Card shadow="sm" padding="lg" radius="md" withBorder>
        <Title order={2} mb="md">Transactions & Statements</Title>
        <Stack gap="md">
          <Group align="end">
            <DatePickerInput
              label="Start Date"
              value={startDate}
              onChange={setStartDate}
              maxDate={endDate || undefined}
              clearable
            />
            <DatePickerInput
              label="End Date"
              value={endDate}
              onChange={setEndDate}
              minDate={startDate || undefined}
              clearable
            />
            <Select
              label="Utility Type"
              value={utilityFilter}
              onChange={(value) => setUtilityFilter(value || "")}
              data={[
                { value: "", label: "All" },
                { value: "water", label: "Water" },
                { value: "gas", label: "Gas" },
                { value: "energy", label: "Energy" }
              ]}
            />
            <Select
              label="Status"
              value={statusFilter}
              onChange={(value) => setStatusFilter(value||"")}
              data={[
                { value: "", label: "All" },
                { value: "active", label: "Active" },
                { value: "expired", label: "Expired" }
              ]}
            />
            <Button onClick={() => fetchTransactions(1)} loading={loading}>
              View Transactions
            </Button>
          </Group>
          
          {/* Summary Section */}
          {Object.keys(summary).length > 0 && (
            <Box mt="md">
              <Title order={4} mb="sm">Summary</Title>
              <Table>
                <Table.Thead>
                  <Table.Tr>
                    <Table.Th>Utility Type</Table.Th>
                    <Table.Th>Total Units</Table.Th>
                    <Table.Th>Total Amount</Table.Th>
                    <Table.Th>Transaction Count</Table.Th>
                  </Table.Tr>
                </Table.Thead>
                <Table.Tbody>
                  {Object.entries(summary).map(([type, data]) => (
                    <Table.Tr key={type}>
                      <Table.Td><Badge>{type}</Badge></Table.Td>
                      <Table.Td>{data.total_units.toLocaleString()}</Table.Td>
                      <Table.Td>${data.total_amount.toFixed(2)}</Table.Td>
                      <Table.Td>{data.count}</Table.Td>
                    </Table.Tr>
                  ))}
                </Table.Tbody>
              </Table>
            </Box>
          )}
          
          {/* Download Section */}
          <Group align="end">
            <Select
              label="Download Format"
              value={downloadFormat}
              onChange={(value) => setDownloadFormat(value || "csv")}
              data={[
                { value: "csv", label: "CSV" },
                { value: "xlsx", label: "XLSX" },
                { value: "pdf", label: "PDF" },
              ]}
            />
            <Button
              onClick={downloadStatement}
              disabled={loading || transactions.length === 0}
              leftSection={<FileDown size={16} />}
            >
              Download Statement
            </Button>
          </Group>
        </Stack>
        
        {error && (
          <Alert icon={<AlertCircle size={16} />} title="Error" color="red" mt="md">
            {error}
          </Alert>
        )}
      </Card>

      {/* Transactions Table */}
      {transactions.length > 0 && (
        <Card shadow="sm" padding="lg" radius="md" withBorder mt="md">
          <Title order={3} mb="md">Transaction History</Title>
          <Table striped highlightOnHover>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Transaction ID</Table.Th>
                <Table.Th>Date</Table.Th>
                <Table.Th>Utility Type</Table.Th>
                <Table.Th>Units</Table.Th>
                <Table.Th>Amount</Table.Th>
                <Table.Th>Status</Table.Th>
                <Table.Th>Recharge Token</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {transactions.map((transaction) => (
                <Table.Tr key={transaction.transaction_id}>
                  <Table.Td>{transaction.transaction_id}</Table.Td>
                  <Table.Td>{new Date(transaction.date).toLocaleString()}</Table.Td>
                  <Table.Td><Badge variant="light">{transaction.utility_type}</Badge></Table.Td>
                  <Table.Td>{transaction.units.toLocaleString()}</Table.Td>
                  <Table.Td>${(transaction.total_amount || 0).toFixed(2)}</Table.Td>
                  <Table.Td><Badge variant="dot">{transaction.status}</Badge></Table.Td>
                  <Table.Td>
                    {transaction.recharge_token ? (
                      <Group gap="xs">
                        <Badge variant="light">{transaction.recharge_token}</Badge>
                        <Tooltip label="Copy token">
                          <ActionIcon onClick={() => navigator.clipboard.writeText(transaction.recharge_token!)}>
                            <Copy size={16} />
                          </ActionIcon>
                        </Tooltip>
                      </Group>
                    ) : "---"}
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
          
          {totalPages > 1 && (
            <Group justify="center" mt="md">
              <Pagination
                value={currentPage}
                onChange={(page) => {
                  setCurrentPage(page);
                  fetchTransactions(page);
                }}
                total={totalPages}
              />
            </Group>
          )}
        </Card>
      )}
      
      {transactions.length === 0 && !loading && (
        <Center mt="xl">
          <Text>No transactions found for the selected period.</Text>
        </Center>
      )}
    </div>
  );
};

export default TransactionsPage;