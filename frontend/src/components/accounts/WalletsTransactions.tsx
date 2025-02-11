import  { useState, useEffect, useCallback } from "react";
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
  Grid,
  Pagination,
} from "@mantine/core";
import { DatePickerInput } from "@mantine/dates";
import { FileDown, AlertCircle, Copy, ArrowUp, ArrowDown } from "lucide-react";
import { api } from "../../utils/api/axios";
import { isAxiosError } from "axios";
import { useAuth } from "../context/useAuthHook";
import { Droplet, Zap, Flame, Wallet } from "lucide-react";
import { PieChart, Pie, Cell } from "recharts";

interface Transaction {
  id: string;
  date: string;
  type: string;
  units: number;
  amount: number;
  status: string;
  recharge_token: string;
  utility_type: string;
  initial_balance: number | null;
  final_balance: number | null;
  transaction_type: string;
  payment_method: string;
}

interface UtilityMetrics {
  total_purchased: number;
  total_used: number;
  remaining_units: number;
}

interface FinancialMetrics {
  total_deposits: number;
  total_direct_purchases: number;
  wallet_balance: number;
}

interface SummaryMetrics {
  water: UtilityMetrics;
  energy: UtilityMetrics;
  gas: UtilityMetrics;
  financial: FinancialMetrics;
}

interface SummaryCardProps {
  title: string;
  data: UtilityMetrics | FinancialMetrics;
  type: "water" | "energy" | "gas" | "financial";
  units: { [key: string]: string };
}

const ITEMS_PER_PAGE_OPTIONS = [10, 20, 50, 0];

const formatDate = (date: Date | null, endOfDay = false) => {
  if (!date) return "";
  const d = new Date(date);
  if (endOfDay) d.setHours(23, 59, 59, 999);
  return d.toISOString().slice(0, 19).replace("T", " ");
};

const SummaryCard = ({ title, data, type, units }: SummaryCardProps) => {
  const cardStyles = {
    water: {
      icon: Droplet,
      color: "bg-blue-50",
      chartColors: ["#ff1a1a", "#009900"],
    },
    energy: {
      icon: Zap,
      color: "bg-yellow-50",
      chartColors: ["#ff1a1a", "#009900"],
    },
    gas: {
      icon: Flame,
      color: "bg-red-50",
      chartColors: ["#ff1a1a", "#009900"],
    },
    financial: {
      icon: Wallet,
      color: "bg-green-50",
      chartColors: ["#3366ff", "#00e600"],
    },
  };

  const IconComponent = cardStyles[type].icon;

  const formatValue = (key: string, value: number) => {
    const isMonetary =
      key.includes("deposits") || key.includes("purchases");

    if (isMonetary) {
      return `${Number(value).toFixed(2)}`;
    }

    return `${Number(value).toLocaleString()} `; //${units[type]}
  };

  const getChartData = () => {
    if ("total_purchased" in data) {
      return [
        { name: "Used", value: data.total_used },
        { name: "Available", value: data.remaining_units },
      ];
    }
    return [
      { name: "Deposits", value: data.total_deposits },
      { name: "Purchases", value: data.total_direct_purchases },
    ];
  };

  const chartData = getChartData();

  return (
    <Card
      shadow="sm"
      p="lg"
      radius="md"
      withBorder
      className={`h-full ${cardStyles[type].color}`}
    >
      <Group justify="space-between" mb="md">
        <Group gap="xs">
          <IconComponent size={24} className="text-gray-700" />
          <Title order={4}>{title}</Title>
        </Group>
          <Badge>{units[type]}</Badge>
      </Group>

      <div className="flex justify-center mb-4">
        <PieChart width={120} height={120}>
          <Pie
            data={chartData}
            cx={60}
            cy={60}
            innerRadius={40}
            outerRadius={55}
            startAngle={180}
            endAngle={0}
            paddingAngle={2}
            dataKey="value"
          >
            {chartData.map((_entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={cardStyles[type].chartColors[index]}
              />
            ))}
          </Pie>
        </PieChart>
      </div>

      <Stack gap="xs">
        {Object.entries(data).map(([key, value]) => {
          const formattedKey = key.replace(/_/g, " ").toUpperCase();
          return (
            <Group key={key} justify="space-between">
              <Text size="sm" c="dimmed">
                {formattedKey}
              </Text>
              <Text fw={500}>{formatValue(key, value)}</Text>
            </Group>
          );
        })}
      </Stack>
    </Card>
  );
};

