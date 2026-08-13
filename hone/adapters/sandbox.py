"""The sandbox adapter: a directory you work in, that the trainer reads back.

The most reusable of the adapters, and the only one that requires nothing to be
installed, because the tool being verified is the filesystem. The trainer
builds a small tree, hands you a real shell sitting in it, and afterwards walks
the tree and compares it to what the challenge asked for.

**Why this is worth having even though it looks simple.** Almost everything in
Linux Basics and bash produces a filesystem result: a file created, renamed,
made executable, redirected into, symlinked. Verifying that is exactly reading
a directory, so one adapter covers two modules and most of a third.

**D1.** The tree is created under a temp directory and removed afterwards. The
shell you are handed starts there, and nothing outside it is written or read.
A challenge that wanted to touch your real home would not be verifiable here,
which is a feature rather than a limitation.

**Which shell.** By default you get your own, because Linux Basics is about
commands that behave identically everywhere and using your real shell is more
honest. A challenge can ask for `bash` specifically, and the bash module does,
because that module is about bash and the author's login shell is fish.
"""

from __future__ import annotations

import os
import shutil
import stat
import tempfile
from pathlib import Path

from . import Adapter, Observation


def _plural(n: int, word: str) -> str:
    return f'{n} {word}' if n == 1 else f'{n} {word}s'


def _describe(files, dirs) -> str:
    d = _plural(len(dirs), "directory").replace("directorys", "directories")
    return f'{_plural(len(files), "file")}, {d}'

EXPECT_KEYS = frozenset({
    'exists', 'missing', 'is_dir', 'is_file',
    'file_equals', 'file_contains', 'file_lacks',
    'mode', 'is_symlink', 'executable',
})

MAX_READ = 64 * 1024


class SandboxAdapter(Adapter):
    name = 'sandbox'
    requires = ()          # a directory needs nothing installed
    description = 'reads the files you actually created'
    expect_keys = EXPECT_KEYS
    return_hint = 'type exit and press Enter'

    def opens(self, spec: dict) -> str:
        # Never say "empty" when the challenge seeded a tree: the next block
        # on the brief lists what is in it, and the two contradicting each
        # other is worse than saying nothing.
        which = 'bash' if spec.get('shell') == 'bash' else 'your shell'
        kind = 'a throwaway directory' if spec.get('tree') else \
               'an empty throwaway directory'
        return (f'Enter hands you {which}, already sitting in {kind}. '
                f'Nothing outside it is touched.')

    def __init__(self) -> None:
        super().__init__()
        self.dir: Path | None = None
        self.shell: str | None = None

    def probe(self) -> tuple[bool, str]:
        return True, ''

    # -- lifecycle ---------------------------------------------------------

    def setup(self, spec: dict) -> None:
        """Build the starting tree.

        `tree` maps a relative path to what should be there. A trailing slash
        or a None value means a directory; a string means file content; a dict
        may carry `content`, `mode` or `symlink`.
        """
        self.teardown()
        self.dir = Path(tempfile.mkdtemp(prefix='hone-box-'))
        self.shell = spec.get('shell')

        for rel, what in (spec.get('tree') or {}).items():
            target = self._resolve(rel)
            if target is None:
                continue
            if rel.endswith('/') or what is None:
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(what, dict):
                if what.get('symlink'):
                    target.symlink_to(str(what['symlink']))
                    continue
                target.write_text(str(what.get('content', '')), encoding='utf-8')
                if what.get('mode'):
                    target.chmod(int(str(what['mode']), 8))
            else:
                target.write_text(str(what), encoding='utf-8')

    def _resolve(self, rel: str) -> Path | None:
        """Join a content-supplied path, refusing anything that escapes.

        Content is authored by hand and a stray `../` would write outside the
        sandbox, which D1 forbids outright. Refusing here means a mistake in a
        content file cannot become a mistake on someone's disk.
        """
        if self.dir is None:
            return None
        candidate = (self.dir / rel.rstrip('/')).resolve()
        try:
            candidate.relative_to(self.dir.resolve())
        except ValueError:
            return None
        return candidate

    def handoff(self, spec: dict) -> list[str]:
        shell = self.shell or spec.get('shell')
        if shell == 'bash':
            return ['bash', '--norc', '-i']
        return [os.environ.get('SHELL', '/bin/sh')]

    def handoff_cwd(self, spec: dict) -> str | None:
        return str(self.dir) if self.dir else None

    def observe(self) -> Observation:
        """Walk the tree. Read-only, per D1."""
        if self.dir is None or not self.dir.is_dir():
            return Observation(False, {'present': False}, 'the sandbox is gone')

        files: dict[str, str] = {}
        dirs: list[str] = []
        modes: dict[str, str] = {}
        symlinks: dict[str, str] = {}
        paths: list[str] = []

        for root, dirnames, filenames in os.walk(self.dir):
            base = Path(root)
            for name in list(dirnames) + filenames:
                full = base / name
                rel = str(full.relative_to(self.dir))
                paths.append(rel)
                try:
                    st = full.lstat()
                    modes[rel] = oct(stat.S_IMODE(st.st_mode))[2:].rjust(3, '0')
                    if stat.S_ISLNK(st.st_mode):
                        symlinks[rel] = os.readlink(full)
                        continue
                    if full.is_dir():
                        dirs.append(rel)
                        continue
                    if st.st_size <= MAX_READ:
                        files[rel] = full.read_text(encoding='utf-8',
                                                    errors='replace')
                    else:
                        files[rel] = ''
                except OSError:
                    continue

        data = {
            'present': True, 'paths': sorted(paths), 'files': files,
            'dirs': sorted(dirs), 'modes': modes, 'symlinks': symlinks,
        }
        return Observation(True, data, _describe(files, dirs))

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

