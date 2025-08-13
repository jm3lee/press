# store-files Script

`store-files` moves assets into the local S3 staging area and creates matching metadata entries.

## Usage

```bash
store-files [-n LIMIT] [-c CONFIG] <path>
```

- `path` may point to a single file or a directory; directories are processed recursively.
- `-n LIMIT` optionally restricts how many files are handled in one run.
- `-c CONFIG` path to a configuration file. Defaults to `cfg/store-files.yml` and is ignored if missing. When a path is explicitly supplied the command exits with an error if the file does not exist.

Each processed file is:

1. Assigned a random identifier.
2. Moved to `s3/v2/files/0/<id>`.
3. Given a YAML metadata file at `src/static/files/<id>.yml` rendered from the `metadata.yml.jinja` template containing
   `id`, `author`, `pubdate`, and `url` fields. The `url` is built from `{baseurl}/v2/files/0/{file_id}` where `baseurl` comes
   from the configuration file (defaulting to an empty string).

Progress information is logged to the console and can be redirected using the standard `--log` option.
