#!/usr/bin/env python3
"""Snapshot the installed Docker CLI and plugins using read-only --help calls."""
import concurrent.futures
import datetime
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ENV = dict(os.environ, NO_COLOR="1", TERM="dumb", DOCKER_CLI_HINTS="false")
ENV.pop("DOCKER_HIDE_LEGACY_COMMANDS", None)
# An active non-Swarm daemon hides Swarm and experimental commands from help.
# Read offline help so the reference is independent of the machine's daemon state.
ENV.pop("DOCKER_CONTEXT", None)
ENV["DOCKER_HOST"] = "unix:///tmp/docker-reference-no-daemon.sock"


def help_for(command):
    result = subprocess.run(command.split() + ["--help"], capture_output=True,
                            text=True, timeout=30, env=ENV)
    if result.returncode:
        raise RuntimeError(f"{command} --help failed: {result.stderr.strip()}")
    return result.stdout


def children(help_text):
    in_commands = False
    for line in help_text.splitlines():
        if line and not line[0].isspace():
            in_commands = bool(re.fullmatch(r"(?:[\w -]+ )?Commands:?", line.strip()))
        if in_commands:
            match = re.match(r"^  ([a-z][a-z0-9-]*)\*?\s+(.+)$", line)
            if match:
                yield match.group(1), " ".join(match.group(2).split())


def main():
    entries = {"docker": "Manage containers, images, networks, volumes, and Docker services"}
    pending = ["docker"]
    visited = set()
    failures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        while pending:
            commands = sorted(set(pending) - visited)
            pending = []
            futures = {pool.submit(help_for, cmd): cmd for cmd in commands}
            for future in concurrent.futures.as_completed(futures):
                command = futures[future]
                visited.add(command)
                try:
                    help_text = future.result()
                except (RuntimeError, subprocess.TimeoutExpired) as exc:
                    failures.append(str(exc))
                    continue
                # Some Desktop plugins dispatch by a command's final token and
                # return their root wrapper help (e.g. `docker swarm init`).
                # It must not become fictitious nested commands such as init init.
                if command != "docker" and re.search(
                        r"Usage:\s+docker \[OPTIONS\] COMMAND", help_text):
                    continue
                alias_section = re.search(r"(?m)^Aliases:\n([^\n]+)", help_text)
                if alias_section:
                    for alias in alias_section.group(1).strip().split(", "):
                        if re.fullmatch(r"docker(?: [a-z][a-z0-9-]*)+", alias):
                            entries.setdefault(alias, entries[command])
                for name, description in children(help_text):
                    child = f"{command} {name}"
                    entries[child] = description
                    if name not in {"help", "completion"} and len(child.split()) < 9:
                        pending.append(child)
            print(f"Read help for {len(visited)} commands; found {len(entries)}", flush=True)
    (ROOT / "commands.txt").write_text("".join(
        f"{cmd} - {entries[cmd]}\n" for cmd in sorted(entries)), encoding="utf-8")
    metadata = {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "source": "Installed Docker CLI and plugins: recursive COMMAND --help",
        "docker_version": subprocess.check_output(["docker", "--version"], text=True).strip(),
        "compose_version": subprocess.check_output(["docker", "compose", "version", "--short"], text=True).strip(),
        "buildx_version": subprocess.check_output(["docker", "buildx", "version"], text=True).strip(),
        "command_count": len(entries),
        "groups": sorted(cmd for cmd in entries if len(cmd.split()) == 2),
        "help_failures": failures,
    }
    (ROOT / "catalog.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
