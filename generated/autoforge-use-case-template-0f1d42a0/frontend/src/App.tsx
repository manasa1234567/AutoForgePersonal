import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { CssBaseline } from "@mui/material";
import DashboardPage from "./pages/DashboardPage";
import LoginPage from "./pages/LoginPage";
import AccessDeniedPage from "./pages/AccessDeniedPage";
import { AuthProvider, useAuth } from "./auth/AuthContext";
import Loader from "./components/Loader";

function PrivateRoute({ children }: { children: JSX.Element }) {
  const { user, loading } = useAuth();

  if (loading) return <Loader />;

  if (!user) return <Navigate to="/login" replace />;

  return children;
}

function AdminRoute({ children }: { children: JSX.Element }) {
  const { user } = useAuth();
  if (!user || user.role !== "admin") {
    return <Navigate to="/access-denied" replace />;
  }
  return children;
}

function App() {
  return (
    <AuthProvider>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/"
            element={
              <PrivateRoute>
                <DashboardPage />
              </PrivateRoute>
            }
          />
          <Route path="/access-denied" element={<AccessDeniedPage />} />
          {/* Additional routes for admin pages, etc. */}
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
