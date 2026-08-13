"""The tmux adapter: the first place the trainer checks real work.

tmux is the easiest of the four adapters because it was built to be scripted.
`list-panes` and `list-windows` take a format string and print exactly what you
ask for, so observing a session is a subprocess call and a split, with no
terminal scraping anywhere.

**D1 is the constraint that shapes this file.** The trainer may create and
destroy its own sandbox and may read your state, and that is all:

* `setup` creates the scratch session only if it does not already exist, and
  records whether it was the creator.
* `teardown` kills the session **only if setup created it**. If you already had
  a session by that name, it is yours and it survives. This is not a nicety:
  the default scratch name is short and someone will have one.
* `observe` only ever runs `has-session`, `list-panes` and `list-windows`, all
  of which are read-only.

Nothing here raises. A tmux that is missing, wedged, or answering slowly
degrades to self-marked per D18, which is why every call has a timeout and
every failure path returns rather than throws.
"""

from __future__ import annotations

import shutil
import subprocess

from . import Adapter, Observation

TIMEOUT = 5.0


def _describe(data: dict) -> str:
    return (f'{_plural(data.get("panes", 0), "pane")} in '
            f'{_plural(data.get("windows", 0), "window")}')

#: Everything `expect` may assert, so `validate.py` can reject a typo in
#: content rather than silently passing a challenge that checks nothing.
EXPECT_KEYS = frozenset({
    'session_exists', 'min_panes', 'max_panes', 'min_windows',
    'named_windows', 'zoomed',
})


def _run(args: list[str]) -> tuple[int, str]:
    """Run a tmux command. Returns (returncode, stdout). Never raises."""
    try:
        r = subprocess.run(['tmux', *args], capture_output=True, text=True,
                           timeout=TIMEOUT)
        return r.returncode, r.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return 127, ''


class TmuxAdapter(Adapter):
    name = 'tmux'
    requires = ('tmux',)
    description = 'reads your real tmux session'
    expect_keys = EXPECT_KEYS
    return_hint = 'press the prefix (C-b) then d to detach'

    #: Windows tmux names automatically. A window still carrying one of these
    #: has not been named by the user, which is what `named_windows` checks.
    DEFAULT_NAMES = frozenset({'bash', 'zsh', 'fish', 'sh', 'tmux', 'ksh'})

    def __init__(self) -> None:
        super().__init__()
        self.session = 'hone-drill'
        self._created = False
        self._pre_existing = False

    # -- availability ------------------------------------------------------

    def probe(self) -> tuple[bool, str]:
        if not shutil.which('tmux'):
            return False, 'tmux not installed'
        code, out = _run(['-V'])
        if code != 0:
            return False, 'tmux is installed but not answering'
        return True, ''

    # -- lifecycle ---------------------------------------------------------

    def has_session(self, name: str | None = None) -> bool:
        return _run(['has-session', '-t', name or self.session])[0] == 0

    def setup(self, spec: dict) -> None:
        """Create the scratch session, unless the content says not to.

        `create: False` is for challenges where creating the session **is** the
        task. Doing it for the student there would verify our own work.
        """
        self.session = str(spec.get('session') or 'hone-drill')
        self._created = False
        # Recorded before anything is created. A session that was already here
        # is both not ours to destroy (D1) and not something we can verify
        # against: its panes and windows are someone else's work, and counting
        # them would hand out a false pass.
        self._pre_existing = self.has_session()
        if not spec.get('create', False) or self._pre_existing:
            return
        code, _ = _run(['new-session', '-d', '-s', self.session])
        self._created = (code == 0)

    def observe(self) -> Observation:
        """Read the session. Read-only, per D1."""
        if self._pre_existing:
            return Observation(
                False,
                {'session_exists': True, 'session': self.session,
                 'cannot_verify': True, 'panes': 0, 'windows': 0,
                 'window_names': []},
                f'a session named {self.session} was already open before this '
                f'started, so there is no way to tell your work from what was '
                f'already there. Close or rename it for a verified run.')
        if not self.has_session():
            # Carry the name even on the failure path: the message the student
            # sees is built from this data, and "no session named ?" is useless.
            return Observation(False,
                               {'session_exists': False, 'session': self.session,
                                'panes': 0, 'windows': 0, 'window_names': []},
                               f'no session named {self.session}')

        _, panes = _run(['list-panes', '-t', self.session, '-a', '-F',
                         '#{session_name}\t#{window_index}\t#{pane_id}\t'
                         '#{?window_zoomed_flag,zoomed,}'])
        _, windows = _run(['list-windows', '-t', self.session, '-F',
                           '#{window_index}\t#{window_name}\t#{window_panes}'])

        pane_rows = [r.split('\t') for r in panes.splitlines() if r.strip()]
        pane_rows = [r for r in pane_rows if r and r[0] == self.session]
        win_rows = [r.split('\t') for r in windows.splitlines() if r.strip()]

        names = [r[1] for r in win_rows if len(r) > 1]
        data = {
            'session_exists': True,
            'session': self.session,
            'panes': len(pane_rows),
            'windows': len(win_rows),
            'window_names': names,
            'zoomed': any(len(r) > 3 and r[3] == 'zoomed' for r in pane_rows),
            'created_by_trainer': self._created,
            'cannot_verify': False,
        }
        return Observation(True, data, _describe(data))

    def check(self, expect: dict, data: dict) -> tuple[bool, str]:
        return check(expect, data)

    def opens(self, spec: dict) -> str:
        if spec.get('handoff') == 'shell':
            return ('Enter hands you a plain shell, because building the '
                    'session is the task.')
        return (f'Enter drops you into a scratch tmux session called '
                f'{self.session}. It is not your own session and nothing '
                f'you do in it touches your real one.')

    def handoff(self, spec: dict) -> list[str]:
        # Show the task inside the session as it comes up. Best effort: a
        # toast that misses is not worth failing a handover over, and the
        # brief screen said the same thing a moment ago.
        brief = spec.get('brief')
        if brief and self.has_session():
            _run(['display-message', '-t', self.session, str(brief)])
        return handoff_command(spec, self.session)

    def teardown(self) -> None:
        """Destroy only what setup created. Safe to call twice.

        If the session already existed when we arrived, it is the user's and we
        leave it alone. See D1.
        """
        if not self._created:
            return
        self._created = False
        _run(['kill-session', '-t', self.session])


