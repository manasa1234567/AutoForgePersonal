import React from 'react';
import { Box, Typography } from '@mui/material';

const NotFound: React.FC = () => {
  return (
    <Box textAlign="center" mt={10}>
      <Typography variant="h3" component="h1">
        404 - Page Not Found
      </Typography>
      <Typography variant="body1" mt={2}>
        The page you are looking for does not exist.
      </Typography>
    </Box>
  );
};

export default NotFound;
