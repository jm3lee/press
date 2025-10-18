import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import QuizManager from './QuizManager.jsx';
import './styles.css';

function bootstrap() {
  const mount = document.getElementById('root');
  if (!mount) {
    return;
  }

  const endpoint = mount.getAttribute('data-endpoint') ?? undefined;
  const root = createRoot(mount);
  root.render(
    <StrictMode>
      <main>
        <QuizManager uploadEndpoint={endpoint} />
      </main>
    </StrictMode>
  );
}

document.addEventListener('DOMContentLoaded', bootstrap);
