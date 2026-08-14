#!/usr/bin/env python3
"""Content graph checks. Run after every content change (D12).

`validate.py` looks at what the content *says*; `test.py` looks at what the app
*does*. The split matters because most of what goes wrong in a content-heavy
app is a dangling reference or a rule quietly broken in one file out of fifty,
and that is cheap to catch here and expensive to catch by clicking.

Errors fail the build. Warnings are things worth seeing that may be deliberate,
so they are reported and do not fail.
"""

from __future__ import annotations

import sys

from hone import adapters as A
from hone import loader
from hone.config import EXIT_CHORD
from hone.keys import AMBIGUOUS_LEGACY, KeyError_, parse_seq, unparse_seq
from hone.loader import KINDS
from hone.screens.drill import ORACLE_TYPES

VIEW_KINDS = ('lessons', 'challenges', 'drills')


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, where: str, msg: str) -> None:
        self.errors.append(f'{where}: {msg}')

    def warn(self, where: str, msg: str) -> None:
        self.warnings.append(f'{where}: {msg}')


def check_ids(mod, rep: Report) -> None:
    for kind in KINDS:
        seen: set[str] = set()
        for i, item in enumerate(mod.items(kind)):
            iid = item.get('id')
            if not iid:
                rep.error(f'{mod.id}/{kind}[{i}]', 'item has no id')
                continue
            if iid in seen:
                rep.error(f'{mod.id}/{kind}', f'duplicate item id {iid!r}')
            seen.add(iid)


def check_lesson_links(mod, rep: Report) -> None:
    ids = {l.get('id') for l in mod.lessons}
    for lesson in mod.lessons:
        nxt = lesson.get('next')
        if nxt and nxt not in ids:
            rep.error(f'{mod.id}/lessons/{lesson.get("id")}',
                      f'next points at {nxt!r}, which is not a lesson here')


def check_oracle_drill(d, where: str, dtype: str, rep: Report) -> None:
    """Prove an oracle drill is answerable, by answering it.

    Same argument as the regex branch below, with more teeth: these drills are
    graded by running the reference, so an author who fat-fingers a filter
    ships a drill that *nobody* can pass, and the tool would report the
    student's correct answer as too narrow against a reference that selects
    nothing. Running it here is the only way to find that.

    When the tool is not installed this degrades to a structural check and
    says so. A build machine without tshark must still be able to validate the
    content; it just cannot make this particular promise about it.
    """
    from hone.screens.drill import ORACLE_TYPES as OT

    answer = str(d.get('answer') or '').strip()
    if not answer:
        rep.error(where, f'{dtype} drill has no reference answer')
        return
    for alt in d.get('accepts') or ():
        if not isinstance(alt, str):
            rep.error(where, f'{dtype} accepts entry {alt!r} is not a string')

    name, language = OT[dtype]
    adapter = A.get(name)
    if adapter is None or not adapter.available():
        rep.warn(where, f'{name} not installed: reference answer unproven')
        return
    if language and hasattr(adapter, 'grades') and not adapter.grades(language):
        rep.warn(where, f'{adapter.why_not(language)}: reference unproven')
        return

    try:
        adapter.setup({})
        verdict = (adapter.evaluate(answer, answer, language) if language
                   else adapter.evaluate(answer, answer))
    except Exception as e:
        rep.error(where, f'its own reference answer could not be run: {e}')
        return

    if not verdict.ok:
        rep.error(where, f'its own reference answer fails: {verdict.detail}')
        return

    # A filter that selects nothing is not wrong, it is untestable: every
    # answer that also selects nothing would pass, including an empty one.
    if language:
        try:
            picked, _ = adapter.select(language, answer)
        except Exception:
            return
        if not picked:
            rep.error(where, 'its reference answer selects no packets, so any '
                             'equally empty answer would pass')


