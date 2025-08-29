# Codex

- text formatting:
  - use 80 char columns for paragraphs only
- metadata management:
  - write `description` in plain text
  - use `_` instead of `-` when modifying `id` 
- When editing math, always use `$` and `$$` instead of `\( \)` or `\[ \]`.
- When editing makefiles, make sure to indent with tabs, not spaces.
- When writing software documentation, write as an expert software engineer.
  Give enough details to help new engineers on the team.

## Python

pytest dependencies: see `app/shell/py/pie/requirements.txt`

pie.logging.logger is an instance of loguru logger.

Use cyclomatic complexity thresholds for Python code:

- Function level: warn at CC > 7, fail at CC > 10
- Class level: maximum CC total ≤ 50
- Module level: maximum CC total ≤ 100

Interpret ranges as:
- 1–5: excellent
- 6–10: acceptable
- 11–20: risky, needs refactor
- >20: very high risk, must refactor

Enforce with radon/xenon in CI to fail builds if thresholds are exceeded.
