import React from "react";
import { Box, Typography, Button } from "@mui/material";
import { useNavigate } from "react-router-dom";

export default function AccessDeniedPage() {
  const navigate = useNavigate();

  return (
    <Box sx={{ textAlign: "center", mt: 8 }}>
      <Typography variant="h3" gutterBottom>
        Access Denied
      </Typography>
      <Typography variant="body1" sx={{ mb: 3 }}>
        You do not have permission to view this page.
      </Typography>
      <Button variant="contained" onClick={() => navigate(-1)}>
        Go Back
      </Button>
    </Box>
  );
}
