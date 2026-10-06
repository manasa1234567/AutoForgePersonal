import React, { createContext, useContext, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

// User type matches backend roles
interface User {
  id: string;
  name: string;
  email: string;
  role: string; // 'Employee', 'Trainer', 'Manager', 'Administrator', 'Learning Program Coordinator'
}

interface AuthContextType {
  user: User | null;
  login: () => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const navigate = useNavigate();

  // Replace mock with real Microsoft Entra ID/OIDC login OpenID Connect flow
  async function login() {
    // For demo, simulate an asynchronous login
    return new Promise<void>((resolve) => {
      setTimeout(() => {
        const mockUser: User = {
          id: 'user-1',
          name: 'Alice Employee',
          email: 'alice.employee@example.com',
          role: 'Employee',
        };
        setUser(mockUser);
        resolve();
      }, 500);
    });
  }

  function logout() {
    setUser(null);
    navigate('/login');
  }

  useEffect(() => {
    // Simulate session restore or token validation with backend
  }, []);

  return <AuthContext.Provider value={{ user, login, logout }}>{children}</AuthContext.Provider>;
};

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
