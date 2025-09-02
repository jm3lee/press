This tutorial introduces the basics of embedding Jinja in Markdown. Each
snippet shows the template followed by its rendered output.

## Variables

Insert the value of a variable:

```jinja
{% raw %}{{ "Hello, world!" }}{% endraw %}
```

renders as:

{{ "Hello, world!" }}

## For loop

Generate repeated content with a loop:

```jinja
{% raw %}{% for i in range(0, 3) -%}
- Jinja test {{ i }}
{% endfor %}{% endraw %}
```

Output:

{% for i in range(0, 3) -%}
- Jinja test {{ i }}
{% endfor %}

## Conditional

Only show text when a condition is true:

```jinja
{% raw %}{% if 2 > 1 %}Two is greater than one{% endif %}{% endraw %}
```

Output:

{% if 2 > 1 %}Two is greater than one{% endif %}

## Filters

Filters transform values. This uses the built-in `upper` filter:

```jinja
{% raw %}{{ "press" | upper }}{% endraw %}
```

Output:

{{ "press" | upper }}

Custom globals work the same way. The `link` global turns metadata into an anchor tag:

```jinja
{% raw %}{{ link({"citation": "Quickstart", "url": "/quickstart.html"}) }}{% endraw %}
```

Output:

{{ link({"citation": "Quickstart", "url": "/quickstart.html"}) }}
