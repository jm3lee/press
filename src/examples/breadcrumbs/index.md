{% extends "src/templates/template.html.jinja" %}

{% block content %}
This page shows the breadcrumb trail rendered by the default Jinja template.
Define a `breadcrumbs` array in the page metadata and each item appears in a
Bootstrap-styled navigation list above the byline.

See the [nested demo](multi-level/) for a breadcrumb trail with three levels.
{% endblock %}
