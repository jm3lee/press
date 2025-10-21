import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { HashRouter, Route, Routes } from 'react-router-dom';
import QuizManager from './QuizManager.jsx';
import './styles.css';

export function App({ endpoint }) {
  return (
    <HashRouter>
      <main>
        <Routes>
          <Route path="/*" element={<QuizManager uploadEndpoint={endpoint} />} />
        </Routes>
      </main>
    </HashRouter>
  );
}

function bootstrap() {
  const mount = document.getElementById('root');
  if (!mount) {
    return;
  }

  const endpoint = mount.getAttribute('data-endpoint') ?? undefined;
  const root = createRoot(mount);
  root.render(
    <StrictMode>
      <App endpoint={endpoint} />
    </StrictMode>
  );
}

document.addEventListener('DOMContentLoaded', bootstrap);
