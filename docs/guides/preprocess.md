# preprocess Script

`preprocess` prepares Markdown files for rendering. It expands includes,
internal links, and emojifies the text. The output mirrors the directory
structure under `build/` so that `src/foo/bar.md` becomes
`build/foo/bar.md`.

## Usage

```bash
preprocess <markdown-file> [more-files...]
```

Each input file is processed in place:

1. **Expand includes** – `include-filter` runs three times to resolve nested
   `include()` blocks and render Mermaid diagrams.
2. **Render links** – `render-jinja-template` converts special link syntax
   using metadata from Redis.
3. **Emoji conversion** – `emojify` replaces `:emoji:` codes with Unicode
   characters.

### Makefile Integration

The project's `makefile` invokes `preprocess` when building `.md` targets:

```make
build/%.md: %.md | build
    preprocess $<
```

Running `preprocess src/guide/intro.md` will create
`build/guide/intro.md` ready for rendering.

