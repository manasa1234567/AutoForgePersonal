import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  Box,
  Typography,
  Grid,
  Paper,
  CircularProgress,
  Alert,
  Button,
} from '@mui/material';

const Dashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchMetrics = () => {
    setLoading(true);
    setError(null);
    axios
      .get('/dashboard/metrics')
      .then((res) => {
        setMetrics(res.data);
        setLoading(false);
      })
      .catch(() => {
        setError('Failed to load dashboard metrics. Please try again.');
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  if (loading) return <CircularProgress aria-label="Loading dashboard metrics" />;

  if (error)
    return (
      <Alert severity="error">
        {error}{' '}
        <Button onClick={fetchMetrics} size="small">
          Retry
        </Button>
      </Alert>
    );

  return (
    <Box padding={2} role="main">
      <Typography variant="h4" component="h1" gutterBottom>
        Dashboard
      </Typography>
      <Grid container spacing={2} aria-label="Dashboard widgets">
        <Grid item xs={12} sm={6} md={3}>
          <Paper elevation={3} style={{ padding: '1em' }}>
            <Typography variant="h6">Total Learners</Typography>
            <Typography variant="h4" aria-live="polite">
              {metrics.total_learners}
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper elevation={3} style={{ padding: '1em' }}>
            <Typography variant="h6">Active Programs</Typography>
            <Typography variant="h4" aria-live="polite">
              {metrics.active_programs}
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper elevation={3} style={{ padding: '1em' }}>
            <Typography variant="h6">Completion Rate</Typography>
            <Typography variant="h4" aria-live="polite">
              {(metrics.completion_rate * 100).toFixed(1)}%
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper elevation={3} style={{ padding: '1em' }}>
            <Typography variant="h6">Upcoming Sessions</Typography>
            <Typography variant="h4" aria-live="polite">
              {metrics.upcoming_sessions}
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
