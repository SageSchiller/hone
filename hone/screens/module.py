"""One tool, with exactly three views (D16).

Walkthrough, Practice, Drill. Always all three, always in that order, always
rendered even when the module has nothing for one of them, because D16 rule 1
says a hidden view reads as a bug and the student cannot tell the difference
from the outside. A drill deck with no walkthrough says so in its Walkthrough
view instead of not having one.

Quiz is deliberately not a fourth view. Per D16 rule 2 it is a check on the
model rather than a mode of its own, so it sits inside Practice as one row.
It used to have a second surface in the cross-module review queue; D24 removed
the queue, and the quiz stayed exactly where it was most useful.
"""

from __future__ import annotations

import random

from .. import adapters as A
from .. import install
from ..render import Caps, Text, line
from . import STAY, Action, ListScreen, push

VIEWS = ('Walkthrough', 'Practice', 'Drill')
KINDS = {'Walkthrough': 'lessons', 'Practice': 'challenges', 'Drill': 'drills'}


class ModuleScreen(ListScreen):
    """A module's three views, with the cursor scoped to the current one."""

    def __init__(self, module, state, now, open_drill=None,
                 open_lesson=None, open_challenge=None, open_quiz=None,
                 registry=None, open_notes=None) -> None:
        super().__init__()
        self.module = module
        self.registry = registry
        self._open_notes = open_notes
        #: Drill order. Authored order by default, because it is a teaching
        #: order; shuffled on request, because a deck you always meet in the
        #: same sequence teaches the sequence as much as the content.
        self.shuffled: list[int] | None = None
        self.state = state
        self.now = now
        self.view = 0
        self.title = module.title
        self._open_drill = open_drill
        self._open_lesson = open_lesson
        self._open_challenge = open_challenge
        self._open_quiz = open_quiz

    # -- view ---------------------------------------------------------------

    @property
    def view_name(self) -> str:
        return VIEWS[self.view]

    @property
    def kind(self) -> str:
        return KINDS[self.view_name]

    #: Marks the synthetic Practice row that opens the quiz.
    QUIZ_ROW = '__quiz__'

    def items(self) -> tuple[dict, ...]:
        """Rows in the current view.

        Practice carries the module's challenges plus one row for the quiz,
        because D16 rule 2 puts quiz inside Practice rather than giving it a
        fourth view of its own.
        """
        base = self.module.items(self.kind)
        if self.kind == 'drills' and self.shuffled is not None:
            return tuple(base[i] for i in self.shuffled if i < len(base))
        if self.kind == 'challenges' and self.module.has('quiz'):
            n = len(self.module.quiz)
            return base + ({'id': self.QUIZ_ROW,
                            'title': f'Quiz: {n} questions on the model'},)
        return base

    def count(self) -> int:
        return len(self.items())

    def set_view(self, index: int) -> None:
        self.view = index % len(VIEWS)
        self.cursor = 0

    # -- content ------------------------------------------------------------

    def header_rows(self, caps: Caps) -> list[Text]:
        p = caps.palette
        tabs = Text().add('  ')
        for i, name in enumerate(VIEWS):
            on = i == self.view
            has = self.module.has(KINDS[name])
            colour = p.accent if on else (p.muted if has else p.dim)
            tabs.add(f' {name} ', colour, bold=on)
            if not has:
                tabs.add('', p.dim)
            if i < len(VIEWS) - 1:
                tabs.add(caps.g('bullet'), p.border)
        rows = [Text(), tabs]

        underline = Text().add('  ')
        for i, name in enumerate(VIEWS):
            seg = caps.g('hh') if i == self.view else ' '
            underline.add(seg * (len(name) + 2),
                          p.accent if i == self.view else p.bg)
            if i < len(VIEWS) - 1:
                underline.add(' ')
        rows.append(underline)

        if self.module.blurb:
            rows += [Text(), Text().add('  ' + self.module.blurb, p.dim)]

        # Advice, never a gate (D16 rule 3). Stated once, here, where there is
        # room for it, rather than in the picker where it moved the list.
        note = ''
        if self.module.prereqs:
            titles = []
            for pid in self.module.prereqs:
                other = self.registry.get(pid) if self.registry else None
                titles.append(other.title if other else pid)
            note = 'easier after ' + ', '.join(titles)
        unmet = self.registry.unmet_prereqs(self.module.id) if self.registry else []
        if unmet:
            note += f'  ({", ".join(unmet)} is not in this build)'
        if note:
            rows.append(Text().add('  ' + note.strip(), p.dim))

        # A missing tool is the one obstacle the app can actually help with.
        # Saying "content only" and stopping is where people give up.
        gone = install.missing(self.module.needs)
        if gone:
            rows.append(Text())
            rows.append(Text().add(f'  {", ".join(gone)} ', p.warn, bold=True)
                              .add('not installed, so nothing here can be '
                                   'checked', p.muted))
            for tool in gone:
                cmd = install.hint(tool)
                if cmd:
                    rows.append(Text().add('    ' + cmd, p.accent))
            rows.append(Text().add('    You can still read and drill it.',
                                   p.dim))

        rows.append(Text())
        return rows

    def rows(self, caps: Caps) -> list[Text]:
        p = caps.palette
        out: list[Text] = []
        for i, item in enumerate(self.items()):
            sel = i == self.cursor
            iid = item.get('id', '?')
            label = item.get('title') or item.get('prompt') or iid
            # peek, never item(): rendering a list must not create a record
            # for everything the cursor passes over.
            rec = self.state.peek(self.module.id, self.kind, iid)

            t = Text().add(f'  {caps.g("sel") if sel else " "} ', p.accent)
            t.add(f'{label}'[:48].ljust(48), p.fg if sel else p.muted, bold=sel)

            if self.kind == 'lessons':
                done = rec.get('done')
                t.add(f'{caps.g("check")} read' if done else 'unread',
                      p.ok if done else p.dim)
            elif self.kind == 'challenges' and iid == self.QUIZ_ROW:
                seen = sum(1 for c in self.state.peek(self.module.id, 'quiz')
                           .values() if isinstance(c, dict) and c.get('seen'))
                t.add(f'{seen}/{len(self.module.quiz)} seen' if seen else 'new',
                      p.ok if seen else p.dim)
            elif self.kind == 'challenges':
                plan = A.plan_for(item)
                if rec.get('done'):
                    t.add(f'{caps.g("check")} {A.LABELS[rec.get("verification", "self")]}',
                          p.ok)
                else:
                    t.add(plan.label, p.warn if plan.degraded else p.dim)
            else:
                seen = rec.get('seen', 0)
                t.add(f'{seen} seen' if seen else 'new', p.ok if seen else p.dim)
            out.append(t)
        return out

    def empty_state(self, caps: Caps) -> list[Text]:
        """D16 rule 1: say why this view is empty rather than hiding it."""
        p = caps.palette
        if self.view_name == 'Walkthrough' and self.module.is_drill_deck:
            return [
                Text().add('    This tool is a drill deck, by design.', p.warn),
                Text(),
                Text().add('    The difficulty here is remembering the '
                           'invocation, not', p.muted),
                Text().add('    understanding a model, so there is nothing to '
                           'read.', p.muted),
                Text().add('    Go straight to ', p.dim).add('Drill', p.accent)
                      .add('.', p.dim),
            ]
        return [
            Text().add(f'    No {self.view_name.lower()} content for '
                       f'{self.module.title} yet.', p.muted),
            Text(),
            Text().add('    Not every tool needs every view (D5). This one is '
                       'simply', p.dim),
            Text().add('    not written yet.', p.dim),
        ]

    # -- input --------------------------------------------------------------

    def extra_hints(self) -> list[tuple[str, str]]:
        out = [('tab', 'view')]
        if self.kind == 'drills' and self.module.drills:
            out.append(('s', 'ordered' if self.shuffled else 'shuffle'))
        if self._open_notes is not None and self.state.notes(self.module.id):
            out.append(('n', 'notes'))
        return out

    def activate(self, index: int) -> Action:
        if self.kind == 'drills' and self._open_drill is not None:
            return push(self._open_drill(self.module, list(self.items()), index))
        if self.kind == 'lessons' and self._open_lesson is not None:
            return push(self._open_lesson(self.module, self.items()[index]))
        if self.kind == 'challenges':
            item = self.items()[index]
            if item.get('id') == self.QUIZ_ROW:
                if self._open_quiz is not None:
                    return push(self._open_quiz(self.module))
                return STAY
            if self._open_challenge is not None:
                return push(self._open_challenge(self.module, item))
        return STAY

    def handle(self, key):
        if key.name == 's' and not key.ctrl and not key.alt \
                and self.kind == 'drills' and self.module.drills:
            if self.shuffled is None:
                order = list(range(len(self.module.drills)))
                random.Random(self.module.id).shuffle(order)
                self.shuffled = order
            else:
                self.shuffled = None
            self.cursor = 0
            return STAY
        if key.name == 'n' and not key.ctrl and not key.alt \
                and self._open_notes is not None \
                and self.state.notes(self.module.id):
            return push(self._open_notes(self.module.id))
        if key.name == 'TAB' and not key.shift:
            self.set_view(self.view + 1)
            return STAY
        if key.name == 'TAB' and key.shift:
            self.set_view(self.view - 1)
            return STAY
        if key.name == 'Left' and not key.ctrl:
            self.set_view(self.view - 1)
            return STAY
        if key.name == 'Right' and not key.ctrl:
            self.set_view(self.view + 1)
            return STAY
        return super().handle(key)
