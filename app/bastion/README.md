# Bastion Host

This image provisions an OpenSSH bastion host for internal development use.

## Building

The build copies a local authorized keys file into `/root/.ssh/authorized_keys`.
By default the Dockerfile copies `app/bastion/authorized_keys.example`. Supply a
custom file when running `docker build`:

```bash
docker build \
  --build-arg AUTHORIZED_KEYS_FILE=path/to/authorized_keys \
  -t press-bastion .
```

`AUTHORIZED_KEYS_FILE` must be relative to the repository root because the
compose file uses the repository as the build context.

## Running

The bastion service is available through docker compose:

```bash
docker compose up bastion
```

SSH listens on port `22` inside the container. The compose service exposes it as
`2222` on the host machine.
