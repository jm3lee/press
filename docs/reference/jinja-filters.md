# Jinja Filters for Link Formatting

Several build scripts provide custom Jinja filters that convert metadata
dictionaries into HTML anchors. Each dictionary is pulled from
`index.json` and must include a `citation` field which supplies the anchor
text, along with a `url` field. Optional keys like `icon`,
`link.tracking`, and `link.class` customize the output.  For an overview of
these metadata fields, see [Metadata Fields](metadata-fields.md).

## `link`

The `link` filter formats a metadata dictionary into an HTML anchor.  It
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
optional `page`, the filter formats the text using Chicago style
(`"Author Year, Page"`) and encloses it in parentheses, matching the behaviour
of the `cite` global.

Example:

```jinja
{{ {"citation": "deltoid tuberosity", "url": "/humerus.html"}
   | link(style="title", anchor="deltoid_tuberosity") }}
```

renders as:

```html
<a href="/humerus.html#deltoid_tuberosity" class="internal-link">Deltoid Tuberosity</a>
```

Bibliographic citations render similarly:

```jinja
{{ {"citation": {"author": "hull", "year": 2016, "page": 307}, "url": "/hull"} | link }}
```

produces:

```html
<a href="/hull" class="internal-link">(Hull 2016, 307)</a>
```

When you pass a string instead of a dictionary, the filter fetches the
corresponding metadata from Redis. The lookup retries a few times before
aborting so templates are more resilient when entries are added concurrently.

### Legacy filters

Older filters such as `linktitle`, `linkcap`, `linkicon`, `link_icon_title`,
and `linkshort` remain available for backward compatibility but are now thin
wrappers around `link`.  They will be removed in a future release.

Example:

```jinja
{{ {"citation": "deltoid tuberosity", "url": "/humerus.html"}
   | linktitle(anchor="deltoid_tuberosity") }}
```

renders as:

```html
<a href="/humerus.html#deltoid_tuberosity" class="internal-link">Deltoid Tuberosity</a>
```

## `get_desc`

Looks up a description object from the build index. If the name is not present,
`get_desc` returns the name unchanged.
