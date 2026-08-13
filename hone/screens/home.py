"""Home: a shelf of tools, grouped, and nothing else (D16, D24).

**What is deliberately absent.** There is no queue, no streak, no count of
things owed, and no line telling you what to do next. All of that existed, and
D24 removed it: the app keeps no clock on you and has no opinion about your
pace. What is left is the question the student actually arrived with, which is
*which tool do I want to learn*, and fifteen answers to it.

**Why grouped.** Fifteen names in one column is a wall you scroll rather than a
menu you scan, and the order was never meaningful to a newcomer: awk sitting
next to Linux sitting next to bash reads as a list nobody sorted. Five or six
short lists under headings turn it into something you can take in at a glance
and choose from by category, which is how people actually decide.

**The third column says what the machine can do, not what you have done.** It
used to read "verified", which is the word D8 puts on a task you completed
under real verification, and printing it beside a tool you have never opened
was a lie by adjacency. It now says whether hone can check your work here, and
when it cannot, what is missing.

Prerequisites are not shown here either. They are advice, never a gate (D16
rule 3), and the row that carried them appeared and disappeared under the
cursor and made the list jump. The module screen says it once, where there is
room and nothing moves.
"""

from __future__ import annotations

from datetime import datetime

from .. import adapters as A
from .. import install
from ..config import APP_TITLE, TAGLINE_PARTS
from ..render import Caps, Text, bar
from . import STAY, Action, ListScreen, push


