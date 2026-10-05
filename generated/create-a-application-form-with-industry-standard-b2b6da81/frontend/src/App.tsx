import React from 'react';
import ApplicationForm from './components/ApplicationForm';
import Header from './components/Header';
import Footer from './components/Footer';

function App() {
  return (
    <div className="min-h-screen flex flex-col text-gray-800 bg-gray-50">
      <Header />
      <main className="flex-grow container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <ApplicationForm />
      </main>
      <Footer />
    </div>
  );
}

export default App;
