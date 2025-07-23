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
- `mermaid(file, alt, id)` – convert a Mermaid code block into an image using
  `mmdc` and emit a Markdown image link

Any links ending with `.md` are automatically rewritten to point at the
corresponding `.html` file.

Typical usage in `app/shell/mk/build.mk` chains the command multiple times to
resolve nested includes before passing the final Markdown to Pandoc.
