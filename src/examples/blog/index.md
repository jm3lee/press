{% extends "src/templates/blog/template.html.jinja" %}
{% block content %}
<section>
{% filter md %}
Welcome to the future of blogging! This sample article demonstrates the
`Jinja` blog template included with Press.
{% endfilter %}
</section>

<section>
{% filter md %}
## Eye-catching content

Because the template uses a full-width hero image and clean typography,
your words take center stage. Each section fades in as you scroll, creating
a smooth reading experience that feels lively yet unobtrusive.

Design-minded readers will appreciate the generous white space and
fall-inspired accents that keep attention on the text. Animations use modern
CSS features so the page remains lightweight and accessible.

Even long-form articles stay readable thanks to the comfortable
line-height and responsive layout.
{% endfilter %}
</section>

<section>
{% filter md %}
## Easy to style

Add your own CSS in the metadata to match your site's branding. The
included IntersectionObserver script ensures content animates only once,
improving performance on slower devices.

- drop in your favorite font
- customize accent colors
- extend the fade-in effect with your own classes

Water.css provides a clean base, while the template's variables make it
simple to tweak the look.
{% endfilter %}
</section>

<section>
{% filter md %}
## Mobile first

Spacing and typographic scale adapt to smaller screens, so the article
feels at home on phones. Try resizing your browser to see the responsive
layout in action.

The hero image scales gracefully and the byline tucks beneath the title
to save vertical space without sacrificing style.
{% endfilter %}
</section>

<section>
{% filter md %}
## Inspiration

Feeling creative? Duplicate this folder and start writing. Because the
layout is pure HTML and CSS, you can experiment freely without a build
step getting in the way.

Share your experiments with the community and keep pushing the template
forward.
{% endfilter %}
</section>
{% endblock %}
