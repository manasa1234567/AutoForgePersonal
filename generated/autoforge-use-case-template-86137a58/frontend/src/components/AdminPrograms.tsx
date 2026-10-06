import React, { useEffect, useState } from 'react';
import { Box, Typography, CircularProgress, Alert, List, ListItem, ListItemText } from '@mui/material';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

interface ProgramSummary {
  id: string;
  name: string;
  description?: string;
}

const AdminPrograms = () => {
  const { user } = useAuth();
  const [programs, setPrograms] = useState<ProgramSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchPrograms = async () => {
    if (!user) return;
    try {
      setLoading(true);
      setError('');
      const res = await axios.get('/admin/programs', {
        headers: { Authorization: `Bearer ${user.token}` },
      });
      setPrograms(res.data);
    } catch (e) {
      setError('Failed to load programs.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPrograms();
  }, []);

  if (loading) return <CircularProgress aria-label="Loading programs" />;
  if (error) return <Alert severity="error">{error}</Alert>;

  if (programs.length === 0) return <Typography>No programs found.</Typography>;

  return (
    <Box>
      <Typography variant="h4" gutterBottom>Program Management</Typography>
      <List>
        {programs.map((p) => (
          <ListItem key={p.id} divider>
            <ListItemText primary={p.name} secondary={p.description || 'No description'} />
          </ListItem>
        ))}
      </List>
    </Box>
  );
};

export default AdminPrograms;
