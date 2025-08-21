# Definition Metadata and Global

The `definition` field stores a short Markdown snippet for a document. The
text may include Jinja syntax. When the `definition` global is invoked with a
metadata dictionary or id, the snippet is rendered through Jinja using the
current environment and returned as Markdown.

Example metadata:

```yaml
definition: "See {{ link('intro') }} for details."
```

Template usage:

```jinja
{{ definition('intro') }}
```

The global expands the Jinja code and returns the processed snippet.
