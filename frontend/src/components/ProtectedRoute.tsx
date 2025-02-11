import { ReactNode, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

interface ProtectedRouteProps {
  children: ReactNode;
}

const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const token = sessionStorage.getItem('accessToken'); // Ensure this matches with your login token name

  useEffect(() => {
    const verifyToken = async () => {
      if (!token) {
        navigate('/login');
        return;
      }

      try {
        // Set up Axios with the token
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        
        // Call backend to verify the token
        await axios.get('http://localhost:5000/api/auth/protected'); // Adjust the URL based on your backend route
        
        // If the token is valid, proceed with the component rendering
        setLoading(false);
      } catch (error) {
        // If token is invalid or expired, clear the token and redirect
        console.error('Token verification failed:', error);
        sessionStorage.removeItem('accessToken');
        navigate('/login');
      }
    };

    verifyToken();
  }, [token, navigate]);

  // Show nothing while checking authentication status
  if (loading) return null;

  return <>{children}</>;
};

export default ProtectedRoute;
