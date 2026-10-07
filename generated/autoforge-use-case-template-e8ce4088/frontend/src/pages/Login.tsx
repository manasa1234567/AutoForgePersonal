import React, { useState } from 'react';
import { Box, Button, TextField, Typography, Alert } from '@mui/material';
import { useAuth } from '../context/AuthContext';

const Login: React.FC = () => {
  const [token, setToken] = useState('');
  const [error, setError] = useState<string | null>(null);
  const { login } = useAuth();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) {
      setError('Please enter a token');
      return;
    }
    login(token);
  };

  return (
    <Box
      maxWidth={400}
      margin="auto"
      mt={10}
      padding={3}
      boxShadow={3}
      component="form"
      onSubmit={handleSubmit}
      aria-label="Login form"
    >
      <Typography variant="h5" mb={2} component="h1">
        Login (Enter Azure AD token)
      </Typography>
      {error && <Alert severity="error">{error}</Alert>}
      <TextField
        label="Access Token"
        variant="outlined"
        fullWidth
        value={token}
        onChange={(e) => setToken(e.target.value)}
        margin="normal"
        aria-required="true"
      />
      <Button type="submit" variant="contained" fullWidth>
        Log In
      </Button>
      <Typography mt={2} variant="body2" color="textSecondary">
        This demo requires a valid Azure AD access token to authenticate.
      </Typography>
    </Box>
  );
};

export default Login;
