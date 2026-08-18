"""The challenge engine: one task, three scaffolding levels, real verification.

**D6 in one screen.** Guided, Coached and Free are not three pieces of content,
they are one definition rendered at three frictions. Guided shows every step
with its hint. Coached shows the steps and keeps the hints behind a keypress.
Free shows only the one-sentence statement. Changing rigor changes what you
see, never what is checked.

**D21 in one keypress.** Press Enter and the trainer gives the terminal back,
drops you into real tmux, and waits. Do the work in the actual tool. Detach or
exit, and the trainer takes the terminal back and looks at what you did. This
is the same handover `git` uses for `$EDITOR`, which is why it needs no
explaining.

**D16 rule 4 and D8 together.** How this challenge will be checked is decided
and displayed *before* you start, never discovered at the moment of grading. A
challenge that wanted an adapter it cannot have says so up front and is marked
self-marked when you finish, and the record keeps that distinction forever.
"""

from __future__ import annotations

from .. import adapters as A
from .. import handover, install
from ..render import Caps, Span, Text, strip_markup, wrap, wrap_rich
from . import POP, STAY, Screen

RIGORS = ('guided', 'coached', 'free')
RIGOR_BLURB = {
    'guided': 'every step, with hints',
    'coached': 'the steps, hints on request',
    'free': 'the task only',
}

#: D6 orders these by scaffolding, most to least, and the picker walks that
#: order with the arrow keys. `free` is the default: handing someone the steps
#: before they have tried the task answers a question they have not asked yet,
#: and the whole point of a challenge is finding out whether you can do it.
#: Dropping to guided is one keypress away and always advertised.
DEFAULT_RIGOR = 'free'


