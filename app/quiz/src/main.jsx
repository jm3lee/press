/**
 * @fileoverview
 * Entry point for the SearchIndex React application.
 *
 * This module waits for the DOM to be fully loaded, locates the
 * `#quiz-root` element, and renders the [`SearchIndex`](./SearchIndex) component
 * into it, passing along any `data-name` attribute as a prop.
 */

import { StrictMode } from 'react';
import { Provider } from 'react-redux';
import { createRoot } from 'react-dom/client';
import './index.css';
import Quiz from './Quiz';
import { store } from './store';

/**
 * Bootstraps and renders the SearchIndex component into the DOM.
 *
 * Waits for the `DOMContentLoaded` event, then:
 * 1. Queries the `#quiz-root` element.
 * 2. If found, creates a React root and renders the application.
 * 3. Passes the element's `data-name` attribute as the `name` prop.
 *
 * @returns {void}
 */
function initializeSearchIndex() {
  const mount = document.getElementById('quiz-root');
  if (!mount) {
    return;
  }

  const root = createRoot(mount);
  root.render(
    <StrictMode>
      <Provider store={store}>
        <Quiz src={mount.getAttribute('data-src')} />
      </Provider>
    </StrictMode>
  );
}

window.addEventListener('DOMContentLoaded', initializeSearchIndex);
