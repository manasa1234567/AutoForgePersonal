import React, { useState } from 'react';
import { useAuth } from '../auth/AuthContext';
import './Login.css';

const tokenMap: { [key: string]: string } = {
  employee1: 'employee_token',
  trainer1: 'trainer_token',
  manager1: 'manager_token',
  coordinator1: 'coordinator_token',
  admin1: 'admin_token'
};

export default function Login() {
  const [username, setUsername] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (tokenMap[username]) {
      login(tokenMap[username]).then(() => {
        localStorage.setItem('authToken', tokenMap[username]);
      });
    } else {
      setError('Unknown username for demo, try employee1, trainer1, manager1, coordinator1, or admin1.');
    }
  };

  return (
    <div className="login-container" role="main">
      <h1>Login</h1>
      <form onSubmit={handleSubmit} aria-label="Login form">
        <label htmlFor="username">Username</label>
        <input
          id="username"
          name="username"
          type="text"
          value={username}
          onChange={e => setUsername(e.target.value)}
          aria-required="true"
          aria-describedby="usernameHelp"
          autoComplete="username"
        />
        <div id="usernameHelp" className="sr-only">Enter your demo username</div>
        <button type="submit" aria-label="Submit login">Login</button>
        {error && <div role="alert" className="error-message">{error}</div>}
      </form>
      <p>Demo users: employee1, trainer1, manager1, coordinator1, admin1</p>
    </div>
  );
}
