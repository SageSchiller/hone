"""The walkthrough reader: one lesson, scrollable.

The walkthrough engine's whole job is to build a model before any drilling
starts, so a lesson is not a wall of prose. It has four parts and each earns
its place:

* **concept** is the model itself, in prose.
* **examples** are the model made concrete, with real commands.
* **misconceptions** name the specific wrong model people build. This is the
  part most tutorials omit, and it is the highest-value part, because knowing
  what you are about to get wrong is worth more than another correct example.
* **try_it** sends you to the real tool. Per D1 the trainer never runs these
  for you; the terminal is the gym.

Reaching the end marks the lesson read. Reading is not something the app can
verify, so this is D8 `self` territory and the app does not pretend otherwise:
it records that you scrolled to the bottom, which is exactly what it knows.
"""

from __future__ import annotations

from ..render import Caps, Text, wrap
from . import POP, STAY, Screen, push


class LessonScreen(Screen):
    """One lesson. Scrolls, marks read at the bottom, chains to `next`."""

    def __init__(self, module, lesson, state, now, open_lesson=None) -> None:
        self.module = module
        self.lesson = lesson
        self.state = state
        self.now = now
        self.scroll = 0
        self._open_lesson = open_lesson
        self.title = f'{module.title}: {lesson.get("title", lesson.get("id", ""))}'
        self._lines_cache: tuple[int, list[Text]] | None = None

    # -- layout ------------------------------------------------------------

    def _viewport(self, caps: Caps) -> int:
        """Body rows available: total minus the frame, divider and footer."""
        return max(4, caps.rows - 5)

    def full_lines(self, caps: Caps) -> list[Text]:
        """The whole lesson as rendered lines, cached per width."""
        if self._lines_cache and self._lines_cache[0] == caps.cols:
            return self._lines_cache[1]

        p = caps.palette
        w = caps.cols - 6
        L = self.lesson
        out: list[Text] = [Text()]

        for ln in wrap(str(L.get('concept', '')), w, '  '):
            out.append(Text().add(ln, p.fg) if ln else Text())

        for ex in L.get('examples') or ():
            out.append(Text())
            if ex.get('label'):
                out.append(Text().add('  ' + str(ex['label']), p.accent, bold=True))
            for code_line in str(ex.get('code', '')).split('\n'):
                out.append(Text().add('    ', p.bg)
                                 .add(code_line.ljust(max(0, w - 2)), p.ok, p.panel))
            for ln in wrap(str(ex.get('note', '')), w, '    '):
                out.append(Text().add(ln, p.dim) if ln else Text())

        for mis in L.get('misconceptions') or ():
            out.append(Text())
            first = True
            for ln in wrap(str(mis), w - 4, '      '):
                if first and ln:
                    out.append(Text().add('  ! ', p.warn, bold=True)
                                     .add(ln.strip(), p.warn))
                    first = False
                else:
                    out.append(Text().add(ln, p.warn) if ln else Text())

        tries = L.get('try_it') or ()
        if tries:
            out += [Text(), Text().add('  TRY IT FOR REAL', p.accent2, bold=True)]
            for item in tries:
                first = True
                for ln in wrap(str(item), w - 4, '      '):
                    if first and ln:
                        out.append(Text().add('  ' + caps.g('arrow') + ' ', p.accent)
                                         .add(ln.strip(), p.fg))
                        first = False
                    else:
                        out.append(Text().add(ln, p.fg) if ln else Text())

        out.append(Text())
        self._lines_cache = (caps.cols, out)
        return out

    def max_scroll(self, caps: Caps) -> int:
        return max(0, len(self.full_lines(caps)) - self._viewport(caps))

    def at_end(self, caps: Caps) -> bool:
        return self.scroll >= self.max_scroll(caps)

    # -- content -----------------------------------------------------------

    @property
    def status(self) -> str:
        rec = self.state.peek(self.module.id, 'lessons',
                              self.lesson.get('id', ''))
        return 'read' if rec.get('done') else ''

    def body(self, caps: Caps) -> list[Text]:
        lines = self.full_lines(caps)
        vp = self._viewport(caps)
        self.scroll = max(0, min(self.scroll, self.max_scroll(caps)))
        window = lines[self.scroll:self.scroll + vp]

        if self.max_scroll(caps) > 0:
            p = caps.palette
            pct = int(100 * self.scroll / self.max_scroll(caps))
            marker = ('more below' if not self.at_end(caps)
                      else 'end of lesson')
            window = list(window) + [Text(), Text().add(
                f'  {caps.g("bullet")} {marker} ({pct}%)', p.dim)]
        # Reaching the bottom is what the app can honestly observe about
        # reading, so that is what it records. See D8.
        if self.at_end(caps):
            self._mark_read()
        return window or [Text().add('  (this lesson has no body yet)',
                                     caps.palette.muted)]

    def _mark_read(self) -> None:
        # Called from body(), which runs every frame: record once per visit,
        # not once per repaint, or sitting at the end of a lesson re-dirties
        # the state on every keystroke.
        if getattr(self, '_recorded', False):
            return
        lid = self.lesson.get('id')
        if not lid:
            return
        self._recorded = True
        if not self.state.peek(self.module.id, 'lessons', lid).get('done'):
            self.state.mark_lesson(self.module.id, lid, self.now)

    def hints(self, caps: Caps) -> list[tuple[str, str]]:
        hints = [(f'{caps.g("up")}{caps.g("down")}', 'scroll')]
        if self._next_lesson() is not None:
            hints.append((caps.g('enter'), 'next lesson'))
        hints += [('esc', 'back'), ('H', 'home'), ('q', 'quit'), ('?', 'help')]
        return hints

    def nav_glyphs(self, caps: Caps) -> tuple[str, str]:
        return caps.g('up') + caps.g('down'), caps.g('enter')

    # -- navigation --------------------------------------------------------

    def _next_lesson(self):
        nxt = self.lesson.get('next')
        if not nxt:
            return None
        return self.module.item('lessons', nxt)

    def handle(self, key):
        name = key.name
        if name in ('Down', 'j') and not key.ctrl:
            self.scroll += 1
            return STAY
        if name in ('Up', 'k') and not key.ctrl:
            self.scroll = max(0, self.scroll - 1)
            return STAY
        if name == 'SPC' or name == 'PgDn':
            self.scroll += 10
            return STAY
        if name == 'PgUp':
            self.scroll = max(0, self.scroll - 10)
            return STAY
        if name == 'Home':
            self.scroll = 0
            return STAY
        if name == 'End':
            self.scroll = 10 ** 6      # clamped on next render
            return STAY
        if name == 'RET':
            nxt = self._next_lesson()
            if nxt is not None and self._open_lesson is not None:
                self._mark_read()
                return push(self._open_lesson(self.module, nxt))
            return POP
        return super().handle(key)
