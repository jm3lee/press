# Nginx Dockerfile

The `app/nginx/Dockerfile` builds a minimal image for serving the static site.
It starts from `nginx:alpine-slim` and copies the generated `build/` directory
into Nginx's default web root. Both the `nginx` and `nginx-dev` services in
`docker-compose.yml` use this image.

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
