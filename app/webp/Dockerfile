# syntax=docker/dockerfile:1.7
######################################################################
# WebP conversion service image
#
# This Dockerfile builds the runtime used by the background worker that
# converts uploaded images to WebP. Only the utilities required for the
# conversion pipeline are installed to keep the image small.
######################################################################

# Start from the slim Debian testing base to access a recent ImageMagick
# build with WebP support without pulling in unnecessary packages.
FROM debian:testing-slim

# Refresh package metadata before installing dependencies.
RUN apt update -qq

# Install ImageMagick for the conversion and jpegoptim to losslessly
# compress JPEG inputs prior to converting them to WebP. Using
# --no-install-recommends keeps the layer focused on the essentials.
RUN apt install -y --no-install-recommends imagemagick
RUN apt install -y --no-install-recommends jpegoptim

# Remove cached package metadata to keep the final image lean.
RUN rm -rf /var/lib/apt/lists/*

# Copy the conversion service entrypoint into the container. The script
# polls the input directory and runs the conversion workflow.
COPY ./bin/service /app/bin/service
