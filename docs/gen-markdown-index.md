# gen-markdown-index

`gen-markdown-index` reads `index.json` produced by `build-index` and prints a simple Markdown list linking to each document. This can be redirected to create an overview page.

## Usage

```bash
gen-markdown-index build/static/index.json > build/README.md
```

The command expects a single argument – the path to the JSON index. It outputs one bullet point per entry in alphabetical order by identifier, using either the `title` or `name` field as the link text.

### Example Output

```markdown
- [Quickstart](/quickstart.html)
- [Study Guide](/study.html)
```

This utility is primarily for generating a lightweight site map that can be included in other pages or served directly.
