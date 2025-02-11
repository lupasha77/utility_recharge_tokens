import { useState } from 'react';
import { Modal, Button, TextInput, Text } from '@mantine/core';

const TokenPurchase = () => {
    const [purchasedToken, setPurchasedToken] = useState<string | null>(null);
    const [units, setUnits] = useState<number>(0);
    const [totalAmount, setTotalAmount] = useState<number>(0);
    const [opened, setOpened] = useState(false);

    const handlePurchaseToken = async () => {
        const response = await fetch('http://localhost:5000/purchase-token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${sessionStorage.getItem('token')}` // Assuming you store the JWT in sessionStorage
            },
            body: JSON.stringify({ units })
        });

        const data = await response.json();
        if (data.success) {
            setPurchasedToken(data.token); // Store the token in state
            setTotalAmount(data.totalAmount);
            setOpened(true); // Open the modal
        } else {
            alert('Failed to purchase token');
        }
    };

    return (
        <div>
            <TextInput
                type="number"
                placeholder="Enter number of units"
                value={units}
                onChange={(e) => setUnits(Number(e.target.value))}
            />
            <Button onClick={handlePurchaseToken}>Purchase Token</Button>

            <Modal
                opened={opened}
                onClose={() => setOpened(false)}
                title="Purchase Successful"
            >
                <Text>Your Token: {purchasedToken}</Text>
                <Text>Total Amount: ${totalAmount}</Text>
            </Modal>
        </div>
    );
};

export default TokenPurchase;