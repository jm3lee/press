# Jinja Global Functions

The template environment provides several helper functions that can be invoked
from any Jinja template. They expose metadata from the build index or offer
small utilities used during rendering. See [Metadata Fields](metadata-fields.md)
for details on the structure of this metadata.

## Available Globals

- `render_jinja(snippet)` – render a snippet of text using the same environment.
- `to_alpha_index(i)` – convert `0`–`3` to `a`–`d`.
- `read_json(path)` – read and parse a JSON file.
- `read_yaml(path)` – read YAML and yield the sequence stored under `toc`.
- `linkparent(id)` – render `Parent: <a …>` pointing to a parent page. When
  called without an argument it uses the current page's `parent` metadata; pass
  an explicit `id` to override.
- `cite(*ids)` – format one or more metadata entries as Chicago style
  citations. When multiple entries share the same author and year their page
  numbers are combined.

These helpers live in `app/shell/py/pie/pie/render_jinja_template.py` and are
registered with the Jinja environment by `create_env()`.

Example usage of `linkparent`:

```jinja
{{ linkparent() }}
{{ linkparent("manual") }}
```

