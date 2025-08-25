Replace underscores with dashes in filenames and the `url` field of metadata
files changed in git.

The console script scans `git status --short` for paths under `src/` that have
been added or modified. Each matched file and its paired metadata are renamed by
substituting `-` for `_`. When a `url` field is present in the metadata, its
value is updated accordingly.

```bash
update-url [--sort-keys] [-l LOGFILE] [-v]
```

Renamed files and updated `url` fields are logged to `LOGFILE`. When not
provided, logs are written to `log/update-url.txt`. Use `--sort-keys` to write
YAML mappings with alphabetically sorted keys and `-v` for debug output.

A summary of the number of files checked and modified is written to the log
after processing.
