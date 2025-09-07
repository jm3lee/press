{% extends "src/templates/template.html.jinja" %}

{% block content %}
Explore all examples through the tree below.

<div class="indextree-root" data-src="/static/index/examples.json"></div>
<script type="module" src="/static/js/indextree.js" defer></script>
{% endblock %}
