# Flatfile format

The flatfile format stores nested key and value pairs one entry after another.
Each key appears on its own line and may use dot notation for nesting. The
following line holds the value, which may be a scalar, list, or dictionary.
Lists are enclosed by `[` and `]` while dictionaries use `{` and `}`. All values
are stored as strings. Clients should cast them to the desired type after
loading. Files that use this format typically end with the `.flatfile`
extension.

Flatfile handlers are implemented in the `pie.flatfile` module, which exposes
helpers like `load`, `load_key`, `loads`, and `dumps` for working with the
format. The module includes:

`load(path: str) -> dict`
: Read a flatfile from disk.

`load_key(path: str, key: str) -> str`
: Return the value for a single key without reading the entire file.

`loads(data: str) -> dict`
: Parse flatfile text already in memory.

`dumps(mapping: Mapping[str, Any]) -> str`
: Serialize a mapping to flatfile text.

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

## Dictionaries

Values that begin with `{` introduce a dictionary. Each entry inside the
dictionary is written as a key line followed by its value. The dictionary ends
at a line containing `}`:

YAML:

```
pie:
  filling:
    fruit: apple
    sugar: cane
```

Flatfile:

```
pie
{
filling
{
fruit
apple
sugar
cane
}
}
```

## Nested lists and mixed types

List items can themselves be lists, dictionaries, or multi-line strings. Every
element is handled recursively:

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

A list item that is itself a dictionary is wrapped in braces:

YAML:

```
pies:
  - flavor: apple
  - flavor: cherry
```

Flatfile:

```
pies
[
{
flavor
apple
}
{
flavor
cherry
}
]
```

## Converting YAML to flatfile

1. Walk every key path in the YAML document.
2. Join path elements with dots to form the key line.
3. For scalars, write the value on the next line. If the value contains a
   newline or equals `[`, `]`, or `"""`, wrap it between `"""` lines.
4. For sequences, write `[`, render each item using these rules, then write `]`.
5. For mappings, write `{`, render each key and value using these rules, then
   write `}`.

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
desserts
{
pie
{
description
"""
A flaky crust
with butter
"""
ingredients
[
flour
"""
sugar
cane
"""
]
layers
[
[
crust
filling
]
[
icing
]
]
topping
cream
}
}
```

## Working with files

Use `flatfile.load(path)` to read an entire `.flatfile` into a dictionary.
To retrieve a single value without loading the whole file, call
`flatfile.load_key(path, "pie.flavor")`. Cast the returned string yourself if
another type is needed:

```
age = int(flatfile.load_key("people.flatfile", "alice.age"))
```
