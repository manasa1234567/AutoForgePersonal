import React, { useState } from 'react';

function App() {
  const [helloMessage, setHelloMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleClick = async () => {
    setLoading(true);
    setError(null);
    setHelloMessage(null);
    try {
      const response = await fetch('/hello');
      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }
      const data = await response.json();
      if (typeof data.message === 'string') {
        setHelloMessage(data.message);
      } else {
        setError('Unexpected response from server');
      }
    } catch (e) {
      setError('Failed to fetch hello message');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main style={{
      maxWidth: 320,
      margin: '2rem auto',
      fontFamily: 'Arial, sans-serif',
      textAlign: 'center',
      padding: '1rem',
      border: '1px solid #ddd',
      borderRadius: 8,
      boxShadow: '0 2px 6px rgba(0,0,0,0.1)'
    }}>
      <h1>Hello World App</h1>
      <button
        onClick={handleClick}
        disabled={loading}
        style={{
          padding: '0.5rem 1rem',
          fontSize: '1rem',
          cursor: loading ? 'not-allowed' : 'pointer',
          borderRadius: 4,
          border: '1px solid #007bff',
          backgroundColor: '#007bff',
          color: 'white'
        }}
        aria-disabled={loading}
      >
        {loading ? 'Loading...' : 'Show Hello World'}
      </button>

      {helloMessage && (
        <p
          role="status"
          aria-live="polite"
          style={{ marginTop: '1rem', fontWeight: 'bold', fontSize: '1.25rem' }}
          data-testid="hello-message"
        >
          {helloMessage}
        </p>
      )}

      {error && (
        <p role="alert" style={{ color: 'red', marginTop: '1rem' }}>
          {error}
        </p>
      )}
    </main>
  );
}

export default App;
