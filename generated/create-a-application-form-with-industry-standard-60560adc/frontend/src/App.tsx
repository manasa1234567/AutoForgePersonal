import React from 'react';
import { CssBaseline, Container, Box } from '@mui/material';
import ApplicationForm from './components/ApplicationForm';
import Header from './components/Header';
import Footer from './components/Footer';

const App: React.FC = () => {
  return (
    <>
      <CssBaseline />
      <Header />
      <Container maxWidth="md" sx={{ mt: 4, mb: 4, minHeight: '80vh' }}>
        <Box sx={{ boxShadow: 3, p: 4, borderRadius: 2, backgroundColor: 'background.paper' }}>
          <ApplicationForm />
        </Box>
      </Container>
      <Footer />
    </>
  );
};

export default App;
