import React, { useState } from 'react';

export default function App() {
  const [message, setMessage] = useState<string | null>(null);

  function handleClick() {
    // When user clicks, set the message exactly
    setMessage('Hello World');
  }

  return (
    <main style={{
      fontFamily: 'Arial, sans-serif',
      padding: '2rem',
      maxWidth: 400,
      margin: 'auto',
      textAlign: 'center',
    }}>
      <h1>Hello World App</h1>
      <button
        onClick={handleClick}
        aria-label="Generate Hello World"
        style={{
          cursor: 'pointer',
          padding: '0.5rem 1rem',
          fontSize: '1rem',
          borderRadius: 4,
          border: '1px solid #007bff',
          backgroundColor: '#007bff',
          color: 'white',
          transition: 'background-color 0.3s',
        }}
        onMouseOver={e => (e.currentTarget.style.backgroundColor = '#0056b3')}
        onMouseOut={e => (e.currentTarget.style.backgroundColor = '#007bff')}
      >
        Show Message
      </button>
      {message && (
        <p
          role="alert"
          style={{
            marginTop: '1.5rem',
            fontSize: '1.25rem',
            fontWeight: 'bold',
          }}
        >
          {message}
        </p>
      )}
    </main>
  );
}
