import React from 'react';
import { Box, Container, Typography, Link } from '@mui/material';

const Footer: React.FC = () => {
  return (
    <Box component="footer" sx={{ bgcolor: 'primary.main', color: 'primary.contrastText', py: 3, mt: 8 }}>
      <Container maxWidth="md">
        <Typography variant="body2" align="center">
          &copy; {new Date().getFullYear()} Example Corp. All rights reserved.
        </Typography>
        <Typography variant="body2" align="center">
          Contact us: <Link href="mailto:contact@example.com" color="inherit">contact@example.com</Link> | Phone: (123) 456-7890
        </Typography>
        <Typography variant="caption" align="center" display="block" sx={{ mt: 1 }}>
          This is a sample application form built to industry standards.
        </Typography>
      </Container>
    </Box>
  );
};

export default Footer;
