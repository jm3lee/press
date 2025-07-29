# gen-markdown-index

`gen-markdown-index` walks a directory tree of YAML files and prints a
structured Markdown list. Each entry uses the `linktitle` Jinja filter to link
to the page identified by its `id`.

## Usage

```bash
gen-markdown-index [directory]
```

If no directory is supplied the current working directory is scanned. YAML files
must define `id` and `title` fields. Subdirectories are traversed recursively and
entries are sorted alphabetically by title.
