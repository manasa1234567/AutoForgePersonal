import React, { useState } from 'react';
import { Box, Typography, TextField, Button, Alert } from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

const FeedbackForm = () => {
  const { user } = useAuth();
  const [sessionId, setSessionId] = useState('');
  const [rating, setRating] = useState<number | ''>('');
  const [comments, setComments] = useState('');
  const [error, setError] = useState<Record<string, string>>({});
  const [submitError, setSubmitError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};
    if (!sessionId.trim()) {
      newErrors.sessionId = 'Session ID is required';
    }
    if (rating === '' || rating < 1 || rating > 5) {
      newErrors.rating = 'Rating must be between 1 and 5';
    }
    if (comments.length > 1000) {
      newErrors.comments = 'Comments must be 1000 characters or fewer';
    }
    setError(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSuccess(false);
    setSubmitError('');
    if (!validate()) {
      return;
    }

    try {
      setLoading(true);
      await axios.post(
        '/feedback',
        { session_id: sessionId, rating, comments: comments || undefined },
        { headers: { Authorization: `Bearer ${user?.token}` } }
      );
      setSuccess(true);
      setSessionId('');
      setRating('');
      setComments('');
    } catch (e) {
      setSubmitError('Failed to submit feedback. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ maxWidth: 600 }}>
      <Typography variant="h4" gutterBottom>Submit Feedback</Typography>
      {success && <Alert severity="success">Feedback submitted successfully.</Alert>}
      {submitError && <Alert severity="error">{submitError}</Alert>}
      <Box component="form" noValidate onSubmit={handleSubmit}>
        <TextField
          label="Session ID"
          fullWidth
          margin="normal"
          value={sessionId}
          onChange={(e) => setSessionId(e.target.value)}
          error={!!error.sessionId}
          helperText={error.sessionId}
          required
          inputProps={{ 'aria-required': true }}
        />
        <TextField
          label="Rating (1-5)"
          type="number"
          fullWidth
          margin="normal"
          value={rating}
          onChange={(e) => setRating(e.target.value === '' ? '' : Number(e.target.value))}
          error={!!error.rating}
          helperText={error.rating}
          required
          inputProps={{ min: 1, max: 5, 'aria-required': true }}
        />
        <TextField
          label="Comments (optional)"
          fullWidth
          margin="normal"
          multiline
          minRows={3}
          maxRows={6}
          value={comments}
          onChange={(e) => setComments(e.target.value)}
          error={!!error.comments}
          helperText={error.comments}
          inputProps={{ maxLength: 1000 }}
        />
        <Button type="submit" variant="contained" disabled={loading} sx={{ mt: 2 }}>
          {loading ? 'Submitting...' : 'Submit'}
        </Button>
      </Box>
    </Box>
  );
};

export default FeedbackForm;
