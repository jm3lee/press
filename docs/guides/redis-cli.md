# redis-cli helper

`bin/redis-cli` wraps `docker compose exec dragonfly redis-cli` to connect to the
project's DragonflyDB/Redis instance. Any arguments passed to the script are
forwarded to `redis-cli`.

## Usage

```bash
./bin/redis-cli
./bin/redis-cli --scan --pattern '*'
```

The Docker compose stack must be running and include the `dragonfly` service.
You can also run the same client via `make -f redo.mk redis`.
