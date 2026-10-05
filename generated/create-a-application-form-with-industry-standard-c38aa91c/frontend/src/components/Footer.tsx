import React from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';

const Footer: React.FC = () => {
  return (
    <Box component="footer" sx={{bgcolor: 'primary.main', color: 'white', py: 2, mt: 4, textAlign: 'center'}}>
      <Typography variant="body2">
        &copy; {new Date().getFullYear()} Application Form Inc. All rights reserved.
      </Typography>
    </Box>
  );
};

export default Footer;
