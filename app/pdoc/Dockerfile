######################################################################
# PIE documentation server image
#
# The pdoc container hosts API documentation for the PIE Python package.
# It installs the same dependencies used in development and exposes the
# auto-generated site via pdoc's built-in web server.
######################################################################

# Start from the slim Python base to reduce image size while retaining pip
# and build tooling.
FROM python:3.11-slim

WORKDIR /pie

# Install pdoc along with the PIE package dependencies to ensure modules
# import correctly when documentation is generated.
COPY app/shell/py/pie/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir pdoc \
    && pip install --no-cache-dir -r /tmp/requirements.txt

# Expose the port used by pdoc's HTTP server and configure the entrypoint to
# render the PIE package docs on demand.
EXPOSE 8080
ENTRYPOINT ["pdoc", "-h", "0.0.0.0", "-p", "8080", "pie"]
