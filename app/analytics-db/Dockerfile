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
RUN apk add s3cmd
RUN apk add --no-cache python3 py3-pip postgresql-client
RUN pip install --no-cache-dir --break-system-packages psycopg[binary] pandas
COPY ./app/analytics-db/s3cfg /root/.s3cfg
COPY ./app/analytics-db/bin/ /root/bin/
