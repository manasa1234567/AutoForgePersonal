import React from 'react';
import { Box, Typography, Container, Link } from '@mui/material';

const Footer: React.FC = () => {
  return (
    <Box component="footer" sx={{ bgcolor: 'grey.200', py: 3, mt: 6 }}>
      <Container maxWidth="md">
        <Typography variant="body2" color="text.secondary" align="center">
          © {new Date().getFullYear()} Example Company. All rights reserved.
        </Typography>
        <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 1 }}>
          <Link href="#" color="inherit" underline="hover">
            Privacy Policy
          </Link>{' '}|{' '}
          <Link href="#" color="inherit" underline="hover">
            Terms of Service
          </Link>
        </Typography>
      </Container>
    </Box>
  );
};

export default Footer;
