"""The git adapter: a scratch repository, read back through git itself.

git is the best-verified module in the roster, and the reason is that almost
nothing about git is hidden. Every question a challenge wants to ask has a
plumbing command that answers it exactly: which branch, how many commits, what
is staged, is the tree clean, where does HEAD point.

Built on the sandbox adapter, because a repository **is** a directory and every
file-level check already works. This adds the part a directory cannot show you:
the commit graph and the index.

**Determinism matters more here than elsewhere.** A challenge that starts from
"whatever your git config says" is not reproducible, so the scratch repo is
initialised with an explicit default branch and a local identity. Nothing is
read from or written to your global configuration, which is D1 anyway.
"""

from __future__ import annotations

import shutil
import subprocess

from . import Observation
from .sandbox import SandboxAdapter, check as sandbox_check

TIMEOUT = 15.0

EXPECT_KEYS = frozenset({
    # inherited from the sandbox
    'exists', 'missing', 'is_dir', 'is_file',
    'file_equals', 'file_contains', 'file_lacks',
    'mode', 'is_symlink', 'executable',
    # git's own
    'branch', 'branches', 'commit_count', 'min_commits', 'head_subject',
    'subjects_contain', 'subjects_lack', 'clean', 'staged', 'untracked',
    'tags', 'detached',
})

#: Set locally on the scratch repo so commits work regardless of, and without
#: touching, the user's global configuration.
IDENTITY = ('-c', 'user.email=hone@example.invalid',
            '-c', 'user.name=hone')

#: Applied to every git call in the sandbox. The user's global config must
#: not leak into grading: a global commit hook can fail the setup history, a
#: global gpgsign can hang a commit waiting for a key, and a global excludes
#: file can hide a student's untracked file from `status` and flunk them for
#: work they did. The repo's own .gitignore still applies, which is the part
#: challenges legitimately teach.
NEUTRAL = ('-c', 'core.hooksPath=/dev/null',
           '-c', 'commit.gpgsign=false',
           '-c', 'tag.gpgsign=false',
           '-c', 'core.excludesFile=/dev/null')


