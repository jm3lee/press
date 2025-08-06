/**
 * Entry point for the IndexTree React demo.
 * Finds the #indextree-root element and renders the IndexTree component
 * using the element's data-src attribute as the JSON source.
 */
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import IndexTree from './IndexTree';

function initializeIndexTree() {
  const mount = document.getElementById('indextree-root');
  if (!mount) {
    return;
  }
  const root = createRoot(mount);
  root.render(
    <StrictMode>
      <IndexTree src={mount.getAttribute('data-src')} />
    </StrictMode>
  );
}

window.addEventListener('DOMContentLoaded', initializeIndexTree);
