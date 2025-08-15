# check-permalinks

`check-permalinks` scans source files for `permalink` metadata and ensures each value is unique. The command exits with a non-zero status when duplicates are found.

## Usage

```bash
check-permalinks [directory]
```

The optional `directory` argument defaults to `src`. Use `-l/--log` to write detailed results to a file.
