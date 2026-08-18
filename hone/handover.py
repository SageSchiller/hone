"""What the student is told when the trainer hands them a real tool.

This module exists because of one specific failure, reported the first time
anyone but the author used the app: press Enter on a vim challenge, nvim opens
on top of hone, and you have no idea what you are supposed to do or how to get
back. Everything you needed was on the screen you just left.

D21 gives the terminal to the real tool, and that is the right design. What was
missing is that a handover is a *transition*, and a transition needs three
things said out loud:

1. **What is about to happen.** Which tool opens, on what, starting from what.
   Surprise is the enemy here: a beginner who did not expect nvim reads its
   arrival as a crash.
2. **What you are trying to do.** The goal, carried into the tool, so it is
   still in front of you when the briefing screen is gone.
3. **How you get back.** Every tool has a different answer and none of them are
   guessable. This is the one a stranger cannot recover from on their own,
   because the usual instinct (close the terminal) destroys the session.

Point 1 is rendered on the brief screen before Enter. Points 2 and 3 travel
*into* the tool, because that is where they are needed: a statusline in nvim, a
header line in Emacs, a message in tmux, printed text in a shell.

Nothing here writes anything or changes a tool's configuration. The reminders
are set on the process the trainer launched, for the life of that process only.
"""

from __future__ import annotations

import os
import shutil
import stat
import tempfile
from pathlib import Path

#: Keep in-tool reminders to one line on a narrow terminal. A reminder that
#: wraps or gets truncated by the tool is worse than a short one.
#:
#: This is the budget for the **whole line**, not for the goal inside it. It
#: used to be the goal's budget alone, and the way out was appended after it,
#: which produced 104 to 118 characters for every adapter in the app: on the
#: 80-column terminal this project treats as the floor, the tail was cut off
#: in every tool, and the tail is the way out. Someone testing the Doom module
#: could read the task and could not find how to close Emacs, which is the
#: exact failure this file was written to prevent.
#:
#: 79 rather than 80 because a statusline or header line that fills the last
#: cell can wrap on some terminals.
MAX_INLINE = 79

#: Never shorten the goal below this. If the way out is so long that less than
#: this is left, the line is allowed to run over instead: a truncated key
#: sequence ("C-x C-s to save, then C-x C-c to qui") is worse than a long line,
#: because it is confidently wrong rather than merely cut off.
MIN_GOAL = 24


def _flat(s: str) -> str:
    """One line, no runs of whitespace. Anything else breaks a statusline."""
    return ' '.join(str(s).split())


def shorten(s: str, limit: int = MAX_INLINE) -> str:
    s = _flat(s)
    if len(s) <= limit:
        return s
    cut = s[:limit - 1]
    # Prefer a word boundary, but never produce a stub.
    space = cut.rfind(' ')
    if space > limit * 0.6:
        cut = cut[:space]
    return cut.rstrip(' ,.;:') + '.'


def goal_of(challenge: dict) -> str:
    """The shortest honest statement of the task.

    `free` is the one-sentence version written for the no-scaffolding rigor,
    which makes it exactly right for a one-line reminder. `goal` is the fuller
    prose and is the fallback.
    """
    return _flat(challenge.get('free') or challenge.get('goal') or
                 challenge.get('title') or 'the task')


def inline(challenge: dict, return_hint: str, width: int = MAX_INLINE) -> str:
    """The single line carried into the tool.

    Goal first because that is what you re-read; the way out second because
    that is what you need once. Both, always: this line is the entire safety
    net for someone who has never opened this tool before.

    **The way out is budgeted first even though it is printed second.** Order
    on the screen is about reading; order in the budget is about what survives
    a narrow terminal, and those are different questions with different
    answers. The goal is also on the brief screen and in the tool's own task
    list; the way out is the one thing a stranger cannot recover on their own,
    so it is the one thing that must not be the part that gets cut.
    """
    hint = _flat(return_hint)
    tail = f'   [{hint}]' if hint else ''
    room = width - len('hone: ') - len(tail)
    goal = shorten(goal_of(challenge), max(room, MIN_GOAL))
    return f'hone: {goal}{tail}'


def briefing(challenge: dict, rigor: str, show_hints: bool,
             return_hint: str = '') -> list[str]:
    """The whole task at the rigor the student chose, as plain lines.

    One line was never enough. `inline` carries the goal and the way out, which
    is the safety net, but a guided challenge is a numbered list and the whole
    point of guided is that you work through it *while looking at it*. Someone
    testing the Doom module could not: the editor takes the terminal, the
    briefing screen is gone, and the steps were on it.

    So this is the full text, built once and shown wherever it can be. A shell
    handover prints it, because a shell does not clear the screen. An editor
    opens it in a second window beside the work, because an editor does. The
    two used to be separate code and could drift; now the student sees exactly
    the same words whichever tool they are handed.

    `free` deliberately gets the goal and nothing else. That is what free
    means, and a rigor that quietly hands over the steps anyway is not a
    rigor.
    """
    out = [goal_of(challenge)]
    if rigor != 'free':
        for i, step in enumerate(challenge.get('steps') or (), 1):
            out.append(f'  {i}. {_flat(step.get("instruction", ""))}')
            hint = step.get('hint')
            if hint and (rigor == 'guided' or show_hints):
                out.append(f'     hint: {_flat(hint)}')
    if return_hint:
        out.append('')
        out.append(f'When you are done, {_flat(return_hint)}.')
        out.append('hone will then check your work.')
    return out


