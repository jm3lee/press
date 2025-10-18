# syntax=docker/dockerfile:1.7
######################################################################
# S3 utility image
#
# This container provides the s3cmd CLI and its configuration for running
# backup and asset-sync tasks from CI. It intentionally remains minimal so
# jobs start quickly.
######################################################################

# Use Debian testing to get recent s3cmd releases without building from
# source.
FROM debian:testing-slim

# Refresh package metadata and install the S3 tooling plus CA certificates
# for TLS validation.
RUN apt update -qq
RUN apt install -y --no-install-recommends s3cmd
RUN apt-get install -y ca-certificates

# Remove apt caches to keep the final image size lean.
RUN rm -rf /var/lib/apt/lists/*

# Provide helper scripts and the default s3cmd configuration.
COPY ./bin /app/bin
COPY ./root/.s3cfg /root/.s3cfg
