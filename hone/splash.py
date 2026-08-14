"""The launch screen: the name, sharpening into focus while the content loads.

Two arguments for this existing at all, and neither is decoration.

**It is honest work, not an artificial pause.** Fifteen content modules get
imported at startup, and that import is the only thing between pressing a
command and seeing a menu. The animation runs *during* that load and stops
when it finishes, so the screen is showing you a real wait rather than
inventing one.

**It then waits for a key rather than timing out.** The animation used to
resolve and vanish on a timer, which meant the one screen carrying the app's
name was the one screen you never got to look at. Holding costs nothing,
because the load has already happened behind it, and it makes the entrance
readable instead of a flicker. The held frame *says* it is waiting, per D19:
a screen that sits there without naming its own exit is indistinguishable
from a hang, and this one greets a first-time user.

**The animation is the name.** You hone a blade: the letters arrive as noise
and resolve, edge by edge, into something sharp. An app that opens with a
spinner tells you nothing about itself.

Everything degrades. No terminal, a small window, `--no-splash`, or the
setting turned off, and this never runs; the ASCII rung gets a plain figlet
rather than block characters, because a screen of tofu is not an entrance.

**And the exit is the same animation, reversed.** `outro` runs the resolve
backwards: the sharp letters break up into grit and go dark. It is the same
`_resolve` call with progress counting down, which is why it costs almost
nothing, and it is the right shape rather than a second idea: you honed it,
now you are putting it away. It is deliberately quicker than the entrance,
because someone leaving has already decided to leave, and it never waits for
a key. It carries the one line worth carrying out of a session, which is what
you actually met while you were in there, and it says nothing at all when the
answer is nothing, because D24 forbids this app having an opinion about your
pace.
"""

from __future__ import annotations

import random
import time

from .config import APP_TITLE, TAGLINE_PARTS
from .render import Caps, GlyphLevel, Text, render_lines, text_width

#: ANSI Shadow, the block-drawing version. 35 columns wide, 6 tall.
BLOCK = r"""
██╗  ██╗ ██████╗ ███╗   ██╗███████╗
██║  ██║██╔═══██╗████╗  ██║██╔════╝
███████║██║   ██║██╔██╗ ██║█████╗
██╔══██║██║   ██║██║╚██╗██║██╔══╝
██║  ██║╚██████╔╝██║ ╚████║███████╗
╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝
""".strip('\n').split('\n')

#: Standard figlet, for terminals that cannot draw the blocks. 25 wide, 5 tall.
PLAIN = r"""
 _   _  ___  _   _ _____
| | | |/ _ \| \ | | ____|
| |_| | | | |  \| |  _|
|  _  | |_| | |\  | |___
|_| |_|\___/|_| \_|_____|
""".strip('\n').split('\n')

#: What an unresolved pixel looks like on its way in. Ordered coarse to fine,
#: so the last frames are visibly sharper than the first.
GRIT_BLOCK = '░▒▓█'
GRIT_PLAIN = '.:-='

#: Frames of the reveal. Enough to read as motion, few enough to stay under a
#: second on the floor path.
STEPS = 7
FRAME_SECONDS = 0.07
#: Shortest time the screen is up when loading finishes instantly. Below this
#: it reads as a flicker rather than an entrance. Only reached when the screen
#: is not being held, which is the degraded path.
MIN_SECONDS = 0.45

#: What the held frame says. D19: every screen names its own exit.
HOLD_HINT = 'press any key'

#: The outro never waits for a key, so its whole length is these numbers.
#: Slower and longer than the first draft, which was over before you had
#: registered it: the dissolve is the last thing the app does and it should
#: read as a sign-off rather than a flicker on the way out.
OUT_STEPS = 7
OUT_FRAME_SECONDS = 0.07

#: Held after the letters have gone, on the farewell alone.
OUT_HOLD_SECONDS = 0.75

#: What it says. Under the wordmark while it comes apart, and then by itself.
OUT_WORD = 'goodbye'

#: A blocking read that returns nothing has hit EOF or a closed stdin, not a
#: patient user. Give up after this many so a redirected or dead terminal
#: cannot spin here forever waiting for a key that can never arrive.
HOLD_EMPTY_READS = 64

#: Never draw into a window the art does not fit. 37 is the block art plus a
#: column of margin either side. The row floor covers the art, the rule, the
#: tagline, the roster line and the hint with a margin above and below.
MIN_COLS = 39
MIN_ROWS = 17


def art_for(caps: Caps) -> tuple[list[str], str]:
    if caps.glyphs == GlyphLevel.ASCII or caps.cols < len(BLOCK[0]) + 4:
        return PLAIN, GRIT_PLAIN
    return BLOCK, GRIT_BLOCK


