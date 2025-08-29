# Flatfile format

The flatfile format stores nested key and value pairs one entry after another.
Each key lives on its own line and may use dot notation for nesting. The value
follows on the next line.

```
pie.flavor
apple
```

`loads` turns this into `{"pie": {"flavor": "apple"}}`.

## Multi-line values

Insert a line containing `"""` immediately after the key. All lines until the
closing sentinel become the value:

```
pie.description
"""
A flaky crust
with butter
"""
```

## Lists

Values that begin with `[` are treated as lists. Each item is parsed using the
same rules as top-level values and the list ends at a line containing `]`.

## Working with files

Use `flatfile.load(path)` to read an entire file into a dictionary. To retrieve
a single value without loading the whole file, call
`flatfile.load_key(path, "pie.flavor")`. Cast the returned string yourself if
another type is needed:

```
age = int(flatfile.load_key("people.ff", "alice.age"))
```
