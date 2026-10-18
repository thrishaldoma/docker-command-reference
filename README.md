# Docker Command Reference

A Docker command reference for the terminal. Each line is exactly:

```text
docker run - Create and run a new container from an image
docker run -d nginx - Run Nginx in detached mode (in the background) and print the container ID
docker run -p 8080:80 nginx - Publish host port 8080 to container port 80; syntax is -p HOST_PORT:CONTAINER_PORT
docker compose up - Create and start containers
docker volume ls - List volumes
```

## Run

```sh
docker run -d --name docker-reference --restart unless-stopped -p 8080:8080 ghcr.io/thrishaldoma/docker-command-reference:latest
curl http://localhost:8080
```

The image supports Linux amd64 and arm64, including Docker Desktop on Intel and Apple Silicon. Public images can be pulled without signing in.

```sh
curl http://localhost:8080/compose
curl http://localhost:8080/run
curl http://localhost:8080/examples
curl http://localhost:8080/examples/run
curl http://localhost:8080/flags/run
curl http://localhost:8080/buildx
curl http://localhost:8080/container
curl http://localhost:8080/compose/up
curl 'http://localhost:8080/search?q=volume'
curl http://localhost:8080/help
curl http://localhost:8080/meta
```

The root response starts with practical examples, followed by command names and flag reference templates, all as one-line descriptions. Use a command path to show its examples, flags, and subcommands together. Search matches names, flags, values, and descriptions. There are no banners, HTML, or ANSI escape codes.

Use `/examples` for practical commands, `/flags` for option templates, and `/commands` for the original command-only catalog. Each collection also supports command paths, such as `/examples/compose/up`, and search, such as `/flags/search?q=detach`.

Examples show values and common combinations: `-d`, `-it`, `-p HOST_PORT:CONTAINER_PORT`, `-v SOURCE:DESTINATION`, `-e KEY=VALUE`, `--rm`, `--restart`, and more. Flags are command-specific: `docker run -p` publishes ports, while `docker compose -p` sets the project name. `-p` and `-P` are distinct flags.

Flag entries such as `docker run --publish <list>` are option reference templates: replace the typed placeholder and add required positional arguments (such as the image for `run`). Practical examples supply values; replace example image, container, service, network, file, and account names with your own. Not every example is runnable without those resources. Cleanup examples describe which resources and data they remove.

To update an existing installation:

```sh
docker pull ghcr.io/thrishaldoma/docker-command-reference:latest
docker rm -f docker-reference
docker run -d --name docker-reference --restart unless-stopped -p 8080:8080 ghcr.io/thrishaldoma/docker-command-reference:latest
```

Requests must send a `curl/` User-Agent, which curl sends by default. Ordinary browser requests get HTTP 403. This is a client convenience restriction, **not authentication**: other clients can imitate curl's User-Agent. The service only displays a static reference; it does not execute commands or require access to a Docker socket.

To share the running service from your own server, publish port 8080 and use `curl http://YOUR_SERVER_IP:8080`. Publishing the container image makes it downloadable; it does not itself host a public HTTP server. To bind only to your machine, replace `-p 8080:8080` with `-p 127.0.0.1:8080:8080`.

## Coverage

`commands.txt` and `flags.txt` are versioned snapshots generated recursively from installed Docker CLI and plugin `--help` output, including core Engine commands, aliases, Swarm, Compose, Buildx, and installed Docker Desktop plugins. Both short and long options are included, with wrapped descriptions joined onto one line. `examples.txt` supplies curated commands with concrete values and common flag combinations. `catalog.json` records versions, generation time, counts, and any help failures. Plugin availability varies by installation; future releases, hidden options, platform-specific options unavailable in this CLI, and third-party plugins are not automatically included. Arbitrary values and every possible combination of flags cannot be enumerated.

Descriptions are taken from the tools' own command help. See the [official Docker CLI reference](https://docs.docker.com/reference/cli/docker/) for syntax, arguments, flags, and requirements. Some listed commands require Swarm, experimental daemon features, a plugin, or a Docker subscription.

## Build, test, and refresh

```sh
python3 scripts/generate_reference.py
python3 -m unittest discover -s tests -v
docker build -t docker-command-reference:local .
docker run --rm -p 8080:8080 docker-command-reference:local
```

Generation reads help only and does not change Docker resources. Offline help prevents an inactive Swarm or disabled daemon features from hiding command groups. The generated catalog is committed so building the service does not require Docker plugins or network access beyond downloading the base image.

The container runs as UID 65532. It supports a read-only filesystem and dropping all Linux capabilities. `GET /healthz` supplies the container health check. The `PORT` environment variable defaults to 8080; if you change it, update the port mapping and health check together.

The GitHub Actions workflow tests and publishes amd64/arm64 images to GHCR on pushes to `main` and version tags. GitHub creates new packages as private; package visibility must be set to public before anonymous pulls succeed.

## Attribution

Docker command names and short descriptions are generated from Docker CLI and plugin help. Docker and its plugins are maintained by their respective upstream authors. This is an independent reference tool and is not an official Docker product.
