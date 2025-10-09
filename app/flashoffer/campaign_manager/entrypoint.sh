#!/usr/bin/env bash
set -euo pipefail

exec uvicorn campaign_manager.app:create_app --host 0.0.0.0 --port "${PORT:-4173}" --factory
