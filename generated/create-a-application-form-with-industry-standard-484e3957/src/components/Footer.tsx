import React from 'react';
import { Box, Typography, Link } from '@mui/material';

const Footer: React.FC = () => {
  return (
    <Box
      component="footer"
      sx={{
        py: 3,
        px: 2,
        mt: 'auto',
        backgroundColor: (theme) => theme.palette.grey[200],
        textAlign: 'center',
        borderTop: (theme) => `1px solid ${theme.palette.divider}`,
      }}
    >
      <Typography variant="body2" color="text.secondary">
        {'© ' + new Date().getFullYear() + ' Application Form. All rights reserved.'}
      </Typography>
      <Typography variant="body2" color="text.secondary">
        <Link href="mailto:support@example.com" underline="hover">
          Contact Support
        </Link>
      </Typography>
    </Box>
  );
};

export default Footer;
