# redo.mk Overview

`redo.mk` defines high-level developer tasks for this project. Most targets wrap
`docker compose` commands so that the build environment is consistent. The file
is meant to be invoked with `make -f redo.mk` (often aliased to `r`). By default
it prints only brief status messages; set `VERBOSE=1` to also show the
underlying commands.

This repository actually uses three Makefiles that work together:

- **`redo.mk`** – run from the host to start Docker containers and delegate
  commands.
- **`build.mk`** – copied into the shell container as `/app/mk/build.mk` and
  executed by `make` inside that container to build the site.
- **`dep.mk`** – optional file included by `build.mk` for custom dependencies.

## Variables

- **`SRC_DIR`** – Directory containing source files (default: `src`).
- **`BUILD_DIR`** – Directory for generated output (default: `build`).
- **`SERVICES`** – Containers started by `up`/`upd` (default: `nginx-dev sync webp`).
- **`MAKE_CMD`** – Helper command to run the lower-level makefile inside the `shell` service.
- **`COMPOSE_FILE`** – Compose file used by commands. Defaults to `docker-compose.yml` in the project root.
- **`DOCKER_COMPOSE`** – Shortcut for `docker compose -f $(COMPOSE_FILE)`.
- **`VERBOSE`** – Set to `1` to print each command executed by `make` in addition to status messages.

## Common Targets

| Target | Description |
| ------ | ----------- |
| `all`  | Builds the site by invoking `/app/mk/build.mk` inside the shell container. |
| `clean` | Removes everything under `build/`. |
| `cov` | Generates an HTML coverage report for the `pie` package inside the shell container (output in `log/cov`). |
| `distclean` | Runs `clean` and removes `.init` markers and the Dragonfly index cache. |
| `docker` | Builds and pushes the Nginx image after running `test`. |
| `down` | Stops and removes the compose stack. |
| `prune` | Runs `docker system prune -f` to clean unused Docker resources. |
| `pytest` | Runs unit tests for the `pie` package inside the shell container. |
| `redis` | Opens a Redis CLI connected to the `dragonfly` service. |
| `rmi` | Removes Docker images matching `press-*` using `./bin/docker-rmi-pattern`. |
| `seed` | Runs the `seed` container to populate initial data (bucket from `S3_BUCKET_PATH`, default `s3://press`; config from `S3CFG_PATH`, default `/root/.s3cfg`). |
| `setup` | Prepares `app/webp` directories and builds all services. |
| `shell` | Opens an interactive shell container. |
| `sync` | Runs the `sync` container to upload site files to S3 (bucket from `S3_BUCKET_PATH`, default `s3://press`; config from `S3CFG_PATH`, default `/root/.s3cfg`). |
| `test` | Restarts `nginx-dev` and runs tests defined in `/app/mk/build.mk`. |
| `up` / `upd` | Starts development containers (`SERVICES`). `upd` runs detached. |
| `webp` | Runs the image conversion service. |

Run `make -f redo.mk <target>` (or `r <target>` if you use the alias from the README) to execute any of these commands.

