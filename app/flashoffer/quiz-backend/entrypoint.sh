#!/bin/sh
set -eu

GUNICORN_BIND="${GUNICORN_BIND:-unix:/tmp/gunicorn.sock}"
GUNICORN_WORKERS="${GUNICORN_WORKERS:-4}"
SOCKET_PATH="$GUNICORN_BIND"
case "$GUNICORN_BIND" in
  unix:*)
    SOCKET_PATH="${GUNICORN_BIND#unix:}"
    ;;
  *)
    SOCKET_PATH=""
    ;;

esac

cleanup() {
  if [ -n "${GUNICORN_PID:-}" ] && kill -0 "$GUNICORN_PID" 2>/dev/null; then
    kill "$GUNICORN_PID" 2>/dev/null || true
    wait "$GUNICORN_PID" 2>/dev/null || true
  fi
  if [ -n "${NGINX_PID:-}" ] && kill -0 "$NGINX_PID" 2>/dev/null; then
    kill "$NGINX_PID" 2>/dev/null || true
    wait "$NGINX_PID" 2>/dev/null || true
  fi
  if [ -n "$SOCKET_PATH" ] && [ -S "$SOCKET_PATH" ]; then
    rm -f "$SOCKET_PATH"
  fi
}

trap cleanup INT TERM EXIT

if [ -n "$SOCKET_PATH" ]; then
  SOCKET_DIR=$(dirname "$SOCKET_PATH")
  mkdir -p "$SOCKET_DIR"
  rm -f "$SOCKET_PATH"
fi

gunicorn \
  --bind "$GUNICORN_BIND" \
  --workers "$GUNICORN_WORKERS" \
  --access-logfile - \
  --error-logfile - \
  "quiz_backend.app:create_app()" &
GUNICORN_PID=$!

nginx -g 'daemon off;' &
NGINX_PID=$!

while :; do
  if ! kill -0 "$GUNICORN_PID" 2>/dev/null; then
    wait "$GUNICORN_PID"
    STATUS=$?
    kill "$NGINX_PID" 2>/dev/null || true
    wait "$NGINX_PID" 2>/dev/null || true
    exit $STATUS
  fi

  if ! kill -0 "$NGINX_PID" 2>/dev/null; then
    wait "$NGINX_PID"
    STATUS=$?
    kill "$GUNICORN_PID" 2>/dev/null || true
    wait "$GUNICORN_PID" 2>/dev/null || true
    exit $STATUS
  fi

  sleep 1
done
