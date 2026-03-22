import React from 'react';
import ReactDOM from 'react-dom/client';
import { ChakraProvider, extendTheme } from '@chakra-ui/react';
import App from './App';

// Custom theme
const theme = extendTheme({
  colors: {
    brand: {
      50: '#f5f7ff',
      100: '#ebefff',
      200: '#c3ccff',
      300: '#9ba9ff',
      400: '#7386ff',
      500: '#667eea',
      600: '#5568d3',
      700: '#4451b8',
      800: '#333b9d',
      900: '#222582',
    },
  },
  fonts: {
    heading: `'Inter', sans-serif`,
    body: `'Inter', sans-serif`,
  },
});

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <ChakraProvider theme={theme}>
      <App />
    </ChakraProvider>
  </React.StrictMode>
);