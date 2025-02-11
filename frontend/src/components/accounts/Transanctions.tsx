import { useState, useEffect } from "react";
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
} from "@mantine/core";
import { DatePickerInput } from "@mantine/dates";
import { FileDown, AlertCircle, Copy } from "lucide-react";
import { api } from "../../utils/api/axios";
import { isAxiosError } from "axios";

interface Transaction {
  id: string;
  date: string;
  type: string;
  units: number;
  amount: number;
  status: string;
  recharge_token?: string;
}

const TransactionsPage = () => {
  const [startDate, setStartDate] = useState<Date | null>(new Date());
  const [endDate, setEndDate] = useState<Date | null>(new Date());
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [downloadFormat, setDownloadFormat] = useState("csv");

  useEffect(() => {
    console.log("Component Mounted - Default Dates:");
    console.log("Start Date:", startDate);
    console.log("End Date:", endDate);
  }, [endDate, startDate]);

  const formatDate = (date: Date | null) => {
    return date ? date.toISOString().split("T")[0] : "";
  };

  const fetchTransactions = async () => {
    if (!startDate || !endDate) {
      setError("Please select both start and end dates");
      return;
    }

    const formattedStartDate = formatDate(startDate);
    const formattedEndDate = formatDate(endDate);

    console.log("Fetching Transactions...");
    console.log("Start Date Sent:", formattedStartDate);
    console.log("End Date Sent:", formattedEndDate);

    setLoading(true);
    setError(null);

    try {
      const response = await api.get("/transactions/view", {
        params: {
          start_date: formattedStartDate,
          end_date: formattedEndDate,
        },
      });

      console.log("API Response:", response.data);
      setTransactions(response.data.transactions || []);
    } catch (err: unknown) {
      console.error("API Error:", err);
      setError(
        isAxiosError(err) && err.response?.data?.message
          ? err.response.data.message
          : "Failed to fetch transactions"
      );
    } finally {
      setLoading(false);
    }
  };

  const downloadStatement = async () => {
    if (!startDate || !endDate) {
      setError("Please select both start and end dates");
      return;
    }

    const formattedStartDate = formatDate(startDate);
    const formattedEndDate = formatDate(endDate);

    console.log("Downloading Statement...");
    console.log("Start Date Sent:", formattedStartDate);
    console.log("End Date Sent:", formattedEndDate);

    try {
      const response = await api.get("/transactions/download", {
        params: {
          start_date: formattedStartDate,
          end_date: formattedEndDate,
          format: downloadFormat,
        },
        responseType: "blob",
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute(
        "download",
        `statement_${formattedStartDate}_${formattedEndDate}.${downloadFormat}`
      );
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error("Download Error:", err);
      setError("Failed to download statement");
    }
  };

  return (
    <div style={{ maxWidth: "1200px", margin: "0 auto", padding: "1rem" }}>
      <Card shadow="sm" padding="lg" radius="md" withBorder>
        <Title order={2} mb="md">
          Transactions & Statements
        </Title>

        <Stack gap="md">
          <Group align="end">
            <DatePickerInput
              value={startDate}
              onChange={(date) => {
                console.log("Start Date Selected:", date);
                setStartDate(date);
              }}
              style={{ width: "200px" }}
            />
            <DatePickerInput
              value={endDate}
              onChange={(date) => {
                console.log("End Date Selected:", date);
                setEndDate(date);
              }}
              style={{ width: "200px" }}
            />
            <Button onClick={fetchTransactions} loading={loading}>
              View Transactions
            </Button>
          </Group>

          <Group align="end">
            <Select
              label="Download Format"
              value={downloadFormat}
              onChange={(value) => value && setDownloadFormat(value)}
              data={[
                { value: "csv", label: "CSV" },
                { value: "xlsx", label: "Excel" },
              ]}
              style={{ width: "200px" }}
            />
            <Button
              onClick={downloadStatement}
              disabled={loading}
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

      {transactions.length > 0 && (
        <Card shadow="sm" padding="lg" radius="md" withBorder mt="md">
          <Title order={3} mb="md">Transaction History</Title>
          <Table striped highlightOnHover>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Date</Table.Th>
                <Table.Th>Type</Table.Th>
                <Table.Th>Units</Table.Th>
                <Table.Th>Amount</Table.Th>
                <Table.Th>Status</Table.Th>
                <Table.Th>Recharge Token</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {transactions.map((transaction) => (
                <Table.Tr key={transaction.id}>
                  <Table.Td>{new Date(transaction.date).toLocaleDateString()}</Table.Td>
                  <Table.Td>
                    <Badge variant="light">{transaction.type}</Badge>
                  </Table.Td>
                  <Table.Td>{transaction.units.toLocaleString()}</Table.Td>
                  <Table.Td>${transaction.amount.toFixed(2)}</Table.Td>
                  <Table.Td>
                    <Badge variant="dot">{transaction.status}</Badge>
                  </Table.Td>
                  <Table.Td>
                    {transaction.recharge_token && (
                      <Tooltip label="Copy token">
                        <ActionIcon
                          variant="subtle"
                          onClick={() => transaction.recharge_token && navigator.clipboard.writeText(transaction.recharge_token)}
                        >
                          <Copy size={16} />
                        </ActionIcon>
                      </Tooltip>
                    )}
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </Card>
      )}
    </div>
  );
};

export default TransactionsPage;
