# Responsive Images

The `figure` Jinja helper, exposed via `pie.render.jinja.figure.render`,
provides responsive `<figure>` blocks. Supply either a URL pattern with a
`{width}` placeholder or explicit width-to-URL mappings under the `figure`
metadata key. The helper emits a `srcset` and `sizes` attribute along with a
fallback `src` for older browsers and applies Bootstrap-compatible classes to
the rendered elements.

## Pattern-based widths

```jinja
{{ figure({
    "title": "Example chart",
    "url": "/img/chart@{width}.png",
    "figure": {
        "widths": [320, 640, 960],
        "sizes": "(max-width: 960px) 100vw, 960px",
        "caption": "An example chart"
    }
}) }}
```

## Explicit URLs

```jinja
{{ figure({
    "title": "Example chart",
    "url": "/img/chart-320.png",
    "figure": {
        "urls": [
            {"url": "/img/chart-320.png", "width": 320},
            {"url": "/img/chart-640.png", "width": 640}
        ],
        "sizes": "(max-width: 640px) 100vw, 640px"
    }
}) }}
```

Both approaches output responsive markup similar to:

```html
<figure class="figure">
  <img src="/img/chart-320.png"
       srcset="/img/chart-320.png 320w, /img/chart-640.png 640w"
       sizes="(max-width: 640px) 100vw, 640px"
       alt="Example chart"
       class="figure-img img-fluid rounded"
       loading="lazy" />
  <figcaption class="figure-caption tex-center">An example chart</figcaption>
</figure>
```

The browser picks the appropriate image size based on device width, reducing
bandwidth while preserving quality.
