Mermaid converts text descriptions into diagrams. This example demonstrates
how to generate a diagram with Press.

Write your diagram in `diagram.mmd`:

```mermaid
flowchart TD
    A[Start] --> B{Is it working?}
    B -- Yes --> C[Great]
    B -- No --> D[Try again]
    D --> B
```

Run `redo` to render the SVG:

```
redo diagram.svg
```

Include the image in your document:

```markdown
![Example flowchart](diagram.svg)
```

Mermaid supports many chart types. The snippet below shows a simple
sequence diagram:

```mermaid
sequenceDiagram
    participant Alice
    participant Bob
    Alice->>Bob: Hello Bob, how are you?
    Bob-->>Alice: I am good thanks!
```

Explore [Mermaid's docs](https://mermaid.js.org/) for more examples.
