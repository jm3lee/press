FROM debian:testing-slim
RUN apt update -qq
RUN apt install -y --no-install-recommends s3cmd
RUN apt-get install -y ca-certificates
RUN rm -rf /var/lib/apt/lists/*
COPY ./bin /app/bin
COPY ./root/.s3cfg /root/.s3cfg
