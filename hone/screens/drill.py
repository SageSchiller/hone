"""Drills, in two modes, and D19a.

**Capture mode** (`type: 'keys'`) takes the keyboard and grades the actual
keystroke. It is the mode that builds motor memory, and it is what vim and Doom
will use.

**Text mode** (`type: 'recall'` and `type: 'command'`) asks you to type the
answer instead. tmux needs this and the reason is concrete: tmux binds `C-b`,
so if the trainer is running inside tmux the prefix never reaches it, and
outside tmux a captured prefix drills the chord with none of its context.
Production practice for tmux arrives in Phase 2 through verified challenges,
where you drive a real session and the adapter reads `tmux list-panes`.

Recall answers are graded by **parsing the typed text back into keys**, so
`C-b "` and `C-b S-'` are both accepted and the same authored `keys` list
serves either mode. Nothing has to be written twice.

D19a applies only in capture mode, because that is the only mode that takes
`Esc` and `q` away from you. In text mode Esc leaves normally, and the frame
stays quiet to signal the difference.

**Orientation.** A capture drill is the most abstract screen in the app: no
file, no cursor, no shell, just a sentence and a keyboard that has been taken
away from you. Two things are shown to fix that, and both come from data the
app already had and was keeping to itself.

*Which world you are in*: a module states it once (`context`), because "delete
the line the cursor is on" means nothing without "you are in vim, in normal
mode, on a line of text".

*How many keystrokes to press*: capture mode judges as soon as the expected
number of keys has arrived, so a student who does not know that number is
pressing keys blind and being graded at a moment they cannot predict. The
slots are drawn empty and fill in as you type. It is a hint, and it is the
right trade: the alternative is a mechanic the app knows and hides.

**Notes.** `n` during feedback attaches a line to the drill, which is where the
useful thought actually happens: the moment you get something wrong you know
*why* you got it wrong, and thirty seconds later you do not. The note comes
back on the prompt every time the drill does.

This is why capture-mode feedback no longer advances on any key. It used to,
and `n` is a letter, so the two could not coexist. Requiring Enter also makes
the two modes agree, which is worth more than the saved keystroke.
"""

from __future__ import annotations

import time

from .. import adapters as A
from .. import keys as K
from ..grading import evaluate_regex
from ..config import EXIT_CHORD
from ..render import Caps, Text, dots, wrap, wrap_rich
from . import POP, STAY, Screen

CAPTURE_TYPES = ('keys',)

#: Drill types graded by running the real tool against a fixture, mapped to
#: the adapter that does it and the language to grade in. These are the only
#: drill types that leave the process, and every one of them degrades to a
#: text comparison when its tool is missing or D26's read-only mode is on.
ORACLE_TYPES = {
    'bpf': ('pcap', 'capture'),
    'display': ('pcap', 'display'),
    'pwsh': ('pwsh', None),
}

TEXT_TYPES = ('recall', 'command', 'regex', *ORACLE_TYPES)


def normalise_command(s: str) -> str:
    """Collapse whitespace. Case is preserved: shell commands are case sensitive."""
    return ' '.join(s.split())


