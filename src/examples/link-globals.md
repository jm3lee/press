{% extends "src/templates/template.html.jinja" %}

{% block content %}
Press provides custom Jinja globals for formatting links. Each example shows
the template followed by its rendered result. Globals accept either a
metadata ID string or a dictionary with at least `doc.citation` and `url`.

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

{{ get_desc('link-globals')['summary'] }}
{% endblock %}
