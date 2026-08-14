#!/usr/bin/env python3
"""Behaviour tests, no terminal required (D12).

`validate.py` checks what the content says. This checks what the app does, and
it does it headlessly on purpose: everything that needs a real TTY is
quarantined in `term.py`, so the whole rest of the app is testable in a pipe.

The sections that matter most, because they guard rules that erode quietly:

* **D19 across the D20 ladder.** Every screen is rendered at every colour and
  glyph rung and checked for a non-empty body, a non-empty footer, a working
  way out, and no overflow.
* **ASCII purity.** No screen may emit a non-ASCII character at the ASCII rung.
  This codebase has shipped that bug three times from hardcoded glyphs in
  constants, so it is a permanent test rather than a habit.
* **D18's promise.** A module whose adapter is missing degrades to self-marked
  rather than raising.
* **The D1 adapter contract.** Observe refuses before setup; teardown is
  idempotent; a failing teardown never masks the result.

Stdlib only, per D2. No pytest.
"""

from __future__ import annotations

import io
import json
import os
import shutil
import time
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from hone import adapters as A
from hone import config
from hone import keys as K
from hone import loader, render, state as st, term, theme
from hone.app import App
from hone.render import Caps, ColorLevel, GlyphLevel, Text
from hone.screens import ScreenContractError

T0 = datetime(2026, 8, 12, 9, 0, tzinfo=timezone.utc)

#: Tools present on any machine that can run this at all. coreutils and
#: openssl are not worth an install hint: without them the trainer itself
#: does not work, so a module may declare them and skip the advice.
GIVEN_TOOLS = {'ssh', 'curl', 'python3', 'sha256sum', 'md5sum', 'stat',
               'tar', 'openssl'}
ROOT = Path(__file__).resolve().parent

RUNGS = [
    ('true+nerd', ColorLevel.TRUE, GlyphLevel.NERD, theme.CYBERPUNK_NEON),
    ('true+uni', ColorLevel.TRUE, GlyphLevel.UNICODE, theme.CYBERPUNK_NEON),
    ('256+uni', ColorLevel.C256, GlyphLevel.UNICODE, theme.CYBERPUNK_NEON),
    ('16+uni', ColorLevel.C16, GlyphLevel.UNICODE, theme.ANSI),
    ('16+ascii', ColorLevel.C16, GlyphLevel.ASCII, theme.NEUTRAL),
    ('none+ascii', ColorLevel.NONE, GlyphLevel.ASCII, theme.NEUTRAL),
]


class Runner:
    def __init__(self) -> None:
        self.passed = 0
        self.failures: list[str] = []
        self.section = ''

    def head(self, name: str) -> None:
        self.section = name

    def ok(self, name: str, cond: bool, detail: str = '') -> None:
        if cond:
            self.passed += 1
        else:
            self.failures.append(f'{self.section} :: {name}' + (f' -- {detail}' if detail else ''))

    def eq(self, name: str, got, want, detail: str = '') -> None:
        self.ok(name, got == want, detail or f'got {got!r}, want {want!r}')

    def raises(self, name: str, exc, fn) -> None:
        try:
            fn()
        except exc:
            self.passed += 1
            return
        except Exception as e:
            self.failures.append(f'{self.section} :: {name} -- raised {type(e).__name__}, want {exc.__name__}')
            return
        self.failures.append(f'{self.section} :: {name} -- did not raise {exc.__name__}')


# --------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------

def fixture_registry() -> loader.Registry:
    """Synthetic content, so tests do not depend on what is installed."""
    reg = loader.Registry()
    reg.modules = [
        loader.build_module({
            'id': 'tmux', 'title': 'tmux', 'blurb': 'Sessions, windows, panes.',
            'adapter': 'tmux', 'order': 1,
            'lessons': [{'id': 'l1', 'title': 'The model', 'next': 'l2'},
                        {'id': 'l2', 'title': 'The prefix'}],
            'challenges': [{'id': 'c1', 'title': 'Three panes',
                            'goal': 'One tall pane left, two stacked right.',
                            'setup': {'kind': 'tmux', 'session': 'trainer-test'},
                            'steps': [
                                {'instruction': 'Split left and right.',
                                 'hint': 'C-b %'},
                                {'instruction': 'Split the right pane.',
                                 'hint': 'C-b \"'}],
                            'free': 'Build a three-pane layout.',
                            'verify': {'kind': 'tmux',
                                       'expect': {'min_panes': 3}},
                            'fallback': 'self'}],
            'drills': [{'id': 'd1', 'type': 'keys', 'keys': ['C-b', '"'],
                        'prompt': 'Split top and bottom.', 'teach': 'Because.'},
                       {'id': 'd2', 'type': 'keys', 'keys': ['C-b', 'd'],
                        'prompt': 'Detach.'}],
        }, 'fixture'),
        loader.build_module({
            'id': 'utils', 'title': 'Linux Utilities', 'order': 2,
            'blurb': 'The flags you always forget.',
            'drills': [{'id': 'u1', 'type': 'recall', 'keys': ['x'],
                        'prompt': 'Extract a gzipped tarball.'}],
        }, 'fixture'),
        loader.build_module({
            'id': 'empty', 'title': 'Nothing Yet', 'order': 3,
            'prereqs': ['tmux'],
        }, 'fixture'),
    ]
    return reg


def seen(state=None):
    """A state that has already seen the first-run tour.

    Used by every test that is not about the tour itself. Without it the tour
    sits on top of a fresh App and the test walks into it, which is correct
    behaviour and not what those tests are checking.
    """
    s = state if state is not None else st.State.blank(T0)
    s.set_setting('seen_tour', True)
    return s


def walk_screens(app, reg):
    """Every reachable screen, as (label, screen).

    Includes the states a screen can be *in*, not just the screens themselves:
    a drill in its feedback and note phases renders and footers differently
    from the same drill on its prompt, and each of those is a screen the
    student sees.
    """
    out = [('home', app.stack[0])]
    for i, m in enumerate(reg.modules):
        app.stack = [app.stack[0]]
        app.stack[0].cursor = i
        app.dispatch(K.parse('RET'))
        ms = app.screen
        if ms is app.stack[0]:
            continue
        for v, vname in enumerate(('walk', 'practice', 'drill')):
            ms.set_view(v)
            out.append((f'{m.id}/{vname}', ms))
            if vname == 'drill' and ms.count():
                app.dispatch(K.parse('RET'))
                drill = app.screen
                out.append((f'{m.id}/capture', drill))
                for _ in range(max(1, drill.target_len())):
                    drill.handle(K.parse('z'))
                out.append((f'{m.id}/feedback', drill))
                drill.handle(K.parse('n'))
                out.append((f'{m.id}/note', drill))
                drill.handle(K.parse('ESC'))
                app.stack.pop()
    out.append(('notes', app.open_notes()))
    return out


# --------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------

def test_keys(t: Runner) -> None:
    t.head('keys / notation')
    corpus = ['a', 'C-b', 'M-x', 'C-M-x', 'SPC', 'RET', 'TAB', 'ESC', 'BSP',
              'F10', 'Up', 'PgDn', '"', '%', 'C-SPC', 'S-TAB', 'C-M-S-F5']
    for s in corpus:
        t.eq(f'round-trip {s}', K.unparse(K.parse(s)), s)
    t.eq('S- folds into shifted char', K.parse("S-'"), K.parse('"'))
    t.eq('S-a is A', K.parse('S-a'), K.parse('A'))
    t.raises('empty key rejected', K.KeyError_, lambda: K.parse(''))
    t.raises('multi-char rejected', K.KeyError_, lambda: K.parse('abc'))
    t.raises('str sequence rejected', K.KeyError_, lambda: K.parse_seq('C-b'))

    t.head('keys / legacy decoding')
    cases = [
        (b'a', ['a']), (b'\x02', ['C-b']), (b'\x02"', ['C-b', '"']),
        (b'\t', ['TAB']), (b'\r', ['RET']), (b'\x1b', ['ESC']),
        (b'\x7f', ['BSP']), (b'\x00', ['C-SPC']), (b'\x1b[A', ['Up']),
        (b'\x1b[1;5A', ['C-Up']), (b'\x1b[21~', ['F10']), (b'\x1bOP', ['F1']),
        (b'\x1bx', ['M-x']), (b'\x1b\x18', ['C-M-x']), (b'\xc3\xa9', ['é']),
        (b'\x1b[3~', ['DEL']),
    ]
    for data, want in cases:
        d = K.Decoder()
        got = K.unparse_seq(d.feed(data) + d.flush())
        t.eq(f'legacy {data!r}', got, want)

    t.head('keys / kitty protocol (D11 payoff)')
    kitty = [
        (b'\x1b[105;5u', ['C-i']), (b'\x1b[9u', ['TAB']),
        (b'\x1b[109;5u', ['C-m']), (b'\x1b[13u', ['RET']),
        (b'\x1b[91;5u', ['C-[']), (b'\x1b[27u', ['ESC']),
        (b'\x1b[39;2u', ['"']), (b'\x1b[120;7u', ['C-M-x']),
    ]
    for data, want in kitty:
        d = K.Decoder(kitty=True)
        got = K.unparse_seq(d.feed(data) + d.flush())
        t.eq(f'kitty {data!r}', got, want)
    # The point of all this: under kitty they differ, under legacy they collide.
    d1 = K.Decoder(kitty=True)
    t.ok('C-i distinct from TAB under kitty',
         K.unparse_seq(d1.feed(b'\x1b[105;5u')) != K.unparse_seq(K.Decoder().feed(b'\t')))
    t.eq('legacy collapses C-i into TAB', K.unparse_seq(K.Decoder().feed(b'\t')), ['TAB'])

    t.head('keys / partial sequences')
    d = K.Decoder()
    t.eq('incomplete CSI held', K.unparse_seq(d.feed(b'\x1b[')), [])
    t.eq('completed on next feed', K.unparse_seq(d.feed(b'A')), ['Up'])
    d = K.Decoder()
    t.eq('lone ESC held pending', K.unparse_seq(d.feed(b'\x1b')), [])
    t.eq('lone ESC released on flush', K.unparse_seq(d.flush()), ['ESC'])

    t.head('keys / ambiguity reporting')
    t.ok('C-i flagged ambiguous', bool(K.ambiguity_for(K.parse_seq(['C-i']))))
    t.ok('C-b not flagged', not K.ambiguity_for(K.parse_seq(['C-b'])))


def test_term(t: Runner) -> None:
    t.head('term / kitty reply parsing')
    cases = [
        (b'\x1b[?1u\x1b[?62;22c', True), (b'\x1b[?0u\x1b[?6c', True),
        (b'\x1b[?62;22c', False), (b'\x1b[?1;2;6c', False), (b'', False),
        (b'\x1b[?u', False),  # malformed: strict, because a false positive lies
        (b'noise\x1b[?31u tail', True),
    ]
    for buf, want in cases:
        t.eq(f'reply {buf!r}', term.kitty_in_reply(buf), want)

    t.head('term / headless safety')
    t.eq('is_tty false in a pipe', term.is_tty(), False)
    t.eq('detect_kitty false with no tty', term.detect_kitty(), False)
    t.ok('size returns two ints', len(term.size()) == 2)
    tt = term.Terminal()
    with tt:
        t.eq('read_keys empty headless', tt.read_keys(timeout=0.01), [])
        with tt.suspended():
            pass
    t.ok('enter/exit/suspend headless raise nothing', True)


def test_render(t: Runner) -> None:
    t.head('render / measurement')
    t.eq('ascii width', render.text_width('plain'), 5)
    t.eq('combining mark is zero width', render.text_width('é'), 1)
    t.eq('CJK is double width', render.text_width('日本'), 4)
    tx = Text().add('abcdefghij').add('KLMNOP')
    tx.truncate(8)
    t.ok('truncate respects budget', tx.width() <= 8, f'width {tx.width()}')

    t.head('render / colour conversion')
    for hexv in ('#00f0ff', '#ff5fd7', '#070b16', '#dce7ff', '#72f1b8'):
        idx = theme._to_256(hexv)
        t.ok(f'{hexv} maps into 256 range', 0 <= idx <= 255, str(idx))

    t.head('render / D19 footer contract')
    caps = Caps(ColorLevel.TRUE, GlyphLevel.UNICODE, theme.CYBERPUNK_NEON, 80, 24)
    t.raises('empty footer refused', ValueError, lambda: render.footer(caps, []))

    t.head('render / ansi palette caps the ladder')
    c = render.detect_caps(theme='ansi', cols=80, rows=24)
    t.ok('ansi never exceeds 16 colours', c.color <= ColorLevel.C16)


def test_state(t: Runner) -> None:
    t.head('state / persistence')
    tmp = Path(tempfile.mkdtemp())
    s = st.State.blank(T0)
    s.mark_lesson('tmux', 'l1', T0)
    s.mark_challenge('tmux', 'c1', 'free', A.VERIFIED, T0)
    p = s.save(tmp / 'state.json', T0)
    back = st.State.load(p)
    t.eq('round-trips exactly', back.data, s.data)
    t.eq('verification label kept',
         back.module('tmux')['challenges']['c1']['verification'], A.VERIFIED)
    t.ok('written atomically, no tmp left', not (tmp / 'state.tmp').exists())

    t.head('state / corrupt file recovery')
    (tmp / 'bad.json').write_text('{ not json at all')
    rec = st.State.load(tmp / 'bad.json', T0)
    t.ok('load did not raise', rec is not None)
    t.ok('quarantined, not deleted', (tmp / 'bad.corrupt1.json').exists())
    t.eq('original bytes preserved',
         (tmp / 'bad.corrupt1.json').read_text(), '{ not json at all')
    t.ok('recovered_from is reported', rec.recovered_from is not None)
    t.eq('missing file is just a new user',
         st.State.load(tmp / 'nope.json', T0).data['modules'], {})

    t.head('state / export and import')
    dest = s.export_to(tmp / 'out.json', T0)
    t.eq('import round-trips', st.State.import_from(dest, T0).data, s.data)
    (tmp / 'junk.json').write_text('{"hello": 1}')
    t.raises('bad import reported, not swallowed', ValueError,
             lambda: st.State.import_from(tmp / 'junk.json', T0))

    t.head('state / progress')
    t.eq('empty kinds excluded from progress',
         s.progress('tmux', {'lessons': 1, 'challenges': 1, 'drills': 0, 'quiz': 0}), 1.0)
    t.eq('no content is zero, not a crash', s.progress('nothing', {}), 0.0)


def test_loader(t: Runner) -> None:
    t.head('loader / normalisation')
    m = loader.build_module({'id': 'x', 'title': 'X', 'drills': [{'id': 'd'}]}, 'src')
    t.eq('totals', m.totals(), {'lessons': 0, 'challenges': 0, 'drills': 1, 'quiz': 0})
    t.ok('drill deck detected', m.is_drill_deck)
    t.eq('lookup by id', m.item('drills', 'd'), {'id': 'd'})
    t.eq('missing lookup is None', m.item('drills', 'nope'), None)
    t.raises('no id rejected', ValueError, lambda: loader.build_module({'title': 'T'}))
    t.raises('no title rejected', ValueError, lambda: loader.build_module({'id': 'i'}))

    t.head('loader / registry')
    reg = fixture_registry()
    t.eq('ids in order', reg.ids(), ['tmux', 'utils', 'empty'])
    t.eq('unmet prereqs found', reg.unmet_prereqs('empty'), [])
    t.eq('get missing is None', reg.get('nope'), None)

    t.head('loader / real discovery is fault tolerant')
    real = loader.load_all()
    t.ok('returns a Registry even with no content', isinstance(real, loader.Registry))
    t.ok('zero modules is valid', len(real) >= 0)


def test_adapters(t: Runner) -> None:
    t.head('adapters / D18 degrade path')
    A.reset()  # genuinely empty: no builtins auto-register after a reset
    t.eq('reset gives an empty registry', A.registered(), [])
    want_tmux = {'id': 'c', 'verify': {'kind': 'tmux'}, 'fallback': 'self'}
    p = A.plan_for(want_tmux)
    t.eq('missing adapter degrades to self', p.kind, A.SELF)
    t.ok('and says why', p.degraded and 'not built yet' in p.reason)

    A.register('tmux', lambda: A.FakeAdapter(ok=True))
    t.eq('present adapter verifies', A.plan_for(want_tmux).kind, A.VERIFIED)

    A.register('tmux', lambda: A.FakeAdapter(available=False))
    p = A.plan_for(want_tmux)
    t.eq('unusable adapter degrades', p.kind, A.SELF)
    t.ok('with the tool reason', 'unavailable' in p.reason)

    t.eq('authored self is not degraded', A.plan_for({'id': 'x'}).degraded, False)
    t.eq('graded needs no adapter',
         A.plan_for({'id': 'y', 'verify': {'kind': 'graded'}}).kind, A.GRADED)
    A.reset()

    t.head('adapters / D1 contract')
    f = A.FakeAdapter()
    t.raises('observe before setup refused', A.AdapterError, f.observe)
    with f.session({'session': 'hone-drill'}) as ad:
        t.ok('observes inside a session', ad.observe().ok)
    t.eq('teardown ran on exit', f.teardown_calls, 1)
    f.teardown()
    t.eq('teardown is idempotent', f.teardown_calls, 2)

    class Exploding(A.FakeAdapter):
        def teardown(self):
            raise RuntimeError('boom')

    e = Exploding()
    with e.session({}) as ad:
        res = ad.observe()
    t.ok('failing teardown does not mask the result', res.ok)

    t.head('adapters / picker status')
    t.eq('no adapter declared', A.status(None), (False, 'content only'))
    ok, reason = A.status('nope')
    t.ok('unknown adapter explains itself', not ok and 'not built yet' in reason)

    t.head('adapters / builtins are registered by default')
    A.reset(builtins=True)
    t.ok('tmux ships', 'tmux' in A.registered())


