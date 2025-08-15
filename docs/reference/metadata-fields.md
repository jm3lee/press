# Metadata Fields

This document lists the common metadata keys used by Press and explains how missing values are automatically generated.

## Required

- `title` – Heading shown in the rendered page.

## Optional Fields

- `author` – Author string passed to Pandoc.
- `description` – Short summary used for meta tags.
- `og_image` – OpenGraph image path.
- `meta` – Array of additional `<meta>` tag definitions for Pandoc.
- `icon` – Emoji or icon displayed by link globals.
- `permalink` – Canonical URL for the page. Use an absolute or relative URL.
- `link.tracking` – Boolean controlling external link behaviour.
- `link.class` – CSS class for rendered links.
- `name` – **Deprecated.** Former display name used in navigation and indexes.

## Auto‑Generated Values

During indexing, `generate_missing_metadata` in `pie.metadata` fills in several fields when they are missing:

| Field      | Default value                                  |
| ---------- | ---------------------------------------------- |
| `id`       | Filename without the extension                 |
| `citation` | Lowercase form of the `title` value            |
| `url`      | Derived from the source path (e.g. `src/foo.md` → `/foo.html`) |

The `citation` value is used as the anchor text when other pages link to this document using Jinja globals such as `linktitle`.
The helper that assigns these defaults lives in `generate_missing_metadata` within `pie.metadata`.

For bibliographic references the `citation` field may instead be a mapping with
`author`, `year`, and `page` keys.  This structure is consumed by the `cite`
Jinja global and by the link-formatting helpers to render Chicago style text in
parentheses.

`link.tracking` defaults to `true`, meaning links open in the same tab. `link.class` defaults to `internal-link`.

