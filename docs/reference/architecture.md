# Architecture

## Overview
Press is a static-site generator that wraps Pandoc tooling in a
containerized build and runtime environment. Docker Compose services and
Makefiles coordinate building Markdown content into HTML or PDF and
serving the generated site.

## Repository Layout
- `app/` – Dockerfiles, Docker Compose templates, and build scripts used
  inside containers.
- `bin/` – host-side helper scripts for container management.
- `cfg/` – configuration files used during validation tasks.
- `src/` – markdown sources, templates, and static assets.

## Orchestration
The top-level Makefile (`redo.mk`) drives all host-side automation. It
launches required services and executes the repository Makefile through
the builder service:

- The default goal starts `dragonfly` and `builder` and uses SSH to run the
  project-root `makefile` inside the builder container, which shares its
  image with `shell`.
- A `test` target reruns the build's own tests from the host environment.

## Services
`docker-compose.yml` defines the container stack used by Press:

- `nginx` and `nginx-dev` serve generated content.
- `shell` provides the build environment and exposes tools and tests.
- `builder` runs the same image as `shell` but exposes an SSH daemon. The
  host Makefile drives builds through it for a clean, repeatable
  environment.
- `dragonfly` supplies a Redis-compatible store used for tracking
  document metadata.
- `mermaid` renders diagram sources with `mermaid-cli`. It remains a
  standalone service because the tool is self-contained and kept
  separate from containers like `shell` and `builder`.
- Auxiliary services `sync`, `seed`, and `webp` handle S3 uploads,
  database seeding, and WebP image conversion. The `sync` and `seed`
  containers read the S3 bucket from the `S3_BUCKET_PATH` environment
  variable (default: `s3://press`) and the S3 configuration file from
  `S3CFG_PATH` (default: `/root/.s3cfg`).

## Build Pipeline
The builder service runs the project-root `makefile` to transform sources
into deliverables. It performs index discovery, pre-processing, rendering,
asset handling, and validation. See the [build-process guide](../guides/
build-process.md) for a detailed walkthrough of each stage. Make's
dependency tracking means subsequent runs only rebuild files whose inputs
changed; use `remake` or `r clean` to force a full regeneration.

## Data Flow
Source files in `src/` become processed artifacts in `build/`. The
development `nginx-dev` service mounts the build directory for local
preview, while production content can be synchronized or served by
`nginx`.

## Testing
Python utilities that support the build live under
`app/shell/py/pie`. Unit tests for these helpers execute with `pytest`
via the host Makefile or directly inside the shell container. See the
[tests guide](../guides/tests.md) for usage.

