"""`--sync`: one remembered file, written on every clean exit.

**This is deliberately not a merge engine, and that is the whole design.**

Two machines that both drilled since the last sync have genuinely divergent
histories, and merging two SM-2 schedules means inventing an answer: whose
interval wins, whose lapse count survives, what happens to an item one machine
has never seen. Every answer to that is a guess about what you knew, which is
exactly the thing this app refuses to guess about elsewhere. Getting it wrong
silently corrupts the one file that represents your learning.

So sync does one honest thing: it remembers a path and keeps a current copy
there. Put that path in a synced folder and the copy travels. Taking it on the
other machine is `--import`, which is explicit, and which you run knowing it
replaces what is there.

The only cleverness is `check`, which compares timestamps and *tells* you when
the remembered file is ahead of local progress. It never acts on that. A tool
that silently replaced your progress because a file looked newer would be the
destructive surprise D1 exists to prevent.
"""

from __future__ import annotations

import json
from pathlib import Path

from .state import parse_iso

#: Ignore differences below this. Two machines' clocks are never identical, and
#: a five-second skew is not evidence that anything happened elsewhere.
SKEW_SECONDS = 60.0


def path_of(state) -> Path | None:
    raw = state.settings.get('sync_path')
    return Path(raw).expanduser() if raw else None


def set_path(state, dest: Path | None) -> None:
    state.set_setting('sync_path', str(dest) if dest else None)
    state.dirty = True


def push(state, at) -> tuple[bool, str]:
    """Write the current progress to the remembered path.

    Returns (ok, message). Never raises: a sync failure must not take down the
    session that produced the progress, and the progress is already safe in the
    real state file by the time this runs.
    """
    dest = path_of(state)
    if dest is None:
        return False, 'no sync file is set'
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        state.export_to(dest, at)
    except (OSError, ValueError) as e:
        return False, f'could not write {dest}: {e}'
    return True, f'progress copied to {dest}'


def _updated(path: Path):
    try:
        raw = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return None
    return parse_iso(raw.get('updated')) if isinstance(raw, dict) else None


def check(state) -> str:
    """One line if the remembered file is ahead of local progress, else ''.

    Advisory only, by design. The message names the command rather than
    offering to run it.
    """
    dest = path_of(state)
    if dest is None or not dest.exists():
        return ''
    theirs = _updated(dest)
    mine = parse_iso(state.data.get('updated'))
    if theirs is None or mine is None:
        return ''
    if (theirs - mine).total_seconds() <= SKEW_SECONDS:
        return ''
    return (f'note: {dest} is newer than your local progress. '
            f'Run  hone --import {dest}  to take it '
            f'(this replaces what is here).')
