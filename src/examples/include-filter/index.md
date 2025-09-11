{% extends "src/templates/template.html.jinja" %}

{% block content %}
<dl>
```python
include_deflist_entry("src/examples/include-filter", glob="[a-z].md")
```
</dl>
{% endblock %}
