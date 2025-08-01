---
title: Include Filter Examples
author: Brian Lee
id: include-filter
citation: include filter
---

The `include-filter` tool lets you embed other Markdown files and diagrams.

## include

The snippet below pulls in a prebuilt fragment from `build/static/index/dist.md` at build time.

```python
include("build/static/index/dist.md")
```

## include_deflist_entry

This variant inserts another Markdown file as a definition list entry:

<dl>
```python
include_deflist_entry("src/dist/include-filter/a.md")
include_deflist_entry("src/dist/include-filter/b.md")
```
</dl>

## mermaid

The `mermaid` helper converts a Mermaid diagram into an image.

```python
mermaid("src/examples/diagram.mmd", "Example diagram", "#flow-example")
```

