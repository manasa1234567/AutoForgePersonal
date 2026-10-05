import React from 'react';
import { Container, CssBaseline, Box, Typography, Paper } from '@mui/material';
import Header from './components/Header';
import Footer from './components/Footer';
import ApplicationForm from './components/ApplicationForm';

const App: React.FC = () => {
  return (
    <>
      <CssBaseline />
      <Header />
      <Box component="main" sx={{ my: 4 }}>
        <Container maxWidth="md">
          <Paper elevation={3} sx={{ p: 4 }}>
            <Typography component="h1" variant="h4" gutterBottom>
              Application Form
            </Typography>
            <ApplicationForm />
          </Paper>
        </Container>
      </Box>
      <Footer />
    </>
  );
};

export default App;
