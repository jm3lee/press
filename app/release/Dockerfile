# syntax=docker/dockerfile:1.7
######################################################################
# Production site image
#
# The release container layers site assets on top of the press-shell base
# image produced by the development tooling. This keeps the runtime
# environment consistent between build and deploy steps.
######################################################################

# Reuse the press-shell image so Python, Node, and other build dependencies
# are already installed.
FROM press-shell

# Copy the compiled JavaScript bundle and shared Jinja macro into the
# locations expected by the running site.
COPY ./build/static/js/ /press/static/js/
COPY ./src/templates/macros.jinja /press/templates/macros.jinja
