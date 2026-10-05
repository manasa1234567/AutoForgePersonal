import React from 'react';
import CssBaseline from '@mui/material/CssBaseline';
import Container from '@mui/material/Container';
import Header from './components/Header';
import Footer from './components/Footer';
import ApplicationForm from './components/ApplicationForm';

function App() {
  return (
    <>
      <CssBaseline />
      <Header />
      <Container component="main" maxWidth="md" sx={{ my: 4 }}>
        <ApplicationForm />
      </Container>
      <Footer />
    </>
  );
}

export default App;
