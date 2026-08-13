"""Progress state: a JSON file on disk, per D7.

**What this records, and what it deliberately does not.** It remembers what you
have read, what you have passed, and how each drill has gone. It does not
remember when you last opened the app, how many days in a row you have turned
up, or when anything is "due", because none of that is yours to be measured on.
See D24: the app keeps no clock on you and has no opinion about your pace.

Two rules the rest of the app depends on:

* **Loading never raises.** A missing file is a new user. A corrupt file is set
  aside rather than deleted, and loading continues with a fresh state carrying
  a `recovered_from` note the UI can surface. Losing someone's progress
  silently is worse than any error message.
* **Time is injected.** Every function that needs 'now' takes it as an
  argument. Less load-bearing than it was now that nothing is scheduled, but
  still what keeps the tests deterministic.
"""

from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import state_path

VERSION = 2

#: Fields that belonged to the spaced-repetition scheduler, stripped from
#: every card on load. Listed explicitly rather than rewritten, so a file
#: written by an older build opens without complaint and simply forgets the
#: parts of itself that no longer mean anything. See D24.
RETIRED_CARD_FIELDS = ('due', 'ease', 'interval', 'reps', 'lapses',
                       'max_interval', 'best_ms', 'last_ms', 'first_try')

#: The same, at the document level: daily activity and the badges built on it.
RETIRED_KEYS = ('activity', 'achievements', 'last')


def now() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat(timespec='seconds')


def parse_iso(s: str | None) -> datetime | None:
    if not s or not isinstance(s, str):
        return None
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    # A hand-edited or foreign timestamp may be naive, and one naive datetime
    # poisons every comparison it meets. Everything here is UTC, so that is
    # what a bare timestamp means.
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _blank(at: datetime) -> dict[str, Any]:
    return {
        'version': VERSION,
        'created': iso(at),
        'updated': iso(at),
        'settings': {
            'theme': None,
            'rigor': 'free',        # D6: guided | coached | free
            'checking': 'checked',  # D26: checked | read
            'seen_tour': False,     # D19 first-run tour
            'nerd_glyphs': False,
            'sync_path': None,      # remembered by --sync
            'splash': True,         # the launch screen
        },
        'modules': {},
    }