def check_drills(mod, rep: Report, exit_chord: str) -> None:
    """Drills come in two shapes: key sequences, and typed commands."""
    for d in mod.drills:
        where = f'{mod.id}/drills/{d.get("id")}'
        dtype = d.get('type', 'keys')
        if dtype not in ('keys', 'recall', 'command', 'regex', *ORACLE_TYPES):
            rep.error(where, f'unknown drill type {dtype!r}')
            continue
        if not d.get('prompt'):
            rep.warn(where, 'no prompt: the student will see only the id')

        if dtype in ORACLE_TYPES:
            check_oracle_drill(d, where, dtype, rep)
            continue

        if dtype == 'regex':
            if not d.get('match') and not d.get('reject'):
                rep.error(where, 'regex drill has nothing to match or reject')
            if not d.get('answer'):
                rep.error(where, 'regex drill has no reference answer')
            else:
                # The reference answer must itself pass. A drill whose own
                # answer is wrong is unanswerable, and only running it finds out.
                from hone.grading import evaluate_regex
                res = evaluate_regex(str(d['answer']),
                                     list(d.get('match') or ()),
                                     list(d.get('reject') or ()),
                                     d.get('flags'))
                if not res.ok:
                    rep.error(where, f'its own reference answer fails: '
                                     f'{res.detail}')
            continue

        if dtype == 'command':
            answers = [d['answer']] if d.get('answer') else []
            answers += [a for a in (d.get('accepts') or ()) if isinstance(a, str)]
            if not answers:
                rep.error(where, 'command drill has no answer')
            elif len(set(' '.join(a.split()) for a in answers)) != len(answers):
                rep.error(where, 'an accepts alternative duplicates the answer')
            for a in answers:
                if not a.strip():
                    rep.error(where, 'empty answer string')
            continue

        seqs = []
        try:
            if d.get('keys'):
                seqs.append(parse_seq(d['keys']))
            for alt in d.get('accepts') or ():
                if isinstance(alt, str):
                    rep.error(where, f'accepts entry {alt!r} is a string; key '
                                     f'drills take lists of key strings')
                    continue
                seqs.append(parse_seq(alt))
        except (KeyError_, TypeError) as e:
            rep.error(where, f'unparseable key sequence: {e}')
            continue

        if not seqs:
            rep.error(where, 'no keys and no accepts: nothing to answer')
            continue

        # D19a: the reserved exit chord can never be an answer, or the student
        # would be unable to leave a drill whose answer is the way out. This
        # only bites in capture mode, but a drill can change type, so it is
        # checked for both.
        for seq in seqs:
            for k in seq:
                if str(k) == exit_chord:
                    rep.error(where, f'claims the reserved exit chord '
                                     f'{exit_chord!r} as an answer (D19a)')

        rendered = [' '.join(unparse_seq(s)) for s in seqs]
        if len(set(rendered)) != len(rendered):
            rep.error(where, 'an accepts alternative duplicates another sequence')

        lengths = {len(s) for s in seqs}
        if dtype == 'keys' and len(lengths) > 1:
            rep.warn(where, f'accepted sequences differ in length {sorted(lengths)}; '
                            f'capture mode judges at the shortest')

        # D11: only capture mode can be blocked by terminal ambiguity. A recall
        # drill types the chord as text, so it is answerable anywhere.
        if dtype == 'keys':
            for seq in seqs:
                for k in seq:
                    for named, chord in AMBIGUOUS_LEGACY.items():
                        if str(k) == chord:
                            rep.warn(where, f'{chord} is indistinguishable from '
                                            f'{named} without the Kitty protocol')


def check_drill_collisions(mod, rep: Report) -> None:
    """Two drills with the same answer cannot both be answered correctly.

    Different prompts with identical keystrokes means the student is being
    asked to distinguish something they cannot express, and the scheduler will
    treat one as a weakness forever. Found by a real collision between a
    context-sensitive key and one of the things it does.
    """
    seen: dict[str, str] = {}
    for d in mod.drills:
        if d.get('type') == 'command':
            answer = ' '.join(str(d.get('answer', '')).split())
        else:
            try:
                answer = ' '.join(unparse_seq(parse_seq(d.get('keys') or [])))
            except (KeyError_, TypeError):
                continue
        if not answer:
            continue
        if answer in seen:
            rep.warn(f'{mod.id}/drills/{d.get("id")}',
                     f'answers {answer!r}, the same as '
                     f'{seen[answer]!r}; the student cannot tell them apart')
        else:
            seen[answer] = d.get('id', '?')


