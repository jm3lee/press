---
title: Chicago Citation Examples
author: Brian Lee
id: chicago-citations
citation: chicago citations
---

Demonstrates Chicago-style citations using the `cite` global and the
`link` filter.

## Creating citation metadata

Each source is stored in a small YAML file that includes the title,
citation details, and URL.  Save the file somewhere under `src/` so it
gets indexed during the build.

Example metadata file:

```yaml
# hull.yml
title: Options, Futures, and Other Derivatives
citation:
  author: Hull
  year: 2016
  page: 307
url: https://example.com/hull
```

Add as many sources as you need.  A second entry might look like:

```yaml
# doe.yml
title: Example Book
citation:
  author: Doe
  year: 2019
  page: 42
url: https://example.com/doe
```

## cite

Use the `cite` global to insert Chicago‑style parenthetical citations.

Single source:

```jinja
{% raw -%}
{{ cite("hull") }}
{% endraw %}
```

renders as:

{{ cite("hull") }}

Multiple sources combine with semicolons:

```jinja
{% raw -%}
{{ cite("hull", "doe") }}
{% endraw %}
```

renders as:

{{ cite("hull", "doe") }}

To override metadata—for example, to cite a different page—you can pass a
dictionary directly:

```jinja
{% raw -%}
{{ cite({"citation": {"author": "Hull", "year": 2016, "page": 350}, "url": "/hull"}) }}
{% endraw %}
```

{{ cite({"citation": {"author": "Hull", "year": 2016, "page": 350}, "url": "/hull"}) }}

## link filter

The `link` filter turns metadata dictionaries or IDs into HTML anchors.

Using a dictionary:

```jinja
{% raw -%}
{{ {"citation": {"author": "hull", "year": 2016, "page": 307}, "url": "/hull"} | link }}
{% endraw %}
```

renders as:

{{ {"citation": {"author": "hull", "year": 2016, "page": 307}, "url": "/hull"} | link }}

Passing an ID fetches the metadata automatically:

```jinja
{% raw -%}
{{ "doe" | link }}
{% endraw %}
```

{{ "doe" | link }}