class ChallengeScreen(Screen):
    """Brief, hand over, verify, report."""

    def __init__(self, module, challenge, state, now, handoff=None) -> None:
        self.module = module
        self.challenge = challenge
        self.state = state
        self.now = now
        self._handoff = handoff

        self.title = f'{module.title}: {challenge.get("title", challenge.get("id"))}'
        self.plan = A.plan_for(challenge)
        self.phase = 'brief'            # brief | result | selfmark
        self.show_hints = False
        self.passed: bool | None = None
        self.detail = ''
        self.attempts = 0
        self._adapter_ready = False
        #: Directory holding the `task` command for the current handover. Held
        #: on the screen rather than the adapter because it is hone's own
        #: scaffolding, not part of the sandbox being verified, and because
        #: `close` is the one place guaranteed to run on every way out.
        self._task_dir = None

    # -- rigor -------------------------------------------------------------

    @property
    def rigor(self) -> str:
        r = self.state.settings.get('rigor', DEFAULT_RIGOR)
        return r if r in RIGORS else DEFAULT_RIGOR

    def set_rigor(self, r: str) -> None:
        self.state.set_setting('rigor', r)

    def step_rigor(self, delta: int) -> None:
        """Move one along the scaffolding scale. Clamps rather than wraps.

        Wrapping would put `free` one press to the left of `guided`, so
        someone stepping towards more help would land on none at all. The ends
        are meaningful here, so they stop.
        """
        i = RIGORS.index(self.rigor)
        self.set_rigor(RIGORS[max(0, min(len(RIGORS) - 1, i + delta))])
        self.show_hints = False

    # -- content -----------------------------------------------------------

    @property
    def status(self) -> str:
        return self.plan.label

    def body(self, caps: Caps) -> list[Text]:
        if self.phase == 'result':
            return self._body_result(caps)
        if self.phase == 'selfmark':
            return self._body_selfmark(caps)
        return self._body_brief(caps)

    def _body_brief(self, caps: Caps) -> list[Text]:
        p = caps.palette
        c = self.challenge
        rows: list[Text] = [Text()]

        rows += wrap_rich(caps, str(c.get('goal', '')), caps.cols - 6, '  ',
                          p.fg, p.accent)
        rows.append(Text())

        # D16 rule 4: say how this gets checked before it starts, not after.
        rows.append(self._verification_line(caps))
        if self.plan.degraded:
            rows.append(Text().add(f'     {self.plan.reason}', p.dim))
            for tool in self._missing_tools():
                cmd = install.hint(tool)
                if cmd:
                    rows.append(Text().add(f'     {cmd}', p.accent))
        rows.append(Text())

        # What Enter is about to do, before it does it. The whole reason
        # this block exists: pressing Enter used to open nvim on top of the
        # app with no warning, no task in sight, and no way back that a
        # beginner could guess.
        happens = handover.what_happens(c, self.plan)
        if happens:
            rows.append(Text().add('  WHEN YOU PRESS ' + caps.g('enter'),
                                   p.accent2, bold=True))
            for text in happens:
                if not text:
                    rows.append(Text())
                elif text.startswith('    '):
                    rows.append(Text().add('    ' + text.strip(), p.accent))
                else:
                    rows += wrap_rich(caps, text, caps.cols - 8, '    ', p.muted,
                                      p.accent)
            rows.append(Text())

        # The label is a heading, not a fourth chip. Dim text sitting flush
        # against three selectable chips read as one of them, which made the
        # only word explaining what the row *is* look like something you could
        # switch to. Same treatment as the handover heading above, which is
        # this screen's existing convention for "this labels what follows".
        rows.append(Text().add('  RIGOR', p.accent2, bold=True)
                          .add(f'   {RIGOR_BLURB[self.rigor]}', p.dim))
        bar = Text().add('    ')
        for r in RIGORS:
            on = r == self.rigor
            bar.add(f' {r} ', p.bg if on else p.muted,
                    p.accent if on else None, bold=on)
            bar.add(' ')
        rows += [bar, Text()]

        if self.rigor == 'free':
            for row in wrap_rich(caps, str(c.get('free', c.get('goal', ''))),
                                 caps.cols - 6, '  ', p.fg, p.accent):
                for sp in row.spans:
                    sp.bold = True
                rows.append(row)
        else:
            for i, step in enumerate(c.get('steps') or (), 1):
                srows = wrap_rich(caps, str(step.get('instruction', '')),
                                  caps.cols - 10, '     ', p.fg, p.accent)
                if srows and srows[0].spans:
                    srows[0].spans[0] = Span(f'  {i}. ', p.accent, None, True)
                rows += srows
                hint = step.get('hint')
                if hint and (self.rigor == 'guided' or self.show_hints):
                    rows.append(Text().add('       ', p.dim)
                                      .add(str(hint), p.ok))
        return rows

    def _missing_tools(self) -> list[str]:
        """What this challenge wanted and could not find.

        Read from the adapter that was asked for, not the one in the plan:
        by the time a plan is degraded its adapter is None, and the whole
        point is to name the thing that is absent.
        """
        kind = (self.challenge.get('verify') or {}).get('kind')
        adapter = A.get(kind) if kind else None
        return install.missing(getattr(adapter, 'requires', ()))

    def _verification_line(self, caps: Caps) -> Text:
        p = caps.palette
        t = Text().add('  this will be  ', p.dim)
        if self.plan.kind == A.VERIFIED:
            t.add(f'{caps.g("check")} verified', p.ok, bold=True)
            t.add(' by reading your real session afterwards', p.dim)
        elif self.plan.kind == A.GRADED:
            t.add('checked', p.accent, bold=True).add(' in the app', p.dim)
        else:
            t.add('self-marked', p.warn, bold=True)
            t.add(' and you decide whether you did it', p.dim)
        return t

    def _body_result(self, caps: Caps) -> list[Text]:
        p = caps.palette
        rows = [Text(), Text()]
        if self.passed:
            rows.append(Text().add('  ' + caps.g('check') + '  ', p.ok, bold=True)
                              .add('done, and ', p.fg)
                              .add(A.LABELS[self.plan.kind], p.ok, bold=True))
        else:
            rows.append(Text().add('  ' + caps.g('cross') + '  ', p.err, bold=True)
                              .add('not there yet', p.fg, bold=True))
        if self.detail:
            rows += [Text()]
            for ln in wrap(strip_markup(self.detail), caps.cols - 8, '     '):
                rows.append(Text().add(ln, p.muted) if ln else Text())
        if not self.passed:
            rows += [Text(),
                     Text().add('     Nothing was lost. Go back in and finish it.',
                                p.dim)]
        rows.append(Text())
        rows.append(Text().add(f'     attempt {self.attempts}', p.dim))
        return rows

    def _body_selfmark(self, caps: Caps) -> list[Text]:
        p = caps.palette
        c = self.challenge
        rows = [Text(), Text().add('  Did you complete it?', p.fg, bold=True), Text()]
        for ln in wrap(strip_markup(str(c.get('free', c.get('goal', '')))),
                       caps.cols - 8, '     '):
            rows.append(Text().add(ln, p.muted) if ln else Text())
        rows += [Text(),
                 Text().add('     This one is on your honour: ', p.dim)
                       .add(self.plan.reason or 'nothing here can be read back',
                            p.warn),
                 Text(),
                 Text().add('     Answer honestly. A record that says you did '
                            'something', p.dim),
                 Text().add('     you did not is worse than no record.', p.dim)]
        return rows

    def hints(self, caps: Caps) -> list[tuple[str, str]]:
        if self.phase == 'result':
            out = [(caps.g('enter'), 'try again' if not self.passed else 'again'),
                   ('esc', 'back'), ('H', 'home'), ('q', 'quit')]
            return out
        if self.phase == 'selfmark':
            return [('y', 'yes, done'), ('n', 'not yet'), ('esc', 'back')]
        out = [(caps.g('enter'), 'start')]
        if self.rigor == 'coached':
            out.append(('h', 'hide hints' if self.show_hints else 'hints'))
        # The arrows are the advertised way to change rigor now; g/c/f stay as
        # direct jumps, the same bargain D19 strikes between arrow keys and
        # the 1-9 shortcuts everywhere else.
        out += [(caps.g('left') + caps.g('right'), 'rigor'),
                ('esc', 'back'), ('H', 'home'), ('q', 'quit')]
        return out

    # -- input -------------------------------------------------------------

    def handle(self, key):
        name = key.name

        if self.phase == 'selfmark':
            # No H here: this is a yes/no the student is in the middle of,
            # and an unadvertised escape that records nothing is worse than
            # making them answer or press Esc.
            if name in ('y', 'Y'):
                self._finish(True, 'you marked this done yourself')
                return STAY
            if name in ('n', 'N'):
                self._finish(False, 'you marked this not done')
                return STAY
            if name == 'ESC':
                self.phase = 'brief'
                return STAY
            return STAY

        if self.phase == 'result':
            if name == 'RET':
                self.phase = 'brief'
                return STAY
            if name == 'ESC':
                self._release()
                return POP
            return super().handle(key)

        if name == 'RET':
            self._start()
            return STAY
        if name == 'h' and self.rigor == 'coached':
            self.show_hints = not self.show_hints
            return STAY
        if name == 'Left':
            self.step_rigor(-1)
            return STAY
        if name == 'Right':
            self.step_rigor(1)
            return STAY
        if name in ('g', 'c', 'f'):
            self.set_rigor({'g': 'guided', 'c': 'coached', 'f': 'free'}[name])
            self.show_hints = False
            return STAY
        if name == 'ESC':
            self._release()
            return POP
        return super().handle(key)

    # -- running -----------------------------------------------------------

    def _start(self) -> None:
        """Hand the terminal over, then look at what happened (D21)."""
        self.attempts += 1
        adapter = self.plan.adapter
        spec = self.challenge.get('setup') or {}

        # The `task` command is built before the adapter branch on purpose. A
        # self-marked challenge still hands you a shell, its steps still scroll
        # away, and "there is no adapter" is a statement about verification
        # rather than about whether the student can still read the task.
        handover.discard(self._task_dir)
        self._task_dir = handover.task_helper(self._briefing())
        env = handover.task_env(self._task_dir)

        if adapter is not None:
            if not self._adapter_ready:
                # Set up once and keep it across retries: killing the session
                # someone half-built and making them start over is a punishment,
                # not feedback.
                try:
                    adapter.setup(spec)
                    self._adapter_ready = True
                except Exception as e:
                    self._finish(False, f'could not prepare the sandbox: {e}')
                    return
            # The task and the way out travel with the handover, so they
            # are still in front of the student once this screen is gone.
            spec = dict(spec)
            spec['brief'] = handover.inline(self.challenge, adapter.return_hint)
            # The whole briefing travels too, for the tools that can show it
            # beside the work. One that cannot ignores it and loses nothing.
            spec['steps'] = self._briefing()
            argv = adapter.handoff(spec)
            cwd = adapter.handoff_cwd(spec)
            env = {**adapter.handoff_env(spec), **env}
        else:
            argv, cwd = [], None

        if self._handoff is not None:
            self._handoff(argv, cwd, self._shell_brief(), env=env)

        if adapter is None:
            # Whatever the plan said, what happens next is self-marking, and
            # the record must say so: mark_challenge stores plan.kind, and a
            # 'graded' label on an honour-system answer is the exact
            # overstatement D8 exists to prevent.
            if self.plan.kind != A.SELF:
                self.plan = A.Plan(A.SELF, None, self.plan.reason)
            self.phase = 'selfmark'
            return

        try:
            obs = adapter.observe()
            # An adapter may report that it looked but cannot honestly grade
            # what it saw. Claiming a pass there would be worse than not
            # verifying at all, so it degrades and says why. See D8.
            if obs.data.get('cannot_verify'):
                self.plan = A.Plan(A.SELF, self.plan.adapter, obs.detail)
                self.phase = 'selfmark'
                return
            expect = (self.challenge.get('verify') or {}).get('expect') or {}
            ok, detail = adapter.check(expect, obs.data)
        except Exception as e:
            # D18: an adapter that breaks mid-run degrades, it does not crash.
            self.plan = A.Plan(A.SELF, None, f'the adapter failed: {e}')
            self.phase = 'selfmark'
            return
        self._finish(ok, detail)

    def _briefing(self) -> list[str]:
        """Full briefing for a handover, at the rigor the student chose.

        Built once and used three ways: printed into a shell, opened in a
        second window by an editor, and written into the `task` command. They
        used to be separate code paths, which meant the words could differ
        depending on which tool you were handed.
        """
        adapter = self.plan.adapter
        return handover.briefing(
            self.challenge, self.rigor, self.show_hints,
            adapter.return_hint if adapter is not None else '')

    def _shell_brief(self) -> list[str]:
        """What a shell handover prints, which is the briefing plus its own way
        of getting it back. Only a shell needs telling: an editor shows the
        same text in a window and nothing scrolls it away.
        """
        out = self._briefing()
        if self._task_dir is not None:
            out.append('')
            out.append(f'Type  {handover.TASK_CMD}  to see this again.')
        return out

    def _finish(self, ok: bool, detail: str) -> None:
        self.passed = ok
        self.detail = detail
        self.phase = 'result'
        if ok:
            self.state.mark_challenge(self.module.id, self.challenge['id'],
                                      self.rigor, self.plan.kind, self.now)
            self._release()
        elif self.plan.kind == A.SELF:
            # Saying "not yet" against your own interest is worth recording,
            # and the Honest achievement exists to say so out loud.
            rec = self.state.item(self.module.id, 'challenges',
                                  self.challenge['id'])
            rec['declined'] = rec.get('declined', 0) + 1
            self.state.dirty = True

    def close(self) -> None:
        self._release()

    def _release(self) -> None:
        """Tear the sandbox down. Safe to call more than once, per D1."""
        if self._adapter_ready and self.plan.adapter is not None:
            try:
                self.plan.adapter.teardown()
            except Exception:
                pass
            self._adapter_ready = False
        # hone's own scaffolding, outside the sandbox and so not covered by
        # the adapter's teardown. D1 counts it the same: we made it, we remove
        # it, on every way out including the ones nobody plans for.
        handover.discard(self._task_dir)
        self._task_dir = None
