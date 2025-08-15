# Nginx Dockerfile

The `app/nginx/Dockerfile` builds a minimal image for serving the static site.
It starts from `nginx:alpine-slim`, copies the generated `build/` directory
into Nginx's default web root, and installs a production config that also
includes any generated redirects. Both the `nginx` and `nginx-dev` services in
`docker-compose.yml` use this image.

```Dockerfile
FROM nginx:alpine-slim
COPY ./build /usr/share/nginx/html
COPY ./app/nginx/prod.conf /etc/nginx/conf.d/default.conf
```

### Build and run

To test the container directly:

```bash
docker build -f app/nginx/Dockerfile -t press-nginx .
docker run -p 80:80 press-nginx
```

During development `nginx-dev` mounts `./build` so pages update automatically.
For production, build the image and run the `nginx` service.

### Redirects

When a document's `url` metadata differs from its derived path, the build step
creates `build/redirects.conf` containing `rewrite` rules. Both
`app/nginx/default.conf` (for local testing) and `app/nginx/prod.conf` include this file:

```nginx
include /usr/share/nginx/html/redirects.conf;
```

Mount `app/nginx/default.conf` for development or rely on the `prod.conf` bundled in
the image to serve permanent redirects.

You can also run `r docker` to build and push the image to your configured
registry. See [DigitalOcean Setup](digitalocean.md) for an example.
