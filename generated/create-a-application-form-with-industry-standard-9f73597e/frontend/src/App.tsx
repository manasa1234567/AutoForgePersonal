import React from 'react';
import { Container, CssBaseline, Box, Typography, Paper } from '@mui/material';
import ApplicationForm from './ApplicationForm';
import Header from './Header';
import Footer from './Footer';

function App() {
  return (
    <>
      <CssBaseline />
      <Header />
      <Container component="main" maxWidth="sm" sx={{ mt: 4, mb: 4 }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography component="h1" variant="h5" gutterBottom>
            Application Form
          </Typography>
          <ApplicationForm />
        </Paper>
      </Container>
      <Footer />
    </>
  );
}

export default App;
