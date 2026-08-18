"""Is each module production quality, and does it flow?

`audit.py` asks whether the survival material arrives in time. `ramp.py` asks
whether anything is drilled that no lesson teaches. Both are now clean, and a
module can pass both while still reading badly, which is the gap this fills.

The complaint this is built to measure, in the author's words: newer lessons
are longer and clearer, older ones are short and "kind of too direct". That is
two distinct faults and they need separate numbers.

**DEPTH** is how much prose a lesson spends. Below about 900 characters a
lesson is a reference card: it states what is true and moves on. That is fine
in a cheat sheet and it is not a walkthrough, and it is the shape of most of
the roster's older material.

**EXPLANATION** is whether the prose says *why*. A lesson that asserts reads
"`-a` preserves permissions". A lesson that explains reads "`-a` preserves
permissions, because a copy whose metadata is wrong is a copy you discover is
wrong much later". The difference is causal connectives, and counting them per
thousand characters separates the two styles surprisingly well. It is a proxy,
not a judgement, and it is only ever read alongside the text.

**CONSISTENCY** is the spread within one module. A module with one 3000
character lesson and five 500 character ones has been edited rather than
written, and it reads exactly like that: the new material is generous and the
old material next to it feels curt by comparison. This is the specific thing
the author noticed, and max/min across a module is what shows it.

**STRUCTURE** is whether each lesson carries its examples, its misconceptions
and its try-it lines, because a lesson missing those is thin whatever its
character count says.

**FLOW** is whether the `next` chain forms one unbroken path from the first
lesson to the last, with nothing orphaned and nothing pointing backwards.

None of these five is quality. Together they find the modules where quality is
worth a human's attention, which is what an audit is for.
"""
import re
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from hone import loader  # noqa: E402

#: Below this a lesson states rather than teaches.
THIN = 900

#: A comfortable walkthrough lesson, for scale.
GOOD = 1600

#: Phrases that mark prose doing explanatory work rather than asserting.
CAUSAL = [
    'because', 'which is why', 'the reason', 'so that', 'that is why',
    'which means', 'so a ', 'so the ', 'therefore', 'in other words',
    'the point is', 'worth knowing', 'the useful', 'which is what',
    'that is the', 'rather than', 'the difference', 'otherwise',
    'catches people', 'the trap', 'people assume', 'and it is not',
]


def concept(lesson):
    return str(lesson.get('concept', ''))


def explanation_density(text):
    """Causal connectives per 1000 characters."""
    if not text:
        return 0.0
    low = text.lower()
    hits = sum(low.count(p) for p in CAUSAL)
    return round(hits * 1000 / len(text), 1)


def flow_ok(mod):
    """Does `next` form one unbroken path over every lesson?"""
    ids = [l.get('id') for l in mod.lessons]
    if not ids:
        return True, ''
    by_id = {l.get('id'): l for l in mod.lessons}
    seen, cur, steps = set(), ids[0], 0
    while cur and cur not in seen:
        seen.add(cur)
        cur = by_id.get(cur, {}).get('next')
        steps += 1
        if steps > len(ids) + 1:
            break
    missed = [i for i in ids if i not in seen]
    if missed:
        return False, f'unreachable: {", ".join(missed[:3])}'
    return True, ''


def audit(mod):
    lens = [len(concept(l)) for l in mod.lessons] or [0]
    text = '\n'.join(concept(l) for l in mod.lessons)
    ex = [len(l.get('examples') or ()) for l in mod.lessons]
    ok, flow_note = flow_ok(mod)
    return {
        'id': mod.id,
        'group': mod.group,
        'lessons': len(mod.lessons),
        'median': int(statistics.median(lens)),
        'thin': sum(1 for n in lens if n < THIN),
        'spread': round(max(lens) / max(min(lens), 1), 1),
        'explain': explanation_density(text),
        'lean_ex': sum(1 for n in ex if n < 2),
        'no_misc': sum(1 for l in mod.lessons if not l.get('misconceptions')),
        'no_try': sum(1 for l in mod.lessons if not l.get('try_it')),
        'chal': len(mod.challenges),
        'quiz': len(mod.quiz),
        'flow': 'ok' if ok else flow_note,
    }


def score(r):
    """Higher is worse. Weighted towards the faults actually reported."""
    s = 0
    s += r['thin'] * 3                       # terse lessons, the main complaint
    s += max(0, (GOOD - r['median']) // 200)  # how far below a good lesson
    s += 4 if r['explain'] < 4 else (2 if r['explain'] < 6 else 0)
    s += 3 if r['spread'] >= 4 else (1 if r['spread'] >= 2.5 else 0)
    s += r['lean_ex']
    s += r['no_misc'] + r['no_try']
    s += 3 if r['chal'] < 3 else 0
    s += 2 if r['quiz'] < 4 else 0
    s += 5 if r['flow'] != 'ok' else 0
    return s


def tier(s):
    if s >= 22:
        return 'REWRITE'
    if s >= 12:
        return 'DEEPEN'
    if s >= 6:
        return 'POLISH'
    return 'ok'


def main():
    reg = loader.load_all()
    rows = [audit(m) for m in reg]
    for r in rows:
        r['score'] = score(r)
        r['tier'] = tier(r['score'])
    rows.sort(key=lambda r: (-r['score'], r['id']))

    print(f'{"module":13}{"grp":9}{"les":>4}{"med":>6}{"thin":>5}{"spr":>5}'
          f'{"expl":>6}{"ex<2":>5}{"chal":>5}{"quiz":>5}{"score":>6}  tier')
    print('-' * 96)
    for r in rows:
        print(f'{r["id"]:13}{r["group"][:8]:9}{r["lessons"]:4d}{r["median"]:6d}'
              f'{r["thin"]:5d}{r["spread"]:5.1f}{r["explain"]:6.1f}'
              f'{r["lean_ex"]:5d}{r["chal"]:5d}{r["quiz"]:5d}{r["score"]:6d}'
              f'  {r["tier"] if r["tier"] != "ok" else ""}')

    print()
    for t in ('REWRITE', 'DEEPEN', 'POLISH'):
        names = [r['id'] for r in rows if r['tier'] == t]
        print(f'{t:8} {len(names):2d}  {" ".join(names)}')
    clean = [r for r in rows if r['tier'] == 'ok']
    print(f'{"ok":8} {len(clean):2d}  {" ".join(r["id"] for r in clean)}')

    broken = [r for r in rows if r['flow'] != 'ok']
    if broken:
        print('\nflow problems:')
        for r in broken:
            print(f'  {r["id"]}: {r["flow"]}')

    print()
    print(f'median lesson length across roster: '
          f'{int(statistics.median([r["median"] for r in rows]))} chars')
    print(f'lessons under {THIN} chars: '
          f'{sum(r["thin"] for r in rows)} of {sum(r["lessons"] for r in rows)}')


main()
