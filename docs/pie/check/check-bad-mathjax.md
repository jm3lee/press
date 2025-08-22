# check-bad-mathjax

`check-bad-mathjax` scans Markdown files for MathJax `\(` `\)` and `\[` `\]`
delimiters. Inline math must use `$...$` and block math `$$...$$`. The script
returns a non-zero exit status when deprecated delimiters are found.

## Usage

```bash
check-bad-mathjax [-x EXCLUDE] [directory]
```

The optional directory defaults to `src`. Pass ``-x`` to supply a YAML file
listing Markdown files to ignore. Each file that contains forbidden delimiters
is logged for review.
