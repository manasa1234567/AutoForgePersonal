import React, { useEffect, useState } from "react";
import {
  Container,
  Typography,
  Box,
  CircularProgress,
  Alert,
  Grid,
  Paper,
  Badge,
  IconButton,
  Snackbar,
  Button
} from "@mui/material";
import NotificationsIcon from "@mui/icons-material/Notifications";
import axios from "axios";

interface Session {
  id: number;
  title: string;
  scheduled_start: string;
}

interface DashboardData {
  total_learners: number;
  active_programs: number;
  completion_rate_percent: number;
  upcoming_sessions: Session[];
  notifications: string[];
}

const App: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [notifOpen, setNotifOpen] = useState(false);

  useEffect(() => {
    const fetchDashboard = async () => {
      setLoading(true);
      setError("");
      try {
        // For demo, token is hardcoded; replace with actual auth tokens
        const token = "fake-supertoken-for-employee";
        const response = await axios.get(`/dashboard/widgets`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setDashboardData(response.data);
      } catch (err) {
        setError("Failed to load dashboard. Please try again.");
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, []);

  if (loading) {
    return <Container sx={{ mt: 4 }}><CircularProgress /> Loading dashboard...</Container>;
  }

  if (error) {
    return <Container sx={{ mt: 4 }}><Alert severity="error">{error}</Alert></Container>;
  }

  if (!dashboardData) return null;

  return (
    <Container sx={{ mt: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Learning Dashboard
      </Typography>
      <Grid container spacing={2}>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle1">Total Learners</Typography>
            <Typography variant="h5">{dashboardData.total_learners}</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle1">Active Programs</Typography>
            <Typography variant="h5">{dashboardData.active_programs}</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle1">Completion Rate %</Typography>
            <Typography variant="h5">{dashboardData.completion_rate_percent.toFixed(1)}%</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2 }}>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Typography variant="subtitle1">Notifications</Typography>
              <IconButton color="primary" onClick={() => setNotifOpen(true)} aria-label="Open notifications">
                <Badge badgeContent={dashboardData.notifications.length} color="error">
                  <NotificationsIcon />
                </Badge>
              </IconButton>
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle1">Upcoming Sessions</Typography>
            <ul>
              {dashboardData.upcoming_sessions.map((session) => (
                <li key={session.id}>
                  {session.title} - {new Date(session.scheduled_start).toLocaleString()}
                </li>
              ))}
              {dashboardData.upcoming_sessions.length === 0 && <li>No upcoming sessions</li>}
            </ul>
          </Paper>
        </Grid>
      </Grid>

      <Snackbar
        open={notifOpen}
        onClose={() => setNotifOpen(false)}
        message={dashboardData.notifications.join(", ")}
        action={<Button color="inherit" size="small" onClick={() => setNotifOpen(false)}>Close</Button>}
      />
    </Container>
  );
};

export default App;
