import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const NotFound = () => {
  const navigate = useNavigate();
  return (
    <Box sx={{ mt: 10, textAlign: 'center' }}>
      <Typography variant="h3" gutterBottom>Page Not Found</Typography>
      <Typography variant="body1" gutterBottom>The page you are looking for does not exist.</Typography>
      <Button variant="contained" onClick={() => navigate('/')}>Go to Dashboard</Button>
    </Box>
  );
};

export default NotFound;
