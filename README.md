## Quickstart

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
