# picasso Makefile Generator

`picasso` scans the `src/` directory for metadata files (`.yml` and `.yaml`) and
emits Makefile rules that render them to HTML using the `render-html` tool. The
generated rules are written to `build/picasso.mk` and included by the
`makefile` during the build. Refer to
[Metadata Fields](../reference/metadata-fields.md) for the supported metadata
keys.

## Usage

Run the command and redirect its output to `build/picasso.mk`:

```bash
picasso > build/picasso.mk
```

This happens automatically in the `makefile` whenever any `.yml` or `.yaml`
file under `src/` changes.

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
    cp $< $@
build/index.html: build/index.md build/index.yml $(HTML_TEMPLATE) $(BUILD_DIR)/.process-yamls
    $(call status,Generate HTML $@)
    render-html $< build/index.yml $@
```

Each metadata file produces similar targets for preprocessing the metadata and
rendering the final HTML.

The command also inspects Markdown files for cross-document links and any
`include-filter` Python blocks.  Links added via Jinja globals such as
`{{link("target-id")}}` are treated the same as filter expressions like
`{{"target-id"|link}}`. Dependencies discovered this way are emitted as
additional Makefile rules so that updates to referenced files trigger a rebuild
of the including document.

If these dependencies form a cycle, `picasso` logs a warning and drops the
minimum number of rules required to break the loop. The build continues with
the remaining rules.
