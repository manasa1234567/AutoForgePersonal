import React, { useState } from 'react';

const API_BASE = process.env.REACT_APP_API_BASE || '';

interface ApiResponse {
    message: string;
}

function App() {
  const [loading, setLoading] = useState(false);
  const [resultMessage, setResultMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Use a hardcoded Authorization token for demonstration
  // In real app, implement login and token management
  const AUTH_TOKEN = process.env.REACT_APP_AUTH_TOKEN || "valid-token";

  const createHiPage = async () => {
    setLoading(true);
    setResultMessage(null);
    setErrorMessage(null);

    try {
      const response = await fetch(`${API_BASE}/pages/hi`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${AUTH_TOKEN}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data: ApiResponse = await response.json();
        setResultMessage(data.message);
      } else {
        const errorData = await response.json();
        setErrorMessage(errorData.detail ?? 'Unknown error occurred');
      }
    } catch (err) {
      setErrorMessage('Network error or backend unavailable');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container" style={{maxWidth: '500px', margin: '2rem auto', textAlign: 'center', fontFamily: 'Arial, sans-serif'}}>
      <h1>Create 'hi' Page</h1>
      <button
        onClick={createHiPage}
        disabled={loading}
        aria-busy={loading}
        aria-label="Create the 'hi' page"
        style={{
          padding: '10px 20px',
          fontSize: '1rem',
          cursor: loading ? 'not-allowed' : 'pointer',
          opacity: loading ? 0.6 : 1
        }}
      >
        {loading ? 'Creating...' : 'Create Page'}
      </button>
      <div
        role={resultMessage ? 'alert' : undefined}
        aria-live="polite"
        style={{marginTop: '1rem', minHeight: '2rem', color: resultMessage ? 'green' : 'red'}}
      >
        {resultMessage || errorMessage || ''}
      </div>
    </div>
  );
}

export default App;
