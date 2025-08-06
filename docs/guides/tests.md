# Running Tests

Press runs its test suite inside the `shell` Docker container. From the project
root you can execute:

```bash
r pytest
```

This command invokes `pytest` within the container so the tests run in the same
environment used for development and CI.

To check test coverage for the `pie` package, run:

```bash
r cov
```

The `cov` target runs `pytest --cov=pie` inside the container and prints a
coverage report.