class GitAdapter(SandboxAdapter):
    name = 'git'
    requires = ('git',)
    description = 'reads a scratch repository'
    expect_keys = EXPECT_KEYS

    def opens(self, spec: dict) -> str:
        return ('Enter hands you a shell inside a scratch git repository. '
                'Your own repositories and your global git config are not '
                'touched.')

    # -- running git -------------------------------------------------------

    def _git(self, *args: str, identity: bool = False) -> tuple[int, str]:
        """Run git inside the sandbox. Never raises."""
        if self.dir is None:
            return 127, ''
        cmd = ['git', *NEUTRAL, *(IDENTITY if identity else ()), *args]
        try:
            r = subprocess.run(cmd, cwd=self.dir, capture_output=True,
                               text=True, timeout=TIMEOUT)
        except (OSError, subprocess.SubprocessError):
            return 127, ''
        return r.returncode, r.stdout.rstrip('\n')

    # -- lifecycle ---------------------------------------------------------

    def setup(self, spec: dict) -> None:
        """Create the tree, then make it a repo with a known history.

        `commits` is a list of `{message, tree}` applied in order, so a
        challenge can start from a history rather than from nothing.
        """
        super().setup(spec)
        branch = str(spec.get('branch') or 'main')
        self._git('init', '-q', '-b', branch, '.')

        for commit in (spec.get('commits') or ()):
            for rel, content in (commit.get('tree') or {}).items():
                target = self._resolve(rel)
                if target is None:
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(str(content), encoding='utf-8')
            self._git('add', '-A')
            self._git('commit', '-q', '--allow-empty',
                      '-m', str(commit.get('message', 'commit')), identity=True)

        for name in (spec.get('extra_branches') or ()):
            self._git('branch', str(name))

    def probe(self) -> tuple[bool, str]:
        if not shutil.which('git'):
            return False, 'git not installed'
        return True, ''

    # -- observing ---------------------------------------------------------

    def observe(self) -> Observation:
        base = super().observe()
        data = dict(base.data)
        if not data.get('present'):
            return Observation(False, data, base.detail)

        # Files inside .git are the repository's own business, not the
        # student's work, and leaving them in makes every file assertion
        # unreadable.
        for key in ('paths', 'dirs'):
            data[key] = [p for p in data.get(key, [])
                         if p != '.git' and not p.startswith('.git/')]
        for key in ('files', 'modes', 'symlinks'):
            data[key] = {k: v for k, v in data.get(key, {}).items()
                         if k != '.git' and not k.startswith('.git/')}

        code, _ = self._git('rev-parse', '--git-dir')
        if code != 0:
            data['repo'] = False
            return Observation(False, data, 'this is not a git repository')
        data['repo'] = True

        _, branch = self._git('branch', '--show-current')
        _, all_branches = self._git('for-each-ref', '--format=%(refname:short)',
                                    'refs/heads')
        _, subjects = self._git('log', '--format=%s')
        _, tags = self._git('tag')
        _, porcelain = self._git('status', '--porcelain=v1')

        staged, modified, untracked = [], [], []
        for line in porcelain.splitlines():
            if len(line) < 4:
                continue
            x, y, path = line[0], line[1], line[3:].strip()
            if x == '?' and y == '?':
                untracked.append(path)
                continue
            if x != ' ':
                staged.append(path)
            if y != ' ':
                modified.append(path)

        subject_list = [s for s in subjects.splitlines() if s]
        data.update({
            'branch': branch,
            'detached': branch == '',
            'branches': sorted(b for b in all_branches.splitlines() if b),
            'subjects': subject_list,
            'head_subject': subject_list[0] if subject_list else '',
            'commit_count': len(subject_list),
            'tags': sorted(t for t in tags.splitlines() if t),
            'staged': sorted(staged),
            'modified': sorted(modified),
            'untracked': sorted(untracked),
            'clean': porcelain.strip() == '',
        })
        where = branch or 'detached HEAD'
        n = data['commit_count']
        return Observation(True, data,
                           f'{n} commit{"" if n == 1 else "s"} on {where}')

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
    """Evaluate a challenge's `expect`. Git assertions first, then files."""
    if not data.get('present'):
        return False, 'the sandbox is gone'
    if not data.get('repo'):
        return False, 'this is not a git repository yet'

    if 'branch' in expect:
        got = data.get('branch') or '(detached)'
        if got != expect['branch']:
            return False, f'you are on {got}, expected {expect["branch"]}'

    for name in _as_list(expect.get('branches')):
        if name not in data.get('branches', []):
            have = ', '.join(data.get('branches', [])) or 'none'
            return False, f'there is no branch called {name}; you have {have}'

    if 'commit_count' in expect and data.get('commit_count') != expect['commit_count']:
        return False, (f'{data.get("commit_count")} commits, expected '
                       f'{expect["commit_count"]}')
    if 'min_commits' in expect and data.get('commit_count', 0) < expect['min_commits']:
        return False, (f'{data.get("commit_count")} commits, expected at least '
                       f'{expect["min_commits"]}')

    if 'head_subject' in expect and data.get('head_subject') != expect['head_subject']:
        return False, (f'the newest commit is {data.get("head_subject")!r}, '
                       f'expected {expect["head_subject"]!r}')

    subjects = data.get('subjects', [])
    for want in _as_list(expect.get('subjects_contain')):
        if not any(want in s for s in subjects):
            return False, f'no commit message mentions {want!r}'
    for unwanted in _as_list(expect.get('subjects_lack')):
        if any(unwanted in s for s in subjects):
            return False, f'a commit message still mentions {unwanted!r}'

    if 'clean' in expect and bool(data.get('clean')) != bool(expect['clean']):
        if expect['clean']:
            leftover = (data.get('staged') or data.get('modified')
                        or data.get('untracked'))
            return False, (f'the working tree is not clean: '
                           f'{", ".join(leftover[:3])}')
        return False, 'the working tree is clean, expected changes'

    for path in _as_list(expect.get('staged')):
        if path not in data.get('staged', []):
            return False, f'{path} is not staged'
    for path in _as_list(expect.get('untracked')):
        if path not in data.get('untracked', []):
            return False, f'{path} is not untracked'
    for name in _as_list(expect.get('tags')):
        if name not in data.get('tags', []):
            return False, f'there is no tag called {name}'

    if 'detached' in expect and bool(data.get('detached')) != bool(expect['detached']):
        return False, ('HEAD is not detached' if expect['detached']
                       else f'HEAD is detached, expected a branch')

    # Anything left is a file-level assertion the sandbox already understands.
    rest = {k: v for k, v in expect.items()
            if k not in {'branch', 'branches', 'commit_count', 'min_commits',
                         'head_subject', 'subjects_contain', 'subjects_lack',
                         'clean', 'staged', 'untracked', 'tags', 'detached'}}
    if rest:
        ok, detail = sandbox_check(rest, data)
        if not ok:
            return False, detail

    n = data.get('commit_count', 0)
    where = data.get('branch') or 'detached HEAD'
    return True, f'{n} commit{"" if n == 1 else "s"} on {where}, as asked'
