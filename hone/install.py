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
    'rsync': {'pacman': 'rsync', 'apt': 'rsync', 'dnf': 'rsync',
              'zypper': 'rsync', 'apk': 'rsync', 'brew': 'rsync'},
    # dig ships in the bind client tools, packaged under a different name on
    # almost every distribution, which is exactly the kind of thing a student
    # should not have to guess.
    'dig': {'pacman': 'bind', 'apt': 'dnsutils', 'dnf': 'bind-utils',
            'zypper': 'bind-utils', 'apk': 'bind-tools', 'brew': 'bind'},
    # netcat has three incompatible builds; the OpenBSD one is the default on
    # most distributions and the one whose flags the lessons assume.
    'nc': {'pacman': 'openbsd-netcat', 'apt': 'netcat-openbsd',
           'dnf': 'nmap-ncat', 'zypper': 'netcat-openbsd',
           'apk': 'netcat-openbsd', 'brew': 'netcat'},
    'proxychains': {'pacman': 'proxychains-ng', 'apt': 'proxychains4',
                    'dnf': 'proxychains-ng', 'zypper': 'proxychains-ng',
                    'apk': 'proxychains-ng'},
    'lsof': {'pacman': 'lsof', 'apt': 'lsof', 'dnf': 'lsof',
             'zypper': 'lsof', 'apk': 'lsof', 'brew': 'lsof'},
    # The init system, so on a systemd distribution it is already there.
    # No apk or brew entry on purpose: Alpine runs OpenRC and macOS runs
    # launchd, and offering a package for either would be a lie.
    'systemctl': {'pacman': 'systemd', 'apt': 'systemd', 'dnf': 'systemd',
                  'zypper': 'systemd'},
    'pwsh': {},   # never in the ordinary repositories: see COMMANDS below

    # The security roster. Several of these are packaged everywhere and a few
    # are packaged almost nowhere, and the difference is worth being exact
    # about: a student who pastes a line that fails concludes the trainer is
    # broken rather than that the package is unusual.
    'nmap': {'pacman': 'nmap', 'apt': 'nmap', 'dnf': 'nmap',
             'zypper': 'nmap', 'apk': 'nmap', 'brew': 'nmap'},
    'file': {'pacman': 'file', 'apt': 'file', 'dnf': 'file',
             'zypper': 'file', 'apk': 'file', 'brew': 'file'},
    'strings': {'pacman': 'binutils', 'apt': 'binutils', 'dnf': 'binutils',
                'zypper': 'binutils', 'apk': 'binutils', 'brew': 'binutils'},
    # Packaged with vim nearly everywhere, which is worth saying rather than
    # letting someone search for an xxd package that does not exist.
    'xxd': {'pacman': 'xxd', 'apt': 'xxd', 'dnf': 'vim-common',
            'zypper': 'vim-data-common', 'apk': 'xxd', 'brew': 'vim'},
    'strace': {'pacman': 'strace', 'apt': 'strace', 'dnf': 'strace',
               'zypper': 'strace', 'apk': 'strace'},
    'gpg': {'pacman': 'gnupg', 'apt': 'gnupg', 'dnf': 'gnupg2',
            'zypper': 'gpg2', 'apk': 'gnupg', 'brew': 'gnupg'},
    'openssl': {'pacman': 'openssl', 'apt': 'openssl', 'dnf': 'openssl',
                'zypper': 'openssl', 'apk': 'openssl', 'brew': 'openssl'},
    'yara': {'pacman': 'yara', 'apt': 'yara', 'dnf': 'yara',
             'zypper': 'yara', 'apk': 'yara', 'brew': 'yara'},
    # No pacman entry on purpose: ffuf is AUR-only on Arch, and printing
    # `pacman -S ffuf` produced "target not found" for a real user. See
    # COMMANDS for the route that works.
    'ffuf': {'apk': 'ffuf', 'brew': 'ffuf'},
    'gobuster': {'pacman': 'gobuster', 'apt': 'gobuster', 'apk': 'gobuster',
                 'brew': 'gobuster'},
    'hashcat': {'pacman': 'hashcat', 'apt': 'hashcat', 'dnf': 'hashcat',
                'zypper': 'hashcat', 'brew': 'hashcat'},
    'john': {'pacman': 'john', 'apt': 'john', 'dnf': 'john',
             'zypper': 'john', 'apk': 'john', 'brew': 'john-jumbo'},
    'hydra': {'pacman': 'hydra', 'apt': 'hydra', 'dnf': 'hydra',
              'brew': 'hydra'},
    'smbclient': {'pacman': 'smbclient', 'apt': 'smbclient', 'dnf': 'samba-client',
                  'zypper': 'samba-client', 'apk': 'samba-client',
                  'brew': 'samba'},
    # Same package as smbclient everywhere, and worth its own entry anyway:
    # the module teaches both binaries, so a machine missing one is missing
    # the other, and being told the package name twice costs nothing.
    'rpcclient': {'pacman': 'smbclient', 'apt': 'smbclient', 'dnf': 'samba-client',
                  'zypper': 'samba-client', 'apk': 'samba-client',
                  'brew': 'samba'},
    'ldapsearch': {'pacman': 'openldap', 'apt': 'ldap-utils',
                   'dnf': 'openldap-clients', 'zypper': 'openldap2-client',
                   'apk': 'openldap-clients', 'brew': 'openldap'},
    # The Sleuth Kit: one package, many binaries (mmls, fls, icat...).
    'fls': {'pacman': 'sleuthkit', 'apt': 'sleuthkit', 'dnf': 'sleuthkit',
            'zypper': 'sleuthkit', 'apk': 'sleuthkit', 'brew': 'sleuthkit'},
    'icat': {'pacman': 'sleuthkit', 'apt': 'sleuthkit', 'dnf': 'sleuthkit',
             'zypper': 'sleuthkit', 'apk': 'sleuthkit', 'brew': 'sleuthkit'},
    # impacket is in the official repos on Arch as `impacket`, not
    # `python-impacket`, which is what a real paste of the wrong name
    # taught us. Debian ships the scripts as python3-impacket.
    'secretsdump.py': {'pacman': 'impacket', 'apt': 'python3-impacket',
                       'dnf': 'python3-impacket'},
    'binwalk': {'pacman': 'binwalk', 'apt': 'binwalk', 'dnf': 'binwalk',
                'brew': 'binwalk'},
    'exiftool': {'pacman': 'perl-image-exiftool', 'apt': 'libimage-exiftool-perl',
                 'dnf': 'perl-Image-ExifTool', 'zypper': 'exiftool',
                 'apk': 'exiftool', 'brew': 'exiftool'},
    'sqlite3': {'pacman': 'sqlite', 'apt': 'sqlite3', 'dnf': 'sqlite',
                'zypper': 'sqlite3', 'apk': 'sqlite', 'brew': 'sqlite'},
    'netexec': {},        # pipx only: see COMMANDS
    'msfconsole': {},     # never in the ordinary repositories: see COMMANDS
    'vol': {},            # a Python project, not a package: see COMMANDS

    # containers and the rest of the later roster
    'docker': {'pacman': 'docker', 'apt': 'docker.io', 'dnf': 'docker',
               'zypper': 'docker', 'apk': 'docker', 'brew': 'docker'},
    'nft': {'pacman': 'nftables', 'apt': 'nftables', 'dnf': 'nftables',
            'zypper': 'nftables', 'apk': 'nftables'},
    'iptables': {'pacman': 'iptables', 'apt': 'iptables', 'dnf': 'iptables',
                 'zypper': 'iptables', 'apk': 'iptables'},
}

