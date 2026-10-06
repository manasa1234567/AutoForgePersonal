import React, { useEffect, useState } from "react";
import { Paper, Typography } from "@mui/material";
import axios from "axios";

interface Props {
  userId: number;
}

const AttendanceTrendWidget: React.FC<Props> = ({ userId }) => {
  // This is a placeholder static content widget
  // In a real app, render a chart with attendance trend

  const [attendanceRate, setAttendanceRate] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = React.useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    axios
      .get(`/api/user/${userId}/registrations`)
      .then((response) => {
        const regs = response.data as any[];
        if (regs.length === 0) {
          setAttendanceRate(0);
        } else {
          const attendedCount = regs.filter((r) => r.attendance).length;
          setAttendanceRate((attendedCount / regs.length) * 100);
        }
        setLoading(false);
      })
      .catch(() => {
        setError("Failed to load attendance data.");
        setLoading(false);
      });
  }, [userId]);

  return (
    <Paper sx={{ p: 2 }} elevation={3} aria-label="Attendance Trend">
      <Typography variant="h6" gutterBottom>
        Attendance Rate
      </Typography>
      {loading && <Typography>Loading...</Typography>}
      {error && <Typography color="error">{error}</Typography>}
      {!loading && !error && attendanceRate !== null && (
        <Typography variant="h4">{attendanceRate.toFixed(1)}%</Typography>
      )}
    </Paper>
  );
};

export default AttendanceTrendWidget;
