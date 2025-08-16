# Nginx Dockerfile

The `app/nginx/Dockerfile` builds a minimal image for serving the static site.
It starts from `nginx:alpine-slim` and copies the generated `build/` directory
into Nginx's default web root. Both the `nginx` and `nginx-dev` services in
`docker-compose.yml` use this image.

The build process also creates a `permalinks.conf` file in the `build/` directory.
Nginx includes this file to redirect legacy URLs specified by a page's
`permalink` metadata to its canonical `url`. Debug logs from this step are
written to `log/nginx-permalinks.txt`.

```Dockerfile
FROM nginx:alpine-slim
COPY ./build /usr/share/nginx/html
```

### Build and run

To test the container directly:

```bash
docker build -f app/nginx/Dockerfile -t press-nginx .
docker run -p 80:80 press-nginx
```

During development `nginx-dev` mounts `./build` so pages update automatically.
For production, build the image and run the `nginx` service.

You can also run `r docker` to build and push the image to your configured
registry. See [DigitalOcean Setup](digitalocean.md) for an example.

### `nginx-test` for isolated testing

`docker-compose.yml` also defines an `nginx-test` service that uses the same
image without publishing any ports to the host. The test suite reaches this
container at `http://nginx-test`, providing a private Nginx instance for link
checks and other HTTP tests. Running a dedicated server prevents conflicts with
other applications that might need port&nbsp;80, making testing easier and more
robust.
The base URL comes from the `TEST_HOST_URL` environment variable, which defaults
to `http://nginx-test` but can be overridden to target a different host during
tests.
