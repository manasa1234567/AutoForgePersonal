import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './auth/AuthContext';
import DashboardPage from './pages/DashboardPage';
import LoginPage from './pages/LoginPage';
import AdminPage from './pages/AdminPage';
import NotAuthorizedPage from './pages/NotAuthorizedPage';
import ProgramCreationPage from './pages/ProgramCreationPage';
import './styles/global.css';

function RequireAuth({ children, roles }: { children: JSX.Element; roles?: string[] }) {
  const { user } = useAuth();

  if (!user) {
    return <Navigate to="/login" />;
  }
  if (roles && !roles.includes(user.role)) {
    return <Navigate to="/not-authorized" />;
  }
  return children;
}

export default function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/"
            element={<RequireAuth><DashboardPage /></RequireAuth>}
          />
          <Route
            path="/admin"
            element={<RequireAuth roles={["Administrator"]}><AdminPage /></RequireAuth>}
          />
          <Route
            path="/programs/new"
            element={<RequireAuth roles={["Learning Program Coordinator"]}><ProgramCreationPage /></RequireAuth>}
          />
          <Route path="/not-authorized" element={<NotAuthorizedPage />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}
