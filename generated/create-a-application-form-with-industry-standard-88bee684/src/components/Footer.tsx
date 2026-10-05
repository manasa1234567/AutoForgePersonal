import React from 'react';

const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-100 text-gray-600 text-sm p-4 mt-12 border-t border-gray-300">
      <div className="container mx-auto flex flex-col md:flex-row justify-between items-center">
        <p>&copy; {currentYear} Acme Corp. All rights reserved.</p>
        <p>Contact us: <a href="mailto:support@acmecorp.com" className="text-blue-600 hover:underline">support@acmecorp.com</a></p>
        <p>Page 1</p>
      </div>
    </footer>
  );
};

export default Footer;
