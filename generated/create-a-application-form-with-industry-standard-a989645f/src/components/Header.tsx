import React from 'react';

const Header: React.FC = () => {
  return (
    <header className="app-header" role="banner">
      <div className="header-content">
        <h1 tabIndex={0}>Application Form</h1>
        {/* Placeholder for branding/logo */}
        <div className="branding" aria-label="Company Branding">
          <svg
            width="40"
            height="40"
            viewBox="0 0 64 64"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            aria-hidden="true"
            focusable="false"
          >
            <circle cx="32" cy="32" r="32" fill="#4F46E5" />
            <path
              d="M20 44L32 28L44 44H20Z"
              fill="white"
            />
          </svg>
        </div>
      </div>
    </header>
  );
};

export default Header;
