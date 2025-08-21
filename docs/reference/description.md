# Description Metadata and Global

The `description` field stores a short Markdown snippet for a document. The
text may include Jinja syntax. When the `description` global is invoked with a
metadata dictionary or id, the snippet is rendered through Jinja using the
current environment and returned as Markdown.

Example metadata:

```yaml
description: "See {{ link('intro') }} for details."
```

Template usage:

```jinja
{{ description('intro') }}
```

The global expands the Jinja code and returns the processed snippet.
