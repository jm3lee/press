# Jinja Globals for Link Formatting

Several build scripts provide custom Jinja globals that convert metadata
descriptions into HTML anchors. Each dictionary is pulled from
`index.json` and must include a `citation` field which supplies the anchor
text, along with a `url` field. Optional keys like `icon`,
`link.tracking`, and `link.class` customize the output.  For an overview of
these metadata fields, see [Metadata Fields](metadata-fields.md).

## `link`

The `link` global formats a metadata dictionary into an HTML anchor.  It
accepts a few optional parameters to control the output:

- `style` – controls capitalization of the citation text.  Use `"plain"`
  (default) to leave text unchanged, `"title"` for title‑case, or `"cap"` to
  capitalise only the first character.
- `use_icon` – when `True` (default) any `icon` field in the metadata is
  prefixed to the link text.  Set to `False` to suppress icons.
- `anchor` – appends a fragment identifier (`#anchor`) to the URL when provided.
- `citation` – selects which citation field to render.  The default `"citation"`
  uses the main citation value; pass `"short"` to use `citation.short`.

When the `citation` field is itself a mapping with `author`, `year`, and an
optional `page`, the helper formats the text using Chicago style
(`"Author Year, Page"`) and encloses it in parentheses, matching the behaviour
of the `cite` global.

Example:

```jinja
{{ link({"citation": "deltoid tuberosity", "url": "/humerus.html"},
         style="title", anchor="deltoid_tuberosity") }}
```

renders as:

```html
<a href="/humerus.html#deltoid_tuberosity" class="internal-link">Deltoid Tuberosity</a>
```

Bibliographic citations render similarly:

```jinja
{{ link({"citation": {"author": "hull", "year": 2016, "page": 307}, "url": "/hull"}) }}
```

produces:

```html
<a href="/hull" class="internal-link">(Hull 2016, 307)</a>
```

When you pass a string instead of a dictionary, the helper fetches the
corresponding metadata from Redis. The lookup retries a few times before
aborting so templates are more resilient when entries are added concurrently.

### Legacy helpers

Older globals such as `linktitle`, `linkcap`, `linkicon`, `link_icon_title`,
and `linkshort` remain available for backward compatibility but are now thin
wrappers around `link`.  They will be removed in a future release.

Example:

```jinja
{{ linktitle({"citation": "deltoid tuberosity", "url": "/humerus.html"},
             anchor="deltoid_tuberosity") }}
```

renders as:

```html
<a href="/humerus.html#deltoid_tuberosity" class="internal-link">Deltoid Tuberosity</a>
```

## `get_desc`

`get_desc` remains a Jinja filter. It looks up a description object from the
build index and returns the name unchanged if it is not present.

Example:

```jinja
{{ "hull" | get_desc }}
```

renders as:

```json
{{ "hull" | get_desc }}
```

## Migration script

The `update-link-filters` console script performs a best-effort rewrite of
legacy filter syntax into calls to these globals. It only handles simple
single-line patterns, so review the results and adjust complex cases manually.
