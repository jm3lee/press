# gen-markdown-index

`gen-markdown-index` walks a directory tree of YAML metadata files and prints a Markdown list.

```
usage: gen-markdown-index [ROOT_DIR]
```

`ROOT_DIR` defaults to the current directory. To exclude an item from the output, set `indextree.show` to `false` in its metadata. To omit a link, set `indextree.link` to `false`. When a directory is hidden this way, its children are still processed at the same indentation level.
