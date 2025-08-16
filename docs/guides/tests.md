# Running Tests

Press runs its test suite inside the `shell` Docker container (see the
[architecture](../reference/architecture.md) reference for an overview of the
environment). From the project root you can execute:

```bash
r pytest
```

This command invokes `pytest` within the container so the tests run in the same
environment used for development and CI.

The suite relies on the `nginx-test` service defined in `docker-compose.yml`.
This container runs a private Nginx instance without exposing port 80, allowing
HTTP checks to run without disturbing other services that might need the default
web port.

Link checks use the `TEST_HOST_URL` environment variable to decide which host to
scan. `docker-compose` sets it to `http://nginx-test` so the tests talk to the
private Nginx container, but you can override it to point at another server
(for example, `TEST_HOST_URL=http://localhost:8080 r pytest`).

To check test coverage for the `pie` package and generate an HTML report, run:

```bash
r cov
```

The `cov` target runs `pytest --cov=pie --cov-report=html:/data/log/cov --cov-report=term-missing` inside the container. The
HTML report is written to `log/cov` in the project root (mounted as `/data/log/cov` inside the container).
