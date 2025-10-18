# syntax=docker/dockerfile:1.7
######################################################################
# Static site nginx image
#
# This container serves the pre-built Press site. The Docker build embeds
# a chosen nginx configuration and the static artifact produced by the
# frontend pipeline so the image can run without external volumes.
######################################################################

# Use the lightweight Alpine-based nginx image since it already contains an
# optimized configuration for serving static files.
FROM nginx:alpine-slim

# Allows specifying which nginx configuration file to include at build time.
ARG NGINX_CONF=app/nginx/default.conf

# Include the chosen configuration in the image so it works without a volume
# mount.
COPY ${NGINX_CONF} /etc/nginx/conf.d/default.conf

# Copy built site and preserve timestamps for Last-Modified headers
COPY --link ./build /usr/share/nginx/html
