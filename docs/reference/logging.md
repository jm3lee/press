# Logging

The `pie.logging` module centralizes logging for command line helpers. It
configures a `loguru.Logger` instance named `logger` at import time so all
tools share the same behavior.

## Logger Configuration

Default handlers provided by `loguru` are removed to allow explicit control
over sinks. `LOG_FORMAT` defines a consistent layout:

```
{time:HH:mm:ss} {module:>10.10}:{function:<15.15}:{line:<4} {level:.1s} {message} {extra}
```

A console sink targeting `sys.stderr` is added at level `INFO`.

## `configure_logging(verbose, log_path)`

Rebuild the logger configuration for a command line tool. When `verbose` is
`True` the console sink uses level `DEBUG`; otherwise it uses `INFO`. Existing
sinks are cleared, a new console sink is added with the chosen level, and
`setup_file_logger` adds a file sink when `log_path` is provided.

## `add_file_logger(filename, level="DEBUG")`

Add a sink that writes to `filename` using `LOG_FORMAT`. The sink defaults to
the `DEBUG` level, capturing detailed traces while leaving console output less
noisy.

## `disable_logging()`

Remove all configured sinks to silence the logger entirely. Call this when a
tool must suppress log output.
