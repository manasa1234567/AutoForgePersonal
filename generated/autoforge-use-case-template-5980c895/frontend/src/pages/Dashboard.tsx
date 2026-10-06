import React, { useEffect, useState } from "react";
import axios from "axios";
import { useAuth } from "../context/AuthContext";
import {
  Grid,
  Paper,
  Typography,
  CircularProgress,
  Alert,
  Box,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  Button,
} from "@mui/material";

interface TrainingProgram {
  id: number;
  title: string;
  description?: string;
}

interface AssignedProgram extends TrainingProgram {
  completion_percentage: number;
}

const API_BASE = "/api/v1";

export default function Dashboard() {
  const { token } = useAuth();
  const [programs, setPrograms] = useState<AssignedProgram[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchPrograms() {
      setLoading(true);
      setError(null);
      try {
        const res = await axios.get<AssignedProgram[]>(`${API_BASE}/trainings/programs`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setPrograms(res.data);
      } catch (e: any) {
        setError("Failed to load assigned training programs.");
      } finally {
        setLoading(false);
      }
    }
    if (token) {
      fetchPrograms();
    }
  }, [token]);

  if (loading) {
    return <Box sx={{ display: "flex", justifyContent: "center", mt: 6 }}><CircularProgress /></Box>;
  }

  if (error) {
    return <Alert severity="error" sx={{ mt: 4 }}>{error}</Alert>;
  }

  if (programs.length === 0) {
    return <Typography variant="h6" align="center" sx={{ mt: 4 }}>
      You have no assigned training programs.
    </Typography>;
  }

  return (
    <Box sx={{ p: { xs: 2, md: 4 } }}>
      <Typography variant="h4" gutterBottom>
        Assigned Training Programs
      </Typography>
      <Grid container spacing={2}>
        {programs.map((program) => (
          <Grid key={program.id} item xs={12} md={6} lg={4}>
            <Paper sx={{ p: 2 }} elevation={3} role="region" aria-label={`Training program ${program.title}`}>
              <Typography variant="h6">{program.title}</Typography>
              <Typography variant="body2" paragraph>
                {program.description || "No description provided."}
              </Typography>
              <Typography variant="body1">
                Completion: {program.completion_percentage.toFixed(1)}%
              </Typography>
            </Paper>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
