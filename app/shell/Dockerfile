FROM pandoc/extra:latest-ubuntu

# Install extra tools
RUN apt update -qq
RUN apt install -y --no-install-recommends locales
RUN apt install -y --no-install-recommends make
RUN apt install -y --no-install-recommends minify
RUN apt install -y --no-install-recommends python3-jinja2
RUN rm -rf /var/lib/apt/lists/*

# Add includefilter.
# Don't install from /app since users can map this path to override the default
# behavior.
COPY ./includefilter /press/includefilter
RUN pip install --break-system-packages -e /press/includefilter

# Enable the en_US.UTF-8 locale
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen \
 && locale-gen

# Set UTF-8 environment variables for proper encoding support
ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8

# Copy custom helper scripts into the image
COPY ./bin/ /app/bin
ENV PATH="/app/bin:${PATH}"

# Copy makefiles
COPY ./mk/ /app/mk
