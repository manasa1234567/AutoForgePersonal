import React from 'react';
import './Footer.css';

const Footer: React.FC = () => {
  return (
    <footer className="app-footer" role="contentinfo">
      <div className="container">
        <p>Contact us: support@example.com | Phone: +1 555 123 4567</p>
        <p>© 2024 Example Company. All rights reserved.</p>
      </div>
    </footer>
  );
};

export default Footer;
