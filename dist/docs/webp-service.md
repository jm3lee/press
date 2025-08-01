# webp image conversion service

The `webp` service converts PNG and JPEG files to WebP format using
[ImageMagick](https://imagemagick.org). The container lives under
`dist/app/webp` and runs `/app/bin/service` in a loop.

## Directories

- `dist/app/webp/input` – place `.png` or `.jpg` files here for processing.
- `dist/app/webp/output` – converted `.webp` files are written here.
- `log/webp.txt` – log of conversions when the service runs.

## Running the service

Use `redo.mk` to start the container:

```bash
r webp
```

The service watches `dist/app/webp/input` and converts anything it finds.
Once finished, the original file is removed and the WebP version
appears under `dist/app/webp/output`.

### Example

```bash
cp foo.png dist/app/webp/input
r webp
ls dist/app/webp/output
```

This will produce `foo.webp` inside `dist/app/webp/output`.

The `setup` target creates the input and output directories if they do
not already exist.
