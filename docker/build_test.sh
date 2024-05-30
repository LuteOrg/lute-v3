#!/bin/bash

docker build -f docker/Dockerfile --build-arg INSTALL_EVERYTHING=true -t lute3 .

docker build -f docker/Dockerfile --build-arg INSTALL_EVERYTHING=false -t lute3-lean .
