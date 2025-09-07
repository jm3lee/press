"""Utilities for Press's document generation pipeline.

The :mod:`pie` package bundles a collection of small command line tools used
to build and maintain Press content.  The modules can be executed directly
through console scripts and are also importable for use in other Python code.

The most commonly used modules are:

* :mod:`update.index` – update an existing index file with new entries.
* :mod:`filter.include` – preprocess Markdown and expand custom ``include``
  directives.
* :mod:`render.jinja` – render Jinja templates with Press metadata.
* :mod:`render_study_json` – convert an index tree to a JSON structure used by
  study tools.
* :mod:`gen_markdown_index` – generate a Markdown index from YAML metadata.
* :mod:`process_yaml` – parse and augment YAML frontmatter.
* :mod:`build.picasso` – bundle assets for diagrams and interactive code examples.
* :mod:`check.page_title` – ensure HTML files contain non-empty ``<h1>`` tags.
* :mod:`check.post_build` – verify that expected build artifacts exist.
* :mod:`filter.emojify` – convert ``:emoji:`` codes to Unicode characters.

Use ``help(pie.<module>)`` to view documentation for any of the individual
modules.
"""

__all__ = [
    "filter",
    "metadata",
    "render",
    "render_study_json",
    "gen_markdown_index",
    "process_yaml",
    "schema",
    "yaml",
    "build",
    "check",
    "update",
]
