# Metadata Fields

This document lists the common metadata keys used by Press and explains how missing values are automatically generated.

## Required

- `name` – Display name used in navigation and indexes.

## Optional Fields

- `title` – Heading shown in the rendered page.
- `author` – Author string passed to Pandoc.
- `description` – Short summary used for meta tags.
- `og_image` – OpenGraph image path.
- `meta` – Array of additional `<meta>` tag definitions for Pandoc.
- `icon` – Emoji or icon displayed by link filters.
- `parent` – ID of a parent page.
- `link.tracking` – Boolean controlling external link behaviour.
- `link.class` – CSS class for rendered links.

## Auto‑Generated Values

During indexing, `build_index.py` fills in several fields when they are missing:

| Field      | Default value                                  |
| ---------- | ---------------------------------------------- |
| `id`       | Filename without the extension                 |
| `citation` | Lowercase form of the `name` value             |
| `url`      | Derived from the source path (e.g. `src/foo.md` → `/foo.html`) |

The `citation` value is used as the anchor text when other pages link to this document using Jinja filters such as `linktitle`.
The helper that assigns these defaults lives in `parse_yaml_metadata` within `pie.build_index`.

For bibliographic references the `citation` field may instead be a mapping with
`author`, `year`, and `page` keys.  This structure is consumed by the `cite`
Jinja global and by the link-formatting filters to render Chicago style text in
parentheses.

`link.tracking` defaults to `true`, meaning links open in the same tab. `link.class` defaults to `internal-link`.

