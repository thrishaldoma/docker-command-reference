#!/usr/bin/env python3
"""Snapshot kubectl's built-in help without reading a real cluster configuration."""
import concurrent.futures
import datetime
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1] / "kubernetes"


def children(help_text):
    active = False
    for line in help_text.splitlines():
        if line and not line[0].isspace():
            active = bool(re.fullmatch(r".*Commands(?: \([^)]*\))?:", line))
        if active:
            match = re.fullmatch(r"  ([a-z][a-z0-9-]*)\s{2,}(.+)", line)
            if match:
                yield match.group(1), match.group(2).strip()


def main():
    entries = {"kubectl": "Manage Kubernetes resources and cluster configuration"}
    help_pages = {}
    pending = ["kubectl"]
    # An empty config prevents local names or credentials from entering the export.
    with tempfile.TemporaryDirectory(prefix="kubectl-reference-") as temp:
        config = Path(temp) / "config"
        config.write_text("apiVersion: v1\nkind: Config\nclusters: []\ncontexts: []\nusers: []\n")
        env = dict(os.environ, KUBECONFIG=str(config), KUBECTL_KUBERC="false",
                   NO_COLOR="1", TERM="dumb")

        def run(args):
            return subprocess.check_output(args, text=True, env=env, timeout=30).replace(
                str(Path.home()), "$HOME")

        def read_help(command):
            return "\n".join(line.rstrip() for line in run(command.split() + ["--help"]).splitlines())

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            while pending:
                batch = sorted(set(pending) - help_pages.keys())
                pending = []
                for command, text in zip(batch, pool.map(read_help, batch)):
                    help_pages[command] = text
                    for name, description in children(text):
                        child = command + " " + name
                        entries[child] = description
                        pending.append(child)
        # Global flags are intentionally printed by this read-only command.
        help_pages["kubectl options"] = "\n".join(
            line.rstrip() for line in run(["kubectl", "options"]).splitlines())
        entries["kubectl options"] = "List global flags shared by kubectl commands"
        version = json.loads(run(["kubectl", "version", "--client", "-o", "json"]))

    ROOT.mkdir(parents=True, exist_ok=True)
    (ROOT / "commands.txt").write_text("".join(
        f"{command} - {description}\n" for command, description in sorted(entries.items())))
    (ROOT / "reference.txt").write_text("\n".join(
        f"{command}\n{'-' * len(command)}\n{text.rstrip()}\n"
        for command, text in sorted(help_pages.items())))
    metadata = {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "source": "Installed kubectl: recursive --help, kubectl options, client-only version",
        "client_version": version,
        "command_count": len(entries),
        "help_page_count": len(help_pages),
        "help_failures": [],
        "scope": "Built-in commands exposed by this client; excludes external plugins and cluster-specific resources",
    }
    (ROOT / "catalog.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(f"Exported {len(entries)} commands and {len(help_pages)} help pages")


if __name__ == "__main__":
    main()