def check_challenges(mod, rep: Report) -> None:
    for c in mod.challenges:
        where = f'{mod.id}/challenges/{c.get("id")}'
        if not c.get('goal') and not c.get('title'):
            rep.error(where, 'no goal and no title: nothing to attempt')
        fb = c.get('fallback')
        if fb is not None and fb not in (A.GRADED, A.SELF):
            rep.error(where, f'fallback {fb!r} is not a D8 label the degrade '
                             f'path can honour (graded or self)')
        if (c.get('verify') or {}).get('kind') == A.GRADED:
            rep.error(where, 'verify.kind "graded" has no challenge checker '
                             'wired; grade it as a drill or name an adapter')
        spec = c.get('verify') or {}
        kind = spec.get('kind')
        if kind and kind not in (A.GRADED, A.SELF) and A.get(kind) is None:
            rep.warn(where, f'verify.kind {kind!r} has no adapter built yet; '
                            f'falls back to {c.get("fallback", A.SELF)!r} (D18)')
        fb = c.get('fallback', A.SELF)
        if fb not in (A.SELF, A.GRADED):
            rep.error(where, f'fallback {fb!r} must be {A.SELF!r} or {A.GRADED!r}')

        # An `expect` the adapter cannot read is worse than no expect at all:
        # it looks like verification and silently is not. This exact bug shipped
        # once, as a prose string where a dict belonged.
        expect = spec.get('expect')
        if expect is not None:
            if not isinstance(expect, dict):
                rep.error(where, f'verify.expect must be a dict, got '
                                 f'{type(expect).__name__}: {expect!r}')
            else:
                ad = A.get(kind)
                known = getattr(ad, 'expect_keys', frozenset()) if ad else None
                if known:
                    unknown = sorted(set(expect) - set(known))
                    if unknown:
                        rep.error(where, f'verify.expect has keys the {kind} '
                                         f'adapter does not understand: '
                                         f'{", ".join(unknown)}')
        if (spec.get('kind') and spec['kind'] not in (A.GRADED, A.SELF)
                and not c.get('solution')):
            rep.warn(where, 'adapter-verified but carries no solution, so '
                            'test.py cannot prove it is actually solvable')
        if spec.get('kind') and spec['kind'] not in (A.GRADED, A.SELF) and not expect:
            rep.warn(where, 'declares an adapter but no verify.expect, so it '
                            'only checks that the sandbox exists')


def check_context(mod, rep: Report) -> None:
    """A module with drills must say what world they assume.

    "Delete the line the cursor is on" is meaningless without "you are in
    nvim, in normal mode, on a line of text". The context line is shown above
    every drill prompt, so a module that omits it ships abstract drills.
    """
    if mod.drills and not mod.context:
        rep.error(mod.id, 'has drills but no context line saying what world '
                          'they assume')


def check_views(mod, rep: Report) -> None:
    """D16 rule 1: all three views always render, so an empty one is a choice.

    A module with nothing in any view has no reason to exist, and a drill deck
    with no walkthrough is fine and says so. Anything else is worth a look.
    """
    present = [k for k in VIEW_KINDS if mod.has(k)]
    if not present:
        rep.error(mod.id, 'has no lessons, challenges or drills')
    elif not mod.has('lessons') and not mod.is_drill_deck:
        rep.warn(mod.id, 'no walkthrough, and not a drill deck either')


# ---------------------------------------------------------------------------
# Lint: prose and consistency, behind --lint
#
# These are opinions about writing, not statements about correctness, and they
# are wrong often enough that they must not be able to fail a build. Kept out
# of the default run for one specific reason: a validator that always prints
# ten complaints you have decided to ignore is a validator you stop reading,
# and then it stops catching the real errors too.
# ---------------------------------------------------------------------------

#: Never in prose: it is the author's own rule, and the one house-style item
#: here that is genuinely absolute rather than a matter of degree.
EM_DASH = '\u2014'