class DrillScreen(Screen):
    """Runs a list of drills in order, in whichever mode each one declares."""

    def __init__(self, module, drills, index, state, now,
                 kitty: bool = False, exit_chord: str = EXIT_CHORD,
                 clock=time.monotonic) -> None:
        self.module = module
        self.drills = list(drills)
        self.index = max(0, min(index, len(self.drills) - 1)) if self.drills else 0
        self.state = state
        self.now = now
        self.kitty = kitty
        self.exit_chord = exit_chord
        self.clock = clock

        self.title = f'{module.title} drill'
        self.collected: list[K.Key] = []
        self.typed = ''
        self.phase = 'prompt'          # prompt | feedback | note
        self.note_buf = ''
        self.last_correct: bool | None = None
        self.last_note = ''
        #: True when the last answer was graded by really running it. None for
        #: drill types where the question does not arise. D8 requires the two
        #: never look alike, so the feedback row reads this rather than
        #: assuming.
        self.last_verified: bool | None = None
        self.started: float | None = None
        self.answered = 0
        self.right = 0

    # -- current drill -----------------------------------------------------

    @property
    def drill(self) -> dict:
        return self.drills[self.index] if self.drills else {}

    @property
    def mode(self) -> str:
        return ('capture' if self.drill.get('type', 'keys') in CAPTURE_TYPES
                else 'text')

    @property
    def capturing(self) -> bool:
        """D19a's heavy frame belongs only to the mode that took your keyboard."""
        return self.mode == 'capture' and self.phase == 'prompt'

    def expected(self) -> list[list[K.Key]]:
        d = self.drill
        out = []
        if d.get('keys'):
            out.append(K.parse_seq(d['keys']))
        for alt in d.get('accepts') or ():
            if isinstance(alt, (list, tuple)):
                out.append(K.parse_seq(alt))
        return out

    def expected_commands(self) -> list[str]:
        """Accepted answers for the typed-string drill types.

        For `command` these are the alternatives that count as correct. For
        `regex` only the first is used, and only for display: a regex is graded
        by behaviour, so the reference pattern is an example rather than a key.
        """
        d = self.drill
        out = []
        if d.get('answer'):
            out.append(normalise_command(str(d['answer'])))
        for alt in d.get('accepts') or ():
            if isinstance(alt, str):
                out.append(normalise_command(alt))
        return out

    def answer_text(self) -> str:
        """What to show as the right answer during feedback.

        For a regex this is *a* correct answer rather than *the* one, since
        grading accepts any pattern with the right behaviour. The same is true
        of every oracle type: the reference filter is one spelling of the
        answer, not the only one that passes.
        """
        if self.drill.get('type') in ('command', 'regex', *ORACLE_TYPES):
            cmds = self.expected_commands()
            return cmds[0] if cmds else '?'
        seqs = self.expected()
        return K.describe(seqs[0]) if seqs else '?'

    def saved_note(self) -> str:
        did = self.drill.get('id')
        return self.state.note(self.module.id, 'drills', did) if did else ''

    def target_len(self) -> int:
        return min((len(s) for s in self.expected()), default=0)

    def unanswerable(self) -> list[str]:
        """Chords this terminal cannot send (D11). Only capture mode is at risk.

        In text mode you type `C-i` as three characters, so the terminal's
        inability to send the real chord does not matter.
        """
        if self.kitty or self.mode == 'text':
            return []
        out: list[str] = []
        for seq in self.expected():
            out.extend(K.ambiguity_for(seq))
        return sorted(set(out))

    # -- content -----------------------------------------------------------

    @property
    def status(self) -> str:
        return (f'{self.exit_chord} to leave' if self.mode == 'capture'
                else f'{self.index + 1} of {len(self.drills)}')

    def body(self, caps: Caps) -> list[Text]:
        p = caps.palette
        d = self.drill
        if not d:
            return [Text().add('    No drills in this module yet.', p.muted)]

        rows: list[Text] = [Text()]

        if self.mode == 'capture':
            banner = Text().add('  ')
            banner.add(' CAPTURING KEYS ', p.bg, p.warn, bold=True)
            banner.add('   every keypress is an answer except ', p.muted)
            banner.add(self.exit_chord, p.warn, bold=True)
            rows += [banner, Text()]

        head = Text().add(f'  {self.module.title} ', p.dim)
        head.add(f'{caps.g("bullet")} drill {self.index + 1} of {len(self.drills)}   ',
                 p.dim)
        head.spans.extend(dots(caps, self.right, len(self.drills)).spans)
        rows += [head, Text()]

        context = d.get('context') or getattr(self.module, 'context', '')
        if context and self.phase == 'prompt':
            rows += wrap_rich(caps, str(context), caps.cols - 6, '  ', p.dim,
                              p.muted)
            rows.append(Text())

        for row in wrap_rich(caps, str(d.get('prompt', d.get('id', ''))),
                             caps.cols - 6, '  ', p.fg, p.accent):
            for sp in row.spans:
                sp.bold = True
            rows.append(row)
        rows.append(Text())

        saved = self.saved_note()
        if saved and self.phase != 'note':
            mark = '  ' + caps.g('note') + ' '
            for ln in wrap(saved, caps.cols - 8, ' ' * len(mark)):
                rows.append(Text().add(mark + ln.strip() if ln.strip() else '',
                                       p.accent2))
                mark = ' ' * len(mark)
            rows.append(Text())

        shown = (K.describe(self.collected) if self.mode == 'capture'
                 and self.collected else
                 (self.typed if self.mode == 'text' else ''))
        entry = Text().add('  ' + caps.g('arrow') + ' ', p.accent)
        entry.add(shown, p.fg, bold=True)
        if self.phase == 'prompt':
            entry.add('_', p.accent, bold=True)
        # Empty slots for the keystrokes still expected. Capture mode grades
        # the moment the last one arrives, so hiding the count means being
        # graded at a moment you could not predict.
        want = self.target_len() if self.mode == 'capture' else 0
        if want and self.phase == 'prompt':
            # The cursor IS the next slot, so only the ones after it are
            # drawn. Counting it twice showed three positions for two keys.
            left = max(0, want - len(self.collected) - 1)
            if left:
                entry.add(' ' + ' '.join(caps.g('slot') * 1 for _ in range(left)),
                          p.border)
            entry.add(f'   {want} keystroke{"" if want == 1 else "s"}', p.dim)
        rows.append(entry)

        if d.get('type') == 'regex':
            rows.append(Text())
            for label, key, colour in (('must match', 'match', p.ok),
                                       ('must not', 'reject', p.err)):
                for subject in (d.get(key) or ()):
                    rows.append(Text().add(f'    {label:<11}', p.dim)
                                      .add(str(subject), colour))
                label = ''
            if d.get('flags'):
                rows.append(Text().add('    flags      ', p.dim)
                                  .add(str(d['flags']), p.accent))
        elif self.mode == 'text' and self.phase == 'prompt':
            hint = ('type the command' if d.get('type') == 'command'
                    else 'type the keys, separated by spaces')
            rows.append(Text().add(f'     {hint}', p.dim))

        for warn in self.unanswerable():
            rows += [Text(), Text().add('  ! ', p.warn, bold=True)
                                   .add(f'this terminal cannot send {warn}', p.warn)]

        if self.phase == 'feedback':
            rows.append(Text())
            if self.last_correct:
                rows.append(Text().add('  ' + caps.g('check') + ' correct',
                                       p.ok, bold=True))
            else:
                rows.append(Text().add('  ' + caps.g('cross') + ' not that. ',
                                       p.err, bold=True)
                                  .add('The answer is ', p.muted)
                                  .add(self.answer_text(), p.accent, bold=True))
            if self.last_verified is not None:
                # D8: which of the three tiers just applied, in the same words
                # the challenge screen uses, every single time.
                label, colour = (('verified', p.ok) if self.last_verified
                                 else ('checked', p.muted))
                rows.append(Text().add('    ' + label, colour, bold=True))
            if self.last_note:
                rows.append(Text().add(f'    {self.last_note}', p.dim))
            teach = d.get('teach')
            if teach:
                rows.append(Text())
                rows += wrap_rich(caps, str(teach), caps.cols - 8, '    ', p.dim,
                                  p.accent)

        if self.phase == 'note':
            rows += [Text(),
                     Text().add('  YOUR NOTE', p.accent2, bold=True),
                     Text().add('    why you missed it, or what finally made '
                                'it stick', p.dim),
                     Text(),
                     Text().add('  ' + caps.g('arrow') + ' ', p.accent)
                           .add(self.note_buf, p.fg, bold=True)
                           .add('_', p.accent, bold=True)]
        return rows

    def hints(self, caps: Caps) -> list[tuple[str, str]]:
        """Text mode never advertises `q quit`.

        In text mode `q` is a letter you are trying to type, so a footer
        offering it as an exit would be describing a key that does something
        else. That is the D19 rule 4 failure, and the harness caught exactly
        this the first time text mode shipped.
        """
        nxt = 'next drill' if self.index + 1 < len(self.drills) else 'finish'
        if self.phase == 'note':
            return [(caps.g('enter'), 'save note'), ('esc', 'cancel'),
                    (self.exit_chord, 'leave')]
        note = 'edit note' if self.saved_note() else 'add note'
        if self.phase == 'feedback':
            if self.mode == 'capture':
                # Not 'any key' any more: `n` is a letter, and a footer that
                # says any key while one key means something else is the
                # rule 4 failure this contract exists to catch.
                return [(caps.g('enter'), nxt), ('n', note),
                        (self.exit_chord, 'leave')]
            return [(caps.g('enter'), nxt), ('n', note), ('esc', 'back')]
        if self.mode == 'capture':
            return [(self.exit_chord, 'leave'), ('keys', 'answer the prompt')]
        what = ('pattern' if self.drill.get('type') == 'regex' else 'answer')
        return [(caps.g('enter'), f'submit {what}'), ('esc', 'back'),
                (self.exit_chord, 'leave')]

    # -- input -------------------------------------------------------------

    @property
    def escape_key(self) -> str:
        """Capture mode reserves a chord because Esc is an answer there.

        Text mode has no such problem, so Esc behaves like everywhere else and
        the footer says so. The reserved chord keeps working in both.
        """
        return self.exit_chord if self.mode == 'capture' else 'ESC'

    def handle(self, key: K.Key):
        # D19a: always first, in every mode and phase, so no drill can shadow it.
        if K.unparse(key) == self.exit_chord:
            return POP
        if self.phase == 'note':
            return self._handle_note(key)
        if self.mode == 'capture':
            return self._handle_capture(key)
        return self._handle_text(key)

    def _handle_note(self, key: K.Key):
        if key.name == 'RET':
            did = self.drill.get('id')
            if did:
                self.state.set_note(self.module.id, 'drills', did,
                                    self.note_buf)
                self.state.dirty = True
            self.phase = 'feedback'
            return STAY
        if key.name == 'ESC':
            self.phase = 'feedback'      # cancel: the saved note is untouched
            return STAY
        if key.name == 'BSP':
            self.note_buf = self.note_buf[:-1]
            return STAY
        if key.name == 'SPC' and not key.ctrl and not key.alt:
            self.note_buf += ' '
            return STAY
        if len(key.name) == 1 and not key.ctrl and not key.alt:
            self.note_buf += key.name
            return STAY
        # Anything else is ignored rather than passed on: while typing a note
        # every stray key would otherwise quit.
        return STAY

    def _open_note(self):
        self.note_buf = self.saved_note()
        self.phase = 'note'
        return STAY

    def _handle_capture(self, key: K.Key):
        # No `?` shortcut here on purpose: while capturing, `?` is an answer,
        # and the footer does not advertise help for exactly that reason.
        if self.phase == 'feedback':
            if key.name == 'n' and not key.ctrl and not key.alt:
                return self._open_note()
            if key.name in ('RET', 'SPC'):
                self._advance()
            return STAY
        if not self.drills:
            return STAY
        self._start_clock()
        self.collected.append(key)
        if len(self.collected) >= self.target_len() > 0:
            self._judge_keys()
        return STAY

    def _handle_text(self, key: K.Key):
        if self.phase == 'feedback':
            if key.name == 'n' and not key.ctrl and not key.alt:
                return self._open_note()
            if key.name in ('RET', 'SPC'):
                self._advance()
                return STAY
            if key.name == 'ESC':
                return POP
            # Nothing else, deliberately: falling through to the base handler
            # would make undeclared letters quit, which is the same rule 4 trap
            # the footer above avoids.
            return STAY

        if key.name == 'RET':
            if self.typed.strip():
                self._judge_text()
            return STAY
        if key.name == 'BSP':
            self.typed = self.typed[:-1]
            return STAY
        if key.name == 'SPC' and not key.ctrl and not key.alt:
            self._start_clock()
            self.typed += ' '
            return STAY
        if len(key.name) == 1 and not key.ctrl and not key.alt:
            self._start_clock()
            self.typed += key.name
            return STAY
        return super().handle(key)

    def _start_clock(self) -> None:
        # Kept only so a drill knows it has been begun; nothing reads the
        # elapsed time any more (D24).
        if self.started is None:
            self.started = self.clock()

    # -- judging -----------------------------------------------------------

    def _judge_keys(self) -> None:
        self._record(any(self.collected == seq for seq in self.expected()))

    def _judge_text(self) -> None:
        note = ''
        self.last_verified = None
        dtype = self.drill.get('type')
        if dtype == 'regex':
            # Graded by behaviour: it must match every positive and reject
            # every negative. Comparing to a reference pattern would fail
            # people who were right in a different shape.
            res = evaluate_regex(self.typed,
                                 list(self.drill.get('match') or ()),
                                 list(self.drill.get('reject') or ()),
                                 self.drill.get('flags'))
            correct, note = res.ok, res.detail
        elif dtype in ORACLE_TYPES:
            correct, note, self.last_verified = self._judge_oracle()
        elif dtype == 'command':
            correct = normalise_command(self.typed) in self.expected_commands()
        else:
            try:
                got = K.parse_seq(self.typed.split())
                correct = any(got == seq for seq in self.expected())
            except K.KeyError_ as e:
                correct, note = False, f'could not read that as keys: {e}'
        self._record(correct)
        self.last_note = note

    def close(self) -> None:
        """Tear down any oracle sandbox this drill run created.

        The challenge screen learned this the hard way and the comment on
        `Screen.close` records it: a screen cannot see the `q` that quits the
        app, so anything held outside the process leaks unless it is released
        here. Oracle drills write a capture file or a sample tree on first
        answer, which makes this screen the second one that holds something.
        """
        for name in {n for n, _ in ORACLE_TYPES.values()}:
            adapter = A.get(name)
            if adapter is not None:
                try:
                    adapter.teardown()
                except Exception:
                    pass    # teardown failure must never mask the real exit

    def _judge_oracle(self) -> tuple[bool, str, bool]:
        """Run the answer against the real tool. Returns (ok, note, verified).

        The three ways this does not run are all the same answer to the
        student: it falls back to comparing the text of your answer with the
        reference, and says that is what it did. An unlabelled text comparison
        dressed as a real run is exactly the D8 overstatement that makes a
        trainer untrustworthy, and it is worse here than anywhere else,
        because the entire promise of these drills is that they ran.
        """
        name, language = ORACLE_TYPES[self.drill['type']]
        reference = str(self.drill.get('answer', ''))

        if A.read_only():
            return (*self._judge_by_text(reference),
                    False)
        adapter = A.get(name)
        if adapter is None or not adapter.available():
            return (*self._judge_by_text(reference), False)
        if language and hasattr(adapter, 'grades') and not adapter.grades(language):
            return (*self._judge_by_text(reference), False)

        try:
            if language:
                verdict = adapter.evaluate(self.typed, reference, language)
            else:
                verdict = adapter.evaluate(self.typed, reference)
        except Exception as e:
            # D18: an adapter that breaks mid-drill degrades, it does not crash.
            ok, note = self._judge_by_text(reference)
            return ok, f'{note} (the checker failed: {e})', False
        return verdict.ok, verdict.detail, True

    def _judge_by_text(self, reference: str) -> tuple[bool, str]:
        """The degraded comparison, and it always says it is degraded."""
        why = ('read and drill only mode is on'
               if A.read_only() else 'the tool is not installed here')
        ok = normalise_command(self.typed) in self.expected_commands()
        return ok, f'compared as text, not run: {why}'

    def _record(self, correct: bool) -> None:
        """Log the attempt. Two counters, and that is all.

        This used to compute an SM-2 interval from the answer and how long it
        took, so the drill came back on a date. D24 removed the schedule: how
        fast you were is interesting for a moment and is not the app's
        business to keep, and nothing is owed on any day.
        """
        did = self.drill.get('id', '?')
        self.state.record_answer(self.module.id, 'drills', did, correct)

        self.answered += 1
        if correct:
            self.right += 1
        self.last_correct = correct
        self.last_note = ''
        self.phase = 'feedback'

    def _advance(self) -> None:
        self.collected = []
        self.typed = ''
        self.note_buf = ''
        self.last_verified = None
        self.started = None
        self.last_correct = None
        self.last_note = ''
        self.phase = 'prompt'
        if self.index + 1 < len(self.drills):
            self.index += 1
