import React from 'react';
import { AppBar, Toolbar, Typography } from '@mui/material';

/**
 * Header component with application title.
 */
const Header: React.FC = () => {
  return (
    <AppBar position="static" component="header">
      <Toolbar>
        <Typography variant="h6" component="h1" sx={{ flexGrow: 1 }}>
          Application Form
        </Typography>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
