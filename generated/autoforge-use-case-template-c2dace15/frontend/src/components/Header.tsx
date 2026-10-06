import React from "react";
import { useAuth } from "../hooks/useAuth";
import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import Box from "@mui/material/Box";
import { Link as RouterLink } from "react-router-dom";

export default function Header() {
  const { user, logout } = useAuth();

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component={RouterLink} to="/dashboard" sx={{ flexGrow: 1, textDecoration: "none", color: "inherit" }}>
          Enterprise LMS
        </Typography>
        {user ? (
          <Box>
            {user.roles.includes("admin") && (
              <Button color="inherit" component={RouterLink} to="/admin">
                Admin
              </Button>
            )}
            <Button color="inherit" onClick={logout}>
              Logout ({user.username})
            </Button>
          </Box>
        ) : (
          <Button color="inherit" component={RouterLink} to="/login">
            Login
          </Button>
        )}
      </Toolbar>
    </AppBar>
  );
}