class HomeScreen(ListScreen):
    """Root screen. Esc quits here rather than popping into nothing."""

    can_pop = False

    def __init__(self, registry, state, now: datetime, open_module=None,
                 open_notes=None) -> None:
        super().__init__()
        self.registry = registry
        self.state = state
        self.now = now
        self.title = APP_TITLE
        self._open_module = open_module
        self._open_notes = open_notes

    # -- data --------------------------------------------------------------

    def count(self) -> int:
        return len(self.registry)

    def ordered(self) -> list:
        """Modules in the order they appear on screen.

        Grouping reorders the list, and the cursor is a position in what you
        are looking at. Indexing `registry.modules` instead meant Enter
        opened a different tool from the highlighted one as soon as a group
        was not contiguous in registry order.
        """
        return [mod for _, mods in self.groups() for mod in mods]

    def groups(self) -> list[tuple[str, list]]:
        """(heading, modules), headings in order of first appearance.

        Registry order is the curriculum order and is preserved inside each
        group, so the priority tools still come first where they belong.
        """
        out: list[tuple[str, list]] = []
        index: dict[str, int] = {}
        for mod in self.registry:
            if mod.group not in index:
                index[mod.group] = len(out)
                out.append((mod.group, []))
            out[index[mod.group]][1].append(mod)
        return out

    def checkable(self, mod) -> tuple[bool, str]:
        """Whether hone can check work in this tool, and what to say if not.

        D26: the mode is answered before anything else, because when the
        student has turned checking off the answer is the same for every
        module and listing what each one *could* have done would be an advert
        for a setting they just changed on purpose.
        """
        if A.read_only():
            return False, 'read and drill only'
        ok, reason = A.status(mod.adapter)
        if ok:
            return True, 'checks your work'
        gone = install.missing(mod.needs)
        if gone:
            return False, f'needs {gone[0]}'
        if not mod.adapter:
            return False, 'read and drill only'
        return False, reason

    # -- content -----------------------------------------------------------

    def header_rows(self, caps: Caps) -> list[Text]:
        p = caps.palette
        # The mode is stated on the one screen every session starts from.
        # Without it, "read and drill only" against every module reads as
        # fifteen things being broken rather than as one switch being off.
        read = A.read_only()
        mode = Text().add('  mode  ', p.dim)
        mode.add(f' {A.mode()} ', p.bg, p.muted if read else p.accent, bold=True)
        mode.add(f'  {A.MODE_BLURB[A.mode()]}', p.dim)
        return [
            Text(),
            Text().add('  ' + ' '.join(APP_TITLE), p.accent, bold=True),
            Text().add('  ' + f' {caps.g("bullet")} '.join(TAGLINE_PARTS), p.dim),
            Text(),
            mode,
            Text(),
        ]

    def module_row(self, caps: Caps, mod, selected: bool) -> Text:
        p = caps.palette
        pct = self.state.progress(mod.id, mod.totals())
        ok, label = self.checkable(mod)

        t = Text().add(f'  {caps.g("sel") if selected else " "} ', p.accent)
        t.add(f'{mod.title[:18]:<18}', p.fg if selected else p.muted,
              bold=selected)
        t.spans.extend(bar(caps, pct).spans)
        t.add(f' {int(pct * 100):3d}%   ', p.dim)
        t.add(f'{caps.g("check")} {label}' if ok
              else f'{caps.g("bullet")} {label}', p.ok if ok else p.dim)
        return t

    def rows(self, caps: Caps) -> list[Text]:
        """Ungrouped rows. Only reached if `body` is overridden away."""
        return [self.module_row(caps, mod, i == self.cursor)
                for i, mod in enumerate(self.ordered())]

    def body(self, caps: Caps) -> list[Text]:
        """Headings and rows, windowed on the cursor.

        Its own windowing rather than `ListScreen.body`, because headings mean
        display rows and selectable items are no longer one to one, and the
        base class's scroll arithmetic assumes they are.
        """
        self.clamp()
        head = self.header_rows(caps)
        if self.count() <= 0:
            return head + self.empty_state(caps)

        p = caps.palette
        lines: list[Text] = []
        cursor_line = 0
        index = 0
        for name, mods in self.groups():
            if lines:
                lines.append(Text())
            lines.append(Text().add('  ' + name.upper(), p.accent2, bold=True))
            for mod in mods:
                if index == self.cursor:
                    cursor_line = len(lines)
                lines.append(self.module_row(caps, mod, index == self.cursor))
                index += 1

        room = max(3, caps.rows - 4 - len(head))
        if len(lines) <= room:
            self.scroll = 0
            return head + lines

        room -= 1                                  # room for the indicator
        if cursor_line < self.scroll:
            self.scroll = max(0, cursor_line - 1)  # keep its heading in view
        elif cursor_line >= self.scroll + room:
            self.scroll = cursor_line - room + 1
        self.scroll = max(0, min(self.scroll, len(lines) - room))

        window = lines[self.scroll:self.scroll + room]
        above, below = self.scroll, max(0, len(lines) - self.scroll - room)
        marker = Text().add('  ', p.dim)
        if above:
            marker.add(f'{caps.g("up")} {above} above   ', p.dim)
        if below:
            marker.add(f'{caps.g("down")} {below} below', p.dim)
        if not above and not below:
            marker.add(' ', p.dim)
        return head + window + [marker]

    def empty_state(self, caps: Caps) -> list[Text]:
        """No content installed. Phase 0 lives here permanently.

        D19 rule 3 in its most literal form: the app with zero modules must
        still explain itself rather than showing an empty box.
        """
        p = caps.palette
        rows = [
            Text().add('    No tools are installed in this build yet.', p.warn),
            Text(),
            Text().add('    A tool is one file under ', p.muted)
                  .add('hone/content/', p.accent)
                  .add(' that defines ', p.muted)
                  .add('MODULE', p.accent),
            Text().add('    Discovery is additive: drop the file in and it '
                       'appears here.', p.dim),
        ]
        if self.registry.errors:
            rows += [Text(), Text().add('    Content failed to load:', p.err)]
            for e in self.registry.errors[:4]:
                rows.append(Text().add(f'      {e.name}: {e.message}', p.dim))
        return rows

    # -- input -------------------------------------------------------------

    def extra_hints(self) -> list[tuple[str, str]]:
        # D19 rule 4: the mode key is always advertised, because a mode you
        # cannot find is a mode you cannot turn back off.
        out = [('m', 'checking mode')]
        if self._open_notes is not None and self.state.notes():
            out.insert(0, ('n', 'your notes'))
        return out

    def activate(self, index: int) -> Action:
        mods = self.ordered()
        if self._open_module is None or index >= len(mods):
            return STAY
        return push(self._open_module(mods[index]))

    def handle(self, key):
        if key.name == 'n' and not key.ctrl and not key.alt \
                and self._open_notes is not None and self.state.notes():
            return push(self._open_notes())
        if key.name == 'm' and not key.ctrl and not key.alt:
            return self._toggle_mode()
        return super().handle(key)

    def _toggle_mode(self) -> Action:
        """Flip between checking and read-and-drill, and remember it.

        Persisted rather than per-session: the reason to turn checking off is
        usually a property of where you are, like a laptop you would rather
        not have spawning tmux sessions, and having to say so again every
        launch would make it a setting nobody keeps.
        """
        new = A.READ if A.mode() == A.CHECKED else A.CHECKED
        A.set_mode(new)
        self.state.set_setting('checking', new)
        self.state.dirty = True
        return STAY
