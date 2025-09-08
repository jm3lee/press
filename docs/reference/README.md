# Reference

Background material and technical specifications for the project. These
documents provide context for the task‑oriented
[guides](../guides/README.md).

## Contents

- [architecture.md](architecture.md) – overview of the site's architecture.
- [link-globals.md](link-globals.md) – global Jinja helpers for link
formatting.
- [jinja-globals.md](jinja-globals.md) – global variables exposed to templates.
- [definition.md](definition.md) – render snippets from the `definition` field.
- [keyterms.md](keyterms.md) – glossary of important terminology.
- [link-metadata.md](link-metadata.md) – link metadata format and usage.
- [logging.md](logging.md) – centralized logging helpers and configuration.
- [metadata-fields.md](metadata-fields.md) – description of common metadata
fields used throughout the project.
- [update-author.md](update-author.md) – refresh the `doc.author` field for
existing documents.
- [update-index.md](update-index.md) – insert index values into Redis.
- [update-pubdate.md](update-pubdate.md) – update the `doc.pubdate` field for
modified files.
- [migrate-metadata.md](migrate-metadata.md) – move legacy fields under
  `doc` and header includes under `html.scripts`.
- [update-url.md](update-url.md) – rename files and update URL fields.
- [update-link-filters.md](update-link-filters.md) – convert legacy `link*`
filters into globals.
- [update-metadata.md](update-metadata.md) – merge YAML data into metadata
files.
- [shell.md](shell.md) – run the project's shell service via docker compose.
- [sitemap.md](sitemap.md) – generate an XML sitemap with absolute URLs.
- [standalone-bin-scripts.md](standalone-bin-scripts.md) – rationale for self-
contained helper scripts.

For step‑by‑step workflows and tutorials, head back to the
[guides](../guides/README.md).