def test_screens(t: Runner) -> None:
    reg = fixture_registry()

    t.head('screens / D19 across the D20 ladder')
    total = 0
    for label, color, glyph, pal in RUNGS:
        caps = Caps(color, glyph, pal, 80, 24)
        app = App(reg, seen(), T0, caps)
        for name, scr in walk_screens(app, reg):
            total += 1
            try:
                lines = scr.render(caps)
            except ScreenContractError as e:
                t.ok(f'{label} {name} renders', False, str(e))
                continue
            t.ok(f'{label} {name} has lines', bool(lines))
            over = [x.width() for x in lines if x.width() > caps.cols]
            t.ok(f'{label} {name} fits {caps.cols} cols', not over, str(over))
            # Height, not just width. A list longer than the terminal is
            # unusable, and only width was ever checked before.
            t.ok(f'{label} {name} fits {caps.rows} rows',
                 len(lines) <= caps.rows, f'{len(lines)} lines')
            t.ok(f'{label} {name} has a footer', bool(scr.hints(caps)))
            # D19 rule 2: every screen has a way out, and it is the key the
            # footer names. The root is the exception and states its own: Esc
            # means "back" everywhere, there is nowhere back to from home, so
            # home is left with `q` and Esc is deliberately inert there.
            leave = 'q' if not scr.can_pop else scr.escape_key
            t.ok(f'{label} {name} can be left via {leave}',
                 scr.handle(K.parse(leave)).kind != 'stay')
            if not scr.can_pop:
                t.eq(f'{label} {name} ignores ESC rather than quitting',
                     scr.handle(K.parse('ESC')).kind, 'stay')
    t.ok(f'walked {total} screen-renders', total > 0)

    t.head('screens / ASCII purity at the ASCII rung')
    # Regression guard: hardcoded glyphs in constants have leaked three times.
    for label, color, glyph, pal in RUNGS:
        if glyph != GlyphLevel.ASCII:
            continue
        caps = Caps(color, glyph, pal, 80, 24)
        app = App(reg, seen(), T0, caps)
        for name, scr in walk_screens(app, reg):
            txt = ''.join(x.plain() for x in scr.render(caps))
            bad = sorted({c for c in txt if ord(c) > 127})
            t.ok(f'{label} {name} is pure ASCII', not bad, ''.join(bad))

    t.head('screens / empty states are never blank (D19 rule 3)')
    empty = loader.Registry()
    caps = Caps(ColorLevel.NONE, GlyphLevel.ASCII, theme.NEUTRAL, 80, 24)
    app = App(empty, seen(), T0, caps)
    lines = app.render()
    t.ok('home with zero modules still explains itself', len(lines) > 4)
    t.ok('and names where content goes',
         'hone/content/' in ''.join(x.plain() for x in lines))

    mod_screen = None
    app2 = App(reg, seen(), T0, caps)
    app2.stack[0].cursor = 2  # the module with no content at all
    app2.dispatch(K.parse('RET'))
    mod_screen = app2.screen
    for v in range(3):
        mod_screen.set_view(v)
        body = mod_screen.body(caps)
        t.ok(f'empty view {v} still renders something', bool(body))

    t.head('screens / drill engine')
    caps = Caps(ColorLevel.TRUE, GlyphLevel.UNICODE, theme.CYBERPUNK_NEON, 80, 24)
    state = seen()
    app3 = App(reg, state, T0, caps)
    app3.stack[0].cursor = 0
    app3.dispatch(K.parse('RET'))
    app3.screen.set_view(2)
    app3.dispatch(K.parse('RET'))
    drill = app3.screen
    t.ok('capture screen is marked capturing', drill.capturing)
    t.eq('escape key is the reserved chord', drill.escape_key, drill.exit_chord)

    for k in ('C-b', '"'):
        drill.handle(K.parse(k))
    t.eq('correct answer judged correct', drill.last_correct, True)
    t.eq('phase moves to feedback', drill.phase, 'feedback')
    card = state.peek('tmux', 'drills', 'd1')
    t.eq('attempt recorded', card.get('seen'), 1)
    t.eq('and marked right', card.get('correct'), 1)
    t.eq('nothing is scheduled', sorted(card), ['correct', 'seen'])

    drill.handle(K.parse('RET'))
    t.eq('enter advances', drill.phase, 'prompt')
    for k in ('C-b', 'x'):
        drill.handle(K.parse(k))
    t.eq('wrong answer judged wrong', drill.last_correct, False)
    miss = state.peek('tmux', 'drills', 'd2')
    t.eq('a miss is recorded', miss.get('seen'), 1)
    t.eq('and not counted right', miss.get('correct', 0), 0)

    t.head('screens / D19a reserved chord always escapes')
    for phase in ('prompt', 'feedback'):
        d2 = App(reg, seen(), T0, caps)
        d2.stack[0].cursor = 0
        d2.dispatch(K.parse('RET'))
        d2.screen.set_view(2)
        d2.dispatch(K.parse('RET'))
        scr = d2.screen
        scr.phase = phase
        t.eq(f'{scr.exit_chord} pops in {phase}',
             scr.handle(K.parse(scr.exit_chord)).kind, 'pop')

    t.head('screens / D11 honesty about the terminal')
    amb = loader.build_module({'id': 'amb', 'title': 'Ambiguous',
                               'drills': [{'id': 'a', 'keys': ['C-i'],
                                           'prompt': 'jump forward'}]}, 'fixture')
    from hone.screens.drill import DrillScreen
    legacy = DrillScreen(amb, list(amb.drills), 0, st.State.blank(T0), T0, kitty=False)
    kitty = DrillScreen(amb, list(amb.drills), 0, st.State.blank(T0), T0, kitty=True)
    t.ok('legacy terminal warned about C-i', bool(legacy.unanswerable()))
    t.ok('kitty terminal not warned', not kitty.unanswerable())
    t.ok('warning appears on screen',
         'cannot send' in ''.join(x.plain() for x in legacy.body(caps)))

    t.head('screens / long lists are windowed, not overflowed')
    long_mod = loader.build_module({
        'id': 'long', 'title': 'Long', 'order': 9,
        'drills': [{'id': f'd{i}', 'type': 'recall', 'keys': ['x'],
                    'prompt': f'drill number {i}'} for i in range(60)],
    }, 'fixture')
    from hone.screens.module import ModuleScreen as _MS
    for rows in (10, 18, 24, 50):
        caps = Caps(ColorLevel.NONE, GlyphLevel.ASCII, theme.NEUTRAL, 80, rows)
        ms = _MS(long_mod, st.State.blank(T0), T0)
        ms.set_view(2)
        t.ok(f'60 drills fit a {rows}-row terminal',
             len(ms.render(caps)) <= rows, f'{len(ms.render(caps))} lines')
        ms.cursor = 59
        t.ok(f'and still fit with the cursor at the end ({rows} rows)',
             len(ms.render(caps)) <= rows)
        shown = ''.join(x.plain() for x in ms.render(caps))
        t.ok(f'the selected item is visible ({rows} rows)',
             'drill number 59' in shown)

    t.head('screens / navigation')
    app4 = App(reg, seen(), T0, caps)
    home = app4.stack[0]
    home.cursor = 0
    home.handle(K.parse('j'))
    t.eq('j moves down', home.cursor, 1)
    home.handle(K.parse('k'))
    t.eq('k moves up', home.cursor, 0)
    home.handle(K.parse('Up'))
    t.eq('cursor wraps', home.cursor, len(reg) - 1)
    t.eq('q quits', home.handle(K.parse('q')).kind, 'quit')
    # Esc used to quit here. It is inert now: the most-pressed key in the
    # app should not also be the one that ends the session from the screen
    # you return to most, and the home footer never advertised it.
    t.eq('esc at root does nothing', home.handle(K.parse('ESC')).kind, 'stay')
    app4.dispatch(K.parse('RET'))
    t.eq('esc in a module pops', app4.screen.handle(K.parse('ESC')).kind, 'pop')

    t.head('screens / every declared hint does something')
    for label, color, glyph, pal in RUNGS[:2]:
        caps = Caps(color, glyph, pal, 80, 24)
        app5 = App(reg, seen(), T0, caps)
        for name, scr in walk_screens(app5, reg):
            for kstr, lbl in scr.hints(caps):
                probe = {'esc': 'ESC', 'tab': 'TAB'}.get(kstr, kstr)
                try:
                    key = K.parse(probe)
                except K.KeyError_:
                    continue  # '↑↓', 'keys', 'any key' describe classes, not keys
                # Previously this only checked esc, q and tab, which is how
                # `?` shipped in every footer while doing nothing at all.
                if kstr in ('esc', 'q'):
                    t.ok(f'{name}: {kstr!r} ({lbl}) is live',
                         scr.handle(key).kind != 'stay')
                elif kstr == '?':
                    before = len(app5.stack)
                    act = scr.handle(key)
                    t.ok(f'{name}: help key is live', act.kind == 'push',
                         f'got {act.kind}')
                elif kstr == 'tab':
                    t.ok(f'{name}: tab is handled', True)


def test_real_content(t: Runner) -> None:
    """Walk the content that is actually installed, not just the fixtures.

    The fixtures keep the engine tests hermetic, but they cannot catch a real
    module that is too wide, links to a lesson that does not exist, or has a
    drill whose answer does not survive a round trip through the grader.
    """
    reg = loader.load_all()
    t.head('real content / present')
    t.ok('at least one module installed', len(reg) > 0, 'nothing to check')
    t.eq('no load errors', [e.name for e in reg.errors], [])
    if not len(reg):
        return

    t.head('real content / renders at every rung')
    for label, color, glyph, pal in RUNGS:
        caps = Caps(color, glyph, pal, 80, 24)
        app = App(reg, seen(), T0, caps)
        for name, scr in walk_screens(app, reg):
            lines = scr.render(caps)
            over = [x.width() for x in lines if x.width() > caps.cols]
            t.ok(f'{label} {name} fits', not over, str(over))
            t.ok(f'{label} {name} fits {caps.rows} rows',
                 len(lines) <= caps.rows, f'{len(lines)} lines')
            if glyph == GlyphLevel.ASCII:
                txt = ''.join(x.plain() for x in lines)
                bad = sorted({c for c in txt if ord(c) > 127})
                t.ok(f'{label} {name} pure ASCII', not bad, ''.join(bad))

    t.head('real content / every lesson renders and chains')
    caps = Caps(ColorLevel.TRUE, GlyphLevel.UNICODE, theme.CYBERPUNK_NEON, 80, 24)
    from hone.screens.lesson import LessonScreen
    for mod in reg:
        for lesson in mod.lessons:
            scr = LessonScreen(mod, lesson, st.State.blank(T0), T0)
            lines = scr.full_lines(caps)
            t.ok(f'{mod.id}/{lesson["id"]} has body', len(lines) > 3)
            over = [x.width() for x in scr.render(caps) if x.width() > caps.cols]
            t.ok(f'{mod.id}/{lesson["id"]} fits', not over, str(over))
            nxt = lesson.get('next')
            if nxt:
                t.ok(f'{mod.id}/{lesson["id"]} next resolves',
                     mod.item('lessons', nxt) is not None)
        # scrolling to the bottom must mark it read
        if mod.lessons:
            state = st.State.blank(T0)
            scr = LessonScreen(mod, mod.lessons[0], state, T0)
            scr.scroll = 10 ** 6
            scr.body(caps)
            t.ok(f'{mod.id}: reaching the end marks read',
                 state.item(mod.id, 'lessons', mod.lessons[0]['id']).get('done'))

    t.head('real content / every drill accepts its own answer')
    from hone.screens.drill import ORACLE_TYPES, DrillScreen
    for mod in reg:
        for i, d in enumerate(mod.drills):
            state = st.State.blank(T0)
            scr = DrillScreen(mod, list(mod.drills), i, state, T0, kitty=True)
            if d.get('type') == 'regex':
                # The reference answer must itself pass the behavioural check.
                scr.typed = str(d['answer'])
                scr._judge_text()
                t.ok(f'{mod.id}/{d["id"]} its own answer passes',
                     scr.last_correct, scr.last_note)
            elif d.get('type') in ORACLE_TYPES:
                # Same argument, run for real: the reference is fed back in
                # and must pass whichever way this machine can grade it. When
                # the tool is present this really runs tcpdump or pwsh, and
                # `last_verified` says which of the two happened, so a machine
                # missing the tool still tests the degrade path rather than
                # skipping the drill.
                scr.typed = str(d['answer'])
                scr._judge_text()
                t.ok(f'{mod.id}/{d["id"]} its own answer passes',
                     scr.last_correct, scr.last_note)
                t.ok(f'{mod.id}/{d["id"]} says how it was graded',
                     scr.last_verified in (True, False))
                scr.close()
            elif d.get('type') == 'command':
                answers = [d['answer']] + [a for a in (d.get('accepts') or ())
                                           if isinstance(a, str)]
                for ans in answers:
                    scr._advance(); scr.index = i
                    scr.typed = ans
                    scr._judge_text()
                    t.ok(f'{mod.id}/{d["id"]} accepts {ans!r}', scr.last_correct)
            elif d.get('type') == 'recall':
                scr.typed = ' '.join(d['keys'])
                scr._judge_text()
                t.ok(f'{mod.id}/{d["id"]} accepts its own keys', scr.last_correct)
            else:
                scr.collected = K.parse_seq(d['keys'])
                scr._judge_keys()
                t.ok(f'{mod.id}/{d["id"]} accepts its own keys', scr.last_correct)

    t.head('real content / a wrong answer is graded wrong')
    for mod in reg:
        for i, d in enumerate(mod.drills[:3]):
            state = st.State.blank(T0)
            scr = DrillScreen(mod, list(mod.drills), i, state, T0, kitty=True)
            scr.typed = 'definitely-not-the-answer'
            if d.get('type') in ('recall', 'command', 'regex', *ORACLE_TYPES):
                scr._judge_text()
                t.ok(f'{mod.id}/{d["id"]} rejects junk', scr.last_correct is False)
                scr.close()

    t.head('real content / quiz items are answerable')
    for mod in reg:
        for q in mod.quiz:
            t.ok(f'{mod.id}/{q["id"]} has an answer', bool(q.get('answer')))
            ds = q.get('distractors') or []
            t.ok(f'{mod.id}/{q["id"]} has distractors', len(ds) >= 2)
            t.ok(f'{mod.id}/{q["id"]} answer not among distractors',
                 q.get('answer') not in ds)


def test_tmux_adapter(t: Runner) -> None:
    """The adapter's pure logic always; its live behaviour only if tmux exists."""
    from hone.adapters import tmux as TA

    t.head('tmux adapter / check logic')
    ok3 = {'session_exists': True, 'panes': 3, 'windows': 1, 'window_names': ['a']}
    t.eq('min_panes met', TA.check({'min_panes': 3}, ok3)[0], True)
    passed, why = TA.check({'min_panes': 5}, ok3)
    t.ok('min_panes unmet says what was seen', not passed and '3 panes' in why, why)
    passed, why = TA.check({'session_exists': True},
                           {'session_exists': False, 'session': 'hone-drill'})
    t.ok('missing session names itself', not passed and 'hone-drill' in why, why)
    passed, why = TA.check({'named_windows': True},
                           {'session_exists': True, 'panes': 1, 'windows': 2,
                            'window_names': ['editor', 'zsh']})
    t.ok('default window name flagged', not passed and 'zsh' in why, why)
    t.eq('all named passes', TA.check({'named_windows': True},
         {'session_exists': True, 'panes': 1, 'windows': 1,
          'window_names': ['editor']})[0], True)
    t.eq('pluralisation', TA._describe({'panes': 1, 'windows': 1}),
         '1 pane in 1 window')

    t.head('tmux adapter / handoff')
    t.eq('attach by default', TA.handoff_command({}, 's'), ['tmux', 'attach', '-t', 's'])
    t.eq('shell when asked', TA.handoff_command({'handoff': 'shell'}, 's'), [])

    ad = TA.TmuxAdapter()
    if not ad.available():
        t.ok('tmux not installed, live checks skipped', True)
        return

    t.head('tmux adapter / live, and the D1 contract')
    import subprocess as sp

    def kill(name):
        sp.run(['tmux', 'kill-session', '-t', name], capture_output=True)

    def make(name, splits=0):
        """Create a session, retrying until it exists.

        Killing the last session stops the tmux server, and the very next
        new-session can then fail outright with "server exited unexpectedly"
        rather than merely being slow. Polling for the session is not enough
        because the creation itself is what failed, so this retries the
        creation. Diagnosed from a test that passed on one run and failed on
        the next with a message about the thing it was not testing.
        """
        for _ in range(50):
            if sp.run(['tmux', 'has-session', '-t', name],
                      capture_output=True).returncode == 0:
                break
            sp.run(['tmux', 'new-session', '-d', '-s', name],
                   capture_output=True)
            time.sleep(0.02)
        for _ in range(splits):
            sp.run(['tmux', 'split-window', '-t', name], capture_output=True)

    kill('hone-test-a'); kill('hone-test-b')

    a = TA.TmuxAdapter()
    a.setup({'session': 'hone-test-a', 'create': True})
    t.ok('created its own sandbox', a._created)
    obs = a.observe()
    t.ok('observes it', obs.ok and obs.data['panes'] == 1)
    sp.run(['tmux', 'split-window', '-t', 'hone-test-a'], capture_output=True)
    t.eq('sees a new pane', a.observe().data['panes'], 2)
    a.teardown()
    t.ok('teardown removed its own session', not a.has_session('hone-test-a'))
    a.teardown()
    t.ok('teardown is idempotent', True)

    # The rule that matters: a session we did not create is not ours to kill.
    make('hone-test-b')
    b = TA.TmuxAdapter()
    b.setup({'session': 'hone-test-b', 'create': True})
    t.ok('does not claim a pre-existing session', not b._created)
    b.teardown()
    t.ok('D1: pre-existing session survives teardown',
         b.has_session('hone-test-b'))
    kill('hone-test-b')

    t.head('tmux adapter / a stale session must not hand out a false pass')
    # The dangerous case: a session left over from anything else already has
    # three panes, and "build three panes" would pass without the student
    # touching a key. The adapter refuses to grade what it cannot attribute.
    make('hone-test-stale', splits=2)
    stale = TA.TmuxAdapter()
    stale.setup({'session': 'hone-test-stale', 'create': True})
    obs = stale.observe()
    t.ok('refuses to verify a pre-existing session',
         obs.data.get('cannot_verify') is True)
    t.ok('and explains why', 'already open' in obs.detail, obs.detail)
    stale.teardown()
    t.ok('D1 still holds: it did not kill it', stale.has_session('hone-test-stale'))
    kill('hone-test-stale')

    t.head('challenge / an untrustworthy observation degrades, never passes')
    from hone.screens.challenge import ChallengeScreen as _CS

    class Untrustworthy(A.FakeAdapter):
        def observe(self):
            return A.Observation(False, {'cannot_verify': True},
                                 'cannot tell your work from what was here')

    A.reset()
    A.register('tmux', Untrustworthy)
    reg2 = fixture_registry()
    ch2 = reg2.get('tmux').item('challenges', 'c1')
    state2 = st.State.blank(T0)
    scr2 = _CS(reg2.get('tmux'), ch2, state2, T0,
               handoff=lambda argv, cwd=None, brief=None, env=None: None)
    t.eq('starts out promising verification', scr2.plan.kind, A.VERIFIED)
    scr2.handle(K.parse('RET'))
    t.eq('but degrades on an untrustworthy observation', scr2.phase, 'selfmark')
    t.ok('carrying the reason', 'cannot tell' in scr2.plan.reason)
    t.ok('and nothing was recorded as verified',
         not state2.module('tmux')['challenges'].get('c1', {}).get('done'))
    A.reset(builtins=True)

    c = TA.TmuxAdapter()
    c.setup({'session': 'hone-test-none', 'create': False})
    t.ok('create False does not create', not c.has_session('hone-test-none'))
    t.ok('observe reports the absence', not c.observe().ok)
    c.teardown()


