# Responsive Images

The `figure` Jinja helper can generate responsive `<img>` tags. Provide either a
URL pattern with a `{w}` placeholder or explicit width-to-URL mappings. The
helper emits a `srcset` and `sizes` attribute along with a fallback `src` for
older browsers.

## Pattern-based widths

```jinja
{{ figure({
    "url": "/img/chart@{w}.png",
    "widths": [320, 640, 960],
    "sizes": "(max-width: 960px) 100vw, 960px",
    "alt": "An example chart"
}) }}
```

## Explicit URLs

```jinja
{{ figure({
    "srcset": {
        "320": "/img/chart-320.png",
        "640": "/img/chart-640.png"
    },
    "sizes": "(max-width: 640px) 100vw, 640px",
    "alt": "An example chart"
}) }}
```

Both approaches output responsive markup similar to:

```html
<img src="/img/chart-320.png" srcset="/img/chart-320.png 320w, /img/chart-640.png 640w" sizes="(max-width: 640px) 100vw, 640px" alt="An example chart">
```

The browser picks the appropriate image size based on device width, reducing
bandwidth while preserving quality.