def _as_list(v) -> list[str]:
    if v is None:
        return []
    return [str(v)] if isinstance(v, str) else [str(x) for x in v]


def check(expect: dict, data: dict) -> tuple[bool, str]:
    """Evaluate a challenge's `expect` against the observed tree.

    Every message names the path and what was actually there, because "wrong"
    is not feedback and "notes/a.txt is missing" is.
    """
    if not data.get('present'):
        return False, 'the sandbox is gone'

    paths = set(data.get('paths', []))
    files = data.get('files', {})
    dirs = set(data.get('dirs', []))
    modes = data.get('modes', {})
    symlinks = data.get('symlinks', {})

    for p in _as_list(expect.get('exists')):
        if p not in paths:
            return False, f'{p} does not exist yet'
    for p in _as_list(expect.get('missing')):
        if p in paths:
            return False, f'{p} is still there'
    for p in _as_list(expect.get('is_dir')):
        if p not in dirs:
            return False, (f'{p} is not a directory'
                           if p in paths else f'{p} does not exist yet')
    for p in _as_list(expect.get('is_file')):
        if p not in files:
            return False, (f'{p} is not a regular file'
                           if p in paths else f'{p} does not exist yet')

    for p, want in (expect.get('file_equals') or {}).items():
        if p not in files:
            return False, f'{p} does not exist yet'
        got = files[p].rstrip('\n')
        if got != str(want).rstrip('\n'):
            return False, f'{p} contains {got[:60]!r}, expected {str(want)[:60]!r}'

    for p, needles in (expect.get('file_contains') or {}).items():
        if p not in files:
            return False, f'{p} does not exist yet'
        for needle in _as_list(needles):
            if needle not in files[p]:
                return False, f'{p} does not contain {needle!r}'

    for p, needles in (expect.get('file_lacks') or {}).items():
        for needle in _as_list(needles):
            if p in files and needle in files[p]:
                return False, f'{p} still contains {needle!r}'

    for p, want in (expect.get('mode') or {}).items():
        got = modes.get(p)
        if got is None:
            return False, f'{p} does not exist yet'
        if got.lstrip('0') != str(want).lstrip('0'):
            return False, f'{p} is mode {got}, expected {want}'

    for p in _as_list(expect.get('executable')):
        got = modes.get(p)
        if got is None:
            return False, f'{p} does not exist yet'
        if not any(int(c) & 1 for c in got):
            return False, f'{p} is mode {got}, which is not executable'

    for p, target in (expect.get('is_symlink') or {}).items():
        if p not in symlinks:
            return False, f'{p} is not a symbolic link'
        if target and symlinks[p] != str(target):
            return False, (f'{p} points at {symlinks[p]!r}, '
                           f'expected {str(target)!r}')

    return True, _describe(files, dirs) + ', as asked'
