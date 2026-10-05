import React from 'react';
import logo from '../assets/logo.svg';

const Header: React.FC = () => {
  return (
    <header className="bg-blue-800 text-white p-4 shadow-md">
      <div className="container mx-auto flex items-center">
        <img src={logo} alt="Company Logo" className="h-10 w-10 mr-3" />
        <h1 className="text-xl font-semibold">Acme Corp Application Form</h1>
      </div>
    </header>
  );
};

export default Header;
