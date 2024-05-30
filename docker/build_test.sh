#!/bin/bash

docker build -f docker/Dockerfile --build-arg INSTALL_EVERYTHING=true -t lute3 .
