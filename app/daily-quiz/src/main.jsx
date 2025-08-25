/**
 * @fileoverview
 * Entry point for the DailyQuiz React application.
 *
 * This module waits for the DOM to be fully loaded, locates the
 * `#daily-quiz-root` element, and renders the [`Quiz`](./Quiz) component into
 * it, passing along any `data-src` attribute as a prop.
 */

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import Quiz from './Quiz';

/**
 * Bootstraps and renders the Quiz component into the DOM.
 *
 * Waits for the `DOMContentLoaded` event, then:
 * 1. Queries the `#daily-quiz-root` element.
 * 2. If found, creates a React root and renders the application.
 * 3. Passes the element's `data-src` attribute as the `src` prop.
 *
 * @returns {void}
 */
function initializeDailyQuiz() {
  const mount = document.getElementById('daily-quiz-root');
  if (!mount) {
    return;
  }

  const root = createRoot(mount);
  root.render(
    <StrictMode>
      <Quiz src={mount.getAttribute('data-src')} />
    </StrictMode>
  );
}

window.addEventListener('DOMContentLoaded', initializeDailyQuiz);

