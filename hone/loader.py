"""Module discovery, per D3 and D4.

Content is organised by tool (D3), so a module is a tool and lives in one file
under `hone/content/`. Discovery is additive: drop in a file that defines
`MODULE` and it appears. Nothing lists the modules by hand, which is what makes
the per-tool exports of D4a nearly free, since a build that ships fewer content
files simply finds fewer modules.

Loading is tolerant and reporting. A content file that fails to import does not
take the app down: it is recorded as a load error the UI and `validate.py` can
show. During Phase 0 there is no content at all, and a registry of zero modules
is a valid state that the home screen must handle rather than a failure.
"""

from __future__ import annotations

import importlib
import pkgutil
from dataclasses import dataclass, field
from typing import Any

CONTENT_PACKAGE = 'hone.content'

#: Every kind of item a module may carry. A module needs none of them: D5 says
#: engines are opt-in per module, so a drill deck with no walkthrough is valid.
KINDS = ('lessons', 'challenges', 'drills', 'quiz')

# Re-exported for existing importers; defined in config (see note there).
from .config import REVERSE_PREFIX  # noqa: E402


@dataclass(frozen=True, slots=True)
class Module:
    """One tool's content, normalised so screens never see a raw dict."""

    id: str
    title: str
    blurb: str = ''
    #: Heading this tool sits under on the picker. Fifteen names in one list
    #: is a wall; five short lists is a menu you can scan.
    group: str = 'Other'
    #: One line naming the world a drill assumes: which tool, which mode,
    #: what is on the screen. Shown above every drill prompt in this module.
    context: str = ''
    #: Binaries this module's content is about. Used to tell a student how to
    #: install what they are missing, which matters most for the modules with
    #: no adapter: they degrade silently to "content only" otherwise.
    needs: tuple[str, ...] = ()
    prereqs: tuple[str, ...] = ()
    provides: tuple[str, ...] = ()
    adapter: str | None = None
    estimate: str = ''
    order: int = 1000
    lessons: tuple[dict, ...] = ()
    challenges: tuple[dict, ...] = ()
    drills: tuple[dict, ...] = ()
    quiz: tuple[dict, ...] = ()
    source: str = ''
    #: Cache for generated recognition questions. Set once, lazily.
    _reverse: tuple | None = None

    def items(self, kind: str) -> tuple[dict, ...]:
        return getattr(self, kind)

    def totals(self) -> dict[str, int]:
        return {kind: len(self.items(kind)) for kind in KINDS}

    def has(self, kind: str) -> bool:
        return bool(self.items(kind))

    def item(self, kind: str, item_id: str) -> dict | None:
        for it in self.items(kind):
            if it.get('id') == item_id:
                return it
        if kind == 'quiz' and item_id.startswith(REVERSE_PREFIX):
            for it in self.reverse_quiz():
                if it['id'] == item_id:
                    return it
        return None

    def reverse_quiz(self) -> tuple[dict, ...]:
        """Recognition questions generated from this module's own drills.

        A drill asks "how do you do X" and tests production. Turning it around
        to "what does this do" tests recognition, which is a genuinely
        different skill and is free: the prompts of the other drills are
        already a pool of plausible distractors written by the same hand.

        Only generated where there are enough drills for the distractors not
        to be obvious, and only from drills that carry a real prompt.
        """
        if self._reverse is not None:
            return self._reverse

        usable = [d for d in self.drills
                  if d.get('prompt') and (d.get('keys') or d.get('answer'))]
        if len(usable) < 4:
            object.__setattr__(self, '_reverse', ())
            return ()

        def shown(d: dict) -> str:
            if d.get('type') in ('command', 'regex'):
                return str(d.get('answer', ''))
            return ' '.join(str(k) for k in (d.get('keys') or ()))

        out = []
        for i, d in enumerate(usable):
            others, step = [], 1
            # Walk forward until three *distinct* prompts are found: two
            # drills may legitimately share a prompt shape, and a distractor
            # identical to the answer would make the question unanswerable.
            while len(others) < 3 and step < len(usable):
                cand = usable[(i + step) % len(usable)]
                if cand['prompt'] != d['prompt'] and \
                        all(cand['prompt'] != o['prompt'] for o in others):
                    others.append(cand)
                step += 1
            if len(others) < 3:
                continue
            out.append({
                'id': f'{REVERSE_PREFIX}{d["id"]}',
                'type': 'mcq',
                'prompt': f'What does  {shown(d)}  do?',
                'answer': str(d['prompt']),
                'distractors': [str(o['prompt']) for o in others],
                'teach': str(d.get('teach') or ''),
                'reverse_of': d['id'],
            })
        object.__setattr__(self, '_reverse', tuple(out))
        return self._reverse

    @property
    def is_drill_deck(self) -> bool:
        """True when this module deliberately has no walkthrough.

        The Walkthrough view still renders for it, per D16 rule 1: a missing
        view would read as a bug, so it says what it is instead.
        """
        return not self.has('lessons') and self.has('drills')