@dataclass
class State:
    """In-memory progress, loadable and savable as one JSON document."""

    data: dict[str, Any]
    path: Path | None = None
    recovered_from: Path | None = None
    dirty: bool = False

    # -- construction ------------------------------------------------------

    @classmethod
    def blank(cls, at: datetime | None = None) -> State:
        return cls(data=_blank(at or now()))

    @classmethod
    def load(cls, path: Path | None = None, at: datetime | None = None) -> State:
        """Read state from disk. Never raises: see the module docstring."""
        at = at or now()
        path = path or state_path()
        if not path.exists():
            return cls(data=_blank(at), path=path)
        try:
            raw = json.loads(path.read_text(encoding='utf-8'))
            if not isinstance(raw, dict) or 'modules' not in raw:
                raise ValueError('not a state document')
        except (OSError, ValueError, json.JSONDecodeError):
            quarantine = cls._quarantine(path)
            return cls(data=_blank(at), path=path, recovered_from=quarantine)
        raw = cls._migrate(raw, at)
        return cls(data=raw, path=path)

    @staticmethod
    def _quarantine(path: Path) -> Path | None:
        """Move an unreadable state file aside instead of overwriting it."""
        for n in range(1, 100):
            dest = path.with_suffix(f'.corrupt{n}.json')
            if not dest.exists():
                try:
                    shutil.move(str(path), str(dest))
                    return dest
                except OSError:
                    return None
        return None

    @staticmethod
    def _migrate(raw: dict, at: datetime) -> dict:
        """Bring an older document up to the current shape.

        Two jobs. **Structural**: `load` only rejects a file that is not a
        JSON object with a `modules` key, so everything below that level can
        still be the wrong shape (a hand edit, a truncated copy, another
        tool's file). Every consumer indexes into these structures assuming
        dicts of dicts, so anything that is not one is dropped here, once,
        rather than defended against at every call site.

        **Version 1 to 2**: the scheduler is gone (D24). Its fields are
        stripped from every card and its top-level keys dropped. What survives
        is what someone actually did: `seen`, `correct`, `done`, and their
        notes. A v1 file therefore opens with its progress intact and its
        streak quietly forgotten, which is the honest outcome. The streak was
        never evidence of anything.
        """
        raw.setdefault('version', VERSION)
        if not isinstance(raw.get('settings'), dict):
            raw['settings'] = {}
        for key, val in _blank(at)['settings'].items():
            raw['settings'].setdefault(key, val)

        mods = raw.get('modules')
        raw['modules'] = mods if isinstance(mods, dict) else {}
        for mid in list(raw['modules']):
            rec = raw['modules'][mid]
            if not isinstance(rec, dict):
                del raw['modules'][mid]
                continue
            for kind in list(rec):
                bucket = rec[kind]
                if not isinstance(bucket, dict):
                    del rec[kind]
                    continue
                for iid in list(bucket):
                    item = bucket[iid]
                    if not isinstance(item, dict):
                        del bucket[iid]
                        continue
                    for field in RETIRED_CARD_FIELDS:
                        item.pop(field, None)

        for key in RETIRED_KEYS:
            raw.pop(key, None)

        raw.setdefault('created', iso(at))
        raw['version'] = VERSION
        return raw

    # -- persistence -------------------------------------------------------

    def _write_json(self, dest: Path) -> None:
        """Temp file beside the target, then rename. Both writers use this: a
        crash mid-write must never leave a half-written document at a path
        someone will later trust, and the --sync copy is exactly such a path.
        """
        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_suffix(dest.suffix + '.tmp')
        tmp.write_text(json.dumps(self.data, indent=2, sort_keys=True) + '\n',
                       encoding='utf-8')
        os.replace(tmp, dest)

    def save(self, path: Path | None = None, at: datetime | None = None) -> Path:
        path = path or self.path or state_path()
        self.data['updated'] = iso(at or now())
        self._write_json(path)
        self.path = path
        self.dirty = False
        return path

    def export_to(self, dest: Path, at: datetime | None = None) -> Path:
        self.data['updated'] = iso(at or now())
        self._write_json(dest)
        return dest

    @classmethod
    def import_from(cls, src: Path, at: datetime | None = None) -> State:
        """Read an exported file. Raises, because the user chose this file.

        Unlike `load`, a bad import is worth reporting rather than swallowing:
        the user pointed at a specific path and expects to hear if it is wrong.
        """
        raw = json.loads(src.read_text(encoding='utf-8'))
        if not isinstance(raw, dict) or 'modules' not in raw:
            raise ValueError(f'{src} is not a hone state file')
        return cls(data=cls._migrate(raw, at or now()))

    # -- settings ----------------------------------------------------------

    @property
    def settings(self) -> dict[str, Any]:
        return self.data['settings']

    def set_setting(self, key: str, value: Any) -> None:
        self.settings[key] = value
        self.dirty = True

    # -- per-module records ------------------------------------------------

    def module(self, module_id: str) -> dict[str, Any]:
        """Get (creating if needed) the record for one module."""
        mods = self.data['modules']
        if module_id not in mods:
            mods[module_id] = {'lessons': {}, 'challenges': {}, 'drills': {},
                               'quiz': {}}
            self.dirty = True
        rec = mods[module_id]
        for key in ('lessons', 'challenges', 'drills', 'quiz'):
            rec.setdefault(key, {})
        return rec

    def item(self, module_id: str, kind: str, item_id: str) -> dict[str, Any]:
        bucket = self.module(module_id)[kind]
        if item_id not in bucket:
            bucket[item_id] = {}
            self.dirty = True
        return bucket[item_id]

    def peek(self, module_id: str, kind: str | None = None,
             item_id: str | None = None):
        """Read a record without creating anything on the way.

        `module()` and `item()` create as they go, which is right when
        recording an answer and wrong everywhere else: rendering a list used
        to create an empty entry for every row the cursor passed over. Reads
        go through here; only writes may create.
        """
        rec = self.data.get('modules', {}).get(module_id)
        if not isinstance(rec, dict):
            return {}
        if kind is None:
            return rec
        bucket = rec.get(kind)
        if not isinstance(bucket, dict):
            return {}
        if item_id is None:
            return bucket
        item = bucket.get(item_id)
        return item if isinstance(item, dict) else {}

    def mark_lesson(self, module_id: str, lesson_id: str,
                    at: datetime | None = None) -> None:
        rec = self.item(module_id, 'lessons', lesson_id)
        rec['done'] = True
        rec['at'] = iso(at or now())
        self.dirty = True

    def mark_challenge(self, module_id: str, challenge_id: str, mode: str,
                       verification: str, at: datetime | None = None) -> None:
        """Record a completed challenge.

        `verification` is D8's label (`verified`, `graded`, `self`) and is kept
        per attempt, so the record can never later be mistaken for stronger
        evidence than it was.
        """
        rec = self.item(module_id, 'challenges', challenge_id)
        rec['done'] = True
        rec['mode'] = mode
        rec['verification'] = verification
        rec['at'] = iso(at or now())
        self.dirty = True

    def record_answer(self, module_id: str, kind: str, item_id: str,
                      correct: bool) -> dict[str, Any]:
        """Log one attempt at a drill or quiz item.

        Two counters and nothing else. There is no interval to compute and no
        date to write down: an attempt is evidence about the item, not about
        the day you had.
        """
        rec = self.item(module_id, kind, item_id)
        rec['seen'] = rec.get('seen', 0) + 1
        if correct:
            rec['correct'] = rec.get('correct', 0) + 1
        self.dirty = True
        return rec

    # -- notes -------------------------------------------------------------

    def note(self, module_id: str, kind: str, item_id: str) -> str:
        return str(self.peek(module_id, kind, item_id).get('note') or '')

    def set_note(self, module_id: str, kind: str, item_id: str,
                 text: str) -> None:
        """Attach a note to one item.

        The one thing a learner knows that the app cannot derive: why *they*
        keep getting this particular one wrong.
        """
        rec = self.item(module_id, kind, item_id)
        text = text.strip()
        if text:
            rec['note'] = text
        else:
            rec.pop('note', None)
        self.dirty = True

    def notes(self, module_id: str | None = None
              ) -> list[tuple[str, str, str, str]]:
        """Every note, as (module_id, kind, item_id, text)."""
        out = []
        for mid, rec in self.data.get('modules', {}).items():
            if module_id is not None and mid != module_id:
                continue
            if not isinstance(rec, dict):
                continue
            for kind, bucket in rec.items():
                if not isinstance(bucket, dict):
                    continue
                for iid, item in bucket.items():
                    if isinstance(item, dict) and item.get('note'):
                        out.append((mid, kind, iid, item['note']))
        return sorted(out)

    # -- starting over -----------------------------------------------------

    def reset(self, module_id: str | None = None) -> dict[str, int]:
        """Erase progress. Returns what was thrown away, for the report.

        Preferences are not progress and survive: theme, rigor, sync path, and
        having seen the tour. The caller backs the file up first; this does
        not touch the disk.
        """
        lost = {'items': 0, 'modules': 0}
        mods = self.data.get('modules', {})

        for mid in ([module_id] if module_id else list(mods)):
            rec = mods.get(mid)
            if not isinstance(rec, dict):
                continue
            lost['modules'] += 1
            for kind in ('lessons', 'challenges', 'drills', 'quiz'):
                lost['items'] += len(rec.get(kind) or {})
            del mods[mid]

        self.dirty = True
        return lost

    # -- progress ----------------------------------------------------------

    def counts(self, module_id: str) -> dict[str, int]:
        """How much of each kind has been genuinely met.

        Lessons and challenges are done or not. Drills and quiz items count as
        met once you have actually attempted them, which is `seen`.
        """
        rec = self.peek(module_id)

        def bucket(kind: str) -> dict:
            b = rec.get(kind)
            return b if isinstance(b, dict) else {}

        return {
            kind: sum(1 for v in bucket(kind).values()
                      if isinstance(v, dict) and v.get('done'))
            for kind in ('lessons', 'challenges')
        } | {
            kind: sum(1 for v in bucket(kind).values()
                      if isinstance(v, dict) and v.get('seen', 0) > 0)
            for kind in ('drills', 'quiz')
        }

    def progress(self, module_id: str, totals: dict[str, int]) -> float:
        """Fraction met across every kind the module actually has.

        Kinds with no content are excluded rather than counted as complete, so
        a drill deck with no walkthrough is not permanently stuck at 75%.
        """
        done = self.counts(module_id)
        num = sum(min(done.get(k, 0), n) for k, n in totals.items() if n)
        den = sum(n for n in totals.values() if n)
        return (num / den) if den else 0.0

    def accuracy(self, module_id: str) -> tuple[int, int]:
        """(correct, seen) across this module's drills and quiz items."""
        rec = self.peek(module_id)
        correct = seen = 0
        for kind in ('drills', 'quiz'):
            bucket = rec.get(kind)
            if not isinstance(bucket, dict):
                continue
            for v in bucket.values():
                if isinstance(v, dict):
                    seen += v.get('seen', 0)
                    correct += v.get('correct', 0)
        return correct, seen
