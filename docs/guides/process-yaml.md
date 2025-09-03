# process-yaml

Fill in missing metadata fields in YAML files, expand Jinja templates, and
replace `:emoji:` codes with their Unicode counterparts.

The command relies on the consolidated helpers in `pie.yaml` for consistent
YAML parsing and writing across tools.

```
usage: process-yaml <file.yml> [file.yml ...]
```

The command renders any Jinja syntax in each YAML file and generates missing
values as described in [Metadata Fields](../reference/metadata-fields.md). It
writes the result back to the same path. If the destination exists and its
metadata is unchanged, the file is left as is; cosmetic differences like key
ordering or quoting are ignored. Otherwise a new or updated file is written.
Use `--log` to save verbose logs.

Example:

```bash
process-yaml foo.yml bar.yml --log build.log
```

## Integration

`process-yaml` is typically invoked automatically during a build. The
[`picasso`](picasso.md) tool scans metadata files and emits Makefile rules. The
metadata files are copied or converted to YAML in the build tree and then
processed in batch. A `find`/`xargs` pipeline keeps the command line short even
with many files:

```make
build/foo/bar.yml: src/foo/bar.yml
    $(Q)mkdir -p $(dir $@)
    $(Q)cp $< $@

$(BUILD_DIR)/.process-yamls: $(BUILD_YAMLS)
    find $(BUILD_DIR) -name '*.yml' -print0 | xargs -0 process-yaml
```

Running the script ensures each document has a complete metadata block so
rendering tools can rely on fields like `id` or `citation`.
