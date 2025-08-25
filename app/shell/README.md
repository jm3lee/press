# Shell Service

The `shell` directory defines the Docker image that provides the build and test
environment for Press.

## Layout

- `Dockerfile` – base image with build tools like Pandoc and Make.
- `mk/` – Makefiles executed inside the container.
- `bin/` – helper scripts invoked during the build.
- `py/` – Python utilities and their tests.

## Usage

The top-level `redo.mk` file builds this image and then invokes the root
`makefile` inside it. Targets can be run from the host with
`make -f redo.mk <target>` or directly inside the container with `make`.
Open an interactive container with:

```bash
make -f redo.mk shell
```

Run the test suite inside the container with:

```bash
make -f redo.mk test
# or inside the container
make test
```
