"""Shared machinery for adapters that grade by running the real tool.

The other adapters watch you work and read the end state afterwards. These
ones take an answer you typed and *run* it, then compare what it produced
against what the reference answer produces. Same idea as `grading.evaluate_regex`
and for the same reason: there are many correct filters for any question, so
comparing the text of your answer to a reference would fail people who were
right. `tcp port 443` and `port 443 and tcp` are the same filter and both
must pass.

**D25 governs this: the trainer runs text you typed, and says so.** D1's
"never runs a command you did not perform yourself" was written against a
trainer that could only watch. Typing an answer into a box that is labelled as
running it *is* performing it, and this is strictly narrower than what D21
already does: a challenge handover drops you at a real interactive shell with
no timeout and no sandbox, which is a far larger capability than one bounded
command. The rules that keep it honest:

* Nothing reaches a shell. The answer is passed as a single argv element to a
  program that parses it as its own language, so there is no word splitting,
  no globbing, and no `;` to smuggle a second command through. The one
  exception is PowerShell, where the answer *is* a program, and that adapter
  says as much on screen before you type.
* Every run is bounded by a timeout and killed on expiry. A student writing an
  infinite loop learns something; a trainer that hangs teaches nothing.
* The working directory is a sandbox this module created and will destroy.
* Nothing here reaches the network, and the fixture is generated locally.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field

#: SGR and friends. Tools colour their errors when they think a human is
#: looking, and a captured pipe apparently counts: PowerShell wraps its
#: exception text in red before we ever see it. Comparing or printing those
#: bytes would leak escape codes into the UI and, worse, make two identical
#: outputs differ.
ANSI = re.compile(r'\x1b\[[0-9;?]*[a-zA-Z]|\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)')


def strip_ansi(s: str) -> str:
    return ANSI.sub('', s)

#: Seconds one graded run may take. Generous for a filter over fifteen
#: packets, and short enough that a runaway answer is caught while the student
#: is still looking at the screen.
TIMEOUT = 6.0

#: A typed answer longer than this is not a filter or a pipeline, it is a
#: paste accident. Refused before it reaches a subprocess.
MAX_ANSWER = 500

#: Truncation bound on captured output, so a pathological answer that prints
#: forever cannot be held in memory in full.
MAX_OUTPUT = 256 * 1024


class OracleUnavailable(RuntimeError):
    """The tool vanished between probing and running. Degrades per D18."""


@dataclass
class Run:
    """One completed subprocess."""

    rc: int
    out: str
    err: str
    timed_out: bool = False

    @property
    def ok(self) -> bool:
        return self.rc == 0 and not self.timed_out

    def first_error(self) -> str:
        """The most useful line of stderr, for showing to a student.

        Tools put the diagnosis on a line of its own and surround it with
        preamble that is noise here: tcpdump announces which file it opened
        before it complains, and the file is not the student's problem.
        """
        for line in strip_ansi(self.err).splitlines():
            line = line.strip()
            if not line or line.startswith('reading from file'):
                continue
            if line.startswith('Warning:'):
                continue
            return line
        rest = strip_ansi(self.err).strip()
        return rest.splitlines()[0] if rest else ''


@dataclass
class Verdict:
    """The result of comparing an answer against the reference.

    Deliberately the same shape as `grading.RegexResult`: `missed` is what the
    reference selected and you did not, `over` is what you selected and it did
    not. The second is the interesting half, exactly as with regex, because a
    filter that matches too much is the failure that looks like success.
    """

    ok: bool
    detail: str = ''
    missed: list[str] = field(default_factory=list)
    over: list[str] = field(default_factory=list)
    error: str = ''
    timed_out: bool = False


def run(argv: list[str], cwd: str | None = None,
        timeout: float = TIMEOUT, env: dict | None = None) -> Run:
    """Run one command, bounded, capturing both streams.

    `shell=False` always, and never with a string: the answer travels as one
    argv element and the tool parses it as its own language. This is the line
    that makes D25 safe to hold.
    """
    try:
        proc = subprocess.run(argv, cwd=cwd, capture_output=True, text=True,
                              timeout=timeout, shell=False, env=env,
                              errors='replace')
    except subprocess.TimeoutExpired as e:
        return Run(rc=-1,
                   out=_clip(_text(e.stdout)),
                   err=_clip(_text(e.stderr)),
                   timed_out=True)
    except FileNotFoundError as e:
        raise OracleUnavailable(str(e)) from e
    except OSError as e:
        raise OracleUnavailable(str(e)) from e
    return Run(rc=proc.returncode, out=_clip(proc.stdout), err=_clip(proc.stderr))


def _text(raw) -> str:
    if raw is None:
        return ''
    return raw.decode('utf-8', 'replace') if isinstance(raw, bytes) else raw


def _clip(s: str) -> str:
    return s if len(s) <= MAX_OUTPUT else s[:MAX_OUTPUT] + '\n[output truncated]'


def check_answer(answer: str) -> str | None:
    """Reject an answer before it reaches a subprocess. None means fine."""
    answer = (answer or '').strip()
    if not answer:
        return 'nothing typed yet'
    if len(answer) > MAX_ANSWER:
        return 'that is implausibly long for an answer'
    if '\x00' in answer:
        return 'that contains a null byte'
    return None


def describe_sets(missed: list[str], over: list[str], noun: str = 'packet') -> str:
    """One sentence naming what went wrong, in grading.py's voice.

    Never just "wrong": the whole value of running the answer is being able to
    say *which* things it picked up or dropped.
    """
    plural = f'{noun}s'
    if not missed and not over:
        return f'selects exactly the right {plural}'
    if missed and over:
        return (f'misses {len(missed)} {plural if len(missed) != 1 else noun} '
                f'and wrongly selects {len(over)}: {over[0]}')
    if missed:
        return (f'too narrow: it misses {len(missed)} '
                f'{plural if len(missed) != 1 else noun}, starting with '
                f'{missed[0]}')
    return (f'too broad: it also selects {len(over)} '
            f'{plural if len(over) != 1 else noun} it should not, '
            f'starting with {over[0]}')
