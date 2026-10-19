IMPORTANT LINUX COMMANDS

commands.txt contains practical command examples and short explanations grouped
by topic: help, files, text, search, permissions, users, processes, system info,
networking, SSH, services, scheduling, storage, packages and Bash scripting.

This is a curated Linux administration reference, not an exhaustive inventory
of every Linux executable or every possible flag combination. It targets Bash
and common GNU/Linux tools. Some flags differ on macOS, BSD and BusyBox systems.
systemctl and journalctl examples require systemd; package commands are grouped
by distribution. Tools such as rg, tree, htop, dig, lsof, strace, sysstat, zip,
ACL utilities, tmux and ShellCheck may need to be installed separately.

Replace account names, paths, devices, hostnames, process IDs and service names
with values appropriate to your system. Uppercase PID and COMMAND are
placeholders. Each line is a separate recipe, not part of a script to run in
sequence. Some examples create, overwrite or delete data or change system state;
their explanations describe those effects. Run sudo only for commands requiring
elevated privileges. Do not run storage commands against an unidentified device.
The examples were reviewed and syntax-checked; they were not all executed.

Conventions:
  - A line starting with # is a topic heading.
  - Each other entry uses COMMAND - EXPLANATION.
  - Quote paths and variable expansions when values may contain spaces.
  - Ctrl+C interrupts a foreground command; q exits common pagers.
  - Shell output redirection with > replaces a file; >> appends to it.
  - Use man COMMAND or COMMAND --help to check your installed version.

Primary documentation for further details:
  GNU core utilities: https://www.gnu.org/software/coreutils/manual/
  Bash: https://www.gnu.org/software/bash/manual/
  Findutils: https://www.gnu.org/software/findutils/manual/
  Grep: https://www.gnu.org/software/grep/manual/
  Sed: https://www.gnu.org/software/sed/manual/
  Awk: https://www.gnu.org/software/gawk/manual/
  systemctl: https://www.freedesktop.org/software/systemd/man/latest/systemctl.html
  journalctl: https://www.freedesktop.org/software/systemd/man/latest/journalctl.html
  iproute2: https://man7.org/linux/man-pages/man8/ip.8.html
  OpenSSH: https://www.openssh.com/manual.html
  curl: https://curl.se/docs/manpage.html
  APT: https://manpages.debian.org/stable/apt/apt.8.en.html
  DNF: https://dnf5.readthedocs.io/en/latest/commands/index.html

Examples and explanations are curated for this repository. The linked manuals
remain the authoritative source for version-specific options and behavior.
