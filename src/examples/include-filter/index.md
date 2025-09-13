{% extends "src/templates/template.html.jinja" %}

{% macro deflist(ids) %}
<dl>
{% for id in ids %}
{% set desc = get_desc(id) %}
<dt id="{{desc.deflist.anchor}}">{{ desc.doc.title }} <a href="#{{desc.deflist.anchor}}"><small>#</small></a></dt>
<dd>{% include desc.deflist.src %}</dd>
{% endfor %}
</dl>
{% endmacro %}

{% block content %}
{{ deflist(["include-filter-a", "include-filter-b"]) }}
{% endblock %}
