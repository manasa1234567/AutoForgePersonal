import React from 'react';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';

const Header: React.FC = () => {
  return (
    <AppBar position="static" component="header">
      <Toolbar>
        <Typography variant="h6" component="h1" sx={{fontWeight: 'bold'}}>
          Application Form
        </Typography>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
