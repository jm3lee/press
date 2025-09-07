{% extends "src/templates/template.html.jinja" %}

{% block content %}
<p>Tap the search button or press <kbd>Ctrl+K</kbd> (<kbd>⌘K</kbd> on macOS) to
toggle the MagicBar.</p>
<div id="magicbar-root" data-src="/magicbar/demo.json"></div>
<script type="module" src="/static/js/magicbar.js" defer></script>
{% endblock %}
