# gen-markdown-index

Generate a simple Markdown list from `index.json`.

```
usage: gen-markdown-index <index.json>
```

The command reads the JSON index file produced by `build-index` and prints
a bullet list of links sorted by the `name` field. If an entry contains
an `icon` value it is prefixed to the link text.
