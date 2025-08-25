/**
 * Entry point for the IndexTree React demo.
 * Finds all elements with the `indextree-root` class and renders the
 * IndexTree component for each, using the element's data-src attribute as the
 * JSON source.
 */
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import './index.css';
import IndexTree from './IndexTree';

function initializeIndexTrees() {
  const mounts = document.querySelectorAll('.indextree-root, #indextree-root');
  if (mounts.length === 0) {
    return;
  }
  const fontBase =
    getComputedStyle(document.documentElement).getPropertyValue('--font-base') ||
    '"minion-pro", serif';
  const theme = createTheme({
    typography: { fontFamily: fontBase.trim(), fontSize: '1em' },
  });
  mounts.forEach((mount) => {
    const root = createRoot(mount);
    root.render(
      <StrictMode>
        <ThemeProvider theme={theme}>
          <IndexTree src={mount.getAttribute('data-src')} />
        </ThemeProvider>
      </StrictMode>
    );
  });
}

window.addEventListener('DOMContentLoaded', initializeIndexTrees);
