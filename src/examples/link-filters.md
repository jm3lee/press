---
title: Link Filter Examples
author: Brian Lee
id: link-filters
citation: link filters
---

Press provides custom Jinja filters for formatting links. Each example
shows the template followed by its rendered result. Filters accept either a
metadata ID string or a dictionary with at least `citation` and `url`.

## linktitle

```jinja
{% raw %}{{ "quickstart" | linktitle }}{% endraw %}
```

Output:

{{ "quickstart" | linktitle }}

## linktitle with anchor

```jinja
{% raw %}{{ {"citation": "home", "url": "/"} | linktitle(anchor="#example") }}{% endraw %}
```

Output:

{{ {"citation": "home", "url": "/"} | linktitle(anchor="#example") }}

## linkcap

```jinja
{% raw %}{{ "quickstart" | linkcap }}{% endraw %}
```

Output:

{{ "quickstart" | linkcap }}

## linkicon

```jinja
{% raw %}{{ {"citation": "Quickstart", "url": "/quickstart.html", "icon": "👉"} | linkicon }}{% endraw %}
```

Output:

{{ {"citation": "Quickstart", "url": "/quickstart.html", "icon": "👉"} | linkicon }}

## link_icon_title

```jinja
{% raw %}{{ {"citation": "Quickstart", "url": "/quickstart.html", "icon": "👉"} | link_icon_title }}{% endraw %}
```

Output:

{{ {"citation": "Quickstart", "url": "/quickstart.html", "icon": "👉"} | link_icon_title }}

## link

The `link` filter combines all the others and is the preferred option:

```jinja
{% raw %}{{ "quickstart" | link }}{% endraw %}
```

Output:

{{ "quickstart" | link }}
