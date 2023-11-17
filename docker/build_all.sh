#!/bin/bash
#
# calls "docker buildx build" to build and tag lute3 variants and push them.
#
# This assumes there's a buildx builder called "mybuilder".
# To create a buildx builder with this name:
#   docker buildx create --name mybuilder
#
# Run this from the root directory:
#
#   ./docker/build_all.sh
#
# Any arguments given to this script are passed to the build command, eg:
#
#   ./docker/build_all.sh --no-cache
#
set -e

# Use builder, sanity check.
docker buildx use mybuilder
docker buildx ls

# Destination repo, may change to an org.
DOCKERHUB_REPO=jzohrab/lute3

# Read version from python (throws if missing).
VERSION=$(python -c "import lute; print(lute.__version__)")

if [ -z "$VERSION" ]; then
    echo
    echo "Couldn't find lute version, quitting"
    echo
    exit 1
fi

TAG="${DOCKERHUB_REPO}:${VERSION}"
LATEST="${DOCKERHUB_REPO}:latest"
LEANTAG="${DOCKERHUB_REPO}:${VERSION}-lean"
LEANLATEST="${DOCKERHUB_REPO}:latest-lean"

echo
echo "Build and push $TAG, $LATEST"
echo

docker buildx build \
       --push \
       --platform linux/amd64,linux/arm64 \
       -f docker/Dockerfile "$@" \
       --build-arg INSTALL_MECAB=true \
       -t $TAG -t $LATEST .

echo
echo "Build and push $LEANTAG, $LEANLATEST"
echo

docker buildx build \
       --push \
       --platform linux/amd64,linux/arm64 \
       -f docker/Dockerfile "$@" \
       --build-arg INSTALL_MECAB=false \
       -t $LEANTAG -t $LEANLATEST .

echo
echo "Done.  Images created and pushed:"
echo
echo $TAG
echo $LATEST
echo $LEANTAG
echo $LEANLATEST
echo