# --------------------------------------------------------------------------
# Expectation checking
# --------------------------------------------------------------------------

def _plural(n: int, word: str) -> str:
    return f'{n} {word}' if n == 1 else f'{n} {word}s'


def check(expect: dict, data: dict) -> tuple[bool, str]:
    """Evaluate a challenge's `expect` against an observation.

    Returns (passed, human-readable detail). The detail is shown to the
    student, so it says what was actually seen rather than just failing: being
    told "2 panes, needs 3" is the difference between a hint and a wall.
    """
    if not expect:
        return bool(data.get('session_exists')), ''

    problems: list[str] = []

    if expect.get('session_exists') and not data.get('session_exists'):
        return False, f'no session named {data.get("session", "?")} exists yet'

    panes = data.get('panes', 0)
    if 'min_panes' in expect and panes < expect['min_panes']:
        problems.append(f'{panes} panes, needs at least {expect["min_panes"]}')
    if 'max_panes' in expect and panes > expect['max_panes']:
        problems.append(f'{panes} panes, expected at most {expect["max_panes"]}')

    windows = data.get('windows', 0)
    if 'min_windows' in expect and windows < expect['min_windows']:
        problems.append(f'{windows} windows, needs at least '
                        f'{expect["min_windows"]}')

    if expect.get('named_windows'):
        unnamed = [n for n in data.get('window_names', [])
                   if n in TmuxAdapter.DEFAULT_NAMES or not n.strip()]
        if unnamed:
            problems.append(f'still using default names: {", ".join(unnamed)}')

    if 'zoomed' in expect and bool(data.get('zoomed')) != bool(expect['zoomed']):
        problems.append('expected a zoomed pane' if expect['zoomed']
                        else 'expected no pane to be zoomed')

    if problems:
        return False, '; '.join(problems)
    return True, _describe(data) if data.get('session_exists') else 'ok'


def handoff_command(spec: dict, session: str) -> list[str]:
    """What to run when the terminal is handed over (D21).

    `attach` drops the student straight into the scratch session, which is the
    contained experience. `shell` hands back a plain shell, which is right when
    the task is to create the session in the first place.
    """
    if spec.get('handoff') == 'shell':
        return []
    return ['tmux', 'attach', '-t', session]
