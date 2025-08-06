# checklinks

`checklinks` verifies that every link on a site resolves successfully. It uses `wget --spider` to crawl the provided URL and exits with a non-zero status when a broken link or HTTP error is encountered.

## Usage

```bash
checklinks URL
```

The command prints `wget`'s output while it scans up to three levels deep. If any link fails to resolve, `checklinks` reports "Broken links detected" and returns `1`. When all links are valid, it prints "No broken links found." and exits with `0`.

This check runs as part of the build pipeline described in [Architecture](../reference/architecture.md). For validating page titles, see
[check-page-title](check-page-title.md).
