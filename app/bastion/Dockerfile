# syntax=docker/dockerfile:1
FROM debian:bookworm-slim

LABEL maintainer="press maintainers"

ARG AUTHORIZED_KEYS_FILE=app/bastion/authorized_keys.example

RUN apt-get update \
    && apt-get install --yes --no-install-recommends openssh-server \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/run/sshd /root/.ssh \
    && chmod 700 /root/.ssh

COPY app/bastion/sshd_config /etc/ssh/sshd_config

COPY ${AUTHORIZED_KEYS_FILE} /root/.ssh/authorized_keys
RUN chmod 600 /root/.ssh/authorized_keys

RUN ssh-keygen -A

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D", "-e"]
