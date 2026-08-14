"""The screen stack and the main loop.

Deliberately thin. Everything interesting is in the screens, the engines, or
the harness; this only owns navigation and the one thing navigation must never
get wrong, which is leaving the terminal in a usable state on the way out.

State is saved when it is dirty and on every exit path, because a trainer that
loses the session you just did is worse than one that never recorded it.
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone as _tz
from pathlib import Path

from . import adapters as A
from . import install, loader, render, splash, state as st, sync, term, theme
from .config import APP_NAME, APP_TITLE, EXIT_CHORD, state_path
from . import handoff as HO
from .screens import QUIT, Screen, set_help_factory
from .screens.help import HELP, TOUR, HelpScreen
from .screens.challenge import ChallengeScreen
from .screens.drill import DrillScreen
from .screens.home import HomeScreen
from .screens.lesson import LessonScreen
from .screens.module import ModuleScreen
from .screens.quiz import QuizScreen
from .screens.notes import NotesScreen
from .screens.search import SearchScreen


class App:
    """Owns the screen stack. Usable headlessly, which is what `test.py` needs."""

    def __init__(self, registry, state, now: datetime, caps: render.Caps,
                 kitty: bool = False, exit_chord: str = EXIT_CHORD,
                 allow_split: bool = True) -> None:
        self.registry = registry
        self.state = state
        self.now = now
        self.caps = caps
        self.kitty = kitty
        self.exit_chord = exit_chord
        self.stack: list[Screen] = [HomeScreen(registry, state, now,
                                               open_module=self._open_module,
                                               open_notes=self.open_notes,
                                               open_search=self.open_search)]
        self.running = True
        self.tty: term.Terminal | None = None
        self.allow_split = allow_split
        set_help_factory(self.open_help)
        if not state.settings.get('seen_tour'):
            self.stack.append(HelpScreen(TOUR, state, now, tour=True))

    # -- screen factories --------------------------------------------------

    def _open_module(self, module) -> Screen:
        return ModuleScreen(module, self.state, self.now, registry=self.registry,
                            open_notes=self.open_notes,
                            open_drill=self._open_drill,
                            open_lesson=self._open_lesson,
                            open_challenge=self._open_challenge,
                            open_quiz=self._open_quiz)

    def _open_lesson(self, module, lesson) -> Screen:
        return LessonScreen(module, lesson, self.state, self.now,
                            open_lesson=self._open_lesson)

    def _open_challenge(self, module, challenge) -> Screen:
        return ChallengeScreen(module, challenge, self.state, self.now,
                               handoff=self.handoff)

    def _open_quiz(self, module) -> Screen:
        return QuizScreen(module, list(module.quiz), 0, self.state, self.now)

    def open_help(self) -> Screen:
        return HelpScreen(HELP, self.state, self.now)

    def open_notes(self, module_id: str | None = None) -> Screen:
        return NotesScreen(self.registry, self.state, self.now,
                           open_item=self._open_item, module_id=module_id)

    def open_search(self) -> Screen:
        return SearchScreen(self.registry, self.state, self.now,
                            open_item=self._open_found,
                            open_module=self._open_module)

    def _open_found(self, module, kind: str, item: dict) -> Screen | None:
        """A search result, opened as the thing it is.

        Landing on the item rather than on its module is the whole point of
        searching: you already said what you were looking for.
        """
        if kind == 'lessons':
            return self._open_lesson(module, item)
        if kind == 'challenges':
            return self._open_challenge(module, item)
        if kind == 'drills':
            return self._open_drill(module, [item], 0)
        if kind == 'quiz':
            return QuizScreen(module, [item], 0, self.state, self.now)
        return None

    def _open_item(self, module_id: str, kind: str, item_id: str) -> Screen | None:
        """A single item as its own one-question session, from a note row."""
        mod = self.registry.get(module_id)
        content = mod.item(kind, item_id) if mod else None
        if mod is None or content is None:
            return None
        if kind == 'quiz':
            return QuizScreen(mod, [content], 0, self.state, self.now)
        if kind == 'drills':
            return self._open_drill(mod, [content], 0)
        return None

    def handoff(self, argv: list[str], cwd: str | None = None,
                brief: list[str] | None = None,
                env: dict[str, str] | None = None) -> None:
        """D21: give the terminal back, run the real tool, take it back.

        With no terminal (tests, or a challenge with nothing to launch) this is
        a no-op, which is what lets the whole challenge flow be played headless.
        """
        if self.tty is None:
            return
        import subprocess

        # A tmux-attach handoff while already inside tmux cannot nest: tmux
        # refuses it, in a pane or suspended alike. switch-client is the
        # correct primitive there, and it is not a split, so --no-split does
        # not disable it. Everything else keeps the pane enhancement.
        target = HO.tmux_attach_target(argv)
        if target is not None and HO.in_tmux():
            if HO.switch_and_wait(target):
                return
        # D21's enhancement: if we are already inside tmux, put the tool in a
        # pane beside us instead of taking the whole terminal. Optional by
        # design, and any failure falls through to the base behaviour.
        if self.allow_split and HO.can_split():
            if HO.split_and_wait(argv, cwd, env=env):
                return

        with self.tty.suspended():
            if not argv:
                argv = [os.environ.get('SHELL', '/bin/sh')]
            # Printed only for a shell handover: an editor clears the screen
            # on the way in, so this would flash past unread. Editors get the
            # same information as a persistent line inside the tool instead.
            if brief and cwd:
                print()
                print('\u2500' * 60)
                for ln in brief:
                    print(f'  {ln}' if ln else '')
                print(f'\n  You are in {cwd}')
                print('\u2500' * 60)
                print()
            try:
                # Overrides only, layered on the real environment: a shell
                # handed a stripped env is a shell with no PATH, and the
                # student would meet a broken prompt rather than a sandbox.
                merged = {**os.environ, **env} if env else None
                subprocess.run(argv, cwd=cwd, env=merged)
            except (OSError, subprocess.SubprocessError):
                pass

    def _open_drill(self, module, drills, index) -> Screen:
        return DrillScreen(module, drills, index, self.state, self.now,
                           kitty=self.kitty, exit_chord=self.exit_chord)

    # -- loop --------------------------------------------------------------

    @property
    def screen(self) -> Screen:
        return self.stack[-1]

    def render(self) -> list[render.Text]:
        return self.screen.render(self.caps)

    @staticmethod
    def _close(screen) -> None:
        try:
            screen.close()
        except Exception:
            pass  # closing is best-effort; teardown errors have nowhere to go

    def dispatch(self, key) -> None:
        action = self.screen.handle(key)
        kind = action.kind
        if kind == 'push' and action.screen is not None:
            self.stack.append(action.screen)  # type: ignore[arg-type]
        elif kind == 'replace' and action.screen is not None:
            self._close(self.stack[-1])
            self.stack[-1] = action.screen    # type: ignore[assignment]
        elif kind == 'pop':
            if len(self.stack) > 1:
                self._close(self.stack.pop())
            else:
                self.running = False
        elif kind == 'root':
            while len(self.stack) > 1:
                self._close(self.stack.pop())
        elif kind == 'quit':
            self.running = False

    def shutdown(self) -> None:
        """Close every stacked screen. The quit path, and the crash path."""
        while self.stack:
            self._close(self.stack.pop())

    def run(self, tty: term.Terminal) -> None:
        self.tty = tty
        redraw = True
        while self.running:
            if redraw:
                frame = render.render_lines(self.caps, self.render())
                tty.write(term.CLEAR + frame.replace('\n', '\r\n'))
                redraw = False
            # The 0.5s timeout is what turns a SIGWINCH into a redraw soon
            # after it happens. Idle timeouts with nothing to do fall through
            # without touching the screen: an unconditional clear-and-repaint
            # twice a second is visible flicker on a slow terminal, and this
            # app has no clock to keep current.
            keys = tty.read_keys(timeout=0.5)
            for key in keys:
                self.dispatch(key)
                if not self.running:
                    break
            if keys:
                redraw = True
            if tty.resized:
                tty.resized = False
                cols, rows = term.size()
                self.caps = render.Caps(self.caps.color, self.caps.glyphs,
                                        self.caps.palette, cols, rows)
                redraw = True
            if self.state.dirty:
                self.state.save()


# --------------------------------------------------------------------------
# Reset
# --------------------------------------------------------------------------

def met_total(state, registry) -> int:
    """How many items have been genuinely met, across every module.

    One number, used only to difference it against the same number taken at
    launch, so the app can say what this session actually covered.
    """
    return sum(sum(state.counts(m.id).values()) for m in registry)


def quit_summary(state, before: int, registry) -> str:
    """The one line worth carrying out of a session, or nothing.

    **Nothing is the common case and the important one.** D24 says the app
    keeps no clock on you and has no opinion about your pace, so a session
    where you read a page and left says nothing rather than reporting a zero,
    which would read as a scold. What it will say is a plain count of what you
    met, with no streak, no target and no comparison to last time.
    """
    gained = met_total(state, registry) - before
    if gained <= 0:
        return ''
    return f'{gained} met this session'


def _backup_path(base: Path, at: datetime) -> Path:
    """A backup name that never overwrites an earlier backup.

    Two resets in the same second are not hypothetical: resetting one tool
    and then everything is a normal sequence, and it collided on the first
    try.
    """
    stamp = at.astimezone(_tz.utc).strftime('%Y%m%d-%H%M%S')
    dest = base.with_name(f'{base.stem}.before-reset-{stamp}.json')
    n = 2
    while dest.exists() and n < 100:
        dest = base.with_name(f'{base.stem}.before-reset-{stamp}-{n}.json')
        n += 1
    return dest


def reset(state, registry, target: str, assume_yes: bool, at) -> int:
    """Erase progress, after saying exactly what is about to be lost.

    A backup is written first, unconditionally and before the prompt, because
    the one thing worse than losing a month of spacing data is losing it to a
    keystroke. The backup is an ordinary export, so `--import` puts it back.

    Preferences survive; see State.reset. Confirmation is required unless
    --yes, and required means required: with no terminal to ask, this refuses
    rather than guessing.
    """
    module_id = None if target == 'all' else target
    if module_id is not None and registry.get(module_id) is None:
        print(f'no tool called {module_id!r}. Installed: '
              f'{", ".join(registry.ids())}', file=sys.stderr)
        return 1

    mods = state.data.get('modules', {})
    scope = [module_id] if module_id else list(mods)
    items = sum(len(rec.get(kind) or {})
                for mid in scope
                for rec in [mods.get(mid) or {}]
                for kind in ('lessons', 'challenges', 'drills', 'quiz'))
    if not items:
        where = f'for {module_id} ' if module_id else ''
        print(f'there is no progress {where}to reset')
        return 0

    what = (f'everything for {registry.get(module_id).title}' if module_id
            else 'all of your progress')
    print(f'This erases {what}:')
    print(f'  {items} recorded item{"" if items == 1 else "s"}')
    print('Your theme, rigor and sync settings are kept.')

    base = state.path or state_path()
    backup = _backup_path(base, at)
    try:
        state.export_to(backup, at)
    except OSError as e:
        print(f'could not write a backup, so nothing was reset: {e}',
              file=sys.stderr)
        return 1
    print(f'\nBacked up to {backup}')
    print(f'Put it back any time with:  {APP_NAME} --import {backup}')

    def _declined(message: str, stream=sys.stdout) -> int:
        # The backup is written before the prompt so the message above can
        # name a file that already exists. If the answer is no, that file is
        # a byte-for-byte copy of the live one and pure litter, so it goes.
        backup.unlink(missing_ok=True)
        sys.stdout.flush()
        print(message, file=stream)
        return 1

    if not assume_yes:
        if not sys.stdin.isatty():
            return _declined('\nrefusing to reset without a confirmation. '
                             'Re-run with --yes. Nothing was changed.',
                             sys.stderr)
        try:
            answer = input('\nType yes to erase it: ')
        except (EOFError, KeyboardInterrupt):
            return _declined('\nnothing was reset')
        if answer.strip().lower() not in ('yes', 'y'):
            return _declined('nothing was reset')

    lost = state.reset(module_id)
    state.save(at=at)
    print(f'reset: {lost["items"]} items across {lost["modules"]} '
          f'tool{"" if lost["modules"] == 1 else "s"} erased')
    return 0


# --------------------------------------------------------------------------
# Doctor
# --------------------------------------------------------------------------

def sheet(registry, tool: str) -> int:
    """Print one tool's commands as a reference card.

    hone is a trainer, and a trainer is something you are inside. This is the
    other half: the thing you want at the moment you are *not* training, when
    you know the tool exists and cannot remember the invocation. The content
    is already there, one command per drill with a line saying why, so the
    only thing missing was a way to get it out without opening the app.

    Plain text on stdout, so it pipes, redirects and prints. It schedules
    nothing and records nothing, so D24 is untouched: this is a reference,
    not a review.
    """
    mod = registry.get(tool)
    if mod is None:
        near = [m.id for m in registry if tool.lower() in m.id.lower()
                or tool.lower() in m.title.lower()]
        print(f'no tool called {tool!r}', file=sys.stderr)
        if near:
            print(f'did you mean: {", ".join(sorted(near))}', file=sys.stderr)
        else:
            print('hone --list shows them all', file=sys.stderr)
        return 1

    rule = '=' * max(12, len(mod.title))
    print(f'{mod.title}\n{rule}')
    if mod.blurb:
        print(mod.blurb)

    # Command drills are the reference material: one invocation and one
    # sentence on why. Keystroke drills are muscle memory and read badly on
    # paper, so they get their own compact section rather than the same shape.
    typed = [d for d in mod.items('drills') if d.get('type') == 'command']
    keys = [d for d in mod.items('drills') if d.get('type') == 'keys']

    if typed:
        width = min(46, max(len(str(d.get('answer', ''))) for d in typed))
        print('\nCOMMANDS')
        for d in typed:
            answer = str(d.get('answer', ''))
            why = render.strip_markup(str(d.get('teach') or d.get('prompt') or ''))
            why = ' '.join(why.split())
            if len(answer) > width:
                print(f'  {answer}')
                print(f'  {"":<{width}}    {why}')
            else:
                print(f'  {answer:<{width}}    {why}')

    if keys:
        print('\nKEYS')
        for d in keys:
            seq = ' '.join(str(k) for k in (d.get('keys') or ()))
            prompt = render.strip_markup(str(d.get('prompt') or ''))
            print(f'  {seq:<18}  {" ".join(prompt.split())}')

    gone = install.missing(mod.needs)
    if gone:
        print(f'\nNOT INSTALLED HERE: {", ".join(gone)}')
        for t in gone:
            hint = install.hint(t)
            if hint:
                print(f'  {hint}')
    return 0


def doctor(state, registry, at) -> int:
    """Everything that decides how this machine's hone behaves, in one page.

    This exists for the support conversation. D18 and D20 mean the app
    silently degrades in half a dozen independent ways, which is right for
    the student and miserable for diagnosing 'verification is not working'
    over chat. One command, one paste.
    """
    def say(label: str, value: str) -> None:
        print(f'  {label:<22} {value}')

    print('hone doctor')
    print()
    print('terminal')
    say('tty', 'yes' if term.is_tty() else 'no (colours and UI off)')
    cols, rows = term.size()
    small = '' if not term.too_small() else f'  (below {80}x{24}: layout degrades)'
    say('size', f'{cols}x{rows}{small}')
    say('TERM', os.environ.get('TERM', '(unset)'))
    say('colour', render.detect_color().name.lower())
    say('glyphs', render.detect_glyphs().name.lower())
    kitty = term.kitty_supported()
    say('kitty protocol', 'yes: all chords expressible' if kitty else
        'no: C-i/TAB, C-m/RET, C-[/ESC fold together in capture drills')
    say('inside tmux', 'yes (attach handoffs use switch-client)'
        if HO.in_tmux() else 'no')

    print()
    print('verification (D18: any \'no\' degrades that tool to self-marked)')
    say('mode', f'{A.mode()}: {A.MODE_BLURB[A.mode()]}')
    if A.read_only():
        # Said once, plainly. Someone reading a doctor report to work out why
        # nothing is being checked should find the answer at the top of the
        # section rather than deduce it from a list of tools that are all
        # present and all unused.
        say('', 'every tool below is installed but will not be run')
    wanted: list[str] = []
    for name in A.registered():
        ad = A.get(name)
        ok = ad.available(recheck=True)
        say(name, 'yes' if ok else f'no: {ad.reason}')
        if not ok:
            wanted.extend(install.missing(ad.requires))

    print()
    print('content')
    say('modules', str(len(registry)))
    for e in registry.errors:
        say('load error', f'{e.name}: {e.message}')
    for mod in registry:
        gone = install.missing(mod.needs)
        if gone:
            say(mod.id, f'content assumes {", ".join(gone)}, not installed')
            wanted.extend(gone)

    wanted = sorted({t for t in wanted if install.known(t)})
    if wanted:
        print()
        mgr = install.detect()
        print(f'how to install what is missing'
              f'{" (" + install.MANAGER_LABELS[mgr] + " detected)" if mgr else ""}')
        for tool in wanted:
            print(f'  {tool}')
            for ln in install.lines(tool, all_managers=mgr is None):
                print(f'      {ln}')

    print()
    print('progress')
    say('state file', str(state.path or state_path()))
    if state.recovered_from:
        say('recovered', f'previous file was unreadable, set aside as '
                         f'{state.recovered_from.name}')
    met = sum(len(state.counts(mod.id)) and
              sum(state.counts(mod.id).values()) for mod in registry)
    say('items met', str(met))
    say('notes', str(len(state.notes())))
    sync_to = sync.path_of(state)
    say('sync', str(sync_to) if sync_to else 'off')
    notice = sync.check(state)
    if notice:
        say('', notice)
    return 0


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog=APP_NAME, description=f'{APP_TITLE}: learn the tools you type into.')
    p.add_argument('--theme', choices=sorted(theme.PALETTES),
                   help='colour palette (default: cyberpunk-neon)')
    p.add_argument('--ascii', action='store_true',
                   help='force ASCII glyphs, no box drawing')
    p.add_argument('--exit-key', default=EXIT_CHORD, metavar='CHORD',
                   help=f'chord that leaves a drill (default: {EXIT_CHORD})')
    p.add_argument('--mode', choices=list(A.MODES),
                   help='checked runs the real tools and checks your work; '
                        'read launches nothing at all. Remembered between '
                        'runs, and switchable with m on the home screen')
    p.add_argument('--export', metavar='PATH', type=Path,
                   help='write progress to a file and exit')
    p.add_argument('--import', dest='import_', metavar='PATH', type=Path,
                   help='replace progress from a file and exit')
    p.add_argument('--sync', metavar='PATH',
                   help='remember a file and rewrite it on every exit; '
                        "'off' forgets it. One-way: use --import to take a "
                        'copy made elsewhere')
    p.add_argument('--list', action='store_true',
                   help='list installed tools and exit')
    p.add_argument('--sheet', metavar='TOOL',
                   help='print a tool\'s commands as a reference card and exit')
    p.add_argument('--doctor', action='store_true',
                   help='report what this machine supports and exit')
    p.add_argument('--reset', nargs='?', const='all', metavar='TOOL',
                   help='erase your progress and start over; name a tool to '
                        'reset only that one. The old progress is written to '
                        'a backup file first')
    p.add_argument('--yes', action='store_true',
                   help='answer yes to the --reset confirmation')
    p.add_argument('--no-split', action='store_true',
                   help='never open a second tmux pane; always hand over the '
                        'whole terminal')
    p.add_argument('--tour', action='store_true',
                   help='show the first-run tour again')
    p.add_argument('--no-splash', action='store_true',
                   help='skip the launch and exit animations')
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    now = st.now()
    state = st.State.load()

    # D26, set before anything reads it. The flag wins for this run and is
    # remembered, so `--mode read` once is enough; without a flag the stored
    # setting applies. This has to happen above the non-interactive branches:
    # `--doctor` and `--list` both report on checking, and a doctor that
    # printed the default while the app would run in another mode would be
    # lying on the one screen whose entire job is telling you the truth.
    if args.mode:
        state.set_setting('checking', args.mode)
        state.dirty = True
        state.save(at=now)
    A.set_mode(args.mode or state.settings.get('checking', A.CHECKED))

    # Content is loaded eagerly for every non-interactive command. The
    # interactive path defers it so the launch screen can cover the real
    # import rather than an invented pause.
    registry = None
    if not term.is_tty() or any([args.export, args.import_, args.list,
                                 args.doctor, args.reset, args.sheet]):
        registry = loader.load_all()

    if args.export:
        dest = state.export_to(args.export, now)
        print(f'progress written to {dest}')
        return 0

    if args.import_:
        try:
            incoming = st.State.import_from(args.import_, now)
        except (OSError, ValueError) as e:
            print(f'could not import: {e}', file=sys.stderr)
            return 1
        incoming.save(at=now)
        print(f'progress replaced from {args.import_}')
        return 0

    if args.sync is not None:
        if args.sync.lower() in ('off', 'none', ''):
            sync.set_path(state, None)
            state.save(at=now)
            print('sync file forgotten')
            return 0
        sync.set_path(state, Path(args.sync).expanduser())
        state.save(at=now)
        ok, msg = sync.push(state, now)
        print(msg, file=sys.stdout if ok else sys.stderr)
        if ok:
            print('It will be rewritten every time you quit. Nothing is sent '
                  'anywhere, and nothing is merged: on another machine run '
                  f'hone --import {args.sync}')
        return 0 if ok else 1

    if args.reset:
        return reset(state, registry, args.reset, args.yes, now)

    if args.doctor:
        return doctor(state, registry, now)

    if args.sheet:
        return sheet(registry, args.sheet)

    if args.list:
        if not registry:
            print('no tools installed in this build')
        for m in registry:
            ok, reason = A.status(m.adapter)
            mark = 'verified' if ok else reason
            print(f'{m.id:24} {m.title:24} {mark}')
        for e in registry.errors:
            print(f'error: {e.name}: {e.message}', file=sys.stderr)
        return 0

    notice = sync.check(state)
    if notice:
        print(notice, file=sys.stderr)

    if state.recovered_from:
        print(f'note: unreadable progress file was set aside as '
              f'{state.recovered_from.name}; starting fresh', file=sys.stderr)

    cols, rows = term.size()
    caps = render.detect_caps(theme=args.theme or state.settings.get('theme'),
                              ascii_only=args.ascii, cols=cols, rows=rows)

    if not term.is_tty():
        print('hone needs an interactive terminal.', file=sys.stderr)
        print('Try --list, --export or --import for non-interactive use.',
              file=sys.stderr)
        return 2

    # SIGTERM and SIGHUP default to killing the process without unwinding,
    # which would skip every finally below: the terminal would be left in raw
    # mode on the alternate screen and the last answers would go unsaved.
    # Turning them into SystemExit lets the with-blocks do their job. Ctrl-C
    # is not in this list: raw mode delivers it as a key, not a signal.
    def _die(_sig, _frame):
        raise SystemExit(1)
    import signal as _signal
    for _sig in (_signal.SIGTERM, _signal.SIGHUP):
        try:
            _signal.signal(_sig, _die)
        except (ValueError, OSError):
            pass

    with term.managed() as tty:
        show = (not args.no_splash and state.settings.get('splash', True)
                and splash.fits(caps))
        if show:
            registry = splash.play(tty, caps, work=loader.load_all,
                                   note_from=splash.roster_note)
        if registry is None:
            registry = loader.load_all()
        if args.tour:
            state.set_setting('seen_tour', False)
        # Taken after the splash, because the splash is what loads the
        # registry, and before any screen opens, so the difference at the end
        # is exactly what this session covered.
        before = met_total(state, registry)
        app = App(registry, state, now, caps, kitty=tty.kitty,
                  exit_chord=args.exit_key, allow_split=not args.no_split)
        summary = ''
        try:
            app.run(tty)
        finally:
            app.shutdown()   # sandboxes die with the app, however it ends
            if state.dirty:
                state.save()
            summary = quit_summary(state, before, registry)
            if show:
                # Same switch as the entrance: someone who turned the splash
                # off does not want an animation on the way out either.
                splash.outro(tty, caps, note=summary)
    if summary:
        print(summary)
    if sync.path_of(state) is not None:
        ok, msg = sync.push(state, now)
        if not ok:
            print(msg, file=sys.stderr)
    return 0
