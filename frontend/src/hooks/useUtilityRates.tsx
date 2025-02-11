import { useEffect, useState } from "react";
import { getUtilityRates } from "../utils/api/apiUtility";
import { useAuth } from '../components/context/useAuthHook';

export const useUtilityRates = () => {
  const [utilityRates, setUtilityRates] = useState<{ [key: string]: number }>({});
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const { isLoggedIn } = useAuth();

  useEffect(() => {
    if (!isLoggedIn) {
      setError('User authentication required. Please log in.');
      return;
    }

    const fetchRates = async () => {
      try {
        const data = await getUtilityRates();
        setUtilityRates(data);
      } catch {
        setError("Failed to load utility rates");
      } finally {
        setLoading(false);
      }
    };

    fetchRates();
  }, [isLoggedIn]);

  return { utilityRates, loading, error };
};