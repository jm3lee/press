# sync service

The `sync` service uploads site files to an S3 bucket using [`s3cmd`](https://s3tools.org/s3cmd). It uses the image under `app/s3` and runs `/app/bin/sync` in a loop.

## Directories

- `../s3` – host directory whose contents are uploaded.

## Running the service

Use `redo.mk` to build and start the container:

```bash
r sync
```

The service mirrors the host `s3/` directory to the bucket specified by
`S3_BUCKET_PATH` (default `s3://press`). Credentials come from the file at
`S3CFG_PATH` (default `/root/.s3cfg`). Configure these values in the
project's `.env` file.

Files removed locally are deleted from the bucket via `s3cmd --delete-removed --delete-after --acl-public`.
