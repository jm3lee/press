# process-yaml

Fill in missing metadata fields in YAML files.

```
usage: process-yaml <file.yml> [file.yml ...]
```

The command reads each YAML file and generates any missing values as described
in [Metadata Fields](../reference/metadata-fields.md). It writes the result back
to the same path. Use `--log` to save verbose logs.

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
    $(Q)emojify < $< > $@
    $(Q)render-jinja-template $@ $@

$(BUILD_DIR)/.process-yamls: $(BUILD_YAMLS)
    find $(BUILD_DIR) -name '*.yml' -print0 | xargs -0 process-yaml
```

Running the script ensures each document has a complete metadata block so
Pandoc and other tools can rely on fields like `id` or `citation`.
