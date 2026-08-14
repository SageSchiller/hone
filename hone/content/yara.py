"""YARA: describing what a file looks like, precisely enough to be useful.

YARA is a pattern language, and the right way to meet it is as a sibling of
regex rather than as a malware tool. regex describes what a line of text looks
like. YARA describes what a *file* looks like: some strings, at some offsets,
in some combination, with some conditions about size and type. The trainer
already teaches one pattern language properly, so this one can lean on it and
spend its time on what is genuinely different.

What is genuinely different is the **condition**. In regex, matching is the
whole statement. In YARA the strings are only candidates, and the condition is
a small boolean language over them: any of, all of, counts, offsets, file size,
and the magic at the start. That separation is the thing to learn, and it is
also where every bad rule comes from.

**The recurring lesson is over-matching**, which is exactly the lesson the
regex module teaches with negatives. A rule that fires on every file with the
word "http" in it is not a detection, it is an alarm you will turn off in a
week. So the drills here are written the same way the regex drills are: the
rule has to match the samples that should match and miss the ones that should
not.

**Verification.** The `yaralab` adapter, which is the sandbox plus a check
that `yara` is actually installed. Where it is, you write rules and run them
against real sample files and the trainer reads the matches. Where it is not,
the module degrades to self-marked and says why, per D18, rather than promising
a check it cannot perform.
"""

