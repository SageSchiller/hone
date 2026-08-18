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


#: Height of the steps window, in lines. Enough for a goal and four or five
#: steps with hints, and never more than about a third of an 80x24 terminal:
#: the work is the point and the instructions are the reference.
STEPS_MIN, STEPS_MAX = 5, 12

STEPS_BUFFER = '*hone*'


def steps_window(lines: list[str]) -> str:
    """Elisp opening the task in a second window under the file.

    **Why a window and not a longer header line.** A header line holds one
    line, and a guided challenge is a numbered list. Someone testing the Doom
    module could not read the steps and do the work at the same time, because
    the steps were on the screen Emacs had just replaced. Splitting is the
    thing Emacs is actually good at, and it costs a hook.

    Run from `emacs-startup-hook` rather than inline, because an `--eval` on
    the command line is evaluated *before* the file argument is visited, so
    splitting there would put the file in whichever window happened to be
    selected afterwards. The hook runs once everything is loaded.

    The buffer is read-only and its window dedicated, so `C-x C-s` from inside
    it cannot try to save the instructions over the student's work, and point
    is left in the file so the first keystroke goes where it was aimed.
    """
    if not lines:
        return ''
    text = '\n'.join(str(l) for l in lines)
    # The size passed to `split-window` is the whole window, mode line
    # included, so the body is one row shorter than it looks. Measured against
    # real Doom: asking for 7 with six lines of text showed five of them.
    height = max(STEPS_MIN, min(STEPS_MAX, len(lines) + 1))
    return (
        "(add-hook 'emacs-startup-hook"
        " (lambda ()"
        "  (condition-case nil"
        f"   (let ((b (get-buffer-create {_el_str(STEPS_BUFFER)}))"
        "         (origin (selected-window)))"
        "     (with-current-buffer b"
        "       (let ((inhibit-read-only t))"
        "         (erase-buffer)"
        f"        (insert {_el_str(text)}))"
        "       (goto-char (point-min))"
        # `reminder` sets header-line-format with setq-default, so this buffer
        # would inherit it and spend a row repeating the line already on
        # screen above it. The steps window is the long form; it does not need
        # the short one.
        "       (setq header-line-format nil)"
        "       (setq buffer-read-only t))"
        f"     (let ((w (split-window origin (- {height}) 'below)))"
        "       (set-window-buffer w b)"
        "       (set-window-dedicated-p w t))"
        "     (select-window origin))"
        # A failure here must never stop the student editing. Losing the
        # steps window is a worse session; losing the editor is a lost one.
        "   (error nil))))"
    )


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
    return_hint = 'C-x C-s saves, C-x C-c quits'
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
               brief: str = '', steps: list[str] | None = None) -> list[str]:
        # `emacs -nw` rather than `emacsclient`: a separate process with its own
        # state, so a challenge cannot leave a stray buffer sitting in a daemon
        # the student is using for real work.
        head = ['emacs', '-nw']
        if brief:
            head += ['--eval', reminder(brief)]
        window = steps_window(steps or [])
        if window:
            head += ['--eval', window]
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
