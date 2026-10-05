import React from 'react';
import ApplicationForm from './components/ApplicationForm';
import Header from './components/Header';
import Footer from './components/Footer';
import './App.css';

function App() {
  return (
    <div className="app-container">
      <Header />
      <main>
        <ApplicationForm />
      </main>
      <Footer />
    </div>
  );
}

export default App;
