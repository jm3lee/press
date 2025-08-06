# gen-markdown-index

Generate a Jinja formatted list from `index.json`. The fields available in the index are described in [Metadata Fields](../reference/metadata-fields.md).

```
usage: gen-markdown-index <index.json>
```

The command reads the JSON index file produced by `build-index` and prints a
bullet list where each item is a Jinja expression. When a metadata entry
provides a `link.tracking` value it is preserved so the rendered HTML uses
`rel="noopener noreferrer"` and `target="_blank"` when set to `false`.
Entries are sorted by the `name` field and icons are included when present.

Example output:

```jinja
- {{ {"citation": "Example", "url": "/ex", "link": {"tracking": false}} | linktitle }}
```

## gen-markdown-index-2

`gen-markdown-index-2` walks a directory tree of YAML metadata files and prints a
Markdown list. To exclude an item from the output, set
`gen-markdown-index-2.show` to `false` in its metadata. When a directory is
hidden this way, its children are still processed at the same indentation level.