def fits(caps: Caps) -> bool:
    return caps.cols >= MIN_COLS and caps.rows >= MIN_ROWS


def _resolve(line: str, progress: float, grit: str, rng) -> str:
    """One line of art, partially resolved.

    `progress` runs 0 to 1. Below it a cell is its real character; above it,
    a grit character chosen from a band that itself sharpens as progress
    rises, so the noise is not static between frames.
    """
    if progress >= 1.0:
        return line
    out = []
    band = max(1, int(len(grit) * progress) + 1)
    for ch in line:
        if ch == ' ':
            out.append(' ')
        elif rng.random() < progress:
            out.append(ch)
        else:
            out.append(grit[rng.randrange(band)])
    return ''.join(out)


def frame(caps: Caps, step: int, steps: int = STEPS,
          seed: int | None = None, hold: bool = False,
          note: str = '') -> list[Text]:
    """One rendered frame, as rows of styled text.

    `hold` adds the waiting-for-a-key line, and is only ever true on the
    resolved frame: an unresolved frame is still loading and inviting a
    keypress there would be a lie about what the key does.

    `note` is what the load actually found, shown only once it has finished.
    The entrance is the one place the whole roster can be stated at once, and
    a student who has just typed `hone` for the first time deserves to see
    the size of the thing before deciding where to start.
    """
    p = caps.palette
    art, grit = art_for(caps)
    rng = random.Random(seed if seed is not None else step * 7919)
    progress = min(1.0, (step + 1) / steps)
    done = progress >= 1.0

    # `center` leaves a string longer than the width untouched, so a roster
    # line that does not fit would run straight off the side. A window too
    # narrow to hold it simply does not get it: same ladder as everything else.
    show_note = bool(note) and done and text_width(note) <= caps.cols - 2

    pad = max(0, (caps.cols - len(art[0])) // 2)
    # Rows reserved below the art, so the block stays put rather than drifting
    # as the tagline, roster line and hint appear under it.
    below = 5 + (2 if show_note else 0)
    top = max(1, (caps.rows - len(art) - below) // 2)

    rows: list[Text] = [Text() for _ in range(top)]
    for line in art:
        colour = p.accent if done else (
            p.accent2 if progress > 0.5 else p.border)
        rows.append(Text().add(' ' * pad + _resolve(line, progress, grit, rng),
                               colour, bold=done))

    # A rule the width of the wordmark, drawn only once the letters have
    # resolved: it reads as the edge the name is about rather than as chrome.
    if done:
        rule = caps.g('hh') * len(art[0]) if caps.glyphs != GlyphLevel.ASCII \
            else '=' * len(art[0])
        rows.append(Text().add(' ' * pad + rule, p.border))

    tag = f' {caps.g("bullet")} '.join(TAGLINE_PARTS)
    rows.append(Text())
    if done:
        rows.append(Text().add(tag.center(caps.cols).rstrip(), p.dim))
        if show_note:
            rows += [Text(), Text().add(note.center(caps.cols).rstrip(),
                                        p.accent2)]
        if hold:
            rows.append(Text())
            rows.append(Text().add(HOLD_HINT.center(caps.cols).rstrip(),
                                   p.muted))
    else:
        # The word for what is happening, and it is also what the app does.
        rows.append(Text().add('sharpening'.center(caps.cols).rstrip(), p.dim))
    return rows


def out_frame(caps: Caps, step: int, steps: int = OUT_STEPS,
              seed: int | None = None, note: str = '') -> list[Text]:
    """One frame of the exit: the wordmark coming apart.

    Progress runs the other way from `frame`, so step 0 is still sharp and the
    last step is nearly gone. The colour walks back down the same ramp the
    entrance walked up, ending on the border colour, which on every palette is
    the closest thing to the background that is still visible.
    """
    p = caps.palette
    art, grit = art_for(caps)
    rng = random.Random(seed if seed is not None else 104729 + step * 7919)
    # Step 0 is fully sharp on purpose: it is the frame the entrance ended on,
    # so the exit begins exactly where the app was rather than jumping. The
    # last step lands on 0, which is all grit and nothing left of the letters.
    span = max(1, steps - 1)
    progress = max(0.0, 1.0 - step / span)
    show_note = bool(note) and text_width(note) <= caps.cols - 2

    pad = max(0, (caps.cols - len(art[0])) // 2)
    below = 5 + (2 if show_note else 0)
    top = max(1, (caps.rows - len(art) - below) // 2)

    rows: list[Text] = [Text() for _ in range(top)]
    colour = (p.accent if progress > 0.66 else
              p.accent2 if progress > 0.33 else p.border)
    for line in art:
        rows.append(Text().add(' ' * pad + _resolve(line, progress, grit, rng),
                               colour))
    # The rule outlives the letters by a frame or two and fades with them,
    # which keeps the block from appearing to fall out of an empty sky.
    rows.append(Text().add(' ' * pad + (caps.g('hh') if caps.glyphs !=
                                        GlyphLevel.ASCII else '=')
                           * len(art[0]), p.border))
    rows.append(Text())
    rows.append(Text().add(OUT_WORD.center(caps.cols).rstrip(), p.dim))
    if show_note:
        rows += [Text(), Text().add(note.center(caps.cols).rstrip(), p.dim)]
    return rows


def farewell_frame(caps: Caps, note: str = '') -> list[Text]:
    """The last thing on screen: the word, and what you did, centred alone.

    Held for a beat after the wordmark has gone, because a dissolve that ends
    on an empty screen ends on nothing, and the point of lingering is to have
    something worth lingering on.
    """
    p = caps.palette
    art, _ = art_for(caps)
    show_note = bool(note) and text_width(note) <= caps.cols - 2
    top = max(1, (caps.rows - len(art) - 5) // 2 + len(art) // 2)

    rows: list[Text] = [Text() for _ in range(top)]
    rows.append(Text().add(OUT_WORD.center(caps.cols).rstrip(), p.accent,
                           bold=True))
    if show_note:
        rows += [Text(), Text().add(note.center(caps.cols).rstrip(), p.dim)]
    return rows


def outro(tty, caps: Caps, note: str = '',
          hold: float = OUT_HOLD_SECONDS) -> None:
    """Play the exit animation. Never raises, never waits for a key.

    Quitting must not be the thing that fails, so every write is guarded and
    any trouble simply ends the animation: the caller has already saved state
    and is on its way out either way.
    """
    if not fits(caps):
        return
    try:
        for step in range(OUT_STEPS):
            tty.write('\x1b[2J\x1b[H'
                      + render_lines(caps, out_frame(caps, step, note=note))
                      .replace('\n', '\r\n'))
            time.sleep(OUT_FRAME_SECONDS)
        tty.write('\x1b[2J\x1b[H'
                  + render_lines(caps, farewell_frame(caps, note))
                  .replace('\n', '\r\n'))
        if hold:
            time.sleep(hold)
        tty.write('\x1b[2J\x1b[H')
    except Exception:
        return


def roster_note(registry) -> str:
    """One line naming what the load found. Empty if it found nothing."""
    try:
        n = registry.tally()
    except AttributeError:
        return ''
    if not n.get('tools'):
        return ''
    return (f'{n["tools"]} tools, {n["lessons"]} lessons, '
            f'{n["drills"]} drills, {n["challenges"]} practice sessions')


def play(tty, caps: Caps, work=None, clock=time.monotonic,
         hold: bool = True, note_from=None) -> object:
    """Animate while `work` runs, then wait for a key. Returns `work`'s result.

    `work` is called after the first frame is on screen, so the wait it
    causes is spent looking at something. A keypress during the animation ends
    it early *and* counts as the key that releases the hold, because someone
    who pressed a key to skip the entrance is asking to get on with it, not
    asking to press a second one. The work still finishes either way: skipping
    an animation is not a request to skip loading the app.

    `hold=False` restores the old timed floor, and is what a caller that
    cannot present a keyboard should pass.
    """
    result = None
    started = clock()
    skipped = False
    drew = False

    for step in range(STEPS):
        try:
            tty.write('\x1b[2J\x1b[H'
                      + render_lines(caps, frame(caps, step)).replace('\n', '\r\n'))
            drew = True
        except Exception:
            break
        if step == 0 and work is not None:
            result = work()
            work = None
        if not skipped:
            try:
                if tty.read_keys(timeout=FRAME_SECONDS):
                    skipped = True
            except Exception:
                time.sleep(FRAME_SECONDS)

    if work is not None:
        result = work()
    if skipped:
        return result

    # Nothing reached the screen, so there is no entrance to hold on: waiting
    # for a key here would be a hang in front of a blank terminal.
    if not (hold and drew):
        remaining = MIN_SECONDS - (clock() - started)
        if remaining > 0:
            time.sleep(remaining)
        return result

    note = ''
    if note_from is not None:
        try:
            note = note_from(result)
        except Exception:
            note = ''          # an entrance must never be what breaks a launch
    try:
        tty.write('\x1b[2J\x1b[H'
                  + render_lines(caps, frame(caps, STEPS - 1, hold=True,
                                             note=note))
                  .replace('\n', '\r\n'))
    except Exception:
        return result

    for _ in range(HOLD_EMPTY_READS):
        try:
            if tty.read_keys(timeout=None):
                break
        except Exception:
            break
    return result
