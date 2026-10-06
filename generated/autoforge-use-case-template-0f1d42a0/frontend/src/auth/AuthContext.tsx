import React, { createContext, useContext, useState, useEffect } from "react";
import axios from "axios";

interface User {
  id: number;
  email: string;
  name: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: () => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  login: () => {},
  logout: () => {},
});

// Fake OAuth redirect login for demo
function simulateSSOLogin(): Promise<User> {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ id: 1, email: "jane.doe@example.com", name: "Jane Doe", role: "employee" });
    }, 500);
  });
}

export const AuthProvider: React.FC<React.PropsWithChildren> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const login = () => {
    setLoading(true);
    simulateSSOLogin().then((u) => {
      setUser(u);
      setLoading(false);
    });
  };

  const logout = () => {
    setUser(null);
  };

  useEffect(() => {
    // For demo, auto login after mount
    login();
  }, []);

  return <AuthContext.Provider value={{ user, loading, login, logout }}>{children}</AuthContext.Provider>;
};

export const useAuth = () => useContext(AuthContext);
