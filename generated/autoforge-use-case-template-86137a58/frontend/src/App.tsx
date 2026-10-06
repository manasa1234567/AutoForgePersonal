import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline, Container } from '@mui/material';
import Dashboard from './components/Dashboard';
import Login from './components/Login';
import AssignedPrograms from './components/AssignedPrograms';
import FeedbackForm from './components/FeedbackForm';
import AttendanceMark from './components/AttendanceMark';
import TeamAnalytics from './components/TeamAnalytics';
import AdminUsers from './components/AdminUsers';
import AdminPrograms from './components/AdminPrograms';
import NotFound from './components/NotFound';
import AccessDenied from './components/AccessDenied';
import { AuthProvider, useAuth } from './contexts/AuthContext';

const theme = createTheme();

function PrivateRoute({ children, roles }: { children: JSX.Element; roles: string[] }) {
  const { user } = useAuth();

  if (!user) {
    return <Navigate to="/login" replace />;
  }
  if (!roles.some(role => user.roles.includes(role))) {
    return <AccessDenied />;
  }

  return children;
}

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <BrowserRouter>
          <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route
                path="/"
                element={
                  <PrivateRoute roles={['Employee', 'Trainer/Mentor', 'Manager', 'Learning Program Coordinator', 'Administrator']}>
                    <Dashboard />
                  </PrivateRoute>
                }
              />
              <Route
                path="/assigned-programs"
                element={
                  <PrivateRoute roles={['Employee']}>
                    <AssignedPrograms />
                  </PrivateRoute>
                }
              />
              <Route
                path="/feedback"
                element={
                  <PrivateRoute roles={['Employee']}>
                    <FeedbackForm />
                  </PrivateRoute>
                }
              />
              <Route
                path="/attendance"
                element={
                  <PrivateRoute roles={['Trainer/Mentor']}>
                    <AttendanceMark />
                  </PrivateRoute>
                }
              />
              <Route
                path="/team-analytics"
                element={
                  <PrivateRoute roles={['Manager']}>
                    <TeamAnalytics />
                  </PrivateRoute>
                }
              />
              <Route
                path="/admin/users"
                element={
                  <PrivateRoute roles={['Administrator']}>
                    <AdminUsers />
                  </PrivateRoute>
                }
              />
              <Route
                path="/admin/programs"
                element={
                  <PrivateRoute roles={['Administrator']}>
                    <AdminPrograms />
                  </PrivateRoute>
                }
              />
              <Route path="/access-denied" element={<AccessDenied />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </Container>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
