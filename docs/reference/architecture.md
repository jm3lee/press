# Architecture

## Overview
Press is a static-site generator that wraps Pandoc tooling in a containerized build and runtime environment. Docker Compose services and Makefiles coordinate building Markdown content into HTML or PDF and serving the generated site.

## Repository Layout
- `app/` – Dockerfiles, Docker Compose templates, and build scripts used inside containers.
- `bin/` – host-side helper scripts for container management.
- `cfg/` – configuration files used during validation tasks.
- `src/` – markdown sources, templates, and static assets.

## Orchestration
The top-level Makefile (`redo.mk`) drives all host-side automation. It launches required services and executes the inner build Makefile within the shell container:

- The default goal starts `dragonfly` and invokes `/app/mk/build.mk` inside the shell container to render the site.
- A `test` target reruns the build's own tests from the host environment.

## Services
`docker-compose.yml` defines the container stack used by Press:

- `nginx` and `nginx-dev` serve generated content.
- `shell` provides the build environment and exposes tools and tests.
- `dragonfly` supplies a Redis-compatible store used for tracking document metadata.
- Auxiliary services `sync`, `seed`, and `webp` handle S3 uploads, database seeding, and WebP image conversion.

## Build Pipeline
The shell container executes `app/shell/mk/build.mk` to transform sources into deliverables:

1. Discover Markdown and YAML files and update a Redis-backed index. See [build-index](../guides/build-index.md) and [update-index](../guides/update-index.md) for details on this step. Each document's source paths are stored under `<id>.path`.
2. Convert preprocessed Markdown to HTML and PDF using Pandoc with a shared template and options for table of contents, math rendering, and cross references.
3. Copy CSS assets and minify the resulting site.
4. Run link checking and page title validation before marking the build complete. See [checklinks](../guides/checklinks.md) and [check-page-title](../guides/check-page-title.md).

## Data Flow
Source files in `src/` become processed artifacts in `build/`. The development `nginx-dev` service mounts the build directory for local preview, while production content can be synchronized or served by `nginx`.

## Testing
Python utilities that support the build live under `app/shell/py/pie`. Unit
tests for these helpers execute with `pytest` via the host Makefile or directly
inside the shell container. See the [tests guide](../guides/tests.md) for
usage.

