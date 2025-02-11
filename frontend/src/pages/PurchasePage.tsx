import { useState, useEffect, useCallback } from "react";
import {
  Container,
  Select,
  NumberInput,
  Button,
  Text,
  Loader,
  Alert,
  Popover,
  SegmentedControl
} from "@mantine/core";
import { useNavigate } from 'react-router-dom';
import { useUtilityRates } from '../hooks/useUtilityRates';

const PurchasePage = () => {
  const { utilityRates, loading, error } = useUtilityRates();
  const [selectedUtility, setSelectedUtility] = useState<string | null>(null);
  const [quantity, setQuantity] = useState<number | "">(1);
  const [totalCost, setTotalCost] = useState<number>(0);
  const [purchaseMode, setPurchaseMode] = useState<'units' | 'amount'>('units');
  const [openPopover, setOpenPopover] = useState<boolean>(false);
  const navigate = useNavigate();

  const handleModeChange = useCallback((value: 'units' | 'amount') => {
    setPurchaseMode(value);
    if (value === 'amount') {
      const unitPrice = selectedUtility !== null ? utilityRates[selectedUtility!] || 1 : 1;
      const units = selectedUtility !== null ? Math.floor(Number(quantity) / unitPrice) : 0;
      setQuantity(units);
    } else {
      const unitPrice = selectedUtility ? utilityRates[selectedUtility!] || 1 : 1;
      const amount = selectedUtility !== null ? Number(quantity) * unitPrice : 0;
      setQuantity(amount);
    }
  }, [selectedUtility, quantity, utilityRates]);

  useEffect(() => {
    if (selectedUtility !== null && quantity !== "") {
      if (purchaseMode === 'units') {
        setTotalCost((utilityRates[selectedUtility!] || 0) * Number(quantity));
      } else {
        setTotalCost(Number(quantity));
      }
    }
  }, [selectedUtility, quantity, purchaseMode, utilityRates]);

  const handlePurchase = () => {
    if (!selectedUtility || quantity === "" || quantity <= 0) return;

    setOpenPopover(false);
    navigate("/dashboard/dummy-payment", {
      state: {
        utilityType: selectedUtility,
        units: purchaseMode === 'units' ? quantity : Math.floor(Number(quantity) / (utilityRates[selectedUtility!] || 1)),
        amount: totalCost,
        rate: utilityRates[selectedUtility!],
        paymentMethod: 'wallet', // Default payment method
      }
    });
  };

  return (
    <Container>
      <Text size="lg" fw={500}>
        Purchase Utilities
      </Text>

      {loading && <Loader />}
      {error && <Alert color="red">{error}</Alert>}

      {!loading && !error && (
        <>
          <Select
            label="Select Utility Type"
            placeholder="Choose a utility"
            data={Object.keys(utilityRates).map((type) => ({ value: type, label: type }))}
            value={selectedUtility}
            onChange={setSelectedUtility}
          />

          <SegmentedControl
            value={purchaseMode}
            onChange={(value) => handleModeChange(value as 'units' | 'amount')}
            data={[
              { label: 'Enter Units', value: 'units' },
              { label: 'Enter Amount', value: 'amount' }
            ]}
          />

          {purchaseMode === 'units' ? (
            <NumberInput
              label="Number of Units"
              value={quantity}
              onChange={(value) => setQuantity(value as number)}
              min={1}
              step={1}
            />
          ) : (
            <NumberInput
              label="Amount to Pay"
              value={quantity}
              onChange={(value) => setQuantity(value as number)}
              min={selectedUtility ? utilityRates[selectedUtility] || 1 : 1}
              step={selectedUtility ? utilityRates[selectedUtility] || 1 : 1}
            />
          )}

          {selectedUtility && (
            <Text mt="sm">
              Unit Price: ${utilityRates[selectedUtility]?.toFixed(2) || "N/A"}
            </Text>
          )}

          {totalCost > 0 && (
            <Text mt="sm" fw={500}>
              Total Cost: ${totalCost.toFixed(2)}
            </Text>
          )}

          {purchaseMode === 'amount' && (
            <Text mt="sm" fw={500}>
              Units Available: {selectedUtility ? Math.floor(Number(quantity) / (utilityRates[selectedUtility!] || 1)) : 0}
            </Text>
          )}

          <Popover
            opened={openPopover}
            onClose={() => setOpenPopover(false)}
            position="bottom"
            withArrow
          >
            <Popover.Target>
              <Button
                mt="md"
                onClick={() => setOpenPopover(true)}
                disabled={!selectedUtility || quantity === "" || quantity <= 0}
              >
                Confirm Purchase
              </Button>
            </Popover.Target>
            <Popover.Dropdown>
              <Text>Are you sure you want to purchase {purchaseMode === 'units' ? quantity : Math.floor(Number(quantity) / (utilityRates[selectedUtility!] || 1))} units of {selectedUtility} for ${totalCost.toFixed(2)}?</Text>
              <Button mt="sm" onClick={handlePurchase}>Confirm</Button>
              <Button mt="sm" variant="outline" onClick={() => setOpenPopover(false)}>Cancel</Button>
            </Popover.Dropdown>
          </Popover>
        </>
      )}
    </Container>
  );
};

export default PurchasePage;