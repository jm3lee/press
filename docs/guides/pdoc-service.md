# pdoc documentation service

The `pdoc` service serves API documentation for the `pie` package using [pdoc](https://pdoc.dev).
It is disabled by default so it only runs when explicitly requested.

## Running the service

Start the container using the `pdoc` profile:

```bash
docker compose --profile pdoc up --remove-orphans pdoc
```

Then open <http://localhost:8080> in your browser to explore the documentation.

The service mounts the local `pie` sources, so edits are reflected without rebuilding the image.
