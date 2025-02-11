// DummyPaymentPage.tsx
import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { showNotification } from "@mantine/notifications";
import { Check, ArrowLeft, Wallet, CreditCard } from "lucide-react";
import axios from "axios";
import { Card, Text, Button, Popover, Stack, Group } from "@mantine/core";
import CardPayments from "./CardPayments"; // Importing the CardPayments component

interface PurchaseDetails {
    utilityType: string;
    units?: number;
    amount?: number;
    rate: number;
}

interface PaymentError {
    message: string;
    required_amount: number;
    wallet_balance: number;
}

const DummyPaymentPage = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const purchaseDetails = location.state as PurchaseDetails;

    // State management
    const [paymentState, setPaymentState] = useState({
        cardNumber: "",
        expiryDate: "",
        cvv: "",
        isProcessing: false,
        paymentSuccess: false,
        rechargeToken: "",
        paymentMethod: 'wallet' as 'wallet' | 'direct',
        showInsufficientFundsPopover: false,
        paymentError: null as PaymentError | null,
        units: purchaseDetails?.units || 0,
        amount: purchaseDetails?.amount || 0,
        walletBalance: 0,
    });

    // Fetch wallet balance
    useEffect(() => {
        const fetchWalletBalance = async () => {
            try {
                const accessToken = sessionStorage.getItem('accessToken');
                const response = await axios.get("http://localhost:5000/api/wallet/balances", {
                    headers: { Authorization: `Bearer ${accessToken}` },
                });
                setPaymentState(prev => ({ ...prev, walletBalance: response.data.balance }));
            } catch (error) {
                console.error("Failed to fetch wallet balance", error);
            }
        };

        fetchWalletBalance();
    }, []);

    // Redirect if necessary
    useEffect(() => {
        if (!purchaseDetails?.utilityType || !purchaseDetails?.rate) {
            navigate("/dashboard/purchase-utility", { replace: true });
        }
    }, [purchaseDetails, navigate]);

    // Handle payment button click
    const handlePayment = async () => {
        setPaymentState(prev => ({ ...prev, isProcessing: true }));

        const paymentBody = {
            utility_type: purchaseDetails.utilityType,
            units: paymentState.units,
            payment_method: paymentState.paymentMethod,
            amount: paymentState.amount,
            ...(paymentState.paymentMethod === 'direct' ? {
                card_number: paymentState.cardNumber,
                expiry_date: paymentState.expiryDate,
                cvv: paymentState.cvv,
            } : {}),
        };

        try {
            const accessToken = sessionStorage.getItem('accessToken');
            const purchaseResponse = await axios.post("http://localhost:5000/api/wallet/purchase-utility", paymentBody, {
                headers: { 
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${accessToken}`,
                },
            });

            const { recharge_token } = purchaseResponse.data;
            if (recharge_token) {
                setPaymentState(prev => ({ ...prev, rechargeToken: recharge_token, paymentSuccess: true, isProcessing: false }));
                showNotification({
                    title: "Payment Successful",
                    message: `Recharge Token: ${recharge_token}`,
                    color: "green",
                    icon: <Check />,
                    autoClose: 5000,
                });
                setTimeout(() => navigate("/dashboard"), 5000);
            }

        } catch (error) {
            handleErrorResponse(error);
        }
    };

    // Handle error response
    const handleErrorResponse = (error: unknown) => {
        setPaymentState(prev => ({ ...prev, isProcessing: false }));

        if (axios.isAxiosError(error) && error.response?.status === 402) {
            const errorData = error.response.data as PaymentError;
            setPaymentState(prev => ({ ...prev, paymentError: errorData, showInsufficientFundsPopover: true }));
        } else {
            const errorMessage = axios.isAxiosError(error) ? error.response?.data?.message || "Payment failed" : "Payment failed";
            showNotification({ title: "Payment Error", message: errorMessage, color: "red" });
        }
    };

    // Handle payment method change
    const handlePaymentMethodChange = (method: 'wallet' | 'direct') => {
        setPaymentState(prev => ({
            ...prev,
            paymentMethod: method,
            ...(method === 'wallet' ? { cardNumber: "", expiryDate: "", cvv: "" } : {})
        }));
    };
  //   const handlePaymentMethodChange = (method: 'wallet' | 'direct') => {
  //     setPaymentState(prev => ({
  //         ...prev,
  //         paymentMethod: method,
  //         ...(method === 'wallet' ? { cardNumber: "", expiryDate: "", cvv: "" } : {}),
  //     }));
  // };
    // Insufficient Funds Popover
    const InsufficientFundsPopover = () => (
        <Popover 
            opened={paymentState.showInsufficientFundsPopover}
            onClose={() => setPaymentState(prev => ({ ...prev, showInsufficientFundsPopover: false }))} 
            position="bottom" 
            withArrow>
            <Popover.Dropdown>
                {paymentState.paymentError && (
                    <Stack gap="xs">
                        <Text size="sm">Current Balance: ${paymentState.paymentError.wallet_balance.toFixed(2)}</Text>
                        <Text size="sm">Required Amount: ${paymentState.amount.toFixed(2)}</Text>
                        <Text size="sm">{paymentState.paymentError.message}</Text>
                        <Group gap="xs">
                            <Button size="xs" onClick={handlePayment}>Continue with Card Payment</Button>
                            <Button size="xs" onClick={() => navigate("/dashboard/deposit-funds")}>Add Funds</Button>
                            <Button size="xs" variant="outline" onClick={() => navigate("/dashboard/purchase-utility")}>Cancel</Button>
                        </Group>
                    </Stack>
                )}
            </Popover.Dropdown>
        </Popover>
    );

    return (
        <div className="flex justify-center items-center min-h-screen bg-gray-100">
            <Card className="w-full max-w-lg p-8 shadow-lg bg-white">
                <div className="flex items-center justify-between p-4">
                    <Text className="text-2xl font-bold">{paymentState.paymentMethod === 'wallet' ? 'Wallet Payment' : 'Direct Payment'}</Text>
                    <Button variant="ghost" size="sm" onClick={() => navigate("/dashboard/purchase-utility")}>
                        <ArrowLeft className="mr-2 h-4 w-4" /> Back
                    </Button>
                </div>

                <div className="p-4 space-y-4">
                    {!paymentState.paymentSuccess ? (
                        <>
                            <Text className="text-lg font-semibold">Utility: {purchaseDetails.utilityType}</Text>
                            <Text className="text-lg mt-4">Select Payment Method:</Text>
                            <Group gap="xs" className="mb-4">
                                <Button 
                                    variant={paymentState.paymentMethod === 'wallet' ? 'filled' : 'outline'} 
                                    onClick={() => handlePaymentMethodChange('wallet')}>
                                    <Wallet size={16} /> Wallet
                                </Button>
                                <Button 
                                    variant={paymentState.paymentMethod === 'direct' ? 'filled' : 'outline'} 
                                    onClick={() => handlePaymentMethodChange('direct')}>
                                    <CreditCard size={16} /> Card
                                </Button>
                            </Group>

                            {paymentState.paymentMethod === 'direct' && (
                                <CardPayments 
                                    onCardNumberChange={(cardNumber: string) => setPaymentState(prev => ({ ...prev, cardNumber }))}
                                    onExpiryDateChange={(expiryDate: string) => setPaymentState(prev => ({ ...prev, expiryDate }))}
                                    onCVVChange={(cvv: string) => setPaymentState(prev => ({ ...prev, cvv }))}
                                />
                            )}

                            <Button 
                                className="mt-6 w-full" 
                                color="green" 
                                onClick={handlePayment}
                                loading={paymentState.isProcessing}
                                disabled={paymentState.isProcessing || 
                                  (paymentState.paymentMethod === 'wallet' && paymentState.walletBalance < paymentState.amount) || 
                                  (paymentState.paymentMethod === 'direct' && (!paymentState.cardNumber || !paymentState.expiryDate || !paymentState.cvv))
                                }>
                                Confirm Payment
                            </Button>

                            <InsufficientFundsPopover />
                        </>
                    ) : (
                        <Text className="alert-success">Payment Successful! Your Recharge Token: {paymentState.rechargeToken}</Text>
                    )}
                </div>
            </Card>
        </div>
    );
};

export default DummyPaymentPage;