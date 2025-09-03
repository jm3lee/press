# -------------------------------------------------------------------
# Press Shell Docker Container
#
# This Dockerfile aggregates shell utilities and build tools into a
# single container, minimizing the number of Docker images and
# containers required to build a site.
# -------------------------------------------------------------------

# Base image: lightweight Python runtime
FROM python:3.11-slim

# -------------------------------------------------------------------
# System preparation
# -------------------------------------------------------------------
# Install core utilities, Node.js and clean up afterwards
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends \
        curl \
        git \
        linkchecker \
        locales \
        make \
        minify \
        openssh-server \
        pysassc && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    mkdir -p /run/sshd

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
# Python dependencies
# -------------------------------------------------------------------
RUN pip install --no-cache-dir --break-system-packages \
        markdown2 \
        jinja2

# Copy Press Python libraries into the image. Users can override by mounting
# /press/py
COPY ./py/pie /press/py/pie

RUN pip install --no-cache-dir --break-system-packages \
        -e /press/py/pie \
        -r /press/py/pie/requirements.txt

# -------------------------------------------------------------------
# Custom helper scripts and makefiles
# -------------------------------------------------------------------
# Add helper scripts to PATH
COPY ./bin/ /app/bin
ENV PATH="/app/bin:${PATH}"
