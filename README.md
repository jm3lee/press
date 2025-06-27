## Quickstart

1. Edit `docker-compose.yml`. Adjust `image` as necessary. *In the future,
   provide users with templates or wizards. Need examples.*
2. Edit `redo.mk`. Update the list of services.
3. Edit documents under `src/`.
4. Optionally customize `src/pandoc-template.html` for your project.
5. Edit `docker` rule in `redo.mk` if you'd like to push docker images to a
   container registry.
6. See `docs/redo-mk.md` for descriptions of the available `make` targets.

### General Setup

```
alias r='make -f redo.mk'
r setup
```

### webp converter

```
cp foo.png app/webp/input
r webp
ls app/webp/output
```

## Wish List

- May need a wizard

## Jinja2 Template Rendering

Script: `app/shell/bin/render_template`

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
- `citation`: The default inline text used for hyperlinks to this document.

### Examples
- **Sidecar metadata**  
  Store metadata in `index.yml` and content in `index.md`.  
- **Inline metadata**  
  Embed the YAML block directly at the top of `quickstart.md`.
