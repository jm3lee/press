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

## Styling

Site styles live under `src/css/` and are compiled with the Python `libsass` library into
`build/css/`. Edit `src/css/style.css` or add additional files in that
directory using SCSS syntax to customize the site appearance.

## Documentation

All project documentation lives under [docs/](docs/). Start with the [guides](docs/guides/README.md) for step-by-step workflows and see the [reference](docs/reference/README.md) for technical details.

## Testing

Run the test suite inside the same container used for development:

```bash
r pytest
```

This command executes pytest in the shell service so results match CI. For
coverage reporting use:

```bash
r cov
```

Coverage reports are written to `log/cov`. See
[docs/guides/tests.md](docs/guides/tests.md) for more details.

