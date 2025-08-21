# Distbuild

The `distbuild` package provides a CLI for dispatching commands to workers over SSH.

## Usage

Run the wrapper script from the host using Docker Compose:

```bash
docker compose exec build-master ./bin/distbuild <command>
```

All commands executed by `distbuild` start in the `/data` directory within the
`build-master` and `build-worker` containers.
