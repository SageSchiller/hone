"""The pcap adapter: your filter, run against a real capture file.

This is the adapter the tcpdump module was said to be unable to have. The
stated reason was that D1 forbids capturing traffic, which is true and stays
true: nothing here opens an interface, and `dumpcap` being unreadable by
ordinary users is not an obstacle because it is never invoked. The capture
file is *written* by `pcapgen`, byte by byte, and reading a file needs no
privilege at all.

**Both languages are graded, which is the point of the module.** A capture
filter is compiled and run by `tcpdump -r`; a display filter is run by
`tshark -r -Y`. The module's whole thesis is that these are two different
languages, and until now it could only assert that. Now a student who types
`tcp.port == 443` into a capture-filter drill gets tcpdump's own parse error
back, and the same string in the next drill passes. That contrast is worth
more coming from the tool than from a paragraph.

**Answers are compared by which packets they select, never by their text.**
`tcp port 443`, `port 443 and tcp` and `tcp and port 443` are one filter with
three spellings, and a trainer that accepted only the spelling it thought of
would be teaching typing. The comparison is a set difference against the
reference filter's selection, reported as too narrow or too broad in the same
words `grading.py` uses for regex, because it is the same mistake.

**Degrades per D18.** No tcpdump, no capture-filter grading; no tshark, no
display-filter grading. Either way the drill falls back to a text comparison
against the reference answer and is labelled `checked` rather than `verified`,
so nothing claims to have run that did not.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from .. import pcapgen
from . import Adapter, AdapterError, Observation
from ._oracle import Verdict, check_answer, describe_sets, run

#: The two languages, and how each is run against the fixture. `-tt` gives an
#: absolute timestamp per packet, which is what identifies a matched packet:
#: `pcapgen` spaces its packets 10ms apart precisely so this is unique.
CAPTURE, DISPLAY = 'capture', 'display'

FIXTURE = 'capture.pcap'

EXPECT_KEYS = frozenset({'language', 'reference', 'selects'})


def _argv(language: str, path: str, expression: str) -> list[str]:
    if language == DISPLAY:
        # -T fields with frame.number is stable across tshark versions in a
        # way the default one-line summary is not, and it gives the packet
        # identity directly rather than by parsing a printed timestamp.
        return ['tshark', '-r', path, '-T', 'fields', '-e', 'frame.number',
                '-Y', expression]
    return ['tcpdump', '-nn', '-tt', '-r', path, expression]


def _selection(language: str, out: str) -> list[int]:
    """The packets a run selected, as packet numbers, in order.

    Both tools are reduced to the same identity here. tshark is asked for
    `frame.number` outright; tcpdump only knows clocks, so its timestamps are
    mapped back through the spacing `pcapgen` applied. Without a common
    identity the two languages could not be compared against each other, which
    is the module's whole subject.
    """
    picked: list[int] = []
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        if language == DISPLAY:
            if line.isdigit():
                picked.append(int(line))
            continue
        stamp = line.split(' ', 1)[0]
        # A continuation line of a hex dump or a wrapped payload does not
        # begin with a timestamp, and counting it would double-count a packet
        # the student selected once.
        try:
            number = pcapgen.number_for(float(stamp))
        except ValueError:
            continue
        if number is not None:
            picked.append(number)
    return picked


class PcapAdapter(Adapter):
    name = 'pcap'
    requires = ('tcpdump',)
    description = 'runs your filter against a capture file it wrote'
    expect_keys = EXPECT_KEYS
    return_hint = 'type your filter and press Enter'

    #: Grading a display filter needs tshark as well. Absence is not fatal to
    #: the adapter, only to the display half, so it is probed separately
    #: rather than being added to `requires`: a machine with tcpdump and no
    #: tshark should still get its capture-filter drills graded.
    display_requires = ('tshark',)

    def __init__(self) -> None:
        super().__init__()
        self.dir: Path | None = None

    def opens(self, spec: dict) -> str:
        # Names Enter because that is the moment the answer runs, which D25
        # requires be disclosed before anything is typed rather than after.
        return ('Enter runs your filter against a capture file hone wrote. '
                'Nothing is captured and no interface is touched.')

    def grades(self, language: str) -> bool:
        """Can this language be graded on this machine right now?"""
        if language == DISPLAY:
            return all(shutil.which(b) for b in self.display_requires)
        return bool(shutil.which('tcpdump'))

    def why_not(self, language: str) -> str:
        if language == DISPLAY:
            missing = [b for b in self.display_requires if not shutil.which(b)]
            if missing:
                return f'{", ".join(missing)} not installed'
        elif not shutil.which('tcpdump'):
            return 'tcpdump not installed'
        return ''

    # -- lifecycle ---------------------------------------------------------

    def setup(self, spec: dict) -> None:
        """Write the fixture into our own temp directory. See D1."""
        self.teardown()
        self.dir = Path(tempfile.mkdtemp(prefix='hone-pcap-'))
        pcapgen.write(self.dir / FIXTURE)

    @property
    def fixture(self) -> str:
        if self.dir is None:
            raise AdapterError('pcap adapter used before setup()')
        return str(self.dir / FIXTURE)

    def handoff(self, spec: dict) -> list[str]:
        # There is no handover: the answer is typed into hone and run here.
        # A student who wants a real shell to explore the file in still gets
        # one from the module's challenges, which use the sandbox adapter.
        return []

    def handoff_cwd(self, spec: dict) -> str | None:
        return str(self.dir) if self.dir else None

    def observe(self) -> Observation:
        if self.dir is None or not (self.dir / FIXTURE).is_file():
            return Observation(False, {'present': False}, 'the fixture is gone')
        return Observation(True, {'present': True, 'fixture': self.fixture},
                           'capture file ready')

    def teardown(self) -> None:
        if self.dir is None:
            return
        shutil.rmtree(self.dir, ignore_errors=True)
        self.dir = None

    # -- grading -----------------------------------------------------------

    def select(self, language: str, expression: str) -> tuple[list[str], object]:
        """Run one expression and return (packets it selected, the Run)."""
        result = run(_argv(language, self.fixture, expression))
        return _selection(language, result.out), result

    def evaluate(self, answer: str, reference: str,
                 language: str = CAPTURE) -> Verdict:
        """Grade a typed filter against the reference, by what each selects."""
        problem = check_answer(answer)
        if problem:
            return Verdict(False, problem)

        if self.dir is None:
            self.setup({})

        try:
            got, got_run = self.select(language, answer.strip())
        except Exception as e:
            return Verdict(False, f'could not run that: {e}', error=str(e))

        if got_run.timed_out:
            return Verdict(False, 'that took too long to run', timed_out=True)
        if not got_run.ok:
            # The tool's own diagnosis, which is the most useful thing that
            # can be said, and is the entire lesson when someone has typed a
            # display filter into a capture-filter drill.
            return Verdict(False, _explain(language, got_run.first_error()),
                           error=got_run.first_error())

        want, want_run = self.select(language, reference)
        if not want_run.ok:
            # The authored reference is broken, not the student's answer.
            # Refusing to grade is the only honest move. validate.py runs every
            # reference at build time so this should be unreachable in a
            # shipped build.
            raise AdapterError(f'reference filter failed: '
                               f'{want_run.first_error()}')

        missed = [pcapgen.label(p) for p in want if p not in set(got)]
        over = [pcapgen.label(p) for p in got if p not in set(want)]
        ok = not missed and not over
        return Verdict(ok, describe_sets(missed, over), missed=missed, over=over)

    def check(self, expect: dict, data: dict) -> tuple[bool, str]:
        """Challenge-shaped entry point, for `verify.expect`."""
        if not data.get('present'):
            return False, 'the fixture is gone'
        answer = str(data.get('answer', ''))
        reference = str(expect.get('reference', ''))
        if not reference:
            return False, 'this challenge names no reference filter'
        verdict = self.evaluate(answer, reference,
                               str(expect.get('language', CAPTURE)))
        return verdict.ok, verdict.detail


def _explain(language: str, error: str) -> str:
    """Turn a tool's parse error into the lesson it is really teaching.

    The single most common mistake in this module is typing one language into
    the other, and both tools report it as an ordinary syntax error. Naming it
    is the difference between a dead end and the point of the exercise.
    """
    if not error:
        return 'that did not run'
    lowered = error.lower()
    if language == CAPTURE and ('parse filter' in lowered
                                or 'syntax error' in lowered):
        return (f'{error}  '
                '(dots and == are display-filter syntax; a capture filter is '
                'words and spaces)')
    if language == DISPLAY and 'unexpected in this context' in lowered:
        return (f'{error}  '
                '(that is capture-filter syntax; a display filter uses '
                'dotted field names and ==)')
    return error
