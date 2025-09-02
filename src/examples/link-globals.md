Press provides custom Jinja globals for formatting links. Each example
shows the template followed by its rendered result. Globals accept either a
metadata ID string or a dictionary with at least `citation` and `url`.

## linktitle

```jinja
{% raw %}{{ linktitle("quickstart") }}{% endraw %}
```

Output:

{{ linktitle("quickstart") }}

## linktitle with anchor

```jinja
{% raw %}{{ linktitle({"citation": "home", "url": "/"}, anchor="#example") }}{% endraw %}
```

Output:

{{ linktitle({"citation": "home", "url": "/"}, anchor="#example") }}

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
{% raw %}{{ linkicon({"citation": "Quickstart", "url": "/quickstart.html", "icon": "👉"}) }}{% endraw %}
```

Output:

{{ linkicon({"citation": "Quickstart", "url": "/quickstart.html", "icon": "👉"}) }}

## link_icon_title

```jinja
{% raw %}{{ link_icon_title({"citation": "Quickstart", "url": "/quickstart.html", "icon": "👉"}) }}{% endraw %}
```

Output:

{{ link_icon_title({"citation": "Quickstart", "url": "/quickstart.html", "icon": "👉"}) }}

## link

The `link` global combines all the others and is the preferred option:

```jinja
{% raw %}{{ link("quickstart") }}{% endraw %}
```

Output:

{{ link("quickstart") }}
