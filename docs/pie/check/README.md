# Checkers

Documentation for Pie's validation scripts.

- [checklinks](checklinks.md) – scan rendered HTML for broken links.
- [check-page-title](check-page-title.md) – verify page titles.
- [check-underscores](check-underscores.md) – report internal URLs that
  contain underscores.
- [check-post-build](check-post-build.md) – verify build artifacts after
  rendering.
- [check-bad-mathjax](check-bad-mathjax.md) – detect deprecated MathJax
  delimiters.
- [check-unescaped-dollar](check-unescaped-dollar.md) – detect unescaped
  dollar signs.

## Custom checks

`cfg/check-extra.yml` adds user checkers to the built-ins. The file lists
`module:function` references, one per line:

```yaml
- mypkg.checks:run
- other.mod:verify
```

Every referenced module must be on `PYTHONPATH`. After mounting the module and
configuration file, run `make check` as usual.

