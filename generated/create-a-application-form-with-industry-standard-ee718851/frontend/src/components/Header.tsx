import React from 'react';
import { AppBar, Toolbar, Typography } from '@mui/material';

const Header: React.FC = () => {
  return (
    <AppBar position="static" component="header">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          ACME Corp Application
        </Typography>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