#: Full commands that replace the template, where the package is not simply
#: in the default repositories. Printing `pacman -S powershell` would be
#: worse than printing nothing, because it fails and looks like our mistake.
COMMANDS: dict[tuple[str, str], str] = {
    # ffuf is a Go program packaged almost nowhere: AUR on Arch, and on
    # Debian a release binary or `go install`. Saying so beats an apt line
    # that does not exist.
    ('ffuf', 'pacman'): 'paru -S ffuf      # AUR, or yay -S ffuf',
    ('ffuf', 'apt'): 'go install github.com/ffuf/ffuf/v2@latest   '
                     '# or grab a release binary from github.com/ffuf/ffuf',
    ('ffuf', 'dnf'): 'go install github.com/ffuf/ffuf/v2@latest   '
                     '# or grab a release binary from github.com/ffuf/ffuf',
    ('ffuf', 'zypper'): 'go install github.com/ffuf/ffuf/v2@latest   '
                        '# or grab a release binary from github.com/ffuf/ffuf',
    ('pwsh', 'pacman'): 'paru -S powershell-bin      # AUR, or yay -S powershell-bin',
    ('pwsh', 'apt'): 'sudo snap install powershell --classic',
    ('pwsh', 'dnf'): 'sudo snap install powershell --classic',
    ('pwsh', 'zypper'): 'sudo snap install powershell --classic',
    ('pwsh', 'brew'): 'brew install --cask powershell',

    # Three security tools that no ordinary repository carries. Each is a real
    # install route rather than a plausible-looking one, and each says which
    # kind of thing it is, because "pipx" and "a git clone" fail differently
    # from a package and are recovered from differently.
    ('netexec', 'pacman'): 'pipx install git+https://github.com/Pennyw0rth/NetExec',
    ('netexec', 'apt'): 'pipx install git+https://github.com/Pennyw0rth/NetExec',
    ('netexec', 'dnf'): 'pipx install git+https://github.com/Pennyw0rth/NetExec',
    ('netexec', 'zypper'): 'pipx install git+https://github.com/Pennyw0rth/NetExec',
    ('netexec', 'brew'): 'pipx install git+https://github.com/Pennyw0rth/NetExec',
    ('msfconsole', 'pacman'): 'paru -S metasploit       # AUR',
    ('msfconsole', 'apt'): 'sudo apt install metasploit-framework   # Kali, or use the omnibus installer',
    ('msfconsole', 'dnf'): 'use the Rapid7 omnibus installer: https://docs.metasploit.com',
    ('msfconsole', 'zypper'): 'use the Rapid7 omnibus installer: https://docs.metasploit.com',
    ('msfconsole', 'brew'): 'brew install --cask metasploit',
    ('vol', 'pacman'): 'pipx install volatility3',
    ('vol', 'apt'): 'pipx install volatility3',
    ('vol', 'dnf'): 'pipx install volatility3',
    ('vol', 'zypper'): 'pipx install volatility3',
    ('vol', 'apk'): 'pipx install volatility3',
    ('vol', 'brew'): 'pipx install volatility3',
}

