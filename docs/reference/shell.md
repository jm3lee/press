# shell

Run the project's shell service defined in the Docker Compose stack. Invoke the
helper from `bin/shell`; if no command is supplied, an interactive shell is
launched inside the container.

```bash
./bin/shell [-u [UID]] [-- COMMAND...]
```

- `-u [UID]` – run as the given numeric user ID. When UID is omitted, the
  current user's UID is used.

Arguments after `--` are passed to the container's entry point.
