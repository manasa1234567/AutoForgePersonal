import React from 'react';
import { Link } from 'react-router-dom';

export default function NotAuthorizedPage() {
  return (
    <main role="alert" className="not-authorized">
      <h1>Access Denied</h1>
      <p>You do not have permission to access this page or perform this action.</p>
      <Link to="/">Return to Dashboard</Link>
    </main>
  );
}
