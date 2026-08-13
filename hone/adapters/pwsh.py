"""The pwsh adapter: your pipeline, actually run.

PowerShell is the module in the roster most often learned by reading, because
the machine people want to run it on is usually somebody else's Windows box.
That is exactly why it needs checking: a language whose central idea is that
the pipeline carries objects rather than text is one you can nod along to for
an hour and still write `| grep` in.

**pwsh runs on Linux, so the object half of the module is fully checkable**,
and that half is the part worth learning: `Sort-Object`, `Where-Object`,
`Select-Object`, `Group-Object`, `Measure-Object`, `Get-Member`, calculated
properties, `-match` against `-like`, and the discipline of never putting a
`Format-*` anywhere but the end of a pipeline. None of that is Windows-specific
and all of it is where beginners actually go wrong.

**The Windows half stays honest and stays self-marked.** `Get-WinEvent`,
`Get-Service`, the registry and WMI do not exist here and are not faked.
Shipping a fake `Get-WinEvent` would be worse than shipping nothing: the entire
lesson of that content is that filtering belongs at the source, in
`-FilterHashtable`, because the source is a log with millions of records and a
`Where-Object` downstream reads all of them. A fake with fifty rows in it
teaches the opposite of that by making both approaches feel instant. What the
sandbox *does* ship is a table of synthetic logon records for practising the
object-shaping half, labelled in the content as what it is: not an event log.

**D25 applies with its sharpest edge here.** A BPF filter is parsed as a
filter; a PowerShell answer is a program, and running it is running code the
student wrote. That is disclosed on screen before anything is typed, it is
bounded by a timeout, it runs with `-NoProfile -NonInteractive` so the
student's own profile cannot change the result, and its working directory is a
sandbox this adapter made and will delete. It remains a strictly smaller
capability than the interactive shell D21 already hands out.

**Authoring discipline.** Answers are compared on their printed output, so a
graded drill must ask for output with one obvious form: "the names, one per
line" grades cleanly, "list the files" does not, because a dozen correct
pipelines print a dozen different tables. `validate.py` runs every reference
at build time, which catches the ambiguous ones by making the author look at
what their own answer prints.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from . import Adapter, AdapterError, Observation
from ._oracle import Verdict, check_answer, run, strip_ansi

EXPECT_KEYS = frozenset({'reference', 'prints'})

#: `-NoProfile` so the author's own profile cannot make an answer pass here
#: and fail everywhere else; `-NonInteractive` so a prompt is an error rather
#: than a hang; `-Command` because the answer is an expression, not a file.
BASE_ARGV = ('pwsh', '-NoProfile', '-NonInteractive', '-Command')

#: Prepended to every expression, the student's and the reference's alike, so
#: neither gets an advantage. PowerShell 7 colours its output and its errors
#: even into a pipe, and a progress bar written to stderr would otherwise
#: appear in the middle of a diff.
PREAMBLE = ("$PSStyle.OutputRendering='PlainText';"
            "$ProgressPreference='SilentlyContinue';")

#: Aliases PowerShell **removes on Linux and macOS** because they would shadow
#: real binaries, which is the single most confusing difference for someone
#: learning on this platform to use on Windows. Typing `sort Length -Desc`
#: here does not fail with "unknown alias", it silently runs `/usr/bin/sort`
#: and complains about a flag, which is an error message pointing at the wrong
#: universe entirely. Detected so the feedback can say what really happened.
UNIX_SHADOWED = {
    'sort': 'Sort-Object', 'ls': 'Get-ChildItem', 'cat': 'Get-Content',
    'cp': 'Copy-Item', 'mv': 'Move-Item', 'rm': 'Remove-Item',
    'ps': 'Get-Process', 'diff': 'Compare-Object', 'echo': 'Write-Output',
    'pwd': 'Get-Location', 'kill': 'Stop-Process', 'tee': 'Tee-Object',
    'man': 'Get-Help',
}

#: Sample tree, chosen so the obvious questions have unambiguous answers:
#: distinct sizes so sorting by length is total, one name with a space in it
#: because that is the drill that separates the two shells, and one extension
#: that appears twice so grouping has something to group.
FILES: dict[str, int] = {
    'notes.txt': 120,
    'report.txt': 4096,
    'archive.zip': 51200,
    'image.png': 2048,
    'my report.txt': 8192,
    'script.ps1': 640,
}

#: Synthetic logon records. Deliberately a CSV and deliberately not called an
#: event log: see the module docstring. The shape mirrors what a 4625 hunt
#: produces after `Select-Object`, so the object-shaping practice transfers.
#:
#: **No ties in the failure counts**, which is a grading constraint rather
#: than a realism one. "Which account failed most" has to have one answer, or
#: two students writing equivalent pipelines get different output depending on
#: how their sort broke the tie, and the one who came second is marked wrong
#: for someone else's implementation detail. jsmith 4, admin 3, svc_backup 2.
LOGONS = '''TimeCreated,Id,Account,Workstation,LogonType
2026-08-01T22:14:03,4625,jsmith,WS-014,3
2026-08-01T22:14:19,4625,jsmith,WS-014,3
2026-08-01T22:15:02,4625,jsmith,WS-014,3
2026-08-01T23:41:55,4625,admin,WS-002,10
2026-08-02T01:03:12,4625,svc_backup,SRV-DB1,5
2026-08-02T01:03:44,4625,svc_backup,SRV-DB1,5
2026-08-02T02:22:07,4624,jsmith,WS-014,3
2026-08-02T08:15:31,4624,rlee,WS-031,2
2026-08-02T09:44:10,4625,admin,WS-002,10
2026-08-02T09:44:38,4625,admin,WS-002,10
2026-08-02T10:02:11,4625,jsmith,WS-014,3
'''


class PwshAdapter(Adapter):
    name = 'pwsh'
    requires = ('pwsh',)
    description = 'runs your pipeline in a real PowerShell'
    expect_keys = EXPECT_KEYS
    return_hint = 'type your pipeline and press Enter'

    def __init__(self) -> None:
        super().__init__()
        self.dir: Path | None = None

    def opens(self, spec: dict) -> str:
        # D25 at its sharpest: what follows is not a filter being parsed, it
        # is a program being run, and the student is told so before typing.
        return ('Enter runs what you typed in a real PowerShell, in a '
                'throwaway directory hone made. Nothing outside it is touched.')

    # -- lifecycle ---------------------------------------------------------

    def setup(self, spec: dict) -> None:
        """Build the sample tree. Our own directory only, per D1."""
        self.teardown()
        self.dir = Path(tempfile.mkdtemp(prefix='hone-pwsh-'))
        for name, size in FILES.items():
            # Written as one repeated character rather than random bytes so
            # the fixture is byte-identical everywhere, for the same reason
            # pcapgen pins its timestamps.
            (self.dir / name).write_text('x' * size, encoding='utf-8')
        (self.dir / 'logons.csv').write_text(LOGONS, encoding='utf-8')

    def handoff(self, spec: dict) -> list[str]:
        return []   # the answer is typed into hone, not into a handover

    def handoff_cwd(self, spec: dict) -> str | None:
        return str(self.dir) if self.dir else None

    def observe(self) -> Observation:
        if self.dir is None or not self.dir.is_dir():
            return Observation(False, {'present': False}, 'the sandbox is gone')
        return Observation(True, {'present': True, 'dir': str(self.dir)},
                           f'{len(FILES)} sample files ready')

    def teardown(self) -> None:
        if self.dir is None:
            return
        shutil.rmtree(self.dir, ignore_errors=True)
        self.dir = None

    # -- grading -----------------------------------------------------------

    def execute(self, expression: str):
        """Run one expression in the sandbox and return the Run."""
        if self.dir is None:
            raise AdapterError('pwsh adapter used before setup()')
        return run([*BASE_ARGV, PREAMBLE + expression], cwd=str(self.dir))

    def evaluate(self, answer: str, reference: str) -> Verdict:
        """Grade a typed pipeline against the reference, by what each prints."""
        problem = check_answer(answer)
        if problem:
            return Verdict(False, problem)

        if self.dir is None:
            self.setup({})

        try:
            got = self.execute(answer.strip())
        except Exception as e:
            return Verdict(False, f'could not run that: {e}', error=str(e))

        if got.timed_out:
            return Verdict(False, 'that took too long to run', timed_out=True)
        if not got.ok:
            error = got.first_error()
            return Verdict(False, explain(answer, error) or 'that did not run',
                           error=error)

        want = self.execute(reference)
        if not want.ok:
            raise AdapterError(f'reference pipeline failed: '
                               f'{want.first_error()}')

        return compare(got.out, want.out)

    def check(self, expect: dict, data: dict) -> tuple[bool, str]:
        if not data.get('present'):
            return False, 'the sandbox is gone'
        reference = str(expect.get('reference', ''))
        if not reference:
            return False, 'this challenge names no reference pipeline'
        verdict = self.evaluate(str(data.get('answer', '')), reference)
        return verdict.ok, verdict.detail


def shadowed_alias(expression: str) -> str | None:
    """The first Unix-shadowed alias used as a command, if any.

    Only counted at the start of a pipeline segment, where a bare word is a
    command. `Select-Object Name, ps` is a property list and must not trip
    this, or the hint would fire on correct answers.
    """
    for segment in expression.replace('\n', '|').split('|'):
        head = segment.strip().split(' ', 1)[0].strip().lower()
        if head in UNIX_SHADOWED:
            return head
    return None


def explain(expression: str, error: str) -> str:
    """Say what really went wrong, when the error points somewhere misleading."""
    alias = shadowed_alias(expression)
    if alias and ('/usr/bin' in error or 'invalid option' in error
                  or 'unrecognized option' in error or 'No such file' in error):
        full = UNIX_SHADOWED[alias]
        return (f'{alias!r} ran the system {alias}, not {full}. PowerShell '
                f'drops that alias on Linux and macOS so it does not shadow '
                f'the real binary, so write {full} in full here. On Windows '
                f'the alias exists, which is exactly why this trips people.')
    if 'is not recognized as a name of a cmdlet' in error:
        name = error.split("'")[1] if "'" in error else 'that cmdlet'
        return (f'{name} does not exist in PowerShell on Linux. If it is a '
                f'Windows-only cmdlet, this is content you can read but not '
                f'run here.')
    return error


def normalise(out: str) -> list[str]:
    """Printed output, reduced to what is worth comparing.

    PowerShell pads table columns to the terminal it thinks it has and leaves
    trailing blank lines, neither of which is a difference in the answer.
    Interior blank lines are kept, because a blank line between records is
    sometimes the shape of the output the question asked for.
    """
    lines = [line.rstrip()
             for line in strip_ansi(out).replace('\r\n', '\n').split('\n')]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return lines


def compare(got_out: str, want_out: str) -> Verdict:
    """Compare two printed outputs, naming the first real difference."""
    got, want = normalise(got_out), normalise(want_out)
    if got == want:
        return Verdict(True, 'prints exactly what the answer prints')
    if not got:
        return Verdict(False, 'that printed nothing')

    for i, (a, b) in enumerate(zip(got, want), 1):
        if a != b:
            return Verdict(False,
                           f'line {i} reads {a.strip()[:40]!r}, '
                           f'the answer prints {b.strip()[:40]!r}',
                           missed=[b], over=[a])
    if len(got) > len(want):
        return Verdict(False,
                       f'prints {len(got) - len(want)} line(s) too many, '
                       f'starting {got[len(want)].strip()[:40]!r}',
                       over=got[len(want):])
    return Verdict(False,
                   f'stops {len(want) - len(got)} line(s) early: the answer '
                   f'goes on to print {want[len(got)].strip()[:40]!r}',
                   missed=want[len(got):])
