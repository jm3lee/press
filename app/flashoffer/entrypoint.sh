#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${FLASHOFFER_ROOT:-/workspace}"
PORT="${PORT:-4173}"

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

ensure_dependencies "${ROOT_DIR}/app/flashoffer-react"
build_package "${ROOT_DIR}/app/flashoffer-react"

ensure_dependencies "${ROOT_DIR}/app/flashoffer-demo"
build_package "${ROOT_DIR}/app/flashoffer-demo"
exec npm run preview -- --host 0.0.0.0 --port "${PORT}"
