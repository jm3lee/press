# check-unescaped-dollar

`check-unescaped-dollar` scans Markdown files for single `$` characters that are
not escaped. Unescaped dollar signs can trigger MathJax parsing. The script
returns a non-zero exit status when any unescaped dollar signs are found.

## Usage

```bash
check-unescaped-dollar [-x EXCLUDE] [directory]
```

The optional directory defaults to `src`. When present,
`cfg/check-unescaped-dollar-exclude.yml` is loaded to determine files to skip.
Use `-x` to supply a different YAML file. Each file with an unescaped dollar
sign is logged for review.
