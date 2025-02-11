// frontend/src/components/PurchaseModal/PaymentForm.tsx
import { memo } from 'react';
import { TextInput, Group, Button } from '@mantine/core';
import { UseFormReturnType } from '@mantine/form';

interface FormValues {
  units: number;
  amount: number;
  cardNumber: string;
  expiryDate: string;
  cvv: string;
}

export interface PaymentFormProps {
  form: UseFormReturnType<FormValues>;
  isProcessing: boolean;
}

const PaymentForm = memo(({ form, isProcessing }: PaymentFormProps) => (
  <>
    <TextInput
      label="Card Number"
      placeholder="1234 5678 9012 3456"
      {...form.getInputProps('cardNumber')}
    />
    <Group grow>
      <TextInput
        label="Expiry Date"
        placeholder="MM/YY"
        {...form.getInputProps('expiryDate')}
      />
      <TextInput
        label="CVV"
        placeholder="123"
        {...form.getInputProps('cvv')}
      />
    </Group>
    <Button type="submit" loading={isProcessing}>
      Complete Purchase
    </Button>
  </>
));

export default PaymentForm;