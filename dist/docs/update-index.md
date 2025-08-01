# update-index

Load a JSON index and insert each value into DragonflyDB or Redis. Keys use a dot-separated format of `<id>.<property>` with nested objects and arrays flattened. Complex values are stored as JSON strings.

## Usage

- ```bash
update-index index.json [--host HOST] [--port PORT] [-l LOGFILE]
```

- `index` path to the JSON index file or a directory of metadata
- `--host` Redis host (default `localhost`)
- `--port` Redis port (default `6379`)
- `-l, --log` optional log file

When a directory is given, `update-index` scans recursively for `.md`, `.yml`, and `.yaml` files, processing each Markdown/YAML pair only once. The command expects an index produced by [`build-index`](build-index.md). Each entry is written to the configured Redis instance using separate keys.
