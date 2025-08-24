FROM python:3.11-slim

WORKDIR /pie

# Install pdoc and dependencies for pie
COPY app/shell/py/pie/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir pdoc \
    && pip install --no-cache-dir -r /tmp/requirements.txt

EXPOSE 8080
ENTRYPOINT ["pdoc", "-h", "0.0.0.0", "-p", "8080", "pie"]
