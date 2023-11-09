# The docker container

The Dockerfile can be used to create two variants: one with mecab and dictionary (800+ MB) , and one without (300 MB).

## Building

Sample build, run from the root folder.  `INSTALL_MECAB` is `true` or `false`

```
docker build -f docker/Dockerfile --build-arg INSTALL_MECAB=false -t lute3 .
```

## Starting

The Docker image is configured to write to directories in the container which must be mounted from the host:

* `/lute_data`: the database, user images, etc.
* `/lute_backup`: your backups

If these directories are not mounted, the container will not start.

### From the command line:

```
docker run -p 5000:5000 -v ./my_data:/lute_data -v ./my_backups:/lute_backup --name my-lute lute3:latest
```

The above:

* runs the container from the lute3:latest image
* exposes port 5000 on the host (so localhost:5000 works)
* mounts the necessary directories
* names the container "my-lute".

### From a compose file

```
# Sample docker-compose.yml file
version: '3.9'
services:
  lute:
    image: lute3:latest
    name: my-lute
    ports:
      - 5000:5000
    volumes:
      - ./my_data:/lute_data
      - ./my_backups:/lute_backup
```

With that file in some location, you could do:

```
docker compose up -d
```

A `docker-compose.yml.example' is provided as a starting point in this directory -- copy that to a docker-compose.yml file in project root and use it:

```
docker compose up -d

python -m utils.verify

docker compose stop lute
```

## Stopping

If you started the container from the command line, you'll need to get the container ID, and then stop it.

```
docker ps   # lists all running IDs
docker stop <containerID>   # ID found in prev. command
```

If you started it with `docker compose`, you can do

```
docker compose stop
```