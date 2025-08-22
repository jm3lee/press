two ways to include mermaid diagrams

## method 1

use include.py

```mermaid
{{ include("diagram.mmd") }}
```

## method 2

use build rules in redo.mk to generate .svg and include it as an image

![Example flowchart](diagram.svg)
