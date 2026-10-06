import React, { createContext, useContext, useState, useEffect } from "react";
import axios from "axios";

export interface User {
  id: number;
  username: string;
  full_name: string;
  email: string;
  role: string;
  is_active: boolean;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const API_BASE = "/api/v1";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const tokenStored = localStorage.getItem("token");
    if (tokenStored) {
      setToken(tokenStored);
      fetchCurrentUser(tokenStored);
    }
  }, []);

  async function fetchCurrentUser(tokenStr: string) {
    try {
      const res = await axios.get<User>(`${API_BASE}/users/me`, {
        headers: { Authorization: `Bearer ${tokenStr}` },
      });
      setUser(res.data);
    } catch (e) {
      logout();
    }
  }

  async function login(username: string, password: string) {
    const res = await axios.post(`${API_BASE}/auth/login`, new URLSearchParams({ username, password }), {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
    const accessToken = res.data.access_token;
    localStorage.setItem("token", accessToken);
    setToken(accessToken);
    await fetchCurrentUser(accessToken);
  }

  function logout() {
    setUser(null);
    setToken(null);
    localStorage.removeItem("token");
  }

  return <AuthContext.Provider value={{ user, token, login, logout }}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