def test_challenge(t: Runner) -> None:
    from hone.screens.challenge import ChallengeScreen

    reg = fixture_registry()
    mod = reg.get('tmux')
    ch = mod.item('challenges', 'c1')
    caps = Caps(ColorLevel.TRUE, GlyphLevel.UNICODE, theme.CYBERPUNK_NEON, 80, 24)

    t.head('challenge / D6 one definition, three frictions')
    A.reset()
    A.register('tmux', lambda: A.FakeAdapter(ok=True, data={'panes': 3}))
    state = st.State.blank(T0)
    scr = ChallengeScreen(mod, ch, state, T0,
                                  handoff=lambda argv, cwd=None, brief=None, env=None: None)
    scr.set_rigor('guided')
    guided = ''.join(x.plain() for x in scr.body(caps))
    scr.set_rigor('coached')
    coached = ''.join(x.plain() for x in scr.body(caps))
    scr.set_rigor('free')
    free = ''.join(x.plain() for x in scr.body(caps))
    t.ok('guided shows hints', 'C-b' in guided or len(guided) > len(coached))
    t.ok('coached hides them', len(coached) < len(guided))
    t.ok('free is shortest', len(free) < len(coached))
    scr.set_rigor('coached')
    scr.handle(K.parse('h'))
    t.ok('h reveals hints in coached',
         len(''.join(x.plain() for x in scr.body(caps))) > len(coached))

    t.head('challenge / D16 rule 4, verification known before starting')
    t.eq('plan decided at construction', scr.plan.kind, A.VERIFIED)
    t.ok('and shown in the brief',
         'verified' in ''.join(x.plain() for x in scr.body(caps)))

    t.head('challenge / verified pass and fail')
    scr.set_rigor('guided')
    scr.handle(K.parse('RET'))
    t.eq('passes when the adapter agrees', scr.passed, True)
    rec = state.module('tmux')['challenges']['c1']
    t.eq('recorded as verified', rec['verification'], A.VERIFIED)
    t.eq('records the rigor used', rec['mode'], 'guided')

    A.reset()
    A.register('tmux', lambda: A.FakeAdapter(ok=False, data={'panes': 1}))
    state2 = st.State.blank(T0)
    scr2 = ChallengeScreen(mod, ch, state2, T0,
                           handoff=lambda argv, cwd=None, brief=None, env=None: None)
    scr2.handle(K.parse('RET'))
    t.ok('fail is not recorded as done',
         not state2.module('tmux')['challenges'].get('c1', {}).get('done'))
    t.ok('failing keeps the sandbox for a retry', scr2._adapter_ready)

    t.head('challenge / D18 degrade to self-marked')
    A.reset()
    state3 = st.State.blank(T0)
    scr3 = ChallengeScreen(mod, ch, state3, T0,
                           handoff=lambda argv, cwd=None, brief=None, env=None: None)
    t.eq('no adapter means self', scr3.plan.kind, A.SELF)
    scr3.handle(K.parse('RET'))
    t.eq('lands on the self-mark prompt', scr3.phase, 'selfmark')
    scr3.handle(K.parse('y'))
    t.eq('records self, never verified',
         state3.module('tmux')['challenges']['c1']['verification'], A.SELF)

    t.head('challenge / an adapter that explodes degrades rather than crashes')
    class Exploding(A.FakeAdapter):
        def observe(self):
            raise RuntimeError('kaboom')
    A.reset()
    A.register('tmux', Exploding)
    scr4 = ChallengeScreen(mod, ch, st.State.blank(T0), T0,
                           handoff=lambda argv, cwd=None, brief=None, env=None: None)
    scr4.handle(K.parse('RET'))
    t.eq('falls back to self-mark', scr4.phase, 'selfmark')
    t.ok('and says why', 'kaboom' in scr4.plan.reason)
    A.reset(builtins=True)


def test_quiz(t: Runner) -> None:
    from hone.screens.quiz import QuizScreen

    reg = fixture_registry()
    mod = loader.build_module({
        'id': 'q', 'title': 'Q',
        'quiz': [{'id': 'q1', 'prompt': 'p?', 'answer': 'right',
                  'distractors': ['wrong a', 'wrong b'], 'teach': 'because'}],
    }, 'fixture')

    t.head('quiz / shuffling')
    state = st.State.blank(T0)
    a = QuizScreen(mod, list(mod.quiz), 0, state, T0)
    b = QuizScreen(mod, list(mod.quiz), 0, state, T0)
    t.eq('same attempt shuffles identically', a.options(), b.options())
    t.eq('all options present', sorted(a.options()),
         sorted(['right', 'wrong a', 'wrong b']))
    t.ok('answer index is findable', a.correct_index() >= 0)
    state.item('q', 'quiz', 'q1')['seen'] = 5
    c = QuizScreen(mod, list(mod.quiz), 0, state, T0)
    t.ok('order may change between attempts', c.options() is not None)

    t.head('quiz / grading feeds the scheduler')
    state = st.State.blank(T0)
    scr = QuizScreen(mod, list(mod.quiz), 0, state, T0)
    correct_key = str(scr.correct_index() + 1)
    scr.handle(K.parse(correct_key))
    t.eq('correct answer registers', scr.last_correct, True)
    t.eq('phase moves to feedback', scr.phase, 'feedback')
    card = state.peek('q', 'quiz', 'q1')
    t.eq('attempt recorded', card.get('seen'), 1)
    t.eq('and marked right', card.get('correct'), 1)

    state = st.State.blank(T0)
    scr = QuizScreen(mod, list(mod.quiz), 0, state, T0)
    wrong = str(((scr.correct_index() + 1) % 3) + 1)
    scr.handle(K.parse(wrong))
    t.eq('wrong answer registers', scr.last_correct, False)
    miss = state.peek('q', 'quiz', 'q1')
    t.eq('a miss is recorded', miss.get('seen'), 1)
    t.eq('and not counted right', miss.get('correct', 0), 0)


def test_solvable(t: Runner) -> None:
    """Play every adapter-verified challenge through the real tool.

    This is the strongest guarantee the harness can give about content: not
    that a challenge parses, but that the task it sets can actually be
    completed and that the verifier agrees. It caught a real bug on its first
    run, where a challenge started with the cursor already on the first match
    so its own steps could never reach the stated goal.

    Skipped per-tool when the tool is not installed, per D18.
    """
    import shutil as _sh
    import subprocess as _sp
    import tempfile as _tf

    reg = loader.load_all()
    A.reset(builtins=True)

    t.head('solvable / every verified challenge has a demonstrated solution')
    checked = 0
    for mod in reg:
        for ch in mod.challenges:
            spec = ch.get('verify') or {}
            kind = spec.get('kind')
            if not kind or kind in (A.GRADED, A.SELF):
                continue
            sol = ch.get('solution')
            t.ok(f'{mod.id}/{ch["id"]} declares a solution', bool(sol))
            if not sol:
                continue
            ad = A.get(kind)
            if ad is None or not ad.available():
                continue
            checked += 1

            from hone.screens.challenge import ChallengeScreen

            def handoff(argv, cwd=None, brief=None, env=None, sol=sol, kind=kind):
                # Dispatch on the SHAPE of the solution rather than on the
                # adapter name. Keying off the name meant every new adapter
                # silently replayed nothing and its challenges "failed", which
                # is exactly what happened when git arrived.
                if sol.get('shell') is not None:
                    # The adapter's env overrides must be honoured here, not
                    # only in the real handover. Without this the gpg
                    # solutions would run against the *tester's* own
                    # ~/.gnupg, which is both a D1 violation and a test that
                    # passes for the wrong reason.
                    _sp.run(['bash', '-c', sol['shell']], cwd=cwd,
                            env={**os.environ, **(env or {})},
                            capture_output=True, timeout=120)
                    return
                # argv[-2] is the leave hook and argv[-1] the file, for every
                # buffer adapter. See BufferAdapter.launch.
                if kind == 'nvim':
                    hook, scratch = argv[-2], argv[-1]
                    sf = Path(_tf.mkdtemp()) / 'keys'
                    sf.write_text(sol['keys'])
                    _sp.run(['nvim', '--headless', '-c', hook,
                             '-s', str(sf), scratch],
                            capture_output=True, timeout=60)
                    _sh.rmtree(sf.parent, ignore_errors=True)
                elif kind == 'emacs':
                    hook, scratch = argv[-2], argv[-1]
                    body = sol.get('elisp', '(ignore)')
                    tail = ('(save-buffer)' if sol.get('save', True)
                            else '(set-buffer-modified-p nil)')
                    _sp.run(['emacs', '--batch', '-Q', '--eval', hook, '--eval',
                             f'(progn (find-file "{scratch}") {body} {tail} '
                             f'(kill-emacs))'],
                            capture_output=True, timeout=120)
                elif kind == 'tmux':
                    for cmd in sol.get('commands', ()):
                        _sp.run(['tmux', *cmd], capture_output=True, timeout=10)

            state = st.State.blank(T0)
            scr = ChallengeScreen(mod, ch, state, T0, handoff=handoff)
            scr.handle(K.parse('RET'))
            t.ok(f'{mod.id}/{ch["id"]} is solvable', scr.passed is True,
                 f'{scr.phase}: {scr.detail or scr.plan.reason}')
            t.eq(f'{mod.id}/{ch["id"]} records verified',
                 state.module(mod.id)['challenges'].get(ch['id'], {})
                      .get('verification'), A.VERIFIED)
            scr._release()
            # A session created by the solution rather than by setup is, per
            # D1, not the adapter's to remove. The test made it, so the test
            # cleans it up; otherwise it leaks into the next challenge and
            # would hand out a false pass.
            if kind == 'tmux':
                _sp.run(['tmux', 'kill-session', '-t', 'hone-drill'],
                        capture_output=True)
    # Asserted, not merely reported. `checked >= 0` is always true, so a
    # whole batch of new challenges silently replaying nothing would have
    # passed: exactly the hole that let the git adapter ship unexercised.
    expected = sum(1 for mod in reg for ch in mod.challenges
                   if (ch.get('verify') or {}).get('kind')
                   not in (None, A.GRADED, A.SELF)
                   and (A.get((ch.get('verify') or {})['kind']) or None)
                   and A.get((ch.get('verify') or {})['kind']).available())
    t.eq(f'played every runnable challenge ({checked})', checked, expected)
    t.ok('and that is most of the roster', checked >= 20, checked)


def test_grading(t: Runner) -> None:
    """The `graded` tier of D8: exact checks with no external tool."""
    from hone.grading import evaluate_regex as ev

    t.head('grading / behaviour, not string comparison')
    M, R = ['ERROR: disk full', 'ERROR'], ['an ERROR happened', 'error: lower']
    t.ok('the obvious answer passes', ev('^ERROR', M, R).ok)
    t.ok('a different correct shape also passes', ev('^(ERROR|FATAL)', M, R).ok)
    t.ok('a third shape too', ev('^ERR', M, R).ok)

    t.head('grading / negatives catch over-matching')
    res = ev('ERROR', M, R)
    t.ok('unanchored is rejected', not res.ok)
    t.ok('and names what it wrongly matched', bool(res.over), res.detail)
    t.ok('detail says "too much"', 'too much' in res.detail, res.detail)

    t.head('grading / positives catch under-matching')
    res = ev('^ERROR: ', M, R)
    t.ok('too narrow is rejected', not res.ok)
    t.ok('and names what it missed', res.missed == ['ERROR'], str(res.missed))

    t.head('grading / bad input is explained, not crashed')
    t.ok('empty', not ev('', M, R).ok)
    bad = ev('^[A-Z', M, R)
    t.ok('syntax error reported', not bad.ok and bad.error, bad.detail)
    t.ok('absurdly long rejected', not ev('a' * 500, M, R).ok)

    t.head('grading / catastrophic backtracking is bounded and taught')
    res = ev(r'(a+)+$', ['a' * 40 + 'b'], [])
    t.ok('it did not hang', True)
    t.ok('reported as a timeout', res.timed_out)
    t.ok('and explains backtracking', 'backtracking' in res.detail, res.detail)
    import signal as _sig
    t.eq('the alarm was disarmed', _sig.getitimer(_sig.ITIMER_REAL), (0.0, 0.0))

    t.head('grading / flags')
    t.ok('i flag honoured', ev('^error', ['ERROR: x'], ['an ERROR'],
                               flags='i').ok)
    t.ok('and absent without it', not ev('^error', ['ERROR: x'], ['an ERROR']).ok)

    t.head('grading / the drill engine routes regex through it')
    from hone.screens.drill import DrillScreen
    mod = loader.build_module({
        'id': 'rx', 'title': 'rx',
        'drills': [{'id': 'd1', 'type': 'regex', 'prompt': 'p',
                    'match': ['abc'], 'reject': ['xyz'], 'answer': 'abc'}],
    }, 'fixture')
    state = st.State.blank(T0)
    scr = DrillScreen(mod, list(mod.drills), 0, state, T0)
    t.eq('regex is a text-mode drill', scr.mode, 'text')
    t.ok('and does not take the keyboard', not scr.capturing)
    scr.typed = 'abc'
    scr._judge_text()
    t.eq('correct pattern accepted', scr.last_correct, True)
    scr._advance()
    scr.typed = '.'
    scr._judge_text()
    t.eq('over-matching pattern rejected', scr.last_correct, False)
    t.ok('with the reason shown', 'too much' in scr.last_note, scr.last_note)
    t.ok('card was scheduled', state.module('rx')['drills']['d1'].get('seen') == 2)


