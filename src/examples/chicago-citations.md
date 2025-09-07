{% extends "src/templates/template.html.jinja" %}

{% block content %}
Demonstrates Chicago-style citations using the `cite` and `link` globals.

## Creating citation metadata

Each source is stored in a small YAML file that includes the title,
`doc.citation` details, and URL. Save the file somewhere under `src/` so it gets
indexed during the build.

Example metadata file:

```yaml
# hull.yml
doc:
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
doc:
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
{% raw %}{{ cite("hull") }}{% endraw %}
```

renders as:

{{ cite("hull") }}

Multiple sources combine with semicolons:

```jinja
{% raw %}{{ cite("hull", "doe") }}{% endraw %}
```

renders as:

{{ cite("hull", "doe") }}

To override metadata—for example, to cite a different page—you can pass a
dictionary directly:

```jinja
{% raw %}{{ cite({"doc": {"citation": {"author": "Hull", "year": 2016, "page": 350}}, "url": "/"}) }}{% endraw %}
```

{{ cite({"doc": {"citation": {"author": "Hull", "year": 2016, "page": 350}}, "url": "/"}) }}

## link global

The `link` global turns metadata dictionaries or IDs into HTML anchors.

Using a dictionary:

```jinja
{% raw %}{{ link({"doc": {"citation": {"author": "hull", "year": 2016, "page": 307}}, "url": "/"}) }}{% endraw %}
```

renders as:

{{ link({"doc": {"citation": {"author": "hull", "year": 2016, "page": 307}}, "url": "/"}) }}

Passing an ID fetches the metadata automatically:

```jinja
{% raw %}{{ link("doe") }}{% endraw %}
```

{{ link("doe") }}
{% endblock %}

