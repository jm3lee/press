# update-index

Load a JSON index, metadata file, or directory of metadata and insert each value into DragonflyDB or Redis. Keys use a dot-separated format of `<id>.<property>` with nested objects and arrays flattened. Complex values are stored as JSON strings. When processing metadata files, the paths to the source files are recorded under `<id>.path` as a JSON array; this `path` array is stored unflattened. Each source path is also stored separately with the path as the key and the document `id` as the value for quick reverse lookups.

## Usage

- ```bash
update-index PATH [--host HOST] [--port PORT] [-l LOGFILE]
```

- `PATH` path to `index.json`, a metadata file, or a directory of metadata
- `--host` Redis host (default `dragonfly` or `$REDIS_HOST`)
- `--port` Redis port (default `6379` or `$REDIS_PORT`)
- `-l, --log` optional log file
- `-v, --verbose` show debug output

`update-index` also reads the `REDIS_HOST` and `REDIS_PORT` environment
variables when `--host` or `--port` are not specified.

## Python API

The `update-index` CLI is implemented in `pie.update.index`. Invoke it directly
when integrating with other Python code:

```python
from pie.update import index

index.main(["index.json"])
```

When a directory is given, `update-index` scans recursively for `.md`, `.yml`, and `.yaml` files, processing each Markdown/YAML pair only once. A single metadata file may also be supplied and is processed directly. When an index JSON file is provided, it should be produced by [`build-index`](build-index.md). Entries are written to the configured Redis instance using pipelined batch writes, with each value stored under its own key, including `id.path` entries pointing to the original files.
