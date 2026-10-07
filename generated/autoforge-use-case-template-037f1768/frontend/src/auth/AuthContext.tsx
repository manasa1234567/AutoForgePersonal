import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import axios from 'axios';

interface User {
  username: string;
  roles: string[];
}

interface AuthContextType {
  token: string | null;
  user: User | null;
  login: (token: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);

  // When token changes, try to decode user info
  useEffect(() => {
    if (token) {
      // In real scenario, decode token or call an API
      // Here map the token string used in FastAPI mock to user info
      switch (token) {
        case 'employee_token':
          setUser({ username: 'employee1', roles: ['Employee'] });
          break;
        case 'trainer_token':
          setUser({ username: 'trainer1', roles: ['Trainer'] });
          break;
        case 'manager_token':
          setUser({ username: 'manager1', roles: ['Manager'] });
          break;
        case 'coordinator_token':
          setUser({ username: 'coordinator1', roles: ['Coordinator'] });
          break;
        case 'admin_token':
          setUser({ username: 'admin1', roles: ['Administrator'] });
          break;
        default:
          setUser(null);
          break;
      }
    } else {
      setUser(null);
    }
  }, [token]);

  async function login(newToken: string) {
    setToken(newToken);
  }

  function logout() {
    setToken(null);
  }

  return (
    <AuthContext.Provider value={{ token, user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
