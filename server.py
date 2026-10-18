"""Plain-text, curl-only Docker command reference; no Docker socket required."""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

ROOT = Path(__file__).resolve().parent
LINES = (ROOT / "commands.txt").read_text(encoding="utf-8").splitlines()
CATALOG = json.loads((ROOT / "catalog.json").read_text())
HELP = """curl localhost:8080 - List all commands
curl localhost:8080/compose - List Docker Compose commands
curl localhost:8080/buildx - List Docker Buildx commands
curl localhost:8080/container - List container commands
curl localhost:8080/compose/up - Show one command
curl 'localhost:8080/search?q=volume' - Search commands and descriptions
curl localhost:8080/meta - Show catalog version and scope
curl localhost:8080/healthz - Check service health
"""


class Handler(BaseHTTPRequestHandler):
    server_version = "DockerReference/1.0"

    def setup(self):
        super().setup()
        self.connection.settimeout(10)

    def send_text(self, status, body):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(data)

    def do_GET(self):
        if not self.headers.get("User-Agent", "").lower().startswith("curl/"):
            return self.send_text(403, "Please use curl: curl http://HOST:PORT/\n")
        url = urlsplit(self.path)
        path = unquote(url.path).strip("/")
        if path == "healthz":
            return self.send_text(200, "ok\n")
        if path == "help":
            return self.send_text(200, HELP)
        if path == "meta":
            return self.send_text(200, json.dumps(CATALOG, indent=2) + "\n")
        if path == "search":
            query = parse_qs(url.query).get("q", [""])[0].strip().lower()
            if not query:
                return self.send_text(400, "Supply a search term: curl 'http://HOST:PORT/search?q=volume'\n")
            lines = [line for line in LINES if query in line.lower()]
        elif not path:
            lines = LINES
        else:
            prefix = "docker " + path.replace("/", " ")
            lines = [line for line in LINES
                     if line.split(" - ", 1)[0] == prefix
                     or line.split(" - ", 1)[0].startswith(prefix + " ")]
        if not lines:
            return self.send_text(404, "No matching commands. Use curl http://HOST:PORT/help\n")
        return self.send_text(200, "\n".join(lines) + "\n")

    do_HEAD = do_GET

    def do_POST(self):
        self.send_text(405, "Use GET with curl. This service only displays command descriptions.\n")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    print(f"Serving {len(LINES)} Docker commands on port {port}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
