# picasso Makefile Generator

`picasso` scans the `src/` directory for YAML metadata files and emits Makefile
rules that convert them to HTML using Pandoc. The generated rules are written to
`build/picasso.mk` and included by `dist/app/shell/mk/build.mk` during the build.
Refer to [Metadata Fields](metadata-fields.md) for the supported metadata keys.

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
    emojify < $< > $@
build/index.html: build/index.md build/index.yml
    $(PANDOC_CMD) $(PANDOC_OPTS) --metadata-file=build/index.yml -o $@ $<
    check-html-for-python-dicts $@
```

Each `.yml` file produces similar targets for preprocessing the metadata and
rendering the final HTML.

The command also inspects Markdown files for cross-document links and any
`include-filter` Python blocks.  Dependencies discovered this way are emitted as
additional Makefile rules so that updates to referenced files trigger a rebuild
of the including document.
