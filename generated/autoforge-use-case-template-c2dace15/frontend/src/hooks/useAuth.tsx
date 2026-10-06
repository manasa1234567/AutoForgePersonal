import React, { createContext, useContext, useState, useEffect } from "react";
import axios from "axios";

export interface User {
  username: string;
  roles: string[];
}

interface AuthContextType {
  user: User | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
  error: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Check localStorage for token and validate
    const token = localStorage.getItem("token");
    if (token) {
      // Decode token payload to get username/roles (no verification here for demo)
      try {
        const payload = JSON.parse(atob(token.split(".")[1]));
        setUser({ username: payload.sub, roles: payload.roles || [] });
      } catch {
        setUser(null);
      }
    }
    setLoading(false);
  }, []);

  const login = async (username: string, password: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post("/auth/token", new URLSearchParams({ username, password }), {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });
      const token = response.data.access_token;
      localStorage.setItem("token", token);
      const payload = JSON.parse(atob(token.split(".")[1]));
      setUser({ username: payload.sub, roles: payload.roles || [] });
    } catch (err: any) {
      setError(err.response?.data?.detail || "Login failed");
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading, error }}>
      {children}
    </AuthContext.Provider>
  );
};

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
