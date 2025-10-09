#!/usr/bin/env bash
set -euo pipefail

: "${BACKEND_PORT:=8000}"
: "${PORT:=4173}"

export VITE_FLASHOFFER_CAMPAIGN_MANAGER_API_BASE="http://127.0.0.1:${BACKEND_PORT}"

cleanup() {
  if [[ -n "${backend_pid:-}" ]]; then
    kill "${backend_pid}" 2>/dev/null || true
  fi
  if [[ -n "${nginx_pid:-}" ]]; then
    kill "${nginx_pid}" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

envsubst '
  $BACKEND_PORT
  $CAMPAIGN_MANAGER_STATIC_DIR
  $PORT
' < /etc/nginx/conf.d/default.conf > /etc/nginx/conf.d/default.conf.rendered
mv /etc/nginx/conf.d/default.conf.rendered /etc/nginx/conf.d/default.conf

uvicorn campaign_manager.app:create_app \
  --host 0.0.0.0 \
  --port "${BACKEND_PORT}" \
  --factory &
backend_pid=$!

nginx -g "daemon off;" &
nginx_pid=$!

wait -n "${backend_pid}" "${nginx_pid}"
