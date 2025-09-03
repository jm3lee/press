# include-filter Utility

`include-filter` processes Markdown files and expands inline Python directives.

Typical usage chains the command multiple times in the project `makefile` to
resolve nested includes before rendering.

It resolves custom `include()` calls and renders Mermaid diagrams during
preprocessing. Any links ending with `.md` are automatically rewritten to
point at the corresponding `.html` file.

The command is installed from the `pie` Python package and exposes a simple
CLI:

```bash
include-filter <output-dir> <input> <output>
```

- `<output-dir>` – directory for any generated assets such as diagram images
- `<input>` – source Markdown file containing Python fences
- `<output>` – destination file that receives the transformed Markdown

Repository examples:

- `src/include-filter/index.md` demonstrates `include_deflist_entry` gathering
  entries from multiple directories.
- `src/examples/diagram.mmd` contains a Mermaid block rendered by the filter.
- `src/include-filter/a.md` is a simple file you can pull in with `include()`.

## Functions

- `include(path)` – insert another Markdown file
- `include_deflist_entry(*paths, glob='*', sort_fn=None)` – build definition
  list entries
- `mermaid(file, alt, id)` – convert a Mermaid code block into an image link

## include

Insert another Markdown file and adjust its heading levels to fit the current
document.

### Example

```markdown
```python
include("src/include-filter/a.md")
```
```

## include_deflist_entry

Insert Markdown files as definition list entries using their `title` metadata.
Metadata is retrieved from Redis via `get_metadata_by_path()` and the resulting
title is followed by a `#` that links to the entry's `url` when available.

Each argument may be a file or directory.
Multiple paths can be provided to gather entries from different locations.
Directories are searched recursively for files matching `glob` and processed in
alphabetical order by default.
A custom `sort_fn` can be provided to override the ordering.

See `src/include-filter/index.md` for a complete example.

### Example

```markdown
<dl>
```python
# combine entries from two directories using include_deflist_filter
include_deflist_entry(
    "src/include-filter",
    "docs/reference",
    glob="*.md",
)
```
</dl>
```

## mermaid

Convert a Mermaid code block into an image using `mmdc` and emit a Markdown
image link.

### Example

```markdown
```python
mermaid("src/examples/diagram.mmd", "Example diagram", "diagram")
```
```
