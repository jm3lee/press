# sitemap

Generate `sitemap.xml` from the HTML files in the build directory.

This command is provided by the ``pie`` package as a console script.

```bash
sitemap [-x EXCLUDE] [DIRECTORY] [BASE_URL]
```

- `-x EXCLUDE` – YAML file listing HTML files to skip. When omitted,
  `cfg/sitemap-exclude.yml` is loaded if present.
- `DIRECTORY` – location of the HTML files; defaults to `build`.
- `BASE_URL` – base URL for absolute links. When omitted, the command reads
  the `BASE_URL` environment variable.

URLs ending with `index.html` are canonicalised to their directory paths so
`http://foo/index.html` becomes `http://foo/`.

`docker-compose.yml` exposes `BASE_URL` so the value can be configured in the
compose environment.

