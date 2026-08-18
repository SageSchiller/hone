"""Audit every hone module for the foundations gap found in Doom.

The first pass asked whether a foundation was taught anywhere and rated Doom
clean, which contradicted a real student's real session. The question is not
presence, it is **position**. Doom teaches how to quit Emacs, what a chord is,
and that SPC f s is three presses in lesson 9 of 9. All of it is correct, and
all of it arrives after the eight lessons and every challenge that assume it.

So each foundation is scored by *where* it first appears. Taught in lesson 1 or
2 is in time. Taught later is a cliff: the student meets the tool before the
sentence that makes the tool usable. Never taught is worse.

Three foundations:

  ENTRY     how to start the tool
  EXIT      how to get back out, which matters most for anything that takes
            the screen and strands you
  NOTATION  what the key notation means, for modules that use one
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from hone import adapters as A, loader  # noqa: E402

A.load_builtin()

#: Taught by here and the student meets it in time. Lesson 3 of a nine-lesson
#: module is already past the first challenge in most of the roster.
IN_TIME = 2

EXIT_PATTERNS = {
    'doom': [r'C-x C-c'], 'org': [r'C-x C-c'], 'emacs': [r'C-x C-c'],
    'vim': [r':q\b', r':wq', r':qa'],
    'tmux': [r'C-b d', r'\bdetach'],
    'sql': [r'\.quit', r'\\q\b', r'\bquit\b'],
    'python': [r'exit\(\)', r'quit\(\)', r'C-d'],
    'msf': [r'\bexit\b', r'\bquit\b'],
    'powershell': [r'\bexit\b'],
    'docker': [r'\bexit\b', r'detach'],
    'ssh': [r'\bexit\b', r'\blogout\b'],
    'strace': [r'C-c'],
    'gdb': [r'\bquit\b', r'\bq\b'],
    'tcpdump': [r'C-c'],
    'ncsocat': [r'C-c'],
    'gpg': [r'C-d', r'\bexit\b'],
}

#: Lowercase only, deliberately. A real chord is written `C-x`; `C-M` with a
#: capital is the tail of an ASCII commit graph (A-B-C-M), and matching it
#: reported the git module as using Emacs notation it never explains.
NOTATION_USED = [
    (r'\bC-[a-z]\b', 'C- chords'),
    (r'\bM-[a-z]\b', 'M- chords'),
    (r'\bSPC [a-z]', 'SPC leader sequences'),
]

NOTATION_EXPLAINED = [
    'hold control', 'holding control', 'ctrl', 'control key',
    'means hold', 'press and hold', 'chord', 'one after the other',
    'in sequence', 'sequentially', 'meta key', 'alt key', 'notation',
    'one key at a time', 'not at the same time',
]


def lesson_blob(l):
    parts = [str(l.get('title', '')), str(l.get('concept', ''))]
    for e in l.get('examples') or ():
        parts += [str(e.get('label', '')), str(e.get('code', '')),
                  str(e.get('note', ''))]
    parts += [str(m) for m in l.get('misconceptions') or ()]
    parts += [str(x) for x in l.get('try_it') or ()]
    return '\n'.join(parts)


#: Prose writes a control key as Ctrl-C; drills and key tables write C-c.
#: Both mean the same keystroke, and an audit that only knows one spelling
#: reports modules as never teaching something they teach in lesson one.
_NOTATION = {
    r'C-c': r'(?:C-c|Ctrl-C|\^C)',
    r'C-d': r'(?:C-d|Ctrl-D|\^D)',
}


def first_lesson_matching(mod, patterns, literal=False):
    """1-based index of the earliest lesson matching, or None.

    Matching is case-insensitive throughout. "Exit that shell" teaches the
    same thing as "type exit", and a case-sensitive audit called the first
    one absent.
    """
    for i, l in enumerate(mod.lessons, 1):
        blob = lesson_blob(l)
        low = blob.lower()
        for p in patterns:
            if literal:
                if p in low:
                    return i
                continue
            if re.search(_NOTATION.get(p, p), blob, re.IGNORECASE):
                return i
    return None


def verdict(pos, total):
    if pos is None:
        return 'never', 3
    if pos <= IN_TIME:
        return f'L{pos}', 0
    return f'L{pos}/{total}', 2


def main():
    reg = loader.load_all()
    rows = []
    for mod in reg:
        total = len(mod.lessons)

        # Only ask "does it show the tool being started" of modules that are
        # about one command. `linux`, `regex` and `linuxutils` are about a
        # subject or a family, so there is no single binary to launch and the
        # question is meaningless: asking it anyway reported four modules as
        # broken for having a name rather than a command.
        # And only when the declared binary IS the subject. `regex` declares
        # nvim because its drills need an editor, `smbenum` declares
        # smbclient as one of several tools it covers. In neither case is
        # "does lesson one launch nvim" a sensible question to ask.
        tool = mod.needs[0] if mod.needs else ''
        subject = tool and (tool in mod.id or mod.id in tool
                            or tool in mod.title.lower())
        if subject:
            entry_pos = first_lesson_matching(
                mod, [rf'(^|\s|`|\$ ){re.escape(tool)}(\s|$|`)'])
            entry_label, entry_cost = verdict(entry_pos, total)
        else:
            entry_label, entry_cost = 'n/a', 0

        exit_pos = exit_label = None
        exit_cost = 0
        if mod.id in EXIT_PATTERNS:
            exit_pos = first_lesson_matching(mod, EXIT_PATTERNS[mod.id])
            exit_label, exit_cost = verdict(exit_pos, total)
            exit_cost = exit_cost + 1 if exit_cost else 0   # stranding is worse

        used = [label for pat, label in NOTATION_USED
                if any(re.search(pat, lesson_blob(l)) for l in mod.lessons)]
        note_label, note_cost = '', 0
        if used:
            npos = first_lesson_matching(mod, NOTATION_EXPLAINED, literal=True)
            note_label, note_cost = verdict(npos, total)
            note_label = f'{note_label} ({", ".join(used)})'

        rows.append({
            'id': mod.id, 'group': mod.group, 'total': total,
            'entry': entry_label, 'exit': exit_label or '-',
            'note': note_label or '-',
            'score': entry_cost + exit_cost + note_cost,
        })

    rows.sort(key=lambda r: (-r['score'], r['id']))
    print(f'{"module":13} {"grp":9} {"les":>3}  {"entry":>7} {"exit":>7}  '
          f'{"score":>5}  notation explained')
    print('-' * 104)
    for r in rows:
        if r['score'] == 0:
            continue
        print(f'{r["id"]:13} {r["group"][:9]:9} {r["total"]:3d}  '
              f'{r["entry"]:>7} {r["exit"]:>7}  {r["score"]:5d}  {r["note"]}')

    clean = sum(1 for r in rows if r['score'] == 0)
    print(f'\n{clean} of {len(rows)} modules clean; '
          f'{len(rows) - clean} have at least one foundation out of position.')
    print('L1/L2 = taught in time.  Ln/total = taught this late.  never = absent.')


main()
