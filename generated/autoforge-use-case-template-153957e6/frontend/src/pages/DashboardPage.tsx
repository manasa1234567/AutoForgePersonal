import React, { useEffect, useState, useCallback } from 'react';
import { useAuth } from '../auth/AuthContext';
import DashboardWidgets from '../components/DashboardWidgets';
import FeedbackForm from '../components/FeedbackForm';
import AttendanceList from '../components/AttendanceList';
import { FeedbackSubmission, TrainingProgram, SessionAttendance, AnalyticsData } from '../types/types';
import '../styles/dashboard.css';

export default function DashboardPage() {
  const { user } = useAuth();
  const [ programs, setPrograms ] = useState<TrainingProgram[]>([]);
  const [ analytics, setAnalytics ] = useState<AnalyticsData | null>(null);
  const [ showFeedbackForProgramId, setShowFeedbackForProgramId ] = useState<string | null>(null);
  const [ attendances, setAttendances ] = useState<SessionAttendance[]>([]);
  const [ loading, setLoading ] = useState(true);
  const [ error, setError ] = useState<string | null>(null);

  const fetchUserDashboard = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      // Using mock fetch from /api/dashboard
      const response = await fetch('/api/dashboard');
      if(!response.ok) {
        throw new Error('Failed to load dashboard data');
      }
      const data = await response.json();

      setPrograms(data.programs);
      setAnalytics(data.analytics);
      setAttendances(data.attendances);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUserDashboard();

    const eventSource = new EventSource('/api/dashboard/updates');
    eventSource.onmessage = (event) => {
      fetchUserDashboard();
    };
    eventSource.onerror = () => {
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [fetchUserDashboard]);

  const onFeedbackSubmitted = () => {
    setShowFeedbackForProgramId(null);
    fetchUserDashboard();
  };

  // Depending on user role, render different dashboard segments
  if (loading) {
    return <main aria-busy="true"><p>Loading dashboard...</p></main>;
  }
  if (error) {
    return <main role="alert"><p>Error: {error}</p><button onClick={fetchUserDashboard}>Retry</button></main>;
  }

  return (
    <main className="dashboard-container">
      <header>
        <h1>Welcome, {user?.name}</h1>
        <p>Role: {user?.role}</p>
      </header>
      <DashboardWidgets
        userRole={user?.role || ''}
        programs={programs}
        analytics={analytics}
        attendances={attendances}
        onRequestFeedback={(programId) => setShowFeedbackForProgramId(programId)}
      />

      {showFeedbackForProgramId && (
        <FeedbackForm
          programId={showFeedbackForProgramId}
          onClose={() => setShowFeedbackForProgramId(null)}
          onSubmitted={onFeedbackSubmitted}
        />
      )}

      {(user?.role === 'Trainer' || user?.role === 'Mentor') && (
        <AttendanceList
          programs={programs}
          onAttendancesUpdated={fetchUserDashboard}
        />
      )}
    </main>
  );
}
