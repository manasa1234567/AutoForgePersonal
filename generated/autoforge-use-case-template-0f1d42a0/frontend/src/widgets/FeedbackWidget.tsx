import React, { useEffect, useState } from "react";
import {
  Paper,
  Typography,
  TextField,
  Button,
  Box,
  Alert,
  Snackbar,
} from "@mui/material";
import axios from "axios";

interface Props {
  userId: number;
}

const FeedbackWidget: React.FC<Props> = ({ userId }) => {
  const [registrationId, setRegistrationId] = useState<number | null>(null);
  const [rating, setRating] = useState<number | ' '>(5);
  const [comments, setComments] = useState("");
  const [feedbacks, setFeedbacks] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  useEffect(() => {
    // Load user's registrations for feedback (simplified: only registrations that are completed and feedback not yet submitted)
    axios.get(`/api/user/${userId}/registrations`).then((res) => {
      const regs = res.data as any[];
      const pending = regs.find((r) => r.completed && !r.feedback_submitted);
      if (pending) setRegistrationId(pending.id);
    }).catch(() => {
      setError("Failed to load registrations.");
    });

    // Load submitted feedbacks
    axios.get(`/api/feedbacks/user/${userId}`).then((res) => {
      setFeedbacks(res.data);
    }).catch(() => {
      // Ignore error here
    });
  }, [userId]);

  const handleSubmit = () => {
    if (!registrationId) {
      setError("No eligible session for feedback.");
      return;
    }
    if (!rating || rating < 1 || rating > 5) {
      setError("Please provide a valid rating between 1 and 5.");
      return;
    }

    axios.post("/api/feedback", { registration_id: registrationId, rating, comments })
      .then(() => {
        setSuccessMsg("Feedback submitted successfully.");
        setRating(5);
        setComments("");
      })
      .catch((err) => {
        setError(err.response?.data?.detail || "Failed to submit feedback.");
      });
  };

  return (
    <Paper sx={{ p: 2 }} elevation={3} aria-label="Feedback Submission">
      <Typography variant="h6" gutterBottom>
        Submit Feedback
      </Typography>

      {error && (
        <Snackbar open autoHideDuration={4000} onClose={() => setError(null)}>
          <Alert severity="error" onClose={() => setError(null)}>
            {error}
          </Alert>
        </Snackbar>
      )}

      {successMsg && (
        <Snackbar open autoHideDuration={4000} onClose={() => setSuccessMsg(null)}>
          <Alert severity="success" onClose={() => setSuccessMsg(null)}>
            {successMsg}
          </Alert>
        </Snackbar>
      )}

      {!registrationId ? (
        <Typography>No sessions available for feedback.</Typography>
      ) : (
        <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
          <TextField
            label="Rating (1-5)"
            type="number"
            inputProps={{ min: 1, max: 5 }}
            value={rating}
            onChange={(e) => {
              const v = e.target.value;
              setRating(v === "" ? " " : Math.min(5, Math.max(1, Number(v))));
            }}
            required
            aria-required="true"
          />
          <TextField
            label="Comments"
            multiline
            rows={3}
            value={comments}
            onChange={(e) => setComments(e.target.value)}
          />

          <Button variant="contained" onClick={handleSubmit} aria-label="Submit Feedback">
            Submit Feedback
          </Button>
        </Box>
      )}
    </Paper>
  );
};

export default FeedbackWidget;
