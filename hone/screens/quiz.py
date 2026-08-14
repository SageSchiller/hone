"""The quiz engine: the check on whether the model landed.

D16 rule 2 says quiz is not a fourth view. It lives inside a module's Practice
view as one row: a set of questions about how the tool thinks, taken together.

Quiz items test the *model*, not the bindings. The drills already cover recall,
so asking "which key splits a pane" twice would be repetition rather than
coverage. Asking "you closed the terminal, what happened to the process" tests
something a drill cannot reach.

Option order is shuffled, because a correct answer that is always third stops
testing anything. The shuffle is **deterministic per attempt**: seeded from the
item id and how many times you have seen it, so the order changes between
attempts but a given attempt replays identically in tests.
"""

from __future__ import annotations

import random
import time

from .. import keys as K
from ..render import Caps, Text, strip_markup, wrap, wrap_rich
from . import POP, ROOT, STAY, Screen


class QuizScreen(Screen):
    """Multiple choice over a list of quiz items."""

    def __init__(self, module, items, index, state, now,
                 clock=time.monotonic, on_finish=None) -> None:
        self.module = module
        self.items = list(items)
        self.index = max(0, min(index, len(self.items) - 1)) if self.items else 0
        self.state = state
        self.now = now
        self.clock = clock
        self.on_finish = on_finish

        self.title = f'{module.title} quiz'
        self.phase = 'prompt'          # prompt | feedback
        self.picked: int | None = None
        self.last_correct: bool | None = None
        self.started: float | None = None
        self.right = 0
        self.answered = 0
        self._options_cache: tuple[str, list[str]] | None = None

    # -- current item ------------------------------------------------------

    @property
    def item(self) -> dict:
        return self.items[self.index] if self.items else {}

    def options(self) -> list[str]:
        """Answer plus distractors, in a stable-per-attempt shuffled order."""
        q = self.item
        qid = q.get('id', '')
        if self._options_cache and self._options_cache[0] == qid:
            return self._options_cache[1]
        # Duplicates would break correct_index(), which finds the answer by
        # text: two identical options means one of them is judged wrong while
        # reading identically. Authored content is linted against this;
        # generated content is deduped here as the backstop.
        opts = [str(q.get('answer', ''))]
        for d in (q.get('distractors') or ()):
            if str(d) not in opts:
                opts.append(str(d))
        # Seeded on how many times you have seen it, so the order is stable
        # while you are looking at it and different next time.
        card = self.state.peek(self.module.id, 'quiz', qid)
        rng = random.Random(f'{qid}:{card.get("seen", 0)}')
        rng.shuffle(opts)
        self._options_cache = (qid, opts)
        return opts

    def correct_index(self) -> int:
        try:
            return self.options().index(str(self.item.get('answer', '')))
        except ValueError:
            return -1

    # -- content -----------------------------------------------------------

    @property
    def status(self) -> str:
        return f'{self.index + 1} of {len(self.items)}'

    def body(self, caps: Caps) -> list[Text]:
        p = caps.palette
        q = self.item
        if not q:
            return [Text().add('    No quiz items in this module yet.', p.muted)]

        rows: list[Text] = [Text()]
        head = Text().add(f'  {self.module.title} ', p.dim)
        head.add(f'{caps.g("bullet")} question {self.index + 1} of '
                 f'{len(self.items)}   ', p.dim)
        head.add(f'{self.right}/{self.answered} right' if self.answered else '',
                 p.dim)
        rows += [head, Text()]

        for ln in wrap(strip_markup(str(q.get('prompt', ''))), caps.cols - 6, '  '):
            rows.append(Text().add(ln, p.fg, bold=True) if ln else Text())
        rows.append(Text())

        for i, opt in enumerate(self.options()):
            picked = self.picked == i
            is_answer = i == self.correct_index()
            if self.phase == 'feedback':
                if is_answer:
                    mark, colour = caps.g('check'), p.ok
                elif picked:
                    mark, colour = caps.g('cross'), p.err
                else:
                    mark, colour = ' ', p.dim
            else:
                mark, colour = ' ', p.fg
            row = Text().add(f'  {mark} ', colour, bold=True)
            row.add(f'{i + 1}. ', p.accent if self.phase == 'prompt' else p.dim)
            first = True
            for ln in wrap(strip_markup(opt), caps.cols - 12, ''):
                if first:
                    row.add(ln, colour, bold=picked or (is_answer and
                                                        self.phase == 'feedback'))
                    rows.append(row)
                    first = False
                else:
                    rows.append(Text().add('       ', p.dim).add(ln, colour))

        if self.phase == 'feedback':
            teach = q.get('teach')
            if teach:
                rows.append(Text())
                rows += wrap_rich(caps, str(teach), caps.cols - 8, '    ', p.dim,
                                  p.accent)
        return rows

    def hints(self, caps: Caps) -> list[tuple[str, str]]:
        if self.phase == 'feedback':
            nxt = 'next' if self.index + 1 < len(self.items) else 'finish'
            return [(caps.g('enter'), nxt), ('esc', 'back'), ('H', 'home')]
        n = len(self.options())
        return [(f'1-{n}' if n > 1 else '1', 'answer'), ('esc', 'back'),
                ('H', 'home')]

    # -- input -------------------------------------------------------------

    def handle(self, key: K.Key):
        # Explicit rather than inherited: this screen deliberately swallows
        # every key it does not name, so that a stray letter cannot quit
        # mid-question. H has to be let through by hand.
        if key.name == 'H' and not key.ctrl and not key.alt:
            return ROOT
        if self.phase == 'feedback':
            if key.name in ('RET', 'SPC'):
                return self._advance()
            if key.name == 'ESC':
                return POP
            return STAY

        if key.name == 'ESC':
            return POP
        if self.started is None:
            self.started = self.clock()
        if key.name.isdigit() and key.name != '0':
            i = int(key.name) - 1
            if 0 <= i < len(self.options()):
                self._judge(i)
        return STAY

    def _judge(self, i: int) -> None:
        self.picked = i
        correct = (i == self.correct_index())
        qid = self.item.get('id', '?')
        self.state.record_answer(self.module.id, 'quiz', qid, correct)

        self.answered += 1
        if correct:
            self.right += 1
        self.last_correct = correct
        self.phase = 'feedback'
