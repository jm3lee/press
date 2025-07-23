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

The filter implementation lives in `app/shell/bin/render_template` and uses a regular expression to extract the link text and URL:

```python
match = _LINK_PATTERN.match(value)
...
transformed = _WHITESPACE_WORD_PATTERN.sub(_capitalize_word, link_text)
return f"[{transformed}]({url})"
```

This ensures that each word is capitalized without altering spacing or punctuation.
