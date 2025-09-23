# Codex Guidelines

## General Formatting

- Wrap **paragraph text** at 80 characters.
  (Code, tables, and lists are exempt.)
- Metadata:
  - `description`: plain text only
  - `id`: use `_` instead of `-` when modifying
- Math: always use `$ ... $` or `$$ ... $$`  
  (never `\(`, `\)`, `\[`, `\]`)
- Makefiles: **indent with real tab characters** for recipe lines.
  Leading spaces will break Makefile syntax. Never replace tabs with spaces.
- Documentation: write as an **expert engineer**.
  Provide enough detail for new team members.

## Checker Scripts

- When generating Codex checker scripts, always include ExcludeList support.
  Ensure the script accepts an `--exclude` argument that reads from an
  `ExcludeList` file and skips matching paths.

## Python

### Dependencies

- `pytest` dependencies: see
  [`app/shell/py/pie/requirements.txt`](app/shell/py/pie/requirements.txt)
- `pie.logging.logger`: instance of `loguru.Logger`
- Prefer structured logging (e.g., `logger.bind(...)`) to capture context with
  Loguru; avoid plain string interpolation.
- Use data models from `pie.model` when possible. If a new data model is
  required, add it to `pie.model` with minimal changes.
- Whenever data models are edited, update all relevant code, tests, and
  documentation.

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

### Testing

- In tests, always ensure the following is executed before accessing templates:

  ```python
  os.environ.setdefault(
      "PIE_DATA_DIR",
      "/data/src/templates",
  )
  ```
