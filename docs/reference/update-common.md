# update-common

Shared helpers for the metadata update scripts.

The module provides utilities used by command line tools such as
`update-author` and `update-pubdate`:

- `get_changed_files()` – return a list of tracked files modified in git.
- `replace_field(fp, field, value)` – replace a metadata field in YAML or
  Markdown frontmatter.
- `update_files(paths, field, value)` – update a metadata field across the
  Markdown/YAML pair associated with each path.

These helpers centralize behavior that was previously duplicated across the
individual update scripts.
