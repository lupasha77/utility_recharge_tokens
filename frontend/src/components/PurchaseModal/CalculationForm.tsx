import { memo } from 'react';
import { NumberInput, Select, Text, Button } from '@mantine/core';
import { UseFormReturnType } from '@mantine/form';

interface FormValues {
  units: number;
  amount: number;
  cardNumber: string;
  expiryDate: string;
  cvv: string;
}

interface CalculationFormProps {
  calculationMode: 'units' | 'amount';
  onModeChange: (value: string | null) => void;
  form: UseFormReturnType<FormValues>;
  handleCalculation: (value: number) => void;
  onProceed: () => void;
}

const CalculationForm = memo(({
  calculationMode,
  onModeChange,
  form,
  handleCalculation,
  onProceed
}: CalculationFormProps) => (
  <>
    <Select
      label="Calculate by"
      data={[
        { label: 'Number of Units', value: 'units' },
        { label: 'Amount (USD)', value: 'amount' }
      ]}
      value={calculationMode}
      onChange={onModeChange}
    />
    {calculationMode === 'units' ? (
      <NumberInput
        label="Number of Units"
        min={1}
        value={form.values.units}
        onChange={(value) => handleCalculation(typeof value === 'number' ? value : 0)}
      />
    ) : (
      <NumberInput
        label="Amount (USD)"
        min={1}
        value={form.values.amount}
        onChange={(value) => handleCalculation(typeof value === 'number' ? value : 0)}
      />
    )}
    <Text>
      {calculationMode === 'units'
        ? `Total Amount: USD ${form.values.amount.toFixed(2)}`
        : `Units to receive: ${form.values.units}`}
    </Text>
    <Button onClick={onProceed}>Proceed to Payment</Button>
  </>
));

export default CalculationForm;