---
title: Jinja Examples
author: Brian Lee
id: jinja
citation: jinja
---

## For-loop

Markdown files can include Jinja2 templates. This loop generates three list items:

{% raw %}
{% for i in range(0, 3): -%}
- Jinja test {{ i }}
{% endfor %}
{% endraw %}

When the page is built the loop outputs items numbered 0–2.
