# sitemap

Generate `sitemap.xml` from the HTML files in the build directory.

```bash
sitemap [DIRECTORY] [BASE_URL]
```

- `DIRECTORY` – location of the HTML files; defaults to `build`.
- `BASE_URL` – base URL for absolute links. When omitted, the command reads
  the `BASE_URL` environment variable.

`docker-compose.yml` exposes `BASE_URL` so the value can be configured in the
compose environment.

