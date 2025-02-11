// src/components/payments/PurchaseUtility.tsx
import { useState } from 'react';
import { Button, Radio, Group, TextInput } from '@mantine/core';

const PurchaseUtility = () => {
  const [paymentMethod, setPaymentMethod] = useState('wallet');  // Default to wallet
  const [utilityType, setUtilityType] = useState('');
  const [units, setUnits] = useState('');

  const accessToken = 'your_access_token_here'; // Replace with actual access token

  const handleSubmit = async () => {
    const response = await fetch('http://localhost:5000/api/wallet/purchase-utility', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
      },
      body: JSON.stringify({
        utility_type: utilityType,
        units: parseInt(units, 10),
        payment_method: paymentMethod,  // Send payment method with request
      }),
    });

    const data = await response.json();
    if (response.ok) {
      if (paymentMethod === 'wallet') {
        alert('Utility purchase successful via wallet');
      } else {
        // Handle redirection for direct payment
        window.location.href = data.redirect_url;  // Redirect to payment page
      }
    } else {
      alert(data.message || 'An error occurred');
    }
  };

  return (
    <div>
      <TextInput
        label="Utility Type"
        value={utilityType}
        onChange={(e) => setUtilityType(e.target.value)}
      />
      <TextInput
        label="Units"
        type="number"
        value={units}
        onChange={(e) => setUnits(e.target.value)}
      />
      <Group  >
        <Radio
          label="Pay with Wallet"
          value="wallet"
          checked={paymentMethod === 'wallet'}
          onChange={() => setPaymentMethod('wallet')}
        />
        <Radio
          label="Pay with Direct Payment"
          value="direct"
          checked={paymentMethod === 'direct'}
          onChange={() => setPaymentMethod('direct')}
        />
      </Group>
      <Button onClick={handleSubmit}>Purchase</Button>
    </div>
  );
};

export default PurchaseUtility;
