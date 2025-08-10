# update-link-filters

Convert legacy `link*` Jinja filters into their global helper equivalents.

The console script scans each provided file or directory and rewrites
expressions like `{{ "hull" | linktitle }}` into `{{ linktitle("hull") }}`.
Only simple single-line patterns are handled; complex or multi-line cases
require manual updates.

```bash
update-link-filters PATH [PATH...]
```

Each modified file path is printed to stdout. A summary of the number of files
checked and changed appears at the end of execution. Log output is written to
`log/update-link-filters.txt` unless a different location is specified via the
`-l` option.
