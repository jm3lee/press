#!/usr/bin/env bash

press_bash() {
  docker compose run \
    --rm --entrypoint bash -u "$(id -u)" \
    shell "$@"
}

