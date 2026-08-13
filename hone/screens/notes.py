"""Every note you have written, in one place, each one drillable.

A note is captured at the moment of a miss, which is the right moment to
write it and the wrong moment to need it. Its value is paid out later, and
"later" needs a place to look: notes that can only be found by stumbling back
into their drills are notes you wrote to nobody.

Enter re-drills the noted item immediately, because a note you are rereading
is usually a weakness you are about to practise anyway.
"""

from __future__ import annotations

from ..render import Caps, Text
from . import STAY, Action, ListScreen, push


class NotesScreen(ListScreen):
    """All notes, newest module first, each row openable as a single drill."""

    def __init__(self, registry, state, now, open_item=None,
                 module_id: str | None = None) -> None:
        super().__init__()
        self.registry = registry
        self.state = state
        self.now = now
        self._open_item = open_item
        self.module_id = module_id
        mod = registry.get(module_id) if module_id else None
        self.title = f'{mod.title}: your notes' if mod else 'Your notes'

    def entries(self) -> list[tuple[str, str, str, str]]:
        # Only notes whose content still exists: a note on a renamed drill
        # cannot be re-drilled, and listing it would advertise a dead Enter.
        out = []
        for mid, kind, iid, text in self.state.notes(self.module_id):
            mod = self.registry.get(mid)
            if mod is not None and mod.item(kind, iid) is not None:
                out.append((mid, kind, iid, text))
        return out

    def count(self) -> int:
        return len(self.entries())

    @property
    def status(self) -> str:
        n = self.count()
        return f'{n} note{"" if n == 1 else "s"}'

    def header_rows(self, caps: Caps) -> list[Text]:
        p = caps.palette
        return [Text(),
                Text().add('  What you told yourself at the moment you got '
                           'it wrong.', p.dim),
                Text()]

    def rows(self, caps: Caps) -> list[Text]:
        p = caps.palette
        out = []
        width = max(12, caps.cols - 46)
        for i, (mid, kind, iid, text) in enumerate(self.entries()):
            sel = i == self.cursor
            mod = self.registry.get(mid)
            item = mod.item(kind, iid) if mod else None
            what = str((item or {}).get('prompt') or iid)[:30]
            t = Text().add(f'  {caps.g("sel") if sel else " "} ', p.accent)
            t.add(f'{(mod.title if mod else mid)[:11]:<12}', p.muted)
            t.add(f'{what:<32}', p.fg if sel else p.muted, bold=sel)
            t.add(caps.g('note') + ' ', p.accent2)
            t.add(text[:width], p.accent2 if sel else p.dim)
            out.append(t)
        return out

    def empty_state(self, caps: Caps) -> list[Text]:
        p = caps.palette
        return [Text().add('    No notes yet.', p.muted),
                Text(),
                Text().add('    Press ', p.dim).add('n', p.accent)
                      .add(' on any drill feedback to leave yourself one.',
                           p.dim)]

    def hints(self, caps: Caps) -> list[tuple[str, str]]:
        up_down, enter = self.nav_glyphs(caps)
        out = [(up_down, 'move'), (enter, 'drill it')]
        out += [('esc', 'back'), ('q', 'quit'), ('?', 'help')]
        return out

    def activate(self, index: int) -> Action:
        entries = self.entries()
        if self._open_item is None or index >= len(entries):
            return STAY
        mid, kind, iid, _ = entries[index]
        screen = self._open_item(mid, kind, iid)
        return push(screen) if screen is not None else STAY
