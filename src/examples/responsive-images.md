---
title: Responsive Images
author: Brian Lee
id: responsive-images
citation: responsive-images
breadcrumbs:
  - title: Home
    url: /
  - title: Examples
    url: /examples/
  - title: Responsive Images
---

This example shows how to build a responsive image using the `figure` Jinja macro.

```jinja
{{ figure({
    "url": "https://via.placeholder.com/{w}",
    "widths": [320, 640],
    "sizes": "(max-width: 640px) 100vw, 640px",
    "alt": "Placeholder"
}) }}
```

renders as:

{{ figure({
    "url": "https://via.placeholder.com/{w}",
    "widths": [320, 640],
    "sizes": "(max-width: 640px) 100vw, 640px",
    "alt": "Placeholder"
}) }}
