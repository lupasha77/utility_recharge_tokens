import { useMemo } from 'react';
import { Paper, Title, Table, Grid, Group, Text, Card, RingProgress, Stack } from '@mantine/core';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, PieChart, Pie, Cell } from 'recharts';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28'];
const UTILITY_TYPES = ['water', 'energy', 'gas'];

interface UtilityBalance {
  type: string;
  total: number;
  used: number;
  purchased: number;
  cost: number;
  remaining: number;
  remaining_cost: number;
}

interface MonthlyUtilityData {
  utility_type: string;
  balance_brought_forward: number;
  units_bought: number;
  units_used: number;
  cost_of_units_used: number;
  cost_of_units_purchased: number;
  balance_remaining: number;
}

interface UtilityDashboardProps {
  balances: UtilityBalance[];
  monthlyData: MonthlyUtilityData[];
}

const UtilityDashboardComponent = ({ balances, monthlyData }: UtilityDashboardProps) => {
  const pieChartData = useMemo(() => 
    balances.map(balance => ({
      name: balance.type.charAt(0).toUpperCase() + balance.type.slice(1),
      value: balance.cost
    })),
    [balances]
  );

  // const totalCost = useMemo(() => 
  //   balances.reduce((sum, balance) => sum + balance.cost, 0),
  //   [balances]
  // );

  const renderUtilityCard = (balance: UtilityBalance) => {
    const usagePercentage = (balance.used / balance.total) * 100;
    const color = COLORS[UTILITY_TYPES.indexOf(balance.type)];

    return (
      <Card key={balance.type} padding="lg" radius="md" withBorder>
        <Group justify='space-between' mb="md">
          <Text size="lg" tt="capitalize">
            {balance.type}
          </Text>
          <RingProgress
            size={80}
            thickness={8}
            sections={[{ value: usagePercentage, color }]}
            label={
              <Text size="xs" ta="center">
                {usagePercentage.toFixed(1)}%
              </Text>
            }
          />
        </Group>

        <Stack gap="xs">
          <Group justify="space-between">
            <Text size="sm" c="dimmed">Total Units:</Text>
            <Text  fw={500}>{balance.total.toFixed(2)}</Text>
          </Group>
          <Group justify="space-between">
            <Text size="sm" c="dimmed">Used:</Text>
            <Text  fw={500}>{balance.used.toFixed(2)}</Text>
          </Group>
          <Group justify="space-between">
            <Text size="sm" c="dimmed">Remaining:</Text>
            <Text  fw={500}>{balance.remaining.toFixed(2)}</Text>
          </Group>
          <Group justify="space-between">
            <Text size="sm" c="dimmed">Cost:</Text>
            <Text  fw={500}>${balance.cost.toFixed(2)}</Text>
          </Group>
        </Stack>
      </Card>
    );
  };

  const monthlyUsageData = useMemo(() => {
    return monthlyData.map(data => ({
      type: data.utility_type,
      units: data.units_used,
      cost: data.cost_of_units_used,
      purchased: data.units_bought,
      purchaseCost: data.cost_of_units_purchased,
      balance: data.balance_remaining
    }));
  }, [monthlyData]);

  return (
    <Stack gap="lg">
      <Grid>
        {balances.map(balance => (
          <Grid.Col key={balance.type} span={{ base: 12, sm: 6, lg: 4 }}>
            {renderUtilityCard(balance)}
          </Grid.Col>
        ))}
      </Grid>

      <Paper shadow="xs" p="md">
        <Title order={2} mb="md">Monthly Usage Summary</Title>
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Utility</Table.Th>
              <Table.Th>Units Used</Table.Th>
              <Table.Th>Cost</Table.Th>
              <Table.Th>Units Purchased</Table.Th>
              <Table.Th>Purchase Cost</Table.Th>
              <Table.Th>Balance</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {monthlyUsageData.map((data) => (
              <Table.Tr key={data.type}>
                <Table.Td>{data.type}</Table.Td>
                <Table.Td>{data.units.toFixed(2)}</Table.Td>
                <Table.Td>${data.cost.toFixed(2)}</Table.Td>
                <Table.Td>{data.purchased.toFixed(2)}</Table.Td>
                <Table.Td>${data.purchaseCost.toFixed(2)}</Table.Td>
                <Table.Td>{data.balance.toFixed(2)}</Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      </Paper>

      <Grid>
        <Grid.Col span={{ base: 12, md: 6 }}>
          <Paper shadow="xs" p="md">
            <Title order={2} mb="md">Monthly Usage by Utility</Title>
            <BarChart width={500} height={300} data={monthlyUsageData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="type" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="units" name="Units Used" fill="#0088FE" />
              <Bar dataKey="purchased" name="Units Purchased" fill="#00C49F" />
            </BarChart>
          </Paper>
        </Grid.Col>

        <Grid.Col span={{ base: 12, md: 6 }}>
          <Paper shadow="xs" p="md">
            <Title order={2} mb="md">Cost Distribution</Title>
            <Group justify='center'>
              <PieChart width={400} height={300}>
                <Pie
                  data={pieChartData}
                  cx={200}
                  cy={150}
                  innerRadius={60}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                  label
                >
                  {pieChartData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </Group>
          </Paper>
        </Grid.Col>
      </Grid>
    </Stack>
  );
};

export default UtilityDashboardComponent;