# check-bad-mathjax

`check-bad-mathjax` scans Markdown files for MathJax `\(` `\)` and `\[` `\]`
delimiters. Inline math must use `$...$` and block math `$$...$$`. The script
returns a non-zero exit status when deprecated delimiters are found.

## Usage

```bash
check-bad-mathjax [-x EXCLUDE] [directory]
```
 
The optional directory defaults to `src`. When present,
`cfg/check-bad-mathjax-exclude.yml` is loaded to determine files to skip. Use
``-x`` to supply a different YAML file. Entries may include wildcards or
regular expressions prefixed with `regex:`. Each file that contains forbidden
delimiters is logged for review.
