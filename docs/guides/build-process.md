# Build Process

This guide walks new engineers through the Press build pipeline. It explains the
moving pieces, how they fit together, and the commands you will use most often.

## Prerequisites

Install Docker and `make` on your machine. The project uses a small Makefile
called `redo.mk` to drive Docker Compose. For convenience, add the alias used
throughout the docs:

```bash
alias r='make -f redo.mk'
```

## Initial setup

Before running any builds, prepare the environment and build Docker images:

```bash
r setup
```

This step creates required directories, builds the service images, and pulls any
base images defined in `docker-compose.yml`.

## Running the build

Start the development stack and render the site:

```bash
r up      # start compose services
r all     # invoke app/shell/mk/build.mk inside the shell container
```

The build reads source files under `src/` (or `SRC_DIR` if overridden) and writes
HTML and assets to `build/`. Logs are stored in `log/`.

If you only need the build step without starting services, run `r all` directly.

## Cleaning up

Use the provided targets to tidy generated files:

```bash
r clean       # remove build/
r distclean   # also clear cached data and .init markers
```

## Troubleshooting

Set `VERBOSE=1` on any command to see the underlying Docker and Make invocations:

```bash
r all VERBOSE=1
```

For a deeper look at how `redo.mk` orchestrates the build, see
[redo-mk.md](redo-mk.md). To customize dependencies, refer to
[dep-mk.md](dep-mk.md).
