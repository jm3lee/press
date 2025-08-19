# check-underscores

`check-underscores` scans HTML files for URLs that contain underscores. Using
underscores in URLs is discouraged; dashes are preferred for readability and
search engine optimisation. The command reports offending URLs and exits with a
non-zero status when it finds any.

## Usage

```bash
check-underscores [directory]
```

If no directory is provided, `build/` is scanned. The script lists each URL
containing underscores so they can be replaced with dashes.
