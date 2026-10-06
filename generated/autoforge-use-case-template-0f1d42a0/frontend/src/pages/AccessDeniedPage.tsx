import React from "react";
import { Container, Typography, Box } from "@mui/material";

const AccessDeniedPage: React.FC = () => {
  return (
    <Container maxWidth="sm" sx={{ mt: 10, textAlign: "center" }}>
      <Typography variant="h4" color="error" gutterBottom>
        Access Denied
      </Typography>
      <Typography variant="body1">
        You do not have permission to access this feature.
      </Typography>
    </Container>
  );
};

export default AccessDeniedPage;
