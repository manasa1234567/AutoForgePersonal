import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function AccessDenied() {
  const navigate = useNavigate();
  return (
    <main role="main" aria-labelledby="accessDeniedTitle" className="access-denied-container">
      <h1 id="accessDeniedTitle">Access Denied</h1>
      <p>You do not have permission to access this page or perform this action.</p>
      <button onClick={() => navigate('/')} aria-label="Go back to dashboard">Go to Dashboard</button>
    </main>
  );
}
