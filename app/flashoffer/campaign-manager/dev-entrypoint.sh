#!/usr/bin/env bash
set -euo pipefail

export VITE_FLASHOFFER_CAMPAIGN_MANAGER_API_BASE="http://127.0.0.1:${BACKEND_PORT:-8000}"

cleanup() {
  if [[ -n "${backend_pid:-}" ]]; then
    kill "${backend_pid}" 2>/dev/null || true
  fi
  if [[ -n "${frontend_pid:-}" ]]; then
    kill "${frontend_pid}" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

uvicorn campaign_manager.app:create_app \
  --host 0.0.0.0 \
  --port "${BACKEND_PORT:-8000}" \
  --factory \
  --reload &
backend_pid=$!

npm run dev -- --host 0.0.0.0 --port "${VITE_DEV_SERVER_PORT:-5174}" &
frontend_pid=$!

wait -n "${backend_pid}" "${frontend_pid}"
