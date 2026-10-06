import React from "react";
import { Box, Typography } from "@mui/material";

export default function AccessDenied() {
  return (
    <Box sx={{ mt: 8, textAlign: "center" }}>
      <Typography variant="h3" color="error" gutterBottom>
        Access Denied
      </Typography>
      <Typography variant="body1">
        You do not have permission to access this page.
      </Typography>
    </Box>
  );
}
