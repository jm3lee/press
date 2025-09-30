#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${FLASHOFFER_ROOT:-/workspace}"
MODE="${FLASHOFFER_MODE:-preview}"

case "${MODE}" in
  dev)
    PORT="${PORT:-5173}"
    ;;
  preview)
    PORT="${PORT:-4173}"
    ;;
  *)
    echo "Unsupported FLASHOFFER_MODE: ${MODE}" >&2
    exit 1
    ;;
esac

ensure_dependencies() {
  local package_dir="$1"
  cd "${package_dir}"

  if [ ! -d node_modules ] || [ ! -x node_modules/.bin/vite ]; then
    npm ci --include=dev
  fi
}

build_package() {
  local package_dir="$1"
  cd "${package_dir}"
  npm run build
}

if [ "${MODE}" = "dev" ]; then
  ensure_dependencies "${ROOT_DIR}/app/flashoffer-react"
  ensure_dependencies "${ROOT_DIR}/app/flashoffer-demo"

  build_package "${ROOT_DIR}/app/flashoffer-react"
  build_package "${ROOT_DIR}/app/flashoffer-demo"

  cd "${ROOT_DIR}/app/flashoffer-demo"
  exec npm run dev -- --host 0.0.0.0 --port "${PORT}"
fi

if [ ! -d "${ROOT_DIR}/app/flashoffer-demo/dist" ]; then
  echo "flashoffer-demo has not been built. Expected dist directory missing." >&2
  echo "Ensure the production image copies build artifacts from the build stage." >&2
  exit 1
fi

exec serve -s "${ROOT_DIR}/app/flashoffer-demo/dist" -l "tcp://0.0.0.0:${PORT}"
