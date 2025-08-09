# update-index

Insert index values into DragonflyDB or Redis.

The console script loads `index.json`, a metadata file, or scans a directory of
metadata files and flattens each document into `<id>.<property>` keys. Complex
values are stored as JSON strings. Source paths are recorded under
`<id>.path` and each path also maps back to the document `id`.

```bash
update-index PATH [--host HOST] [--port PORT] [-l LOGFILE]
```

- `PATH` path to `index.json`, a metadata file, or a directory of metadata
- `--host` Redis host (default `dragonfly` or `$REDIS_HOST`)
- `--port` Redis port (default `6379` or `$REDIS_PORT`)
- `-l, --log` optional log file

Values are inserted using pipelined writes and a summary of the number of files
processed and the elapsed time is logged. Environment variables `REDIS_HOST`
and `REDIS_PORT` are used when `--host` or `--port` are not supplied.
