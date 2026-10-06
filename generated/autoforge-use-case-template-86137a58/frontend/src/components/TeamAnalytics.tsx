import React, { useEffect, useState } from 'react';
import { Box, Typography, CircularProgress, Alert, Paper } from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

interface TeamAnalyticsData {
  attendance_percentage: number;
  completion_rate: number;
  feedback_trends: number[];
}

const TeamAnalytics = () => {
  const { user } = useAuth();
  const [data, setData] = useState<TeamAnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchAnalytics = async () => {
    if (!user) return;
    try {
      setLoading(true);
      setError('');
      const res = await axios.get('/team/analytics', {
        headers: { Authorization: `Bearer ${user.token}` },
      });
      setData(res.data);
    } catch (e) {
      setError('Failed to load team analytics.');
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    fetchAnalytics();
  }, []);

  if (loading) return <CircularProgress aria-label="Loading team analytics" />;
  if (error) return <Alert severity="error">{error}</Alert>;
  if (!data) return <Typography>No analytics available.</Typography>;

  return (
    <Box>
      <Typography variant="h4" gutterBottom>Team Analytics</Typography>
      <Paper sx={{ p: 2, mb: 2 }} aria-label="Attendance Percentage">
        <Typography variant="h6">Attendance Percentage</Typography>
        <Typography>{data.attendance_percentage.toFixed(1)}%</Typography>
      </Paper>
      <Paper sx={{ p: 2, mb: 2 }} aria-label="Completion Rate">
        <Typography variant="h6">Completion Rate</Typography>
        <Typography>{data.completion_rate.toFixed(1)}%</Typography>
      </Paper>
      <Paper sx={{ p: 2 }} aria-label="Feedback Trends">
        <Typography variant="h6">Feedback Trends</Typography>
        <Typography>Data: {data.feedback_trends.join(', ')}</Typography>
      </Paper>
    </Box>
  );
};

export default TeamAnalytics;
