import React from 'react';
import { Container, CssBaseline, Box, Typography } from '@mui/material';
import Header from './components/Header';
import Footer from './components/Footer';
import ApplicationForm from './components/ApplicationForm';

function App() {
  return (
    <>
      <CssBaseline />
      <Header />
      <Box sx={{ mt: 8, mb: 4 }}>
        <Container maxWidth="md">
          <Typography component="h1" variant="h4" align="center" gutterBottom>
            Application Form
          </Typography>
          <ApplicationForm />
        </Container>
      </Box>
      <Footer />
    </>
  );
}

export default App;
