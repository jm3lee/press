FROM pandoc/extra:latest-ubuntu

# Install locales, linkchecker, avoid extra packages.
RUN apt update -qq
RUN apt install -y --no-install-recommends locales
RUN rm -rf /var/lib/apt/lists/*

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

# Add includefilter.
COPY ./includefilter /app/shell/includefilter
RUN pip install --break-system-packages -e /app/shell/includefilter