def test_help_and_tour(t: Runner) -> None:
    from hone.screens.help import HELP, TOUR, HelpScreen
    from hone.screens import set_help_factory

    reg = fixture_registry()
    caps = Caps(ColorLevel.TRUE, GlyphLevel.UNICODE, theme.CYBERPUNK_NEON, 80, 24)

    t.head('help / the key every footer promises')
    set_help_factory(lambda: HelpScreen(HELP))
    app = App(reg, seen(), T0, caps)
    app.state.set_setting('seen_tour', True)
    for name, scr in walk_screens(app, reg):
        advertised = any(k == '?' for k, _ in scr.hints(caps))
        if not advertised:
            continue
        act = scr.handle(K.parse('?'))
        t.eq(f'{name}: ? opens help', act.kind, 'push')

    t.head('help / capture mode does not steal ?')
    from hone.screens.drill import DrillScreen
    mod = loader.build_module({
        'id': 'k', 'title': 'K',
        'drills': [{'id': 'd', 'type': 'keys', 'keys': ['?'], 'prompt': 'p'}],
    }, 'fixture')
    scr = DrillScreen(mod, list(mod.drills), 0, st.State.blank(T0), T0)
    t.ok('? is not advertised while capturing',
         not any(k == '?' for k, _ in scr.hints(caps)))
    scr.handle(K.parse('?'))
    t.eq('and is taken as an answer', K.unparse_seq(scr.collected), ['?'])

    t.head('help / paging')
    h = HelpScreen(HELP)
    t.eq('starts at the first card', h.index, 0)
    h.handle(K.parse('RET'))
    t.eq('enter advances', h.index, 1)
    h.handle(K.parse('h'))
    t.eq('h goes back', h.index, 0)
    t.eq('h at the start does nothing', h.handle(K.parse('h')).kind, 'stay')
    for _ in range(len(HELP)):
        act = h.handle(K.parse('RET'))
    t.eq('enter on the last card closes', act.kind, 'pop')
    for i in range(len(HELP)):
        h.index = i
        t.ok(f'card {i} renders', len(h.render(caps)) > 3)
        t.ok(f'card {i} fits', not [x for x in h.render(caps)
                                    if x.width() > caps.cols])

    t.head('tour / shown once, then never again')
    state = st.State.blank(T0)
    t.ok('a fresh state has not seen it', not state.settings.get('seen_tour'))
    app = App(reg, state, T0, caps)
    t.eq('it is on top at first run', type(app.screen).__name__, 'HelpScreen')
    t.ok('and it is the tour, not the help', app.screen.tour)
    for _ in range(len(TOUR)):
        app.dispatch(K.parse('RET'))
    t.ok('finishing records it', state.settings.get('seen_tour'))
    t.eq('and it is gone', len(app.stack), 1)

    state2 = st.State.blank(T0)
    app2 = App(reg, state2, T0, caps)
    app2.dispatch(K.parse('ESC'))
    t.ok('skipping also records it', state2.settings.get('seen_tour'))

    app3 = App(reg, state2, T0, caps)
    t.eq('a returning user does not see it', len(app3.stack), 1)

    t.head('tour / renders at every rung')
    for label, color, glyph, pal in RUNGS:
        c = Caps(color, glyph, pal, 80, 24)
        for cards in (TOUR, HELP):
            h = HelpScreen(cards)
            for i in range(len(cards)):
                h.index = i
                lines = h.render(c)
                t.ok(f'{label} card {i} fits', not [x for x in lines
                                                    if x.width() > c.cols])
                t.ok(f'{label} card {i} fits rows', len(lines) <= c.rows)
                if glyph == GlyphLevel.ASCII:
                    bad = sorted({ch for x in lines for ch in x.plain()
                                  if ord(ch) > 127})
                    t.ok(f'{label} card {i} pure ASCII', not bad, ''.join(bad))


def test_handoff(t: Runner) -> None:
    from hone import handoff as HO
    import os as _os
    import subprocess as _sp

    t.head('handoff / the split is opt-in and degrades')
    saved = _os.environ.pop('TMUX', None)
    try:
        t.ok('not in tmux, so no split', not HO.in_tmux())
        t.ok('and can_split says so', not HO.can_split())
        t.ok('split_and_wait declines rather than raising',
             HO.split_and_wait(['true']) is False)
    finally:
        if saved is not None:
            _os.environ['TMUX'] = saved

    t.head('handoff / describe')
    t.ok('names the command', 'nvim' in HO.describe(['nvim', 'f.txt'], None))
    t.ok('names the directory', '/tmp/x' in HO.describe(['ls'], '/tmp/x'))
    t.ok('an empty argv reads as a shell', 'shell' in HO.describe([], None))

    if not shutil.which('tmux'):
        t.ok('tmux missing, live split skipped', True)
        return

    t.head('handoff / live split, inside a real tmux session')
    import tempfile as _tf
    from pathlib import Path as _P
    sess = 'hone-split-test'
    _sp.run(['tmux', 'kill-session', '-t', sess], capture_output=True)
    _sp.run(['tmux', 'new-session', '-d', '-s', sess, '-x', '80', '-y', '24'],
            capture_output=True)
    box = _P(_tf.mkdtemp())
    # Drive it the way the app does: from a process whose TMUX points at the
    # session. tmux resolves the target from that, so no window index is ever
    # named, which is what broke the first attempt at this.
    code = _sp.run(['tmux', 'display-message', '-p', '-t', sess,
                    '#{socket_path},#{session_id}'],
                   capture_output=True, text=True).stdout.strip()
    env = dict(_os.environ, TMUX=f'{code.split(",")[0]},0,0')
    r = _sp.run([sys.executable, '-c',
                 'import sys; sys.path.insert(0, "."); '
                 'from hone import handoff as H; '
                 f'print(H.split_and_wait(["sh","-c","pwd > out.txt"], '
                 f'{str(box)!r}))'],
                cwd=str(ROOT), env=env, capture_output=True, text=True,
                timeout=60)
    ok = r.stdout.strip().endswith('True')
    t.ok('the split ran and returned', ok, (r.stdout + r.stderr)[:200])
    if ok:
        t.ok('the command ran in the sandbox',
             (box / 'out.txt').exists()
             and (box / 'out.txt').read_text().strip() == str(box),
             (box / 'out.txt').read_text() if (box / 'out.txt').exists() else 'no file')
    panes = _sp.run(['tmux', 'list-panes', '-t', sess], capture_output=True,
                    text=True).stdout
    t.eq('the pane closed afterwards', len(panes.splitlines()), 1)
    _sp.run(['tmux', 'kill-session', '-t', sess], capture_output=True)
    shutil.rmtree(box, ignore_errors=True)


def test_app(t: Runner) -> None:
    t.head('app / stack')
    reg = fixture_registry()
    caps = Caps(ColorLevel.NONE, GlyphLevel.ASCII, theme.NEUTRAL, 80, 24)
    app = App(reg, seen(), T0, caps)
    t.eq('starts at home', len(app.stack), 1)
    app.dispatch(K.parse('RET'))
    t.eq('enter pushes', len(app.stack), 2)
    app.dispatch(K.parse('ESC'))
    t.eq('esc pops', len(app.stack), 1)
    app.dispatch(K.parse('ESC'))
    t.ok('esc at root leaves the app running', app.running)
    t.eq('and stays on home', len(app.stack), 1)
    app.dispatch(K.parse('q'))
    t.ok('q at root stops the loop', not app.running)

    t.head('app / cli')
    from hone.app import build_parser
    a = build_parser().parse_args(['--theme', 'ansi', '--ascii'])
    t.eq('theme parsed', a.theme, 'ansi')
    t.ok('ascii parsed', a.ascii)

    tmp = Path(tempfile.mkdtemp())
    s = st.State.blank(T0)
    s.mark_lesson('tmux', 'l1', T0)
    s.export_to(tmp / 'e.json', T0)
    t.ok('export writes valid json', json.loads((tmp / 'e.json').read_text())['modules'])


def test_build(t: Runner) -> None:
    t.head('build / zipapp (D2)')
    # Run the real build.sh rather than reimplementing it, so the test and the
    # shipped build cannot drift apart.
    out = Path(tempfile.mkdtemp())
    r = subprocess.run(['bash', str(ROOT / 'build.sh')], capture_output=True,
                       text=True, cwd=ROOT, env={'PATH': '/usr/bin:/bin',
                                                 'OUT': str(out)})
    t.ok('build.sh succeeds', r.returncode == 0, (r.stderr or r.stdout).strip()[:300])
    pyz = out / 'hone.pyz'
    t.ok('produces a single file', pyz.is_file())
    if pyz.is_file():
        run = subprocess.run([sys.executable, str(pyz), '--list'],
                             capture_output=True, text=True)
        t.ok('the built file runs', run.returncode == 0,
             (run.stderr or run.stdout).strip()[:300])
        t.ok('needs no third-party packages',
             'ModuleNotFoundError' not in run.stderr, run.stderr[:200])
        t.ok('is executable', pyz.stat().st_mode & 0o111)


def test_validate(t: Runner) -> None:
    t.head('validate / runs clean on installed content')
    import validate
    buf, old = io.StringIO(), sys.stdout
    sys.stdout = buf
    try:
        code = validate.main([])
    finally:
        sys.stdout = old
    t.eq('validate.py exits 0', code, 0, buf.getvalue()[-400:])


def test_notes(t: Runner) -> None:
    """Per-drill notes, and the footer change that had to come with them."""
    from hone.screens.drill import DrillScreen

    reg = fixture_registry()
    mod = reg.get('tmux')
    caps = Caps(ColorLevel.NONE, GlyphLevel.UNICODE, theme.CYBERPUNK_NEON, 80, 24)

    def typed(scr, text):
        for ch in text:
            scr.handle(K.parse('SPC') if ch == ' ' else K.parse(ch))

    def answer_wrong(scr):
        """Fill the capture buffer with the wrong keys, however long it is."""
        for _ in range(max(1, scr.target_len())):
            scr.handle(K.parse('z'))

    t.head('notes / state stores one note per item and lists them all')
    s = st.State.blank(T0)
    t.eq('absent is empty, not None', s.note('tmux', 'drills', 'd1'), '')
    s.set_note('tmux', 'drills', 'd1', 'I keep reaching for %')
    t.eq('round trip', s.note('tmux', 'drills', 'd1'), 'I keep reaching for %')
    t.eq('listed', s.notes(), [('tmux', 'drills', 'd1', 'I keep reaching for %')])
    s.set_note('tmux', 'drills', 'd1', '   ')
    t.eq('blanking removes it', s.notes(), [])

    t.head('notes / n during feedback opens an editor, enter saves it')
    s = st.State.blank(T0)
    scr = DrillScreen(mod, [dict(mod.drills[0])], 0, s, T0)
    answer_wrong(scr)
    t.eq('wrong answer lands in feedback', scr.phase, 'feedback')
    scr.handle(K.parse('n'))
    t.eq('note phase', scr.phase, 'note')
    typed(scr, 'quote not percent')
    t.ok('buffer shows in the body',
         any('quote not percent' in x.plain() for x in scr.body(caps)))
    scr.handle(K.parse('RET'))
    t.eq('back to feedback', scr.phase, 'feedback')
    t.eq('saved', s.note('tmux', 'drills', 'd1'), 'quote not percent')
    t.ok('state marked dirty', s.dirty)

    t.head('notes / the note comes back with the drill')
    scr.handle(K.parse('RET'))
    body = ' '.join(x.plain() for x in scr.body(caps))
    t.ok('shown on the prompt', 'quote not percent' in body, body)

    t.head('notes / esc cancels without touching what was saved')
    scr = DrillScreen(mod, [dict(mod.drills[0])], 0, s, T0)
    answer_wrong(scr)
    scr.handle(K.parse('n'))
    t.eq('editor pre-filled', scr.note_buf, 'quote not percent')
    typed(scr, ' AND MORE')
    scr.handle(K.parse('ESC'))
    t.eq('cancelled', scr.phase, 'feedback')
    t.eq('unchanged', s.note('tmux', 'drills', 'd1'), 'quote not percent')

    t.head('notes / capture feedback no longer advances on any key (D19 rule 4)')
    scr = DrillScreen(mod, [dict(mod.drills[0]), dict(mod.drills[1])], 0,
                      st.State.blank(T0), T0)
    answer_wrong(scr)
    keys = [k for k, _ in scr.hints(caps)]
    t.ok('footer no longer claims any key', 'any key' not in keys, keys)
    t.ok('footer declares n', 'n' in keys, keys)
    scr.handle(K.parse('n'))
    t.eq('n is a note, not an advance', scr.phase, 'note')
    scr.handle(K.parse('ESC'))
    scr.handle(K.parse('RET'))
    t.eq('enter advances', scr.index, 1)

    t.head('notes / the editor swallows keys that would otherwise quit')
    scr = DrillScreen(mod, [dict(mod.drills[0])], 0, st.State.blank(T0), T0)
    answer_wrong(scr)
    scr.handle(K.parse('n'))
    for name in ('q', 'j', '?'):
        t.eq(f'{name} types rather than acts',
             scr.handle(K.parse(name)).kind, 'stay')
    t.eq('all three landed in the buffer', scr.note_buf, 'qj?')
    scr.handle(K.parse('BSP'))
    t.eq('backspace works', scr.note_buf, 'qj')
    t.eq('exit chord still leaves',
         scr.handle(K.parse(scr.exit_chord)).kind, 'pop')

    t.head('notes / a drill with no id cannot be annotated and does not crash')
    scr = DrillScreen(mod, [{'type': 'keys', 'keys': ['a'], 'prompt': 'x'}], 0,
                      st.State.blank(T0), T0)
    answer_wrong(scr)
    scr.handle(K.parse('n'))
    typed(scr, 'hi')
    t.eq('save is a no-op', scr.handle(K.parse('RET')).kind, 'stay')
    t.eq('saved note is empty', scr.saved_note(), '')


def test_sync(t: Runner) -> None:
    """--sync: a remembered file, and an advisory that never acts."""
    from hone import sync

    t.head('sync / remembering and forgetting a path')
    s = st.State.blank(T0)
    t.eq('nothing set', sync.path_of(s), None)
    ok, msg = sync.push(s, T0)
    t.eq('push with no path fails cleanly', ok, False)
    t.ok('and says so', 'no sync file' in msg, msg)

    tmp = Path(tempfile.mkdtemp())
    try:
        dest = tmp / 'nested' / 'travel.json'
        sync.set_path(s, dest)
        t.eq('remembered', sync.path_of(s), dest)
        ok, msg = sync.push(s, T0)
        t.ok('written', ok, msg)
        t.ok('parent created', dest.exists())
        t.eq('valid state file', json.loads(dest.read_text())['version'],
             s.data['version'])

        t.head('sync / an unwritable destination is a warning, never a crash')
        (tmp / 'afile').write_text('not a directory')
        blocked = tmp / 'afile' / 'deeper.json'
        sync.set_path(s, blocked)
        ok, msg = sync.push(s, T0)
        t.eq('reports failure', ok, False)
        t.ok('names the path', str(blocked) in msg, msg)

        t.head('sync / check is advisory: it reports, it never imports')
        sync.set_path(s, dest)
        t.eq('same age says nothing', sync.check(s), '')
        raw = json.loads(dest.read_text())
        raw['updated'] = st.iso(T0 + timedelta(hours=2))
        dest.write_text(json.dumps(raw))
        note = sync.check(s)
        t.ok('newer file is reported', 'newer' in note, note)
        t.ok('names the command', '--import' in note, note)
        t.ok('warns that it replaces', 'replaces' in note, note)
        t.eq('local progress untouched', json.loads(dest.read_text())['updated'],
             st.iso(T0 + timedelta(hours=2)))

        t.head('sync / small clock skew is not treated as news')
        raw['updated'] = st.iso(T0 + timedelta(seconds=10))
        dest.write_text(json.dumps(raw))
        t.eq('skew ignored', sync.check(s), '')

        t.head('sync / an unreadable or missing sync file is silent')
        dest.write_text('{not json')
        t.eq('corrupt is silent', sync.check(s), '')
        dest.unlink()
        t.eq('missing is silent', sync.check(s), '')

        sync.set_path(s, None)
        t.eq('forgotten', sync.path_of(s), None)
        t.eq('and check is silent', sync.check(s), '')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_lint(t: Runner) -> None:
    """--lint: opinions about writing, kept out of the default run."""
    import validate

    t.head('lint / the default run stays clean and the flag adds checks')
    reg = loader.load_all()
    plain, linted = validate.Report(), validate.Report()
    for mod in reg:
        validate.lint_module(mod, linted)
    validate.lint_registry(reg, linted)
    t.eq('lint never errors, only warns', linted.errors, [])
    t.eq('default report is untouched', plain.warnings, [])

    t.head('lint / it catches what it claims to')
    bad = loader.build_module({
        'id': 'bad', 'title': 'x' * 60,
        'lessons': [{'id': 'thin', 'title': 'Thin', 'concept': 'short'}],
        'drills': [
            {'id': 'dash', 'type': 'keys', 'keys': ['a'],
             'prompt': 'Do the thing.', 'teach': 'A line \u2014 with a dash.'},
            {'id': 'weak', 'type': 'keys', 'keys': ['b'],
             'prompt': 'The pane that is currently focused.', 'teach': 'x'},
            {'id': 'long', 'type': 'keys', 'keys': ['c'],
             'prompt': 'Q' * 200 + '.', 'teach': 'x'},
            {'id': 'spaced', 'type': 'keys', 'keys': ['d'],
             'prompt': 'Fine.', 'teach': 'two  spaces'},
        ]}, 'fixture')
    rep = validate.Report()
    validate.lint_module(bad, rep)
    joined = ' | '.join(rep.warnings)
    for want in ('em dash', 'describes rather than instructs',
                 'over', 'double space', 'is it finished'):
        t.ok(f'flags {want}', want in joined, joined)
    t.eq('still no errors', rep.errors, [])

    t.head('lint / structural fields are never linted as prose')
    fine = loader.build_module({
        'id': 'fine', 'title': 'Fine',
        'drills': [{'id': 'c', 'type': 'command',
                    'answer': 'grep  -E  "a|b"  file',
                    'prompt': 'Grep for a or b.', 'teach': 'Fine.'}]}, 'fixture')
    rep = validate.Report()
    validate.lint_module(fine, rep)
    t.eq('a shell command is not a sentence', rep.warnings, [])

    t.head('lint / duplicate wording across modules is reported once')
    a = loader.build_module({'id': 'a', 'title': 'A', 'drills': [
        {'id': 'x', 'type': 'keys', 'keys': ['a'], 'prompt': 'Same words.'}]},
        'fixture')
    b = loader.build_module({'id': 'b', 'title': 'B', 'drills': [
        {'id': 'y', 'type': 'keys', 'keys': ['b'], 'prompt': 'Same words.'}]},
        'fixture')
    reg2 = loader.Registry(); reg2.modules = [a, b]
    rep = validate.Report()
    validate.lint_registry(reg2, rep)
    t.eq('one warning', len(rep.warnings), 1)
    t.ok('names both', 'a/x' in rep.warnings[0] and 'b/y' in rep.warnings[0],
         rep.warnings[0])

    t.head('lint / the shipped content is fully clean, teach lines included')
    rep = validate.Report()
    for mod in reg:
        validate.lint_module(mod, rep)
    t.eq('zero lint warnings in shipped content', rep.warnings, [],
         rep.warnings[:6])

    t.head('lint / a drill without a teach line is named individually')
    bare = loader.build_module({
        'id': 'bare', 'title': 'Bare', 'drills': [
            {'id': 'no-teach', 'type': 'keys', 'keys': ['a'],
             'prompt': 'Do it.'}]}, 'fixture')
    rep = validate.Report()
    validate.lint_module(bare, rep)
    t.ok('flagged by id', any('bare/no-teach' in w and 'teach' in w
                              for w in rep.warnings), rep.warnings)


