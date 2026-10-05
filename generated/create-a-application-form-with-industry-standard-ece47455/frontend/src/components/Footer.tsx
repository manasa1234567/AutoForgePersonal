import React from 'react';
import { Box, Typography, Link } from '@mui/material';

/**
 * Footer component with copyright and links.
 */
const Footer: React.FC = () => {
  return (
    <Box component="footer" sx={{ bgcolor: 'primary.dark', color: 'primary.contrastText', py: 2, mt: 4 }}>
      <Typography variant="body2" align="center">
        {'\u00A9 '}2024 Your Company. All rights reserved. |{' '}
        <Link href="/privacy" color="inherit" underline="hover">
          Privacy Policy
        </Link>{' '}
        |{' '}
        <Link href="/terms" color="inherit" underline="hover">
          Terms of Service
        </Link>
      </Typography>
    </Box>
  );
};

export default Footer;
