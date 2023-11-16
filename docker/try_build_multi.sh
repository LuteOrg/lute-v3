#!/bin/bash
#
# calls "docker build" to build and tag a test multi-platform variant, using buildx
#
# Run this from the root directory:
#
#   ./docker/try_build_multi.sh
set -e

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

TAG="${DOCKERHUB_REPO}:testmultiplatform"

echo
echo "Building $TAG"
echo

# Start a new builder
# docker buildx create --name mybuilder
docker buildx use mybuilder

# See what's available
docker buildx ls

# Build for platforms.
# Have to either --load or --push for built images to be available ...
# Notes
#  --load (to make the image locally available) isn't available for multi-arch builds.
#  --push pushes to docker hub
docker buildx build \
       --push \
       --platform linux/amd64,linux/arm64 \
       -f docker/Dockerfile "$@" \
       --build-arg INSTALL_MECAB=true \
       -t $TAG .

# Remove the current builder
# docker buildx rm mybuilder
