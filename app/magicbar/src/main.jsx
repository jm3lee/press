import React from 'react';
import { createRoot } from 'react-dom/client';
import MagicBar from './MagicBar.jsx';

const container = document.getElementById('magicbar-root');
const src = container.dataset.src;

fetch(src)
  .then((res) => res.json())
  .then((pages) => {
    createRoot(container).render(<MagicBar pages={pages} />);
  });
