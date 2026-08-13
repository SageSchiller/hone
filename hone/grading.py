"""In-process grading: the `graded` tier of D8.

The other two tiers need something outside the app. `verified` needs a real
tool to read back, `self` needs your word for it. This one needs neither,
because some answers can be checked exactly right here, and regex is the
clearest case.

**Patterns are graded by behaviour, never by string comparison.** There are
many correct regexes for any task, so checking the text of your answer against
a reference would fail people who were right. Instead the pattern is run
against strings it must match and strings it must **not** match. The negatives
are the important half: they are what catches a pattern that works by matching
far too much, which is the most common way a regex is quietly wrong.

**Runaway patterns report themselves.** `(a+)+$` against a few dozen characters
takes longer than the universe has, and a trainer that hangs on it would be
worse than useless. Execution is bounded, and hitting the bound is not an
error, it is a lesson: catastrophic backtracking is a real thing to learn about
and this is the moment to meet it.
"""

from __future__ import annotations

import re
import signal
from dataclasses import dataclass, field

#: Seconds a single pattern may run before it is treated as catastrophic.
TIMEOUT = 0.5

#: Guards so a pathological input cannot be handed to the engine at all. Test
#: strings in content are short sentences; nothing legitimate approaches these.
MAX_PATTERN = 400
MAX_SUBJECT = 2000

FLAG_MAP = {
    'i': re.IGNORECASE,
    'm': re.MULTILINE,
    's': re.DOTALL,
    'x': re.VERBOSE,
}


class PatternTimeout(Exception):
    """The pattern ran too long. Almost always catastrophic backtracking."""


@dataclass
class RegexResult:
    ok: bool
    #: Short sentence for the student. Says what went wrong, not just that it did.
    detail: str = ''
    #: Positives it failed to match, and negatives it wrongly matched.
    missed: list[str] = field(default_factory=list)
    over: list[str] = field(default_factory=list)
    error: str = ''
    timed_out: bool = False


def parse_flags(spec: str | None) -> int:
    flags = 0
    for ch in (spec or ''):
        flags |= FLAG_MAP.get(ch.lower(), 0)
    return flags


def _bounded_search(rx, subject: str) -> bool:
    """Run one search under a time bound.

    CPython's regex engine checks for pending signals while it runs, so an
    alarm interrupts a runaway match rather than waiting for it. Verified
    against the usual pathological patterns before this was relied on. The
    timer is always disarmed, including on the exception path, because a stray
    alarm firing later would surface somewhere unrelated and be miserable to
    diagnose.
    """
    def _fire(_sig, _frame):
        raise PatternTimeout()

    previous = signal.signal(signal.SIGALRM, _fire)
    signal.setitimer(signal.ITIMER_REAL, TIMEOUT)
    try:
        return rx.search(subject) is not None
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


def evaluate_regex(pattern: str, match: list[str], reject: list[str],
                   flags: str | None = None) -> RegexResult:
    """Does this pattern match everything it should and nothing it should not?"""
    pattern = (pattern or '').strip()
    if not pattern:
        return RegexResult(False, 'nothing typed yet')
    if len(pattern) > MAX_PATTERN:
        return RegexResult(False, 'that pattern is implausibly long')

    try:
        rx = re.compile(pattern, parse_flags(flags))
    except re.error as e:
        return RegexResult(False, f'that is not a valid pattern: {e}',
                           error=str(e))

    missed: list[str] = []
    over: list[str] = []
    try:
        for subject in match:
            if len(subject) <= MAX_SUBJECT and not _bounded_search(rx, subject):
                missed.append(subject)
        for subject in reject:
            if len(subject) <= MAX_SUBJECT and _bounded_search(rx, subject):
                over.append(subject)
    except PatternTimeout:
        return RegexResult(
            False,
            'that pattern took too long, which means catastrophic '
            'backtracking. Nested quantifiers like (a+)+ are the usual cause',
            timed_out=True)

    if not missed and not over:
        return RegexResult(True, 'matches everything it should, and nothing '
                                 'it should not')
    if missed and over:
        return RegexResult(False, f'misses {missed[0]!r} and wrongly matches '
                                  f'{over[0]!r}', missed=missed, over=over)
    if missed:
        return RegexResult(False, f'does not match {missed[0]!r}', missed=missed)
    # The interesting failure, and the reason the negatives exist at all.
    return RegexResult(False, f'matches too much: it also matches {over[0]!r}',
                       over=over)
