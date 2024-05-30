# The Dockerfile can be used to create two variants
# by using "--build-arg INSTALL_EVERYTHING=[true|false]":
# - "true": with mecab and dictionary, mandarin parser (800+ MB)
# - "false": without (230 MB)
#
# e.g.  docker build --build-arg INSTALL_EVERYTHING=true -t lute3 .

# Official python base image.
FROM python:3.11-slim-bookworm

WORKDIR /lute

# Install base.
ENV PIP_ROOT_USER_ACTION=ignore
RUN pip install lute3
COPY lute/config/config.yml.docker ./config.yml

# Define a build argument with a default value.
ARG INSTALL_EVERYTHING=false

# Add mecab.
RUN if [ "$INSTALL_EVERYTHING" = "true" ]; then \
    apt-get update -y && \
    apt-get install -y mecab mecab-ipadic-utf8 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*; \
    fi

EXPOSE 5000

# Start script.
COPY docker/check_mounts_and_start.sh ./start.sh
RUN chmod +x ./start.sh
ENTRYPOINT ["/lute/start.sh"]
