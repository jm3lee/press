Merge YAML data into metadata files.

The console script merges fields from a YAML mapping into metadata files.
Input data is read from a YAML file with -f or from stdin when omitted.

```bash
update-metadata [-f FILE] [--sort-keys] [-l LOGFILE] [-v] [PATH ...]
```

When PATH arguments are given they may refer to files, directories, or glob
patterns. Each path is scanned for Markdown or YAML files before processing. If
no paths are supplied, files changed in git are used instead.

Fields are merged recursively. Lists are extended with new entries and scalar
conflicts abort the update for the affected file. Updated files and conflict
warnings are written to LOGFILE. When not provided, logs are written to
log/update-metadata.txt. Use --sort-keys to write YAML mappings with
alphabetically sorted keys and -v for debug output.

A summary of the number of files checked and modified is written to the log
after processing.
