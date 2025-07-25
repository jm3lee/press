# check-page-title

`check-page-title` verifies that each HTML file under `build/` contains a non-empty first level heading. It exits with a non-zero status if any file is missing a `<h1>` tag or the tag contains no text.

## Usage

```bash
check-page-title [directory]
```

If no directory is given, `build/` is assumed. The command prints messages for files that fail the check and returns `1` when a problem is found.
