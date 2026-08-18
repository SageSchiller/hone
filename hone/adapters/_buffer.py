"""Shared machinery for adapters that verify an editor by reading a buffer.

nvim and Emacs verify the same way and differ only in two places: how you
launch them, and how you ask them to dump their buffer on the way out. That
shape will repeat again for org-mode, so the common part lives here and each
editor supplies the two pieces it actually owns.

**The pattern.** Seed a scratch file in a sandbox directory, hand the terminal
to the real editor on that file, and register a leave hook that writes the
buffer and the final cursor position into the sandbox. Then read all three
back: the file on disk, the buffer at exit, and the cursor.

**Why the buffer dump is worth the trouble.** Reading only the saved file
cannot tell "made the edit and forgot to save" from "never made the edit", and
those deserve different feedback. Every editor this applies to has a hook that
fires on quit, so the distinction is cheap and it is the single most useful
thing the check can say.

**D1.** Everything written lives inside a directory the adapter created and
removes. The editor runs with the user's own configuration, deliberately: a
trainer that launches with no config grades an editor nobody has, and the
remaps in your config are part of your reality rather than noise.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from . import Adapter, Observation

SCRATCH = 'scratch.txt'
BUFFER_DUMP = '.buffer'
CURSOR_DUMP = '.cursor'

EXPECT_KEYS = frozenset({
    'lines', 'contains', 'not_contains', 'line_count',
    'cursor_line', 'cursor_col', 'saved',
})


class BufferAdapter(Adapter):
    """Base for editors verified by reading what you left in the buffer."""

    expect_keys = EXPECT_KEYS
    #: Name of the scratch file. Some content wants a real extension so the
    #: editor turns on the right mode.
    scratch_name = SCRATCH

    def __init__(self) -> None:
        super().__init__()
        self.dir: Path | None = None

    # -- to implement ------------------------------------------------------

    #: Name of the editor as the student would say it.
    editor = 'the editor'

    def opens(self, spec: dict) -> str:
        return (f'Enter opens {self.editor} on a scratch file called '
                f'{self.scratch_name}, in a throwaway directory.')

    def launch(self, scratch: Path, buf: Path, cur: Path,
               brief: str = '', steps: list[str] | None = None) -> list[str]:
        """argv that opens `scratch` and dumps buffer and cursor on exit.

        `brief` is one line to keep in front of the student for the whole
        session: the task, and how to get back out. Each editor displays it
        its own way.

        `steps` is the same information at length, for editors that can put it
        in a second window beside the work. One line is the safety net; the
        list is what you actually follow in guided mode, and an editor is the
        one kind of tool that can show it without the student typing anything.

        **Convention:** the leave hook must be `argv[-2]` and the file
        `argv[-1]`. Editors put their flags in different places (`-c` for nvim,
        `--eval` for Emacs), so indexing from the front means every caller has
        to know which editor it is holding. Indexing from the back does not,
        which is what lets `test.py` replay a solution against either.
        """
        raise NotImplementedError

    # -- lifecycle ---------------------------------------------------------

    @property
    def scratch(self) -> Path | None:
        return self.dir / self.scratch_name if self.dir else None

    def setup(self, spec: dict) -> None:
        self.teardown()
        self.dir = Path(tempfile.mkdtemp(prefix='hone-'))
        # Reset to the class default first: a name set by one challenge would
        # otherwise leak into the next one on the shared adapter instance, and
        # a .org scratch handed to a plain-text challenge turns on a major mode
        # nobody asked for.
        self.scratch_name = type(self).scratch_name
        if spec.get('scratch_name'):
            self.scratch_name = str(spec['scratch_name'])
        start = spec.get('start') or ['']
        if isinstance(start, str):
            start = start.split('\n')
        self.scratch.write_text('\n'.join(str(l) for l in start) + '\n',
                                encoding='utf-8')

    def handoff(self, spec: dict) -> list[str]:
        if self.dir is None:
            return []
        return self.launch(self.scratch, self.dir / BUFFER_DUMP,
                           self.dir / CURSOR_DUMP, str(spec.get('brief') or ''),
                           list(spec.get('steps') or ()))

    def observe(self) -> Observation:
        """Read the sandbox back. Read-only, per D1."""
        if self.dir is None or not self.scratch.exists():
            return Observation(False, {'opened': False},
                               'the scratch file is missing')

        saved = self.scratch.read_text(encoding='utf-8').rstrip('\n').split('\n')
        buf_path = self.dir / BUFFER_DUMP
        opened = buf_path.exists()
        buffer = (buf_path.read_text(encoding='utf-8').rstrip('\n').split('\n')
                  if opened else list(saved))

        line = col = 0
        cur_path = self.dir / CURSOR_DUMP
        if cur_path.exists():
            parts = cur_path.read_text(encoding='utf-8').split()
            if len(parts) == 2 and all(p.lstrip('-').isdigit() for p in parts):
                line, col = int(parts[0]), int(parts[1])

        data = {
            'opened': opened,
            'saved_lines': saved,
            'buffer_lines': buffer,
            'saved': saved == buffer,
            'cursor_line': line,
            'cursor_col': col,
        }
        return Observation(opened, data,
                           f'{len(buffer)} lines, cursor {line}:{col}')

    def teardown(self) -> None:
        if self.dir is None:
            return
        shutil.rmtree(self.dir, ignore_errors=True)
        self.dir = None

    def check(self, expect: dict, data: dict) -> tuple[bool, str]:
        return check(expect, data)


# --------------------------------------------------------------------------
# Expectation checking
# --------------------------------------------------------------------------

def check(expect: dict, data: dict) -> tuple[bool, str]:
    """Evaluate a challenge's `expect` against an observation.

    The order of the branches is the teaching. "you never opened it" and "you
    made the edit but never saved it" are different mistakes from "the edit is
    wrong", and each gets its own sentence.
    """
    if not data.get('opened'):
        return False, 'the editor never opened the scratch file'

    buffer = data.get('buffer_lines', [])
    saved = data.get('saved_lines', [])

    if 'lines' in expect:
        want = [str(l) for l in expect['lines']]
        if buffer != want:
            return False, _diff(want, buffer)
        if expect.get('saved', True) and saved != want:
            # The valuable case: the edit was right and the write was missed.
            return False, ('the edit is right, but you left without saving it')
    elif expect.get('saved') and saved != buffer:
        return False, 'you left without saving'

    text = '\n'.join(buffer)
    for needle in _as_list(expect.get('contains')):
        if needle not in text:
            return False, f'expected to find {needle!r} in the buffer'
    for needle in _as_list(expect.get('not_contains')):
        if needle in text:
            return False, f'{needle!r} is still there'

    if 'line_count' in expect and len(buffer) != expect['line_count']:
        return False, f'{len(buffer)} lines, expected {expect["line_count"]}'

    for key, label in (('cursor_line', 'line'), ('cursor_col', 'column')):
        if key in expect and data.get(key) != expect[key]:
            return False, (f'cursor ended on {label} {data.get(key)}, '
                           f'expected {expect[key]}')

    n = len(buffer)
    return True, f'{n} line{"" if n == 1 else "s"}, as asked'


def _as_list(v) -> list[str]:
    if v is None:
        return []
    return [str(v)] if isinstance(v, str) else [str(x) for x in v]


def _diff(want: list[str], got: list[str]) -> str:
    """Name the first line that differs, rather than dumping both buffers."""
    for i, (w, g) in enumerate(zip(want, got), 1):
        if w != g:
            return f'line {i} is {g!r}, expected {w!r}'
    if len(got) < len(want):
        return (f'{len(got)} lines, expected {len(want)}: '
                f'line {len(got) + 1} is missing')
    return (f'{len(got)} lines, expected {len(want)}: '
            f'line {len(want) + 1} is {got[len(want)]!r} and should not be there')
