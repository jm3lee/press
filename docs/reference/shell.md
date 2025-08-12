# shell

Run the project's shell service defined in docker-compose. If no command is specified, an interactive shell is launched.

```bash
shell [-u [UID]] [-- COMMAND...]
```

- `-u [UID]` – run as the given numeric user ID. When UID is omitted, the current user's UID is used.

Arguments after `--` are passed to the container's entry point.
