<!-- Description to be copy-pasted into the "Repository overview" in hub.docker.com -->

# What is Lute v3?

LUTE (Learning Using Texts) is an application for learning foreign languages through reading.

<img src="https://luteorg.github.io/lute-manual/assets/intro.gif" width="700">

For more information, see the [Lute manual](https://luteorg.github.io/lute-manual/).

# How to use this image

```
docker run -p 5000:5000 -v <MY_DATA_PATH>:/lute_data -v <MY_BACKUP_PATH>:/lute_backup jzohrab/lute3:latest
```

Docker containers using this image writes to container directories which must be mounted from the host:

* `/lute_data`: the database, user images, etc.
* `/lute_backup`: your backups

If these directories are not mounted, the container will not start.

Example:

```
mkdir -p ~/lute/data
mkdir -p ~/lute/backups
docker run -p 5000:5000 -v ~/lute/data:/lute_data -v ~/lute/backups:/lute_backup --name my-lute jzohrab/lute3:latest
```

The above:

* runs the container from the `jzohrab/lute3:latest` image
* exposes port 5000 on the host (so http://localhost:5000 works)
* mounts the necessary directories
* names the running container "my-lute"

and it prints:

```
  Starting Lute:
  
  Initializing app.
  data path: /lute_data
  database: /lute_data/lute.db
  (Note these are container paths, not host paths.)
  
  Running at:
  
  http://localhost:5000
  
  
  When you're finished reading, stop this container
  with Ctrl-C, docker compose stop, or docker stop <containerid>
  as appropriate.
```

(You can now open your browser to `http://localhost:5000` and start working through the Lute demo.)

With the above command, the `lutev3` process takes over that console window, so start a new console window and enter

```
docker stop my-lute
```

After the first call to `docker run`, you can start and stop that same container with:

```
docker start my-lute
docker stop my-lute
```

## ... via [`docker compose`](https://github.com/docker/compose)

Example `docker-compose.yml` for `lute3`:

```
version: '3.9'
services:
  lute:
    image: jzohrab/lute3:latest
    ports:
      - 5000:5000
    volumes:
      - ~/lute/data:/lute_data
      - ./lute/backups:/lute_backup
```

Store that file in some directory on your machine.  Then, starting a console in that directory, starting and stopping examples:

```
docker compose up -d
docker compose stop lute
```

# Image Variants

`lute3` has two variants:

* `lute3:<version>` (or `lute3:latest`): Lute v3 and all requirements, plus [MeCab](https://en.wikipedia.org/wiki/MeCab) and a MeCab dictionary for Japanese. ~830 MB.
* `lute3:<version>-lean` (or `lute3:latest-lean`): The same as the above, but without MeCab (Japanese parsing and the Japanese demo are disabled). ~300 MB

# Source code and building your own images

Lute v3 is on [GitHub](https://github.com/luteorg/lute-v3/).

The Dockerfile used to build the images, and docs, are in `/docker` in that repo.

# Help

If you encounter any issues or have questions, please check the [GitHub Issues](https://github.com/luteorg/lute-v3/issues) or join the [Discord](https://discord.gg/CzFUQP5m8u).

# License

Lute v3 and its Docker image are under the [MIT license](https://github.com/luteorg/lute-v3/blob/master/LICENSE.txt).
