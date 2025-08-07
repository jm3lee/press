# check-post-build

`check-post-build` verifies that expected build artifacts exist after a build
completes. The list of required paths lives in `cfg/check-post-build.yml`,
making it easy to extend in the future. Results are written to
`log/check-post-build.txt`.

## Usage

```bash
check-post-build [build-directory]
```

If no directory is provided, `build/` is assumed. Use `-c` to point to a
different YAML config file. The command logs the outcome of each check and
exits with a non-zero status when any required file is missing.

