{% extends "src/templates/template.html.jinja" %}

{% block content %}
<div id="quiz-root" data-src="/quiz/demo.json"></div>
<script type="module" src="/static/js/quiz.js" defer></script>
{% endblock %}
