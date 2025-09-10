# Breadcrumb Navigation

Add a `doc.breadcrumbs` array to a page's metadata to show hierarchical links
at the top of the page. Each breadcrumb item has a `title` and optional
`url`. When `url` is omitted, the item renders as the current page. Start the
array with a `Home` entry that links to the site root.

```yaml
doc:
  breadcrumbs:
    - title: Home
      url: /
    - title: Examples
      url: /examples/
    - title: Breadcrumb Demo
```

For deeper hierarchies, add more items:

```yaml
doc:
  breadcrumbs:
    - title: Home
      url: /
    - title: Examples
      url: /examples/
    - title: Breadcrumb Demo
      url: /examples/breadcrumbs/
    - title: Nested Demo
```

See `src/examples/breadcrumbs` for a simple demo and
`src/examples/breadcrumbs/multi-level` for a three-level example.
