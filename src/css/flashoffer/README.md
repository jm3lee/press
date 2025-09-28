# Flashoffer Bootstrap bundle

The Flashoffer Bootstrap build is compiled from Bootstrap v5.3.8 sources. The
Makefile downloads and extracts the release tarball on demand during the
Sass compile so we do not vendor upstream assets.

To rebuild the stylesheet locally run:

```
make build/css/flashoffer/flashoffer-bootstrap.css
```
