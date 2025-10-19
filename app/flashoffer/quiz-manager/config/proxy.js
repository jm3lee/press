export function resolveProxyConfig(env = process.env) {
  const apiBase =
    env?.VITE_QUIZ_MANAGER_API_BASE ??
    env?.QUIZ_MANAGER_API_BASE ??
    'http://quiz-backend:8000';

  return {
    '/api/quiz': {
      target: apiBase,
      changeOrigin: true
    }
  };
}
