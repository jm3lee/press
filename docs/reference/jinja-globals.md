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
- `cite(*ids)` – format one or more metadata entries as Chicago style
  citations. When multiple entries share the same author and year their page
  numbers are combined.
- `link(desc, anchor=None)` and related helpers `linktitle`, `linkcap`,
  `link_icon_title`, `linkicon`, and `linkshort` – format metadata into HTML
  anchors. See [link-globals.md](link-globals.md) for details.

Example:

```jinja
{{ cite("hull", "doe") }}
```

These helpers live in `app/shell/py/pie/pie/render/jinja.py` and are
registered with the Jinja environment by `create_env()`.

