# check-underscores

`check-underscores` scans HTML files for internal URLs that contain underscores.
Using underscores in URLs is discouraged; dashes are preferred for readability
and search engine optimisation. External links are ignored because third-party
sites often use underscores legitimately. Pass `--error` to exit with a non-zero
status when underscores are found.

## Usage

```bash
check-underscores [--error] [directory]
```

If no directory is provided, `build/` is scanned. The script lists each URL
containing underscores so they can be reviewed or replaced with dashes.
