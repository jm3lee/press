# DigitalOcean Setup

The project pushes its Nginx image to DigitalOcean's container registry. Follow the [doctl install guide](https://docs.digitalocean.com/reference/doctl/how-to/install/) to set up the CLI and the [registry documentation](https://docs.digitalocean.com/products/container-registry/how-to/use-registry-docker-kubernetes/) for instructions on uploading images and using them with Kubernetes.

In `redo.mk`, `CONTAINER_REGISTRY` is set to `registry.digitalocean.com/artisticanatomy`. Authenticate before pushing with:

```bash
doctl auth init
doctl registry login
```

After logging in, run `r docker` to build and push the latest image.
