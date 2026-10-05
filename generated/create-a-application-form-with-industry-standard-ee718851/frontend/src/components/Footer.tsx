import React from 'react';
import { Box, Typography, Link } from '@mui/material';

const Footer: React.FC = () => {
  return (
    <Box component="footer" sx={{ bgcolor: 'background.paper', py: 3, mt: 6, textAlign: 'center' }}>
      <Typography variant="body2" color="text.secondary">
        © {new Date().getFullYear()} ACME Corp. All rights reserved. | 
        <Link href="/privacy" underline="hover">Privacy Policy</Link>
      </Typography>
    </Box>
  );
};

export default Footer;
