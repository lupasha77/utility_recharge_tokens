import { useState, useEffect } from "react";
import {
  Container,
  Card,
  Text,
  Group,
  Button,
  Stack,
  Title,
  Progress,
  SimpleGrid,
  LoadingOverlay,
  Alert,
} from "@mantine/core";
import { PieChart } from '@mantine/charts';
 
import {
//   Droplets,
//   Bolt,
//   Flame,
//   History,
//   CreditCard,
//   Wallet,
//   Plus,
  AlertCircle,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { api } from "../utils/api/axios";

type UtilityType = "water" | "energy" | "gas";

interface UtilityStats {
  purchased: number;
  purchasedCost: number;
  used: number;
  usedCost: number;
  balance: number;
  balanceCost: number;
  type: UtilityType;
}

interface DashboardData {
  utilities: UtilityStats[];
  transactions: { id: string; amount: number; date: string; description: string }[];
  monthlySummary: { [key: string]: number };
}

const UtilityCard = ({ utility }: { utility: UtilityStats }) => {
  const navigate = useNavigate();

  const usagePercentage = (utility.used / utility.purchased) * 100;
  const isLowOnUnits = utility.balance < (utility.purchased * 0.2);

  const chartData = [
    { value: utility.used, color: "#FF6384", name: "Used" },
    { value: utility.balance, color: "#36A2EB", name: "Remaining" },
  ];

  return (
    <Card shadow="sm" padding="lg" radius="md">
      <Stack>
        <Group>
          <Text size="lg" fw={500}>{utility.type.toUpperCase()}</Text>
        </Group>
        <Text size="sm">Purchased: {utility.purchased} units (${utility.purchasedCost})</Text>
        <Text size="sm">Used: {utility.used} units (${utility.usedCost})</Text>
        <Text size="sm">Balance: {utility.balance} units (${utility.balanceCost})</Text>
        <Progress value={usagePercentage} color={isLowOnUnits ? "red" : "blue"} size="lg" />
        <PieChart data={chartData} />
        <Button fullWidth onClick={() => navigate(`/purchase/${utility.type}`)}>Purchase More</Button>
      </Stack>
    </Card>
  );
};

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const res = await api.get("/dashboard");
        setDashboardData(res.data);
      } catch  {
        setError("Failed to load data");
      } finally {
        setLoading(false);
      }
    };
    fetchDashboardData();
  }, []);

  return (
    <Container size="lg" py="lg">
      <LoadingOverlay visible={loading} />
      {error && <Alert icon={<AlertCircle />} color="red">{error}</Alert>}
      {dashboardData && (
        <>
          <Title>Dashboard</Title>
          <SimpleGrid cols={3} spacing="lg">
            {dashboardData.utilities.map((utility) => (
              <UtilityCard key={utility.type} utility={utility} />
            ))}
          </SimpleGrid>
        </>
      )}
    </Container>
  );
};

export default Dashboard;
