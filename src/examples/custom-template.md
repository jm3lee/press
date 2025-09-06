The `template` metadata field renders this page with an alternate HTML layout.

```yaml
template: src/examples/custom-template.html
```

The snippet above comes from this page's metadata file.

`custom-template.html` defines a `note` macro that outputs a styled paragraph.
Macros are Jinja's version of functions: they accept arguments and return HTML
fragments. The `content` block invokes
`note("This page uses a custom template.")` to display the message before
delegating back to the default body with `{{ super() }}`.
