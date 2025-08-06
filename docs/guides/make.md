# make

The `make` script runs `make` inside the Docker Compose `shell` service. It ensures
that the build environment matches the containerized setup and that generated
files are owned by your user.

## Usage

```bash
make [MAKE_TARGETS]
```

All arguments are forwarded to `make` running in the container.

### Example

```bash
make all
```

The script uses your current UID when starting the container and removes the
container after `make` completes.

### Cleaning Build Artifacts

Use `remake` to delete targets before rebuilding:

```bash
remake build webp
```
