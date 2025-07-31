FROM debian:testing-slim
RUN apt update -qq
RUN apt install -y --no-install-recommends imagemagick
RUN apt install -y --no-install-recommends jpegoptim
RUN rm -rf /var/lib/apt/lists/*
COPY ./bin/service /app/bin/service
