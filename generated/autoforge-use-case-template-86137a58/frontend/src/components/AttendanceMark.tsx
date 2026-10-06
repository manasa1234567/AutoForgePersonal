import React, { useState } from 'react';
import { Box, Typography, TextField, Button, Alert } from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

const AttendanceMark = () => {
  const { user } = useAuth();
  const [sessionId, setSessionId] = useState('');
  const [participantId, setParticipantId] = useState('');
  const [present, setPresent] = useState(true);
  const [error, setError] = useState<Record<string, string>>({});
  const [submitError, setSubmitError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};
    if (!sessionId.trim()) {
      newErrors.sessionId = 'Session ID is required';
    }
    if (!participantId.trim()) {
      newErrors.participantId = 'Participant ID is required';
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
        '/attendance/mark',
        { session_id: sessionId, participant_id: participantId, present },
        { headers: { Authorization: `Bearer ${user?.token}` } }
      );
      setSuccess(true);
      setSessionId('');
      setParticipantId('');
      setPresent(true);
    } catch (e) {
      setSubmitError('Failed to mark attendance. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ maxWidth: 600 }}>
      <Typography variant="h4" gutterBottom>Mark Attendance</Typography>
      {success && <Alert severity="success">Attendance marked successfully.</Alert>}
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
          label="Participant ID"
          fullWidth
          margin="normal"
          value={participantId}
          onChange={(e) => setParticipantId(e.target.value)}
          error={!!error.participantId}
          helperText={error.participantId}
          required
          inputProps={{ 'aria-required': true }}
        />
        <Typography component="fieldset" variant="body1" sx={{ mt: 2 }}>
          <label>
            <input
              type="radio"
              name="present"
              value="true"
              checked={present === true}
              onChange={() => setPresent(true)}
            /> Present
          </label>{' '}
          <label>
            <input
              type="radio"
              name="present"
              value="false"
              checked={present === false}
              onChange={() => setPresent(false)}
            /> Absent
          </label>
        </Typography>

        <Button type="submit" variant="contained" disabled={loading} sx={{ mt: 2 }}>
          {loading ? 'Marking...' : 'Mark Attendance'}
        </Button>
      </Box>
    </Box>
  );
};

export default AttendanceMark;
