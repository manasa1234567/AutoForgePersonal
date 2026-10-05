import React from 'react';
import { Container, Typography, Link, Box } from '@mui/material';

const Footer: React.FC = () => {
  return (
    <Box component="footer" sx={{ bgcolor: 'primary.main', p: 2, mt: 4, color: 'primary.contrastText' }}>
      <Container maxWidth="md" sx={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap' }}>
        <Typography variant="body2" component="p">
          &copy; {new Date().getFullYear()} ExampleCorp. All rights reserved.
        </Typography>
        <Typography variant="body2" component="p">
          <Link href="mailto:support@examplecorp.com" color="inherit" underline="hover">
            Support
          </Link>{' '}
          |{' '}
          <Link href="/privacy" color="inherit" underline="hover">
            Privacy Policy
          </Link>
        </Typography>
      </Container>
    </Box>
  );
};

export default Footer;
