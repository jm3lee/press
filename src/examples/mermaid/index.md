# Mermaid Example

This short tutorial shows how to render a Mermaid diagram during the build.

The source lives in `diagram.mmd`:

```mermaid
{{ include("diagram.mmd") }}
```

The `src/dep.mk` file copies the source into the build tree and invokes the
Mermaid CLI:

```make
all: build/examples/mermaid/diagram.mmd

build/examples/mermaid:
        mkdir -p $@

build/examples/mermaid/diagram.mmd: src/examples/mermaid/diagram.mmd | \
    build/examples/mermaid
        cp $< $@
```

The rule above uses a pattern from `redo.mk` to convert the copied `.mmd`
file into `diagram.svg`.

Refer to the generated image below:

![Example flowchart](diagram.svg)
