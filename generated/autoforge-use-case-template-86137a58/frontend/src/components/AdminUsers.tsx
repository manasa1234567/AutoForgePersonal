import React, { useEffect, useState } from 'react';
import { Box, Typography, CircularProgress, Alert, List, ListItem, ListItemText, Button, TextField } from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

interface UserSummary {
  id: string;
  name: string;
  email: string;
  roles: string[];
}

const AdminUsers = () => {
  const { user } = useAuth();
  const [users, setUsers] = useState<UserSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [newUserName, setNewUserName] = useState('');
  const [newUserEmail, setNewUserEmail] = useState('');
  const [newUserRoles, setNewUserRoles] = useState('Employee');
  const [submitError, setSubmitError] = useState('');
  const [submitSuccess, setSubmitSuccess] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const fetchUsers = async () => {
    if (!user) return;
    try {
      setLoading(true);
      setError('');
      const res = await axios.get('/admin/users', {
        headers: { Authorization: `Bearer ${user.token}` },
      });
      setUsers(res.data);
    } catch (e) {
      setError('Failed to load users.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleCreateUser = async () => {
    setSubmitError('');
    setSubmitSuccess('');
    if (!newUserName.trim() || !newUserEmail.trim()) {
      setSubmitError('Name and email are required');
      return;
    }

    try {
      setSubmitting(true);
      const res = await axios.post(
        '/admin/users',
        { name: newUserName, email: newUserEmail, roles: [newUserRoles] },
        { headers: { Authorization: `Bearer ${user?.token}` } }
      );
      setSubmitSuccess(`User ${res.data.name} created successfully.`);
      setNewUserName('');
      setNewUserEmail('');
      setNewUserRoles('Employee');
      await fetchUsers();
    } catch (e) {
      setSubmitError('Failed to create user.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <CircularProgress aria-label="Loading users" />;
  if (error) return <Alert severity="error">{error}</Alert>;

  return (
    <Box>
      <Typography variant="h4" gutterBottom>User Management</Typography>
      {submitError && <Alert severity="error">{submitError}</Alert>}
      {submitSuccess && <Alert severity="success">{submitSuccess}</Alert>}
      <Box sx={{ mb: 3 }}>
        <TextField
          label="Name"
          value={newUserName}
          onChange={(e) => setNewUserName(e.target.value)}
          sx={{ mr: 2, width: 200 }}
        />
        <TextField
          label="Email"
          value={newUserEmail}
          onChange={(e) => setNewUserEmail(e.target.value)}
          sx={{ mr: 2, width: 250 }}
        />
        <TextField
          label="Role"
          value={newUserRoles}
          select
          SelectProps={{ native: true }}
          onChange={(e) => setNewUserRoles(e.target.value)}
          sx={{ mr: 2, width: 180 }}
        >
          <option value="Employee">Employee</option>
          <option value="Trainer/Mentor">Trainer/Mentor</option>
          <option value="Manager">Manager</option>
          <option value="Learning Program Coordinator">Learning Program Coordinator</option>
          <option value="Administrator">Administrator</option>
        </TextField>
        <Button variant="contained" onClick={handleCreateUser} disabled={submitting}>
          {submitting ? 'Creating...' : 'Create User'}
        </Button>
      </Box>

      <List>
        {users.map((u) => (
          <ListItem key={u.id} divider>
            <ListItemText primary={`${u.name} (${u.email})`} secondary={`Roles: ${u.roles.join(', ')}`} />
          </ListItem>
        ))}
      </List>
    </Box>
  );
};

export default AdminUsers;
