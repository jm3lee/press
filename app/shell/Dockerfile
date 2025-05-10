FROM debian:testing-slim

# Install locales
RUN apt update -qq
RUN apt install -y --no-install-recommends locales
RUN apt install -y --no-install-recommends linkchecker
RUN rm -rf /var/lib/apt/lists/*

# Enable the UTF-8 locale
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen \
 && locale-gen

# Set environment variables
ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8

COPY ./bin/* /usr/local/bin/
