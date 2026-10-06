import React, { useEffect, useState } from 'react';
import { Box, Typography, Grid, Paper, CircularProgress, Alert, Button } from '@mui/material';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

interface DashboardData {
  total_learners: number;
  active_programs: number;
  completion_rate_percent: number;
  upcoming_sessions: string[];
  attendance_trend_chart_data: number[];
  feedback_rating_chart_data: number[];
  recent_activities: string[];
  top_performing_learners: string[];
  notifications: string[];
  quick_actions: string[];
}

const Dashboard = () => {
  const { user, logout } = useAuth();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchData = async () => {
    try {
      setLoading(true);
      setError('');
      const res = await axios.get('/dashboard', {
        headers: { Authorization: `Bearer ${user?.token}` },
      });
      setData(res.data);
    } catch (e) {
      setError('Failed to load dashboard data. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) return <CircularProgress aria-label="Loading dashboard data" />;
  if (error) return <Alert severity="error">{error} <Button onClick={fetchData}>Retry</Button></Alert>;

  if (!data) return <Typography>No data available.</Typography>;

  return (
    <Box>
      <Typography variant="h4" gutterBottom>Dashboard</Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2 }} aria-label="Total Learners">
            <Typography variant="h6">Total Learners</Typography>
            <Typography variant="h5">{data.total_learners}</Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2 }} aria-label="Active Programs">
            <Typography variant="h6">Active Programs</Typography>
            <Typography variant="h5">{data.active_programs}</Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2 }} aria-label="Completion Rate">
            <Typography variant="h6">Completion Rate %</Typography>
            <Typography variant="h5">{data.completion_rate_percent.toFixed(1)}%</Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2 }} aria-label="Upcoming Sessions">
            <Typography variant="h6">Upcoming Sessions</Typography>
            {data.upcoming_sessions.length === 0 ? (
              <Typography>No upcoming sessions</Typography>
            ) : (
              <ul>
                {data.upcoming_sessions.map((session, idx) => (
                  <li key={idx}>{session}</li>
                ))}
              </ul>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }} aria-label="Attendance Trend Chart">
            <Typography variant="h6">Attendance Trend</Typography>
            {/* Placeholder chart area, replace with chart library if wanted */}
            <Typography>Data: {data.attendance_trend_chart_data.join(', ')}</Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }} aria-label="Feedback Rating Chart">
            <Typography variant="h6">Feedback Rating</Typography>
            <Typography>Data: {data.feedback_rating_chart_data.join(', ')}</Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }} aria-label="Recent Activities">
            <Typography variant="h6">Recent Activities</Typography>
            {data.recent_activities.length === 0 ? (
              <Typography>No recent activities</Typography>
            ) : (
              <ul>
                {data.recent_activities.map((activity, idx) => (
                  <li key={idx}>{activity}</li>
                ))}
              </ul>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }} aria-label="Top Performing Learners">
            <Typography variant="h6">Top Performing Learners</Typography>
            {data.top_performing_learners.length === 0 ? (
              <Typography>No top learners data</Typography>
            ) : (
              <ul>
                {data.top_performing_learners.map((learner, idx) => (
                  <li key={idx}>{learner}</li>
                ))}
              </ul>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }} aria-label="Notifications">
            <Typography variant="h6">Notifications</Typography>
            {data.notifications.length === 0 ? (
              <Typography>No notifications</Typography>
            ) : (
              <ul>
                {data.notifications.map((note, idx) => (
                  <li key={idx}>{note}</li>
                ))}
              </ul>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 2 }} aria-label="Quick Actions">
            <Typography variant="h6">Quick Actions</Typography>
            {data.quick_actions.length === 0 ? (
              <Typography>No quick actions available</Typography>
            ) : (
              <ul>
                {data.quick_actions.map((action, idx) => (
                  <li key={idx}>{action}</li>
                ))}
              </ul>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Button variant="outlined" onClick={logout}>Logout</Button>
        </Grid>

      </Grid>
    </Box>
  );
};

export default Dashboard;
