# Press

Press is a static-site generator built on Pandoc and Docker, orchestrated with `docker compose` and `redo.mk`.

## Benefits

- Reproducible builds through containerized services and declarative tasks
- Flexible content formats processed by Pandoc
- Built-in validation keeps pages consistent and free of broken links

## Key Features

- `redo.mk`-driven pipeline with incremental build steps
- Automatic metadata indexing and JSON index generation
- Optional services for API docs, image optimization, and local previews

## Documentation

All project documentation lives under [docs/](docs/). Start with the [guides](docs/guides/README.md) for step-by-step workflows and see the [reference](docs/reference/README.md) for technical details.

## Configuration

Environment variables for Docker services are defined in a `.env` file.
The makefile copies `.env.example` to `.env` if it does not exist; adjust the
values as needed.

