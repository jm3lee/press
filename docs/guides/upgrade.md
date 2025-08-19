# upgrade helper

`bin/upgrade` rebuilds the development environment after pulling new changes. It stops running containers, rebuilds images and dependencies, and runs the full test suite to ensure the project is ready.

## Usage

```bash
./bin/upgrade
```

The script performs the following steps:

1. Stops existing Docker services.
2. Cleans the workspace with `distclean` and rebuilds the shell image.
3. Runs `make`, `make test`, and `pytest` to validate the build.
4. Restarts `nginx-test` and other required containers.

### Environment variables

- `VERBOSE` – set to `1` for verbose `make` output. Defaults to `0`.
- `SRC_DIR` – source directory for `make`. Defaults to `src`.
- `BUILD_DIR` – build output directory for `make`. Defaults to `build`.

Run this script after `git pull` to keep your development environment in sync with repository changes.
