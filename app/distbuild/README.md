# Distributed Build Prototype

This directory provides a minimal master/worker build system driven entirely
over SSH. The master node dispatches commands to workers using
[Fabric](https://www.fabfile.org/) (Paramiko/SSH).

## Components

- `py/distbuild/cli.py` – console entrypoint that relays jobs to the worker.
- `py/distbuild/worker.py` – helper module providing `execute_commands` used by
  the master.
- `Dockerfile.master` and `Dockerfile.worker` – container images running an SSH
  daemon for the master and worker nodes.
- `tests/` – unit tests for the worker module.
- `bin/distbuild` – host helper script that invokes the master over SSH.

## Usage

1. Build and start the services:

   ```bash
   docker compose up -d build-master build-worker
   ```

2. Render a Markdown file with pandoc through the master:

   ```bash
   ./app/distbuild/bin/distbuild "pandoc README.md -o README.html"
   ```

   The resulting `README.html` will be written to the repository root.

Fresh SSH keys are generated for both containers on each build. The master
connects to workers listed in the `WORKER_HOSTS` environment variable and uses a
simple round-robin load balancer that favors remote workers before falling back
to local execution.

The `Dockerfile.master` and `Dockerfile.worker` both run the same `ssh-keygen`
steps. Docker's layer cache reuses the generated key material across the two
images, so the master and worker end up sharing an identical key pair. The
master's private key (`/root/.ssh/id_rsa`) matches the public key preloaded into
the worker's `authorized_keys`, enabling passwordless SSH between the nodes.
