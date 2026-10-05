import React from 'react';
import './Header.css';

const Header: React.FC = () => {
  return (
    <header className="header">
      <div className="container">
        <h1>Application Form</h1>
        <p>Please fill out the form below completely and accurately.</p>
      </div>
    </header>
  );
};

export default Header;
