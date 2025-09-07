# migrate-metadata

Move legacy top-level `author`, `pubdate`, `link`, `title`, `citation`, and
`header_includes` fields under the `doc` mapping and `html.extras`.
This script scans the provided files or directories and rewrites Markdown
front matter and YAML metadata in place.

```bash
migrate-metadata PATH [PATH...]
```

Each updated file is printed as `<path>: migrated` and logged to
`log/migrate-metadata.txt` unless a different log path is supplied via the
standard `--log` option. After processing, a summary reports how many files
were checked and changed.
