"""D21: giving the terminal to the real tool, and taking it back.

Two ways to do that, and the choice is made here so no screen has to know
about it.

**Suspend and hand over** is the base behaviour and works everywhere. The
trainer restores the terminal, runs the tool in the foreground, and re-enters
when it exits. It is the pattern `git` uses for `$EDITOR`, which is why it
needs no explaining.

**Split the pane** is the enhancement, and only when the trainer is already
running inside tmux. The tool opens beside the trainer instead of replacing it,
so the task stays visible while you work. D21 made this optional on purpose:
it is the nicer first-run experience and the single most confusing thing to
debug when it misbehaves, so it is never required and `--no-split` turns it
off.

**Why polling rather than `tmux wait-for`.** `wait-for` is the elegant
synchronisation primitive and has one fatal mode: if the pane dies without
signalling, because the user killed it or the command crashed, the trainer
blocks forever with no way out. Polling for the pane id to disappear is robust
to every way a pane can end. Found by hanging a terminal for two minutes.

**Never hardcode a window index.** `session:0` does not exist wherever
`base-index` is 1, which is a real and common configuration and the exact
fragility this project's own tmux module warns about. Target the session.
"""

from __future__ import annotations

import os
import shlex
import subprocess
import time

#: How long to wait for the split pane to close before giving up and carrying
#: on. Generous: someone may genuinely spend twenty minutes in a challenge.
MAX_WAIT = 3600.0
POLL = 0.15
TMUX_TIMEOUT = 5.0


def in_tmux() -> bool:
    """Is the trainer itself running inside a tmux pane?"""
    return bool(os.environ.get('TMUX'))


def _tmux(*args: str) -> tuple[int, str]:
    try:
        r = subprocess.run(['tmux', *args], capture_output=True, text=True,
                           timeout=TMUX_TIMEOUT)
    except (OSError, subprocess.SubprocessError):
        return 127, ''
    return r.returncode, r.stdout.strip()


def can_split() -> bool:
    """Is the split enhancement available right now?"""
    if not in_tmux():
        return False
    return _tmux('display-message', '-p', '#{session_name}')[0] == 0


def pane_exists(pane_id: str) -> bool:
    code, out = _tmux('list-panes', '-a', '-F', '#{pane_id}')
    return code == 0 and pane_id in out.split()


def split_and_wait(argv: list[str], cwd: str | None = None,
                   vertical: bool = False, clock=time.monotonic,
                   env: dict[str, str] | None = None) -> bool:
    """Open `argv` in a new tmux pane and block until that pane closes.

    Returns True if the split happened and completed. False means the caller
    should fall back to suspend-and-hand-over, and every failure path returns
    False rather than raising, because a handover that cannot happen must not
    take the challenge down with it.
    """
    if not can_split():
        return False

    inner = shlex.join(argv) if argv else os.environ.get('SHELL', '/bin/sh')
    args = ['split-window', '-P', '-F', '#{pane_id}',
            '-v' if vertical else '-h']
    if cwd:
        args += ['-c', cwd]
    # `-e` landed in tmux 3.0. An older tmux rejects the whole command, and
    # the caller falls back to the suspended handover, which honours env
    # properly. Failing over is right: silently dropping the override would
    # point gpg at the student's real keyring, which is the one outcome the
    # env plumbing exists to prevent.
    for key, value in (env or {}).items():
        args += ['-e', f'{key}={value}']
    args.append(inner)

    code, pane_id = _tmux(*args)
    if code != 0 or not pane_id.startswith('%'):
        return False

    deadline = clock() + MAX_WAIT
    while clock() < deadline:
        if not pane_exists(pane_id):
            return True
        time.sleep(POLL)

    # Timed out. Leave the pane alone: it is the user's work, and killing it
    # would be exactly the destructive surprise D1 exists to prevent.
    return True


def tmux_attach_target(argv: list[str]) -> str | None:
    """The session name if `argv` is a plain `tmux attach -t <name>`.

    Pure, so the decision is testable. Anything more elaborate than the shape
    the tmux adapter emits returns None and takes the ordinary path.
    """
    if len(argv) == 4 and argv[0] == 'tmux' and \
            argv[1] in ('attach', 'attach-session') and argv[2] == '-t':
        return argv[3]
    return None


def switch_and_wait(session: str, clock=time.monotonic) -> bool:
    """Move this tmux client to `session`, and block until it leaves.

    The reason this exists: **a nested `tmux attach` from inside tmux is
    refused outright**, so both the split pane and the suspended handoff
    bounced straight back and the challenge graded an empty session. On a
    single server the right primitive is switch-client: no nesting, and the
    prefix key reaches the drill session natively instead of being eaten by
    the outer session.

    'Until it leaves' is observed as the drill session having no clients,
    which covers every way back: switching away, `choose-tree`, or detaching
    entirely. Polling, not wait-for, for the reasons at the top of this file.
    """
    if not in_tmux():
        return False
    code, _ = _tmux('switch-client', '-t', session)
    if code != 0:
        return False
    # One line in the drill session's status bar saying how to come back.
    # Best effort: the student was told in the brief as well.
    _tmux('display-message', '-t', session,
          'hone is waiting: switch back (C-b L) or detach when done')

    deadline = clock() + MAX_WAIT
    while clock() < deadline:
        code, out = _tmux('list-clients', '-t', session, '-F', '#{client_name}')
        if code != 0 or not out.strip():
            return True
        time.sleep(POLL)
    return True


def describe(argv: list[str], cwd: str | None) -> str:
    """One line telling the student what is about to happen."""
    what = shlex.join(argv) if argv else 'a shell'
    where = f' in {cwd}' if cwd else ''
    return f'{what}{where}'
