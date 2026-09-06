# hone

An offline terminal trainer for command-line tools. It teaches one tool per
module, hands you the real tool to practise in, and then reads back what you
actually did.

56 tools, 360 lessons, 1177 drills, 336 practice sessions.

## Getting it

You need **Python 3.10 or newer** and a terminal (`--ascii` if it cannot draw
boxes). Then either:

- download `hone.pyz` from the
  [latest release](https://github.com/SageSchiller/hone/releases/latest)
  and run `python3 hone.pyz`, or
- clone this repository and run `python3 -m hone` from inside it.

Standard library only: no dependencies, no network, no install step. The
tools themselves (tmux, nvim, git, tcpdump and the rest) are whatever your
machine already has. `hone --doctor` says what it can verify here, and a
module whose tool is absent still teaches and drills, and tells you the
install command.

## What makes it different

**It checks real work.** Where it can, hone hands the terminal to the actual
program and inspects the result afterwards: it reads `tmux list-panes` after you
build a layout, reads the buffer back over RPC after you edit in nvim, runs your
BPF filter through `tcpdump -r` against a capture it wrote itself, and runs your
SQL in a real sqlite database. Where it cannot check, it says so plainly rather
than pretending. Every task is labelled with which of three tiers applied:

| Tier | Meaning |
|---|---|
| `verified` | a real tool confirmed the end state |
| `checked` | graded exactly, in process |
| `self-marked` | you did it somewhere hone cannot see, and you said so |

**It never touches anything of yours.** Every exercise runs in a sandbox hone
creates and destroys. It does not write to your config, does not touch your
existing sessions, and never opens a network connection. Where a subject needs
a target, hone builds one out of its own sockets: loopback listeners for the
nmap module, a stdlib HTTP server for the web modules, a capture file written
rather than sniffed for tcpdump.

**It keeps no clock on you.** No streaks, no daily goals, no reminders, no
queue of things you owe. Pick a tool, work at it as long as you feel like, put
it down for a month. Nothing in the app will mention that you did.

## Using it

Three views per tool, switched with `Tab`:

- **Walkthrough**: read it, when the thing makes no sense yet
- **Practice**: do a real task, with as much or as little help as you ask for
- **Drill**: grind the invocation until you stop having to think

Practice has three levels of rigor, changeable at any time: `guided` gives every
step with hints, `coached` gives the steps, `free` gives the task only. Rigor
changes what you see and never what is checked.

```
hone --list        what is installed, and what can be verified here
hone --sheet ssh   one tool as a reference card; "all" for every tool
hone --doctor      why something degrades on this machine, and how to fix it
hone --export f    your progress, as one JSON file
hone --import f    replace your progress from one
hone --reset       erase your progress; name a tool to reset only that one
hone --ascii       no box drawing, for a plain terminal
```

Progress is one JSON file in `~/.local/share/hone/`. Nothing is sent anywhere.

`--reset` asks before it does anything, and writes a timestamped backup first,
so `hone --import` always has something to put back. Your theme, rigor and sync
settings are not progress and survive it. With no terminal to ask on it refuses
outright rather than guessing; `--yes` is the way to mean it in a script.

## Tools covered

**Editors** vim/neovim, Doom Emacs, org-mode ·
**Terminal** tmux, bash ·
**Text** regex, awk, jq, SQL, LaTeX ·
**Linux** basics, pacman/apt, advanced, utilities, systemd ·
**Version control** git ·
**Network** ssh, scp/rsync, dig, curl, netcat/socat, xfreerdp, nftables/iptables, tcpdump ·
**Scripting** Python, PowerShell, make ·
**Containers** Docker ·
**Security** nmap, strace, gdb, file, strings, xxd, readelf/objdump, hashing, stat, openssl, gpg, ffuf,
gobuster, hashcat, John the Ripper, hydra, YARA, smbclient/rpcclient, ldapsearch,
netexec, impacket, Metasploit, Volatility, mimikatz, Windows/Sysmon DFIR,
Linux DFIR, The Sleuth Kit

A tool earns a module by being **useful and hard to learn**. The security modules
teach the tool and never the engagement: how it works and what its output means,
never target selection. The test for anything proposed is whether it would still
be worth knowing with no engagement in progress.

## Missing tools

hone works without them. A module whose tool is absent degrades to read-and-drill
and tells you the exact install command for your package manager rather than
leaving you at a dead end. It never installs anything itself.

## For testers

Thank you. Three things are worth an evening each:

1. **A tool you already use.** Pick it, read the walkthrough, do one practice
   at `coached`, then drill until the invocation is automatic. If a check
   disagrees with what you did, that is the bug: note the tier it showed
   (`verified`, `checked`, `self-marked`) and what you typed.
2. **A tool you do not have installed.** The module should degrade to
   read-and-drill and name the install command, never a dead end.
3. **The capture drills** (tmux, vim, Doom). Keys are the hardest thing to
   read back through a terminal, and `hone --doctor` says whether yours folds
   TAB, RET and ESC together.

A useful report is `hone --doctor`, the module and the item, and what the
screen said; `hone --export f` makes a file of your progress you can attach.
Known edges: only Linux has been tried; the author runs Python 3.14, and 3.10
to 3.13 have not been tried by hand.

## Development

```
python3 validate.py --lint    # content graph and prose
python3 test.py               # 12445 checks, plays every verified solution through the real tool
bash build.sh                 # dist/hone.pyz
bash build.sh --per-tool      # plus one .pyz per tool
```

`test.py` plays every verified challenge's solution through the real tool, so the
suite proves the content is solvable rather than merely parseable.

Design decisions and their reasoning live in `HONE-PLAN.md`.

## Licence

MIT. See `LICENSE`.
