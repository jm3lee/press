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
