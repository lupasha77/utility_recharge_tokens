
// src/components/context/AuthContext.ts
import { createContext } from 'react';
 
export interface AuthContextType {
  user: { email: string; accessToken: string; firstName: string; lastName: string; role: string } | null;
  login: (credentials: { email: string; password: string }) => Promise<boolean | undefined>;
  logout: () => Promise<void>;
  isLoggedIn: boolean;
  refreshToken: () => Promise<boolean>;
}
export const AuthContext = createContext<AuthContextType | null>(null);
