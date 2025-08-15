# MagicBar

`MagicBar` provides a floating search bar fixed to the top of the page. It
allows users to enter a regular expression and quickly navigate to matching
pages. Suggestions appear as you type and selecting an entry loads the
associated URL. Press **Ctrl+K** (or **⌘K** on macOS) to toggle the bar and
use **Esc** or the close button to dismiss it. On touch devices, a floating
search button toggles the bar.

The component is built with [Material UI](https://mui.com/) and optimised for
mobile use. Include the script on any page and supply a JSON file describing
the available pages.

## Usage

```jsx
import { createRoot } from 'react-dom/client';
import MagicBar from './MagicBar';

createRoot(document.getElementById('magicbar-root')).render(
  <MagicBar pages={[{ title: 'Home', url: '/' }]} />
);
```

For static pages, a common pattern is to store the dataset in a separate file
and let the component fetch it. The element mounting the component should
include a `data-src` attribute pointing to the JSON file:

```html
<div id="magicbar-root" data-src="/magicbar/demo.json"></div>
<script type="module" src="/static/js/magicbar.js" defer></script>
```

## JSON Format

`MagicBar` expects an array of page objects:

```json
[
  { "title": "Using Option Pricing & Greek Calculator", "url": "/calc" }
]
```

Each object must contain a `title` and `url` property. An optional
`shortcut` string can be provided and is also matched against the search
expression.

Typing a regular expression filters the list by testing the pattern against
each page's `title` and `shortcut`. When the user selects a result, the
browser navigates to the page's `url`.

When the search field is empty the component shows all pages in a scrollable
panel capped to three visible items so it never covers the full screen.

## Demo

An example dataset and page live in `src/magicbar`. After building the
`app/magicbar` project, the component script is available at
`/static/js/magicbar.js` and the demo page loads the data from
`/magicbar/demo.json`.

For details on generating the JSON dataset, see the
[MagicBar indexing documentation](../../app/magicbar/docs/magicbar-index.md).

