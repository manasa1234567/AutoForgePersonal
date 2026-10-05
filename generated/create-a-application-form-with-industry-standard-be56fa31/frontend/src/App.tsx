import React from 'react';
import { Container } from '@mui/material';
import Header from './components/Header';
import ApplicationForm from './components/ApplicationForm';
import Footer from './components/Footer';

function App() {
  return (
    <>
      <Header />
      <Container maxWidth="md" sx={{ py: 4 }}>
        <ApplicationForm />
      </Container>
      <Footer />
    </>
  );
}

export default App;
