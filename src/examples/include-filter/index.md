{% extends "src/templates/template.html.jinja" %}
{% from "src/templates/macros.jinja" import deflist %}
{% block content %}
{{ deflist(["include-filter-a", "include-filter-b"]) }}
{% endblock %}
