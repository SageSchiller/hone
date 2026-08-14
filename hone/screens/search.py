"""Search across every tool, because the roster outgrew browsing.

With fifteen modules you found things by remembering which tool they were
under. With forty-six you do not, and the question people actually arrive
with is not "what is in the ssh module", it is **"which module teaches the
thing I am trying to do right now"**. Nothing in the app could answer that,
so the content was only reachable by already knowing where it lived.

**It searches what you would search for**: lesson titles, drill prompts and
their answers, challenge goals, quiz prompts. The answer text is included
deliberately, because half the time you remember the flag and not the
sentence: typing `--delete` should find the rsync drill even though those
characters appear nowhere in its prompt.

**Ranked, not merely filtered.** A word in a title means more than the same
word buried in an answer, and a whole-word hit means more than a fragment, so
results are ordered by where they matched rather than by module order. With
929 drills an unranked substring list is a wall.

Opening a result goes to the item itself, not to its module, because the
point is to land on the thing you searched for.
"""

from __future__ import annotations

from ..render import Caps, Text, strip_markup
from . import STAY, Action, ListScreen, push

#: Where a hit can land, and what it is worth. Titles and prompts are what a
#: person half-remembers; an answer match is a real hit but a weaker signal.
FIELD_WEIGHT = (
    ('title', 10),
    ('prompt', 10),
    ('goal', 6),
    ('answer', 4),
    ('teach', 2),
)

#: What each kind is called on screen. The module screen's own tab names, so
#: a result reads the same way the place it lives does.
KIND_LABEL = {
    'lessons': 'walkthrough',
    'challenges': 'practice',
    'drills': 'drill',
    'quiz': 'quiz',
}

#: Longer than this and the row cannot show enough of either side to be read.
MAX_SNIPPET = 46

#: Plain dots on purpose. This is chosen without `caps` in reach, so it has to
#: be safe at the ASCII rung, where a Unicode ellipsis would be tofu.
CUT = '...'


