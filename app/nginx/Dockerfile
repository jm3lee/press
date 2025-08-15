FROM nginx:alpine-slim

# Allows specifying which nginx configuration file to include at build time.
ARG NGINX_CONF=app/nginx/default.conf

# Include the chosen configuration in the image so it works without a volume
# mount.
COPY ${NGINX_CONF} /etc/nginx/conf.d/default.conf

COPY ./build /usr/share/nginx/html
