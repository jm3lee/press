from __future__ import annotations

from os import PathLike
from typing import Dict, Iterable, Iterator, List, Tuple

SENTINEL = '"""'
LIST_START = '['
LIST_END = ']'



def _set_nested(mapping: Dict, dotted_key: str, value) -> None:
    parts = dotted_key.split('.')
    for part in parts[:-1]:
        mapping = mapping.setdefault(part, {})
    mapping[parts[-1]] = value


def _parse_multiline(it: Iterator[str]) -> str:
    lines: List[str] = []
    for line in it:
        if line == SENTINEL:
            break
        lines.append(line)
    else:
        raise ValueError("Unterminated multi-line value")
    return "\n".join(lines)


def _parse_list(it: Iterator[str]) -> List:
    items: List = []
    for line in it:
        if line == LIST_END:
            break
        items.append(_parse_value(it, line))
    else:
        raise ValueError("Unterminated list")
    return items


def _parse_value(it: Iterator[str], first: str):
    if first == SENTINEL:
        return _parse_multiline(it)
    if first == LIST_START:
        return _parse_list(it)
    return first


def loads(lines: Iterable[str]) -> Dict:
    """Load a flatfile into a nested dictionary."""

    it = iter(line.rstrip("\n") for line in lines)
    result: Dict = {}
    for key in it:
        try:
            first = next(it)
        except StopIteration:
            raise ValueError(f"Missing value for key '{key}'")
        _set_nested(result, key, _parse_value(it, first))
    return result


def _flatten(prefix: str, obj) -> Iterable[Tuple[str, object]]:
    if isinstance(obj, dict):
        for k, v in obj.items():
            dotted = f"{prefix}.{k}" if prefix else k
            yield from _flatten(dotted, v)
    else:
        yield prefix, obj


def _dump_multiline(text: str) -> List[str]:
    return [SENTINEL, *text.splitlines(), SENTINEL]


def _dump_list(items: List) -> List[str]:
    lines = [LIST_START]
    for item in items:
        if isinstance(item, list):
            lines.extend(_dump_list(item))
            continue
        item_str = str(item)
        if item_str in (SENTINEL, LIST_START, LIST_END) or "\n" in item_str:
            lines.extend(_dump_multiline(item_str))
        else:
            lines.append(item_str)
    lines.append(LIST_END)
    return lines


def _dump_value(value) -> List[str]:
    if isinstance(value, list):
        return _dump_list(value)
    value_str = str(value)
    if "\n" in value_str or value_str == SENTINEL:
        return _dump_multiline(value_str)
    return [value_str]


def dumps(mapping: Dict) -> str:
    """Serialize a mapping into flatfile format."""

    lines: List[str] = []
    for key, value in _flatten("", mapping):
        lines.append(key)
        lines.extend(_dump_value(value))
    return "\n".join(lines) + "\n"


def load(path: str | PathLike[str]) -> Dict:
    """Read *path* and return a nested dictionary."""

    with open(path, encoding="utf-8") as fh:
        return loads(fh)


def load_key(path: str | PathLike[str], dotted_key: str) -> str:
    """Return the string value for *dotted_key* from *path*.

    The file is scanned until the key is found. Multi-line values are
    supported. Lists raise ``TypeError``.
    """

    with open(path, encoding="utf-8") as fh:
        it = iter(line.rstrip("\n") for line in fh)
        for key in it:
            try:
                first = next(it)
            except StopIteration:
                raise ValueError(f"Missing value for key '{key}'")
            if key == dotted_key:
                value = _parse_value(it, first)
                if isinstance(value, list):
                    raise TypeError(f"Value for key '{key}' is a list")
                return value
            _parse_value(it, first)
        raise KeyError(dotted_key)

