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

- `src/examples/diagram.mmd` contains a Mermaid block rendered by the filter.
- `src/examples/include-filter/a.md` is a simple file you can pull in with
  `include()`.

## Functions

- `include(path)` – insert another Markdown file
- `mermaid(file, alt, id)` – convert a Mermaid code block into an image link

## include

Insert another Markdown file and adjust its heading levels to fit the current
document.

### Example

```markdown
```python
include("src/examples/include-filter/a.md")
```
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