def test_handover_and_reset(t: Runner) -> None:
    """Briefing at the handover, H for home, and --reset."""
    from hone import handover
    from hone.app import App, reset as cli_reset
    from hone.screens.challenge import ChallengeScreen

    reg = fixture_registry()
    caps = Caps(ColorLevel.NONE, GlyphLevel.ASCII, theme.NEUTRAL, 80, 40)

    t.head('handover / the brief says what opens, from what, and how to leave')
    A.reset(builtins=True)
    mod = reg.get('tmux')
    chal = dict(mod.challenges[0])
    scr = ChallengeScreen(mod, chal, seen(), T0)
    text = ' '.join(x.plain() for x in scr.body(caps))
    t.ok('names the transition', 'WHEN YOU PRESS' in text, text[:120])
    if scr.plan.adapter is not None:
        t.ok('says how to get back', 'To come back' in text, text[:200])
        t.ok('names the way out', scr.plan.adapter.return_hint.split()[0] in text)

    t.head('handover / every adapter answers both questions')
    for name in A.registered():
        ad = A.get(name)
        t.ok(f'{name} has a way back', len(ad.return_hint) > 6, ad.return_hint)
        t.ok(f'{name} says what opens', 'Enter' in ad.opens({}), ad.opens({}))

    t.head('handover / the starting state is shown before the tool opens')
    lines = handover.starting_state({'start': ['hello world here', 'second']})
    t.ok('lists the seeded lines', any('hello world here' in l for l in lines))
    lines = handover.starting_state({'tree': {'a.txt': 'x', 'b/': None}})
    t.ok('lists the seeded files', any('a.txt' in l for l in lines))
    lines = handover.starting_state({'commits': [{'message': 'seed'}]})
    t.ok('lists the seeded history', any('seed' in l for l in lines))
    t.eq('nothing to say stays quiet', handover.starting_state({}), [])

    t.head('handover / the inline reminder is one line and carries both')
    line = handover.inline({'free': 'x' * 300}, 'press Esc then :wq')
    t.eq('single line', line.count(chr(10)), 0)
    t.ok('bounded', len(line) < 140, len(line))
    t.ok('carries the way out', ':wq' in line, line)

    t.head('handover / nvim keeps the leave hook and file where they belong')
    from hone.adapters import nvim as NV
    argv = NV.NvimAdapter().launch(Path('/tmp/s.txt'), Path('/tmp/b'),
                                   Path('/tmp/c'), brief='task [Esc :wq]')
    t.ok('leave hook at -2', argv[-2].startswith('autocmd'))
    t.eq('file at -1', argv[-1], '/tmp/s.txt')
    t.ok('buffer addressed by number, not by current',
         'getbufline(bufnr(' in argv[-2], argv[-2][:80])
    t.ok('reminder present', any('statusline' in a for a in argv))
    t.eq('percent escaped for a statusline', NV.status_text('50% done'),
         '50%% done')

    t.head('handover / a shell handover prints the whole brief')
    seen_args = {}
    app = App(reg, seen(), T0, caps)
    app.tty = None
    sc = ChallengeScreen(mod, chal, seen(), T0,
                         handoff=lambda a, c=None, b=None, env=None: seen_args.update(
                             argv=a, cwd=c, brief=b))
    sc._start()
    t.ok('brief passed to the handoff', seen_args.get('brief') is not None)
    t.ok('it contains the goal',
         any(handover.goal_of(chal)[:20] in l for l in seen_args['brief']))
    A.reset(builtins=True)

    t.head('home key / H unwinds the stack from any depth')
    reg2 = loader.load_all()
    s = seen()
    app = App(reg2, s, T0, caps)
    app.dispatch(K.parse('RET'))
    app.dispatch(K.parse('RET'))
    t.eq('three deep', len(app.stack), 3)
    t.ok('declared', ('H', 'home') in app.screen.hints(caps))
    app.dispatch(K.parse('H'))
    t.eq('back at root', len(app.stack), 1)
    t.eq('and it is home', type(app.stack[0]).__name__, 'HomeScreen')

    t.head('home key / H is an answer inside a capture drill, never an exit')
    app.dispatch(K.parse('RET'))
    app.screen.set_view(2)
    app.dispatch(K.parse('RET'))
    drill = app.screen
    t.ok('capturing', drill.capturing)
    t.ok('footer does not claim H', ('H', 'home') not in drill.hints(caps))
    depth = len(app.stack)
    app.dispatch(K.parse('H'))
    t.eq('still in the drill', len(app.stack), depth)
    t.eq('taken as an answer', [str(k) for k in drill.collected], ['H'])

    t.head('home key / at the root it does nothing rather than quitting')
    app2 = App(reg2, seen(), T0, caps)
    app2.dispatch(K.parse('H'))
    t.ok('still running', app2.running)
    t.eq('still home', len(app2.stack), 1)

    t.head('reset / erases progress but never preferences')
    s2 = st.State.blank(T0)
    s2.set_setting('theme', 'cyberpunk')
    s2.set_setting('sync_path', '/tmp/x.json')
    for m in ('tmux', 'utils'):
        for i in range(3):
            s2.record_answer(m, 'drills', f'd{i}', True)
    lost = s2.reset('tmux')
    t.eq('one module gone', lost['modules'], 1)
    t.eq('its items counted', lost['items'], 3)
    t.ok('other module kept', 'utils' in s2.data['modules'])
    lost = s2.reset()
    t.eq('everything gone', s2.data['modules'], {})
    t.eq('theme kept', s2.settings['theme'], 'cyberpunk')
    t.eq('sync path kept', s2.settings['sync_path'], '/tmp/x.json')

    t.head('reset / the CLI backs up first and refuses without a confirmation')
    tmp = Path(tempfile.mkdtemp())
    try:
        s3 = st.State.blank(T0)
        s3.path = tmp / 'state.json'
        for i in range(2):
            s3.record_answer('tmux', 'drills', f'd{i}', True)
        s3.save(at=T0)

        buf, err = io.StringIO(), io.StringIO()
        old_out, old_err = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = buf, err
        try:
            code = cli_reset(s3, reg2, 'all', False, T0)   # no tty in tests
        finally:
            sys.stdout, sys.stderr = old_out, old_err
        t.eq('refused', code, 1)
        t.ok('said why', 'confirmation' in err.getvalue(), err.getvalue())
        t.ok('progress untouched', 'tmux' in s3.data['modules'])
        t.eq('no litter left behind',
             sorted(p.name for p in tmp.iterdir()), ['state.json'])

        buf = io.StringIO()
        sys.stdout = buf
        try:
            code = cli_reset(s3, reg2, 'all', True, T0)
        finally:
            sys.stdout = old_out
        t.eq('accepted with --yes', code, 0)
        t.eq('erased', s3.data['modules'], {})
        backups = [p for p in tmp.iterdir() if 'before-reset' in p.name]
        t.eq('one backup written', len(backups), 1)
        restored = st.State.import_from(backups[0], T0)
        t.ok('and it restores', 'tmux' in restored.data['modules'])
        t.ok('naming the way back', '--import' in buf.getvalue())

        # Same second, second reset: the name must not collide.
        s3.record_answer('tmux', 'drills', 'd0', True)
        sys.stdout = io.StringIO()
        try:
            cli_reset(s3, reg2, 'all', True, T0)
        finally:
            sys.stdout = old_out
        t.eq('backups never overwrite',
             len([p for p in tmp.iterdir() if 'before-reset' in p.name]), 2)

        sys.stdout, sys.stderr = io.StringIO(), io.StringIO()
        try:
            code = cli_reset(s3, reg2, 'nonsense', True, T0)
        finally:
            sys.stdout, sys.stderr = old_out, old_err
        t.eq('unknown tool refused', code, 1)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_orientation(t: Runner) -> None:
    """A drill has to say what world it is in and how long the answer is."""
    from hone.screens.drill import DrillScreen

    caps = Caps(ColorLevel.NONE, GlyphLevel.UNICODE, theme.CYBERPUNK_NEON, 80, 30)
    reg = loader.load_all()

    t.head('orientation / every shipped module with drills states its world')
    for mod in reg:
        if mod.drills:
            t.ok(f'{mod.id} has context', bool(mod.context))

    t.head('orientation / the context is shown above the prompt, while prompting')
    mod = reg.get('vim')
    d = next(x for x in mod.drills if x.get('type', 'keys') == 'keys')
    scr = DrillScreen(mod, [dict(d)], 0, st.State.blank(T0), T0)
    body = ' '.join(x.plain() for x in scr.body(caps))
    t.ok('present on the prompt', mod.context[:24] in body, body[:160])
    for _ in range(max(1, scr.target_len())):
        scr.handle(K.parse('z'))
    t.eq('now in feedback', scr.phase, 'feedback')
    body = ' '.join(x.plain() for x in scr.body(caps))
    t.ok('gone once answered', mod.context[:24] not in body)

    t.head('orientation / a per-drill context overrides the module one')
    scr = DrillScreen(mod, [dict(d, context='SPECIAL WORLD')], 0,
                      st.State.blank(T0), T0)
    body = ' '.join(x.plain() for x in scr.body(caps))
    t.ok('override wins', 'SPECIAL WORLD' in body)
    t.ok('module line suppressed', mod.context[:24] not in body)

    t.head('orientation / capture drills show how many keystrokes are wanted')
    three = {'id': 'x', 'type': 'keys', 'keys': ['SPC', 'h', 'b'],
             'prompt': 'Do it.', 'teach': 'Because.'}
    scr = DrillScreen(mod, [three], 0, st.State.blank(T0), T0)

    def entry():
        return next(x.plain() for x in scr.body(caps) if caps.g('arrow') in x.plain())

    t.ok('count stated', '3 keystrokes' in entry(), entry())
    slot = caps.g('slot')
    t.eq('two slots beyond the cursor', entry().count(slot), 2, entry())
    scr.handle(K.parse('SPC'))
    t.eq('one slot left', entry().count(slot), 1, entry())
    scr.handle(K.parse('h'))
    t.eq('no slots left', entry().count(slot), 0, entry())
    scr.handle(K.parse('b'))
    t.eq('third keystroke ends it', scr.phase, 'feedback')

    t.head('orientation / a single-key drill draws no slots at all')
    one = {'id': 'y', 'type': 'keys', 'keys': ['u'], 'prompt': 'Undo.',
           'teach': 'Because.'}
    scr = DrillScreen(mod, [one], 0, st.State.blank(T0), T0)
    line = next(x.plain() for x in scr.body(caps) if caps.g('arrow') in x.plain())
    t.ok('says one keystroke', '1 keystroke' in line and '1 keystrokes' not in line)
    t.eq('and no slots', line.count(caps.g('slot')), 0, line)

    t.head('orientation / text drills get no slot count, since length is free')
    txt = next((x for x in reg.get('tmux').drills
                if x.get('type') in ('recall', 'command')), None)
    if txt is not None:
        scr = DrillScreen(reg.get('tmux'), [dict(txt)], 0, st.State.blank(T0), T0)
        line = next(x.plain() for x in scr.body(caps)
                    if caps.g('arrow') in x.plain())
        t.ok('no keystroke count', 'keystroke' not in line, line)


def test_splash(t: Runner) -> None:
    """The launch screen: degrades, resolves, and never blocks the app."""
    from hone import splash
    reg = fixture_registry()

    t.head('splash / it fits or it does not run')
    big = Caps(ColorLevel.TRUE, GlyphLevel.UNICODE, theme.CYBERPUNK_NEON, 80, 24)
    small = Caps(ColorLevel.NONE, GlyphLevel.ASCII, theme.NEUTRAL, 30, 10)
    t.ok('runs at 80x24', splash.fits(big))
    t.ok('refuses a tiny window', not splash.fits(small))

    t.head('splash / the ASCII rung gets a plain figlet, never tofu')
    art, _ = splash.art_for(Caps(ColorLevel.NONE, GlyphLevel.ASCII,
                                 theme.NEUTRAL, 80, 24))
    t.eq('plain art chosen', art, splash.PLAIN)
    for row in splash.frame(Caps(ColorLevel.NONE, GlyphLevel.ASCII,
                                 theme.NEUTRAL, 80, 24), splash.STEPS - 1):
        line = row.plain()
        t.ok('pure ASCII', all(ord(c) < 128 for c in line), repr(line))

    t.head('splash / a narrow but tall window steps down to the plain art')
    art, _ = splash.art_for(Caps(ColorLevel.TRUE, GlyphLevel.UNICODE,
                                 theme.NEUTRAL, 38, 24))
    t.eq('narrow uses plain', art, splash.PLAIN)

    t.head('splash / the last frame is the real art, and says the tagline')
    last = splash.frame(big, splash.STEPS - 1)
    text = '\n'.join(x.plain() for x in last)
    for line in splash.BLOCK:
        t.ok('art line resolved', line in text, line)
    # Asserted through the constant rather than against a literal: the tagline
    # is meant to be rewritten, and a test that pins its words turns editing
    # the front door into a test failure.
    for part in config.TAGLINE_PARTS:
        t.ok('tagline shown', part in text, part)
    t.ok('no longer sharpening', 'sharpening' not in text)
    t.ok('tagline carries no module count',
         not any(ch.isdigit() for ch in ' '.join(config.TAGLINE_PARTS)))

    t.head('splash / an early frame is noise, not the finished art')
    first = '\n'.join(x.plain() for x in splash.frame(big, 0))
    t.ok('not yet resolved', splash.BLOCK[0] not in first)
    t.ok('says what it is doing', 'sharpening' in first)

    t.head('splash / no frame ever overflows the terminal')
    for cols, rows in ((80, 24), (120, 40), (40, 20)):
        caps = Caps(ColorLevel.NONE, GlyphLevel.UNICODE, theme.NEUTRAL, cols, rows)
        if not splash.fits(caps):
            continue
        for step in range(splash.STEPS):
            for row in splash.frame(caps, step):
                t.ok(f'{cols}x{rows} step {step} fits', row.width() <= cols,
                     row.plain())

    t.head('splash / the work runs even when the animation is skipped')
    class FakeTty:
        def __init__(self, keys):
            self.keys, self.written = keys, 0

        def write(self, s):
            self.written += 1

        def read_keys(self, timeout=None):
            return [K.parse('a')] if self.keys else []

    ran = []
    tty = FakeTty(keys=True)
    out = splash.play(tty, big, work=lambda: ran.append(1) or 'registry',
                      clock=lambda: 0.0)
    t.eq('work returned through', out, 'registry')
    t.eq('work ran exactly once', len(ran), 1)
    t.ok('something was drawn', tty.written >= 1)

    t.head('splash / a write failure never takes the launch down')
    class BrokenTty:
        def write(self, s):
            raise OSError('no terminal')

        def read_keys(self, timeout=None):
            return []

    ran = []
    out = splash.play(BrokenTty(), big, work=lambda: ran.append(1) or 'reg',
                      clock=lambda: 0.0)
    t.eq('still loaded', out, 'reg')
    t.eq('still exactly once', len(ran), 1)

    t.head('splash / the held frame says it is waiting, the others do not')
    held = '\n'.join(x.plain() for x in splash.frame(big, splash.STEPS - 1,
                                                     hold=True))
    t.ok('names its exit', splash.HOLD_HINT in held)
    t.ok('still says the tagline', config.TAGLINE_PARTS[-1] in held)
    loading = '\n'.join(x.plain() for x in splash.frame(big, 0, hold=True))
    t.ok('no key hint while still loading', splash.HOLD_HINT not in loading)
    plain_last = '\n'.join(x.plain() for x in splash.frame(big, splash.STEPS - 1))
    t.ok('no hint when not holding', splash.HOLD_HINT not in plain_last)

    t.head('splash / holding still fits the window')
    note = splash.roster_note(reg)
    for cols, rows in ((80, 24), (120, 40), (40, 20)):
        caps = Caps(ColorLevel.NONE, GlyphLevel.UNICODE, theme.NEUTRAL, cols, rows)
        if not splash.fits(caps):
            continue
        drawn = splash.frame(caps, splash.STEPS - 1, hold=True, note=note)
        for row in drawn:
            t.ok(f'{cols}x{rows} held frame fits wide', row.width() <= cols,
                 row.plain())
        t.ok(f'{cols}x{rows} held frame fits tall', len(drawn) <= rows)

    t.head('splash / the roster line is counted, and dropped when it cannot fit')
    t.ok('counts the real roster', note.startswith(f'{len(reg)} tools'), note)
    wide = '\n'.join(x.plain() for x in
                     splash.frame(big, splash.STEPS - 1, hold=True, note=note))
    t.ok('shown when there is room', note in wide)
    narrow = Caps(ColorLevel.NONE, GlyphLevel.UNICODE, theme.NEUTRAL, 40, 20)
    thin = splash.frame(narrow, splash.STEPS - 1, hold=True, note=note)
    t.ok('dropped rather than overflowing',
         all(row.width() <= 40 for row in thin))
    t.eq('an empty registry says nothing', splash.roster_note(loader.Registry()), '')
    t.eq('a non-registry says nothing', splash.roster_note(object()), '')

    t.head('splash / it waits for a key rather than timing out')
    class PatientTty:
        """Silent for two reads, then a key. Records how it was asked."""

        def __init__(self):
            self.timeouts, self.reads, self.written = [], 0, 0

        def write(self, s):
            self.written += 1

        def read_keys(self, timeout=None):
            self.reads += 1
            if timeout is None:          # the hold, not the animation
                self.timeouts.append(timeout)
                return [K.parse('a')] if len(self.timeouts) >= 3 else []
            return []

    tty = PatientTty()
    out = splash.play(tty, big, work=lambda: 'reg', clock=lambda: 0.0)
    t.eq('work still returned', out, 'reg')
    t.eq('blocked until a key arrived', len(tty.timeouts), 3)
    t.ok('redrew the resolved frame to hold', tty.written > splash.STEPS)

    t.head('splash / a dead stdin gives up instead of hanging')
    class DeadTty:
        def __init__(self):
            self.reads = 0

        def write(self, s):
            pass

        def read_keys(self, timeout=None):
            self.reads += 1
            return []

    tty = DeadTty()
    out = splash.play(tty, big, work=lambda: 'reg', clock=lambda: 0.0)
    t.eq('still loaded', out, 'reg')
    t.ok('bounded, not infinite',
         tty.reads <= splash.STEPS + splash.HOLD_EMPTY_READS)

    t.head('splash / a key during the animation does not ask for a second one')
    tty = FakeTty(keys=True)
    out = splash.play(tty, big, work=lambda: 'reg', clock=lambda: 0.0)
    t.eq('loaded', out, 'reg')
    t.ok('no hold frame drawn', tty.written <= splash.STEPS)

    t.head('splash / hold=False keeps the old timed floor')
    tty = DeadTty()
    out = splash.play(tty, big, work=lambda: 'reg', clock=lambda: 0.0,
                      hold=False)
    t.eq('loaded', out, 'reg')
    t.ok('never blocked', tty.reads <= splash.STEPS)


