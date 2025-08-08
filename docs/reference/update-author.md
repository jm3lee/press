# update-author

Update the `author` field in metadata files for documents modified in git.

The console script scans `git status --short` for files that have been added,
changed, or are untracked. For each path it locates the associated Markdown and YAML
metadata pair using `load_metadata_pair` and replaces the `author` field in
Markdown frontmatter or metadata YAML with the author configured in
`cfg/update-author.yml`.

```bash
update-author [-l LOGFILE]
```

Each updated file is printed as `<path>: <old> -> <new>` and logged to
`LOGFILE`.  When not specified, log output is written to
`log/update-author.txt`.

After processing, a summary of the number of files checked and modified is
printed to the console.

If a file under `src` is modified but no `author` field can be updated, a
warning is logged.

