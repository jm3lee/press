Press is a static-site generator built on Pandoc and Docker. It uses
`docker-compose` together with `redo.mk` to orchestrate services for building
and serving content. The project includes helpers for rendering Markdown to HTML
or PDF, converting images to WebP, and customizing Jinja templates. It's meant
for building documentation or other small websites that can be served from a
containerized Nginx instance.

### Makefiles

The build relies on three cooperating Makefiles:

- **`redo.mk`** – run from the host to launch Docker containers and kick off
  builds.
- **`app/shell/mk/build.mk`** – executed by `make` inside the shell container to
  generate the site.
- **`dep.mk`** – optional file included by `build.mk` for custom dependencies.
  See [dist/docs/dep-mk.md](dist/docs/dep-mk.md).

## Quickstart

1. Run `git submodule update --init --recursive` after cloning to fetch
   required submodules such as `xmera`.
2. Edit `dist/docker-compose.yml`. Adjust `image` as necessary. **TODO: Examples**
3. Edit `redo.mk`. Update the list of services.
4. Edit documents under `src/`.
5. Optionally customize `src/pandoc-template.html` for your project.
6. Edit `docker` rule in `redo.mk` if you'd like to push docker images to a
   container registry.
7. Run `r help` (or `make -f redo.mk help`) to see available tasks. See
   `dist/docs/redo-mk.md` for more details.

### Install prerequisites

Install Docker and `make` using your package manager.
For example on Debian/Ubuntu:

```bash
sudo apt-get install docker.io make
```

On macOS with Homebrew:

```bash
brew install --cask docker
brew install make
```

### Build and start the environment

```bash
alias r='make -f redo.mk'
r setup   # build images and prepare volumes
r up      # start the development stack
```

Set `VERBOSE=1` to see the actual commands executed by `make`:

```bash
r up VERBOSE=1
```

### Shut down the stack

```bash
r down
```

### webp converter

```
cp foo.png app/webp/input
r webp
ls app/webp/output
```
See [dist/docs/webp-service.md](dist/docs/webp-service.md) for more about how the
converter works.

## Wish List

- May need a wizard

## Jinja2 Template Rendering

Script: `app/shell/bin/render_jinja_template`

You can put metadata at the top of a markdown file. This metadata is optional.
The system collects it. Then it uses it to fill Jinja2 templates.

Custom filters:

- `linktitle`: formats `linktext` as a title.
- `linkcap`: capitalizes `linktext` (for the start of a sentence).

## Overriding Python Modules

In `dist/docker-compose.yml`, map `./app/shell/py` to `/press/py`. Python modules are
installed using the `-e` flag so you can edit them in place without reinstalling
Python modules.

```
shell:
  image: press-shell
  volumes:
    - ./app/shell/py:/press/py
```

## Document Metadata

Pandoc lets you define document metadata in two ways:

1. **Inline**: Add a YAML block at the beginning of your Markdown file.  
2. **Sidecar**: Place a separate `.yml` file alongside your Markdown.

### Required Field
- `name`: The display name of the document.

### Auto-Generated Fields
If you don’t provide these, Pandoc (or your build tooling) will generate them automatically:
- `id`: A unique identifier for cross-document linking (e.g., when using Jinja templates).
- `citation`: Default anchor text for cross-document links. Jinja filters such as `linktitle` use this value.

See [dist/docs/metadata-fields.md](dist/docs/metadata-fields.md) for a complete list of supported fields and defaults.

### Examples
- **Sidecar metadata**  
  Store metadata in `index.yml` and content in `index.md`.  
- **Inline metadata**
  Embed the YAML block directly at the top of `quickstart.md`.

## picasso

`picasso` scans YAML metadata files and generates Makefile rules to render them
with Pandoc. The output is written to `build/picasso.mk` and included during the
build. Use `--src DIR` to search a different directory for `.yml` files and
`--build DIR` to change where generated rules point.

## Further Reading

- [Jinja Filters](dist/docs/jinja-filters.md)
- [Jinja Globals](dist/docs/jinja-globals.md)
- [Build Index](dist/docs/build-index.md)
- [update-index](dist/docs/update-index.md)
- [Quiz Workflow](dist/docs/quiz-workflow.md)
- [include-filter](dist/docs/include-filter.md)
- [preprocess](dist/docs/preprocess.md)
- [picasso](dist/docs/picasso.md)
- [gen-markdown-index](dist/docs/gen-markdown-index.md)
- [process-yaml](dist/docs/process-yaml.md)
- [Nginx Dockerfile](dist/docs/nginx.md)
- [docker-make](dist/docs/docker-make.md)
- [WebP Service](dist/docs/webp-service.md)
- [check-page-title](dist/docs/check-page-title.md)
