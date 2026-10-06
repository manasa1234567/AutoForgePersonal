import React, { useEffect, useState } from "react";
import axios from "axios";
import {
  Typography,
  Container,
  Grid,
  Paper,
  Box,
  Button,
  Alert,
  Snackbar,
} from "@mui/material";
import { useAuth } from "../auth/AuthContext";
import AssignedProgramsWidget from "../widgets/AssignedProgramsWidget";
import CompletionRateWidget from "../widgets/CompletionRateWidget";
import FeedbackWidget from "../widgets/FeedbackWidget";
import AttendanceTrendWidget from "../widgets/AttendanceTrendWidget";

const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [programs, setPrograms] = useState<any[]>([]);
  const [refreshCounter, setRefreshCounter] = useState(0);

  const fetchPrograms = async () => {
    try {
      const response = await axios.get(`/api/user/${user?.id}/assigned-programs`);
      setPrograms(response.data ?? []);
    } catch (err) {
      setError("Learning services are currently unavailable. Please try again.");
    }
  };

  useEffect(() => {
    if (user) fetchPrograms();
  }, [user, refreshCounter]);

  const handleRefresh = () => {
    setRefreshCounter((prev) => prev + 1);
  };

  if (!user) return null;

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Welcome, {user.name}
      </Typography>

      {error && (
        <Snackbar open onClose={() => setError(null)} autoHideDuration={4000}>
          <Alert severity="error" onClose={() => setError(null)}>
            {error}
          </Alert>
        </Snackbar>
      )}

      <Button variant="outlined" onClick={handleRefresh} sx={{ mb: 2 }}>
        Refresh Dashboard
      </Button>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6} lg={4}>
          <AssignedProgramsWidget programs={programs} />
        </Grid>

        <Grid item xs={12} md={6} lg={4}>
          <CompletionRateWidget userId={user.id} />
        </Grid>

        <Grid item xs={12} md={6} lg={4}>
          <AttendanceTrendWidget userId={user.id} />
        </Grid>

        <Grid item xs={12} md={6} lg={4}>
          <FeedbackWidget userId={user.id} />
        </Grid>

        {/* Additional widgets per requirements can be added here */}
      </Grid>
    </Container>
  );
};

export default DashboardPage;
