# Jinja Filters for Link Formatting

Several build scripts provide custom Jinja filters that transform Markdown links. They operate on strings of the form `[text](url)` and return HTML anchors. This document describes the `linktitle` filter which capitalizes every word in the link text.

## `linktitle`

The `linktitle` filter capitalizes the first character of **each** word in the link text while preserving all whitespace. Values that do not match the Markdown link pattern are returned unchanged.

Example:

```jinja
{{ "[deltoid tuberosity](/humerus.html#deltoid_tuberosity)" | linktitle }}
```

renders as:

```html
<a href="/humerus.html#deltoid_tuberosity" class="internal-link">Deltoid Tuberosity</a>
```

You can also use it inside YAML fragments that feed into Jinja templates:

```yaml
toc:
  - "{{deltoid_tuberosity|linktitle}}"
```

The filter implementation lives in `pie.render_jinja_template` and is available via the `render-jinja-template` command. It uses a regular expression to extract the link text and URL:

```python
match = _LINK_PATTERN.match(value)
...
transformed = _WHITESPACE_WORD_PATTERN.sub(_capitalize_word, link_text)
return f"[{transformed}]({url})"
```

This ensures that each word is capitalized without altering spacing or punctuation.

## `linkcap`

The `linkcap` filter capitalizes only the first character of the link text.
It expects the same `[text](url)` syntax and leaves the rest of the string
untouched.

```jinja
{{ "[deltoid tuberosity](/humerus.html#deltoid_tuberosity)" | linkcap }}
```

renders as:

```html
<a href="/humerus.html#deltoid_tuberosity" class="internal-link">Deltoid tuberosity</a>
```

## `linkicon`

`linkicon` leaves the link text unchanged but allows emoji or other icons to be
included. It is useful when the source metadata provides an `icon` field that
should appear before the link text.

## `link_icon_title`

This filter combines the behavior of `linkicon` with word capitalization. It is
primarily used when a metadata entry defines both an icon and link text.

## `link`

A simple filter that returns the raw HTML `<a>` tag without any additional
transformation.

## `get_desc`

Looks up a description object from the build index. If the name is not present,
`get_desc` returns the name unchanged.
