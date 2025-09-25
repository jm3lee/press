## Demo

<div class="react-demo-root"></div>

## User Guide

### Overview

The React Demo component is a deliberately empty shell that provides a
pre-configured build pipeline and a predictable mounting contract. Use it to
bootstrap experiments or to scaffold production-ready features before the
visual design is finalized.

### Installation

1. Install dependencies and build the bundle:

   ```bash
   make build/static/js/react-demo.js
   ```

2. Add the generated script to your page metadata. The examples site uses the
   following snippet:

   ```yaml
   html:
     scripts:
     - <script type="module" src="/static/js/react-demo.js" defer></script>
   ```

3. Place a container element with the `react-demo-root` class wherever you want
   the component to appear.

### Embedding in Templates

Press renders Markdown through Jinja templates. You can embed the component by
adding a container div to your Markdown or template:

```html
<div class="react-demo-root"></div>
```

The bootstrap script automatically discovers every matching element and mounts
an isolated React root. The guard on `data-react-demo-mounted` ensures the
component is only instantiated once per node, even if the script is included
multiple times.

### Customizing Content

The placeholder markup is intentionally simple. To replace it with real
features, edit `app/react-demo/src/ReactDemo.jsx`. You can pass a `sections`
prop to the component to control the rendered panels:

```js
root.render(
  <ReactDemo
    sections={[
      { title: 'Step One', body: 'Collect requirements from stakeholders.' },
      { title: 'Step Two', body: 'Iterate on UI states with design partners.' }
    ]}
  />
)
```

Because the component uses PropTypes, invalid inputs are caught during
development builds.

### Styling

The current implementation is unstyled so that teams can supply their own
systems. Add a CSS file next to the component and import it from `main.jsx` to
apply brand-specific tokens. Press will bundle the stylesheet with the rest of
the assets during `npm run build`.

### Production Checklist

- Replace the placeholder copy with final messaging.
- Add storybook coverage or unit tests alongside the component.
- Wire any data fetching or event handling required by the feature.
- Run `npm run build` to verify the bundle before committing changes.
