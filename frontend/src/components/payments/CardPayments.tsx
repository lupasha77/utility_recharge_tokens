import React from 'react';
import { TextInput, Space } from '@mantine/core';

// Types
type CardInputEvent = React.ChangeEvent<HTMLInputElement>;
type InputChangeHandler = (value: string) => void;

interface CardPaymentProps {
  onCardNumberChange: InputChangeHandler;
  onExpiryDateChange: InputChangeHandler;
  onCVVChange: InputChangeHandler;
}

// Custom hook for managing card input state and validation
const useCardInput = (
  initialValue: string, 
  formatter: (value: string) => string, 
  onChange: InputChangeHandler
) => {
  const [value, setValue] = React.useState(initialValue);

  const handleChange = (event: CardInputEvent) => {
    const newValue = formatter(event.target.value);
    setValue(newValue);
    onChange(newValue);
  };

  return { value, setValue, handleChange };
};

// Utility functions
const formatters = {
  cardNumber: (value: string): string => 
    value.replace(/\D/g, '').replace(/(\d{4})(?=\d)/g, '$1 ').trim().slice(0, 19),

  expiryDate: (value: string): string => {
    const cleaned = value.replace(/\D/g, '');
    if (cleaned.length < 3) return cleaned;
    return `${cleaned.slice(0, 2)}/${cleaned.slice(2, 4)}`;
  },

  cvv: (value: string): string => value.replace(/\D/g, '').slice(0, 3),
};

const validators = {
  expiryDate: (value: string): boolean => {
    const [month, year] = value.split('/').map(part => part.trim());
    if (!month || !year) return false;

    const expMonth = parseInt(month, 10);
    const expYear = parseInt(year, 10) + 2000;
    const now = new Date();
    const currentYear = now.getFullYear();
    const currentMonth = now.getMonth() + 1;

    return expMonth >= 1 && expMonth <= 12 && 
           (expYear > currentYear || (expYear === currentYear && expMonth >= currentMonth));
  }
};

const CardPayments: React.FC<CardPaymentProps> = React.memo(({ 
  onCardNumberChange, 
  onExpiryDateChange, 
  onCVVChange 
}) => {
  const cardNumber = useCardInput('', formatters.cardNumber, onCardNumberChange);
  const expiryDate = useCardInput('', formatters.expiryDate, (value) => {
    if (validators.expiryDate(value)) {
      onExpiryDateChange(value);
    }
  });
  const cvv = useCardInput('', formatters.cvv, onCVVChange);

  // Prevent multiple resets using useRef
  const isMounted = React.useRef(false);

  React.useEffect(() => {
    if (!isMounted.current) {
      cardNumber.setValue('');
      expiryDate.setValue('');
      cvv.setValue('');

      onCardNumberChange('');
      onExpiryDateChange('');
      onCVVChange('');
      
      isMounted.current = true;
    }
  }, []); // Ensures effect runs only once

  return (
    <div>
      <TextInput
        label="Card Number"
        placeholder="1234 5678 9012 3456"
        value={cardNumber.value}
        onChange={cardNumber.handleChange}
        maxLength={19}
      />
      <Space h="md" />
      <TextInput
        label="Expiry Date"
        placeholder="MM/YY"
        value={expiryDate.value}
        onChange={expiryDate.handleChange}
        maxLength={5}
      />
      <Space h="md" />
      <TextInput
        label="CVV"
        placeholder="123"
        type="password"
        value={cvv.value}
        onChange={cvv.handleChange}
        maxLength={3}
      />
    </div>
  );
});

CardPayments.displayName = 'CardPayments';

export default CardPayments;
