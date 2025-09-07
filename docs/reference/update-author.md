# update-author

Update the `doc.author` field in metadata files for documents modified in git
or within specified paths or glob patterns.

By default the console script scans `git status --short` for tracked files that
have been added or changed. When directories, files, or glob patterns are
provided, Markdown and YAML files matching those paths are examined instead.
For each file it locates the associated Markdown and YAML metadata pair using
`load_metadata_pair` and ensures the `doc.author` field is present. When a
metadata YAML file exists, the field is added or updated there and the Markdown
file is left untouched. Metadata is created if none exists. The value is taken
from `cfg/update-author.yml`, but can be overridden with the `--author` or `-a`
option when batch updating book excerpts, quotes, or other content.

```bash
update-author [-a AUTHOR] [--sort-keys] [-l LOGFILE] [-v] [PATH ...]
```

Each updated file is printed as `<path>: <old> -> <new>` and logged to
`LOGFILE`.  When not specified, log output is written to
`log/update-author.txt`. Pass `--sort-keys` to serialize YAML mappings with
keys in alphabetical order and `-v` to enable debug logging.

After processing, a summary of the number of files checked and modified is
printed to the console.

If a file under `src` is modified but no `doc.author` field can be updated, a
warning is logged.

