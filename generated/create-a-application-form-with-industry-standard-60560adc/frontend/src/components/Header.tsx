import React from 'react';
import { AppBar, Toolbar, Typography, Box } from '@mui/material';

const Header: React.FC = () => {
  return (
    <AppBar position="static">
      <Toolbar>
        <Box sx={{ flexGrow: 1 }}>
          <Typography variant="h6" component="div" sx={{ fontWeight: 'bold' }}>
            Acme Corporation
          </Typography>
          <Typography variant="subtitle1" component="div" sx={{ fontSize: 13 }}>
            Employment Application Form
          </Typography>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
