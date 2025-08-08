# process-yaml

Fill in missing metadata fields in a YAML file.

```
usage: process-yaml <input.yml> <output.yml>
```

The command reads the input YAML file, generates any missing values as described in [Metadata Fields](../reference/metadata-fields.md), and writes the result to the output file. Use `--log` to save verbose logs.

Example:

```bash
process-yaml in.yml out.yml --log build.log
```

## Integration

`process-yaml` is typically invoked automatically during a build. The
[`picasso`](picasso.md) tool scans metadata files and emits Makefile rules
that call this script before running Pandoc. A generated rule looks like:

```make
build/foo/bar.yml: src/foo/bar.yml
    $(Q)mkdir -p $(dir $@)
    $(Q)emojify < $< > $@
    $(Q)process-yaml $< $@
```

Running the script ensures each document has a complete metadata block
so Pandoc and other tools can rely on fields like `id` or `citation`.
