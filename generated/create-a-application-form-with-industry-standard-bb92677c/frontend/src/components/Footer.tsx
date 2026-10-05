import React from 'react';
import { Box, Typography, Link, Container } from '@mui/material';

export default function Footer() {
  return (
    <Box component="footer" sx={{ py: 3, mt: 'auto', backgroundColor: (theme) => theme.palette.grey[200] }}>
      <Container maxWidth="md">
        <Typography variant="body2" color="text.secondary" align="center">
          {'© ' + new Date().getFullYear() + ' Company Name. All rights reserved.'}
        </Typography>
        <Typography variant="caption" color="text.secondary" align="center">
          <Link href="/privacy" underline="hover">Privacy Policy</Link>{' | '}
          <Link href="/terms" underline="hover">Terms of Service</Link>
        </Typography>
      </Container>
    </Box>
  );
}
