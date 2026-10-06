import React, { useState } from "react";
import { useAuth } from "../hooks/useAuth";
import { Box, Button, TextField, Typography, Alert, CircularProgress } from "@mui/material";

export default function LoginPage() {
  const { login, error, loading } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await login(username, password);
  };

  return (
    <Box sx={{ maxWidth: 320, mx: "auto", mt: 10 }}>
      <Typography variant="h5" gutterBottom>
        Login
      </Typography>
      <form onSubmit={handleSubmit} noValidate>
        <TextField
          label="Username"
          fullWidth
          margin="normal"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
          autoComplete="username"
          autoFocus
        />
        <TextField
          label="Password"
          type="password"
          fullWidth
          margin="normal"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          autoComplete="current-password"
        />
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        <Button type="submit" variant="contained" fullWidth disabled={loading}>
          {loading ? <CircularProgress size={24} /> : "Login"}
        </Button>
      </form>
    </Box>
  );
}
