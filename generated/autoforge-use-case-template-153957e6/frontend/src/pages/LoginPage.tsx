import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import '../styles/login.css';

export default function LoginPage() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user) {
      navigate('/');
    }
  }, [user, navigate]);

  const handleLogin = async () => {
    setLoading(true);
    try {
      await login();
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="login-container">
      <h1>Sign in to Learning Management System</h1>
      <button onClick={handleLogin} disabled={loading} aria-busy={loading} aria-label="Login via Microsoft Entra ID">
        {loading ? 'Signing in...' : 'Sign in with Microsoft'}
      </button>
    </main>
  );
}
