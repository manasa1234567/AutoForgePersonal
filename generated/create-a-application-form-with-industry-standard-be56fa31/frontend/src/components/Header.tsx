import React from 'react';
import { AppBar, Toolbar, Typography, Container } from '@mui/material';

const Header: React.FC = () => {
  return (
    <AppBar position="static" component="header" elevation={2} sx={{ bgcolor: 'primary.main' }}>
      <Container maxWidth="md">
        <Toolbar disableGutters>
          <Typography variant="h6" component="h1" sx={{ fontWeight: 700 }}>
            Application Form
          </Typography>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Header;
