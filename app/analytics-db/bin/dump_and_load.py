#!/usr/bin/env python3
# Streaming COPY → pandas in batches (memory-safe) with psycopg v3

import codecs
import csv
import io
import json
import os

import pandas as pd
import psycopg

# Connection string (override with env PGURL if you like)
PGURL = os.getenv("PGURL", "postgresql://analytics:analytics@localhost:5432/analytics")

# Adjust WHERE for your window to leverage Timescale chunk pruning
SQL = """
COPY (
  SELECT id,
         site,
         session_id::text AS session_id,
         event_type,
         target,
    to_char(occurred_at AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"') AS occurred_at,
    to_char(received_at AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"') AS received_at,
         meta
  FROM public.engagement_events
  -- WHERE occurred_at >= now() - interval '30 days'
  ORDER BY occurred_at, id
) TO STDOUT WITH (FORMAT csv, HEADER true)
"""


def copy_text_lines(cur, sql: str, chunk_bytes: int = 1 << 20):
    """
    Yield decoded text lines from a psycopg v3 COPY stream.
    Uses an incremental UTF-8 decoder to avoid splitting multibyte chars.
    """
    decoder = codecs.getincrementaldecoder("utf-8")()
    tail = ""
    with cur.copy(sql) as cpy:
        while True:
            b = cpy.read()  # bytes
            if not b:
                break
            text = decoder.decode(b)
            chunk = tail + text
            *lines, tail = chunk.split("\n")
            for line in lines:
                yield line
        # flush any remaining decoded bytes
        rest = decoder.decode(b"", final=True)
        if rest:
            tail += rest
    if tail:
        yield tail


def dataframes_from_copy(cur, sql: str, batch_rows: int = 200_000):
    """
    Stream CSV rows from COPY, yield pandas DataFrames of size batch_rows.
    """
    lines = copy_text_lines(cur, sql)
    header_line = next(lines)  # first line is header
    fieldnames = next(csv.reader([header_line]))
    batch = []
    for line in lines:
        if not line:
            continue
        values = next(csv.reader([line]))
        row = dict(zip(fieldnames, values))
        # parse jsonb lazily
        row["meta"] = json.loads(row["meta"]) if row.get("meta") else {}
        batch.append(row)
        if len(batch) >= batch_rows:
            yield pd.DataFrame.from_records(batch)
            batch.clear()
    if batch:
        yield pd.DataFrame.from_records(batch)


def load():
    dfs = []
    with psycopg.connect(PGURL, autocommit=True) as conn, conn.cursor() as cur:
        # If you use compressed chunks:
        conn.execute("SET timescaledb.enable_transparent_decompression=on")
        for part in dataframes_from_copy(cur, SQL, batch_rows=200_000):
            # dtypes & timestamp parsing per-batch to keep memory bounded
            part["occurred_at"] = pd.to_datetime(part["occurred_at"], utc=True)
            part["received_at"] = pd.to_datetime(part["received_at"], utc=True)
            part = part.astype(
                {
                    "id": "Int64",
                    "site": "string",
                    "session_id": "string",
                    "event_type": "string",
                    "target": "string",
                }
            )
            dfs.append(part)

    global df
    df = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()


# For use in ipython
df = load()
