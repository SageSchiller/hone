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
"""

from __future__ import annotations

import random
import time

from .config import APP_TITLE, TAGLINE_PARTS
from .render import Caps, GlyphLevel, Text, render_lines

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

#: A blocking read that returns nothing has hit EOF or a closed stdin, not a
#: patient user. Give up after this many so a redirected or dead terminal
#: cannot spin here forever waiting for a key that can never arrive.
HOLD_EMPTY_READS = 64

#: Never draw into a window the art does not fit. 37 is the block art plus a
#: column of margin either side.
MIN_COLS = 39
MIN_ROWS = 14


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
          seed: int | None = None, hold: bool = False) -> list[Text]:
    """One rendered frame, as rows of styled text.

    `hold` adds the waiting-for-a-key line, and is only ever true on the
    resolved frame: an unresolved frame is still loading and inviting a
    keypress there would be a lie about what the key does.
    """
    p = caps.palette
    art, grit = art_for(caps)
    rng = random.Random(seed if seed is not None else step * 7919)
    progress = min(1.0, (step + 1) / steps)

    pad = max(0, (caps.cols - len(art[0])) // 2)
    # Five rows are reserved below the art rather than four once a hint can
    # sit under the tagline, so the block stays centred instead of drifting
    # down by half a line in the held frame.
    top = max(1, (caps.rows - len(art) - 5) // 2)

    rows: list[Text] = [Text() for _ in range(top)]
    for line in art:
        colour = p.accent if progress >= 1.0 else (
            p.accent2 if progress > 0.5 else p.border)
        rows.append(Text().add(' ' * pad + _resolve(line, progress, grit, rng),
                               colour, bold=progress >= 1.0))

    tag = f' {caps.g("bullet")} '.join(TAGLINE_PARTS)
    rows.append(Text())
    if progress >= 1.0:
        rows.append(Text().add(tag.center(caps.cols).rstrip(), p.dim))
        if hold:
            rows.append(Text().add(HOLD_HINT.center(caps.cols).rstrip(),
                                   p.accent2))
    else:
        # The word for what is happening, and it is also what the app does.
        rows.append(Text().add('sharpening'.center(caps.cols).rstrip(), p.dim))
    return rows


def play(tty, caps: Caps, work=None, clock=time.monotonic,
         hold: bool = True) -> object:
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

    try:
        tty.write('\x1b[2J\x1b[H'
                  + render_lines(caps, frame(caps, STEPS - 1, hold=True))
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