#: Prompts should say what to *do*. A prompt beginning like this is usually a
#: statement about the tool rather than an instruction to the student.
WEAK_PROMPT_STARTS = ('the ', 'this ', 'it ', 'there ')

#: Roughly two wrapped lines in the narrowest supported terminal. Wrapping is
#: fine; a prompt you have to re-read is not. Set from the real distribution,
#: so it flags outliers rather than the house style.
MAX_PROMPT = 96

#: Quiz prompts get more room because a good one is often a scenario, and the
#: setup is the question. "You close the terminal window. What happens to the
#: import?" cannot be said in a drill prompt's worth of words.
MAX_QUIZ_PROMPT = 140

#: A title has to fit a list row beside a progress bar. This is what fits.
MAX_TITLE = 52

#: A lesson with less prose than this is usually a heading someone meant to
#: come back to.
MIN_LESSON_PROSE = 200

#: Every prose-bearing field, per kind. Anything not listed is structural
#: (ids, key sequences, shell commands) and must not be linted as writing:
#: a shell command legitimately contains double spaces and no full stop.
PROSE_FIELDS = {
    'lessons': ('title', 'concept', 'misconceptions', 'try_it'),
    'modules': ('context',),
    'challenges': ('title', 'goal', 'steps', 'free'),
    'drills': ('prompt', 'teach'),
    'quiz': ('prompt', 'teach'),
}


def _prose(item: dict, fields) -> list[tuple[str, str]]:
    out = []
    for f in fields:
        v = item.get(f)
        if isinstance(v, str):
            out.append((f, v))
        elif isinstance(v, (list, tuple)):
            out.extend((f, part) for part in v if isinstance(part, str))
    return out


def lint_module(mod, rep: Report) -> None:
    where = mod.id

    for kind in KINDS:
        for it in mod.items(kind):
            iid = it.get('id', '?')
            for field, text in _prose(it, PROSE_FIELDS.get(kind, ())):
                if EM_DASH in text:
                    rep.warn(f'{where}/{iid}',
                             f'em dash in {field}; use a colon, comma or full '
                             f'stop')
                if '  ' in text.strip():
                    rep.warn(f'{where}/{iid}', f'double space in {field}')

            prompt = it.get('prompt')
            if isinstance(prompt, str):
                cap = MAX_QUIZ_PROMPT if kind == 'quiz' else MAX_PROMPT
                if len(prompt) > cap:
                    rep.warn(f'{where}/{iid}',
                             f'prompt is {len(prompt)} chars, over {cap}')
                if kind == 'drills':
                    if prompt.lower().startswith(WEAK_PROMPT_STARTS):
                        rep.warn(f'{where}/{iid}',
                                 'drill prompt describes rather than instructs')
                    if not prompt.rstrip().endswith(('.', '?', ':')):
                        rep.warn(f'{where}/{iid}',
                                 'drill prompt does not end in . ? or :')

            title = it.get('title')
            if isinstance(title, str) and len(title) > MAX_TITLE:
                rep.warn(f'{where}/{iid}',
                         f'title is {len(title)} chars, over {MAX_TITLE}')

    for les in mod.lessons:
        size = sum(len(t) for _, t in
                   _prose(les, PROSE_FIELDS['lessons'][1:]))
        if size < MIN_LESSON_PROSE:
            rep.warn(f'{where}/{les.get("id", "?")}',
                     f'lesson has {size} chars of prose; is it finished?')

    # Coverage is 100% as of 2026-08-12, so regressions are named one at a
    # time. (This started as a per-module ratio to avoid printing 181
    # identical lines; with zero bare drills the roster IS the signal.)
    for d in mod.drills:
        if not d.get('teach'):
            rep.warn(f'{where}/{d.get("id", "?")}',
                     'drill has no teach line, so a wrong answer explains '
                     'nothing')


