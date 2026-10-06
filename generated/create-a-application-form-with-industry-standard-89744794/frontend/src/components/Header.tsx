import React from 'react';
import { AppBar, Toolbar, Typography, Box } from '@mui/material';

const Header: React.FC = () => {
  return (
    <AppBar position="static" component="header">
      <Toolbar>
        {/* Company logo can be replaced or extended here */}
        <Box component="img" src="/logo192.png" alt="Company Logo" sx={{ width: 40, height: 40, mr: 2 }} />
        <Typography variant="h6" component="h1" sx={{ flexGrow: 1 }}>
          Example Corp
        </Typography>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
