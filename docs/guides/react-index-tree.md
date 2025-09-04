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
options (`show` and `link`) used by the Markdown index generator. When
linking is enabled, the `url` property is copied from the metadata
without modification. Items may also specify `indextree.order` to control
their position. Numeric filenames are sorted numerically before falling
back to case-insensitive titles:

```bash
indextree-json docs doc-tree.json
```

Use `-t` to limit results to entries whose `tags` list contains an exact
match:

```bash
indextree-json -t tutorial docs doc-tree.json
```

A runnable demo lives in `app/indextree` and can be started with `npm run dev`.

## Build setup

Include the IndexTree makefile so the bundle is produced during regular
builds. Add the dependency to `src/dep.mk`:

```make
include app/indextree/dep.mk
```

Running `make` compiles the React source with Vite and copies
`build/static/js/indextree.js` into the build tree. The rule installs any
required packages on first run.

Define a rule to build the tree data alongside the bundle. The example
below writes `build/static/doc-tree.json` whenever a YAML metadata file
changes and adds both outputs to the `build` target:

```make
DOC_TREE := build/static/doc-tree.json

$(DOC_TREE): $(shell find docs -name '*.yaml' -o -name '*.yml')
	indextree-json docs $@

build: $(DOC_TREE) build/static/js/indextree.js
```

## Markdown integration

Generate the tree data and embed the component in a Markdown file:

```bash
indextree-json docs doc-tree.json
```

```markdown
<div class="indextree-root" data-src="/doc-tree.json"></div>
```

Any element with the `indextree-root` class marks where a tree renders. Add as
many as needed on the same page, each with a `data-src` attribute pointing to
its JSON file. Include `indextree.js` in the page template because the Markdown
renderer escapes `<script>` tags to prevent XSS.

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
    "label": "Alpha",
    "url": "/alpha/index.html",
    "children": [
      { "id": "beta", "label": "Beta", "url": "/alpha/beta.html" }
    ]
  }
]
```

Nodes are expandable when they contain a `children` array. Typing in the
filter box hides entries whose labels do not include the query while
automatically expanding the paths to matching descendants so results are
always visible.
