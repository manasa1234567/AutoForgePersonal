import React from 'react';
import { CssBaseline, Container, Box } from '@mui/material';
import Header from './components/Header';
import Footer from './components/Footer';
import ApplicationForm from './components/ApplicationForm';

function App() {
  return (
    <>
      <CssBaseline />
      <Header />
      <Container maxWidth="md" component="main" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ bgcolor: 'background.paper', p: 3, borderRadius: 1, boxShadow: 1 }}>
          <ApplicationForm />
        </Box>
      </Container>
      <Footer />
    </>
  );
}

export default App;
