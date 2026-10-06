import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Typography, Box, CircularProgress, Alert, List, ListItem, ListItemText, Button } from '@mui/material';
import { useAuth } from '../contexts/AuthContext';

interface AssignedProgram {
  program_id: string;
  program_name: string;
  completion_percentage: number;
  status: string;
}

const AssignedPrograms = () => {
  const { user } = useAuth();
  const [programs, setPrograms] = useState<AssignedProgram[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchPrograms = async () => {
    if (!user) return;
    try {
      setLoading(true);
      setError('');
      const res = await axios.get('/programs/assigned', {
        headers: { Authorization: `Bearer ${user.token}` },
      });
      setPrograms(res.data);
    } catch (e) {
      setError('Failed to load assigned programs.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPrograms();
  }, []);

  if (loading) return <CircularProgress aria-label="Loading assigned programs" />;
  if (error) return <Alert severity="error">{error}</Alert>;

  if (programs.length === 0) return <Typography>No assigned programs found.</Typography>;

  return (
    <Box>
      <Typography variant="h4" gutterBottom>Assigned Programs</Typography>
      <List>
        {programs.map((p) => (
          <ListItem key={p.program_id} divider>
            <ListItemText
              primary={p.program_name}
              secondary={`Completion: ${p.completion_percentage}% — Status: ${p.status}`}
            />
          </ListItem>
        ))}
      </List>
    </Box>
  );
};

export default AssignedPrograms;
