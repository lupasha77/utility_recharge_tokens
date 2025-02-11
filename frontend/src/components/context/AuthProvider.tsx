import React, { useState, useEffect, useCallback } from "react"; 
import { AuthContext } from "./AuthContext";
import { api } from "../../utils/api/axios";

interface User {
  email: string;
  accessToken: string;
  firstName: string;
  lastName: string;
  avatar?: string;
  role: string;
}

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const safeSetStorage = (key: string, value: string): boolean => {
    try {
      // Use sessionStorage instead of sessionStorage for session-based auth
      sessionStorage.setItem(key, value);
      return true;
    } catch (error) {
      console.error(`Storage error for ${key}:`, error);
      return false;
    }
  };

  const [user, setUser] = useState<User | null>(() => {
    const storedUser = sessionStorage.getItem("user");
    const accessToken = sessionStorage.getItem("accessToken");
    
    if (storedUser && accessToken) {
      try {
        return JSON.parse(storedUser);
      } catch {
        sessionStorage.removeItem("user");
        sessionStorage.removeItem("accessToken");
        return null;
      }
    }
    return null;
  });

  useEffect(() => {
    const interceptor = api.interceptors.request.use(
      (config) => {
        const token = sessionStorage.getItem("accessToken");
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    return () => {
      api.interceptors.request.eject(interceptor);
    };
  }, []);

  const logout = useCallback(async () => {
    try {
      const refreshToken = sessionStorage.getItem('refreshToken');
      
      if (!refreshToken) {
        console.log('No refresh token found, clearing session');
        sessionStorage.clear();
        setUser(null);
        return;
      }
  
      // Try to revoke the token server-side
      try {
        await api.post("/auth/logout", null, {
          headers: {
            'Authorization': `Bearer ${refreshToken}`,
            'Accept': 'application/json'
          },
          // Prevent axios from automatically handling the token
          transformRequest: [(data, headers) => {
            delete headers['Common']['Authorization'];
            return data;
          }]
        });
      } catch (error) {
        // Log but don't throw - we'll clear local state regardless
        console.warn('Server-side logout failed:', error);
      }
  
    } finally {
      // Clear all auth-related data
      const keysToRemove = [
        'accessToken',
        'refreshToken',
        'user',
        // Add any other auth-related keys
      ];
      
      keysToRemove.forEach(key => sessionStorage.removeItem(key));
      setUser(null);
  
      // Optional: Force reload to clear any in-memory state
      // window.location.href = '/login'; // or your login page
    }
  }, []);
  const forceLogout = useCallback(() => {
    sessionStorage.clear();
    setUser(null);
    // Optionally redirect to login
    window.location.href = '/login';
  }, []);
  useEffect(() => {
    const interceptor = api.interceptors.response.use(
      response => response,
      async (error) => {
        if (error.response?.status === 401 || error.response?.status === 422) {
          // Token is invalid/expired - force logout
          await forceLogout();
        }
        return Promise.reject(error);
      }
    );
  
    return () => {
      api.interceptors.response.eject(interceptor);
    };
  }, [forceLogout]);
  // Add to your AuthProvider
useEffect(() => {
  if (!user) return;

  // Check session every minute
  const interval = setInterval(() => {
    const lastActive = sessionStorage.getItem('lastActive');
    const SESSION_TIMEOUT = 30 * 60 * 1000; // 30 minutes

    if (lastActive && Date.now() - Number(lastActive) > SESSION_TIMEOUT) {
      logout();
    }
  }, 60000);

  // Update last active timestamp
  const updateLastActive = () => {
    sessionStorage.setItem('lastActive', Date.now().toString());
  };

  window.addEventListener('mousemove', updateLastActive);
  window.addEventListener('keydown', updateLastActive);

  return () => {
    clearInterval(interval);
    window.removeEventListener('mousemove', updateLastActive);
    window.removeEventListener('keydown', updateLastActive);
  };
}, [user, logout]);
  const login = useCallback(async (credentials: { email: string; password: string }): Promise<boolean> => {
    try {
      const response = await api.post('/auth/login', credentials);
      
      const { access_token, refresh_token, user: userData } = response.data;
      
      const essentialUserData = {
        email: userData.email,
        firstName: userData.firstName,
        lastName: userData.lastName,
        role: userData.role,
        accessToken: access_token,
        ...(userData.avatar?.length < 200 && { avatar: userData.avatar })
      };

      // Store in sessionStorage instead of sessionStorage
      const userStored = safeSetStorage('user', JSON.stringify(essentialUserData));
      const tokenStored = safeSetStorage('accessToken', access_token);
      const refreshStored = safeSetStorage('refreshToken', refresh_token);

      if (!userStored || !tokenStored || !refreshStored) {
        throw new Error('Failed to store authentication data');
      }

      setUser(essentialUserData);
      return true;
    } catch (error) {
      console.error('Login failed:', error);
      await logout();
      throw new Error(error instanceof Error ? error.message : 'Login failed');
    }
  }, [logout]);

  const refreshToken = useCallback(async () => {
    try {
      const refresh = sessionStorage.getItem('refreshToken');
      if (!refresh) {
        throw new Error('No refresh token available');
      }

      const response = await api.post('/auth/refresh', {
        refresh_token: refresh
      });

      const { access_token } = response.data;
      sessionStorage.setItem('accessToken', access_token);

      return true;
    } catch (error) {
      console.error('Token refresh failed:', error);
      await logout();
      return false;
    }
  }, [logout]);

  useEffect(() => {
    const verifyAuth = async () => {
      const accessToken = sessionStorage.getItem('accessToken');
      const storedUser = sessionStorage.getItem('user');

      if (accessToken && !user && storedUser) {
        try {
          const userData = JSON.parse(storedUser);
          setUser(userData);
        } catch (error) {
          console.error('Failed to parse stored user:', error);
          await logout();
        }
      } else if (!accessToken && user) {
        await logout();
      }
    };

    verifyAuth();
  }, [logout, user]);

  return (
    <AuthContext.Provider value={{
      user,
      login,
      logout,
      isLoggedIn: !!user,
      refreshToken
    }}>
      {children}
    </AuthContext.Provider>
  );
};