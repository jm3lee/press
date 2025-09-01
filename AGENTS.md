# Codex Guidelines

## General Formatting

- Wrap **paragraph text** at 80 characters.  
  (Code, tables, and lists are exempt.)
- Metadata:
  - `description`: plain text only
  - `id`: use `_` instead of `-` when modifying
- Math: always use `$ ... $` or `$$ ... $$`  
  (never `\(`, `\)`, `\[`, `\]`)
- Makefiles: **indent with tabs**, not spaces
- Documentation: write as an **expert engineer**.  
  Provide enough detail for new team members.

## Python

### Dependencies

- `pytest` dependencies: see  
  [`app/shell/py/pie/requirements.txt`](app/shell/py/pie/requirements.txt)
- `pie.logging.logger`: instance of `loguru.Logger`

### Cyclomatic Complexity

Thresholds:

- **Function level**: warn > 7, fail > 10
- **Class level**: max total ≤ 50
- **Module level**: max total ≤ 100

Range interpretation:

- 1–5: excellent
- 6–10: acceptable
- 11–20: risky — refactor recommended
- >20: very high risk — must refactor

### Enforcement

- Use `radon`/`xenon` in CI
- Fail builds if thresholds are exceeded
