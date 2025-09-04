# update-pubdate

Update the `doc.pubdate` field in metadata files for documents modified in git.

The console script scans `git status --short` for tracked files that have been
added or changed. For each path it locates the associated Markdown and YAML
metadata pair using `load_metadata_pair` and ensures the `doc.pubdate` field is
present. When a metadata YAML file exists, the field is added or updated there
and the Markdown file is left untouched. When the field is missing it is added,
and metadata is created if none exists, using today's date in the format
`%b %d, %Y`.

```python
from pathlib import Path
from pie.metadata import load_metadata_pair

# Inspect the metadata for a document pair before it is updated
load_metadata_pair(Path("docs/post/index.yml"))
```

```bash
update-pubdate [--sort-keys] [-l LOGFILE]
```

Each updated file is printed as `<path>: <old> -> <new>` and the same
information is logged to `LOGFILE`. When omitted, log output is written to
`log/update-pubdate.txt`. Pass `--sort-keys` to serialize YAML mappings with
keys in alphabetical order.

When finished, the script reports how many files were checked and how many were
updated.

If a file under `src` is modified but no `doc.pubdate` field can be updated, a
warning is logged.
