DOCKER COMMAND REFERENCE

commands.txt   Complete command catalog from the installed Docker CLI and plugins.
flags.txt      Command-specific short and long option templates and descriptions.
examples.txt   Practical command examples with values and explanations.
catalog.json  Snapshot versions, counts, generation time and any help failures.

Refresh from the repository root:
  python3 scripts/generate_reference.py

The existing curl service reads these files from this directory. All existing
HTTP endpoints are preserved. See the repository README.md for service usage.
The catalog covers commands exposed by the recorded CLI and installed plugins;
it does not enumerate every possible argument combination or third-party plugin.

Official Docker CLI documentation:
  https://docs.docker.com/reference/cli/docker/
