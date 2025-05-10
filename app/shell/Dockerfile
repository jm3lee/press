# Dockerfile for creating a Debian-based image with linkchecker installed
#
# This image installs locales and linkchecker on top of debian:testing-slim,
# configures UTF-8 locale support, and copies custom scripts into /usr/local/bin.
#
# Usage:
#   docker build -t my-linkchecker-image .
#   docker run --rm my-linkchecker-image linkchecker https://example.com
#
# Environment Variables:
#   LANG        Set to en_US.UTF-8 to ensure UTF-8 support.
#   LANGUAGE    Set to en_US:en for fallback language resolution.
#   LC_ALL      Set to en_US.UTF-8 to enforce the chosen locale.

FROM debian:testing-slim

# Install locales, linkchecker, avoid extra packages.
RUN apt update -qq
RUN apt install -y --no-install-recommends locales
RUN apt install -y --no-install-recommends linkchecker
RUN rm -rf /var/lib/apt/lists/*

# Enable the en_US.UTF-8 locale
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen \
 && locale-gen

# Set UTF-8 environment variables for proper encoding support
ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8

# Copy custom helper scripts into the image
COPY ./bin/* /usr/local/bin/
