import React from 'react';
import { Card, Text, Button, Group, ThemeIcon, Stack, Progress ,Badge} from '@mantine/core';
import { IconDroplet, IconFlame, IconAlertCircle, IconWallet } from '@tabler/icons-react';
import { useNavigate } from 'react-router-dom';
import { UtilityData } from '../../utils/type';
import { transformUtilityData } from '../../utils/TransformUtilityData';
import {  ZapIcon } from 'lucide-react';

const getUtilityColors = (type: string) => {
  switch (type.toLowerCase()) {
    case 'energy':
      return {
        background: 'bg-yellow-50',
        theme: 'yellow',
        progress: (usage: number) => usage > 80 ? 'red' : usage > 60 ? 'yellow' : 'green'
      };
    case 'water':
      return {
        background: 'bg-blue-50',
        theme: 'blue',
        progress: (usage: number) => usage > 80 ? 'red' : usage > 60 ? 'blue' : 'cyan'
      };
    case 'gas':
      return {
        background: 'bg-orange-50',
        theme: 'orange',
        progress: (usage: number) => usage > 80 ? 'red' : usage > 60 ? 'orange' : 'green'
      };
    default:
      return {
        background: 'bg-gray-50',
        theme: 'gray',
        progress: (usage: number) => usage > 80 ? 'red' : usage > 60 ? 'gray' : 'blue'
      };
  }
};

const getUtilityIcon = (type: string) => {
  switch (type.toLowerCase()) {
    case 'energy': return <ZapIcon size={24} />; 
//IconSunElectricity
    case 'water': return <IconDroplet size={16} />;
    case 'gas': return <IconFlame size={16} />;
    default: return <IconAlertCircle size={16} />;
  }
};

const formatNumber = (num: number | undefined): string => {
  if (num === undefined || isNaN(num)) return '0.00';
  return num.toFixed(2);
};

interface UtilityCardProps {
  utilityData: UtilityData;
}

const UtilityCard: React.FC<UtilityCardProps> = ({ utilityData }) => {
  const navigate = useNavigate();
  const utility = React.useMemo(() => transformUtilityData(utilityData), [utilityData]);
  const colors = React.useMemo(() => getUtilityColors(utility.utility_type), [utility.utility_type]);

  const usagePercentageUnits = React.useMemo(() => {
    if (!utility.total_units_to_date || utility.total_units_to_date <= 0) return 0;
    return Math.min((utility.units_used_to_date / utility.total_units_to_date) * 100, 100);
  }, [utility.total_units_to_date, utility.units_used_to_date]);

  const handlePurchaseToken = (utilityType: string) => {
    navigate('/dashboard/purchase/:utilityType', { state: { utilityType } });
  };

  return (
    <Card 
      shadow="sm" 
      padding="lg" 
      radius="md" 
      withBorder 
      className={colors.background}
    >
      <Stack gap="md">
        <Group justify="space-between">
          <Group gap="xs">
            <ThemeIcon size="md" variant="light" color={colors.theme}>
              {getUtilityIcon(utility.utility_type)}
            </ThemeIcon>
            <Text size="lg" fw={600} tt="capitalize">
              {utility.utility_type}
            </Text>
          </Group>
          <Badge size="sm" color={colors.theme}>
            ${formatNumber(utility.unit_price)}/unit
          </Badge>
        </Group>

        <Stack gap="xs">
          <Group justify="space-between">
            <Text size="sm" style={{ lineHeight: 3 }}>Total Units Purchased to date:</Text>
            <Badge size="sm">{formatNumber(utility.total_units_to_date)} </Badge>
          </Group>
          <Group justify="space-between">
            <Text size="sm" style={{ lineHeight: 3 }}  >Total cost of Units Purchased:</Text>
            <Badge size="sm" variant="outline" c={colors.theme}>USD {formatNumber(utility.cost_of_units_purchased_to_date)}</Badge>
          </Group>
        </Stack>

        <Stack gap="xs">
          <Progress 
            value={usagePercentageUnits} 
            size="md" 
            color={colors.progress(usagePercentageUnits)} 
          />
          <Group justify="space-between">
            <Text size="sm" style={{ lineHeight: 3 }}>Usage to date: </Text>
              <Badge size="sm" variant="outline" c={colors.theme}>{formatNumber(utility.units_used_to_date)} units</Badge>
          </Group>
          <Group justify="space-between">
            <Text size="sm" style={{ lineHeight: 3 }}>Balance of Units to date: </Text>
            <Badge>{formatNumber(utility.units_balance_remaining_to_date)} units</Badge>
          </Group>
        </Stack>

        <Button 
          fullWidth 
          leftSection={<IconWallet size={16} />} 
          color={colors.theme}
          onClick={() => handlePurchaseToken(utility.utility_type)}
        >
          Purchase {utility.utility_type}
        </Button>
      </Stack>
    </Card>
  );
};

export default UtilityCard;



// const getUtilityColors = (type: string, theme: MantineTheme) => {
//   const isDark = theme.colors.dark[0] === '#C1C2C5'; // Check if using dark theme

//   switch (type.toLowerCase()) {
//     case 'energy':
//       return {
//         background: isDark ? theme.colors.yellow[9] : theme.colors.yellow[0],
//         theme: 'yellow',
//         progress: (usage: number) => usage > 80 ? 'red' : usage > 60 ? 'yellow' : 'green'
//       };
//     case 'water':
//       return {
//         background: isDark ? theme.colors.blue[9] : theme.colors.blue[0],
//         theme: 'blue',
//         progress: (usage: number) => usage > 80 ? 'red' : usage > 60 ? 'blue' : 'cyan'
//       };
//     case 'gas':
//       return {
//         background: isDark ? theme.colors.orange[9] : theme.colors.orange[0],
//         theme: 'orange',
//         progress: (usage: number) => usage > 80 ? 'red' : usage > 60 ? 'orange' : 'green'
//       };
//     default:
//       return {
//         background: isDark ? theme.colors.gray[9] : theme.colors.gray[0],
//         theme: 'gray',
//         progress: (usage: number) => usage > 80 ? 'red' : usage > 60 ? 'gray' : 'blue'
//       };
//   }
// };