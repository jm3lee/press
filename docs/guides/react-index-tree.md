# React Index Tree

Render a collapsible navigation tree for metadata processed by
`gen-markdown-index`. The `IndexTree` component loads a JSON
representation of the directory structure, displays it as an expandable
list, and provides a text box to filter entries by label. The demo is
styled using [Material UI](https://mui.com/), so make sure
`@mui/material`, `@mui/x-tree-view`, and `@mui/icons-material` are available in
your project.

The `indextree-json` console script can generate the required JSON by
scanning a directory of YAML metadata files and producing nodes for each
file and subdirectory. Entries honour the same `indextree`
options (`show` and `link`) used by the Markdown index generator.

To keep files compact, node identifiers are shortened to the minimal
unique prefixes of their document IDs. A companion mapping file is
written alongside the tree so applications can recover the original
identifiers if needed. When linking is enabled, the `url` property is
copied from the metadata without modification:

```bash
indextree-json docs doc-tree.json
# writes doc-tree.json and doc-tree.map.json
```

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
    "id": "a",
    "label": "Alpha",
    "url": "/alpha/index.html",
    "children": [
      { "id": "b", "label": "Beta", "url": "/alpha/beta.html" }
    ]
  }
]

The accompanying `doc-tree.map.json` records the original
identifiers:

```json
{
  "alpha": "a",
  "beta": "b"
}
```

Nodes are expandable when they contain a `children` array. Typing in the
filter box hides entries whose labels do not include the query while
automatically expanding the paths to matching descendants so results are
always visible.