def lint_registry(reg, rep: Report) -> None:
    """Cross-module consistency: the same wording meaning the same thing."""
    titles: dict[str, list[str]] = {}
    for mod in reg:
        for kind in KINDS:
            for it in mod.items(kind):
                t = it.get('title') or it.get('prompt')
                if isinstance(t, str):
                    titles.setdefault(t.strip().lower(), []).append(
                        f'{mod.id}/{it.get("id", "?")}')
    for text, owners in sorted(titles.items()):
        if len(owners) > 1:
            rep.warn('cross-module',
                     f'same wording in {", ".join(owners)}: {text[:48]}')


def check_duplicate_keys(rep: Report, package: str = 'hone.content') -> None:
    """A dict literal that sets the same key twice, read from the source.

    Every other check here runs against loaded content, and by then this bug
    is already invisible: Python keeps the last value silently, so a lesson
    with two `next` keys parses fine and chains correctly right up until
    someone edits near the dead one. Five of them had accumulated, each the
    signature of a lesson inserted after the fact. Only the source text can
    show them, so this check reads it.
    """
    import ast
    import collections
    import pathlib

    here = pathlib.Path(__file__).parent / package.replace('.', '/')
    for path in sorted(here.glob('*.py')):
        if path.name == '__init__.py':
            continue
        try:
            tree = ast.parse(path.read_text(encoding='utf-8'))
        except SyntaxError as e:
            rep.error(path.name, f'cannot parse: {e}')
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Dict):
                continue
            keys = [k.value for k in node.keys
                    if isinstance(k, ast.Constant) and isinstance(k.value, str)]
            dupes = sorted(k for k, n in collections.Counter(keys).items() if n > 1)
            if not dupes:
                continue
            ident = next((v.value for k, v in zip(node.keys, node.values)
                          if isinstance(k, ast.Constant) and k.value == 'id'
                          and isinstance(v, ast.Constant)), '?')
            rep.error(f'{path.stem}/{ident}',
                      f'line {node.lineno}: duplicate key '
                      f'{", ".join(repr(d) for d in dupes)}; the earlier value '
                      f'is dead code')


def check_prereqs(reg, rep: Report) -> None:
    for mod in reg:
        for p in mod.prereqs:
            if p not in reg.ids():
                rep.warn(mod.id, f'prereq {p!r} is not installed in this build '
                                 f'(shown, never enforced: D16 rule 3)')
        if mod.id in mod.prereqs:
            rep.error(mod.id, 'lists itself as a prereq')


def check_packs(reg, rep: Report) -> None:
    """D9: a shared pack must have exactly one owner."""
    owners: dict[str, list[str]] = {}
    for mod in reg:
        for pack in mod.provides:
            owners.setdefault(pack, []).append(mod.id)
    for pack, mods in owners.items():
        if len(mods) > 1:
            rep.error('packs', f'{pack!r} is provided by more than one module: '
                               f'{", ".join(mods)}')


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    exit_chord = EXIT_CHORD
    if '--exit-key' in argv:
        exit_chord = argv[argv.index('--exit-key') + 1]
    lint = '--lint' in argv

    reg = loader.load_all()
    rep = Report()

    for err in reg.errors:
        rep.error(err.name, err.message)

    for mod in reg:
        check_ids(mod, rep)
        check_lesson_links(mod, rep)
        check_drills(mod, rep, exit_chord)
        check_drill_collisions(mod, rep)
        check_challenges(mod, rep)
        check_views(mod, rep)
        check_context(mod, rep)
        if lint:
            lint_module(mod, rep)
    check_prereqs(reg, rep)
    check_packs(reg, rep)
    check_duplicate_keys(rep)
    if lint:
        lint_registry(reg, rep)

    counts = {k: sum(len(m.items(k)) for m in reg) for k in KINDS}
    print(f'{len(reg)} modules: ' + ', '.join(f'{v} {k}' for k, v in counts.items()))

    for w in rep.warnings:
        print(f'  warning  {w}')
    for e in rep.errors:
        print(f'  ERROR    {e}')

    if rep.errors:
        print(f'\nFAILED: {len(rep.errors)} error(s), {len(rep.warnings)} warning(s)')
        return 1
    print(f'\nOK: 0 errors, {len(rep.warnings)} warning(s)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
