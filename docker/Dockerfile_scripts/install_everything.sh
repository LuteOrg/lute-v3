#!/bin/sh
#
# Install all the extra stuff when using INSTALL_EVERYTHING
# in the Dockerfile.

# Mecab
apt-get update -y
apt-get install -y mecab mecab-ipadic-utf8
apt-get clean && rm -rf /var/lib/apt/lists/*

# Mandarin.
pip install lute3-mandarin
