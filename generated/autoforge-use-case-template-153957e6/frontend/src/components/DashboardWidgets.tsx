import React from 'react';
import { TrainingProgram, AnalyticsData, SessionAttendance } from '../types/types';
import { useNavigate } from 'react-router-dom';
import '../styles/dashboardWidgets.css';

interface Props {
  userRole: string;
  programs: TrainingProgram[];
  analytics: AnalyticsData | null;
  attendances: SessionAttendance[];
  onRequestFeedback: (programId: string) => void;
}

export default function DashboardWidgets({ userRole, programs, analytics, attendances, onRequestFeedback }: Props) {
  const navigate = useNavigate();

  const totalLearners = analytics?.totalLearners ?? 0;
  const activePrograms = analytics?.activePrograms ?? 0;
  const completionRate = analytics?.completionRate ?? 0;
  const upcomingSessions = analytics?.upcomingSessions ?? [];
  const attendanceTrend = analytics?.attendanceTrend ?? [];
  const feedbackRatings = analytics?.feedbackRatings ?? [];
  const recentActivities = analytics?.recentActivities ?? [];
  const topPerformers = analytics?.topPerformers ?? [];
  const notifications = analytics?.notifications ?? [];

  return (
    <section aria-label="Dashboard widgets" className="dashboard-widgets">
      <div className="widgets-row">
        <article className="widget card" tabIndex={0} aria-label="Total Learners">
          <h2>Total Learners</h2>
          <p>{totalLearners}</p>
        </article>

        <article className="widget card" tabIndex={0} aria-label="Active Programs">
          <h2>Active Programs</h2>
          <p>{activePrograms}</p>
        </article>

        <article className="widget card" tabIndex={0} aria-label="Completion Rate">
          <h2>Completion Rate</h2>
          <p>{completionRate.toFixed(1)}%</p>
        </article>

        <article className="widget card" tabIndex={0} aria-label="Upcoming Sessions">
          <h2>Upcoming Sessions</h2>
          <ul>
            {upcomingSessions.slice(0, 5).map(session => (
              <li key={session.sessionId}>{session.title} - {new Date(session.start).toLocaleDateString()}</li>
            ))}
            {upcomingSessions.length === 0 && <li>No upcoming sessions</li>}
          </ul>
        </article>
      </div>

      {(userRole === 'Manager' || userRole === 'Administrator') && (
        <div className="widgets-row">
          <article className="widget card" tabIndex={0} aria-label="Attendance Trend">
            <h2>Attendance Trend</h2>
            <Chart data={attendanceTrend} />
          </article>

          <article className="widget card" tabIndex={0} aria-label="Feedback Ratings">
            <h2>Feedback Ratings</h2>
            <Chart data={feedbackRatings} />
          </article>

          <article className="widget card" tabIndex={0} aria-label="Recent Activities">
            <h2>Recent Activities</h2>
            <ul>
              {recentActivities.map((activity, i) => (
                <li key={i}>{activity}</li>
              ))}
              {recentActivities.length === 0 && <li>No recent activities</li>}
            </ul>
          </article>

          <article className="widget card" tabIndex={0} aria-label="Top Performing Learners">
            <h2>Top Performing Learners</h2>
            <ul>
              {topPerformers.map(learner => (
                <li key={learner.id}>{learner.name} ({learner.completionRate.toFixed(1)}%)</li>
              ))}
              {topPerformers.length === 0 && <li>No data available</li>}
            </ul>
          </article>

          <article className="widget card" tabIndex={0} aria-label="Notifications">
            <h2>Notifications</h2>
            <ul>
              {notifications.map((note, i) => (
                <li key={i}>{note}</li>
              ))}
              {notifications.length === 0 && <li>No notifications</li>}
            </ul>
          </article>

          <article className="widget card" tabIndex={0} aria-label="Quick Actions">
            <h2>Quick Actions</h2>
            {userRole === 'Administrator' && <button onClick={() => navigate('/admin')}>Manage Users/Programs</button>}
            {userRole === 'Learning Program Coordinator' && <button onClick={() => navigate('/programs/new')}>Create New Program</button>}
          </article>
        </div>
      )}

      {(userRole === 'Employee') && (
        <div className="widgets-row">
          <article className="widget card" tabIndex={0} aria-label="Assigned Programs">
            <h2>Assigned Programs</h2>
            <ul>
              {programs.length > 0 ? programs.map(p => (
                <li key={p.id}>
                  {p.title} - {p.completionPercentage.toFixed(1)}% complete
                  <button onClick={() => onRequestFeedback(p.id)}>Submit Feedback</button>
                </li>
              )) : <li>No assigned programs</li>}
            </ul>
          </article>
        </div>
      )}
    </section>
  );
}

function Chart({ data }: { data: { label: string; value: number }[] }) {
  if (!data.length) return <p>No Data</p>;
  return (
    <ul>
      {data.map(({ label, value }) => (
        <li key={label}>{label}: {value}</li>
      ))}
    </ul>
  );
}
