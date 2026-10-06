import React from "react";
import { Container, Typography, Button, Box } from "@mui/material";
import { useAuth } from "../auth/AuthContext";

const LoginPage: React.FC = () => {
  const { login } = useAuth();
  return (
    <Container maxWidth="sm" sx={{ mt: 10, textAlign: "center" }}>
      <Typography variant="h3" gutterBottom>
        Sign in to AutoForge
      </Typography>
      <Typography variant="body1" gutterBottom>
        Please use your corporate Microsoft account to sign in.
      </Typography>
      <Box sx={{ mt: 4 }}>
        <Button variant="contained" onClick={login}>
          Sign In with Microsoft
        </Button>
      </Box>
    </Container>
  );
};

export default LoginPage;
