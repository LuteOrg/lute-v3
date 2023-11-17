#!/bin/bash

docker build -f docker/Dockerfile --build-arg INSTALL_MECAB=true -t lute3 .
