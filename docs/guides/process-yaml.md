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
