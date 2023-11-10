#!/bin/bash
#
# calls "docker build" to build and tag lute3 variants, and optionally push.
#
# Run this from the root directory:
#
#   ./docker/build_all.sh
#
# Any arguments given to this script are passed to the build command, eg:
#
#   ./docker/build_all.sh --no-cache
#
# To also push the images to docker hub, set a DO_PUSH environment variable:
#
#   DO_PUSH=1 ./docker/build_all.sh
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

TAG="${DOCKERHUB_REPO}:${VERSION}"
LATEST="${DOCKERHUB_REPO}:latest"
LEANTAG="${DOCKERHUB_REPO}:${VERSION}-lean"
LEANLATEST="${DOCKERHUB_REPO}:latest-lean"

echo
echo "Building $TAG"
echo

docker build -f docker/Dockerfile "$@" \
       --build-arg INSTALL_MECAB=true \
       -t $TAG .

docker tag $TAG $LATEST

echo
echo "Building $LEANTAG"
echo

docker build -f docker/Dockerfile "$@" \
       --build-arg INSTALL_MECAB=false \
       -t $LEANTAG .

docker tag $LEANTAG $LEANLATEST

echo
echo "Done.  Images created:"
echo
echo $TAG
echo $LATEST
echo $LEANTAG
echo $LEANLATEST
echo

if [ -z "$DO_PUSH" ]; then
    echo "Images NOT pushed to docker hub.  Run this with DO_PUSH env var to push."
    echo
else
    echo "Pushing images."
    for t in $TAG $LATEST $LEANTAG $LEANLATEST; do
        echo
        echo "Push $t"
        docker push $t
    done
    echo
    echo "Done, images pushed."
fi
