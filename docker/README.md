# Docker and scripts

## Local test builds

```
./docker/build_test.sh
```

The `docker-compose.yml.example` in this directory works with the `build_test.sh` image; copy that file to root, rename things, and then it should work:

```
./docker/build_test.sh && docker compose up
```

## Building and pushing

Build and push all variants:

```
./docker/build_all.sh
```

## Using

See ./docker_hub_overview.md (the contents of which are copied/pasted into the "Repository overview" on docker hub).
