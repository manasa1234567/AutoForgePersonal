import React from 'react';

const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="app-footer" role="contentinfo">
      <div className="footer-content">
        <p>Contact us: <a href="mailto:support@example.com">support@example.com</a> | Phone: <a href="tel:+1234567890">+1 234 567 890</a></p>
        <p>© {currentYear} Example Corp. All rights reserved.</p>
        <p className="disclaimer">
          This form and its contents are confidential. Please do not share sensitive information unnecessarily.
        </p>
      </div>
    </footer>
  );
};

export default Footer;
