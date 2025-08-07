/**
 * Entry point for the IndexTree React demo.
 * Finds the #indextree-root element and renders the IndexTree component
 * using the element's data-src attribute as the JSON source.
 */
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import './index.css';
import IndexTree from './IndexTree';

function initializeIndexTree() {
  const mount = document.getElementById('indextree-root');
  if (!mount) {
    return;
  }
  const fontBase =
    getComputedStyle(document.documentElement).getPropertyValue('--font-base') ||
    '"minion-pro", serif';
  const theme = createTheme({
    typography: { fontFamily: fontBase.trim() },
  });
  const root = createRoot(mount);
  root.render(
    <StrictMode>
      <ThemeProvider theme={theme}>
        <IndexTree src={mount.getAttribute('data-src')} />
      </ThemeProvider>
    </StrictMode>
  );
}

window.addEventListener('DOMContentLoaded', initializeIndexTree);
