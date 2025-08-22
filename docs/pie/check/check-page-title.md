# check-page-title

`check-page-title` verifies that each HTML file under `build/` contains a
non-empty first level heading. It exits with a non-zero status if any
file is missing a `<h1>` tag or the tag contains no text.

## Usage

```bash
check-page-title [directory] [-x exclude.yml]
```

If no directory is given, `build/` is assumed. The command prints
messages for files that fail the check and returns `1` when a problem is
found. Use `-x`/`--exclude` to provide a YAML file listing HTML files to
skip. Paths may be absolute or relative to the directory being scanned.

### Example exclude file

```yaml
- index.html
- guide/intro.html
```
