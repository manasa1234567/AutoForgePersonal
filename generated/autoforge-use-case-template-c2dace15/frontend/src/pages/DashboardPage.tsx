import React, { useEffect, useState } from "react";
import axios from "axios";
import { Box, Typography, Grid, Paper, CircularProgress, Alert } from "@mui/material";

interface DashboardData {
  total_learners?: number;
  active_programs?: number;
  completion_rate?: number;
  upcoming_sessions?: any[];
  attendance_trend?: any[];
  feedback_rating?: any[];
  recent_activities?: any[];
  top_performing_learners?: any[];
  notifications?: any[];
  quick_actions?: any[];
  team_analytics?: {
    attendance: number;
    completion_rates: number;
    feedback_trends: any[];
  };
  message?: string;
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchDashboard() {
      try {
        setLoading(true);
        const res = await axios.get("/dashboard");
        setData(res.data);
        setError(null);
      } catch (err: any) {
        setError(err.response?.data?.detail || "Failed to load dashboard");
      } finally {
        setLoading(false);
      }
    }
    fetchDashboard();
  }, []);

  if (loading) return <CircularProgress />;
  if (error) return <Alert severity="error">{error}</Alert>;
  if (!data) return null;

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      {/* Example widget: Basic display for employee or manager */}
      {data.message && <Typography>{data.message}</Typography>}

      {data.total_learners !== undefined && (
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="subtitle1">Total Learners</Typography>
              <Typography variant="h5">{data.total_learners}</Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="subtitle1">Active Programs</Typography>
              <Typography variant="h5">{data.active_programs}</Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="subtitle1">Completion Rate %</Typography>
              <Typography variant="h5">{data.completion_rate?.toFixed(1)}</Typography>
            </Paper>
          </Grid>
        </Grid>
      )}

      {data.team_analytics && (
        <Box mt={4}>
          <Typography variant="h6">Team Analytics</Typography>
          <Typography>Attendance: {data.team_analytics.attendance}%</Typography>
          <Typography>Completion Rates: {data.team_analytics.completion_rates}%</Typography>
          {/* Feedback trends and other analytics can be shown here */}
        </Box>
      )}

      {/* Placeholder for other widgets */}
    </Box>
  );
}
