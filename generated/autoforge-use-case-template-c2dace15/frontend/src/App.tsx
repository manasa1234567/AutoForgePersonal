import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import DashboardPage from "./pages/DashboardPage";
import LoginPage from "./pages/LoginPage";
import AccessDeniedPage from "./pages/AccessDeniedPage";
import Header from "./components/Header";
import { AuthProvider, useAuth } from "./hooks/useAuth";

function PrivateRoute({ children, roles }: { children: JSX.Element; roles?: string[] }) {
  const { user } = useAuth();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (roles && !roles.some(r => user.roles.includes(r))) {
    return <Navigate to="/access-denied" replace />;
  }

  return children;
}

export default function App() {
  return (
    <AuthProvider>
      <Header />
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/dashboard"
          element={
            <PrivateRoute>
              <DashboardPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/admin"
          element={
            <PrivateRoute roles={["admin"]}>
              <div style={{ padding: "2rem" }}>
                <h2>Admin Page</h2>
                <div>Full admin access to manage users, programs, permissions, reports.</div>
              </div>
            </PrivateRoute>
          }
        />
        <Route path="/access-denied" element={<AccessDeniedPage />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </AuthProvider>
  );
}
