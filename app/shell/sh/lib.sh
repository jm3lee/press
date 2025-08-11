#!/usr/bin/env bash

press_run() {
  docker compose run \
    --rm --entrypoint "$1" -u "$(id -u)" \
    shell "${@:2}"
}

press_bash() {
  press_run bash "$@"
}

press_make() {
  press_run make -f /app/mk/build.mk "$@"
}

press_redis_cli() {
  docker compose exec dragonfly redis-cli "$@"
}

