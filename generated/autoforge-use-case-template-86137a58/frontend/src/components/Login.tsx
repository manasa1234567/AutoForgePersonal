import React, { useState } from 'react';
import { TextField, Button, Typography, Box, Alert } from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

const Login = () => {
  const [tokenInput, setTokenInput] = useState('');
  const [error, setError] = useState('');
  const { login, user } = useAuth();
  const navigate = useNavigate();

  if (user) {
    navigate('/');
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    await login(tokenInput);
    if (!tokenInput) {
      setError('Please enter a token');
    } else {
      const u = await login(tokenInput);
      // login() sets user if token valid
      if (!u) {
        setError('Invalid token');
      }
    }
  };

  return (
    <Box sx={{ maxWidth: 400, mx: 'auto', mt: 10 }}>
      <Typography variant="h4" gutterBottom>Login (Simulated)</Typography>
      <Typography variant="body2" gutterBottom>Select or enter token to login as a role:</Typography>
      <Button sx={{ mr: 1, mb: 1 }} variant="outlined" onClick={() => setTokenInput('employee-token')}>Employee</Button>
      <Button sx={{ mr: 1, mb: 1 }} variant="outlined" onClick={() => setTokenInput('trainer-token')}>Trainer/Mentor</Button>
      <Button sx={{ mr: 1, mb: 1 }} variant="outlined" onClick={() => setTokenInput('manager-token')}>Manager</Button>
      <Button sx={{ mr: 1, mb: 1 }} variant="outlined" onClick={() => setTokenInput('coordinator-token')}>Coordinator</Button>
      <Button sx={{ mr: 1, mb: 1 }} variant="outlined" onClick={() => setTokenInput('admin-token')}>Administrator</Button>
      <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
        <TextField
          label="Token"
          fullWidth
          value={tokenInput}
          onChange={(e) => setTokenInput(e.target.value)}
          margin="normal"
          autoComplete="off"
          autoFocus
          aria-describedby="token-helper-text"
        />
        {error && <Alert severity="error">{error}</Alert>}
        <Button variant="contained" type="submit" sx={{ mt: 2 }} fullWidth>
          Login
        </Button>
      </Box>
      <Typography variant="body2" sx={{ mt: 4 }}>
        Note: Use predefined tokens for demo:
        <ul>
          <li>employee-token</li>
          <li>trainer-token</li>
          <li>manager-token</li>
          <li>coordinator-token</li>
          <li>admin-token</li>
        </ul>
      </Typography>
    </Box>
  );
};

export default Login;
