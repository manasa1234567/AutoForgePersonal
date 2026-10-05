import React from 'react';
import { Container, CssBaseline, Box } from '@mui/material';
import Header from './components/Header';
import Footer from './components/Footer';
import ApplicationForm from './components/ApplicationForm';

function App() {
  return (
    <>
      <CssBaseline />
      <Header />
      <Container component="main" maxWidth="md" sx={{ mb: 4, mt: 4 }}>
        <Box sx={{ p: 3, bgcolor: 'background.paper', borderRadius: 1, boxShadow: 1 }}>
          <ApplicationForm />
        </Box>
      </Container>
      <Footer />
    </>
  );
}

export default App;
