# Jinja Global Functions

The template environment provides several helper functions that can be invoked
from any Jinja template. They expose metadata from the build index or offer
small utilities used during rendering. See [Metadata Fields](metadata-fields.md)
for details on the structure of this metadata.

## Available Globals

- `get_origins(name)` – yield origin strings for the given key.
- `get_insertions(name)` – yield insertion strings for the key.
- `get_actions(name)` – yield action descriptions.
- `get_translations(name)` – iterate over translation pairs.
- `render_jinja(snippet)` – render a snippet of text using the same environment.
- `to_alpha_index(i)` – convert `0`–`3` to `a`–`d`.
- `read_json(path)` – read and parse a JSON file.
- `read_yaml(path)` – read YAML and yield the sequence stored under `toc`.

These helpers live in `dist/app/shell/py/pie/pie/render_jinja_template.py` and are
registered with the Jinja environment by `create_env()`.

