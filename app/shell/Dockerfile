# -------------------------------------------------------------------
# Press Shell Docker Container
#
# This Dockerfile aggregates shell utilities and build tools into a
# single container, minimizing the number of Docker images and
# containers required to build a site.
# -------------------------------------------------------------------

# Base image: pandoc with extra scripts on Ubuntu
FROM pandoc/extra:latest-ubuntu

# -------------------------------------------------------------------
# System preparation
# -------------------------------------------------------------------
# Update package index and install required packages
RUN apt update -qq \
 && apt install -y --no-install-recommends \
        locales \
        make \
        minify \
        linkchecker

# Install curl to install nodejs
RUN apt install -y --no-install-recommends curl

# Install Node.js and npm
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
 && apt install -y --no-install-recommends nodejs

RUN rm -rf /var/lib/apt/lists/*

# -------------------------------------------------------------------
# Locale configuration
# -------------------------------------------------------------------
# Generate en_US locale for consistent UTF-8 support
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen \
 && locale-gen

# Set environment variables for UTF-8 encoding
ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8

# -------------------------------------------------------------------
# Python filters and backends
# Copy Press Python libraries into the image. Users can override by mounting
# /press/py
# -------------------------------------------------------------------
# Install library under development.
COPY ./py/pie /press/py/pie
RUN pip install --break-system-packages \
        -e /press/py/pie \
        -r /press/py/pie/requirements.txt

# -------------------------------------------------------------------
# Custom helper scripts and makefiles
# -------------------------------------------------------------------
# Add helper scripts to PATH
COPY ./bin/ /app/bin
ENV PATH="/app/bin:${PATH}"

# Copy additional Makefile fragments
COPY ./mk/ /app/mk