const WalletsTransactions = () => {
  const [startDate, setStartDate] = useState<Date | null>(new Date());
  const [endDate, setEndDate] = useState<Date | null>(new Date());
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [summaryMetrics, setSummaryMetrics] = useState<SummaryMetrics | null>(
    null
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [downloadFormat, setDownloadFormat] = useState("csv");
  const [sortConfig, setSortConfig] = useState({
    key: "date",
    direction: "desc" as "asc" | "desc",
  });
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(10);
  const { isLoggedIn } = useAuth();

  useEffect(() => {
    if (!isLoggedIn) {
      setError("User authentication required. Please log in.");
    }
  }, [isLoggedIn]);

  const validateDates = useCallback(() => {
    if (!startDate || !endDate) {
      setError("Please select both start and end dates");
      return false;
    }
    return startDate <= endDate;
  }, [startDate, endDate]);

  const fetchTransactions = async () => {
    if (!validateDates()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await api.get(
        "/wallets_transactions/wallet-dir-pay-transactions/view",
        {
          params: {
            start_date: formatDate(startDate),
            end_date: formatDate(endDate, true),
          },
        }
      );

      const transactionData = response.data.transactions || [];
      setTransactions(transactionData);

      if (response.data.summary_metrics) {
        setSummaryMetrics(response.data.summary_metrics);
      }

      setCurrentPage(1);
    } catch (err: unknown) {
      console.error("API Error:", err);
      setError(
        isAxiosError(err) ? err.response?.data?.message : "Failed to fetch data"
      );
    } finally {
      setLoading(false);
    }
  };

  const sortTransactions = (key: keyof Transaction) => {
    setSortConfig((current) => ({
      key,
      direction: current.key === key && current.direction === "asc" ? "desc" : "asc",
    }));
  };

  const downloadTransactions = async () => {
    if (!transactions.length) return;

    setLoading(true);
    try {
      const response = await api.get(
        "/wallets_transactions/wallet-dir-pay-transactions/download",
        {
          params: {
            start_date: formatDate(startDate),
            end_date: formatDate(endDate, true),
            format: downloadFormat,
          },
          responseType: "blob",
        }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `transactions.${downloadFormat}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Download Error:", err);
      setError(
        isAxiosError(err) ? err.response?.data?.message : "Failed to download transactions"
      );
    } finally {
      setLoading(false);
    }
  };

  const getSortedAndPaginatedTransactions = useCallback(() => {
    const sorted = [...transactions].sort((a, b) => {
      const aValue = a[sortConfig.key as keyof Transaction];
      const bValue = b[sortConfig.key as keyof Transaction];

      if (aValue == null || bValue == null) return 0;
      if (aValue < bValue) return sortConfig.direction === "asc" ? -1 : 1;
      if (aValue > bValue) return sortConfig.direction === "asc" ? 1 : -1;
      return 0;
    });

    if (itemsPerPage === 0) return sorted;

    const startIndex = (currentPage - 1) * itemsPerPage;
    return sorted.slice(startIndex, startIndex + itemsPerPage);
  }, [transactions, sortConfig, currentPage, itemsPerPage]);

  const totalPages = itemsPerPage === 0 ? 1 : Math.ceil(transactions.length / itemsPerPage);

  const SortHeader = ({ label, field }: { label: string; field: keyof Transaction }) => (
    <Group gap="xs" onClick={() => sortTransactions(field)} style={{ cursor: "pointer" }}>
      {label}
      {sortConfig.key === field && (
        sortConfig.direction === "asc" ? <ArrowUp size={14} /> : <ArrowDown size={14} />
      )}
    </Group>
  );

  const units = {
    water: "M³",
    energy: "kWh",
    gas: "Kg",
    financial: "Usd",
  };

  return (
    <div className="max-w-7xl mx-auto p-4">
      <Card shadow="sm" padding="lg" radius="md" withBorder>
        <Title order={2} mb="md">Wallet & Direct Payments Dashboard</Title>

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
            <Button onClick={fetchTransactions} loading={loading}>
              View Transactions
            </Button>
          </Group>

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
            <Select
              label="Items per page"
              value={itemsPerPage.toString()}
              onChange={(value) => {
                setItemsPerPage(Number(value));
                setCurrentPage(1);
              }}
              data={ITEMS_PER_PAGE_OPTIONS.map((value) => ({
                value: value.toString(),
                label: value === 0 ? "All" : value.toString(),
              }))}
            />
          </Group>
        </Stack>

        {error && (
          <Alert icon={<AlertCircle size={16} />} title="Error" color="red" mt="md">
            {error}
          </Alert>
        )}
      </Card>

      {summaryMetrics && (
        <Grid mt="md" gutter="md">
          {(Object.entries(summaryMetrics) as Array<[keyof SummaryMetrics, UtilityMetrics | FinancialMetrics]>).map(([key, data]) => (
            <Grid.Col key={key} span={3}>
              <SummaryCard
                title={`${key.charAt(0).toUpperCase() + key.slice(1)} Metrics`}
                data={data}
                type={key as "water" | "energy" | "gas" | "financial"}
                units={units}
              />
            </Grid.Col>
          ))}
        </Grid>
      )}

      {transactions.length === 0 && !loading && (
        <Center mt="xl">
          <Text>No transactions found for the selected period.</Text>
        </Center>
      )}

      {transactions.length > 0 && (
        <Card shadow="sm" padding="lg" radius="md" withBorder mt="md">
          <Group justify="space-between" mb="md">
            <Title order={3}>Transaction History</Title>
            <Button
              onClick={downloadTransactions}
              disabled={loading || transactions.length === 0}
              leftSection={<FileDown size={16} />}
            >
              Download Statement
            </Button>
          </Group>

          <Table striped highlightOnHover withTableBorder withColumnBorders>
            <Table.Thead>
              <Table.Tr>
                <Table.Th><SortHeader label="Date" field="date" /></Table.Th>
                <Table.Th><SortHeader label="Transaction Type" field="transaction_type" /></Table.Th>
                <Table.Th><SortHeader label="Payment Method" field="payment_method" /></Table.Th>
                <Table.Th><SortHeader label="Utility Type" field="utility_type" /></Table.Th>
                <Table.Th><SortHeader label="Units" field="units" /></Table.Th>
                <Table.Th><SortHeader label="Amount" field="amount" /></Table.Th>
                <Table.Th>Initial Balance</Table.Th>
                <Table.Th>Final Balance</Table.Th>
                <Table.Th>Recharge Token</Table.Th>
                <Table.Th><SortHeader label="Status" field="status" /></Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {getSortedAndPaginatedTransactions().map(({
                id,
                date,
                units,
                amount,
                status,
                recharge_token,
                initial_balance,
                final_balance,
                utility_type,
                transaction_type,
                payment_method
              }) => (
                <Table.Tr key={id}>
                  <Table.Td>{new Date(date).toLocaleString()}</Table.Td>
                  <Table.Td>{transaction_type}</Table.Td>
                  <Table.Td>{payment_method}</Table.Td>
                  <Table.Td>{utility_type}</Table.Td>
                  <Table.Td>{units.toLocaleString()}</Table.Td>
                  <Table.Td>${amount.toFixed(2)}</Table.Td>
                  <Table.Td>${initial_balance?.toFixed(2) ?? "0.00"}</Table.Td>
                  <Table.Td>${final_balance?.toFixed(2) ?? "0.00"}</Table.Td>
                  <Table.Td>
                    {recharge_token ? (
                      <Group gap="xs">
                        <Text>{recharge_token}</Text>
                        <Tooltip label="Copy token">
                          <ActionIcon
                            variant="subtle"
                            onClick={() => navigator.clipboard.writeText(recharge_token)}
                          >
                            <Copy size={16} />
                          </ActionIcon>
                        </Tooltip>
                      </Group>
                    ) : (
                      "---"
                    )}
                  </Table.Td>
                  <Table.Td>
                    <Badge
                      variant="dot"
                      color={status === "completed" ? "green" : "yellow"}
                    >
                      {status}
                    </Badge>
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>

          {itemsPerPage > 0 && (
            <Group justify="center" mt="md">
              <Pagination
                value={currentPage}
                onChange={setCurrentPage}
                total={totalPages}
              />
            </Group>
          )}
        </Card>
      )}
    </div>
  );
};

export default WalletsTransactions;