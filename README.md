# Docker Command Reference

A Docker command reference for the terminal. Each line is exactly:

```text
docker run - Create and run a new container from an image
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
curl http://localhost:8080/buildx
curl http://localhost:8080/container
curl http://localhost:8080/compose/up
curl 'http://localhost:8080/search?q=volume'
curl http://localhost:8080/help
curl http://localhost:8080/meta
```

Use a command path to show that command and its subcommands. Search matches both command names and descriptions. The root response contains only one-line command descriptions, with no banners, HTML, or ANSI escape codes.

Requests must send a `curl/` User-Agent, which curl sends by default. Ordinary browser requests get HTTP 403. This is a client convenience restriction, **not authentication**: other clients can imitate curl's User-Agent. The service only displays a static reference; it does not execute commands or require access to a Docker socket.

To share the running service from your own server, publish port 8080 and use `curl http://YOUR_SERVER_IP:8080`. Publishing the container image makes it downloadable; it does not itself host a public HTTP server. To bind only to your machine, replace `-p 8080:8080` with `-p 127.0.0.1:8080:8080`.

## Coverage

`commands.txt` is a versioned snapshot generated recursively from the installed Docker CLI and plugin `--help` output, including core Engine commands, aliases, Swarm, Compose, Buildx, and installed Docker Desktop plugins. `catalog.json` records the version, generation time, count, and any help failures. Plugin availability varies by installation; future releases and third-party plugins are not automatically included. Flags and arbitrary combinations of command arguments are not separate commands.

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
