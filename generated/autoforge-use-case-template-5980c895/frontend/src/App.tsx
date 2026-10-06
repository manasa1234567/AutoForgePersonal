import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";
import AccessDenied from "./pages/AccessDenied";
import { AuthProvider, useAuth } from "./context/AuthContext";

function PrivateRoute({ children, roles }: { children: React.ReactElement; roles?: string[] }) {
  const { user } = useAuth();
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  if (roles && !roles.includes(user.role)) {
    return <Navigate to="/access-denied" replace />;
  }
  return children;
}

export default function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/dashboard"
            element={<PrivateRoute><Dashboard /></PrivateRoute>}
          />
          <Route
            path="/admin"
            element={<PrivateRoute roles={["Administrator"]}><div>Admin Panel - Under Construction</div></PrivateRoute>}
          />
          <Route path="/access-denied" element={<AccessDenied />} />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}
