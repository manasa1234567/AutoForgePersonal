import React from 'react';
import { Box, Typography } from '@mui/material';

const Footer = () => {
  return (
    <Box component="footer" sx={{ bgcolor: 'primary.main', color: 'primary.contrastText', py: 2, mt: 'auto' }}>
      <Typography variant="body2" align="center">
        © 2024 Application Portal. All rights reserved.
      </Typography>
    </Box>
  );
};

export default Footer;
