"""How to install a tool this machine is missing.

D18 says a missing tool degrades gracefully, and it does: the challenge falls
back to self-marked and says why. But "nvim not installed" is a dead end. The
student is told what is wrong and left to go and work out the rest somewhere
else, which is the moment a lot of people stop.

This turns the dead end into one line they can paste. It is the smallest
possible amount of package-manager knowledge: enough to unblock, never enough
to pretend to be a package manager.

**What this deliberately does not do.** It never runs anything. There is no
"install it for me" button and there is not going to be one: installing
software is a decision about someone's machine, and D1 is explicit that the
trainer does not act on your behalf. It prints a command and stops.

**Accuracy over coverage.** Where a tool is not in the ordinary repositories,
the entry says so and gives the route that actually works, rather than a
plausible command that fails. PowerShell on Arch is the case that forced this:
`pacman -S powershell` does not exist, and printing it would be worse than
printing nothing.
"""

from __future__ import annotations

import shutil

#: (manager binary, label, command template). Ordered by how likely the
#: binary is to be a reliable signal: pacman and apk are unambiguous, brew is
#: last because it can be installed alongside a system manager.
MANAGERS: tuple[tuple[str, str, str], ...] = (
    ('pacman', 'Arch, CachyOS, Manjaro', 'sudo pacman -S {pkg}'),
    ('apt', 'Debian, Ubuntu, Mint, Kali', 'sudo apt install {pkg}'),
    ('dnf', 'Fedora, RHEL, Rocky', 'sudo dnf install {pkg}'),
    ('zypper', 'openSUSE', 'sudo zypper install {pkg}'),
    ('apk', 'Alpine', 'sudo apk add {pkg}'),
    ('brew', 'macOS or Homebrew', 'brew install {pkg}'),
)

MANAGER_LABELS = {name: label for name, label, _ in MANAGERS}

#: tool binary -> {manager: package name}, plus optional per-manager full
#: command overrides for the awkward cases. A tool absent from a manager's
#: map simply is not offered for that manager.
PACKAGES: dict[str, dict[str, str]] = {
    'nvim': {'pacman': 'neovim', 'apt': 'neovim', 'dnf': 'neovim',
             'zypper': 'neovim', 'apk': 'neovim', 'brew': 'neovim'},
    'emacs': {'pacman': 'emacs', 'apt': 'emacs', 'dnf': 'emacs',
              'zypper': 'emacs', 'apk': 'emacs', 'brew': 'emacs'},
    'tmux': {'pacman': 'tmux', 'apt': 'tmux', 'dnf': 'tmux',
             'zypper': 'tmux', 'apk': 'tmux', 'brew': 'tmux'},
    'git': {'pacman': 'git', 'apt': 'git', 'dnf': 'git',
            'zypper': 'git', 'apk': 'git', 'brew': 'git'},
    'tcpdump': {'pacman': 'tcpdump', 'apt': 'tcpdump', 'dnf': 'tcpdump',
                'zypper': 'tcpdump', 'apk': 'tcpdump', 'brew': 'tcpdump'},
    'tshark': {'pacman': 'wireshark-cli', 'apt': 'tshark', 'dnf': 'wireshark-cli',
               'zypper': 'wireshark', 'apk': 'tshark', 'brew': 'wireshark'},
    'jq': {'pacman': 'jq', 'apt': 'jq', 'dnf': 'jq', 'zypper': 'jq',
           'apk': 'jq', 'brew': 'jq'},
    'awk': {'pacman': 'gawk', 'apt': 'gawk', 'dnf': 'gawk',
            'zypper': 'gawk', 'apk': 'gawk', 'brew': 'gawk'},
    'rg': {'pacman': 'ripgrep', 'apt': 'ripgrep', 'dnf': 'ripgrep',
           'zypper': 'ripgrep', 'apk': 'ripgrep', 'brew': 'ripgrep'},
    'xfreerdp': {'pacman': 'freerdp', 'apt': 'freerdp2-x11',
                 'dnf': 'freerdp', 'zypper': 'freerdp', 'brew': 'freerdp'},
    'socat': {'pacman': 'socat', 'apt': 'socat', 'dnf': 'socat',
              'zypper': 'socat', 'apk': 'socat', 'brew': 'socat'},
    'pwsh': {},   # never in the ordinary repositories: see COMMANDS below
}

#: Full commands that replace the template, where the package is not simply
#: in the default repositories. Printing `pacman -S powershell` would be
#: worse than printing nothing, because it fails and looks like our mistake.
COMMANDS: dict[tuple[str, str], str] = {
    ('pwsh', 'pacman'): 'paru -S powershell-bin      # AUR, or yay -S powershell-bin',
    ('pwsh', 'apt'): 'sudo snap install powershell --classic',
    ('pwsh', 'dnf'): 'sudo snap install powershell --classic',
    ('pwsh', 'zypper'): 'sudo snap install powershell --classic',
    ('pwsh', 'brew'): 'brew install --cask powershell',
}

#: Said once, next to a tool that needs more than installing.
NOTES: dict[str, str] = {
    'tcpdump': 'capturing needs root; reading a saved file does not',
    'pwsh': 'PowerShell runs on Linux, and is worth having for the module '
            'even if you never touch Windows',
    'tshark': 'the wireshark package will offer to let non-root users '
              'capture; you can say no and still read files',
}


def detect() -> str | None:
    """The package manager on this machine, or None if none is recognised."""
    for name, _, _ in MANAGERS:
        if shutil.which(name):
            return name
    return None


def command_for(tool: str, manager: str) -> str | None:
    """The exact line to paste, or None if we have nothing honest to offer."""
    override = COMMANDS.get((tool, manager))
    if override:
        return override
    pkg = PACKAGES.get(tool, {}).get(manager)
    if not pkg:
        return None
    for name, _, template in MANAGERS:
        if name == manager:
            return template.format(pkg=pkg)
    return None


def known(tool: str) -> bool:
    return tool in PACKAGES


def missing(tools) -> list[str]:
    return [t for t in tools if not shutil.which(t)]


def hint(tool: str) -> str:
    """One line for a cramped space: the command for *this* machine.

    Empty when nothing honest can be said, which the caller must treat as
    "say nothing" rather than printing an empty prefix.
    """
    manager = detect()
    if manager is None:
        return ''
    return command_for(tool, manager) or ''


def lines(tool: str, all_managers: bool = False) -> list[str]:
    """Install advice for `tool`, this machine's manager first.

    `all_managers` adds the others, which is what a shareable report wants
    (`--doctor` output gets pasted into a chat by someone helping) and what a
    single cramped UI line does not.
    """
    out: list[str] = []
    manager = detect()

    if manager is not None:
        cmd = command_for(tool, manager)
        if cmd:
            out.append(f'{cmd}   ({MANAGER_LABELS[manager]})')

    if all_managers or manager is None:
        for name, label, _ in MANAGERS:
            if name == manager:
                continue
            cmd = command_for(tool, name)
            if cmd:
                out.append(f'{cmd}   ({label})')

    note = NOTES.get(tool)
    if note and out:
        out.append(note)
    return out
