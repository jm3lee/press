import test from 'node:test';
import assert from 'node:assert/strict';
import { resolveProxyConfig } from '../config/proxy.js';

test('defaults to local quiz backend proxy', () => {
  const proxy = resolveProxyConfig({});
  assert.ok(proxy['/api/quiz'], 'proxy configuration missing /api/quiz');
  assert.equal(proxy['/api/quiz'].target, 'http://localhost:8002');
  assert.equal(proxy['/api/quiz'].changeOrigin, true);
});

test('prefers VITE_QUIZ_MANAGER_API_BASE environment variable', () => {
  const base = 'http://quiz-backend:9000';
  const proxy = resolveProxyConfig({ VITE_QUIZ_MANAGER_API_BASE: base });
  assert.equal(proxy['/api/quiz'].target, base);
});

test('falls back to QUIZ_MANAGER_API_BASE environment variable', () => {
  const base = 'http://quiz-backend:8000';
  const proxy = resolveProxyConfig({ QUIZ_MANAGER_API_BASE: base });
  assert.equal(proxy['/api/quiz'].target, base);
});
