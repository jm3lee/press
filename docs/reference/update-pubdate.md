# update-pubdate

Update the `pubdate` field in metadata files for documents modified in git.

The console script scans `git status --short` for tracked files that have been
added or changed. For each path it locates the associated Markdown and YAML
metadata pair using `load_metadata_pair` and replaces the `pubdate` field in
Markdown frontmatter or metadata YAML with today's date in the format `%b %d, %Y`.

```bash
update-pubdate
```

Each updated file is printed as `<path>: <old> -> <new>` and the same information
is logged to `log/update-pubdate.txt`.
