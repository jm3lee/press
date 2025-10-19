# syntax=docker/dockerfile:1.7
######################################################################
# Analytics database image
#
# The analytics service persists metrics inside TimescaleDB. We reuse the
# upstream image so that database tuning and extension management stay in
# sync with the official Timescale releases.
######################################################################

# Pull the latest PostgreSQL 14 TimescaleDB image which includes the
# extension and recommended configuration out of the box.
FROM timescale/timescaledb:latest-pg14

RUN --mount=type=cache,target=/var/cache/apk,sharing=locked \
  apk add --no-cache s3cmd python3 py3-pip postgresql-client ipython

RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
  pip install --break-system-packages psycopg[binary] pandas

COPY ./app/flashoffer/analytics/db/bin/ /root/bin/
