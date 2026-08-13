"""regex: the pattern language, then the tools that consume it.

**The prerequisite module.** grep, ripgrep, sed, awk, vim's `/` and `:%s`, and
Python's `re` all take patterns, so this unlocks a large part of the roster.
Teaching it once here and treating those tools as delivery mechanisms is why
the roster has no separate grep module.

**Drills are graded by behaviour.** Each one gives strings the pattern must
match and strings it must **not**, and any pattern with the right behaviour
passes. That matters twice over: it accepts the many correct shapes of an
answer rather than one blessed string, and the negatives catch the failure mode
that a positives-only check cannot see, which is a pattern that works by
matching far too much.

**Dialects.** The drills grade with Python's `re`, which is the same engine
behind `grep -P`, `rg` and most modern tooling. Basic `grep` and `sed` use an
older syntax where `+`, `?`, `|` and grouping need backslashes, and vim differs
again. The dialect lesson covers this rather than pretending one syntax exists.
"""

MODULE = {
    'id': 'regex',
    'title': 'regex',
    'group': 'Text processing',
    'blurb': 'The pattern language, and the tools that read it.',
    'context': 'You are writing a pattern, not running a command. Assume no flags unless the drill says otherwise.',
    'prereqs': [],
    'adapter': 'nvim',
    'estimate': '4-6 hours',
    'order': 30,

    # ------------------------------------------------------------------
    'lessons': [
        {
            'id': 'rx-why',
            'title': 'What a regex actually is',
            'next': 'rx-literals',
            'concept': (
                'A regular expression is a tiny program that answers one '
                'question: does this text contain something shaped like this? '
                'The engine walks the text trying to make your pattern fit, and '
                'reports where it succeeded.\n\n'
                'Almost every mistake people make comes from forgetting two '
                'things. First, by default a pattern SEARCHES rather than '
                'matches the whole string: `cat` finds the cat in '
                '`concatenate`. Second, quantifiers are GREEDY: they take as '
                'much as they can and only give back when forced.\n\n'
                'Learning regex is mostly learning to constrain. A pattern that '
                'finds what you wanted is easy; a pattern that finds what you '
                'wanted and nothing else is the actual skill, and it is why '
                'every drill here also gives you strings that must not match.'
            ),
            'examples': [
                {
                    'label': 'Searching, not matching',
                    'code': ('pattern:  cat\n'
                             'matches:  cat, concatenate, the cat sat\n'
                             '\n'
                             'pattern:  ^cat$\n'
                             'matches:  cat, and nothing else'),
                    'note': 'If you did not anchor it, you asked for "contains", '
                            'whatever you meant.',
                },
            ],
            'misconceptions': [
                'A regex does not understand what your data means. It has no '
                'idea what an email address is; it only knows shapes.',
                'Regex cannot parse nested structures. HTML, JSON and balanced '
                'brackets are genuinely beyond it, and reaching for a parser is '
                'not defeat.',
                'A pattern that works on your three test lines is not finished. '
                'The question is always what else it matches.',
            ],
            'try_it': [
                'Run `grep -n cat /usr/share/dict/words | head` if you have a '
                'words file, and notice how much it finds.',
            ],
        },
        {
            'id': 'rx-literals',
            'title': 'Literals, classes and the dot',
            'next': 'rx-quantifiers',
            'concept': (
                'Most characters match themselves. The interesting ones are the '
                'metacharacters, and the first job is knowing which are which.\n\n'
                '`.` matches any single character except a newline. Square '
                'brackets make a CHARACTER CLASS: `[aeiou]` is any one vowel, '
                '`[a-z]` any lowercase letter, `[^0-9]` anything that is not a '
                'digit. Inside brackets most metacharacters lose their power, '
                'which is why `[.]` is a literal dot.\n\n'
                'The shorthands are worth memorising because they appear '
                'everywhere: `\\d` digit, `\\w` word character, `\\s` '
                'whitespace, and their capitals are the negations.'
            ),
            'examples': [
                {
                    'label': 'Classes',
                    'code': ('.        any character except newline\n'
                             '[abc]    one of a, b or c\n'
                             '[a-z]    any lowercase letter\n'
                             '[^0-9]   anything that is not a digit\n'
                             '\\d \\w \\s   digit, word char, whitespace\n'
                             '\\D \\W \\S   the negations'),
                    'note': 'A hyphen at the start or end of a class is a '
                            'literal hyphen: `[-a-z]`.',
                },
                {
                    'label': 'Escaping',
                    'code': ('\\.       a literal dot\n'
                             '\\\\       a literal backslash\n'
                             '[.]      also a literal dot, and easier to read'),
                    'note': 'A character class is often the readable way to '
                            'escape something.',
                },
            ],
            'misconceptions': [
                '`.` is not "any character". It excludes newline unless you ask '
                'otherwise, which is why a multi-line match silently fails.',
                '`\\w` includes the underscore and digits, not just letters. It '
                'is "word character" in the programming sense.',
                'Inside `[...]`, a dot is just a dot. Escaping it there is '
                'harmless but unnecessary.',
            ],
            'try_it': [
                'Write a pattern for a single hex digit two ways: with a range, '
                'and with a shorthand plus a range.',
            ],
        },
        {
            'id': 'rx-quantifiers',
            'title': 'Quantifiers, and why greedy hurts',
            'next': 'rx-anchors',
            'concept': (
                'Quantifiers say how many. `*` is zero or more, `+` is one or '
                'more, `?` is zero or one, and `{2,5}` is an explicit range. '
                'They apply to whatever came immediately before.\n\n'
                'All of them are GREEDY by default: they consume as much as '
                'possible, then hand characters back one at a time only if the '
                'rest of the pattern cannot otherwise fit. This is the single '
                'biggest source of surprise in regex.\n\n'
                'Adding `?` after a quantifier makes it LAZY: it takes as little '
                'as possible instead. `<.*>` on `<a> and <b>` matches the whole '
                'line; `<.*?>` matches just `<a>`. When a pattern grabs far more '
                'than you meant, laziness is usually the fix, and a negated '
                'character class is usually the better one.'
            ),
            'examples': [
                {
                    'label': 'Greedy versus lazy',
                    'code': ('text:     <a> and <b>\n'
                             '\n'
                             '<.*>      matches  <a> and <b>     (greedy)\n'
                             '<.*?>     matches  <a>             (lazy)\n'
                             '<[^>]*>   matches  <a>             (better)'),
                    'note': 'The third is best: it says what you mean rather '
                            'than relying on backtracking to undo an overreach.',
                },
                {
                    'label': 'Counting',
                    'code': ('a*       zero or more a\n'
                             'a+       one or more\n'
                             'a?       optional\n'
                             'a{3}     exactly three\n'
                             'a{2,}    two or more\n'
                             'a{2,5}   between two and five'),
                    'note': 'A quantifier binds to the single item before it. '
                            'Use a group to quantify more than one character.',
                },
            ],
            'misconceptions': [
                '`.*` is not a wildcard for "some stuff here". It is "as much as '
                'possible", and it will happily swallow the rest of the line.',
                'Lazy is not the opposite of broken. `[^x]*` is usually clearer '
                'and faster than `.*?`.',
                'Nesting quantifiers, as in `(a+)+`, can make a pattern take '
                'effectively forever. The drills here will tell you when you '
                'have done it.',
            ],
            'try_it': [
                'On a line of HTML, try `<.*>` then `<.*?>` then `<[^>]*>` and '
                'watch what each one takes.',
            ],
        },
        {
            'id': 'rx-anchors',
            'title': 'Anchors and boundaries',
            'next': 'rx-groups',
            'concept': (
                'Anchors match a position rather than a character, which is why '
                'they consume nothing.\n\n'
                '`^` is the start of the string, or of a line in multiline mode. '
                '`$` is the end. Together they turn "contains" into "is '
                'exactly", which is the most common fix a pattern needs.\n\n'
                '`\\b` is a word boundary: the seam between a word character and '
                'a non-word character. `\\bcat\\b` finds the cat in "the cat '
                'sat" but not in "concatenate", and it is the right answer far '
                'more often than people reach for it.'
            ),
            'examples': [
                {
                    'label': 'Pinning things down',
                    'code': ('^ERROR       lines starting with ERROR\n'
                             'done$        lines ending with done\n'
                             '^$           an empty line\n'
                             '\\bcat\\b      the word cat, not concatenate\n'
                             '^\\s*$        a blank line, whitespace included'),
                    'note': '`^\\s*$` is the pattern for "blank" as a human '
                            'means it.',
                },
            ],
            'misconceptions': [
                '`$` matches before a trailing newline in most tools, which is '
                'why `done$` still matches a line read from a file.',
                '`^` inside square brackets is negation, not an anchor. `[^a]` '
                'and `^a` have nothing to do with each other.',
                'Without multiline mode, `^` and `$` are the ends of the whole '
                'string, not of each line. Tools that work line by line, like '
                'grep, hide this from you.',
            ],
            'try_it': [
                'Find every blank line in a file with `grep -c "^$"`, then try '
                '`grep -c "^\\s*$"` and compare.',
            ],
        },
        {
            'id': 'rx-groups',
            'title': 'Groups, alternation and capture',
            'next': 'rx-dialects',
            'concept': (
                'Parentheses do two jobs at once, and separating them in your '
                'head helps.\n\n'
                'They GROUP, so a quantifier or an alternation applies to more '
                'than one character: `(ab)+` is one or more "ab", and '
                '`^(ERROR|WARN)` anchors both alternatives rather than just the '
                'first.\n\n'
                'They also CAPTURE, remembering what they matched so you can '
                'refer to it. In a substitution the captures come back as `\\1`, '
                '`$1` or `\\g<1>` depending on the tool, which is how '
                'search-and-replace rearranges text rather than only deleting '
                'it. `(?:...)` groups without capturing, for when you only '
                'wanted the first job.'
            ),
            'examples': [
                {
                    'label': 'Both jobs',
                    'code': ('(ab)+           one or more "ab"\n'
                             '^(ERROR|WARN)   either, both anchored\n'
                             '^ERROR|WARN     NOT the same: anchors only ERROR\n'
                             '(?:ab)+         grouped, not captured'),
                    'note': 'Alternation has the lowest precedence of anything, '
                            'which is why the third line is a classic bug.',
                },
                {
                    'label': 'Rearranging with captures',
                    'code': ('text:     Smith, John\n'
                             'pattern:  ^(\\w+), (\\w+)$\n'
                             'replace:  \\2 \\1\n'
                             'result:   John Smith'),
                    'note': 'This is what makes substitution more than deletion.',
                },
            ],
            'misconceptions': [
                'Alternation binds loosest. `^a|b` means "starts with a, or '
                'contains b", which is almost never what was meant.',
                'Capture groups are numbered by their opening parenthesis, left '
                'to right, so nesting them renumbers everything after.',
                'Backreference syntax is not portable. `\\1` in sed and vim, '
                '`$1` in many languages, `\\g<1>` in Python.',
            ],
            'try_it': [
                'Swap two comma-separated fields in a file using vim: '
                '`:%s/^\\(\\w\\+\\), \\(\\w\\+\\)$/\\2 \\1/`.',
            ],
        },
        {
            'id': 'rx-dialects',
            'title': 'The dialects, and which tool speaks which',
            'next': 'rx-tools',
            'concept': (
                'There is no single regex syntax, and pretending otherwise is '
                'why patterns that work in one place fail in another.\n\n'
                'Three families matter. BASIC regex, which plain `grep` and '
                '`sed` use, needs backslashes for `+`, `?`, `|`, `{}` and '
                'grouping. EXTENDED regex, which `grep -E`, `sed -E` and `awk` '
                'use, does not. PERL-compatible, which `grep -P`, `rg`, Python '
                'and most modern tools use, adds `\\d`, `\\w`, lazy quantifiers '
                'and lookaround.\n\n'
                'The practical rule: reach for `-E` or `-P` and stop fighting '
                'backslashes. Vim is its own dialect again, closest to basic, '
                'and `\\v` at the start of a vim pattern switches it to '
                'something much closer to extended.'
            ),
            'examples': [
                {
                    'label': 'The same pattern, three ways',
                    'code': ('extended:  ^(ERROR|WARN)\n'
                             'basic:     ^\\(ERROR\\|WARN\\)\n'
                             'vim:       ^\\(ERROR\\|WARN\\)\n'
                             'vim, \\v:   \\v^(ERROR|WARN)'),
                    'note': 'Vim\'s `\\v` ("very magic") makes vim patterns look '
                            'like everyone else\'s, and is worth typing.',
                },
                {
                    'label': 'Choosing a flavour',
                    'code': ('grep      basic       avoid\n'
                             'grep -E   extended    fine\n'
                             'grep -P   perl        best, needs PCRE support\n'
                             'rg        perl-ish    the default, no flag needed\n'
                             'sed -E    extended    use this\n'
                             'awk       extended\n'
                             'python    perl-ish'),
                    'note': 'ripgrep needing no flag is a real reason to reach '
                            'for it over grep.',
                },
            ],
            'misconceptions': [
                '`\\d` does not work in basic or extended regex. `grep "\\d"` '
                'silently finds nothing useful, and `[0-9]` is the portable '
                'answer.',
                'macOS `sed` is not GNU `sed`. `-E` works on both; `-i` behaves '
                'differently and is a classic portability trap.',
                'These drills grade with Python, so they are the perl-ish '
                'dialect. That matches `rg`, `grep -P` and Python itself.',
            ],
            'try_it': [
                'Run `grep "colou\\?r"` and `grep -E "colou?r"` on the same '
                'file and confirm they do the same thing.',
            ],
        },
        {
            'id': 'rx-tools',
            'title': 'Using it: grep, rg, sed and vim',
            'next': 'rx-lookaround',
            'concept': (
                'The pattern language is the hard part. The tools are '
                'delivery, and each has a small set of flags worth knowing.\n\n'
                'For SEARCHING, `rg` is the default worth building: it is fast, '
                'recursive by default, respects gitignore, and takes '
                'perl-ish patterns with no flag. `grep` remains what exists on '
                'every server, so know `-E`, `-i`, `-v`, `-n`, `-r`, `-o` and '
                '`-c`.\n\n'
                'For CHANGING, `sed -E "s/pattern/replacement/g"` is the '
                'one-liner and vim\'s `:%s/pattern/replacement/g` is the '
                'interactive version. Adding `c` to vim\'s flags makes it '
                'confirm each one, which is the difference between a '
                'substitution you can review and one you have to trust.'
            ),
            'examples': [
                {
                    'label': 'Searching',
                    'code': ('rg "^ERROR"              recursive, fast\n'
                             'rg -i pattern           case insensitive\n'
                             'rg -n pattern           show line numbers\n'
                             'grep -Ern "pat" .       the portable equivalent\n'
                             'grep -o "pat" f         print only the match\n'
                             'grep -v "pat" f         invert: lines without it'),
                    'note': '`-o` is how you extract rather than locate, and '
                            'pairs well with `sort | uniq -c`.',
                },
                {
                    'label': 'Changing',
                    'code': ('sed -E "s/old/new/g" f        print the result\n'
                             'sed -E -i "s/old/new/g" f     edit in place\n'
                             '\n'
                             ':%s/old/new/g                 whole file in vim\n'
                             ':%s/old/new/gc                confirm each one'),
                    'note': 'Run sed without `-i` first, every time. It costs '
                            'one second and it has saved every person who does '
                            'it.',
                },
            ],
            'misconceptions': [
                '`sed -i` has no undo. Preview without it first, and the habit '
                'is worth more than the pattern.',
                'A `/` in your pattern collides with the delimiter. Both sed '
                'and vim let you pick another: `s|a/b|c|` works.',
                'vim substitution without `%` only touches the current line, '
                'which is why "nothing happened" is usually a missing range.',
            ],
            'try_it': [
                'Extract every IP-shaped string from a log with '
                '`rg -o "[0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+" | sort | uniq -c`.',
            ],
        },
        {
            'id': 'rx-lookaround',
            'title': 'Lookaround, and when to stop',
            'concept': (
                'Lookaround matches a position based on what surrounds it, '
                'without consuming anything. `(?=...)` is a positive lookahead, '
                '`(?!...)` a negative one, and `(?<=...)` and `(?<!...)` are the '
                'behind versions.\n\n'
                'The genuinely useful case is "this, but not when followed by '
                'that", which is otherwise awkward to express: '
                '`ERROR(?! recovered)` finds errors that were not recovered. '
                'Extraction is the other: `(?<=user=)\\w+` grabs the value '
                'without the label.\n\n'
                'The last lesson is knowing when to stop. If a pattern needs '
                'three lookarounds and a nested alternation, it will be '
                'unreadable in a month and it is a sign the problem wants a '
                'parser, a two-step pipeline, or a real programming language. '
                'Regex is a tool with an edge, and finding it is part of using '
                'it well.'
            ),
            'examples': [
                {
                    'label': 'Lookaround',
                    'code': ('foo(?=bar)     foo, only when followed by bar\n'
                             'foo(?!bar)     foo, only when NOT followed by bar\n'
                             '(?<=user=)\\w+  the value after user=\n'
                             '(?<!un)happy   happy, but not unhappy'),
                    'note': 'Nothing inside the lookaround is part of the '
                            'match, which is what makes extraction clean.',
                },
                {
                    'label': 'Where the edge is',
                    'code': ('fine:      a log line with known fields\n'
                             'fine:      one-off extraction from a text dump\n'
                             '\n'
                             'stop:      nested HTML or JSON\n'
                             'stop:      balanced brackets\n'
                             'stop:      anything needing three lookarounds'),
                    'note': 'Two greps in a pipeline beat one unreadable '
                            'pattern, and you can debug each half.',
                },
            ],
            'misconceptions': [
                'Lookbehind is not universally supported and often must be '
                'fixed width. `grep -P` and Python have it; extended regex does '
                'not.',
                'A long pattern is not a clever pattern. The one you can read '
                'in six months is the better one.',
            ],
            'try_it': [
                'Find every ERROR line that is not followed by the word '
                'recovered, using `rg "ERROR(?! recovered)"`.',
            ],
        },
    ],

    # ------------------------------------------------------------------
    # Drill: graded live. Every one carries negatives, because a pattern
    # that matches too much is the failure a positives-only check misses.
    # ------------------------------------------------------------------
    'drills': [
        {'id': 'rx-literal', 'type': 'regex',
         'prompt': 'Match any line containing the word cat, anywhere.',
         'match': ['cat', 'the cat sat', 'concatenate'],
         'reject': ['dog', 'CAT'],
         'answer': 'cat',
         'teach': 'A bare pattern searches rather than matches. This is the '
                  'default and the source of most surprise.'},

        {'id': 'rx-word-boundary', 'type': 'regex',
         'prompt': 'Match the word cat only when it stands alone, not inside '
                   'another word.',
         'match': ['cat', 'the cat sat', 'a cat.'],
         'reject': ['concatenate', 'category', 'bobcat'],
         'answer': r'\bcat\b',
         'teach': 'Word boundaries are the right answer far more often than '
                  'people reach for them.'},

        {'id': 'rx-anchor-start', 'type': 'regex',
         'prompt': 'Match lines that start with ERROR.',
         'match': ['ERROR', 'ERROR: disk full'],
         'reject': ['an ERROR happened', 'WARN: ERROR later', 'error: lower'],
         'answer': '^ERROR',
         'teach': 'Anchoring turns "contains" into "starts with". Notice the '
                  'negatives are what prove you did it.'},

        {'id': 'rx-anchor-both', 'type': 'regex',
         'prompt': 'Match a line that is exactly the word done, nothing else.',
         'match': ['done'],
         'reject': ['done deal', 'not done', 'DONE', 'done '],
         'answer': '^done$',
         'teach': 'Both anchors together mean "is exactly", which is the most '
                  'common fix a pattern needs.'},

        {'id': 'rx-blank-line', 'type': 'regex',
         'prompt': 'Match a blank line, counting a line of only spaces or tabs '
                   'as blank.',
         'match': ['', '   ', '\t'],
         'reject': ['x', '  x  '],
         'answer': r'^\s*$',
         'teach': 'The pattern for "blank" as a human means it, rather than as '
                  'a computer does.'},

        {'id': 'rx-digits', 'type': 'regex',
         'prompt': 'Match a line containing at least one digit.',
         'match': ['abc1', '42', 'v2 release'],
         'reject': ['abc', 'no numbers here'],
         'answer': r'\d',
         'teach': r'\d is perl-ish and works in rg, grep -P and Python. Basic '
                  'and extended grep need [0-9] instead.'},

        {'id': 'rx-exact-count', 'type': 'regex',
         'prompt': 'Match a line that is exactly three digits.',
         'match': ['123', '000'],
         'reject': ['12', '1234', 'abc', '12a'],
         'answer': r'^\d{3}$',
         'teach': 'Braces give an exact count. Without both anchors this would '
                  'find three digits inside a longer number.'},

        {'id': 'rx-optional', 'type': 'regex',
         'prompt': 'Match both the British and American spellings of colour.',
         'match': ['colour', 'color', 'the color red'],
         'reject': ['colr', 'colouur'],
         'answer': 'colou?r',
         'teach': '? makes the preceding item optional, and applies to just '
                  'that one character.'},

        {'id': 'rx-class-range', 'type': 'regex',
         'prompt': 'Match a line that is exactly one hexadecimal digit, '
                   'lowercase letters only.',
         'match': ['0', '9', 'a', 'f'],
         'reject': ['g', 'A', '10', ''],
         'answer': '^[0-9a-f]$',
         'teach': 'Ranges combine inside one class. Order does not matter.'},

        {'id': 'rx-negated-class', 'type': 'regex',
         'prompt': 'Match a line containing a character that is not a digit.',
         'match': ['12a34', 'abc', '1 2'],
         'reject': ['123', '0'],
         'answer': r'[^0-9]',
         'teach': 'A caret inside brackets negates the class. It has nothing to '
                  'do with the anchor of the same character.'},

        {'id': 'rx-alternation', 'type': 'regex',
         'prompt': 'Match lines that start with either ERROR or WARN.',
         'match': ['ERROR: x', 'WARN: y'],
         'reject': ['INFO: z', 'an ERROR', 'a WARN'],
         'answer': '^(ERROR|WARN)',
         'teach': 'The classic bug is ^ERROR|WARN, which anchors only the first '
                  'alternative. Alternation binds loosest of everything.'},

        {'id': 'rx-greedy', 'type': 'regex',
         'prompt': 'Match a single HTML tag, and not everything between two of '
                   'them.',
         'match': ['<a>', '<div>'],
         'reject': ['<a> and <b>'],
         'answer': '^<[^>]*>$',
         'teach': 'A negated class says what you mean. A lazy <.*?> also works '
                  'but relies on backtracking to undo an overreach.'},

        {'id': 'rx-group-quantifier', 'type': 'regex',
         'prompt': 'Match a line that is one or more repetitions of "ab", and '
                   'nothing else.',
         'match': ['ab', 'abab', 'ababab'],
         'reject': ['', 'aba', 'abc', 'ba'],
         'answer': '^(ab)+$',
         'teach': 'A quantifier binds to the single item before it, so grouping '
                  'is how you quantify more than one character.'},

        {'id': 'rx-ip-ish', 'type': 'regex',
         'prompt': 'Match an IPv4-shaped string: four groups of digits split by dots. It need not reject 999.',
         'match': ['10.0.0.1', '192.168.1.254', 'from 8.8.8.8 ok'],
         'reject': ['10.0.0', 'abc.def.ghi.jkl', '1x2x3x4'],
         'answer': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
         'teach': 'The dots must be escaped: an unescaped dot matches any '
                  'character, which is why 1x2x3x4 is in the reject list. This '
                  'version still finds 1.2.3.4 inside 1.2.3.4.5.6.7, and the '
                  'strict drill later fixes that.'},

        {'id': 'rx-quoted', 'type': 'regex',
         'prompt': 'Match the first double-quoted string on a line, without '
                   'swallowing across two of them.',
         'match': ['say "hello" now', '"only one"'],
         'reject': ['no quotes here'],
         'answer': '"[^"]*"',
         'teach': 'The negated class stops at the closing quote. This is the '
                  'general shape of "one delimited thing".'},

        {'id': 'rx-trailing-space', 'type': 'regex',
         'prompt': 'Match lines that end in whitespace, which is the thing '
                   'linters complain about.',
         'match': ['x ', 'hello\t', 'a b  '],
         'reject': ['x', 'hello'],
         'answer': r'\s$',
         'teach': 'Useful in anger: :%s/\\s\\+$// strips them in vim.'},

        {'id': 'rx-case-insensitive', 'type': 'regex',
         'prompt': 'Match error in any capitalisation. The i flag is on for '
                   'this one.',
         'match': ['ERROR', 'error', 'Error: x'],
         'reject': ['warning', 'err'],
         'flags': 'i',
         'answer': 'error',
         'teach': 'Flags are set outside the pattern in most tools: grep -i, '
                  'rg -i, or (?i) inline.'},

        {'id': 'rx-capture-swap', 'type': 'regex',
         'prompt': 'Match a "Surname, Forename" line and capture both names, so '
                   'a substitution could swap them.',
         'match': ['Smith, John', 'Doe, Jane'],
         'reject': ['John Smith', 'Smith,John,Extra'],
         'answer': r'^(\w+), (\w+)$',
         'teach': 'The captures come back as \\1 and \\2 in a sed or vim '
                  'replacement, which is how substitution rearranges rather '
                  'than only deletes.'},

        {'id': 'rx-lookahead', 'type': 'regex',
         'prompt': 'Match ERROR only when it is not followed by " recovered".',
         'match': ['ERROR: disk full', 'ERROR again'],
         'reject': ['ERROR recovered'],
         'answer': 'ERROR(?! recovered)',
         'teach': 'Negative lookahead is the clean way to say "this, but not '
                  'when followed by that". It consumes nothing.'},

        {'id': 'rx-ip-strict', 'type': 'regex',
         'prompt': 'Match an IPv4-shaped address only when it is not part of a '
                   'longer run of dotted numbers.',
         'match': ['10.0.0.1', 'from 8.8.8.8 ok'],
         'reject': ['1.2.3.4.5.6.7', '10.0.0'],
         'answer': r'(?<![\d.])\d{1,3}(?:\.\d{1,3}){3}(?![\d.])',
         'teach': 'A word boundary is not enough here, because a dot is already '
                  'a non-word character, so \\b sits happily in the middle of '
                  '1.2.3.4.5.6.7. Lookaround for "not a digit or a dot" is what '
                  'actually expresses the intent.'},

        {'id': 'rx-lookbehind', 'type': 'regex',
         'prompt': 'Match the value after "user=", without including the label '
                   'itself in the match.',
         'match': ['user=alice', 'log: user=bob here'],
         'reject': ['username=carol', 'user='],
         'answer': r'(?<=\buser=)\w+',
         'teach': 'Nothing inside a lookbehind is part of the match, which is '
                  'what makes extraction clean. Note it must reject '
                  'username=, so the boundary matters.'},

        # tool invocations, so the pattern language lands somewhere real
        {'id': 'rx-cmd-rg', 'type': 'command',
         'answer': 'rg -n "^ERROR"',
         'accepts': ['rg -n ^ERROR'],
         'prompt': 'From your shell: search recursively for lines starting with '
                   'ERROR, showing line numbers.',
         'teach': 'ripgrep is recursive by default and takes perl-ish patterns '
                  'with no flag, which is the main reason to prefer it.'},
        {'id': 'rx-cmd-grep-e', 'type': 'command',
         'answer': 'grep -E "^(ERROR|WARN)" file.log',
         'accepts': ['grep -E ^(ERROR|WARN) file.log'],
         'prompt': 'Grep file.log for lines starting with ERROR or WARN, without escaping the groups.',
         'teach': '-E is extended regex. Without it you would need '
                  '^\\(ERROR\\|WARN\\).'},
        {'id': 'rx-cmd-grep-o', 'type': 'command',
         'answer': 'grep -o "[0-9]*" file.log',
         'prompt': 'From your shell: print only the matching digits from '
                   'file.log rather than the whole line.',
         'teach': '-o turns grep from a locator into an extractor, and pairs '
                  'with sort | uniq -c.'},
        {'id': 'rx-cmd-sed', 'type': 'command',
         'answer': 'sed -E "s/old/new/g" file.txt',
         'prompt': 'Print file.txt with every old replaced by new, without editing the file.',
         'teach': 'Always run it without -i first. It costs a second and it has '
                  'saved everyone who does it.'},
    ],

    # ------------------------------------------------------------------
    # Practice: real substitutions in real nvim, which is one of the
    # module's own stated applications.
    # ------------------------------------------------------------------
    'challenges': [
        {
            'id': 'rx-strip-trailing',
            'title': 'Strip trailing whitespace',
            'goal': 'Use a substitution with a pattern rather than fixing lines '
                    'by hand.',
            'setup': {'kind': 'nvim',
                      'start': ['alpha   ', 'bravo', 'charlie\t\t',
                                'delta  ']},
            'solution': {'keys': ':%s/\\s\\+$//e\r:wq\r'},
            'steps': [
                {'instruction': 'Substitute across the whole file.',
                 'hint': ':%s/ starts it; % means every line'},
                {'instruction': 'Match one or more whitespace characters at the '
                                'end of a line, and replace with nothing.',
                 'hint': r':%s/\s\+$//'},
                {'instruction': 'Save and quit.', 'hint': ':wq'},
            ],
            'free': 'Remove all trailing whitespace using a single substitution, '
                    'then save.',
            'verify': {'kind': 'nvim',
                       'expect': {'lines': ['alpha', 'bravo', 'charlie',
                                            'delta']}},
            'fallback': 'self',
        },
        {
            'id': 'rx-swap-fields',
            'title': 'Swap two fields with captures',
            'goal': 'Rearrange text rather than only deleting it, using capture '
                    'groups in the replacement.',
            'setup': {'kind': 'nvim',
                      'start': ['Smith, John', 'Doe, Jane', 'Khan, Amir']},
            'solution': {'keys': ':%s/^\\(\\w\\+\\), \\(\\w\\+\\)$/\\2 \\1/\r:wq\r'},
            'steps': [
                {'instruction': 'Capture the surname and the forename.',
                 'hint': r'vim needs backslashed groups: \(\w\+\)'},
                {'instruction': 'Put them back in the other order.',
                 'hint': r'the replacement is \2 \1'},
                {'instruction': 'Save and quit.'},
            ],
            'free': 'Turn every "Surname, Forename" line into "Forename '
                    'Surname" with one substitution, then save.',
            'verify': {'kind': 'nvim',
                       'expect': {'lines': ['John Smith', 'Jane Doe',
                                            'Amir Khan']}},
            'fallback': 'self',
        },
        {
            'id': 'rx-extract-ips',
            'title': 'Keep only the lines that matter',
            'goal': 'Delete every line that does not contain an address, using '
                    'a pattern rather than reading them.',
            'setup': {'kind': 'nvim',
                      'start': ['connect from 10.0.0.1 ok',
                                'starting service',
                                'connect from 192.168.1.7 ok',
                                'shutting down',
                                'connect from 8.8.8.8 ok']},
            'solution': {'keys': ':v/\\d\\+\\.\\d\\+\\.\\d\\+\\.\\d\\+/d\r:wq\r'},
            'steps': [
                {'instruction': 'Use the inverse global command, which acts on '
                                'lines that do NOT match.',
                 'hint': ':v/pattern/d  deletes every non-matching line'},
                {'instruction': 'Match four dot-separated groups of digits.',
                 'hint': r'\d\+\.\d\+\.\d\+\.\d\+  and note the escaped dots'},
                {'instruction': 'Save and quit.'},
            ],
            'free': 'Delete every line that does not contain something shaped '
                    'like an IPv4 address, then save.',
            'verify': {'kind': 'nvim',
                       'expect': {'lines': ['connect from 10.0.0.1 ok',
                                            'connect from 192.168.1.7 ok',
                                            'connect from 8.8.8.8 ok']}},
            'fallback': 'self',
        },
        {
            'id': 'rx-very-magic',
            'title': 'Use very magic mode',
            'goal': 'Write a vim pattern that looks like everyone else\'s, by '
                    'turning on \\v.',
            'setup': {'kind': 'nvim',
                      'start': ['ERROR: one', 'INFO: two', 'WARN: three',
                                'DEBUG: four']},
            'solution': {'keys': ':%s/\\v^(ERROR|WARN)/SEVERE/\r:wq\r'},
            'steps': [
                {'instruction': 'Start the pattern with \\v so groups and pipes '
                                'need no backslashes.',
                 'hint': r':%s/\v^(ERROR|WARN)/'},
                {'instruction': 'Replace either severity with SEVERE.',
                 'hint': r':%s/\v^(ERROR|WARN)/SEVERE/'},
                {'instruction': 'Save and quit.'},
            ],
            'free': 'Using \\v, replace ERROR or WARN at the start of a line '
                    'with SEVERE, then save.',
            'verify': {'kind': 'nvim',
                       'expect': {'lines': ['SEVERE: one', 'INFO: two',
                                            'SEVERE: three', 'DEBUG: four']}},
            'fallback': 'self',
        },
    ],

    # ------------------------------------------------------------------
    'quiz': [
        {'id': 'rq-search-vs-match', 'type': 'mcq',
         'prompt': 'Your pattern is cat and it matched concatenate. Why?',
         'answer': 'An unanchored pattern searches, so it means "contains".',
         'distractors': ['The engine defaulted to case-insensitive.',
                         'cat is a reserved word in regex.',
                         'You needed to escape the letters.'],
         'teach': 'This and greediness are the two defaults behind most regex '
                  'surprise. Anchors and \\b are the fixes.'},

        {'id': 'rq-greedy', 'type': 'mcq',
         'prompt': 'On the text `<a> and <b>`, what does `<.*>` match?',
         'answer': 'The whole thing, `<a> and <b>`.',
         'distractors': ['Just `<a>`.', 'Just `<b>`.',
                         'Nothing, because of the spaces.'],
         'teach': 'Greedy quantifiers take as much as possible. `<[^>]*>` says '
                  'what you meant rather than relying on backtracking.'},

        {'id': 'rq-alternation-precedence', 'type': 'mcq',
         'prompt': 'What does `^ERROR|WARN` mean?',
         'answer': 'Starts with ERROR, or contains WARN anywhere.',
         'distractors': ['Starts with either ERROR or WARN.',
                         'Contains both ERROR and WARN.',
                         'It is a syntax error.'],
         'teach': 'Alternation binds loosest of everything, so the anchor '
                  'applies only to the first branch. Group it: ^(ERROR|WARN).'},

        {'id': 'rq-caret', 'type': 'mcq',
         'prompt': 'What is the difference between `^a` and `[^a]`?',
         'answer': 'The first anchors to the start; the second means "not a".',
         'distractors': ['They are equivalent.',
                         'The first is basic regex, the second extended.',
                         'The second only works inside a group.'],
         'teach': 'The same character does two unrelated jobs depending on '
                  'where it sits, which is a genuine wart of the syntax.'},

        {'id': 'rq-dot', 'type': 'mcq',
         'prompt': 'Why does `a.c` fail to match a line break between a and c?',
         'answer': 'Dot excludes newline unless you turn that off.',
         'distractors': ['Dot only matches letters.',
                         'You must escape the dot to match anything.',
                         'Multiline mode is on by default.'],
         'teach': 'This is why a pattern that looks right silently fails across '
                  'lines. The s or DOTALL flag changes it.'},

        {'id': 'rq-dialect', 'type': 'mcq',
         'prompt': 'Why does `grep "colou?r"` not match color?',
         'answer': 'Plain grep is basic regex, where ? must be backslashed.',
         'distractors': ['? is not a regex metacharacter.',
                         'grep needs -i for optional characters.',
                         'The pattern needs anchors.'],
         'teach': 'Reach for grep -E or grep -P and stop fighting backslashes. '
                  'rg needs no flag at all.'},

        {'id': 'rq-d-portability', 'type': 'mcq',
         'prompt': r'Where does \d NOT work?',
         'answer': 'In basic and extended grep, without -P.',
         'distractors': ['In Python.', 'In ripgrep.', 'In grep -P.'],
         'teach': r'[0-9] is the portable answer. \d is perl-ish and needs a '
                  'tool that speaks it.'},

        {'id': 'rq-catastrophic', 'type': 'mcq',
         'prompt': 'Why can `(a+)+$` take effectively forever on a line of 40 '
                   'a-characters?',
         'answer': 'Nested quantifiers make the engine try exponentially many '
                   'ways to split the text.',
         'distractors': ['The line is too long for the engine.',
                         'The $ anchor forces a full-file scan.',
                         'It leaks memory until it is killed.'],
         'teach': 'Catastrophic backtracking. The drills here detect it and '
                  'say so rather than hanging.'},

        {'id': 'rq-when-to-stop', 'type': 'mcq',
         'prompt': 'Which of these is regex genuinely the wrong tool for?',
         'answer': 'Extracting a value from arbitrarily nested JSON.',
         'distractors': ['Finding lines starting with a timestamp.',
                         'Stripping trailing whitespace.',
                         'Pulling IP addresses out of a log.'],
         'teach': 'Regex cannot count nesting. Two greps in a pipeline, or a '
                  'real parser like jq, beat one unreadable pattern.'},
    ],
}