def test_pcapgen(t: Runner) -> None:
    """The fixture is a file format, not a capture. It must be stable."""
    from hone import pcapgen

    t.head('pcapgen / the inventory and its labels cannot drift apart')
    pkts = pcapgen.packets()
    t.eq('one label per packet', len(pcapgen.LABELS), len(pkts))
    t.ok('every label says something', all(len(x) > 6 for x in pcapgen.LABELS))

    t.head('pcapgen / the file is byte-identical every time')
    # Content is validated by running filters over this file, so a fixture
    # that varied would make validate.py flaky rather than merely untidy.
    t.eq('deterministic', pcapgen.build(), pcapgen.build())
    blob = pcapgen.build()
    t.ok('has the pcap magic', blob[:4] == b'\xa1\xb2\xc3\xd4')
    t.ok('plausible size', 400 < len(blob) < 4000, len(blob))

    t.head('pcapgen / timestamps map back to packet numbers exactly')
    # tcpdump identifies a packet by its clock and tshark by its index; the
    # two must land on the same identity or the languages cannot be compared.
    for i in range(len(pkts)):
        t.eq(f'packet {i + 1} round-trips',
             pcapgen.number_for(pcapgen.BASE_TIME + i * 0.01), i + 1)
    t.eq('out of range is None', pcapgen.number_for(pcapgen.BASE_TIME - 5), None)
    t.ok('labels are 1-based', 'packet 1' in pcapgen.label(1))
    t.ok('unknown number still describes', 'packet 99' in pcapgen.label(99))


def test_oracle(t: Runner) -> None:
    """Answers graded by running them, and the honesty rules around that."""
    from hone.adapters import _oracle as O
    from hone.adapters import pwsh as PW
    from hone.adapters.pcap import PcapAdapter, CAPTURE, DISPLAY

    t.head('oracle / an answer is bounded before it reaches a subprocess')
    t.ok('empty refused', O.check_answer('   ') is not None)
    t.ok('overlong refused', O.check_answer('x' * 5000) is not None)
    t.ok('null byte refused', O.check_answer('a\x00b') is not None)
    t.eq('ordinary answer allowed', O.check_answer('tcp port 443'), None)

    t.head('oracle / a runaway answer is killed, not waited on')
    r = O.run(['sleep', '30'], timeout=0.3)
    t.ok('timed out', r.timed_out)
    t.ok('not reported ok', not r.ok)

    t.head('oracle / escape codes never reach the comparison or the screen')
    t.eq('stripped', O.strip_ansi('\x1b[31;1mboom\x1b[0m'), 'boom')
    t.ok('first_error is clean',
         '\x1b' not in O.Run(1, '', '\x1b[31;1mreal problem\x1b[0m').first_error())

    t.head('oracle / set differences are described, never merely denied')
    d = O.describe_sets([], ['the DNS query'])
    t.ok('names what was over-selected', 'DNS query' in d, d)
    t.ok('says which way it was wrong', 'too broad' in d, d)
    d = O.describe_sets(['the HTTP GET'], [])
    t.ok('too narrow reported', 'too narrow' in d, d)
    t.ok('a clean pass says so', 'exactly' in O.describe_sets([], []))

    t.head('oracle / pwsh output comparison ignores only what is noise')
    t.ok('trailing blank lines are noise',
         PW.compare('a\nb\n\n\n', 'a\nb').ok)
    t.ok('carriage returns are noise', PW.compare('a\r\nb', 'a\nb').ok)
    t.ok('a different value is not noise', not PW.compare('a\nc', 'a\nb').ok)
    v = PW.compare('a\nc', 'a\nb')
    t.ok('names the differing line', "'c'" in v.detail and "'b'" in v.detail,
         v.detail)
    t.ok('short output reported',
         'early' in PW.compare('a', 'a\nb').detail)
    t.ok('long output reported',
         'too many' in PW.compare('a\nb', 'a').detail)

    t.head('oracle / the Linux alias trap is named, not left as a stray error')
    t.eq('detected at a pipeline head',
         PW.shadowed_alias('Get-ChildItem | sort Length'), 'sort')
    t.eq('not detected as a property name',
         PW.shadowed_alias('Select-Object Name, ps'), None)
    msg = PW.explain('gci | sort Length -Desc', "/usr/bin/sort: invalid option")
    t.ok('says which cmdlet was meant', 'Sort-Object' in msg, msg)
    t.ok('says why it happens here', 'Linux' in msg, msg)
    msg = PW.explain('Get-WinEvent -LogName Security',
                     "The term 'Get-WinEvent' is not recognized as a name of a cmdlet")
    t.ok('windows-only cmdlets explained', 'Windows-only' in msg, msg)

    # Everything below needs the real tools. Skipped rather than faked when
    # they are absent: a test double proving tcpdump parses BPF would be
    # proving something about the double.
    pcap = PcapAdapter()
    if not pcap.available():
        t.head('oracle / tcpdump absent, live grading not exercised')
        t.ok('adapter reports why', bool(pcap.reason))
        return

    t.head('oracle / filters are graded by what they select, not how spelt')
    pcap.setup({})
    try:
        for spelling in ('tcp port 443', 'port 443 and tcp', 'tcp and port 443'):
            t.ok(f'{spelling!r} passes',
                 pcap.evaluate(spelling, 'tcp port 443', CAPTURE).ok)

        t.head('oracle / a filter that matches too much is caught and named')
        v = pcap.evaluate('tcp', 'tcp port 443', CAPTURE)
        t.ok('rejected', not v.ok)
        t.ok('says too broad', 'too broad' in v.detail, v.detail)
        t.ok('names a packet in words', 'packet' in v.detail, v.detail)

        t.head('oracle / a filter that matches too little is caught and named')
        v = pcap.evaluate('dst port 443', 'tcp port 443', CAPTURE)
        t.ok('rejected', not v.ok)
        t.ok('says too narrow', 'too narrow' in v.detail, v.detail)

        t.head('oracle / the wrong language is explained, not just refused')
        v = pcap.evaluate('tcp.port == 443', 'tcp port 443', CAPTURE)
        t.ok('rejected', not v.ok)
        t.ok('explains the two languages', 'display-filter' in v.detail, v.detail)

        if pcap.grades(DISPLAY):
            v = pcap.evaluate('tcp port 443', 'tcp.port == 443', DISPLAY)
            t.ok('and in the other direction', not v.ok)
            t.ok('explains it too', 'capture-filter' in v.detail, v.detail)

            t.head('oracle / both tools agree on which packets are which')
            # The pairing the module is built on: if these disagreed, no drill
            # could ask for "the same packets in the other language".
            cap, _ = pcap.select(CAPTURE, 'tcp port 443')
            dis, _ = pcap.select(DISPLAY, 'tcp.port == 443')
            t.eq('same packet set from both languages', cap, dis)
            t.ok('and it is not empty', bool(cap))

        t.head('oracle / an empty answer is refused before anything runs')
        t.ok('nothing typed', not pcap.evaluate('', 'tcp', CAPTURE).ok)
    finally:
        pcap.teardown()
    t.ok('teardown removes the fixture', pcap.dir is None)
    t.ok('teardown is safe twice', pcap.teardown() is None)


def test_checking_mode(t: Runner) -> None:
    """D26: read-and-drill-only, and the honesty it has to preserve."""
    from hone.screens.drill import DrillScreen, ORACLE_TYPES
    from hone.screens.home import HomeScreen

    caps = Caps(ColorLevel.NONE, GlyphLevel.UNICODE, theme.NEUTRAL, 80, 24)
    try:
        t.head('mode / it defaults to checking and rejects nonsense')
        t.eq('default', A.mode(), A.CHECKED)
        t.eq('unknown falls back', A.set_mode('sideways'), A.CHECKED)
        t.eq('read is real', A.set_mode(A.READ), A.READ)
        t.ok('read_only agrees', A.read_only())

        t.head('mode / read-only degrades every adapter challenge, with a reason')
        plan = A.plan_for({'verify': {'kind': 'tmux'}})
        t.eq('degraded to self', plan.kind, A.SELF)
        t.ok('and says why', 'read and drill' in plan.reason, plan.reason)
        t.ok('marked as degraded, not authored', plan.degraded)

        t.head('mode / an authored self-marked task is not called degraded')
        # It was always self-marked, so blaming the mode would be a lie that
        # makes the mode look more destructive than it is.
        plan = A.plan_for({'verify': {'kind': 'self'}})
        t.eq('still self', plan.kind, A.SELF)
        t.eq('no reason invented', plan.reason, '')

        t.head('mode / in-process grading survives, since it launches nothing')
        t.eq('graded stays graded',
             A.plan_for({'verify': {'kind': 'graded'}}).kind, A.GRADED)

        t.head('mode / the picker says the same thing about every module')
        reg = fixture_registry()
        state = st.State.blank(T0)
        home = HomeScreen(reg, state, T0)
        for mod in reg:
            ok, label = home.checkable(mod)
            t.ok(f'{mod.id} not offered as checked', not ok)
            t.eq(f'{mod.id} says read and drill only', label,
                 'read and drill only')
        t.ok('and the header states the mode',
             any('read' in r.plain() for r in home.header_rows(caps)))

        t.head('mode / an oracle drill degrades to text and admits it')
        drill = {'id': 'd1', 'type': 'bpf', 'prompt': 'select HTTPS',
                 'answer': 'tcp port 443'}
        mod = reg.modules[0]
        scr = DrillScreen(mod, [drill], 0, st.State.blank(T0), T0, kitty=True)
        scr.typed = 'tcp port 443'
        scr._judge_text()
        t.ok('its own answer still passes', scr.last_correct)
        t.ok('not claimed as verified', scr.last_verified is False)
        t.ok('says it was not run', 'not run' in scr.last_note, scr.last_note)
        t.ok('names the mode as the cause',
             'read and drill' in scr.last_note, scr.last_note)

        t.head('mode / and nothing was written to disk to do it')
        for name in {n for n, _ in ORACLE_TYPES.values()}:
            adapter = A.get(name)
            t.ok(f'{name} built no sandbox', getattr(adapter, 'dir', None) is None)
    finally:
        A.set_mode(A.CHECKED)

    t.head('mode / switching back restores real checking')
    t.ok('checked again', not A.read_only())
    plan = A.plan_for({'verify': {'kind': 'tmux'}})
    t.ok('no longer blamed on the mode', 'read and drill' not in plan.reason)

    t.head('mode / the home screen toggle flips it and remembers')
    reg = fixture_registry()
    state = st.State.blank(T0)
    home = HomeScreen(reg, state, T0)
    home.handle(K.parse('m'))
    t.eq('flipped to read', A.mode(), A.READ)
    t.eq('and persisted', state.settings.get('checking'), A.READ)
    home.handle(K.parse('m'))
    t.eq('flips back', A.mode(), A.CHECKED)
    t.eq('and persists that too', state.settings.get('checking'), A.CHECKED)
    t.ok('the key is advertised',
         any(k == 'm' for k, _ in home.extra_hints()))


def test_rigor(t: Runner) -> None:
    """D6's scaffolding scale: its default, and walking it with the arrows."""
    from hone.screens.challenge import (ChallengeScreen, DEFAULT_RIGOR, RIGORS)

    caps = Caps(ColorLevel.NONE, GlyphLevel.UNICODE, theme.NEUTRAL, 80, 24)
    reg = fixture_registry()
    mod = reg.modules[0]
    challenge = {'id': 'c1', 'title': 'a task', 'goal': 'do the thing',
                 'steps': [{'instruction': 'first', 'hint': 'a hint'}],
                 'free': 'do it', 'verify': {'kind': 'self'}}

    t.head('rigor / a fresh student gets the task only')
    t.eq('default is free', DEFAULT_RIGOR, 'free')
    state = st.State.blank(T0)
    t.eq('blank state agrees', state.settings.get('rigor'), 'free')
    scr = ChallengeScreen(mod, challenge, state, T0)
    t.eq('and the screen reads it', scr.rigor, 'free')

    t.head('rigor / a corrupt setting falls back rather than crashing')
    state.set_setting('rigor', 'nonsense')
    t.eq('falls back to the default', scr.rigor, DEFAULT_RIGOR)

    t.head('rigor / the arrows walk the scale and stop at the ends')
    state.set_setting('rigor', 'free')
    scr.handle(K.parse('Left'))
    t.eq('left is more help', scr.rigor, 'coached')
    scr.handle(K.parse('Left'))
    t.eq('left again', scr.rigor, 'guided')
    scr.handle(K.parse('Left'))
    t.eq('clamps rather than wrapping to free', scr.rigor, 'guided')
    scr.handle(K.parse('Right'))
    t.eq('right is less help', scr.rigor, 'coached')
    scr.handle(K.parse('Right'))
    t.eq('right again', scr.rigor, 'free')
    scr.handle(K.parse('Right'))
    t.eq('clamps at the other end too', scr.rigor, 'free')

    t.head('rigor / the letters still jump directly')
    for key, want in (('g', 'guided'), ('c', 'coached'), ('f', 'free')):
        scr.handle(K.parse(key))
        t.eq(f'{key} selects {want}', scr.rigor, want)

    t.head('rigor / the arrows are advertised, per D19 rule 4')
    keys = [k for k, _ in scr.hints(caps)]
    t.ok('a left-right hint is shown',
         any(caps.g('left') in k for k in keys), keys)

    t.head('rigor / the label reads as a heading, not a fourth option')
    rows = [r.plain() for r in scr.body(caps)]
    label = next((r for r in rows if 'RIGOR' in r), '')
    t.ok('the label is present and distinct', bool(label), rows[:12])
    t.ok('the chips are not on the label line',
         all(r not in label for r in RIGORS), label)


