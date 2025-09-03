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
r all     # run the repository makefile in the shell service
```

The build reads source files under `src/` (or `SRC_DIR` if overridden) and
writes HTML and assets to `build/`. Logs are stored in `log/`.

If you only need the build step without starting services, run `r all` directly.

Behind the scenes `r all` runs the build inside the `shell` service using
`docker compose run`. Use `shell` for ad-hoc commands, tests, and
repeatable builds.

## Pipeline overview

Running `r all` triggers a sequence of Make targets inside the `shell`
container:

1. **Index discovery** – Markdown and YAML files are scanned and their metadata
   recorded in the `dragonfly` key-value store. Each document's source paths are
   stored under `<id>.path` and each path maps back to its owning ID. The build
   uses this index to resolve cross references and dependency relationships.
2. **Pre-processing** – Custom filters convert assets before rendering. Examples
   include `preprocess` for macro expansion, YAML normalization, and rules that
   turn Mermaid diagrams into SVG. Diagram rendering delegates to the
   standalone `mermaid` service, which isolates the third-party CLI from core
   images such as `shell`.
3. **Markdown rendering** – Pre-processed Markdown is converted to HTML using a
   shared template powered by `markdown2` and `Jinja2`. Table of contents
   generation, MathJax rendering, and cross-reference resolution are handled in
   Python.
4. **Asset pipeline** – SCSS stylesheets and other static files are compiled or
   copied into `build/`. The default `src/css/style.css` file supports the full
   SCSS syntax and produces `build/css/style.css`. Additional rules from
   `dep.mk` can introduce custom targets.
5. **Validation** – Link checking and page title verification run against the
   generated HTML before the build is considered complete. See
  [checklinks](../pie/check/checklinks.md) and
  [check-page-title](../pie/check/check-page-title.md).

The Makefiles track dependencies so incremental runs only rebuild what changed.
Deleting targets with `remake` or `r clean` forces regeneration when needed.

## Styling with SCSS

Site styles live under `src/css/` and are compiled with the Python `libsass`
library into `build/css/`. The default stylesheet is `src/css/style.css` which
supports full SCSS syntax. Any changes to files in this directory are
automatically processed during the `r all` build and the output CSS is written
to `build/css/style.css`.

To add additional stylesheets, create new files in `src/css/` and reference the
resulting `/css/*.css` paths from your pages or templates.

The build injects a version query string into stylesheet links using the
`BUILD_VER` variable. Each run sets it to the short Git commit hash,
producing references like `/css/style.css?v=<hash>` so browsers always
fetch the latest CSS after each commit.

## Cleaning up

Use the provided targets to tidy generated files:

```bash
r clean       # remove build/
r distclean   # also clear cached data and .init markers
```

## Troubleshooting

Set `VERBOSE=1` on any command to see the underlying Docker and Make
invocations:

```bash
r all VERBOSE=1
```

For a deeper look at how `redo.mk` orchestrates the build, see
[redo-mk.md](redo-mk.md). To customize dependencies, refer to
[dep-mk.md](dep-mk.md).
