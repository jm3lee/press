# check-breadcrumbs

`check-breadcrumbs` verifies that each metadata file under `src/` defines a
`breadcrumbs` array. It exits with a non-zero status when a file lacks the
field. Messages are logged to `stderr` and written to
`log/check-breadcrumbs.txt`.

## Usage

```bash
check-breadcrumbs [directory] [-x EXCLUDE]
```

If no directory is given, `src/` is assumed. The command logs errors for files
that fail the check and returns `1` when a problem is found. The default
exclude file `cfg/check-breadcrumbs-exclude.yml` is used when present. Use
`-x`/`--exclude` to provide a YAML file listing metadata files to skip. Paths
may be absolute or relative to the directory being scanned. Entries may include
wildcards or regular expressions prefixed with `regex:`.