MODULE = {
    'id': 'yara',
    'title': 'YARA rules',
    'group': 'Security',
    'blurb': 'Strings, conditions, hex patterns and modifiers, and not over-matching.',
    'context': 'You are writing YARA rules against sample files you can run them on.',
    'needs': ['yara'],
    'prereqs': ['regex', 'file'],
    'adapter': 'yaralab',
    'estimate': '3-4 hours',
    'order': 84,

    'lessons': [
        {
            'id': 'ya-shape',
            'title': 'The shape of a rule',
            'concept':
                'Every rule has the same three part shape, and two of the '
                'parts are optional.\n\n'
                'A rule opens with the keyword rule and a name, which must be '
                'unique in the file and is what gets printed when it fires. '
                'Inside are up to three sections: meta for information about '
                'the rule, strings for the things to look for, and condition '
                'for when the rule counts as matched.\n\n'
                'Only the condition is required. A rule with a condition of '
                'true matches every file, which is a legitimate thing to '
                'write once while you are testing your command line.\n\n'
                'Strings are named with a dollar sign and defined as text, '
                'hex or regular expressions. The names are yours: $a and $b '
                'are conventional and $suspicious_url is better in a rule '
                'anyone else will read.\n\n'
                'The condition refers to those names, and here is the part '
                'that trips people coming from regex: **a bare string name in '
                'a condition is a boolean meaning "this was found somewhere". '
                'Prefixed with a hash it is a count, and with an at sign it '
                'is an offset.** Those three sigils are most of the language.\n\n'
                'meta is free-form key and value, and it is where the author, '
                'the date, the reference and the hash of the sample belong. '
                'It affects nothing at match time and it is what makes a rule '
                'maintainable a year later.',
            'examples': [
                {'label': 'A complete, minimal rule',
                 'code': 'rule finds_a_url\n'
                         '{\n'
                         '    strings:\n'
                         '        $u = "http://"\n'
                         '    condition:\n'
                         '        $u\n'
                         '}',
                 'note': 'The bare $u means "found somewhere in the file". '
                         'This particular rule is also far too broad.'},
                {'label': 'With the parts that make it maintainable',
                 'code': 'rule example_two\n'
                         '{\n'
                         '    meta:\n'
                         '        author = "you"\n'
                         '        date = "2026-08-12"\n'
                         '        reference = "sample sha256 ..."\n'
                         '    strings:\n'
                         '        $a = "one"\n'
                         '        $b = "two"\n'
                         '    condition:\n'
                         '        all of them\n'
                         '}',
                 'note': 'meta changes nothing at match time and is the '
                         'difference between a rule you can maintain and one '
                         'you delete.'},
                {'label': 'Run it',
                 'code': 'yara rules.yar sample.bin',
                 'note': 'Rules first, then the target. Prints the rule name '
                         'and the file for each match.'},
            ],
            'misconceptions': [
                'The strings section does not decide whether the rule '
                'matches. The condition does, and it may ignore strings you '
                'defined.',
                'A rule with no strings section is valid, as long as the '
                'condition does not refer to any.',
                'Rule names are identifiers, not text. They cannot contain '
                'spaces and they are what appears in the output.',
            ],
            'try_it': [
                'Write a rule whose condition is just true and run it against '
                'three files.',
                'Write a two string rule and try it with all of them and then '
                'any of them.',
            ],
            'next': 'ya-strings',
        },
        {
            'id': 'ya-strings',
            'title': 'Three kinds of string, and their modifiers',
            'concept':
                'YARA has three ways to describe what to look for, and '
                'choosing the right one is most of writing a good rule.\n\n'
                '**Text strings** are in double quotes and are exact by '
                'default. Their modifiers are where the power is. `nocase` '
                'makes them case insensitive. `wide` matches the UTF-16 form, '
                'which is essential for Windows binaries and is the single '
                'most commonly forgotten modifier. `ascii` is the default and '
                'is written explicitly when you also want wide. `fullword` '
                'requires non-alphanumeric boundaries, which stops "admin" '
                'matching "badminton". `xor` matches the string XORed with '
                'every single byte key, which finds trivially obfuscated '
                'content.\n\n'
                '**Hex strings** are in braces and describe bytes. They take '
                'wildcards: `??` is any byte, `?A` is any byte whose low '
                'nibble is A, `[4-6]` is a jump of four to six bytes, and '
                '`( 01 02 | 03 04 )` is an alternation. This is how you match '
                'code patterns and file structures rather than text.\n\n'
                '**Regular expressions** are in slashes and are exactly the '
                'pattern language the regex module teaches, with the same '
                'greedy and lazy semantics. They are the most expensive of '
                'the three and the one to reach for last, because a regex '
                'over a large file is far slower than a literal string.\n\n'
                'The performance ordering matters at scale: literals are '
                'fast, hex with wildcards is slower, and regex is slowest. A '
                'rule that runs across a fleet is a rule whose cost is real.',
            'examples': [
                {'label': 'The modifier everyone forgets',
                 'code': '$s = "CreateRemoteThread" ascii wide',
                 'note': 'Windows binaries carry UTF-16 text. Without wide, '
                         'half your strings never match.'},
                {'label': 'Word boundaries, so admin is not badminton',
                 'code': '$w = "admin" fullword nocase',
                 'note': 'fullword requires non-alphanumeric neighbours. It '
                         'removes an enormous class of false positive.'},
                {'label': 'Bytes, with room to move',
                 'code': '$h = { 4D 5A ?? ?? [4-8] 50 45 00 00 }',
                 'note': 'MZ, two unknown bytes, a jump of four to eight, '
                         'then PE. This is a structure, not text.'},
                {'label': 'Trivially obfuscated text',
                 'code': '$x = "powershell" xor nocase',
                 'note': 'Matches the string XORed with any single byte, '
                         'which catches the laziest obfuscation there is.'},
                {'label': 'A regex, used sparingly',
                 'code': '$r = /https?:\\/\\/[a-z0-9.-]{4,}\\.onion/ nocase',
                 'note': 'Same language as the regex module. The slowest '
                         'option, so make the condition cheap around it.'},
            ],
            'misconceptions': [
                'Text strings are not case insensitive by default, and they '
                'do not match UTF-16 by default. nocase and wide are both '
                'opt-in.',
                'A hex wildcard ?? is one byte, not any number of bytes. The '
                'jump syntax [n-m] is what skips a variable run.',
                'A regex string is not cheaper than a text string because it '
                'is shorter. It is much more expensive.',
            ],
            'try_it': [
                'Write the same string twice, with and without wide, and run '
                'both against a UTF-16 file.',
                'Write a hex pattern with a jump and confirm it matches two '
                'files with different spacing.',
            ],
            'next': 'ya-condition',
        },
        {
            'id': 'ya-condition',
            'title': 'The condition is the rule',
            'concept':
                'The condition is a small boolean expression language, and '
                'learning its vocabulary is what turns a list of strings into '
                'a detection.\n\n'
                'The basics are what you expect: and, or, not, parentheses, '
                'and comparisons. A bare `$a` is true when the string was '
                'found anywhere.\n\n'
                'The set operators are what you will use constantly. '
                '`any of them`, `all of them`, `2 of them`, and the wildcard '
                'form `any of ($a*)` which selects every string whose name '
                'starts with a. `2 of ($str*)` is the everyday shape of a '
                'decent rule: several indicators, needing more than one, '
                'which is exactly what keeps it from over-matching.\n\n'
                '`#a` is the number of times $a was found, so `#a > 3` '
                'requires repetition. `@a[1]` is the offset of the first '
                'match and `!a[1]` is its length, which is how you express '
                '"these two strings appear near each other".\n\n'
                '`filesize` is available and is the cheapest condition there '
                'is, so putting `filesize < 500KB` first short-circuits the '
                'expensive work on every file that cannot match.\n\n'
                '`uint16(0)` and friends read integers at an offset, and '
                '`uint16(0) == 0x5A4D` is the idiomatic "this is a Windows '
                'executable" check. It is fast, it is precise, and it belongs '
                'at the front of nearly every rule about executables.',
            'examples': [
                {'label': 'The everyday shape',
                 'code': 'condition:\n'
                         '    uint16(0) == 0x5A4D and filesize < 2MB\n'
                         '    and 2 of ($s*)',
                 'note': 'Cheap checks first, then require more than one '
                         'indicator. This is what a decent rule looks like.'},
                {'label': 'Counting rather than finding',
                 'code': 'condition:\n    #url > 5',
                 'note': 'Repetition is often the signal, where a single '
                         'occurrence is noise.'},
                {'label': 'Proximity, using offsets',
                 'code': 'condition:\n    $a and $b and @b[1] - @a[1] < 100',
                 'note': 'Both strings, within a hundred bytes of each other. '
                         'Much stronger than both anywhere.'},
                {'label': 'Anchored to the start or end',
                 'code': 'condition:\n'
                         '    $header at 0 and $footer at filesize - 8',
                 'note': '"at" fixes an exact offset, and filesize arithmetic '
                         'reaches the trailer.'},
                {'label': 'Sets by name prefix',
                 'code': 'condition:\n'
                         '    all of ($required*) and any of ($optional*)',
                 'note': 'Naming your strings in groups makes the condition '
                         'read like the intent.'},
            ],
            'misconceptions': [
                '"any of them" is the weakest possible condition and is '
                'almost never the right one for a real rule.',
                '@a is not the offset by itself. It is an array, so the first '
                'match is @a[1], and YARA indexes from one.',
                'Putting filesize last does not save anything. Cheap '
                'conditions belong first so the expensive ones short circuit.',
            ],
            'try_it': [
                'Take a rule with any of them and tighten it to 2 of them, '
                'then check what stops matching.',
                'Write a rule using uint16(0) to require an MZ header and '
                'confirm it skips text files.',
            ],
            'next': 'ya-overmatch',
        },
        {
            'id': 'ya-overmatch',
            'title': 'Over-matching, and how to know before you deploy',
            'concept':
                'A rule that matches everything is worse than no rule. It '
                'costs the same to run, it produces alerts nobody reads, and '
                'it teaches the people around it to ignore the tool. This is '
                'the same lesson the regex module teaches with negative test '
                'cases, and it lands harder here because the corpus is every '
                'file on a machine.\n\n'
                'The failure modes are predictable. **Strings that are too '
                'common**: any English word, any common API name, any URL '
                'scheme. **Conditions that are too loose**: any of them, on '
                'three generic strings. **No type or size gate**: a rule '
                'about a Windows binary that also examines every log file on '
                'the disk.\n\n'
                'The discipline is a goodware corpus. Run every new rule '
                'against a directory of known-clean files, ideally a few '
                'thousand from a real system, and count the hits. A rule that '
                'fires there is not finished. This is precisely the '
                'must-not-match half of a regex drill, at file scale.\n\n'
                'The other discipline is specificity of intent. Write down, '
                'in meta, what the rule is supposed to catch. If the strings '
                'do not obviously serve that sentence, they are decoration '
                'and they are costing you precision.\n\n'
                'And prefer to be narrow and miss things. A rule that catches '
                'one family reliably is deployable. A rule that catches four '
                'families and half a fleet is not.',
            'examples': [
                {'label': 'Test against known good, every time',
                 'code': 'yara -r new-rule.yar /usr/bin | wc -l',
                 'note': 'Any output at all is a problem. This takes seconds '
                         'and saves weeks.'},
                {'label': 'Too broad, and it looks reasonable',
                 'code': 'strings:\n'
                         '    $a = "cmd.exe"\n'
                         '    $b = "http"\n'
                         'condition:\n'
                         '    any of them',
                 'note': 'Matches a large share of Windows and most log '
                         'files. Two generic strings and the weakest '
                         'condition.'},
                {'label': 'The same intent, made deployable',
                 'code': 'condition:\n'
                         '    uint16(0) == 0x5A4D and filesize < 1MB\n'
                         '    and all of them and #b < 20',
                 'note': 'Executables only, small ones, both strings, and not '
                         'the ones full of URLs.'},
                {'label': 'Count matches per rule while tuning',
                 'code': 'yara -c rules.yar samples/',
                 'note': '-c prints counts rather than lines, which is what '
                         'you want while iterating.'},
            ],
            'misconceptions': [
                'A rule matching the sample it was written from is not '
                'evidence that it works. That is the easy half.',
                'Adding more strings does not tighten a rule if the condition '
                'is still any of them.',
                'False positives are not a tuning detail. They are the reason '
                'detection programmes lose credibility.',
            ],
            'try_it': [
                'Run a rule you wrote against /usr/bin and count the hits.',
                'Take an over-broad rule and tighten it until the goodware '
                'count is zero without losing the sample.',
            ],
            'next': 'ya-modules',
        },
        {
            'id': 'ya-modules',
            'title': 'Modules: pe, math, hash and the rest',
            'concept':
                'YARA ships modules that expose structured facts about a '
                'file, so a rule can talk about what the file *is* rather '
                'than only what bytes it contains. Import them at the top of '
                'the file.\n\n'
                'The **pe** module is the most used. It parses Windows '
                'executables and gives you `pe.entry_point`, `pe.sections`, '
                '`pe.imports("kernel32.dll", "CreateRemoteThread")`, '
                '`pe.number_of_sections`, the timestamp, and the imphash. '
                'Matching on an import is enormously more precise than '
                'matching on the string of a function name, because the '
                'string can appear anywhere and the import table means the '
                'binary actually calls it.\n\n'
                'The **math** module computes over the file, and '
                '`math.entropy(0, filesize)` is the one people reach for: '
                'high entropy means packed or encrypted, and a section with '
                'much higher entropy than its neighbours is a classic '
                'packing signal.\n\n'
                '**hash** lets a condition compute md5 or sha256 of a range, '
                'which is how you write a rule about a specific embedded '
                'blob rather than a whole file.\n\n'
                '**elf** does for Linux binaries roughly what pe does for '
                'Windows, and **dotnet**, **magic** and **cuckoo** cover '
                'their own niches.\n\n'
                'Modules are also the honest way to keep rules fast: a pe '
                'check is a parse, not a scan, so it is a cheap gate.',
            'examples': [
                {'label': 'Import at the top, before any rule',
                 'code': 'import "pe"\nimport "math"',
                 'note': 'Once per file. Rules below can then use them.'},
                {'label': 'It really calls this function',
                 'code': 'condition:\n'
                         '    pe.imports("kernel32.dll", '
                         '"CreateRemoteThread")',
                 'note': 'The import table, not a string search. Far more '
                         'precise and far harder to trip accidentally.'},
                {'label': 'Probably packed',
                 'code': 'condition:\n'
                         '    math.entropy(0, filesize) > 7.5',
                 'note': 'Near maximum entropy means compressed or '
                         'encrypted. On its own it is a hint, not a verdict.'},
                {'label': 'A specific embedded blob',
                 'code': 'condition:\n'
                         '    hash.sha256(0x100, 0x200) == "abc123..."',
                 'note': 'Hash a range rather than the file, which survives '
                         'the rest of the file changing.'},
                {'label': 'Structural oddities',
                 'code': 'condition:\n'
                         '    pe.number_of_sections > 8 or '
                         'pe.timestamp > 1900000000',
                 'note': 'Impossible timestamps and unusual section counts '
                         'are cheap signals.'},
            ],
            'misconceptions': [
                'Matching the string "CreateRemoteThread" is not the same as '
                'the binary importing it. The string can be anywhere, '
                'including in your own rule file.',
                'High entropy does not mean malicious. Every installer, '
                'archive and encrypted document looks the same way.',
                'The pe module does not fail loudly on a non-PE file. Its '
                'fields are simply undefined, so gate on the header.',
            ],
            'try_it': [
                'Write a rule using pe.imports and run it against a Windows '
                'binary you have.',
                'Compute the entropy of a compressed file and an ordinary '
                'text file and compare.',
            ],
            'next': 'ya-running',
        },
        {
            'id': 'ya-running',
            'title': 'Running rules, and reading what came back',
            'concept':
                'The command line is small and the useful flags are worth '
                'knowing by heart.\n\n'
                '`yara rules.yar target` is the base: rules first, then a '
                'file or a directory. `-r` recurses. `-s` prints the matching '
                'strings and their offsets, which is what turns a match into '
                'something you can investigate. `-c` counts instead of '
                'listing, which is what you want while tuning. `-m` prints '
                'the meta, so a rule with a good reference field explains '
                'itself in the output.\n\n'
                '`-f` is fast matching mode, `-w` suppresses warnings, and '
                '`-p` sets the number of threads. `-d` defines an external '
                'variable, which is how one rule file adapts to different '
                'contexts without editing.\n\n'
                'Two flags matter for not shooting yourself in the foot on a '
                'real system. `-a` sets a timeout in seconds, because a bad '
                'regex against a huge file genuinely can run for a very long '
                'time. And `--max-strings-per-rule` guards against a '
                'generated rule file that is far larger than you expected.\n\n'
                '`yarac` compiles rules to a binary form, which is worth it '
                'when the same large ruleset runs repeatedly, and the '
                'compiled form is version specific so it is not a '
                'distribution format.\n\n'
                'Exit status reports whether the scan ran, not whether '
                'anything matched: unlike grep, yara exits zero either way, so '
                'decide from the printed output or the -c count.',
            'examples': [
                {'label': 'Scan a tree',
                 'code': 'yara -r rules.yar /home/user/Downloads',
                 'note': 'Rules first, then the target. -r for directories.'},
                {'label': 'Show what actually matched, and where',
                 'code': 'yara -s rules.yar sample.bin',
                 'note': 'Offsets and the matching bytes. The difference '
                         'between a match and a finding.'},
                {'label': 'Tuning loop',
                 'code': 'yara -c rules.yar goodware/',
                 'note': 'Counts per rule. Any non-zero number here is work '
                         'still to do.'},
                {'label': 'Do not let a rule run forever',
                 'code': 'yara -a 60 -r rules.yar /',
                 'note': 'A timeout in seconds. A pathological regex over a '
                         'large file is a real hazard.'},
                {'label': 'Compile a large ruleset once',
                 'code': 'yarac rules.yar rules.compiled',
                 'note': 'Faster to load repeatedly, and version specific, so '
                         'never ship the compiled form.'},
            ],
            'misconceptions': [
                'The argument order is not interchangeable. Rules come first '
                'and the target second.',
                'A match printed without -s tells you the rule fired and '
                'nothing about why. -s is what makes it investigable.',
                'Compiled rules are not portable between YARA versions, so '
                'they are a cache and not a format.',
            ],
            'try_it': [
                'Run a rule with and without -s and compare how useful the '
                'output is.',
                'Time a scan of a large directory and then repeat it with '
                'compiled rules.',
            ],
            'next': 'ya-practice',
        },
        {
            'id': 'ya-practice',
            'title': 'Where rules come from, and where they go',
            'concept':
                'A rule is usually written from a sample, and the process is '
                'the same triage routine as the file module, with one extra '
                'step at the end.\n\n'
                'Identify the file and hash it. Pull its strings, with a '
                'sensible minimum and with the UTF-16 pass. Look at the '
                'structure with the pe module or with a hex dump. Pick the '
                'strings that are **specific to this thing and unlikely to be '
                'anywhere else**, which usually means an unusual '
                'concatenation, a mutex name, a hardcoded path, a peculiar '
                'user agent, rather than an API name or a common word. Write '
                'the condition to require several of them behind a cheap '
                'gate. Then test against goodware.\n\n'
                'Where rules go is worth knowing because YARA is embedded '
                'nearly everywhere: in ClamAV via conversion, in many EDR '
                'products, in VirusTotal retrohunt, in memory scanners, in '
                'Volatility through a plugin, and in incident response '
                'scripts that sweep a fleet. The rule you write is portable '
                'in a way that most detection content is not.\n\n'
                'Public rulesets are worth reading rather than only running. '
                'The YARA-Rules repository, Florian Roth\'s signature-base '
                'and the Neo23x0 collections are large bodies of worked '
                'examples, and reading how an experienced author gates and '
                'combines strings teaches more quickly than writing in '
                'isolation.',
            'examples': [
                {'label': 'The strings pass, both encodings',
                 'code': 'strings -n 8 sample.bin > a.txt\n'
                         'strings -e l -n 8 sample.bin > w.txt',
                 'note': 'The UTF-16 pass is where Windows samples keep their '
                         'interesting text.'},
                {'label': 'What is unusual, not what is common',
                 'code': 'comm -13 <(sort common-strings.txt) <(sort sample-strings.txt)',
                 'note': 'Subtracting a list of strings that appear in '
                         'goodware leaves the candidates worth using.'},
                {'label': 'Test both directions before you deploy',
                 'code': 'yara rules.yar sample.bin && yara -c rules.yar '
                         'goodware/',
                 'note': 'Must match the sample, must not match the corpus. '
                         'Exactly a regex drill, at file scale.'},
            ],
            'misconceptions': [
                'A rule written from one sample usually catches only that '
                'sample. Generalising deliberately, and testing that you '
                'did, is the actual work.',
                'Public rules are not all good. Read them before running '
                'them across a fleet, especially for cost.',
                'YARA is not an antivirus. It matches patterns you give it '
                'and has no opinion about maliciousness.',
            ],
            'try_it': [
                'Write a rule from a file you have, then test it against '
                '/usr/bin and tighten until it is clean.',
                'Read three rules from a public ruleset and identify the '
                'cheap gate in each.',
            ],
            'next': None,
        },
    ],

    'drills': [
        {'id': 'yad-run', 'type': 'command',
         'prompt': 'Run the rules in rules.yar against sample.bin.',
         'answer': 'yara rules.yar sample.bin',
         'teach': 'Rules first, target second. The order is not '
                  'interchangeable.'},
        {'id': 'yad-recurse', 'type': 'command',
         'prompt': 'Run rules.yar recursively over the directory samples.',
         'answer': 'yara -r rules.yar samples',
         'teach': 'Without -r a directory argument scans nothing useful.'},
        {'id': 'yad-strings-out', 'type': 'command',
         'prompt': 'Run rules.yar on sample.bin showing which strings matched.',
         'answer': 'yara -s rules.yar sample.bin',
         'teach': '-s prints offsets and matched bytes, which is the '
                  'difference between a match and a finding.'},
        {'id': 'yad-count', 'type': 'command',
         'prompt': 'Count matches per rule for rules.yar over the goodware directory.',
         'answer': 'yara -c -r rules.yar goodware',
         'teach': 'The tuning loop. Any non-zero count against known-clean '
                  'files is work still to do.'},
        {'id': 'yad-meta', 'type': 'command',
         'prompt': 'Run rules.yar on sample.bin printing each rule meta section.',
         'answer': 'yara -m rules.yar sample.bin',
         'teach': 'A rule with a good reference field explains itself in the '
                  'output, which is why meta is worth writing.'},
        {'id': 'yad-timeout', 'type': 'command',
         'prompt': 'Scan the whole filesystem with rules.yar, timing out after 60 seconds.',
         'answer': 'yara -a 60 -r rules.yar /',
         'teach': 'A pathological regex against a huge file is a real hazard, '
                  'and -a is the guard.'},
        {'id': 'yad-threads', 'type': 'command',
         'prompt': 'Scan samples with rules.yar using eight threads.',
         'answer': 'yara -p 8 -r rules.yar samples',
         'teach': 'Worth setting on a big scan, and irrelevant on one file.'},
        {'id': 'yad-define', 'type': 'command',
         'prompt': 'Run rules.yar defining the external variable env as prod.',
         'answer': 'yara -d env=prod rules.yar sample.bin',
         'teach': 'External variables let one rule file adapt to different '
                  'contexts without being edited.'},
        {'id': 'yad-compile', 'type': 'command',
         'prompt': 'Compile rules.yar into rules.compiled.',
         'answer': 'yarac rules.yar rules.compiled',
         'teach': 'Faster to load repeatedly. Version specific, so it is a '
                  'cache rather than a distribution format.'},
        {'id': 'yad-run-compiled', 'type': 'command',
         'prompt': 'Run the compiled ruleset rules.compiled against sample.bin.',
         'answer': 'yara -C rules.compiled sample.bin',
         'teach': '-C says the rules argument is already compiled.'},
        {'id': 'yad-text-nocase', 'type': 'command',
         'prompt': 'Write the string definition for a case insensitive "admin".',
         'answer': '$a = "admin" nocase',
         'teach': 'Text strings are exact by default. nocase is opt-in, like '
                  'every modifier.'},
        {'id': 'yad-text-wide', 'type': 'command',
         'prompt': 'Write a string matching "svchost" in both ASCII and UTF-16.',
         'answer': '$a = "svchost" ascii wide',
         'teach': 'The most commonly forgotten modifier. Windows binaries '
                  'carry UTF-16 text.'},
        {'id': 'yad-text-fullword', 'type': 'command',
         'prompt': 'Write a string matching "admin" only as a whole word.',
         'answer': '$a = "admin" fullword',
         'teach': 'fullword requires non-alphanumeric neighbours, so admin no '
                  'longer matches badminton.'},
        {'id': 'yad-text-xor', 'type': 'command',
         'prompt': 'Write a string matching "powershell" XORed with any single byte.',
         'answer': '$a = "powershell" xor',
         'teach': 'Catches the laziest obfuscation there is, at the cost of '
                  'trying all 256 single-byte keys.'},
        {'id': 'yad-hex-wild', 'type': 'command',
         'prompt': 'Write a hex string of 4D 5A, any two bytes, then 50 45.',
         'answer': '$h = { 4D 5A ?? ?? 50 45 }',
         'teach': '?? is exactly one unknown byte. It does not skip a '
                  'variable run.'},
        {'id': 'yad-hex-jump', 'type': 'command',
         'prompt': 'Write a hex string of 4D 5A, a gap of 4 to 8 bytes, then 50 45.',
         'answer': '$h = { 4D 5A [4-8] 50 45 }',
         'teach': 'The jump syntax is what handles variable spacing between '
                  'two known byte sequences.'},
        {'id': 'yad-cond-all', 'type': 'command',
         'prompt': 'Write a condition requiring every defined string.',
         'answer': 'all of them',
         'teach': 'Stronger than any of them, and often still not strong '
                  'enough without a type or size gate.'},
        {'id': 'yad-cond-2of', 'type': 'command',
         'prompt': 'Write a condition requiring any two of the strings named $s...',
         'answer': '2 of ($s*)',
         'teach': 'The everyday shape of a decent rule: several indicators, '
                  'more than one required.'},
        {'id': 'yad-cond-count', 'type': 'command',
         'prompt': 'Write a condition requiring $url to appear more than five times.',
         'answer': '#url > 5',
         'teach': 'The hash sigil is a count. Repetition is often the signal '
                  'where one occurrence is noise.'},
        {'id': 'yad-cond-offset', 'type': 'command',
         'prompt': 'Write a condition requiring $b within 100 bytes after $a.',
         'answer': '@b[1] - @a[1] < 100',
         'teach': 'The at sigil is an offset array, indexed from one. '
                  'Proximity is much stronger than co-occurrence.'},
        {'id': 'yad-cond-at', 'type': 'command',
         'prompt': 'Write a condition requiring $header at the very start of the file.',
         'answer': '$header at 0',
         'teach': '"at" fixes an exact offset, where a bare string name means '
                  'anywhere.'},
        {'id': 'yad-cond-mz', 'type': 'command',
         'prompt': 'Write a condition testing for the MZ signature at offset zero.',
         'answer': 'uint16(0) == 0x5A4D',
         'teach': 'Byte order makes it 5A4D rather than 4D5A. The idiomatic '
                  'and very cheap "is this a PE" gate.'},
        {'id': 'yad-cond-filesize', 'type': 'command',
         'prompt': 'Write a condition limiting the rule to files under 2 megabytes.',
         'answer': 'filesize < 2MB',
         'teach': 'The cheapest condition there is, so it belongs first and '
                  'short circuits the expensive work.'},
        {'id': 'yad-import-pe', 'type': 'command',
         'prompt': 'Write the line that makes the pe module available.',
         'answer': 'import "pe"',
         'teach': 'At the top of the file, before any rule, and once per '
                  'file.'},
        {'id': 'yad-pe-imports', 'type': 'command',
         'prompt': 'Write a condition requiring an import of CreateRemoteThread '
                   'from kernel32.dll.',
         'answer': 'pe.imports("kernel32.dll", "CreateRemoteThread")',
         'teach': 'The import table, not a string search. Far more precise, '
                  'and it cannot be tripped by the name appearing in data.'},
        {'id': 'yad-math-entropy', 'type': 'command',
         'prompt': 'Write a condition matching whole-file entropy above 7.5.',
         'answer': 'math.entropy(0, filesize) > 7.5',
         'teach': 'Near maximum entropy means packed or encrypted, which '
                  'describes every installer as well as every packer.'},
        {'id': 'yad-pe-sections', 'type': 'command',
         'prompt': 'Write a condition matching a PE with more than eight '
                   'sections.',
         'answer': 'pe.number_of_sections > 8',
         'teach': 'A structural oddity: unusual section counts and impossible '
                  'timestamps are cheap signals the pe module exposes without '
                  'a scan.'},
        {'id': 'yad-goodware', 'type': 'command',
         'prompt': 'Count how many files in /usr/bin your new rule matches.',
         'answer': 'yara -c -r new-rule.yar /usr/bin',
         'teach': 'The must-not-match half. Any output is a rule that is not '
                  'finished.'},
    ],

    'challenges': [
        {
            'id': 'yac-first-rule',
            'title': 'Match one file and not the others',
            'goal': 'Three sample files, one target. Write a rule specific '
                    'enough to hit only the one you meant.',
            'setup': {'kind': 'yaralab', 'shell': 'bash', 'tree': {
                'samples/target.txt':
                    'config loaded\nmutex name: hone-lab-mutex-7f3a\n'
                    'connecting to updates.example.invalid\n',
                'samples/other1.txt':
                    'config loaded\nordinary application log\n'
                    'connecting to updates.example.invalid\n',
                'samples/other2.txt':
                    'config loaded\nnothing interesting here at all\n',
            }},
            'solution': {'shell':
                'printf \'rule finds_target\\n{\\n    meta:\\n'
                '        author = "student"\\n    strings:\\n'
                '        $m = "hone-lab-mutex-7f3a"\\n    condition:\\n'
                '        $m\\n}\\n\' > rule.yar && '
                'yara -r rule.yar samples > matches.txt'},
            'steps': [
                {'instruction': 'Read all three samples and find what is true '
                                'of target.txt and of neither other file.',
                 'hint': 'head -5 samples/*'},
                {'instruction': 'Write rule.yar with one string and a '
                                'condition naming it.',
                 'hint': 'strings:\n    $m = "hone-lab-mutex-7f3a"\n'
                         'condition:\n    $m'},
                {'instruction': 'Run it recursively over samples and save the '
                                'output to matches.txt. Exactly one line.',
                 'hint': 'yara -r rule.yar samples > matches.txt'},
            ],
            'free': 'Produce rule.yar and matches.txt, where the rule matches '
                    'samples/target.txt and neither of the others.',
            'verify': {'kind': 'yaralab', 'expect': {
                'file_contains': {'rule.yar': ['rule', 'condition'],
                                  'matches.txt': 'target.txt'},
                'file_lacks': {'matches.txt': ['other1', 'other2']}}},
            'fallback': 'self',
        },
        {
            'id': 'yac-tighten',
            'title': 'Fix a rule that matches everything',
            'goal': 'Take an over-broad rule, find out how broad, and tighten '
                    'it until it is deployable.',
            'setup': {'kind': 'yaralab', 'shell': 'bash', 'tree': {
                'broad.yar':
                    'rule too_broad\n{\n    strings:\n'
                    '        $a = "config"\n        $b = "http"\n'
                    '    condition:\n        any of them\n}\n',
                'samples/bad.txt':
                    'config loaded\nhttp://updates.example.invalid/payload\n'
                    'mutex: hone-lab-7f3a\n',
                'goodware/app1.log': 'config loaded at boot\n',
                'goodware/app2.log': 'fetching http://example.com/index\n',
                'goodware/app3.log': 'config reloaded, http retry\n',
            }},
            'solution': {'shell':
                'yara -r broad.yar goodware > before.txt; '
                'printf \'rule tightened\\n{\\n    strings:\\n'
                '        $a = "config"\\n        $b = "http"\\n'
                '        $m = "hone-lab-7f3a"\\n    condition:\\n'
                '        $m and 2 of ($a, $b)\\n}\\n\' > tight.yar && '
                'yara -r tight.yar goodware > after.txt; '
                'yara -r tight.yar samples > still-matches.txt; true'},
            'steps': [
                {'instruction': 'Count how many known-clean files broad.yar '
                                'matches, into before.txt.',
                 'hint': 'yara -r broad.yar goodware > before.txt'},
                {'instruction': 'Write tight.yar: keep the intent, add a '
                                'string that is specific to the sample, and '
                                'require more than one thing.',
                 'hint': 'condition:\n    $m and 2 of ($a, $b)'},
                {'instruction': 'Count the goodware matches again into '
                                'after.txt. It should be zero.',
                 'hint': 'yara -r tight.yar goodware > after.txt'},
                {'instruction': 'Confirm the tightened rule still catches the '
                                'sample, into still-matches.txt.'},
            ],
            'free': 'Produce before.txt and after.txt showing the goodware '
                    'match count falling to zero, and still-matches.txt '
                    'proving the tightened rule still finds the sample.',
            'verify': {'kind': 'yaralab', 'expect': {
                'is_file': ['tight.yar', 'before.txt', 'after.txt'],
                'file_contains': {'still-matches.txt': 'bad.txt'},
                'file_lacks': {'after.txt': 'app'}}},
            'fallback': 'self',
        },
        {
            'id': 'yac-hex',
            'title': 'Match a structure rather than text',
            'goal': 'Write a hex pattern with a wildcard and a jump, and '
                    'prove it matches two files whose spacing differs.',
            'setup': {'kind': 'yaralab', 'shell': 'bash', 'tree': {
                'gen.sh': {'content':
                    '#!/bin/bash\n'
                    'printf "MZ\\x90\\x00\\x00\\x00\\x00PE\\x00\\x00rest" '
                    '> a.bin\n'
                    'printf "MZ\\x90\\x00\\x00\\x00\\x00\\x00\\x00PE\\x00\\x00" '
                    '> b.bin\n'
                    'printf "ELF not a pe file at all" > c.bin\n',
                    'mode': '755'},
            }},
            'solution': {'shell':
                './gen.sh && '
                'printf \'rule pe_shape\\n{\\n    strings:\\n'
                '        $h = { 4D 5A ?? [4-8] 50 45 00 00 }\\n'
                '    condition:\\n        $h at 0\\n}\\n\' > hex.yar && '
                'mkdir -p bins && mv a.bin b.bin c.bin bins/ && '
                'yara hex.yar bins > hexmatch.txt; true'},
            'steps': [
                {'instruction': 'Run ./gen.sh to create three binary files '
                                'with different spacing.',
                 'hint': './gen.sh'},
                {'instruction': 'Write hex.yar matching 4D 5A, one wildcard '
                                'byte, a jump, then 50 45 00 00, anchored at '
                                'offset zero.',
                 'hint': '$h = { 4D 5A ?? [4-8] 50 45 00 00 }'},
                {'instruction': 'Put the three binaries in a directory and '
                                'scan that, into hexmatch.txt. Two should '
                                'match and one should not.',
                 'hint': 'mkdir bins && mv *.bin bins/ && yara hex.yar bins'},
                {'instruction': 'Note why you scanned a directory: yara takes '
                                'any number of RULE files and exactly one '
                                'target, so `yara hex.yar a.bin b.bin` would '
                                'read a.bin as a second rule file and fail on '
                                'a syntax error.'},
            ],
            'free': 'Produce hex.yar with a wildcard and a jump, and '
                    'hexmatch.txt showing it matched a.bin and b.bin but not '
                    'c.bin.',
            'verify': {'kind': 'yaralab', 'expect': {
                'file_contains': {'hex.yar': ['4D 5A', '['],
                                  'hexmatch.txt': ['a.bin', 'b.bin']},
                'file_lacks': {'hexmatch.txt': 'c.bin'}}},
            'fallback': 'self',
        },
        {
            'id': 'yac-condition',
            'title': 'Put the cheap gate first',
            'goal': 'Write a rule whose condition is ordered for cost: size '
                    'and type before strings.',
            'setup': {'kind': 'yaralab', 'shell': 'bash', 'tree': {
                'samples/small.txt': 'alpha beta gamma delta\n',
                'samples/also.txt': 'alpha beta\n',
                'big.sh': {'content':
                    '#!/bin/bash\n'
                    'mkdir -p samples\n'
                    'for i in $(seq 1 4000); do echo "alpha beta gamma delta"; '
                    'done > samples/large.txt\n',
                    'mode': '755'},
            }},
            'solution': {'shell':
                './big.sh && '
                'printf \'rule cheap_first\\n{\\n    strings:\\n'
                '        $a = "alpha"\\n        $b = "beta"\\n'
                '        $c = "gamma"\\n    condition:\\n'
                '        filesize < 1KB and all of them\\n}\\n\' '
                '> gated.yar && '
                'yara -r gated.yar samples > gated-matches.txt; true'},
            'steps': [
                {'instruction': 'Run ./big.sh to add a large file to samples.',
                 'hint': './big.sh'},
                {'instruction': 'Write gated.yar with three strings, and a '
                                'condition that requires all of them but only '
                                'for files under 1KB.',
                 'hint': 'condition:\n    filesize < 1KB and all of them'},
                {'instruction': 'Run it over samples into gated-matches.txt. '
                                'The large file should be excluded even '
                                'though it contains every string.'},
            ],
            'free': 'Produce gated.yar whose condition puts filesize before '
                    'the strings, and gated-matches.txt showing the large '
                    'file excluded.',
            'verify': {'kind': 'yaralab', 'expect': {
                'file_contains': {'gated.yar': 'filesize',
                                  'gated-matches.txt': 'small.txt'},
                'file_lacks': {'gated-matches.txt': 'large.txt'}}},
            'fallback': 'self',
        },
        {
            'id': 'yac-count-proximity',
            'title': 'Require repetition and closeness',
            'goal': 'Use the count and offset sigils, which are the two parts '
                    'of the condition language people never reach for.',
            'setup': {'kind': 'yaralab', 'shell': 'bash', 'tree': {
                'samples/many.txt':
                    'http://a\nhttp://b\nhttp://c\nhttp://d\n'
                    'http://e\nhttp://f\nbeacon\n',
                'samples/few.txt': 'http://a\nbeacon\n',
            }},
            'solution': {'shell':
                'printf \'rule many_urls\\n{\\n    strings:\\n'
                '        $u = "http://"\\n    condition:\\n'
                '        #u > 5\\n}\\n\' > count.yar && '
                'yara -r count.yar samples > count-matches.txt; true'},
            'steps': [
                {'instruction': 'Read both samples. They contain the same '
                                'strings, in different quantities.'},
                {'instruction': 'Write count.yar whose condition requires the '
                                'URL string more than five times.',
                 'hint': 'condition:\n    #u > 5'},
                {'instruction': 'Run it into count-matches.txt. Only the '
                                'file with many URLs should appear.'},
            ],
            'free': 'Produce count.yar using the count sigil, and '
                    'count-matches.txt showing only the sample with more than '
                    'five URLs.',
            'verify': {'kind': 'yaralab', 'expect': {
                'file_contains': {'count.yar': '#u',
                                  'count-matches.txt': 'many.txt'},
                'file_lacks': {'count-matches.txt': 'few.txt'}}},
            'fallback': 'self',
        },
        {
            'id': 'yac-real-corpus',
            'title': 'Test a rule against a real machine',
            'goal': 'The samples were three files. Run your rules against a '
                    'real corpus and find out what they actually cost.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'Write a rule from a file on your own machine '
                                'that you can identify: an installer, an '
                                'archive, anything with distinctive strings.'},
                {'instruction': 'Run it against /usr/bin and count the '
                                'matches.',
                 'hint': 'yara -c -r yours.yar /usr/bin'},
                {'instruction': 'Tighten until that count is zero while the '
                                'original file still matches.'},
                {'instruction': 'Time a scan of a large directory with and '
                                'without a filesize gate at the front of the '
                                'condition.'},
                {'instruction': 'Read three rules from a public ruleset and '
                                'name the cheap gate in each.'},
            ],
            'free': 'On your own machine: write a rule from a real file, get '
                    'it to zero matches against a goodware corpus without '
                    'losing the sample, and measure what a cheap gate saves.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
    ],

    'quiz': [
        {'id': 'yaq-required', 'type': 'mcq',
         'prompt': 'Which section must a YARA rule have?',
         'answer': 'condition.',
         'distractors': ['strings.', 'meta.', 'All three.'],
         'teach': 'A rule with condition: true and nothing else is valid, and '
                  'is a useful way to test your command line.'},
        {'id': 'yaq-sigils', 'type': 'mcq',
         'prompt': 'In a condition, what is the difference between $a, #a and '
                   '@a?',
         'answer': 'Found or not, how many times, and at what offsets.',
         'distractors': ['ASCII, hex and regex forms of the same string.',
                         'The string, its length, and its encoding.',
                         'Local, global and external scope.'],
         'teach': 'Three sigils and most of the condition language is in '
                  'them. @a is an array indexed from one.'},
        {'id': 'yaq-wide', 'type': 'mcq',
         'prompt': 'Your rule has correct strings but never fires on Windows '
                   'binaries. What is the likely cause?',
         'answer': 'The text is UTF-16 and the rule lacks the wide modifier.',
         'distractors': ['The strings need the xor modifier.',
                         'The condition needs any of them rather than all of '
                         'them.',
                         'Windows binaries are compressed, so strings never '
                         'match.'],
         'teach': 'ascii wide covers both. This is the most commonly '
                  'forgotten modifier in the language.'},
        {'id': 'yaq-fullword', 'type': 'mcq',
         'prompt': 'What does fullword do to the string "admin"?',
         'answer': 'Requires non-alphanumeric characters on both sides, so '
                   'badminton no longer matches.',
         'distractors': ['Makes the match case insensitive.',
                         'Requires the string to be the whole file.',
                         'Matches only when the word appears at a line '
                         'start.'],
         'teach': 'It removes an enormous class of accidental match for very '
                  'little cost.'},
        {'id': 'yaq-hexjump', 'type': 'mcq',
         'prompt': 'In a hex string, what is the difference between ?? and '
                   '[4-8]?',
         'answer': 'One unknown byte, against a gap of four to eight bytes.',
         'distractors': ['A wildcard nibble against a wildcard byte.',
                         'A single byte against a repeated byte.',
                         'An optional byte against a required range.'],
         'teach': '?? is exactly one byte. The jump syntax is what handles '
                  'variable spacing.'},
        {'id': 'yaq-mz', 'type': 'mcq',
         'prompt': 'Why is the PE check written uint16(0) == 0x5A4D rather '
                   'than 0x4D5A?',
         'answer': 'uint16 reads little-endian, so the bytes 4D 5A read as '
                   '0x5A4D.',
         'distractors': ['0x4D5A is the ELF magic, not the PE one.',
                         'YARA requires hex constants in ascending order.',
                         'The MZ signature is stored reversed in the file.'],
         'teach': 'Byte order catches everyone once. The bytes on disk really '
                  'are 4D 5A.'},
        {'id': 'yaq-order', 'type': 'mcq',
         'prompt': 'Why put filesize and uint16 checks before the string '
                   'conditions?',
         'answer': 'They are far cheaper, and they short circuit the '
                   'expensive scanning.',
         'distractors': ['YARA requires numeric conditions before string '
                         'ones.',
                         'It makes the rule match more files.',
                         'String conditions cannot be evaluated first.'],
         'teach': 'A parse and a size lookup cost almost nothing. A scan '
                  'costs real time on every file.'},
        {'id': 'yaq-imports', 'type': 'mcq',
         'prompt': 'Why is pe.imports() better than a string match on the '
                   'function name?',
         'answer': 'It proves the binary actually calls the function, rather '
                   'than merely containing the text.',
         'distractors': ['It is case insensitive by default.',
                         'It works on non-PE files as well.',
                         'It is the only way to see functions in a packed '
                         'binary.'],
         'teach': 'The string can appear in data, in a resource, or in your '
                  'own rule file. The import table cannot.'},
        {'id': 'yaq-entropy', 'type': 'mcq',
         'prompt': 'A file has entropy of 7.9. What does that establish?',
         'answer': 'It is compressed or encrypted, which describes installers '
                   'as much as packers.',
         'distractors': ['It is packed malware.',
                         'It contains random data with no structure.',
                         'It is a false positive in the math module.'],
         'teach': 'Entropy is a hint that pairs with other signals. On its '
                  'own it flags every archive on the disk.'},
        {'id': 'yaq-goodware', 'type': 'mcq',
         'prompt': 'You wrote a rule and it matches your sample. What is the '
                   'next step before deploying it?',
         'answer': 'Run it against a corpus of known-clean files and require '
                   'zero matches.',
         'distractors': ['Compile it with yarac for performance.',
                         'Add more strings to make it more thorough.',
                         'Submit it to a public ruleset for review.'],
         'teach': 'Matching the sample is the easy half. The must-not-match '
                  'half is the same discipline the regex drills use.'},
    ],
}
