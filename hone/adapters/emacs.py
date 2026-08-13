"""The Emacs adapter: real edits in real Doom, plus what only Emacs can answer.

Structurally this is the nvim adapter with different quoting: a scratch file, a
handoff to the real editor, and a `kill-emacs-hook` that dumps the buffer and
point into the sandbox on the way out.

**Two things make it different, and both are worth having.**

First, it does **not** require `emacsclient` or a running server. A Doom user
may or may not run a daemon, and a verification tier that only works for half
of them is not a tier. The baseline launches `emacs -nw` on the scratch file,
which needs nothing but Emacs.

Second, when a server *is* running, `emacsclient --eval` is the richest query
surface any of these adapters has: it can answer what a key is actually bound
to in **your** configuration, which is exactly the thing a Doom trainer wants
to check and which no amount of reading a buffer would reveal. That is used
opportunistically and never required.

**D1 and reading your files.** `config_contains` reads `~/.config/doom/*.el` to
verify a challenge that asked you to change your own configuration. D1 permits
reading your state; what it forbids is writing outside the sandbox. The trainer
never edits those files, it only looks at them, and a challenge that asks you
to change your config says so plainly first.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from . import Observation
from ._buffer import BufferAdapter, check as buffer_check

TIMEOUT = 15.0

EXPECT_KEYS = frozenset({
    'lines', 'contains', 'not_contains', 'line_count',
    'cursor_line', 'cursor_col', 'saved',
    #: Emacs-only: read the user's Doom configuration back.
    'config_contains',
})

DOOM_CONFIG_FILES = ('init.el', 'config.el', 'packages.el')


def _el_str(s) -> str:
    """Quote a path as an elisp string literal."""
    return '"' + str(s).replace('\\', '\\\\').replace('"', '\\"') + '"'


def leave_hook(scratch: Path, buf: Path, cur: Path) -> str:
    """Elisp that dumps the buffer and point when Emacs exits.

    Attached with `--eval` rather than written anywhere, so nothing persists
    past this one process and no configuration file is touched. See D1.
    """
    return (
        "(add-hook 'kill-emacs-hook"
        " (lambda ()"
        f"  (let ((b (get-file-buffer {_el_str(scratch)})))"
        "    (when b"
        "      (with-current-buffer b"
        f"       (write-region (point-min) (point-max) {_el_str(buf)} nil 'silent)"
        "        (write-region (format \"%d %d\" (line-number-at-pos)"
        f"                     (current-column)) nil {_el_str(cur)} nil 'silent))))))"
    )


def reminder(text: str) -> str:
    """Elisp that keeps the task visible above every buffer.

    `header-line-format` is the one line Emacs draws at the top of a window
    and nothing in a normal configuration fights for it, unlike the mode line.
    `setq-default` because the scratch buffer does not exist yet when this
    runs, and this process edits nothing else.

    A bare `%` in the text would be read as a mode-line construct, so it is
    doubled.
    """
    flat = ' '.join(str(text).split()).replace('%', '%%')
    return (f'(progn (setq-default header-line-format {_el_str(flat)})'
            f' (message {_el_str(flat)}))')


def doom_dir() -> Path:
    return Path(os.environ.get('DOOMDIR')
                or Path.home() / '.config' / 'doom')


def read_doom_config() -> str:
    """Concatenate the Doom config files that exist. Read-only, per D1."""
    out = []
    base = doom_dir()
    for name in DOOM_CONFIG_FILES:
        p = base / name
        try:
            if p.is_file():
                out.append(p.read_text(encoding='utf-8', errors='replace'))
        except OSError:
            continue
    return '\n'.join(out)


def server_running() -> bool:
    """Is an Emacs server answering? Optional capability, never required."""
    if not shutil.which('emacsclient'):
        return False
    try:
        r = subprocess.run(['emacsclient', '--eval', 't'],
                           capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return False
    return r.returncode == 0 and r.stdout.strip() == 't'


def eval_in_server(expr: str) -> str | None:
    """Evaluate read-only elisp in the running server, or None if unavailable."""
    if not server_running():
        return None
    try:
        r = subprocess.run(['emacsclient', '--eval', expr],
                           capture_output=True, text=True, timeout=TIMEOUT)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.strip() if r.returncode == 0 else None


class EmacsAdapter(BufferAdapter):
    name = 'emacs'
    requires = ('emacs',)
    description = 'reads the buffer you edited, and your Doom config'
    editor = 'Emacs'
    return_hint = 'C-x C-s to save, then C-x C-c to quit'
    expect_keys = EXPECT_KEYS

    def probe(self) -> tuple[bool, str]:
        if not shutil.which('emacs'):
            return False, 'emacs not installed'
        try:
            r = subprocess.run(['emacs', '--version'], capture_output=True,
                               text=True, timeout=TIMEOUT)
        except (OSError, subprocess.SubprocessError):
            return False, 'emacs is installed but not answering'
        return (True, '') if r.returncode == 0 else (False, 'emacs failed to start')

    def launch(self, scratch: Path, buf: Path, cur: Path,
               brief: str = '') -> list[str]:
        # `emacs -nw` rather than `emacsclient`: a separate process with its own
        # state, so a challenge cannot leave a stray buffer sitting in a daemon
        # the student is using for real work.
        head = ['emacs', '-nw']
        if brief:
            head += ['--eval', reminder(brief)]
        return head + ['--eval', leave_hook(scratch, buf, cur), str(scratch)]

    def observe(self) -> Observation:
        obs = super().observe()
        data = dict(obs.data)
        data['doom_config'] = read_doom_config()
        data['server'] = server_running()
        return Observation(obs.ok, data, obs.detail)

    def check(self, expect: dict, data: dict) -> tuple[bool, str]:
        wanted = expect.get('config_contains')
        if wanted:
            config = data.get('doom_config', '')
            missing = [w for w in ([wanted] if isinstance(wanted, str) else wanted)
                       if w not in config]
            if missing:
                return False, (f'{doom_dir()} does not mention '
                               f'{", ".join(repr(m) for m in missing)} yet')
            if len(expect) == 1:
                return True, f'found in {doom_dir().name}'
        rest = {k: v for k, v in expect.items() if k != 'config_contains'}
        return buffer_check(rest, data)
