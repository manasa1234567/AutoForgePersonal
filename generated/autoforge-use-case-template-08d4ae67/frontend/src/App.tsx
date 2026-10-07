import React, { useEffect, useState } from 'react';

interface CourseProgress {
  program_id: number;
  status: string;
  completion_percentage: number;
}

function App() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState<CourseProgress[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch('/dashboard/employee', { credentials: 'include' });
        if (!res.ok) {
          throw new Error(`Failed to fetch: ${res.status}`);
        }
        const data = await res.json();
        setProgress(data);
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchData();

    // Poll every 60 seconds to auto-refresh dashboard (per R022)
    const interval = setInterval(fetchData, 60000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div>Loading dashboard...</div>;
  if (error) return <div role="alert">Error loading dashboard: {error}</div>;

  return (
    <main>
      <h1>My Training Programs</h1>
      {progress.length === 0 ? (
        <p>No assigned training programs found.</p>
      ) : (
        <ul>
          {progress.map(prog => (
            <li key={prog.program_id}>
              Program ID: {prog.program_id} - Status: {prog.status} - Completion: {prog.completion_percentage}%
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}

export default App;
