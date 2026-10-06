import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';

export interface User {
  id: string;
  name: string;
  email: string;
  roles: string[];
  token: string;
}

interface AuthContextType {
  user: User | null;
  login: (token: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);

  // Simulate fetching user info from token
  const fetchUser = async (token: string) => {
    // For demo, map token to fixed users
    const userMap: Record<string, Omit<User, 'token'>> = {
      'employee-token': { id: 'u1', name: 'Alice Employee', email: 'alice@example.com', roles: ['Employee'] },
      'trainer-token': { id: 'u2', name: 'Bob Trainer', email: 'bob@example.com', roles: ['Trainer/Mentor'] },
      'manager-token': { id: 'u3', name: 'Carol Manager', email: 'carol@example.com', roles: ['Manager'] },
      'admin-token': { id: 'u4', name: 'Dave Admin', email: 'dave@example.com', roles: ['Administrator'] },
      'coordinator-token': { id: 'u5', name: 'Eva Coordinator', email: 'eva@example.com', roles: ['Learning Program Coordinator'] }
    };
    const u = userMap[token];
    if (u) {
      return { ...u, token };
    }
    return null;
  };

  const login = async (token: string) => {
    const u = await fetchUser(token);
    if (u) {
      setUser(u);
      localStorage.setItem('authToken', token);
    } else {
      setUser(null);
      localStorage.removeItem('authToken');
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('authToken');
  };

  useEffect(() => {
    const token = localStorage.getItem('authToken');
    if (token) {
      login(token);
    }
  }, []);

  return <AuthContext.Provider value={{ user, login, logout }}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
