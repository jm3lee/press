"""
link.py: Perform in-place substitutions on one or more files.

Usage:
    link.py <filename> <filename> ...

For each file:
1. Read its content.
2. Perform substitutions defined in `SUBSTITUTIONS`.
   - Each key can be a regex pattern (string) or a callable returning (pattern, repl).
3. Write the modified content back to the original file.
"""
import re
import sys
from typing import Callable, Dict, List, Pattern, Tuple, Union


def expand_with_anchor(m):
    name = m.group(1)
    url = name.lower() + ".html"
    anchor = m.group(2)
    if anchor:
        s = f"(/{url}{anchor})"
    else:
        s = f"(/{url})"
    return s


# Define your substitutions here.
# The key can be:
# - A regex pattern (string) mapping to a replacement string.
# - A regex pattern mapping to a callable: Callable[[re.Match], str].
# Example:
# {
#   r"foo": "bar",\#   r"date:(\\d{4}-\\d{2}-\\d{2})": lambda m: f"DATE[{m.group(1)}]",
# }
SubstitutionValue = Union[str, Callable[[re.Match], str]]
SUBSTITUTIONS: Dict[str, SubstitutionValue] = {
    r"<3d>": "**[3D](/resources/#3d)**",
    r"<Anc>": "[Anconeus](/anconeus.html)",
    r"<anc>": "[anconeus](/anconeus.html)",
    r"<Bc>": "[Biceps](/biceps.html)",
    r"<bc>": "[biceps](/biceps.html)",
    r"<Dt>": "[Deltoid](/deltoid.html)",
    r"<dt>": "[deltoid](/deltoid.html)",
    r"<FCU>": "[Flexor Carpi Ulnaris](/flexor-carpi-ulnaris.html)",
    r"<fcu>": "[flexor carpi ulnaris](/flexor-carpi-ulnaris.html)",
    r"<gf>": "[Goldfinger 1991](/resources/index.html#gf)",
    r"<humerus#insertion>": "[humerus](/humerus.html#insertion)",
    r"<Humerus>": "[Humerus](/humerus.html)",
    r"<humerus>": "[humerus](/humerus.html)",
    r"<ld>": "[latissimus dorsi](/latissimus-dorsi.html)",
    r"<ProTrs>": "[Pronator Teres](/pronator-teres.html)",
    r"<protrs>": "[pronator teres](/pronator-teres.html)",
    r"<Radius>": "[Radius](/radius.html)",
    r"<radius>": "[radius](/radius.html)",
    r"<Sartorius>": "[Sartorius](/sartorius.html)",
    r"<sartorius>": "[sartorius](/sartorius.html)",
    r"<Scapula>": "[Scapula](/scapula/)",
    r"<scapula>": "[scapula](/scapula/)",
    r"<Teres Minor>": "[Teres Minor](/teres-minor.html)",
    r"<Trc>": "[Triceps](/triceps.html)",
    r"<trc>": "[triceps](/triceps.html)",
    r"<Triceps>": "[Triceps](/triceps.html)",
    r"<triceps>": "[triceps](/triceps.html)",
    r"<trsmaj>": "[teres major](/teres-major.html)",
    r"<TrsMin>": "[Teres Minor](/teres-minor.html)",
    r"<Trz>": "[Trapezius](/trapezius.html)",
    r"<trz>": "[trapezius](/trapezius.html)",
    r"<Brc>": "[Brachialis](/brachialis.html)",
    r"<brc>": "[brachialis](/brachialis.html)",
    r"{{([a-zA-Z_\-/]+)(#[a-zA-Z_-]+)?}}": expand_with_anchor,
}


def apply_substitutions(
    content: str, substitutions: Dict[str, SubstitutionValue]
) -> str:
    """
    Apply all substitutions to the content string.

    :param content: Original text.
    :param substitutions: Mapping of regex patterns to replacement strings or callables.
    :return: Modified text.
    """
    # Compile all patterns
    compiled: List[Tuple[Pattern, SubstitutionValue]] = []
    for pat, repl in substitutions.items():
        compiled.append((re.compile(pat), repl))

    # Apply each substitution sequentially
    for pattern, repl in compiled:
        content = pattern.sub(repl, content)  # type: ignore
    return content


def process_file(path: str):
    """
    Read file, apply substitutions, and overwrite the file.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            original = f.read()
    except FileNotFoundError:
        print(f"File not found: {path}", file=sys.stderr)
        return

    modified = apply_substitutions(original, SUBSTITUTIONS)

    # Only write if changes occurred
    if modified != original:
        with open(path, "w", encoding="utf-8") as f:
            f.write(modified)
        print(f"Updated: {path}")
    else:
        print(f"No changes: {path}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    for filepath in sys.argv[1:]:
        process_file(filepath)


if __name__ == "__main__":
    main()
