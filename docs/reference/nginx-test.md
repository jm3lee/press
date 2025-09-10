# nginx-test

Start the `nginx-test` service and run the project's test suite.

```bash
nginx-test
```

The script launches the service with `docker compose` and executes `make test`
in the current repository. The container is torn down automatically when the
command finishes.

Environment variables influence the underlying `make` invocation:

- `VERBOSE` – passed to `make` (default: `0`)
- `SRC_DIR` – source directory (default: `src`)
- `BUILD_DIR` – build directory (default: `build`)

