# React Index Tree

Render a collapsible navigation tree for metadata processed by
`gen-markdown-index-2`. The `IndexTree` component loads a JSON
representation of the directory structure, displays it as an expandable
list, and provides a text box to filter entries by title. The demo is
styled using [Material UI](https://mui.com/), so make sure
`@mui/material` and `@mui/icons-material` are available in your project.

A runnable demo lives in `app/indextree` and can be started with `npm run dev`.

## Usage

```jsx
import { createRoot } from 'react-dom/client';
import IndexTree from './IndexTree';

createRoot(document.getElementById('root')).render(
  <IndexTree src="/static/doc-tree.json" />
);
```

The expected JSON file contains an array of nodes:

```json
[
  {
    "id": "alpha",
    "title": "Alpha",
    "url": "/alpha",
    "children": [
      { "id": "beta", "title": "Beta", "url": "/alpha/beta" }
    ]
  }
]
```

Nodes are expandable when they contain a `children` array. Typing in the
filter box hides entries whose titles do not include the query while
keeping matching descendants visible.
