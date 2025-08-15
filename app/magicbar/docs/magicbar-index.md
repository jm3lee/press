# magicbar-index

`magicbar-index` scans files or directories and builds a JSON navigation list for the MagicBar React component.

## Usage

```bash
magicbar-index [PATH ...] [-o OUTPUT]
```

- `PATH` can point to Markdown or YAML files or directories to search recursively.
- `-o`, `--output` choose the output filename (defaults to `magicbar.json`).
- `-v`, `-l` enable verbose logging or log file support via `pie`.

Each `.md`, `.yml`, or `.yaml` file should define `title` and `url` metadata. An optional `magicbar.shortcut` value is preserved for quick access.

Example:

```bash
magicbar-index docs -o src/magicbar/demo.json
```

This writes a sorted list of entries to `src/magicbar/demo.json` ready to be consumed by the MagicBar component.
