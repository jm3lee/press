# Flatfile format

The flatfile format stores nested key and value pairs one entry after another.
Each key appears on its own line and may use dot notation for nesting. The
following line holds the value. All values are stored as strings. Clients should
cast them to the desired type after loading.

```
pie.flavor
apple
```

`flatfile.loads` turns this into `{\"pie\": {\"flavor\": \"apple\"}}`.

## Keys and nesting

Dot notation lets the file express nested mappings. A YAML fragment

```
desserts:
  pie:
    flavor: apple
```

becomes

```
desserts.pie.flavor
apple
```

## Multi-line values

Insert a line containing `"""` immediately after the key. All lines until the
closing sentinel become the value:

YAML:

```
description: |
  A flaky crust
  with butter
```

Flatfile:

```
pie.description
"""
A flaky crust
with butter
"""
```

## Lists

Values that begin with `[` introduce a list. Each item is parsed using the same
rules as top level values and the list ends at a line containing `]`. YAML lists
map directly to this structure:

YAML:

```
ingredients:
  - flour
  - water
  - butter
```

Flatfile:

```
pie.ingredients
[
flour
water
butter
]
```

## Nested lists and mixed types

List items can themselves be lists or multi-line strings. Every element is
handled recursively:

YAML:

```
layers:
  - [crust, filling]
  - [icing]
```

Flatfile:

```
pie.layers
[
[
crust
filling
]
[
icing
]
]
```

A list item with multiple lines uses the sentinel as well:

YAML:

```
ingredients:
  - flour
  - |
      sugar
      cane
```

Flatfile:

```
pie.ingredients
[
flour
"""
sugar
cane
"""
]
```

## Converting YAML to flatfile

1. Walk every key path in the YAML document.
2. Join path elements with dots to form the key line.
3. For scalars, write the value on the next line. If the value contains a
   newline or equals `[`, `]`, or `"""`, wrap it between `"""` lines.
4. For sequences, write `[`, render each item using these rules, then write `]`.
5. Repeat for nested mappings.

### Full example

YAML:

```
desserts:
  pie:
    description: |
      A flaky crust
      with butter
    ingredients:
      - flour
      - |
          sugar
          cane
    layers:
      - [crust, filling]
      - [icing]
    topping: cream
```

Flatfile:

```
desserts.pie.description
"""
A flaky crust
with butter
"""
desserts.pie.ingredients
[
flour
"""
sugar
cane
"""
]
desserts.pie.layers
[
[
crust
filling
]
[
icing
]
]
desserts.pie.topping
cream
```

## Working with files

Use `flatfile.load(path)` to read an entire file into a dictionary.
To retrieve a
single value without loading the whole file, call `flatfile.load_key(path,
"pie.flavor")`. Cast the returned string yourself if another type is needed:

```
age = int(flatfile.load_key("people.ff", "alice.age"))
```
