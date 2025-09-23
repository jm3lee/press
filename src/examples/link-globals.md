
Press provides custom Jinja globals for formatting links. Each example shows
the template followed by its rendered result. Globals accept either a metadata
ID string or a dictionary with at least `doc.citation` and `url`. Icons are now
opt-in; pass `use_icon=True` or rely on helpers such as `linkicon` when you
want to render the `icon` field.

## linktitle

```jinja
{% raw %}{{ linktitle("quickstart") }}{% endraw %}
```

Output:

{{ linktitle("quickstart") }}

## linktitle with anchor

```jinja
{% raw %}{{ linktitle({"doc": {"citation": "home"}, "url": "/"}, anchor="#example") }}{% endraw %}
```

Output:

{{ linktitle({"doc": {"citation": "home"}, "url": "/"}, anchor="#example") }}

## linktitle with custom citation

```jinja
{% raw %}{{ linktitle("quickstart", citation="custom citation") }}{% endraw %}
```

Output:

{{ linktitle("quickstart", citation="custom citation") }}

## linkcap

```jinja
{% raw %}{{ linkcap("quickstart") }}{% endraw %}
```

Output:

{{ linkcap("quickstart") }}

## linkicon

```jinja
{% raw %}{{ linkicon({"doc": {"citation": "Quickstart"}, "url": "/quickstart.html", "icon": "👉"}) }}{% endraw %}
```

Output:

{{ linkicon({"doc": {"citation": "Quickstart"}, "url": "/quickstart.html", "icon": "👉"}) }}

## link_icon_title

```jinja
{% raw %}{{ link_icon_title({"doc": {"citation": "Quickstart"}, "url": "/quickstart.html", "icon": "👉"}) }}{% endraw %}
```

Output:

{{ link_icon_title({"doc": {"citation": "Quickstart"}, "url": "/quickstart.html", "icon": "👉"}) }}

## link

The `link` global combines all the others and is the preferred option:

```jinja
{% raw %}{{ link("quickstart") }}{% endraw %}
```

Output:

{{ link("quickstart") }}

## Metadata

Jinja globals work inside YAML metadata. The `link-globals.yml` file defines
`summary` with the `link` global:

```yaml
{% raw %}summary: '{{ link("quickstart") }}'{% endraw %}
```

Rendered:

{{ render_jinja(summary) }}
