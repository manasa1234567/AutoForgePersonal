import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import CssBaseline from '@mui/material/CssBaseline';
import { ThemeProvider, createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2'
    },
    background: {
      default: '#f9f9f9'
    }
  },
  typography: {
    fontFamily: 'Roboto, Arial, sans-serif'
  },
  components: {
    MuiButton: {
      defaultProps: {
        disableElevation: true
      }
    }
  }
});

const root = ReactDOM.createRoot(document.getElementById('root')!);
root.render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  </React.StrictMode>
);