#: Said once, next to a tool that needs more than installing.
NOTES: dict[str, str] = {
    'tcpdump': 'capturing needs root; reading a saved file does not',
    'pwsh': 'PowerShell runs on Linux, and is worth having for the module '
            'even if you never touch Windows',
    'tshark': 'the wireshark package will offer to let non-root users '
              'capture; you can say no and still read files',
    'nmap': 'a SYN scan needs root; the connect scan the lab uses does not',
    'strace': 'tracing your own processes needs nothing; tracing anyone '
              'else\'s needs root or a relaxed ptrace_scope',
    'msfconsole': 'large, and it wants its own database; the module is '
                  'readable without it installed',
    'vol': 'volatility3 needs symbol tables for the kernel of the machine '
           'the memory image came from, not yours',
    'netexec': 'the tool formerly called crackmapexec; the old name still '
               'appears in most write-ups',
    'john': 'Debian and Fedora ship the basic build; the jumbo build is the '
            'one with the format zoo, and is what write-ups assume',
}


#: Other binary names that satisfy a declared need. A tool that renamed its
#: executable is still installed, and reporting it missing sends someone to
#: install a package they already have: FreeRDP 3 ships `xfreerdp3` and no
#: `xfreerdp`, so a fully installed machine was being told it needed one.
ALIASES: dict[str, tuple[str, ...]] = {
    'xfreerdp': ('xfreerdp3', 'sdl-freerdp3'),
    'vol': ('vol.py', 'volatility3'),
    'netexec': ('nxc',),
}


def present(tool: str) -> bool:
    """Is this tool usable here, under its own name or a known alias?"""
    return any(shutil.which(n) for n in (tool, *ALIASES.get(tool, ())))


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
    return [t for t in tools if not present(t)]


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
