import React from 'react';
import { CssBaseline, Container, Box, Typography } from '@mui/material';
import Header from './components/Header';
import Footer from './components/Footer';
import ApplicationForm from './components/ApplicationForm';

function App() {
  return (
    <>
      <CssBaseline />
      <Header />
      <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
        <Typography component="h1" variant="h4" align="center" gutterBottom>
          Application Form
        </Typography>
        <Box sx={{ mt: 3 }}>
          <ApplicationForm />
        </Box>
      </Container>
      <Footer />
    </>
  );
}

export default App;
