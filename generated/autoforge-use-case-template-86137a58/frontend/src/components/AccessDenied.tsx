import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const AccessDenied = () => {
  const navigate = useNavigate();
  return (
    <Box sx={{ mt: 10, textAlign: 'center' }}>
      <Typography variant="h3" gutterBottom>Access Denied</Typography>
      <Typography variant="body1" gutterBottom>You do not have permission to access this page.</Typography>
      <Button variant="contained" onClick={() => navigate('/')}>Go to Dashboard</Button>
    </Box>
  );
};

export default AccessDenied;
