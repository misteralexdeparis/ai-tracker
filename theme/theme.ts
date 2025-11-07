import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1f7afe',
    },
    secondary: {
      main: '#ffcd38',
    },
    background: {
      default: '#f7f8fc',
      paper: '#fff',
    },
  },
  typography: {
    fontFamily: 'Inter, Arial, sans-serif',
  },
});

export default theme;
