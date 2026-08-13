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

#: Keep in-tool reminders to one line on a narrow terminal. A reminder that
#: wraps or gets truncated by the tool is worse than a short one.
MAX_INLINE = 68


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


def inline(challenge: dict, return_hint: str) -> str:
    """The single line carried into the tool.

    Goal first because that is what you re-read; the way out second because
    that is what you need once. Both, always: this line is the entire safety
    net for someone who has never opened this tool before.
    """
    goal = shorten(goal_of(challenge), MAX_INLINE)
    return f'hone: {goal}   [{_flat(return_hint)}]'


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
