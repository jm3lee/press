#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${FLASHOFFER_ROOT:-/workspace}"
PORT="${PORT:-4173}"

cd "${ROOT_DIR}/app/flashoffer-react"
if [ ! -d node_modules ]; then
  npm ci
fi
npm run build

cd "${ROOT_DIR}/app/flashoffer-demo"
if [ ! -d node_modules ]; then
  npm ci
fi
npm run build
exec npm run preview -- --host 0.0.0.0 --port "${PORT}"
