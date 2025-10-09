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

ensure_dependencies "${ROOT_DIR}/app/flashoffer/flashoffer-react"
ensure_dependencies "${ROOT_DIR}/app/flashoffer/flashoffer-demo"

if [ "${MODE}" = "dev" ]; then
  cd "${ROOT_DIR}/app/flashoffer/flashoffer-demo"
  exec npm run dev -- --host 0.0.0.0 --port "${PORT}"
fi

build_package "${ROOT_DIR}/app/flashoffer/flashoffer-react"
build_package "${ROOT_DIR}/app/flashoffer/flashoffer-demo"
exec npm run preview -- --host 0.0.0.0 --port "${PORT}"
