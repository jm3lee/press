# Link Metadata Files

This document explains how to describe external links using YAML files and how the build scripts interpret them. A list of all metadata keys can be found in [Metadata Fields](metadata-fields.md).

## Creating a Metadata File

Place YAML files under `src/links/`. Each file defines at least a `name` and a `url` for the destination. Any additional fields become part of the build index. When the file does not specify an `id`, it is derived from the filename.

Example `src/links/press_io_home.yml`:

```yaml
name: press.io home
url: https://press.io
link:
  tracking: false
  class: external-link
```

This file generates an entry with the `id` `press_io_home` because the filename (without extension) is used when the `id` field is missing.

## Link Tracking

If the nested `link.tracking` value is set to `false`, rendered HTML links include `rel="noopener noreferrer"` and `target="_blank"`. This prevents referral information from being sent and opens the link in a new tab. Omitting the field or setting it to `true` keeps the default behaviour.

The logic lives in `pie.render.jinja.get_tracking_options()` which checks the metadata for this flag.

```
if "link" in desc:
    if "tracking" in desc:
        if desc["tracking"] == False:
            return 'rel="noopener noreferrer" target="_blank"'
```

## Link Class

By default, rendered links use the CSS class `internal-link`. You can override this by specifying `link.class` in the metadata. For example:

```yaml
link:
  class: external-link
```

## How IDs Are Generated

During indexing, :func:`fill_missing_metadata` from ``pie.metadata`` assigns an ``id`` when it is absent:

```python
metadata = fill_missing_metadata(metadata, filepath)
```

Thus ``src/links/press_io_home.yml`` results in the ``id`` ``press_io_home``.

After defining link metadata, run [checklinks](../guides/checklinks.md) to ensure each target resolves correctly.
