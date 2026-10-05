import React from 'react';
import { AppBar, Toolbar, Typography } from '@mui/material';

const Header: React.FC = () => {
  return (
    <AppBar position="static" component="header" color="primary" elevation={4}>
      <Toolbar>
        <Typography variant="h6" component="h1" sx={{ flexGrow: 1 }}>
          Application Form
        </Typography>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
