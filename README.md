Press is a static-site generator built on Pandoc and Docker. It uses
`docker compose` together with `redo.mk` to orchestrate services for building
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
  See [docs/guides/dep-mk.md](docs/guides/dep-mk.md).

These Makefiles centralize key directories through variables so paths can be
adjusted in one place:

- `SRC_DIR` – source files (default `src`)
- `BUILD_DIR` – generated output (default `build`)
- `LOG_DIR` – log files (default `log`)
- `CFG_DIR` – configuration files (default `cfg`)

`SRC_DIR` and `BUILD_DIR` are mirrored in `redo.mk` to keep host targets and
container builds aligned.

## Quickstart

1. Clone the repository.
2. Edit `docker-compose.yml`. Adjust `image` as necessary. **TODO: Examples**
3. Edit `redo.mk`. Update the list of services.
4. Edit documents under `src/` (or your configured `SRC_DIR`).
5. Optionally customize `src/pandoc-template.html` for your project.
6. Edit `docker` rule in `redo.mk` if you'd like to push docker images to a
   container registry.
7. Run `r help` (or `make -f redo.mk help`) to see available tasks. See
   `docs/guides/redo-mk.md` for more details.

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
See [docs/guides/webp-service.md](docs/guides/webp-service.md) for more about how the
converter works.

### pdoc documentation server

Use [pdoc](https://pdoc.dev) to browse API docs for the `pie` package.
Start the service with the optional profile:

```bash
docker compose --profile pdoc up pdoc
```

Open <http://localhost:8080> to view the documentation.

## Redis Configuration

The build tools connect to DragonflyDB/Redis using the `REDIS_HOST` and
`REDIS_PORT` environment variables. These default to `dragonfly` and `6379`
respectively when not set.

## Wish List

- May need a wizard

## Jinja2 Template Rendering

Command: `render-jinja-template`

You can put metadata at the top of a markdown file. This metadata is optional.
The system collects it. Then it uses it to fill Jinja2 templates.

Custom filters:

- `linktitle`: formats `linktext` as a title.
- `linkcap`: capitalizes `linktext` (for the start of a sentence).

## Overriding Python Modules

In `docker-compose.yml`, map `./app/shell/py` to `/press/py`. Python modules are
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
- `citation`: Default anchor text for cross-document links. Jinja filters such as `linktitle` use this value. For bibliographic references this may instead be a mapping with `author`, `year`, and `page`, which the filters and the `cite` global render as Chicago style text in parentheses.

See [docs/reference/metadata-fields.md](docs/reference/metadata-fields.md) for a complete list of supported fields and defaults. For describing
external URLs in YAML, refer to [docs/reference/link-metadata.md](docs/reference/link-metadata.md).

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

- [Jinja Filters](docs/reference/jinja-filters.md)
- [Jinja Globals](docs/reference/jinja-globals.md)
- [Build Index](docs/guides/build-index.md)
- [update-index](docs/guides/update-index.md)
- [Quiz Workflow](docs/guides/quiz-workflow.md)
- [include-filter](docs/guides/include-filter.md)
- [preprocess](docs/guides/preprocess.md)
- [picasso](docs/guides/picasso.md)
- [gen-markdown-index](docs/guides/gen-markdown-index.md)
- [process-yaml](docs/guides/process-yaml.md)
- [Nginx Dockerfile](docs/guides/nginx.md)
- [make](docs/guides/make.md)
- [WebP Service](docs/guides/webp-service.md)
- [check-page-title](docs/guides/check-page-title.md)
- [Architecture](docs/reference/architecture.md)
- [Link Metadata](docs/reference/link-metadata.md)
- [checklinks](docs/guides/checklinks.md)
