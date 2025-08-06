# Running Tests

Press runs its test suite inside the `shell` Docker container. From the project
root you can execute:

```bash
r pytest
```

This command invokes `pytest` within the container so the tests run in the same
environment used for development and CI.

To check test coverage for the `pie` package and generate an HTML report, run:

```bash
r cov
```

The `cov` target runs `pytest --cov=pie --cov-report=html:/data/log/cov --cov-report=term-missing` inside the container. The
HTML report is written to `log/cov` in the project root (mounted as `/data/log/cov` inside the container).
