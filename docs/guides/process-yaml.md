# process-yaml

Fill in missing metadata fields in YAML files and replace `:emoji:` codes with
their Unicode counterparts.

```
usage: process-yaml <file.yml> [file.yml ...]
```

The command reads each YAML file and generates any missing values as described
in [Metadata Fields](../reference/metadata-fields.md). It writes the result
back to the same path. If the destination exists and its metadata is
unchanged, the file is left as is; cosmetic differences like key ordering or
quoting are ignored. Otherwise a new or updated file is written. Use `--log`
to save verbose logs.

Example:

```bash
process-yaml foo.yml bar.yml --log build.log
```

## Integration

`process-yaml` is typically invoked automatically during a build. The
[`picasso`](picasso.md) tool scans metadata files and emits Makefile rules.
The YAML files are preprocessed individually and then processed in batch. A
`find`/`xargs` pipeline keeps the command line short even with many files:

```make
build/foo/bar.yml: src/foo/bar.yml
    $(Q)mkdir -p $(dir $@)
    $(Q)render-jinja-template $< $@

$(BUILD_DIR)/.process-yamls: $(BUILD_YAMLS)
    find $(BUILD_DIR) -name '*.yml' -print0 | xargs -0 process-yaml
```

Running the script ensures each document has a complete metadata block so
Pandoc and other tools can rely on fields like `id` or `citation`.
