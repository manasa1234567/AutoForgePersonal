import React from 'react';

export default function Footer() {
  return (
    <footer id="footer" className="bg-white border-t mt-12">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-6 text-center text-gray-500 text-sm">
        <p>© {new Date().getFullYear()} Application Form Inc. All rights reserved.</p>
        <p className="mt-1">Contact us: <a href="mailto:support@applicationform.com" className="text-indigo-600 hover:text-indigo-800">support@applicationform.com</a></p>
      </div>
    </footer>
  );
}
