# Codex Guidelines

## General Formatting

- Wrap **paragraph text** at 80 characters.
  (Code, tables, and lists are exempt.)
- Within `<pre>` blocks:
  - Use two spaces for indentation.
  - Prefer breaking lines at 80 characters on word boundaries.
  - If no suitable word boundary exists, leave the line unbroken.
- Metadata:
  - `description`: plain text only
- Math: always use `$ ... $` or `$$ ... $$`  
  (never `\(`, `\)`, `\[`, `\]`)
- Makefiles: **indent with real tab characters** for recipe lines.
  Leading spaces will break Makefile syntax. Never replace tabs with spaces.
- Documentation: write as an **expert engineer**.
  Provide enough detail for new team members.
- When generating links with anchors, ensure that the target anchor exists.
  Create the anchor if it is missing.
- Flashoffer updates: whenever `app/shell/py/pie/pie/flashoffer.py` or related
  helpers change, also refresh
  `docs/guides/flashoffer-codex-instructions.md` to keep Codex guidance in
  sync.
- When modifying Flashoffer methods, ensure any text rendered to end users is
  configurable via function parameters.
- Node.js projects: modify `package.json` and `package-lock.json` only when
  the dependency list changes.

## `docker-compose.yml`

- Always document services with comments that explain ongoing maintenance and
  operational expectations.
- Group related services together and sort them alphabetically within their
  groupings.

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

Thresholds (apply to **all** languages in this repository — Python and
JavaScript/TypeScript):

- **Function level**: warn > 7, fail > 10
- **Class level**: max total ≤ 50
- **Module level**: max total ≤ 100

Range interpretation:

- 1–5: excellent
- 6–10: acceptable
- 11–20: risky — refactor recommended
- >20: very high risk — must refactor

### Enforcement

- **Python**: enforce with `radon`/`xenon` in CI; fail builds if thresholds are
  exceeded.
- **JavaScript/TypeScript**: enforce with ESLint (`complexity` rule) in CI;
  fail builds if thresholds are exceeded.

### Testing

- In tests, always ensure the following is executed before accessing templates:

  ```python
  os.environ.setdefault(
      "PIE_DATA_DIR",
      "/data/src/templates",
  )
  ```
- Avoid creating stubs or shims for Python dependencies in tests whenever
  possible; assume that required Python modules are available in the testing
  environment.
- When tests fail due to missing Python packages, install the dependencies
  needed for the suite instead of skipping tests or introducing stand-ins.
