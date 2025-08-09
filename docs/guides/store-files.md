# store-files Script

`store-files` moves assets into the local S3 staging area and creates matching metadata entries.

## Usage

```bash
store-files [-n LIMIT] <path>
```

- `path` may point to a single file or a directory; directories are processed recursively.
- `-n LIMIT` optionally restricts how many files are handled in one run.

Each processed file is:

1. Assigned a random identifier.
2. Moved to `s3/v2/files/0/<id>`.
3. Given a YAML metadata file at `src/static/files/<id>.yml` containing `id`, `author`, `pubdate`, and `url` fields.

Progress information is logged to the console and can be redirected using the standard `--log` option.
