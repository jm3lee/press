{% extends "src/templates/template.html.jinja" %}

{% block content %}
<dl>
```python
include_deflist_entry("src/include-filter", glob="[a-z].md")
```
</dl>
{% endblock %}