class SearchScreen(ListScreen):
    """Type to narrow, Enter to open the item itself."""

    def __init__(self, registry, state, now, open_item=None,
                 open_module=None) -> None:
        super().__init__()
        self.registry = registry
        self.state = state
        self.now = now
        self._open_item = open_item
        self._open_module = open_module
        self.query = ''
        self.title = 'Search'
        self._cache: tuple[str, list] | None = None

    # -- searching ---------------------------------------------------------

    def results(self) -> list[dict]:
        """Matching items, best first. Cached per query: `body` runs per frame."""
        q = self.query.strip().lower()
        if self._cache and self._cache[0] == q:
            return self._cache[1]
        found = [] if len(q) < 2 else self._search(q)
        self._cache = (q, found)
        return found

    def _search(self, q: str) -> list[dict]:
        out = []
        for mod in self.registry:
            for kind in ('lessons', 'challenges', 'drills', 'quiz'):
                for item in mod.items(kind):
                    score, field, text = self._score(item, q)
                    if score:
                        out.append({'module': mod, 'kind': kind, 'item': item,
                                    'score': score, 'field': field,
                                    'text': text})
        # Stable within a score so repeated searches do not reshuffle.
        out.sort(key=lambda r: (-r['score'], r['module'].order,
                                r['module'].id))
        return out

    def _score(self, item: dict, q: str) -> tuple[int, str, str]:
        """Best (score, field, matching text) for one item, or (0, '', '')."""
        best = (0, '', '')
        for field, weight in FIELD_WEIGHT:
            raw = item.get(field)
            if not isinstance(raw, str) or not raw:
                continue
            text = strip_markup(raw)
            at = text.lower().find(q)
            if at < 0:
                continue
            score = weight
            # A hit at a word boundary is what the person meant far more
            # often than one inside a longer word: "ssh" should rank the ssh
            # drill above a sentence containing "sshd_config".
            if at == 0 or not text[at - 1].isalnum():
                score += 3
            if at == 0:
                score += 2
            if score > best[0]:
                best = (score, field, text)
        return best

    # -- content -----------------------------------------------------------

    def count(self) -> int:
        return len(self.results())

    @property
    def status(self) -> str:
        n = len(self.results())
        if len(self.query.strip()) < 2:
            return ''
        return f'{n} result{"" if n == 1 else "s"}'

    def header_rows(self, caps: Caps) -> list[Text]:
        p = caps.palette
        box = Text().add('  ' + caps.g('arrow') + ' ', p.accent)
        box.add(self.query, p.fg, bold=True)
        box.add('_', p.accent, bold=True)
        hint = Text().add('    type at least two characters, across all '
                          f'{len(self.registry)} tools', p.dim)
        return [Text(), box, hint, Text()]

    def _snippet(self, text: str, q: str) -> tuple[str, str, str]:
        """The matched text split into (before, hit, after), trimmed to fit."""
        at = text.lower().find(q.strip().lower())
        if at < 0:
            return text[:MAX_SNIPPET], '', ''
        hit = text[at:at + len(q.strip())]
        before, after = text[:at], text[at + len(hit):]
        room = MAX_SNIPPET - len(hit)
        if len(before) > room // 2:
            before = CUT + before[-(room // 2):]
        after = after[:max(0, room - len(before))]
        return before, hit, after

    def rows(self, caps: Caps) -> list[Text]:
        p = caps.palette
        q = self.query.strip()
        out = []
        for i, r in enumerate(self.results()):
            sel = i == self.cursor
            t = Text().add(f'  {caps.g("sel") if sel else " "} ', p.accent)
            label = Text().add(r['module'].title, p.fg if sel else p.muted,
                               bold=sel)
            label.truncate(16, caps.g('ellipsis')).pad_to(17)
            t.spans.extend(label.spans)
            t.add(f'{KIND_LABEL[r["kind"]]:<12}', p.dim)
            before, hit, after = self._snippet(r['text'], q)
            t.add(before, p.muted if not sel else p.fg)
            t.add(hit, p.accent2, bold=True)
            t.add(after, p.muted if not sel else p.fg)
            out.append(t)
        return out

    def empty_state(self, caps: Caps) -> list[Text]:
        p = caps.palette
        if len(self.query.strip()) < 2:
            return [
                Text().add('    Search every lesson, drill, practice session '
                           'and quiz.', p.muted),
                Text(),
                Text().add('    Flags work too: ', p.dim)
                      .add('--delete', p.accent)
                      .add(' finds the rsync drill that uses it.', p.dim),
            ]
        return [
            Text().add(f'    Nothing matches "{self.query.strip()}".', p.warn),
            Text(),
            Text().add('    Backspace to edit it, or Esc to go back.', p.dim),
        ]

    # -- input -------------------------------------------------------------

    def extra_hints(self) -> list[tuple[str, str]]:
        return [('type', 'narrow')]

    def activate(self, index: int) -> Action:
        found = self.results()
        if index >= len(found):
            return STAY
        r = found[index]
        if self._open_item is not None:
            screen = self._open_item(r['module'], r['kind'], r['item'])
            if screen is not None:
                return push(screen)
        if self._open_module is not None:
            return push(self._open_module(r['module']))
        return STAY

    def handle(self, key):
        name = key.name
        if name == 'ESC':
            return super().handle(key)
        if name in ('BSP', 'DEL'):
            self.query = self.query[:-1]
            self.cursor = 0
            return STAY
        if name == 'SPC':
            self.query += ' '
            self.cursor = 0
            return STAY
        # A printable key is a character to search for, never a shortcut:
        # this screen owns the keyboard while it is open, which is why its
        # footer advertises `type` and not the usual letter keys.
        if len(name) == 1 and name.isprintable() and not key.ctrl and not key.alt:
            self.query += name
            self.cursor = 0
            return STAY
        return super().handle(key)
