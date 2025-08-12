# update-author

Update the `author` field in metadata files for documents modified in git or
within a specified directory.

By default the console script scans `git status --short` for tracked files that
have been added or changed. When a directory is provided, all Markdown and YAML
files under that path are examined instead. For each file it locates the
associated Markdown and YAML metadata pair using `load_metadata_pair` and
replaces the `author` field in Markdown frontmatter or metadata YAML with the
author configured in `cfg/update-author.yml`. Pass `--author` or `-a` to
override this value, which is useful when batch updating book excerpts, quotes,
or other content.

```bash
update-author [-a AUTHOR] [-l LOGFILE] [DIR]
```

Each updated file is printed as `<path>: <old> -> <new>` and logged to
`LOGFILE`.  When not specified, log output is written to
`log/update-author.txt`.

After processing, a summary of the number of files checked and modified is
printed to the console.

If a file under `src` is modified but no `author` field can be updated, a
warning is logged.

