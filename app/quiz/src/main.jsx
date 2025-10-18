import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import Quiz from './Quiz';

/**
 * Mount the Quiz component as soon as the DOM is ready.
 *
 * @returns {void}
 */
function bootstrapQuiz() {
  const mount = document.getElementById('quiz-root');
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

window.addEventListener('DOMContentLoaded', bootstrapQuiz);
