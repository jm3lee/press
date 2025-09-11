{% extends "src/templates/template.html.jinja" %}

{% block content %}
<dl>
{{ include_deflist_entry("src/examples/include-filter", glob="[a-z].mdi") }}
</dl>
{% endblock %}
