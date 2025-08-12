# Standalone `bin/` Scripts

Scripts under `bin/` are intentionally self-contained. Each script includes any logic it needs so it can be copied to another project or environment without bringing along additional files from this repository.

Duplicating small snippets of shell is a deliberate choice: portability and ease of reuse are preferred over deduplicating a few lines into shared libraries. This minimizes coupling between directories and ensures the scripts work wherever they are placed.

Tools like codex make it straightforward to find and update repeated snippets when needed. Keeping duplication within `bin/` keeps the burden on maintainers low even without automated tools.
