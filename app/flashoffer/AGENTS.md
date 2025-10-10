# Flashoffer Workspace Guidelines

## Global

- All Flashoffer documentation lives under `app/flashoffer/docs`.
- All Flashoffer engineering guidance is centralized in this file.
- All `flashoffer-react` components must be compatible with the Flashoffer
  theme provider.
- Persist all timestamps in Coordinated Universal Time (UTC).
- Convert UTC timestamps to a viewer's local timezone before displaying them.
- Pin all Flashoffer Docker Node base images to `node:22-slim`.
- Pin all Flashoffer Docker Python base images to `python:3.14-slim`.

## Flashoffer React Components

- Prioritize responsive layouts that adapt gracefully to mobile viewports.
- Each source file must begin with a copyright header crediting "Flashoffer
  Developers" and noting that the library is released under the MIT license.
- Document every function with a succinct summary of its purpose; use Typedoc
  conventions for detailed parameter and return information.
- Author documentation with the depth and tone expected between expert
  software engineers.
- When updating documentation, include a representative code sample whenever
  possible.
- Avoid complex ternary expressions in component logic. When branching exceeds
  a single simple condition, extract the logic into a named helper instead of
  nesting ternaries.
