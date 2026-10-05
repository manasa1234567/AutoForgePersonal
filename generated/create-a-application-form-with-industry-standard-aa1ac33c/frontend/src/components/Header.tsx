import React from 'react';
import './Header.css';

const Header: React.FC = () => {
  return (
    <header className="app-header" role="banner">
      <div className="container">
        <img src="/logo192.png" alt="Company Logo" className="logo" />
        <h1 className="form-title">Application Form</h1>
      </div>
    </header>
  );
};

export default Header;
