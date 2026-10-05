import React from 'react';

export default function Header() {
  return (
    <header className="bg-white shadow">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-indigo-600">Application Form</h1>
        <nav aria-label="Primary navigation">
          <ul className="flex space-x-4">
            <li><a href="#form" className="text-indigo-600 hover:text-indigo-800 font-medium">Form</a></li>
            <li><a href="#footer" className="text-gray-600 hover:text-indigo-600">Contact</a></li>
          </ul>
        </nav>
      </div>
    </header>
  );
}