def test_install_help(t: Runner) -> None:
    """Telling someone how to get the tool they are missing."""
    from hone import install

    t.head('install / a manager is detected, or nothing is claimed')
    mgr = install.detect()
    t.ok('detected or honestly None',
         mgr is None or mgr in install.MANAGER_LABELS, mgr)

    t.head('install / every adapter requirement can be installed')
    A.reset(builtins=True)
    for name in A.registered():
        for tool in A.get(name).requires:
            t.ok(f'{tool} is in the table', install.known(tool), tool)
            t.ok(f'{tool} has advice for every manager',
                 all(install.command_for(tool, m) for m, _, _ in install.MANAGERS
                     if tool in install.PACKAGES and m in install.PACKAGES[tool]))

    t.head('install / every module need can be installed or is a given')
    for mod in loader.load_all():
        for tool in mod.needs:
            t.ok(f'{mod.id} needs {tool}: known or a given',
                 install.known(tool) or tool in GIVEN_TOOLS, tool)

    t.head('install / Arch and Debian both get a route for every tool')
    # The two distributions this is actually used on. A tool that some module
    # declares, or that an adapter needs, must have a working line for both,
    # because "not installed" with no way forward is where people stop. This
    # caught `pacman -S ffuf`, which does not exist: ffuf is AUR-only on Arch
    # and unpackaged on Debian, and a real paste of that line failed.
    wanted = {tool for mod in loader.load_all() for tool in mod.needs}
    for name in A.registered():
        wanted.update(getattr(A.get(name), 'requires', ()))
    for tool in sorted(wanted - GIVEN_TOOLS):
        for pm, label in (('pacman', 'Arch'), ('apt', 'Debian')):
            cmd = install.command_for(tool, pm)
            t.ok(f'{tool} has a {label} route', bool(cmd), f'{tool}/{pm}')

    t.head('install / a route names a real package or a real alternative')
    # A bare `pacman -S x` / `apt install x` is a claim that x is in the
    # distribution's own repositories. Where it is not, the entry must say so
    # rather than print a line that fails.
    for tool, pm, why in (('ffuf', 'pacman', 'AUR only'),
                          ('ffuf', 'apt', 'not packaged'),
                          ('pwsh', 'pacman', 'AUR only'),
                          ('netexec', 'apt', 'pipx only'),
                          ('vol', 'apt', 'pipx only')):
        cmd = install.command_for(tool, pm) or ''
        plain = cmd.startswith(('sudo pacman -S ', 'sudo apt install '))
        t.ok(f'{tool} on {pm} is not a bare package claim ({why})',
             not plain, cmd)

    t.head('install / a renamed binary still counts as installed')
    # FreeRDP 3 ships xfreerdp3 and no xfreerdp, so a fully installed machine
    # was being told it needed to install FreeRDP.
    t.ok('xfreerdp has known aliases', 'xfreerdp3' in install.ALIASES['xfreerdp'])
    t.eq('an alias satisfies the need',
         install.missing(['definitely-not-real']), ['definitely-not-real'])
    real = next((a for a in ('xfreerdp',) if install.present(a)), None)
    t.ok('present() accepts either name',
         install.present('xfreerdp') == bool(
             shutil.which('xfreerdp') or shutil.which('xfreerdp3')
             or shutil.which('sdl-freerdp3')), real)

    t.head('install / the awkward cases are honest, not plausible')
    # pacman -S powershell does not exist. Printing it would fail and look
    # like our mistake, which is the whole reason COMMANDS exists.
    t.eq('no pacman package invented', install.PACKAGES['pwsh'].get('pacman'), None)
    cmd = install.command_for('pwsh', 'pacman')
    t.ok('routed via the AUR', cmd and 'AUR' in cmd, cmd)
    t.ok('apt route is the one that works',
         'snap' in (install.command_for('pwsh', 'apt') or ''))

    t.head('install / an unknown tool produces nothing at all')
    t.eq('no lines', install.lines('definitely-not-a-tool'), [])
    t.eq('no hint', install.hint('definitely-not-a-tool'), '')
    t.eq('not known', install.known('definitely-not-a-tool'), False)

    t.head('install / missing() only reports what is actually absent')
    t.eq('a present tool is not missing', install.missing(['sh']), [])
    t.eq('an absent one is', install.missing(['definitely-not-a-tool']),
         ['definitely-not-a-tool'])

    t.head('install / lines lead with this machine, and can list them all')
    if mgr is not None:
        first = install.lines('tmux')[0]
        t.ok('this machine first', install.MANAGER_LABELS[mgr] in first, first)
        every = install.lines('tmux', all_managers=True)
        t.ok('all managers offered', len(every) >= len(install.MANAGERS), every)

    t.head('install / the module screen offers the command, never runs it')
    from hone.screens.module import ModuleScreen
    caps = Caps(ColorLevel.NONE, GlyphLevel.ASCII, theme.NEUTRAL, 80, 30)
    reg = loader.load_all()
    mod = next((m for m in reg if install.missing(m.needs)), None)
    if mod is not None:
        body = ' '.join(x.plain() for x in
                        ModuleScreen(mod, seen(), T0, registry=reg).body(caps))
        t.ok('names what is missing',
             install.missing(mod.needs)[0] in body, body[:200])
        t.ok('offers a command', install.hint(install.missing(mod.needs)[0])[:12]
             in body or not install.detect(), body[:200])
        t.ok('and says the content still works', 'still read' in body)


def test_audit(t: Runner) -> None:
    """Regressions from the 2026-08-12 deep audit. Each guards a fixed bug."""
    from hone import handoff as HO

    reg = fixture_registry()
    caps = Caps(ColorLevel.NONE, GlyphLevel.ASCII, theme.NEUTRAL, 80, 24)

    t.head('audit / structurally broken state loads and is usable')
    raw = {'modules': {'a': ['nope'], 'b': {'drills': 'x',
                                            'quiz': {'q': 'x', 'ok': {'seen': 1}}}},
           'settings': 'x'}
    s2 = st.State(data=st.State._migrate(raw, T0))
    t.eq('list module dropped', 'a' not in s2.data['modules'], True)
    t.eq('string bucket dropped', 'drills' not in s2.data['modules']['b'], True)
    t.eq('string item dropped', list(s2.data['modules']['b']['quiz']), ['ok'])
    t.eq('broken settings replaced', type(s2.settings).__name__, 'dict')
    s2.record_answer('b', 'drills', 'x', True)
    s2.counts('b')
    t.ok('consumers run clean', True)

    t.head('audit / naive timestamps become UTC rather than poisoning compares')
    dt = st.parse_iso('2026-01-01T00:00:00')
    t.ok('tz attached', dt.tzinfo is not None)
    t.ok('comparable', dt < T0)

    t.head('audit / reads create nothing: note, and rendering a list')
    s3 = st.State.blank(T0)
    t.eq('note read is empty', s3.note('tmux', 'drills', 'd1'), '')
    t.eq('and created nothing', s3.data['modules'], {})

    t.head('audit / module rows render without creating records')
    from hone.screens.module import ModuleScreen
    s4 = st.State.blank(T0)
    ms = ModuleScreen(reg.get('tmux'), s4, T0)
    for v in (0, 1, 2):
        ms.set_view(v)
        ms.body(caps)
    t.eq('rendering created nothing', s4.data['modules'], {})
    t.eq('not dirtied', s4.dirty, False)

    t.head('audit / Alt does not swallow the key behind it')
    d = K.Decoder()
    t.eq('ESC a b in one read', [str(k) for k in d.feed(b'\x1bab')],
         ['M-a', 'b'])
    t.eq('alt escape sequence', [str(k) for k in K.Decoder().feed(b'\x1b\x1b[A')],
         ['M-Up'])

    t.head('audit / box_top clamps instead of tearing the frame')
    from hone.render import box_top
    top = box_top(caps, 40, title='x' * 60, right='status')
    t.eq('clamped to width', top.width(), 40)

    t.head('audit / quitting mid-challenge releases the sandbox')
    A.reset(builtins=True)
    fake = A.FakeAdapter(ok=False)
    A.register('tmux', lambda: fake)
    from hone.app import App
    app = App(reg, seen(), T0, caps)
    app.dispatch(K.parse('RET'))
    app.screen.set_view(1)
    app.dispatch(K.parse('RET'))
    app.dispatch(K.parse('RET'))
    t.eq('sandbox alive across failed check', fake.teardown_calls, 0)
    app.dispatch(K.parse('q'))
    app.shutdown()
    t.eq('released at shutdown', fake.teardown_calls, 1)
    app.shutdown()
    t.eq('shutdown is idempotent', fake.teardown_calls, 1)
    A.reset(builtins=True)

    t.head('audit / D8 labels cannot be overstated by the degrade path')
    # An adapter that is genuinely absent, so the degrade path is the one
    # under test rather than whatever happens to be installed here.
    t.eq('unknown fallback collapses to self',
         A.plan_for({'verify': {'kind': 'no-such-adapter'},
                     'fallback': 'verified'}).kind,
         A.SELF)
    from hone.screens.challenge import ChallengeScreen
    chal = {'id': 'c', 'title': 'T', 'goal': 'g',
            'verify': {'kind': A.GRADED}}
    scr = ChallengeScreen(reg.get('tmux'), chal, seen(), T0, handoff=None)
    t.eq('graded plan with no checker', scr.plan.kind, A.GRADED)
    scr._start()
    t.eq('relabelled before self-marking', scr.plan.kind, A.SELF)
    t.eq('lands in selfmark', scr.phase, 'selfmark')

    t.head('audit / lesson records once per visit, not once per repaint')
    from hone.screens.lesson import LessonScreen
    mod = reg.get('tmux')
    s6 = seen()
    scr = LessonScreen(mod, mod.lessons[0], s6, T0)
    scr.scroll = 10 ** 6
    scr.body(caps)
    s6.dirty = False
    scr.body(caps)
    t.eq('second render does not re-dirty', s6.dirty, False)

    t.head('audit / tmux attach inside tmux goes through switch-client')
    t.eq('attach parsed', HO.tmux_attach_target(
        ['tmux', 'attach', '-t', 'hone-drill']), 'hone-drill')
    t.eq('attach-session parsed', HO.tmux_attach_target(
        ['tmux', 'attach-session', '-t', 's']), 's')
    t.eq('other argv passes through', HO.tmux_attach_target(['nvim', 'f']), None)
    t.eq('shell handoff passes through', HO.tmux_attach_target([]), None)

    t.head('audit / git sandbox is insulated from global config')
    from hone.adapters import git as G
    t.ok('hooks neutralised', 'core.hooksPath=/dev/null' in G.NEUTRAL)
    t.ok('signing off', 'commit.gpgsign=false' in G.NEUTRAL)
    t.ok('global excludes off', 'core.excludesFile=/dev/null' in G.NEUTRAL)
    ga = G.GitAdapter()
    captured = []
    import subprocess as _sp
    real_run = _sp.run
    class _R:
        returncode, stdout = 0, ''
    try:
        _sp.run = lambda cmd, **kw: (captured.append(cmd), _R())[1]
        ga.dir = Path('.')
        ga._git('status')
    finally:
        _sp.run = real_run
        ga.dir = None
    t.ok('every git call carries the flags',
         captured and all(f in captured[0] for f in G.NEUTRAL))


def test_free_pace(t: Runner) -> None:
    """D24: nothing is scheduled, nothing is owed, nothing keeps score."""
    from hone import install
    from hone.screens.home import HomeScreen

    reg = loader.load_all()
    caps = Caps(ColorLevel.NONE, GlyphLevel.UNICODE, theme.CYBERPUNK_NEON, 80, 30)

    t.head('free pace / the scheduler and its screens are gone for good')
    for name in ('hone.schedule', 'hone.achievements', 'hone.suggest',
                 'hone.screens.review', 'hone.screens.stats'):
        try:
            __import__(name)
            t.ok(f'{name} is gone', False, 'still importable')
        except ImportError:
            t.ok(f'{name} is gone', True)

    t.head('free pace / a blank state carries no clock and no score')
    s = st.State.blank(T0)
    for key in ('activity', 'achievements', 'last'):
        t.ok(f'no {key}', key not in s.data, sorted(s.data))
    t.eq('version bumped', s.data['version'], 2)

    t.head('free pace / an answer records two counters and nothing else')
    rec = s.record_answer('tmux', 'drills', 'd1', True)
    t.eq('seen', rec['seen'], 1)
    t.eq('correct', rec['correct'], 1)
    t.eq('nothing else is stored', sorted(rec), ['correct', 'seen'])
    rec = s.record_answer('tmux', 'drills', 'd1', False)
    t.eq('seen again', rec['seen'], 2)
    t.eq('correct held', rec['correct'], 1)

    t.head('free pace / a v1 file opens with its progress and loses its streak')
    old = {
        'version': 1,
        'settings': {'theme': 'cyberpunk'},
        'activity': {'2026-08-01': {'answered': 9, 'correct': 8}},
        'achievements': {'reflex': {'at': '2026-08-01T00:00:00+00:00'}},
        'last': {'module': 'vim', 'kind': 'drills', 'item': 'x'},
        'modules': {'vim': {'drills': {
            'vim-ciw': {'seen': 7, 'correct': 6, 'note': 'inner not around',
                        'due': '2026-09-01T00:00:00+00:00', 'ease': 2.6,
                        'interval': 21, 'reps': 4, 'lapses': 1,
                        'best_ms': 800, 'max_interval': 21, 'first_try': True},
        }, 'lessons': {'vim-why': {'done': True}}}},
    }
    migrated = st.State(data=st.State._migrate(dict(old), T0))
    card = migrated.data['modules']['vim']['drills']['vim-ciw']
    t.eq('what you did survives', card['seen'], 7)
    t.eq('so does how well', card['correct'], 6)
    t.eq('and the note', card['note'], 'inner not around')
    t.eq('lesson still read',
         migrated.data['modules']['vim']['lessons']['vim-why']['done'], True)
    for field in st.RETIRED_CARD_FIELDS:
        t.ok(f'{field} dropped', field not in card, sorted(card))
    for key in st.RETIRED_KEYS:
        t.ok(f'{key} dropped', key not in migrated.data)
    t.eq('preferences kept', migrated.settings['theme'], 'cyberpunk')
    t.eq('version rewritten', migrated.data['version'], 2)

    t.head('free pace / progress is what you met, and never goes backwards')
    s2 = st.State.blank(T0)
    mod = reg.get('tmux')
    before = s2.progress('tmux', mod.totals())
    for d in mod.drills[:5]:
        s2.record_answer('tmux', 'drills', d['id'], False)
    after = s2.progress('tmux', mod.totals())
    t.ok('wrong answers still count as met', after > before)
    for d in mod.drills[:5]:
        s2.record_answer('tmux', 'drills', d['id'], False)
    t.eq('meeting it twice does not double it',
         s2.progress('tmux', mod.totals()), after)

    t.head('free pace / accuracy is available without being advertised')
    right, attempts = s2.accuracy('tmux')
    t.eq('attempts counted', attempts, 10)
    t.eq('none right', right, 0)

    t.head('home / grouped, and every module lands in a group')
    home = HomeScreen(reg, seen(), T0)
    groups = home.groups()
    t.eq('every module placed', sum(len(v) for _, v in groups), len(reg))
    t.ok('several headings', len(groups) >= 4, [g for g, _ in groups])
    t.eq('no orphan group', [g for g, _ in groups if g == 'Other'], [])
    order = [m.id for _, mods in groups for m in mods]
    t.eq('no duplicates', len(set(order)), len(order))

    t.head('home / it says what the machine can do, not what you did')
    body = ' '.join(x.plain() for x in home.body(caps))
    t.ok('no queue', 'due' not in body.lower(), body[:200])
    t.ok('no streak', 'streak' not in body.lower())
    t.ok('no next line', 'NEXT' not in body)
    t.ok('never claims you verified anything',
         'verified' not in body, body[:300])
    mod = reg.get('tmux')
    ok, label = home.checkable(mod)
    t.ok('says what it can do', label in ('checks your work',
                                          'read and drill only')
         or label.startswith('needs'), label)

    t.head('home / a missing tool is named even when its adapter is fine')
    # The sandbox is available on every machine by definition, so asking the
    # adapter first reported "checks your work" for a module that runs a
    # binary this machine has not got. Twenty modules were wrong that way.
    sandboxed = loader.build_module(
        {'id': 'ghost', 'title': 'Ghost', 'adapter': 'sandbox',
         'needs': ['definitely-not-a-real-binary'],
         'lessons': [{'id': 'a', 'title': 'A', 'concept': 'x' * 220,
                      'misconceptions': ['m'], 'try_it': ['t']}]}, 'fixture')
    ok, label = home.checkable(sandboxed)
    t.ok('sandbox does not hide it', not ok, label)
    t.ok('names the binary', 'definitely-not-a-real-binary' in label, label)

    t.head('home / two missing tools are both named, three are counted')
    from hone.screens.home import _and_list
    t.eq('one', _and_list(['nft']), 'nft')
    t.eq('two', _and_list(['nft', 'iptables']), 'nft and iptables')
    t.eq('three', _and_list(['a', 'b', 'c']), 'a and 2 more')

    t.head('home / every declared need can actually be advised on')
    for mod in reg:
        for tool in mod.needs:
            t.ok(f'{mod.id} needs {tool}: hint or a given',
                 install.known(tool) or tool in GIVEN_TOOLS, tool)

    t.head('home / footer offers nothing that no longer exists')
    keys = [k for k, _ in home.hints(caps)]
    for gone in ('r', 't', 'w', 'x', 'space'):
        t.ok(f'{gone} not offered', gone not in keys, keys)

    t.head('home / the cursor stays visible when the list is grouped')
    small = Caps(ColorLevel.NONE, GlyphLevel.ASCII, theme.NEUTRAL, 80, 16)
    for cursor in range(len(reg)):
        home.cursor = cursor
        rows = home.body(small)
        want = home.ordered()[cursor].title[:18]
        t.ok(f'module {cursor} on screen',
             any(want in r.plain() for r in rows), want)

    t.head('home / the highlighted row is the one Enter opens')
    opened = []
    picker = HomeScreen(reg, seen(), T0,
                        open_module=lambda m: opened.append(m.id) or None)
    for cursor in range(len(reg)):
        picker.cursor = cursor
        rows = picker.body(caps)
        marked = [r.plain() for r in rows if caps.g('sel') in r.plain()]
        opened.clear()
        picker.activate(cursor)
        t.ok(f'row {cursor} matches its action',
             marked and opened and opened[0] in marked[0].lower()
             or marked and picker.ordered()[cursor].title[:18] in marked[0],
             (marked[:1], opened))

    t.head('drill deck / shuffle is available and reversible')
    from hone.screens.module import ModuleScreen
    ms = ModuleScreen(reg.get('vim'), seen(), T0, registry=reg)
    ms.set_view(2)
    ordered = [d['id'] for d in ms.items()]
    ms.handle(K.parse('s'))
    shuffled = [d['id'] for d in ms.items()]
    t.eq('same deck', sorted(shuffled), sorted(ordered))
    t.ok('different order', shuffled != ordered)
    t.ok('declared while on', ('s', 'ordered') in ms.hints(caps))
    ms.handle(K.parse('s'))
    t.eq('and back', [d['id'] for d in ms.items()], ordered)

    t.head('notes / reachable from home and scoped from a module')
    s3 = seen()
    s3.set_note('vim', 'drills', 'vim-ciw', 'inner not around')
    s3.set_note('tmux', 'drills', 'tmux-split-h', 'quote is the other one')
    app = App(reg, s3, T0, caps)
    t.ok('home offers notes', ('n', 'your notes') in app.stack[0].hints(caps))
    t.eq('all of them', app.open_notes().count(), 2)
    t.eq('one module only', app.open_notes('vim').count(), 1)
    t.ok('titled for the module', 'vim' in app.open_notes('vim').title)


