# update-pubdate

Update the `pubdate` field in metadata files for documents modified in git.

The console script scans `git status --short` for files that have been added,
changed, or are untracked. For each path it locates the associated Markdown and YAML
metadata pair using `load_metadata_pair` and replaces the `pubdate` field in
Markdown frontmatter or metadata YAML with today's date in the format `%b %d, %Y`.

```bash
update-pubdate [-l LOGFILE]
```

Each updated file is printed as `<path>: <old> -> <new>` and the same information
is logged to `LOGFILE`. When omitted, log output is written to
`log/update-pubdate.txt`.

When finished, the script reports how many files were checked and how many were
updated.

If a file under `src` is modified but no `pubdate` field can be updated, a
warning is logged.
