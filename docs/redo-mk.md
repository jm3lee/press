# redo.mk Overview

`redo.mk` defines high-level developer tasks for this project. Most targets wrap `docker compose` commands so that the build environment is consistent. The file is meant to be invoked with `make -f redo.mk` (often aliased to `r`).

## Variables

- **`SERVICES`** – Containers started by `up`/`upd` (default: `nginx-dev sync webp`).
- **`MAKE_CMD`** – Helper command to run the lower-level makefile inside the `shell` service.
- **`IMAGE_NAME`** – Name of the Nginx image to tag and push (default: `koreanbriancom-nginx`).
- **`REGISTRY`** – Container registry used by the `docker` target (default: `registry.digitalocean.com/artisticanatomy`).

## Common Targets

| Target | Description |
| ------ | ----------- |
| `all`  | Builds the site by invoking `/app/mk/build.mk` inside the shell container. |
| `docker` | Builds and pushes the Nginx image after running `test`. |
| `test` | Restarts `nginx-dev` and runs tests defined in `/app/mk/build.mk`. |
| `up` / `upd` | Starts development containers (`SERVICES`). `upd` runs detached. |
| `down` | Stops and removes the compose stack. |
| `clean` | Removes everything under `build/`. |
| `prune` | Runs `docker system prune -f` to clean unused Docker resources. |
| `setup` | Builds the service framework image, prepares `app/webp` directories and builds all services. |
| `seed` | Runs the `seed` container to populate initial data. |
| `sync` | Runs the `sync` container to upload site files to S3. |
| `webp` | Runs the image conversion service. |
| `shell` | Opens an interactive shell container. |
| `rmi` | Removes Docker images matching `press-*` using `./bin/docker-rmi-pattern`. |

Run `make -f redo.mk <target>` (or `r <target>` if you use the alias from the README) to execute any of these commands.

