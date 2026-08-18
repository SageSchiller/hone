"""Does every module teach what it goes on to demand?

`audit.py` asks three mechanical questions about the start of a module: entry,
exit, notation. Passing it means a student can get in and out of the tool. It
says nothing at all about the middle, and the middle is where a module either
carries someone to competence or quietly leaves them behind.

This asks the other question, and it is the one a real student's report turns
into: **is anything drilled or set as a challenge that the lessons never
taught?** "It was really unclear what the commands were it was asking me to do"
is exactly that failure, and unlike ramp quality in general it is countable.

The rule is deliberately generous. A token counts as taught if it appears
anywhere in any lesson, in prose or in a code example, at any position. So a
flag here is not a pacing quibble or a wording preference: it is a drill asking
for something the walkthrough never mentions, anywhere, once.

What this still cannot see, and what only reading can judge:

  - whether an explanation is any good
  - whether the order builds or merely accumulates
  - whether "taught" meant a sentence in passing or an actual teaching
  - whether the last lesson leaves you able to use the tool

Treat a clean report as the floor, not the ceiling.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from hone import loader  # noqa: E402

#: Tokens too common to mean anything. Matching them would hide real gaps
#: behind noise rather than reveal it.
NOISE = {
    'the', 'and', 'a', 'to', 'of', 'in', 'is', 'it', 'for', 'on', 'you',
    'run', 'type', 'use', 'with', 'from', 'that', 'this', 'not', 'or',
    'file', 'files', 'line', 'lines', 'text', 'name', 'do', 'be', 'e',
}

#: A key sequence as the content writes it: C-x, M-w, SPC, C-b, RET, TAB.
KEYISH = re.compile(r'^(?:[CMS]-\S+|SPC|RET|TAB|ESC|DEL|BSP|F\d+)$')


def lesson_corpus(mod):
    """Everything the walkthrough says, prose and code alike."""
    parts = []
    for l in mod.lessons:
        parts += [str(l.get('title', '')), str(l.get('concept', ''))]
        for e in l.get('examples') or ():
            parts += [str(e.get('label', '')), str(e.get('code', '')),
                      str(e.get('note', ''))]
        parts += [str(m) for m in l.get('misconceptions') or ()]
        parts += [str(x) for x in l.get('try_it') or ()]
    return '\n'.join(parts)


def demanded(mod):
    """(token, where) pairs the drills and challenges require of the student."""
    out = []
    for d in mod.drills:
        did = d.get('id', '?')
        dtype = d.get('type')
        if dtype in ('keys', 'recall'):
            seq = [str(k) for k in d.get('keys') or ()]
            if seq:
                out.append((' '.join(seq), f'drill {did}'))
        elif dtype == 'command':
            ans = str(d.get('answer') or '')
            head = ans.split()
            if head:
                out.append((head[0], f'drill {did}'))
            for flag in re.findall(r'(?<!\S)--?[a-zA-Z][\w-]*', ans):
                out.append((flag, f'drill {did}'))

    for ch in mod.challenges:
        cid = ch.get('id', '?')
        for step in ch.get('steps') or ():
            hint = str(step.get('hint') or '')
            # A hint is where a challenge names the thing to press or type.
            for tok in re.findall(r'`([^`]+)`|(?<!\S)([CMS]-\S+)', hint):
                t = clean(tok[0] or tok[1])
                if t and t.lower() not in NOISE:
                    out.append((t, f'challenge {cid}'))
    return out


def clean(token: str) -> str:
    """Strip the prose punctuation a hint wraps around a key sequence.

    "Esc then SPC f s, and it saves" yields `SPC` and `s,` without this, and
    a trailing comma reported as an untaught key is noise that buries the
    real findings underneath it.
    """
    t = token.strip().strip(',;.')
    # A half-caught expression, from a backtick spanning something the regex
    # could not close. Reporting it teaches nobody anything.
    if t.count('(') != t.count(')'):
        return ''
    return t


def shift_forms(token: str) -> list[str]:
    """How prose writes a shifted key, versus how a capture drill records it.

    A drill answer is `S-f` because that is what the keyboard sent. A lesson
    writes `F`, because that is what a person presses and what every pager
    manual has said for forty years. They are the same keystroke, and
    reporting the lesson as not teaching it is a false positive that buries
    the real findings underneath it.
    """
    out = [token]
    if token.startswith('S-') and len(token) == 3 and token[2].isalpha():
        out.append(token[2].upper())
    return out


def taught(corpus, token):
    """Generous: anywhere in the walkthrough, prose or code, counts."""
    if any(f in corpus for f in shift_forms(token)):
        return True
    parts = token.split()
    if len(parts) > 1 and all(
            any(f in corpus for f in shift_forms(p)) for p in parts):
        # A sequence counts as taught when every key in it is, since content
        # legitimately writes "SPC f s" as "SPC f" then "s" in a tree.
        return True
    return False


def with_prereqs(reg, mod, seen=None):
    """This module's walkthrough plus every module it declares as a prereq.

    A module is allowed to lean on what it says you should read first. Linux
    Advanced using `grep` is not a gap when Linux Basics is its prereq and
    teaches it at length; demanding otherwise would mean re-teaching grep in
    nine modules, which is worse content, not better.

    Transitive, because prereq chains are: org names doom, doom names vim.
    """
    if seen is None:
        seen = set()
    if mod.id in seen:
        return ''
    seen.add(mod.id)
    parts = [lesson_corpus(mod)]
    for pid in mod.prereqs or ():
        other = reg.get(pid)
        if other is not None:
            parts.append(with_prereqs(reg, other, seen))
    return '\n'.join(parts)


def main():
    reg = loader.load_all()
    rows = []
    for mod in reg:
        corpus = with_prereqs(reg, mod)
        if not corpus.strip():
            continue                      # drill decks teach nothing on purpose
        gaps = []
        seen = set()
        for token, where in demanded(mod):
            if token in seen or token.lower() in NOISE:
                continue
            seen.add(token)
            if not taught(corpus, token):
                gaps.append((token, where))
        if gaps:
            rows.append((mod.id, len(mod.lessons), len(seen), gaps))

    rows.sort(key=lambda r: -len(r[3]))
    total = 0
    for mid, nles, ndem, gaps in rows:
        total += len(gaps)
        print(f'{mid}  ({nles} lessons, {ndem} things demanded, '
              f'{len(gaps)} never taught)')
        for token, where in sorted(gaps)[:12]:
            print(f'    {token:28} {where}')
        if len(gaps) > 12:
            print(f'    ... and {len(gaps) - 12} more')
        print()

    clean = len([m for m in reg if m.lessons]) - len(rows)
    print(f'{clean} modules demand nothing they did not teach.')
    print(f'{len(rows)} modules have gaps, {total} in total.')
    print()
    print('Generous matching: a token counts as taught if it appears anywhere')
    print('in any lesson. Everything listed is absent from the walkthrough.')


main()
