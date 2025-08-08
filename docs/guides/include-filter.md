# include-filter Utility

`include-filter` is a small helper that processes Markdown files and expands
inline Python directives. It is used by the build system to resolve custom
`include()` calls and to render Mermaid diagrams during preprocessing.

The command is installed from the `pie` Python package and exposes a simple
CLI:

```bash
include-filter <output-dir> <input> <output>
```

- `<output-dir>` – directory for any generated assets such as diagram images
- `<input>` – source Markdown file containing Python fences
- `<output>` – destination file that receives the transformed Markdown

Within fenced `python` blocks the following functions are available:

- `include(path)` – insert another Markdown file and adjust heading levels
- `include_deflist_entry(*paths, glob='*', sort_fn=None)` – insert Markdown
  files as definition list entries using their `title` metadata. Metadata is
  looked up via `get_cached_metadata()` and the resulting title is followed by a
  `#` that links to the entry's `url` when available. Each argument may be a
  file or directory. Directories are searched recursively for files matching
  `glob` and processed in alphabetical order by default. A custom `sort_fn` can
  be provided to override the ordering.
- `mermaid(file, alt, id)` – convert a Mermaid code block into an image using
  `mmdc` and emit a Markdown image link

Example:

```markdown
<dl>
```python
include_deflist_entry("src/include-filter", glob="*.md")
```
</dl>
```

Any links ending with `.md` are automatically rewritten to point at the
corresponding `.html` file.

Typical usage in `app/shell/mk/build.mk` chains the command multiple times to
resolve nested includes before passing the final Markdown to Pandoc.
