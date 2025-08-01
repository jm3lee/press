# Jinja Filters for Link Formatting

Several build scripts provide custom Jinja filters that convert metadata
dictionaries into HTML anchors. Each dictionary is pulled from
`index.json` and must include a `citation` field which supplies the anchor
text, along with a `url` field. Optional keys like `icon`,
`link.tracking`, and `link.class` customize the output.  For an overview of
these metadata fields, see [Metadata Fields](metadata-fields.md).

## `linktitle`

`linktitle` capitalizes the first character of **each** word in the
`citation` field. It returns an HTML `<a>` element using the supplied
`url` and optional `icon`, `link.class`, or `link.tracking` fields.

Example:

```jinja
{{ {"citation": "deltoid tuberosity", "url": "/humerus.html#deltoid_tuberosity"} | linktitle }}
```

renders as:

```html
<a href="/humerus.html#deltoid_tuberosity" class="internal-link">Deltoid Tuberosity</a>
```

You can also use it inside YAML fragments that feed into Jinja templates:

```yaml
toc:
  - "{{\"deltoid_tuberosity\"|linktitle}}"
```

This filter lives in `pie.render_jinja_template` and is also exposed by the
`render-jinja-template` command.

When you pass a string instead of a dictionary, the filters fetch the
corresponding metadata from Redis. The lookup now retries a few times before
aborting so templates are more resilient when entries are added concurrently.

## `linkcap`

`linkcap` capitalizes only the first character of the `citation` text. It uses
the same metadata fields as `linktitle` and returns an anchor element.

```jinja
{{ {"citation": "deltoid tuberosity", "url": "/humerus.html#deltoid_tuberosity"} | linkcap }}
```

renders as:

```html
<a href="/humerus.html#deltoid_tuberosity" class="internal-link">Deltoid tuberosity</a>
```

## `linkicon`

`linkicon` leaves the `citation` text unchanged but allows emoji or other icons
to appear before it. Provide the optional `icon` field in the metadata to prefix
the link text.

## `link_icon_title`

This filter combines the behavior of `linkicon` with word capitalization. It is
primarily used when the metadata includes both an `icon` and a `citation`
value.

## `link`

`link` renders the `citation` field as-is without altering capitalization.
It is useful when no formatting is desired but you still want an anchor
element with the correct `url` and optional link attributes.

## `get_desc`

Looks up a description object from the build index. If the name is not present,
`get_desc` returns the name unchanged.
