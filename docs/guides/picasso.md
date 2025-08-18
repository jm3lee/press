# picasso Makefile Generator

`picasso` scans the `src/` directory for YAML metadata files and emits Makefile
rules that convert them to HTML using Pandoc. The generated rules are written to
`build/picasso.mk` and included by `app/shell/mk/build.mk` during the build.
Refer to [Metadata Fields](../reference/metadata-fields.md) for the supported metadata keys.

## Usage

Run the command and redirect its output to `build/picasso.mk`:

```bash
picasso > build/picasso.mk
```

This happens automatically in `build.mk` whenever any `.yml` file under `src/`
changes.

You can override the source or build directories using `--src` and `--build`:

```bash
picasso --src path/to/src --build path/to/build > build/picasso.mk
```

## Example Output

For a source file `src/index.yml` the output looks like:

```make
build/index.yml: src/index.yml
    $(call status,Preprocess $<)
    mkdir -p $(dir build/index.yml)
    emojify < $< > $@
    render-jinja-template $@ $@
build/index.html: build/index.md build/index.yml $(PANDOC_TEMPLATE)
    $(call status,Generate HTML $@)
    $(PANDOC_CMD) $(PANDOC_OPTS) --template=$(PANDOC_TEMPLATE) --metadata-file=build/index.yml -o $@ $<
    check-bad-jinja-output $@
```

Each `.yml` file produces similar targets for preprocessing the metadata and
rendering the final HTML.

## Custom Pandoc Templates

`picasso` retrieves per-document metadata from Redis. If a document defines
`pandoc.template`, that template path is added as a dependency and passed to
Pandoc's `--template` option when rendering. For example:

```yaml
pandoc:
  template: src/blog/pandoc-template.html
```

This allows different pages to use specialized templates while falling back to
`$(PANDOC_TEMPLATE)` when no custom template is provided.

The command also inspects Markdown files for cross-document links and any
`include-filter` Python blocks.  Links added via Jinja globals such as
`{{link("target-id")}}` are treated the same as filter expressions like
`{{"target-id"|link}}`. Dependencies discovered this way are emitted as
additional Makefile rules so that updates to referenced files trigger a rebuild
of the including document.  If a referenced document has both Markdown and YAML
sources, dependencies are added for each existing file.

If these dependencies form a cycle, `picasso` logs a warning and drops the
minimum number of rules required to break the loop. The build continues with the
remaining rules.
