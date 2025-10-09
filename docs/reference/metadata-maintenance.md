# Metadata maintenance

Keep metadata fields consistent with the console scripts shipped in the Pie
package. Each tool can operate on tracked git changes or on explicit paths, so
you can tidy individual documents or run sweeping updates across the project.

## update-author

`update-author` ensures every document records the latest `doc.author` value.
When no paths are supplied it inspects `git status --short` for modified
Markdown and YAML files. You can also pass files, directories, or glob patterns
to update specific sections of the site. Metadata is loaded with
`load_metadata_pair`, updated in place, and written back to YAML when present.
Missing metadata files are created automatically. The author defaults to the
value in `cfg/update-author.yml`; override it with `--author` (or `-a`) for
batch operations.

```bash
update-author [-a AUTHOR] [--sort-keys] [-l LOGFILE] [-v] [PATH ...]
```

Updated files are printed as `<path>: <old> -> <new>` and written to the log.
When `--log` is omitted, output lands in `log/update-author.txt`. Pass
`--sort-keys` to write YAML mappings with alphabetized keys and `-v` for debug
logging.

## update-pubdate

`update-pubdate` mirrors `update-author` but refreshes the `doc.pubdate` field.
When metadata is missing, the script creates it and records today's date using
`%b %d, %Y` formatting. It shares the same CLI options for sorting keys, setting
log destinations, and enabling verbose output.

```bash
update-pubdate [--sort-keys] [-l LOGFILE]
```

Warnings are emitted when a modified file under `src/` lacks an associated
metadata pair, ensuring missing pubdates are easy to spot.

## update-metadata

`update-metadata` merges YAML mappings into metadata files. Input comes from a
YAML file passed with `-f` or from stdin when the option is omitted. Paths may
reference files, directories, or glob patterns; without them the tool processes
files changed in git.

```bash
update-metadata [-f FILE] [--sort-keys] [-l LOGFILE] [-v] [PATH ...]
```

Mappings are merged recursively. Lists are extended, while conflicting scalar
values abort the update for the affected file. Updated files and conflicts are
logged (default `log/update-metadata.txt`). Use `--sort-keys` to alphabetize
YAML keys and `-v` for detailed diagnostics.

## migrate-metadata

`migrate-metadata` rewrites legacy fields so new templates can rely on the
modern structure. It moves top-level `author`, `pubdate`, `link`, `title`,
`citation`, and `breadcrumbs` fields under `doc`, and migrates
`header_includes` to `html.scripts`.

```bash
migrate-metadata PATH [PATH ...]
```

The command updates Markdown front matter and YAML metadata in place, printing
`<path>: migrated` for each file. Logs default to `log/migrate-metadata.txt` but
can be redirected with the shared `--log` option. A final summary reports how
many files were examined and changed.
