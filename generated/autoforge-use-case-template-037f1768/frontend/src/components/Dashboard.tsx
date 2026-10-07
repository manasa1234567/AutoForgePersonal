import React, { useEffect, useState } from 'react';
import api from '../api/apiClient';
import { useAuth } from '../auth/AuthContext';
import './Dashboard.css';

interface Program {
  id: number;
  title: string;
  description?: string;
  active: boolean;
  completionStatus?: string;
}

export default function Dashboard() {
  const { user, logout } = useAuth();

  const [programs, setPrograms] = useState<Program[]>([]);
  const [metrics, setMetrics] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchDashboard() {
      setLoading(true);
      setError(null);
      try {
        // Fetch assigned programs
        const resPrograms = await api.get('/employee/programs');
        setPrograms(resPrograms.data);

        // Fetch dashboard metrics
        const resMetrics = await api.get('/dashboard/metrics');
        setMetrics(resMetrics.data);
      } catch (err) {
        setError('Learning service unavailable. Please try again.');
      } finally {
        setLoading(false);
      }
    }

    fetchDashboard();

    // Real-time updates could be integrated here (e.g., WebSocket)
  }, []);

  return (
    <main className="dashboard-container" role="main">
      <header>
        <h1>Learning Dashboard</h1>
        <div>
          <span>Logged in as: {user?.username}</span>{' '}
          <button onClick={logout} aria-label="Logout">Logout</button>
        </div>
      </header>

      {loading ? (
        <p>Loading dashboard...</p>
      ) : error ? (
        <div role="alert" className="error-message">
          {error}{' '}
          <button onClick={() => window.location.reload()} aria-label="Retry loading dashboard">Retry</button>
        </div>
      ) : (
        <>
          <section aria-label="Assigned Training Programs">
            <h2>Your Assigned Training Programs</h2>
            {programs.length === 0 ? (
              <p>No assigned training programs.</p>
            ) : (
              <ul>
                {programs.map(program => (
                  <li key={program.id} tabIndex={0}>
                    <strong>{program.title}</strong> - {program.description || 'No description'}
                    <br />
                    Status: {program.completionStatus || 'In progress'}
                  </li>
                ))}
              </ul>
            )}
          </section>

          <section aria-label="Dashboard Metrics">
            <h2>Dashboard Metrics</h2>
            <div className="metrics-grid">
              <div className="metric" tabIndex={0}>
                <h3>Total Learners</h3>
                <p>{metrics?.total_learners ?? '-'}</p>
              </div>
              <div className="metric" tabIndex={0}>
                <h3>Active Programs</h3>
                <p>{metrics?.active_programs ?? '-'}</p>
              </div>
              <div className="metric" tabIndex={0}>
                <h3>Completion Rate %</h3>
                <p>{metrics?.completion_rate_percent ?? '-'}%</p>
              </div>
              {/* Other widgets such as Upcoming Sessions, Attendance Trend, Feedback Rating, etc. can be added here */}
            </div>
          </section>
        </>
      )}
    </main>
  );
}
