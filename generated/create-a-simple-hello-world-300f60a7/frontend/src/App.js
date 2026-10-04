import React, { useEffect, useState } from 'react';

function App() {
  const [message, setMessage] = useState('Loading...');
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('/hello')
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        setMessage(data.message);
      })
      .catch(e => {
        setError('Failed to fetch Hello World message.');
      });
  }, []);

  if (error) {
    return <div role="alert" style={{ color: 'red' }}>{error}</div>;
  }

  return (
    <main aria-live="polite" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', fontSize: '2rem' }}>
      {message}
    </main>
  );
}

export default App;
