import React from 'react';
import { Box, Typography, Link } from '@mui/material';

const Footer: React.FC = () => {
  return (
    <Box component="footer" sx={{ bgcolor: 'primary.main', color: 'primary.contrastText', p: 2, textAlign: 'center', mt: 'auto' }}>
      <Typography variant="body2">
        &copy; {new Date().getFullYear()} Acme Corporation. All rights reserved.
      </Typography>
      <Typography variant="caption" sx={{ display: 'block' }}>
        <Link href="#" color="inherit" underline="hover">
          Privacy Policy
        </Link>{' '}
        |{' '}
        <Link href="#" color="inherit" underline="hover">
          Terms of Use
        </Link>
      </Typography>
    </Box>
  );
};

export default Footer;
