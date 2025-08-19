# Guides

Step‑by‑step notes for working with the Press toolchain. For background
concepts and data formats, see the
[reference documentation](../reference/README.md).

## Build process
- [create-site.md](create-site.md) – scaffold a new Press project.
- [build-process.md](build-process.md) – overview of the build pipeline for new engineers.
- [build-index.md](build-index.md) – generate a JSON index of document
  metadata. See the [metadata fields reference](../reference/metadata-fields.md).
- [picasso.md](picasso.md) – create Makefile rules from YAML metadata.
- [preprocess.md](preprocess.md) – run custom pre‑processing steps.
- [update-index.md](update-index.md) – keep the index in sync after edits.

## Validation and testing
- [check-page-title.md](check-page-title.md) – verify page titles.
- [checklinks.md](checklinks.md) – scan rendered HTML for broken links.
- [check-underscores.md](check-underscores.md) – report URLs that contain underscores.
- [tests.md](tests.md) – run the automated test suite.

## Services and utilities
- [nginx.md](nginx.md) – development and production server configuration.
- [pdoc-service.md](pdoc-service.md) – generate API documentation.
- [react-index-tree.md](react-index-tree.md) – browse index data interactively.
- [store-files.md](store-files.md) – move files into S3 staging and create metadata.
- [sync-service.md](sync-service.md) – upload site files to S3 using the sync container.
- [webp-service.md](webp-service.md) – convert images to WebP using the helper
  container.
- [upgrade.md](upgrade.md) – rebuild containers and run tests
  after pulling changes.

Refer to the individual files for additional guides not listed here.

## Content features
- [responsive-images.md](responsive-images.md) – render responsive images with the figure helper.
