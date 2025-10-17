# Flashoffer React Demo

This Vite-powered playground showcases the `flashoffer-react` component
library in an isolated application shell. It mounts every surface used in
Flashoffer landing pages (hero, call-to-action rows, preview cards, and
footer) so designers and product teams can iterate on messaging before
shipping updates to production sites.

## Getting started

Install dependencies and link the local component library:

```bash
cd app/flashoffer/flashoffer-demo
npm install
```

`flashoffer-react` (located at `app/flashoffer/flashoffer-react`) is referenced
through a relative `file:` dependency, so
local edits to the library are reflected the next time you start or rebuild
the demo.

## Available scripts

| Command | Description |
| ------- | ----------- |
| `npm run dev` | Start the Vite dev server with hot module replacement. |
| `npm run build` | Produce the static bundle consumed by Press Make targets. |
| `npm run preview` | Preview the production build locally. |
| `npm test` | Execute Vitest + React Testing Library smoke tests. |
| `npm run test:watch` | Run the demo tests in watch mode. |

## Customizing the showcase

The demo seeds each section with neutral imagery and placeholder URLs. You
can experiment with different palettes or hero layouts using the controls at
the top of the page:

- **Palette selector** cycles through the default Ocean preset plus nine
  additional themes (Sunset, Midnight, Sunrise Glow, Midnight Pulse, Ocean
  Breeze, Forest Canopy, Monochrome Focus, Spacious Typography Light, and
  Spacious Typography Dark).
- **Hero alignment** demonstrates how the hero banner adjusts copy, CTAs,
  and media when switching between centered and left-aligned presentations.
- **Celebration effect** lets you switch between the available
  `QuizCelebrations` presets or disable the animation entirely so stakeholders
  can validate how `MultipleChoiceQuiz` behaves in reduced motion contexts.

To try different copy or preview cards, update the arrays declared in
`src/App.tsx`. Reload the dev server (or rerun the build) after changing the
sample data to ensure the generated bundle matches your updates.

The countdown showcase highlights how to wire `CountdownTimer` into offer
pages. Adjust the props in `src/sections/CountdownShowcaseSection.tsx` to try
alternate headlines, quantities, or end times that match your promotion. Persist
offer windows in UTC within the demo data and convert the UTC timestamp to the
viewer’s local timezone before rendering friendly copy.
