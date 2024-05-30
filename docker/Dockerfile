# The Dockerfile can be used to create two variants
# by using "--build-arg INSTALL_EVERYTHING=[true|false]":
# - "true": with mecab and dictionary, mandarin parser (800+ MB)
# - "false": without (300 MB)
#
# e.g.  docker build --build-arg INSTALL_EVERYTHING=true -t lute3 .

# Official python base image.
FROM python:3.11-slim-bookworm

# Define a build argument with a default value.
ARG INSTALL_EVERYTHING=false

# Mecab.
RUN if [ "$INSTALL_EVERYTHING" = "true" ]; then \
    apt-get update -y && \
    apt-get install -y mecab mecab-ipadic-utf8 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*; \
    fi

# Lute code and config.
COPY requirements.txt .
ENV PIP_ROOT_USER_ACTION=ignore
RUN pip install -r requirements.txt
COPY lute /lute
RUN mv /lute/config/config.yml.docker /lute/config/config.yml

EXPOSE 5000

# Start script.
COPY docker/check_mounts_and_start.sh /lute/start.sh
RUN chmod +x /lute/start.sh
ENTRYPOINT ["/lute/start.sh"]
