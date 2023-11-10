# Docker and scripts

## Building

tl/dr: To build and push all variants:

```
DO_PUSH=1 ./docker/build_all.sh
```

Building single image:

```
docker build -f docker/Dockerfile --build-arg INSTALL_MECAB=false -t lute3 .
```

## Using

See ./docker_hub_overview.md (the contents of which are copied/pasted into the "Repository overview" on docker hub).
