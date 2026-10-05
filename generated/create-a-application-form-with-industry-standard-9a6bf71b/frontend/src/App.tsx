import React from 'react';
import { Container, CssBaseline, Typography, Paper } from '@mui/material';
import ApplicationForm from './components/ApplicationForm';
import Header from './components/Header';
import Footer from './components/Footer';

function App() {
  return (
    <>
      <CssBaseline />
      <Header />
      <Container maxWidth="md" component="main" sx={{ mb: 4, mt: 2 }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography component="h1" variant="h4" align="center" gutterBottom>
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
