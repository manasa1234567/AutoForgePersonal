import React from 'react';
import Header from './components/Header';
import Footer from './components/Footer';
import ApplicationForm from './components/ApplicationForm';

function App() {
  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <Header />
      <main className="flex-grow py-8 px-4">
        <ApplicationForm />
      </main>
      <Footer />
    </div>
  );
}

export default App;