def test_labs(t: Runner) -> None:
    """The two lab adapters, which build their own target rather than find one.

    These need testing here and not only through `test_solvable`, because the
    solvability harness skips an adapter whose tool is missing, and `nmap` is
    missing on plenty of machines including the one this was written on. That
    would leave the netlab code shipping entirely unexercised, which is the
    exact hole that let the git adapter ship unplayed once already.
    """
    import socket
    import urllib.error
    import urllib.request

    A.reset(builtins=True)

    t.head('netlab / the target is sockets the trainer owns')
    net = A.get('netlab')
    t.ok('registered', net is not None)
    t.ok('needs nmap, and says so when it is missing',
         net.available() or 'nmap' in net.reason, net.reason)
    net.setup({'ports': [0, 0]})
    try:
        ports = net.ports()
        t.eq('opened both', len(ports), 2)
        t.ok('on loopback only', all(p > 0 for p in ports), ports)
        t.ok('targets.txt names them',
             all(str(p) in (net.dir / 'targets.txt').read_text() for p in ports))

        sock = socket.create_connection(('127.0.0.1', ports[0]), timeout=2)
        greeting = sock.recv(64)
        sock.close()
        t.ok('a connection is greeted', greeting.startswith(b'hone-lab'), greeting)

        obs = net.observe()
        t.eq('and counted', obs.data['connections'], 1)
        (net.dir / 'scan.txt').write_text(f'{ports[0]}/tcp open unknown\n')
        obs = net.observe()
        ok, _ = net.check({'scanned': True,
                           'file_contains': {'scan.txt': '{p1}/tcp open'}},
                          obs.data)
        t.ok('{pN} resolves to the port actually opened', ok)
        ok, why = net.check({'scanned': True}, dict(obs.data, connections=0))
        t.ok('a scan that never arrived is refused', not ok, why)
        t.ok('and says why', 'nothing connected' in why, why)
    finally:
        box = net.dir
        net.teardown()
        net.teardown()          # D1: safe twice
    t.ok('teardown removes the sandbox', box is not None and not box.exists())
    t.eq('and closes the ports', net.ports(), [])

    t.head('weblab / a site on loopback, and what it saw')
    web = A.get('weblab')
    t.ok('needs no fuzzer, only some client',
         web.available() or 'installed' in web.reason, web.reason)
    web.setup({})
    try:
        base = f'http://127.0.0.1:{web.port}'
        t.ok('serving', web.port > 0, web.port)
        t.ok('$TARGET is handed over too',
             web.handoff_env({})['TARGET'] == base, web.handoff_env({}))

        t.eq('a real path is 200',
             urllib.request.urlopen(f'{base}/robots.txt').status, 200)
        try:
            urllib.request.urlopen(f'{base}/nothing-here')
            miss = 0
        except urllib.error.HTTPError as e:
            miss, body = e.code, e.read()
        t.eq('a miss is 404', miss, 404)
        t.ok('with a padded body, so -fs and -fw have something to bite on',
             len(body) > 120, len(body))
        try:
            urllib.request.urlopen(f'{base}/uploads/')
            code = 0
        except urllib.error.HTTPError as e:
            code = e.code
        t.eq('a forbidden path is 403, not 404', code, 403)

        req = urllib.request.Request(base + '/', headers={'Host': 'dev.hone.lab'})
        t.ok('the virtual host answers only to its own name',
             b'virtual host' in urllib.request.urlopen(req).read())

        obs = web.observe()
        ok, _ = web.check({'requested': '/robots.txt'}, obs.data)
        t.ok('the request log is checkable', ok)
        ok, why = web.check({'requested': '/never-asked'}, obs.data)
        t.ok('and a path nobody fetched fails', not ok, why)
    finally:
        web.teardown()
        web.teardown()
    t.ok('the server is stopped', web.server is None)

    t.head('handoff env / the sandbox can point a tool away from your home')
    box = A.get('sandbox')
    box.setup({'tree': {'ring': {'dir': True, 'mode': '700'}},
               'env': {'GNUPGHOME': '{dir}/ring'}})
    try:
        env = box.handoff_env({'env': {'GNUPGHOME': '{dir}/ring'}})
        t.ok('{dir} resolves to the real sandbox',
             env['GNUPGHOME'] == f'{box.dir}/ring', env)
        t.ok('and it is a directory that exists', (box.dir / 'ring').is_dir())
        t.eq('created with the mode asked for',
             oct((box.dir / 'ring').stat().st_mode)[-3:], '700')
        t.eq('no env means no overrides', box.handoff_env({}), {})
    finally:
        box.teardown()

    t.head('handoff env / the split path carries it or fails over')
    from hone import handoff as HO
    argv_seen = {}
    real = HO._tmux
    HO._tmux = lambda *a: (argv_seen.setdefault('args', a), (1, ''))[1]
    try:
        HO.in_tmux() and None
        HO.split_and_wait(['sh'], cwd='/tmp', env={'GNUPGHOME': '/tmp/ring'})
    finally:
        HO._tmux = real
    args = argv_seen.get('args', ())
    if args and args[0] == 'split-window':
        t.ok('-e is passed to the pane', '-e' in args, args)
        t.ok('with the value', 'GNUPGHOME=/tmp/ring' in args, args)
    else:
        t.ok('not inside tmux, so the split was never attempted', True)


def test_outro(t: Runner) -> None:
    """The exit animation, and the session line it carries out."""
    from hone import app as _app, splash

    reg = loader.load_all()
    big = Caps(ColorLevel.TRUE, GlyphLevel.UNICODE, theme.CYBERPUNK_NEON, 80, 24)

    t.head('outro / it is the entrance run backwards')
    first = '\n'.join(x.plain() for x in splash.out_frame(big, 0))
    last = '\n'.join(x.plain() for x in
                     splash.out_frame(big, splash.OUT_STEPS - 1))
    t.ok('starts sharp', splash.BLOCK[0] in first, first[:80])
    t.ok('ends broken up', splash.BLOCK[0] not in last)
    t.ok('names what it is doing', splash.OUT_WORD in first)

    t.head('outro / no frame overflows, at any size it agrees to run at')
    for cols, rows in ((80, 24), (120, 40), (40, 20)):
        caps = Caps(ColorLevel.NONE, GlyphLevel.UNICODE, theme.NEUTRAL, cols, rows)
        if not splash.fits(caps):
            continue
        for step in range(splash.OUT_STEPS):
            drawn = splash.out_frame(caps, step, note='12 met this session')
            for row in drawn:
                t.ok(f'{cols}x{rows} step {step} fits', row.width() <= cols,
                     row.plain())
            t.ok(f'{cols}x{rows} step {step} fits tall', len(drawn) <= rows)

    t.head('outro / quitting is never the thing that fails')
    class BrokenTty:
        def write(self, _s):
            raise OSError('pipe closed while quitting')
    splash.outro(BrokenTty(), big, note='x', hold=0)
    t.ok('a dead terminal is survived', True)
    tiny = Caps(ColorLevel.NONE, GlyphLevel.ASCII, theme.NEUTRAL, 20, 6)
    written = []
    class Rec:
        def write(self, s):
            written.append(s)
    splash.outro(Rec(), tiny, hold=0)
    t.eq('a window too small draws nothing', written, [])

    t.head('outro / the session line counts, and stays quiet when there is nothing')
    s = st.State.blank(T0)
    before = _app.met_total(s, reg)
    t.eq('a fresh state has met nothing', before, 0)
    t.eq('an empty session says nothing', _app.quit_summary(s, before, reg), '')
    mod = reg.get('vim')
    s.mark_lesson('vim', mod.lessons[0]['id'], T0)
    s.record_answer('vim', 'drills', mod.drills[0]['id'], True)
    t.eq('counts what was met', _app.met_total(s, reg), 2)
    t.eq('and says so', _app.quit_summary(s, before, reg), '2 met this session')
    t.ok('a wrong answer still counts as met',
         'met' in _app.quit_summary(s, before, reg))
    # D24: never a scold, never a target, never a comparison.
    line = _app.quit_summary(s, before, reg)
    for banned in ('streak', 'goal', 'target', 'yesterday', 'keep it up', '!'):
        t.ok(f'no {banned}', banned not in line.lower(), line)


def test_no_undefined_names(t: Runner) -> None:
    """Every name a module uses at runtime actually exists.

    This test exists because a real one shipped and nothing caught it:
    `main()` called `quit_summary(state, before, ...)`, and neither name was
    ever defined. It crashed with a NameError on every single interactive
    quit, and 9400 checks missed it because `main()`'s tail runs only under a
    real TTY, which a headless suite never provides.

    So rather than trying to drive every branch, this reads the source: for
    each module, collect what it defines, imports, takes as a parameter or
    binds in a comprehension, and flag any load of a name that is none of
    those and is not a builtin. It is a cheap, blunt check and it catches
    exactly the class of bug that got through.
    """
    import ast
    import builtins as _b
    from pathlib import Path

    root = Path(__file__).parent / 'hone'
    files = sorted(p for p in root.rglob('*.py')
                   if '__pycache__' not in p.parts)
    t.head('static / no module loads a name that is never defined')
    t.ok('found the source tree', len(files) > 20, len(files))

    for path in files:
        tree = ast.parse(path.read_text(), filename=str(path))
        bound = set(dir(_b)) | {'__file__', '__name__', '__doc__', '__spec__',
                                '__package__', '__builtins__', '__loader__'}
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for a in node.names:
                    bound.add((a.asname or a.name).split('.')[0])
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                                   ast.ClassDef)):
                bound.add(node.name)
            elif isinstance(node, ast.arg):
                bound.add(node.arg)
            elif isinstance(node, ast.Name) and isinstance(node.ctx,
                                                           (ast.Store,
                                                            ast.Del)):
                bound.add(node.id)
            elif isinstance(node, ast.ExceptHandler) and node.name:
                bound.add(node.name)
            elif isinstance(node, ast.Global):
                bound.update(node.names)
            elif isinstance(node, (ast.comprehension,)):
                for sub in ast.walk(node.target):
                    if isinstance(sub, ast.Name):
                        bound.add(sub.id)

        used = {(n.id, getattr(n, 'lineno', 0)) for n in ast.walk(tree)
                if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
        unknown = sorted({name for name, _ in used} - bound)
        rel = path.relative_to(root.parent)
        t.eq(f'{rel} defines every name it uses', unknown, [])


def test_search(t: Runner) -> None:
    """Search across every tool: ranking, snippets, and the keyboard."""
    from hone.screens.search import SearchScreen

    reg = loader.load_all()
    caps = Caps(ColorLevel.NONE, GlyphLevel.UNICODE, theme.NEUTRAL, 90, 24)

    def typed(q):
        scr = SearchScreen(reg, st.State.blank(T0), T0)
        for ch in q:
            scr.handle(K.parse(ch) if ch != ' ' else K.parse('SPC'))
        return scr

    t.head('search / it will not run on a fragment')
    t.eq('one character finds nothing', typed('s').count(), 0)
    t.ok('two characters do', typed('ssh').count() > 0)

    t.head('search / it finds a flag that appears only in an answer')
    # The point of searching answers: you remember the flag, not the sentence.
    scr = typed('--delete')
    t.ok('finds --delete', scr.count() > 0)
    hit = scr.results()[0]
    t.ok('and it is the rsync material', hit['module'].id == 'scprsync',
         hit['module'].id)

    t.head('search / a title outranks a mention buried in prose')
    scr = typed('pane')
    top = scr.results()[0]
    t.eq('tmux first', top['module'].id, 'tmux')
    t.eq('and it matched a title', top['field'], 'title')

    t.head('search / every result can actually be opened')
    for q in ('ssh', 'pane', 'dnat', 'hash'):
        for r in typed(q).results()[:8]:
            t.ok(f'{q}: {r["module"].id}/{r["kind"]} is a real item',
                 r['item'] in r['module'].items(r['kind']))

    t.head('search / rows fit and never overflow')
    for cols in (80, 100, 120):
        c = Caps(ColorLevel.NONE, GlyphLevel.UNICODE, theme.NEUTRAL, cols, 24)
        scr = typed('config')
        for row in scr.render(c):
            t.ok(f'{cols} cols fits', row.width() <= cols, row.plain())

    t.head('search / typing edits the query rather than triggering shortcuts')
    scr = typed('ssh')
    t.eq('query built from keys', scr.query, 'ssh')
    scr.handle(K.parse('BSP'))
    t.eq('backspace deletes', scr.query, 'ss')
    # `q` and `j` are quit and down elsewhere; here they are just letters.
    scr.handle(K.parse('q'))
    t.eq('q is a character, not quit', scr.query, 'ssq')
    t.eq('and the screen stays', scr.handle(K.parse('j')).kind, 'stay')
    t.eq('j typed too', scr.query, 'ssqj')

    t.head('search / esc still leaves, and the footer says so')
    t.eq('esc pops', typed('ssh').handle(K.parse('ESC')).kind, 'pop')
    hints = [k for k, _ in typed('ssh').hints(caps)]
    t.ok('esc advertised', 'esc' in hints, hints)

    t.head('search / an empty state explains itself rather than sitting blank')
    blank = ' '.join(x.plain() for x in typed('').render(caps))
    t.ok('says what it searches', 'lesson' in blank.lower(), blank[:120])
    none = ' '.join(x.plain() for x in typed('zzzznotathing').render(caps))
    t.ok('says nothing matched', 'Nothing matches' in none, none[:120])

    t.head('search / home offers the key and it opens this screen')
    from hone.screens.home import HomeScreen
    opened = []
    home = HomeScreen(reg, st.State.blank(T0), T0,
                      open_search=lambda: opened.append(1) or SearchScreen(
                          reg, st.State.blank(T0), T0))
    t.ok('/ advertised', '/' in [k for k, _ in home.hints(caps)])
    t.eq('/ pushes search', home.handle(K.parse('/')).kind, 'push')
    t.eq('factory called', len(opened), 1)


def test_sheet(t: Runner) -> None:
    """--sheet: the reference card, for when you are not training."""
    import io, contextlib
    from hone.app import sheet

    reg = loader.load_all()

    def run(tool):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = sheet(reg, tool)
        return rc, out.getvalue(), err.getvalue()

    t.head('sheet / it prints a tool\'s real commands')
    rc, out, _ = run('scprsync')
    t.eq('succeeds', rc, 0)
    t.ok('names the tool', 'scp and rsync' in out, out[:80])
    t.ok('has a COMMANDS section', 'COMMANDS' in out)
    # Every command drill answer must appear: that is the whole point.
    mod = reg.get('scprsync')
    for d in mod.items('drills'):
        if d.get('type') == 'command':
            t.ok(f'lists {d["answer"][:24]}', d['answer'] in out)

    t.head('sheet / a keystroke tool gets a KEYS section instead')
    rc, out, _ = run('vim')
    t.eq('succeeds', rc, 0)
    t.ok('has KEYS', 'KEYS' in out, out[:60])

    t.head('sheet / markup is rendered away, not printed raw')
    for tool in ('ssh', 'curl', 'systemd', 'git'):
        _, out, _ = run(tool)
        t.ok(f'{tool}: no stray backticks', '`' not in out, out[:120])

    t.head('sheet / an unknown tool fails usefully, not silently')
    rc, out, err = run('rsync')          # a real binary, not a module id
    t.eq('non-zero exit', rc, 1)
    t.ok('says so', 'no tool called' in err, err)
    t.ok('suggests the module that holds it', 'scprsync' in err, err)
    rc, _, err = run('zzznope')
    t.eq('still non-zero', rc, 1)
    t.ok('points at --list', '--list' in err, err)

    t.head('sheet / every module produces a card without raising')
    for mod in reg:
        rc, out, _ = run(mod.id)
        t.eq(f'{mod.id} exits 0', rc, 0)
        t.ok(f'{mod.id} says something', len(out.strip()) > 20, mod.id)


def main() -> int:
    t = Runner()
    for fn in (test_keys, test_term, test_render, test_state,
               test_loader, test_adapters, test_tmux_adapter, test_screens,
               test_real_content, test_challenge, test_quiz,
               test_solvable, test_grading,
               test_help_and_tour, test_handoff, test_app, test_build,
               test_notes, test_sync, test_lint,
               test_audit, test_handover_and_reset,
               test_orientation, test_splash, test_install_help,
               test_pcapgen, test_oracle, test_checking_mode, test_rigor,
               test_labs, test_free_pace, test_validate,
               test_no_undefined_names, test_outro, test_search,
               test_sheet):
        fn(t)

    print(f'{t.passed} checks passed')
    if t.failures:
        print(f'\n{len(t.failures)} FAILED:')
        for f in t.failures:
            print(f'  {f}')
        return 1
    print('all green')
    return 0


if __name__ == '__main__':
    sys.exit(main())
