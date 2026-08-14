"""The help screen, and the first-run tour. Both are D19 promises.

`?` is advertised in the footer of nearly every screen. It did nothing for the
whole build, which is precisely the D19 rule 4 failure the footer contract
exists to prevent: a key the student was told about that does not work. Worse
than an undocumented key, because it teaches that the footer lies.

The tour is the other half. D19 says a first run should not drop someone on the
home screen cold, and `state.settings['seen_tour']` was reserved for it and
never read. Three cards, skippable, never shown again unless asked for.

Both are the same shape, so they share one screen: a list of cards you page
through. The tour is the help screen started at card zero with a flag that
records having seen it.
"""

from __future__ import annotations

from ..config import EXIT_CHORD
from ..render import Caps, Text, wrap_rich
from . import POP, STAY, Screen


def _card(title: str, body: str, rows: list[tuple[str, str]]) -> dict:
    return {'title': title, 'body': body, 'rows': rows}


#: The tour: what someone needs before the home screen makes sense.
TOUR = [
    _card('Three ways to learn each tool',
          'Every tool has the same three views, and you move between them with '
          'Tab. Which one you want depends on what you are trying to do right '
          'now, not on where you are in a course.',
          [('Walkthrough', 'read it, when the thing makes no sense yet'),
           ('Practice', 'do a real task, with as much help as you ask for'),
           ('Drill', 'grind the keys until you stop having to think'),
           ('', 'esc goes back one screen, H goes straight home')]),
    _card('Your pace is yours',
          'Nothing here is scheduled and nothing is ever owed. Pick the tool '
          'you actually want, work at it for as long as you feel like, and '
          'put it down. Coming back after a month costs you nothing, and no '
          'part of this app will mention that you did.',
          [('', 'no streak, no daily target, no reminders'),
           ('', 'the bar is how much you have met, not a deadline'),
           ('', 'every tool stands on its own: start wherever you like'),
           ('n', 'reread the notes you left yourself')]),
    _card('It checks your real work',
          'Where it can, hone hands you the actual tool and then reads back '
          'what you did. Where it cannot, it says so and takes your word for '
          'it. Those are never blurred.',
          [('verified', 'a real tool confirmed it'),
           ('checked', 'graded exactly, inside the app'),
           ('self-marked', 'you decided, and it is recorded as such'),
           ('', 'it tells you what opens and how to get back before it does'),
           ('', 'and the task follows you into the tool')]),
]

#: The help screen: what every key does, available from anywhere with `?`.
HELP = [
    _card('Moving around',
          'The footer at the bottom of every screen always lists the keys that '
          'work on that screen. If a key is not in the footer, it does '
          'nothing.',
          [('up / down, j / k', 'move the cursor'),
           ('enter, l', 'open the selected thing'),
           ('tab', 'switch between a tool\'s three views'),
           ('1-9', 'jump straight to that item'),
           ('esc', 'back one screen, or quit from the home screen'),
           ('H', 'straight back to the home screen, however deep you are'),
           ('q', 'quit from anywhere'),
           ('?', 'this screen')]),
    _card('Drills',
          'A drill either takes the keyboard or asks you to type an answer, '
          'and the frame tells you which. When it has the keyboard the border '
          'changes colour and says CAPTURING, because then almost every key is '
          'an answer.',
          [(EXIT_CHORD, 'always leaves a drill, in either mode'),
           ('any key', 'answers, while capturing'),
           ('enter', 'submits, then moves on'),
           ('n', 'note why you missed it; it comes back with the drill'),
           ('', 'the dots show how many keystrokes it is waiting for')]),
    _card('Practice and rigor',
          'A challenge is one task at three levels of help. Change the level '
          'any time; it changes what you see and never what is checked.',
          [('g', 'guided: every step, with hints'),
           ('c', 'coached: the steps, hints on request with h'),
           ('f', 'free: the task only'),
           ('enter', 'hand the terminal to the real tool, then come back'),
           ('', 'the brief says what opens and how to get back out of it'),
           ('', 'the task stays visible inside the tool while you work')]),
    _card('Where your progress lives',
          'One JSON file, and you can move it between machines. Nothing is '
          'sent anywhere and nothing outside that file and its own scratch '
          'directories is ever written.',
          [('hone --export f.json', 'write your progress to a file'),
           ('hone --import f.json', 'replace it from one'),
           ('hone --sync f.json', 'remember a file and keep it current'),
           ('hone --list', 'what is installed, and what can be verified'),
           ('hone --sheet ssh', 'print one tool as a reference card'),
           ('hone --doctor', 'why something degrades on this machine'),
           ('hone --reset', 'erase progress and start over, backup written'),
           ('hone --ascii', 'no box drawing, for a plain terminal'),
           ('hone --no-splash', 'skip the launch and exit animations'),
           ('hone --no-split', 'never open a second tmux pane')]),
]


class HelpScreen(Screen):
    """Paged cards. Used for both `?` and the first-run tour."""

    def __init__(self, cards=None, state=None, now=None,
                 tour: bool = False) -> None:
        self.cards = list(cards if cards is not None else HELP)
        self.state = state
        self.now = now
        self.tour = tour
        self.index = 0
        self.title = 'Welcome to hone' if tour else 'Help'

    @property
    def card(self) -> dict:
        return self.cards[self.index] if self.cards else {}

    @property
    def status(self) -> str:
        return f'{self.index + 1} of {len(self.cards)}' if self.cards else ''

    def body(self, caps: Caps) -> list[Text]:
        p = caps.palette
        c = self.card
        if not c:
            return [Text().add('  No help is available.', p.muted)]

        rows: list[Text] = [Text(),
                            Text().add('  ' + c['title'], p.accent, bold=True),
                            Text()]
        rows += wrap_rich(caps, c['body'], caps.cols - 6, '  ', p.fg, p.accent)
        rows.append(Text())

        width = max((len(k) for k, _ in c['rows']), default=0)
        for key, meaning in c['rows']:
            row = Text().add('    ')
            row.add(f'{key:<{width}}  ', p.accent if key else p.dim, bold=bool(key))
            row.add(meaning, p.muted if key else p.dim)
            rows.append(row)

        rows.append(Text())
        dots = Text().add('  ')
        for i in range(len(self.cards)):
            dots.add(caps.g('dot_on') if i == self.index else caps.g('dot_off'),
                     p.accent if i == self.index else p.border)
        rows.append(dots)
        return rows

    def hints(self, caps: Caps) -> list[tuple[str, str]]:
        last = self.index + 1 >= len(self.cards)
        nxt = ('start' if self.tour else 'done') if last else 'next'
        out = [(caps.g('enter'), nxt)]
        if self.index:
            out.append(('h', 'back'))
        out.append(('esc', 'skip' if self.tour else 'close'))
        return out

    def _finish(self):
        # Recorded on the way out either way, so a skipped tour is still a
        # seen tour. Being shown it again after choosing to skip would be
        # its own small insult.
        if self.tour and self.state is not None:
            self.state.set_setting('seen_tour', True)
        return POP

    def handle(self, key):
        name = key.name
        if name in ('RET', 'SPC', 'Right', 'l'):
            if self.index + 1 < len(self.cards):
                self.index += 1
                return STAY
            return self._finish()
        if name in ('h', 'Left') and self.index:
            self.index -= 1
            return STAY
        if name == 'ESC':
            return self._finish()
        if name == 'q' and not self.tour:
            return super().handle(key)
        return STAY
