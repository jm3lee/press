# Shell Service

The `shell` directory defines the Docker image that provides the build and test environment for Press.

## Layout

- `Dockerfile` – base image with build tools like Pandoc and Make.
- `mk/` – Makefiles executed inside the container.
- `bin/` – helper scripts invoked during the build.
- `py/` – Python utilities and their tests.

## Usage

The top-level Makefile `redo.mk` builds this image and runs `app/shell/mk/build.mk` inside it. Open an interactive container with:

```bash
make -f redo.mk shell
```

Run the test suite inside the container with:

```bash
make -f redo.mk pytest
```
