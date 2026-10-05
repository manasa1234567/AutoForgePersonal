import React from 'react';
import { AppBar, Toolbar, Typography, Container, Box } from '@mui/material';
import { Business } from '@mui/icons-material';

const Header: React.FC = () => {
  return (
    <AppBar position="static" color="primary" component="header">
      <Container maxWidth="md">
        <Toolbar disableGutters>
          <Business sx={{ mr: 1 }} aria-hidden="true" />
          <Typography variant="h6" component="h1" sx={{ flexGrow: 1 }}>
            ExampleCorp
          </Typography>
          <Box sx={{ display: { xs: 'none', sm: 'block' } }}>
            <Typography variant="body2">
              Contact: contact@examplecorp.com | +1 555 123 4567
            </Typography>
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Header;
