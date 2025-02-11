// useDashboardData.ts
import { useState, useEffect } from 'react';
import { api } from '../utils/api/axios';
import { UtilityData } from '../utils/type';
import { useAuth } from '../components/context/useAuthHook';

interface Profile {
  first_name: string;
  last_name: string;
  email: string;
}

interface DashboardData {
  balance: number;
  utilities: UtilityData[];
  profile: Profile;
}

export const useDashboardData = () => {
  const { isLoggedIn } = useAuth();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isLoggedIn) {
      setError('User authentication required. Please log in.');
      setLoading(false);
      return;
    }

    const fetchDashboardData = async () => {
      try {
        const [balanceRes, utilitiesRes, profileRes] = await Promise.all([
          api.get('/wallet/balances'),
          api.get('/utilities/get_monthly_utility_data'),
          api.get('/dashboard/profile'),
        ]);

        // console.log("Utility API Response:", utilitiesRes.data.utilities); // ✅ Debug response

        // Deduplicate utilities by utility_type
        const uniqueUtilities = utilitiesRes.data.utilities.reduce((acc: UtilityData[], current: UtilityData) => {
          const exists = acc.find(item => item.utility_type === current.utility_type);
          if (!exists) {
            acc.push(current);
          }
          return acc;
        }, []);

        // console.log("Filtered Utilities:", uniqueUtilities); // ✅ Debug final data

        setData({
          balance: balanceRes.data['wallet_balance'] || 0,
          utilities: uniqueUtilities,
          profile: profileRes.data.profile,
        });
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Unable to load dashboard data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [isLoggedIn]);

  return { data, loading, error };
};