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

# Update package index quietly to fetch latest package lists
RUN apt update -qq

# Install locales package first (changes less often than other tools,
# so placing it early saves rebuild time when other layers change).
RUN apt install -y --no-install-recommends locales

# -------------------------------------------------------------------
# Locale configuration
# -------------------------------------------------------------------

# Enable en_US.UTF-8 locale for consistent UTF-8 support
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen \
 && locale-gen

# Set environment variables for UTF-8 encoding
ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8

# -------------------------------------------------------------------
# Install build and utility tools
# -------------------------------------------------------------------

# Install GNU Make for build automation
RUN apt install -y --no-install-recommends make

# Install HTML/CSS/JS minifier
RUN apt install -y --no-install-recommends minify

# Install Jinja2 for Python templating
RUN apt install -y --no-install-recommends python3-jinja2

# Install linkchecker to validate links in generated sites
RUN apt install -y --no-install-recommends linkchecker

# Clean up apt cache to reduce image size
RUN rm -rf /var/lib/apt/lists/*

# -------------------------------------------------------------------
# Python filters and backends
# -------------------------------------------------------------------

# Copy Press Python libraries into the image. Users can override by mounting /press/py.
COPY ./py /press/py

# Install includefilter plugin in editable mode
RUN pip install --break-system-packages -e /press/py/includefilter

# Install pie plugin in editable mode
RUN pip install --break-system-packages -e /press/py/pie

# Install Xmera backend dependencies
RUN pip install --break-system-packages -r /press/py/xmera/backend/requirements.txt

# Install Xmera backend plugin in editable mode
RUN pip install --break-system-packages -e /press/py/xmera/backend

# -------------------------------------------------------------------
# Custom helper scripts and makefiles
# -------------------------------------------------------------------

# Copy custom shell scripts into /app/bin and ensure they're in PATH
COPY ./bin/ /app/bin
ENV PATH="/app/bin:${PATH}"

# Copy custom Makefile fragments into /app/mk
COPY ./mk/ /app/mk
