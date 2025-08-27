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

### Custom checkers

Run additional validators by mounting a module and a YAML file listing the
checks:

```bash
docker compose run --rm \
  -v "$PWD/mychecks.py":/press/mychecks.py \
  -v "$PWD/extra.yml":/press/cfg/check-extra.yml \
  press-release \
  make check
```

The file contains `module:function` pairs, one per line. Each referenced
function runs after the built-in checks.