@dataclass(frozen=True, slots=True)
class LoadError:
    name: str
    message: str


@dataclass
class Registry:
    modules: list[Module] = field(default_factory=list)
    errors: list[LoadError] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.modules)

    def __iter__(self):
        return iter(self.modules)

    def get(self, module_id: str) -> Module | None:
        for m in self.modules:
            if m.id == module_id:
                return m
        return None

    def ids(self) -> list[str]:
        return [m.id for m in self.modules]

    def providers(self) -> dict[str, str]:
        """Shared content packs (D9) mapped to the module that owns them.

        `modal-grammar` is owned by vim and consumed by Doom, so the pack lives
        in exactly one place and the other module declares a prereq.
        """
        out: dict[str, str] = {}
        for m in self.modules:
            for pack in m.provides:
                out[pack] = m.id
        return out

    def unmet_prereqs(self, module_id: str) -> list[str]:
        """Prereqs naming modules that are not installed.

        Shown, never enforced, per D16 rule 3.
        """
        m = self.get(module_id)
        if not m:
            return []
        known = set(self.ids())
        return [p for p in m.prereqs if p not in known]


def _tuple_of(raw: Any) -> tuple[str, ...]:
    if not raw:
        return ()
    if isinstance(raw, str):
        return (raw,)
    return tuple(raw)


def build_module(raw: dict, source: str = '') -> Module:
    """Normalise a content dict into a Module.

    Raises on the two things that make a module unusable rather than merely
    incomplete: no id, and no title. Everything else has a sane default,
    because content is written by hand and should not need boilerplate.
    """
    mid = raw.get('id')
    if not mid or not isinstance(mid, str):
        raise ValueError(f'{source or "module"}: missing a string id')
    title = raw.get('title')
    if not title:
        raise ValueError(f'{mid}: missing a title')
    return Module(
        id=mid,
        title=title,
        blurb=raw.get('blurb', ''),
        group=raw.get('group') or 'Other',
        context=raw.get('context', ''),
        needs=_tuple_of(raw.get('needs')),
        prereqs=_tuple_of(raw.get('prereqs')),
        provides=_tuple_of(raw.get('provides')),
        adapter=raw.get('adapter'),
        estimate=raw.get('estimate', ''),
        order=int(raw.get('order', 1000)),
        lessons=tuple(raw.get('lessons') or ()),
        challenges=tuple(raw.get('challenges') or ()),
        drills=tuple(raw.get('drills') or ()),
        quiz=tuple(raw.get('quiz') or ()),
        source=source,
    )


def load_all(package: str = CONTENT_PACKAGE) -> Registry:
    """Import every content file and collect the modules they define.

    Sorted by the manifest's `order`, then by title, so the picker matches the
    reading order in the plan rather than whatever the filesystem returns.
    """
    reg = Registry()
    try:
        pkg = importlib.import_module(package)
    except ImportError as e:
        reg.errors.append(LoadError(package, f'content package missing: {e}'))
        return reg

    for info in pkgutil.iter_modules(pkg.__path__):
        name = f'{package}.{info.name}'
        try:
            mod = importlib.import_module(name)
        except Exception as e:  # a broken file must not take the app down
            reg.errors.append(LoadError(name, f'{type(e).__name__}: {e}'))
            continue
        raw = getattr(mod, 'MODULE', None)
        if raw is None:
            continue  # helper file, not a module
        try:
            reg.modules.append(build_module(raw, source=name))
        except ValueError as e:
            reg.errors.append(LoadError(name, str(e)))

    seen: dict[str, str] = {}
    unique: list[Module] = []
    for m in reg.modules:
        if m.id in seen:
            reg.errors.append(
                LoadError(m.source, f'duplicate module id {m.id!r}, '
                                    f'already defined in {seen[m.id]}'))
            continue
        seen[m.id] = m.source
        unique.append(m)
    reg.modules = sorted(unique, key=lambda m: (m.order, m.title.lower()))
    return reg
