"""Verification adapters: the capability tier of D18.

An adapter is how the trainer finds out what you actually did. `tmux
list-panes` after you build a layout, an nvim RPC call after you edit a buffer,
`emacsclient --eval` after you refile a heading. That is the whole argument for
this being a terminal application, and it is also the fragile part, which is
why every bit of it lives behind this one boundary.

**D18: this tier is optional and never load-bearing.** A module whose adapter
is missing degrades to self-marked and says so. It does not error, it does not
hide its content, and it does not stop you learning. A stranger with no nvim
installed gets a working trainer.

**D1 constrains what an adapter may do**, and the constraint is not decorative:

* `setup` creates only the adapter's *own* sandbox, named so it is obviously
  ours, and never touches an existing session, file, or config.
* `observe` reads and never mutates.
* `teardown` destroys only what `setup` created, and is safe to call twice.
* Nothing here ever reaches the network.

Phase 0 ships **zero real adapters**, deliberately. This is the interface, the
registry, the degrade path, and a fake for the tests.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from typing import Any, Callable

#: D8's three labels. The UI must always show which one applied, so a
#: self-marked task can never be mistaken for a verified one later.
VERIFIED = 'verified'   # an adapter observed real end state
GRADED = 'graded'       # deterministic in-process check, no external tool
SELF = 'self'           # you did it where we cannot see, and you marked it

LABELS = {
    VERIFIED: 'verified',
    GRADED: 'checked',
    SELF: 'self-marked',
}


class AdapterError(RuntimeError):
    """An adapter failed at runtime. Always caught: it degrades, never crashes."""


@dataclass(frozen=True, slots=True)
class Observation:
    """What an adapter saw. `data` is adapter-specific and content matches on it."""

    ok: bool
    data: dict[str, Any]
    detail: str = ''


class Adapter:
    """Base class. Subclasses override `probe`, `setup`, `observe`, `teardown`.

    Availability is probed once and cached, because the picker shows adapter
    status on the first screen (D16 rule 4) and re-shelling out for every row
    would make the home screen slow for no benefit.
    """

    name = 'base'
    #: Executables that must exist for this adapter to work at all.
    requires: tuple[str, ...] = ()
    #: Shown on the picker and in the degrade message.
    description = ''
    #: Keys this adapter understands in a challenge's `verify.expect`.
    #: `validate.py` rejects anything else, so a typo in content fails the
    #: build instead of surfacing at runtime as a degraded challenge.
    expect_keys: frozenset[str] = frozenset()

    #: How the student gets back to hone from this tool, in their words.
    #: Shown before the handover and carried into the tool itself. Every
    #: adapter must answer this: the way out of nvim is not guessable from
    #: the way out of tmux, and guessing wrong loses the work.
    return_hint = 'finish, and come back'

    def __init__(self) -> None:
        self._available: bool | None = None
        self._reason: str = ''
        self._sandbox: Any = None

    # -- availability ------------------------------------------------------

    def probe(self) -> tuple[bool, str]:
        """Is this adapter usable right now? Returns (ok, reason-if-not)."""
        missing = [b for b in self.requires if not shutil.which(b)]
        if missing:
            return False, f'{", ".join(missing)} not installed'
        return True, ''

    def available(self, recheck: bool = False) -> bool:
        if self._available is None or recheck:
            try:
                self._available, self._reason = self.probe()
            except Exception as e:  # a broken probe must not break the app
                self._available, self._reason = False, f'probe failed: {e}'
        return self._available

    @property
    def reason(self) -> str:
        self.available()
        return self._reason

    # -- lifecycle ---------------------------------------------------------

    def setup(self, spec: dict) -> None:
        """Create our own sandbox only. See D1."""

    def observe(self) -> Observation:
        """Read real state. Must not mutate anything. See D1."""
        return Observation(False, {}, 'adapter does not observe')

    def teardown(self) -> None:
        """Destroy only what setup created. Must be safe to call twice."""

    def check(self, expect: dict, data: dict) -> tuple[bool, str]:
        """Evaluate a challenge's `expect` against an observation.

        Lives on the adapter so the challenge screen never learns what a pane
        or a buffer is. Returns (passed, detail), and the detail is shown to
        the student, so it should say what was actually seen: "2 panes, needs
        3" teaches, "failed" does not.
        """
        return bool(data), ''

    def handoff(self, spec: dict) -> list[str]:
        """Command to run when the terminal is handed over (D21).

        An empty list means hand back a plain shell.
        """
        return []

    def opens(self, spec: dict) -> str:
        """One sentence naming what Enter is about to launch.

        Surprise is the enemy at a handover: a beginner who did not expect
        another program to take the screen reads its arrival as a crash.
        """
        return 'Enter hands the terminal to the real tool.'

    def handoff_cwd(self, spec: dict) -> str | None:
        """Directory to start the handoff in, or None for wherever we are.

        Only the sandbox needs this: its whole point is that you are standing
        inside the tree being verified.
        """
        return None

    # -- convenience -------------------------------------------------------

    def session(self, spec: dict):
        """Context manager pairing setup with a guaranteed teardown."""
        adapter = self

        class _Session:
            def __enter__(self):
                adapter.setup(spec)
                return adapter

            def __exit__(self, *exc):
                try:
                    adapter.teardown()
                except Exception:
                    pass  # teardown failure must never mask the real result
                return False

        return _Session()


class FakeAdapter(Adapter):
    """Test double. Used by `test.py` to play every challenge with no real tool.

    It also enforces the D1 contract in tests: `observe` refuses to run before
    `setup`, and `teardown` is asserted idempotent, so a real adapter that
    breaks either rule fails the shared contract test rather than misbehaving
    quietly on someone's machine.
    """

    name = 'fake'
    description = 'test double'

    def __init__(self, ok: bool = True, data: dict | None = None,
                 available: bool = True) -> None:
        super().__init__()
        self._force_available = available
        self._ok = ok
        self._data = data or {}
        self.setup_calls = 0
        self.teardown_calls = 0
        self.observed = 0

    def probe(self) -> tuple[bool, str]:
        return (True, '') if self._force_available else (False, 'fake unavailable')

    def setup(self, spec: dict) -> None:
        self.setup_calls += 1
        self._sandbox = dict(spec)

    def observe(self) -> Observation:
        if self._sandbox is None:
            raise AdapterError('observe() called before setup()')
        self.observed += 1
        return Observation(self._ok, dict(self._data), 'fake observation')

    def check(self, expect: dict, data: dict) -> tuple[bool, str]:
        """Honour the `ok` flag rather than the base's truthiness default.

        The base returns `bool(data)`, which is right for "did I see anything"
        but makes a fake unable to express a failed verification, and a test
        that cannot fail is not a test.
        """
        return self._ok, 'fake check'

    def teardown(self) -> None:
        self.teardown_calls += 1
        self._sandbox = None


# --------------------------------------------------------------------------
# Registry
# --------------------------------------------------------------------------

_REGISTRY: dict[str, Callable[[], Adapter]] = {}
_INSTANCES: dict[str, Adapter] = {}
_builtins_loaded = False


def load_builtin() -> None:
    """Register the adapters that ship with the app.

    Lazy and idempotent, so nothing has to remember to call it and there is no
    import cycle: by the time this runs, this module is fully loaded and the
    adapter modules can import from it normally.
    """
    global _builtins_loaded
    if _builtins_loaded:
        return
    _builtins_loaded = True
    for module_name, class_name, key in (('tmux', 'TmuxAdapter', 'tmux'),
                                         ('nvim', 'NvimAdapter', 'nvim'),
                                         ('emacs', 'EmacsAdapter', 'emacs'),
                                         ('sandbox', 'SandboxAdapter', 'sandbox'),
                                         ('git', 'GitAdapter', 'git'),
                                         ('pcap', 'PcapAdapter', 'pcap'),
                                         ('pwsh', 'PwshAdapter', 'pwsh')):
        try:
            mod = __import__(f'{__name__}.{module_name}', fromlist=[class_name])
            register(key, getattr(mod, class_name))
        except (ImportError, AttributeError):
            pass  # a missing adapter degrades per D18, it does not crash


def register(name: str, factory: Callable[[], Adapter]) -> None:
    _REGISTRY[name] = factory
    _INSTANCES.pop(name, None)


def get(name: str | None) -> Adapter | None:
    """Return the shared instance for `name`, or None if nothing is registered."""
    load_builtin()
    if not name:
        return None
    if name not in _INSTANCES:
        factory = _REGISTRY.get(name)
        if factory is None:
            return None
        _INSTANCES[name] = factory()
    return _INSTANCES[name]


def registered() -> list[str]:
    load_builtin()
    return sorted(_REGISTRY)


def reset(builtins: bool = False) -> None:
    """Drop every instance and registration. Tests only.

    `builtins=True` re-registers the shipped adapters afterwards, for tests
    that want a clean slate but still need tmux present.
    """
    global _builtins_loaded
    _REGISTRY.clear()
    _INSTANCES.clear()
    # Suppress auto-registration rather than merely clearing, otherwise the
    # next get() quietly puts the builtins back and "no adapters installed"
    # becomes untestable.
    _builtins_loaded = True
    if builtins:
        _builtins_loaded = False
        load_builtin()


def status(name: str | None) -> tuple[bool, str]:
    """(available, reason) for the picker. An unregistered adapter is 'not built yet'."""
    load_builtin()
    if not name:
        return False, 'content only'
    ad = get(name)
    if ad is None:
        return False, f'{name} adapter not built yet'
    return (True, '') if ad.available() else (False, ad.reason)


# --------------------------------------------------------------------------
# Checking mode (D26)
# --------------------------------------------------------------------------

#: The two modes. `CHECKED` is what the app has always done: anything that can
#: be verified is. `READ` turns the whole capability tier off by choice rather
#: than by absence, so nothing is launched, no sandbox is written and no
#: subprocess runs, anywhere.
CHECKED, READ = 'checked', 'read'
MODES = (CHECKED, READ)

MODE_BLURB = {
    CHECKED: 'runs the real tools and checks your work',
    READ: 'lessons, drills and quizzes only, nothing is launched',
}

_mode = CHECKED


def set_mode(name: str) -> str:
    """Set the checking mode. Unknown names fall back to checked."""
    global _mode
    _mode = name if name in MODES else CHECKED
    return _mode


def mode() -> str:
    return _mode


def read_only() -> bool:
    return _mode == READ


# --------------------------------------------------------------------------
# Degrade path
# --------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class Plan:
    """How a challenge will be checked, decided before it starts.

    D16 rule 4 requires this be known up front rather than discovered at the
    moment of grading, so the student is never promised verification and then
    quietly handed an honour-system checkbox.
    """

    kind: str                 # VERIFIED | GRADED | SELF
    adapter: Adapter | None
    reason: str = ''

    @property
    def label(self) -> str:
        return LABELS[self.kind]

    @property
    def degraded(self) -> bool:
        return self.kind == SELF and bool(self.reason)


def plan_for(challenge: dict) -> Plan:
    """Decide how one challenge gets checked, given what is installed.

    A challenge declaring an adapter that is missing falls back to its declared
    `fallback` (default self-marked) and carries the reason, so the UI can say
    'nvim not installed, so this one is on your honour' rather than pretending.
    """
    spec = challenge.get('verify') or {}
    kind = spec.get('kind')

    if not kind:
        return Plan(SELF, None, '')          # authored as self-marked, not degraded
    if kind in (GRADED, SELF):
        return Plan(kind, None, '')

    # D26: the student asked for nothing to be launched. This is the same
    # degrade path a missing tool takes, and it carries a reason for the same
    # reason: the UI must never show an honour-system tick where it promised
    # verification, whether the cause is an absent tool or a chosen mode.
    if read_only():
        fallback = challenge.get('fallback', SELF)
        return Plan(fallback if fallback in (GRADED, SELF) else SELF, None,
                    'read and drill only mode is on')

    # The fallback names a *label*, and a wrong label is a D8 violation
    # waiting to be recorded, so anything unrecognised collapses to SELF.
    fallback = challenge.get('fallback', SELF)
    if fallback not in (GRADED, SELF):
        fallback = SELF

    ad = get(kind)
    if ad is None:
        return Plan(fallback, None, f'{kind} adapter not built yet')
    if not ad.available():
        return Plan(fallback, None, ad.reason)
    return Plan(VERIFIED, ad, '')
