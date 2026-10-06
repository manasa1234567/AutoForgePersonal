import React, { useEffect, useState } from "react";
import { Paper, Typography, CircularProgress } from "@mui/material";
import axios from "axios";

interface Props {
  userId: number;
}

const CompletionRateWidget: React.FC<Props> = ({ userId }) => {
  const [completionRate, setCompletionRate] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    // Dummy API call, replace with real
    axios
      .get(`/api/user/${userId}/registrations`)
      .then((response) => {
        const regs = response.data as any[];
        if (regs.length === 0) {
          setCompletionRate(0);
        } else {
          const completedCount = regs.filter((r) => r.completed).length;
          setCompletionRate((completedCount / regs.length) * 100);
        }
        setLoading(false);
      })
      .catch(() => {
        setError("Failed to load completion rate.");
        setLoading(false);
      });
  }, [userId]);

  return (
    <Paper sx={{ p: 2 }} elevation={3} aria-label="Training Completion Rate">
      <Typography variant="h6" gutterBottom>
        Training Completion Rate
      </Typography>
      {loading && <CircularProgress size={30} />}
      {error && <Typography color="error">{error}</Typography>}
      {!loading && !error && (
        <Typography variant="h4">
          {completionRate?.toFixed(1) ?? "0"}%
        </Typography>
      )}
    </Paper>
  );
};

export default CompletionRateWidget;