#: The command dropped on PATH for shell handovers.
TASK_CMD = 'task'

#: Heredoc delimiter for the generated script. Distinctive so no line of a
#: briefing can accidentally terminate it.
_EOF = '__HONE_TASK_EOF__'


def task_helper(lines: list[str]) -> Path | None:
    """A throwaway directory holding a `task` command that reprints `lines`.

    **Why a command rather than just printing.** A shell handover prints the
    briefing once, which is the whole of D21's answer for a shell and is fine
    for about ninety seconds. Then you run `ls`, and `cat`, and something that
    fails, and the task has scrolled off the top of a terminal you cannot
    scroll back in without leaving the tool. An editor at least keeps its
    screen; a shell eats it.

    **Why its own directory, and not the sandbox.** `SandboxAdapter.observe`
    walks the whole tree, hidden entries included, so anything hone drops in
    there shows up in file listings and in any challenge that asserts on the
    exact contents of a directory. The helper therefore lives outside the
    sandbox entirely and reaches the shell through PATH.

    Prepended rather than appended, because the directory contains exactly one
    file and nothing a challenge ever calls is named `task`. Appending would
    let a student's Taskwarrior shadow it and quietly break the one command
    the briefing just told them to run.

    Returns None when there is nothing to say, which keeps the caller free of
    a special case.
    """
    body = [str(l) for l in lines if l is not None]
    if not body:
        return None
    directory = Path(tempfile.mkdtemp(prefix='hone-task-'))
    script = directory / TASK_CMD
    script.write_text(
        '#!/bin/sh\n'
        f"cat <<'{_EOF}'\n" + '\n'.join(body) + f'\n{_EOF}\n',
        encoding='utf-8')
    script.chmod(script.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP)
    return directory


def task_env(directory: Path | None,
             environ: dict | None = None) -> dict[str, str]:
    """PATH override putting `task` in reach, or {} if there is no helper."""
    if directory is None:
        return {}
    current = (environ if environ is not None else os.environ).get('PATH', '')
    return {'PATH': f'{directory}{os.pathsep}{current}' if current
                    else str(directory)}


def discard(directory: Path | None) -> None:
    """Remove a helper directory. Never raises: this runs on the way out."""
    if directory is not None:
        shutil.rmtree(directory, ignore_errors=True)


def what_happens(challenge: dict, plan) -> list[str]:
    """Lines for the brief screen describing the handover, before it happens.

    Returns plain strings; the screen styles them. Empty when there is nothing
    to hand over, which is the self-marked case, and there the screen says its
    own thing instead.
    """
    adapter = getattr(plan, 'adapter', None)
    if adapter is None:
        return []

    spec = challenge.get('setup') or {}
    out = [adapter.opens(spec)]

    start = starting_state(spec)
    if start:
        out.append('')
        out.extend(start)

    out.append('')
    out.append(f'To come back: {_flat(adapter.return_hint)}')
    out.append('hone then reads what you did and tells you how it went.')
    return out


def starting_state(spec: dict) -> list[str]:
    """What will already be there when the tool opens.

    Derived from the challenge's own `setup`, so every challenge gets this for
    free and none of them had to be rewritten. Not knowing the starting state
    is most of the disorientation: 'change world to EARTH' means nothing until
    you know a file already contains 'hello world here'.
    """
    lines: list[str] = []

    start = spec.get('start')
    if start:
        if isinstance(start, str):
            start = start.split('\n')
        lines.append('It starts with these lines:')
        for text in list(start)[:6]:
            lines.append(f'    {text}')
        if len(list(start)) > 6:
            lines.append('    ...')
        return lines

    tree = spec.get('tree')
    if tree:
        names = sorted(tree)
        lines.append('The directory already contains:')
        for name in names[:6]:
            lines.append(f'    {name}')
        if len(names) > 6:
            lines.append(f'    ... and {len(names) - 6} more')
        return lines

    commits = spec.get('commits')
    if commits:
        n = len(commits)
        lines.append(f'The repository already has {n} '
                     f'commit{"" if n == 1 else "s"}:')
        for c in commits[:4]:
            lines.append(f'    {c.get("message", "commit")}')
        if n > 4:
            lines.append('    ...')
        return lines

    return lines
