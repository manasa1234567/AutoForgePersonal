import React from 'react';
import Header from './components/Header';
import Footer from './components/Footer';
import ApplicationForm from './components/ApplicationForm';
import './App.css';

function App() {
  return (
    <div className="app-container">
      <Header />
      <main className="main-content" role="main">
        <ApplicationForm />
      </main>
      <Footer />
    </div>
  );
}

export default App;
