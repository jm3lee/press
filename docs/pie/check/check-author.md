# check-author

`check-author` ensures that every metadata file found under the target tree
defines a `doc.author` field. The checker inspects Markdown/YAML pairs using
`pie.metadata.load_metadata_pair` so front matter and sidecar YAML are merged
before validation. Results are logged to `stderr` and appended to
`log/check-author.txt` by default.

## Usage

```bash
check-author [directory]
```

When no directory is supplied the command scans `src/`. The checker walks the
filesystem looking for `*.md`, `*.yml`, and `*.yaml` files and groups matching
Markdown/YAML pairs to avoid duplicate warnings. For each metadata document, the
checker verifies that `doc.author` is defined and non-empty. Missing authors are
reported as errors; the process exits with status `1` when any are found.

Use `-l`/`--log` to change the log destination and `-v`/`--verbose` to emit
per-file debug messages describing the detected author values. Pass
`--exclude` (or `-x`) to provide a YAML file listing metadata entries to skip.
When no flag is supplied the checker loads `cfg/check-author-exclude.yml` if
the file exists. Paths may be absolute or relative to the scanned directory
and can include shell-style wildcards or regular expressions prefixed with
`regex:`.

### Example exclude file

```yaml
- news/archive/doc.yml
- regex:.*drafts/.*
```
