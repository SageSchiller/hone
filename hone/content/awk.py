"""awk: a small language for columns of text.

awk looks like a command and is a programming language, and it is the tool you
reach for the moment a stream of columns needs more than `cut` and `grep` can
give. Its records are lines and its fields are columns, which is the shape of
`/etc/passwd`, of `ps` output, and of every log file ever written. The whole of
awk is one idea: for every line, if a pattern matches, run an action, and awk
writes the loop for you.

Fully verified, no new adapter. awk reads a file and writes to stdout, so a
challenge is "process this input and write the result", and the sandbox adapter
reads the result back.

regex is a prerequisite: awk patterns are regexes.
"""

MODULE = {
    'id': 'awk',
    'title': 'awk',
    'group': 'Text processing',
    'blurb': 'Fields, patterns and actions, and the report awk writes without a loop.',
    'context': 'You are at a shell, writing the command that would go on the right-hand side of a pipe.',
    'needs': ('awk',),
    'prereqs': ['regex'],
    'adapter': 'sandbox',
    'estimate': '3-4 hours',
    'order': 31,

    'lessons': [
        {
            'id': 'awk-what',
            'title': 'What awk is for',
            'next': 'aj-awk-model',
            'concept': (
                'awk is a small language people mistake for a command, and it '
                'answers one question: given a stream of lines, keep the '
                'interesting ones and reshape them. Its records are lines and '
                'its fields are the columns within a line, which is exactly the '
                'shape of a password file, of process output, and of a log.\n\n'
                'The reason to learn it is the moment you are chaining three '
                '`cut`s and a `grep` and it is still not right. awk does all of '
                'that in one program, and it can do arithmetic and keep state '
                'between lines, which the pipeline cannot. You do not need to '
                'learn it fully: ten percent of awk covers almost everything '
                'anyone actually types.\n\n'
                'The one habit to build from the start is to single-quote the '
                'program. Everything inside an awk program looks like shell '
                'metacharacters, and double quotes let the shell eat `$1` '
                'before awk ever sees it.'
            ),
            'examples': [
                {
                    'label': 'A smarter cut, and then some',
                    'code': ("awk -F: '{print $1}' /etc/passwd\n"
                             '  same answer as  cut -d: -f1  ...\n'
                             '\n'
                             "awk -F: '$3 >= 1000 {print $1}' /etc/passwd\n"
                             '  ... but now with a condition cut cannot express'),
                    'note': 'The moment you need a comparison or a running '
                            'total, the pipeline stops and awk starts.',
                },
            ],
            'misconceptions': [
                'awk is not only for one-liners, but ten percent of it is all '
                'most people ever need, so do not be put off by the manual.',
                'Single-quote the program. In double quotes the shell expands '
                '`$1` before awk runs, and you lose the field reference.',
                'awk is not slow. On a large file it usually beats a pipeline '
                'of three tools doing the same job.',
            ],
            'try_it': [
                'Run `awk -F: \'{print $1}\' /etc/passwd` and confirm it is the '
                'same answer `cut -d: -f1` gives, with room to grow.',
            ],
        },
        {
            'id': 'aj-awk-model',
            'title': 'Pattern, action, and the loop you do not write',
            'next': 'aj-awk-fields',
            'concept': (
                'An awk program is a list of `pattern { action }` pairs, and awk '
                'runs the whole list against every line of input for you. That '
                'implicit loop is the thing to internalise: you never write '
                '`for`, you describe what to do to one line.\n\n'
                'Leave out the pattern and the action runs on every line. Leave '
                'out the action and the default is `{ print }`, which is why '
                '`awk \'/ERROR/\'` behaves exactly like grep.\n\n'
                'A pattern can be a regex between slashes, a comparison, or a '
                'combination. That is already most of what people use awk for: '
                'a smarter grep that can also do arithmetic.'
            ),
            'examples': [
                {
                    'label': 'The shape',
                    'code': ("awk '/ERROR/'              like grep\n"
                             "awk '/ERROR/ {print $2}'   and take a column\n"
                             "awk '{print $1}'           every line\n"
                             "awk '$3 > 100'             a comparison as pattern\n"
                             "awk '$1 == \"GET\" {n++} END {print n}'"),
                    'note': 'The last one counts matching lines and prints the '
                            'total. No loop, no counter initialisation.',
                },
            ],
            'misconceptions': [
                'awk is not line-oriented by accident. Records are configurable '
                'with `RS`, and paragraph mode with `RS=""` is genuinely '
                'useful.',
                'Single-quote the program. Everything in it is shell '
                'metacharacters, and double quotes will let `$1` be eaten '
                'before awk sees it.',
                'Uninitialised variables are 0 and "", which is why `n++` works '
                'without declaring n. That is a feature, not a bug to be '
                'defended against.',
            ],
            'try_it': [
                "Run `awk '/bash/' /etc/passwd` and then `awk '/bash/ {print "
                "$1}' /etc/passwd` on a colon-separated file, and work out why "
                'the second prints whole lines.',
            ],
        },
        {
            'id': 'aj-awk-fields',
            'title': 'Fields, separators and the built-in variables',
            'next': 'aj-awk-accumulate',
            'concept': (
                '`$1` is the first field, `$2` the second, and `$0` is the whole '
                'record. `NF` is the number of fields, so `$NF` is the last one '
                'and `$(NF-1)` the one before it, which is how you handle lines '
                'whose length varies.\n\n'
                '`NR` is the record number, so `NR == 1` is the header line and '
                '`NR > 1` skips it.\n\n'
                'The field separator is whitespace by default, and crucially '
                '**runs of whitespace count as one**, which is exactly the thing '
                '`cut` cannot do and the usual reason to reach for awk. `-F:` '
                'sets it to a colon, `-F\'\\t\'` to a tab, and `-F` takes a '
                'regex, so `-F\'[,;]\'` splits on either.'
            ),
            'examples': [
                {
                    'label': 'Fields',
                    'code': ("awk '{print $1, $NF}'        first and last\n"
                             "awk '{print NF}'             how many fields\n"
                             "awk 'NR > 1'                 skip a header\n"
                             "awk -F: '{print $1}'         colon separated\n"
                             "awk -F'[,;]' '{print $2}'    a regex separator\n"
                             "awk '{$1=\"\"; print}'         drop the first field"),
                    'note': 'A comma between print arguments inserts OFS, a '
                            'space by default. No comma concatenates them.',
                },
                {
                    'label': 'The thing cut cannot do',
                    'code': ('ps aux output has runs of spaces:\n'
                             '  root  1234   0.0  0.1 ...\n'
                             '\n'
                             "cut -d' ' -f2   ->  empty, because of the run\n"
                             "awk '{print $2}' ->  1234"),
                    'note': 'This alone justifies learning awk.',
                },
            ],
            'misconceptions': [
                'Assigning to a field rebuilds `$0` using OFS, which is why '
                '`$1=""` leaves a leading separator. Sometimes that surprises '
                'people.',
                '`-F` takes a regex, but a single character is taken literally, '
                'so `-F.` already splits on dots with no escaping needed. '
                'Only a multi-character `-F` is treated as a regex.',
                '`$NF` is the last field, `NF` is how many there are. Dropping '
                'the dollar is a very common typo.',
            ],
            'try_it': [
                "Run `ps aux | awk '{print $2, $11}'` and then try the same "
                'with `cut`.',
            ],
        },
        {
            'id': 'aj-awk-accumulate',
            'title': 'BEGIN, END, and counting things',
            'next': 'aj-awk-real',
            'concept': (
                '`BEGIN { }` runs once before any input and `END { }` runs once '
                'after all of it. Between them, awk stops being a filter and '
                'becomes a small program that summarises.\n\n'
                'This is where awk earns its keep. Sum a column, count by key, '
                'find a maximum, compute an average: all of them are a variable '
                'incremented in the body and printed in END.\n\n'
                'Associative arrays make counting by key trivial. `count[$1]++` '
                'creates the entry on first use, and `for (k in count)` in END '
                'walks it. That single idiom replaces `sort | uniq -c` and is '
                'faster on large files because nothing has to be sorted.'
            ),
            'examples': [
                {
                    'label': 'Summarising',
                    'code': ("awk '{s += $3} END {print s}'         sum a column\n"
                             "awk '{s += $3} END {print s/NR}'      average\n"
                             "awk '$3 > m {m = $3} END {print m}'   maximum\n"
                             "awk 'END {print NR}'                  count lines"),
                    'note': 'NR in END is the total number of records, which is '
                            'the shortest `wc -l` you will ever write.',
                },
                {
                    'label': 'Counting by key',
                    'code': ("awk '{count[$1]++} END {for (k in count)\n"
                             '        print count[k], k}\' access.log\n'
                             '\n'
                             'replaces:\n'
                             "  awk '{print $1}' | sort | uniq -c"),
                    'note': 'Pipe it to `sort -rn` if you want it ranked. awk '
                            'does not guarantee any order for `for (k in ...)`.',
                },
            ],
            'misconceptions': [
                'BEGIN runs before the first line is read, so `$1` is empty '
                'there. Set `FS` in BEGIN, not the data.',
                '`for (k in arr)` has no defined order. If order matters, sort '
                'the output afterwards.',
                'awk arrays are always associative, so the index is a string '
                'even when it looks like a number.',
            ],
            'try_it': [
                "Count the shells in /etc/passwd with `awk -F: '{c[$7]++} END "
                "{for (s in c) print c[s], s}' /etc/passwd`.",
            ],
        },
        {
            'id': 'aj-awk-real',
            'title': 'The one-liners that pay for the language',
            'concept': (
                'A handful of awk programs cover most of what anyone actually '
                'types, and knowing them by shape means you can adapt rather '
                'than look up.\n\n'
                'Filter by a column. Sum or count. Print a range of lines. '
                'Reformat a line. Deduplicate without sorting, which is the one '
                'people are most surprised by: `!seen[$0]++` keeps the first '
                'occurrence of each line and preserves the original order, '
                'which `sort -u` cannot do.\n\n'
                'The last one deserves explaining because it looks like magic. '
                '`seen[$0]++` is zero the first time a line appears, so `!` '
                'makes it true, and the default action prints. Every later '
                'time it is non-zero, so `!` is false and nothing prints.'
            ),
            'examples': [
                {
                    'label': 'Worth knowing by heart',
                    'code': ("awk '!seen[$0]++'          dedupe, keep order\n"
                             "awk 'NR==10,NR==20'        a line range\n"
                             "awk 'NF'                    drop blank lines\n"
                             "awk '{print NR\": \"$0}'      number the lines\n"
                             "awk 'length > 80'           long lines\n"
                             "awk -F: '$3 >= 1000'        real users only"),
                    'note': "`awk 'NF'` works because a blank line has zero "
                            'fields, which is false, and the default action '
                            'prints everything else.',
                },
            ],
            'misconceptions': [
                '`!seen[$0]++` is not sorting. It keeps first occurrences in '
                'the original order, which is often what you wanted and what '
                '`sort -u` destroys.',
                'awk is fast. On a large file it will usually beat a pipeline of '
                'three other tools doing the same job.',
            ],
            'try_it': [
                "Take a file with duplicate lines and compare `sort -u` with "
                "`awk '!seen[$0]++'`. Look at the order.",
            ],
        },
    ],

    'drills': [
        {'id': 'aj-cmd-col', 'type': 'command', 'answer': "awk '{print $1}'",
         'prompt': 'Print the first whitespace-separated field of every line.',
         'teach': '$0 is the whole line and $1 onward are the fields. awk '
                  'splits on runs of whitespace by default, so leading spaces '
                  'do not produce an empty first field.'},
        {'id': 'aj-cmd-last', 'type': 'command', 'answer': "awk '{print $NF}'",
         'prompt': 'Print the last field of every line, however many there are.',
         'teach': '$NF is the last field; NF without the dollar is how many '
                  'there are.'},
        {'id': 'aj-cmd-fs', 'type': 'command', 'answer': "awk -F: '{print $1}'",
         'prompt': 'Print the first colon-separated field.',
         'teach': '-F sets the input separator and it takes a regex, so '
                  "-F'[:,]' splits on either character."},
        {'id': 'aj-cmd-fs-regex', 'type': 'command',
         'answer': "awk -F'[,;]' '{print $2}'",
         'prompt': 'Print the second field, splitting on either a comma or a '
                   'semicolon.',
         'teach': '-F takes a regex, which is why regex is a prerequisite here.'},
        {'id': 'aj-cmd-grep', 'type': 'command', 'answer': "awk '/ERROR/'",
         'prompt': 'Print lines containing ERROR, using awk as a grep.',
         'teach': 'A pattern with no action defaults to { print }.'},
        {'id': 'aj-cmd-cmp', 'type': 'command', 'answer': "awk '$3 > 100'",
         'prompt': 'Print lines whose third field is greater than 100.',
         'teach': 'A pattern with no action means print. The comparison is '
                  'numeric because the field looks like a number; quote it '
                  'and you get a string compare instead.'},
        {'id': 'aj-cmd-skip-header', 'type': 'command', 'answer': "awk 'NR > 1'",
         'prompt': 'Print every line except the first.',
         'teach': 'NR counts records across all input. FNR restarts at each '
                  'file, which is the one you want when passing several files '
                  'at once.'},
        {'id': 'aj-cmd-count', 'type': 'command', 'answer': "awk 'END {print NR}'",
         'prompt': 'Count the lines in the input, using awk.',
         'teach': 'END runs once after the last record, and NR still holds '
                  'the final count when it does.'},
        {'id': 'aj-cmd-sum', 'type': 'command',
         'answer': "awk '{s += $3} END {print s}'",
         'prompt': 'Sum the third column and print the total.',
         'teach': 'Variables need no declaration and start at zero, which is '
                  'why s works without being set first.'},
        {'id': 'aj-cmd-avg', 'type': 'command',
         'answer': "awk '{s += $3} END {print s/NR}'",
         'prompt': 'Print the average of the third column.',
         'teach': 'NR in END is every record read, so this averages over all '
                  'of them, including any header you meant to skip.'},
        {'id': 'aj-cmd-max', 'type': 'command',
         'answer': "awk '$3 > m {m = $3} END {print m}'",
         'prompt': 'Print the largest value in the third column.',
         'teach': 'm starts at zero, so this gets a column of negative '
                  'numbers wrong. Seed it in a NR==1 block when that matters.'},
        {'id': 'aj-cmd-bykey', 'type': 'command',
         'answer': "awk '{c[$1]++} END {for (k in c) print c[k], k}'",
         'prompt': 'Count how many times each value appears in the first '
                   'column, and print the counts.',
         'teach': 'Replaces sort | uniq -c, and is faster because nothing needs '
                  'sorting.'},
        {'id': 'aj-cmd-dedupe', 'type': 'command', 'answer': "awk '!seen[$0]++'",
         'prompt': 'Remove duplicate lines while keeping the original order.',
         'teach': 'The counter is zero the first time, so ! is true and the '
                  'default action prints. Every later time it is non-zero.'},
        {'id': 'aj-cmd-nonblank', 'type': 'command', 'answer': "awk 'NF'",
         'prompt': 'Drop blank lines.',
         'teach': 'A blank line has zero fields, which is false.'},
        {'id': 'aj-cmd-range', 'type': 'command', 'answer': "awk 'NR==10,NR==20'",
         'prompt': 'Print lines 10 through 20.',
         'teach': 'A comma between two patterns is a range: it switches on at '
                  'the first match and off at the second.'},
        {'id': 'aj-cmd-number', 'type': 'command',
         'answer': "awk '{print NR\": \"$0}'",
         'prompt': 'Prefix every line with its line number and a colon.',
         'teach': 'Adjacent expressions are concatenated in awk. There is no '
                  'operator for it, which is why the spacing looks wrong '
                  'until you know.'},
        {'id': 'aj-cmd-long', 'type': 'command', 'answer': "awk 'length > 80'",
         'prompt': 'Print lines longer than 80 characters.',
         'teach': 'length with no argument is the length of $0. It is a '
                  'pattern, so the default action prints.'},
    ],

    'challenges': [
        {
            'id': 'aj-awk-report',
            'title': 'Summarise a log with awk',
            'goal': 'Use fields, a comparison and END to turn a log into two '
                    'numbers.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'access.log': ('10.0.0.1 GET 200 512\n'
                               '10.0.0.2 GET 404 128\n'
                               '10.0.0.1 POST 500 2048\n'
                               '10.0.0.3 GET 200 256\n'
                               '10.0.0.1 GET 200 1024\n'),
            }},
            'solution': {'shell': "awk '{s += $4} END {print s}' access.log > total.txt && "
                                  "awk '$3 >= 400' access.log > errors.txt"},
            'steps': [
                {'instruction': 'Sum the fourth column into total.txt.',
                 'hint': "awk '{s += $4} END {print s}' access.log > total.txt"},
                {'instruction': 'Write every line whose status is 400 or more '
                                'into errors.txt.',
                 'hint': "awk '$3 >= 400' access.log > errors.txt"},
            ],
            'free': 'Write the total of column four into total.txt, and every '
                    'line with a status of 400 or more into errors.txt.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_equals': {'total.txt': '3968'},
                'file_contains': {'errors.txt': ['404', '500']},
                'file_lacks': {'errors.txt': '200'}}},
            'fallback': 'self',
        },
        {
            'id': 'aj-awk-bykey',
            'title': 'Count by key without sorting',
            'goal': 'Use an associative array and END, which replaces a whole '
                    'pipeline.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'access.log': ('10.0.0.1 GET\n10.0.0.2 GET\n10.0.0.1 POST\n'
                               '10.0.0.3 GET\n10.0.0.1 GET\n10.0.0.2 POST\n'),
            }},
            'solution': {'shell': "awk '{c[$1]++} END {for (k in c) print c[k], k}' "
                                  "access.log | sort -rn > ranked.txt"},
            'steps': [
                {'instruction': 'Count occurrences of the first field using an '
                                'array.', 'hint': "awk '{c[$1]++}'"},
                {'instruction': 'Print each count and key in END.',
                 'hint': 'END {for (k in c) print c[k], k}'},
                {'instruction': 'Sort by count, highest first, into ranked.txt.',
                 'hint': 'awk does not guarantee an order, so pipe to sort -rn'},
            ],
            'free': 'Write ranked.txt containing each client address and how '
                    'often it appears, most frequent first.',
            'verify': {'kind': 'sandbox', 'expect': {
                'exists': ['ranked.txt'],
                'file_contains': {'ranked.txt': ['3 10.0.0.1', '2 10.0.0.2',
                                                 '1 10.0.0.3']}}},
            'fallback': 'self',
        },
        {'id': 'aj-awk-column-total',
         'title': 'Total a column and report it',
         'goal': 'awk keeps state between lines. Sum a column and print '
                 'the total once, at the end.',
         'setup': {'kind': 'sandbox',
                   'tree': {'sales.txt': 'north 120\n'
                                         'south 80\n'
                                         'east 200\n'
                                         'west 50\n'}},
         'solution': {'shell': "awk '{s += $2} END {print s}' sales.txt > "
                               'total.txt'},
         'steps': [{'instruction': 'The second field is the number. Add '
                                   'each one to a running variable.',
                    'hint': "'{s += $2}'. You do not have to declare s"},
                   {'instruction': 'Print the running total once, after '
                                   'the last line.',
                    'hint': 'END {print s} runs after the input is '
                            'exhausted'},
                   {'instruction': 'Redirect the answer into total.txt.',
                    'hint': '> total.txt'}],
         'free': 'Put the sum of the second column of sales.txt into '
                 'total.txt.',
         'verify': {'kind': 'sandbox',
                    'expect': {'file_contains': {'total.txt': '450'}}},
         'fallback': 'self'},
        {'id': 'aj-awk-filter-format',
         'title': 'Filter rows, then reshape them',
         'goal': 'Pattern and action are two halves of the same thing. '
                 'Select the rows you want and print them in a new shape.',
         'setup': {'kind': 'sandbox',
                   'tree': {'servers.txt': 'web01 up 120\n'
                                           'web02 down 0\n'
                                           'db01 up 340\n'
                                           'db02 down 0\n'}},
         'solution': {'shell': 'awk \'$2 == "up" {print $1": "$3}\' '
                               'servers.txt > up.txt'},
         'steps': [{'instruction': 'Keep only the lines whose second field '
                                   'is up.',
                    'hint': '\'$2 == "up"\' as the pattern'},
                   {'instruction': 'For those, print the name, a colon and '
                                   'a space, then the number.',
                    'hint': 'adjacent expressions concatenate: $1": "$3'},
                   {'instruction': 'Send the result to up.txt.',
                    'hint': '> up.txt'}],
         'free': 'Write "name: number" into up.txt for every server that '
                 'is up.',
         'verify': {'kind': 'sandbox',
                    'expect': {'file_contains': {'up.txt': ['web01: 120',
                                                            'db01: 340']},
                               'file_lacks': {'up.txt': 'web02'}}},
         'fallback': 'self'},
        {'id': 'aj-awk-fieldsep',
         'title': 'A file that is not split on spaces',
         'goal': 'Real data uses colons, commas and tabs. Tell awk what '
                 'the separator is instead of fighting it.',
         'setup': {'kind': 'sandbox',
                   'tree': {'users.csv': 'sage,admin,active\n'
                                         'lee,user,disabled\n'
                                         'kim,admin,active\n'}},
         'solution': {'shell': 'awk -F, \'$2 == "admin" {print $1}\' '
                               'users.csv > admins.txt'},
         'steps': [{'instruction': 'Tell awk the fields are separated by '
                                   'commas.',
                    'hint': '-F, before the program'},
                   {'instruction': 'Keep the rows whose second field is '
                                   'admin.',
                    'hint': '\'$2 == "admin"\''},
                   {'instruction': 'Print only the name, into admins.txt.',
                    'hint': '{print $1}'}],
         'free': 'Put the names of the admins from users.csv into '
                 'admins.txt, one per line.',
         'verify': {'kind': 'sandbox',
                    'expect': {'file_contains': {'admins.txt': ['sage',
                                                                'kim']},
                               'file_lacks': {'admins.txt': 'lee'}}},
         'fallback': 'self'},
        {'id': 'aj-awk-beginend',
         'title': 'BEGIN and END for what is not per-line',
         'goal': 'A header, a running total, and a footer. That is the whole '
                 'shape of an awk report.',
         'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
             'sales.txt': 'north 120\nsouth 80\neast 200\nwest 45\n'}},
         'solution': {'shell':
             'awk \'BEGIN { print "region amount"; total = 0 } '
             '{ total += $2; print $1, $2 } '
             'END { print "total", total; print "rows", NR }\' '
             'sales.txt > report.txt'},
         'steps': [{'instruction': 'In BEGIN, print a header line and '
                                   'initialise a total.',
                    'hint': 'BEGIN { print "region amount"; total = 0 }'},
                   {'instruction': 'For each line, add the second field to '
                                   'the total and print the row.'},
                   {'instruction': 'In END, print the total and the number of '
                                   'rows, using NR.',
                    'hint': 'END { print "total", total; print "rows", NR }'}],
         'free': 'Produce report.txt with a header, every row, then a total '
                 'line and a row count.',
         'verify': {'kind': 'sandbox', 'expect': {
             'file_contains': {'report.txt': ['region amount', 'north 120',
                                              'total 445', 'rows 4']}}},
         'fallback': 'self'},
        {'id': 'aj-awk-nf',
         'title': 'Use NF when you do not know the width',
         'goal': 'NF is the field count and $NF is the last field. That pair '
                 'handles ragged input a fixed column number cannot.',
         'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
             'ragged.txt': 'alpha 1 ok\n'
                           'bravo 2 3 4 fail\n'
                           'charlie 9 ok\n'
                           'delta 1 2 3 4 5 fail\n'}},
         'solution': {'shell':
             'awk \'{ print $1, NF, $NF }\' ragged.txt > shape.txt && '
             'awk \'$NF == "fail" { print $1 }\' ragged.txt > failed.txt && '
             'awk \'NF > 3 { print $1 }\' ragged.txt > wide.txt'},
         'steps': [{'instruction': 'Print the first field, the field count '
                                   'and the last field of every row into '
                                   'shape.txt.',
                    'hint': 'awk with print $1, NF, $NF'},
                   {'instruction': 'Print the name of every row whose last '
                                   'field is fail, into failed.txt.',
                    'hint': 'the pattern is $NF == "fail"'},
                   {'instruction': 'Print the name of every row with more '
                                   'than three fields, into wide.txt.'}],
         'free': 'Produce shape.txt with name, field count and last field per '
                 'row, failed.txt naming the failing rows, and wide.txt '
                 'naming the rows with more than three fields.',
         'verify': {'kind': 'sandbox', 'expect': {
             'file_contains': {'shape.txt': ['alpha 3 ok', 'delta 7 fail'],
                               'failed.txt': ['bravo', 'delta'],
                               'wide.txt': ['bravo', 'delta']},
             'file_lacks': {'failed.txt': 'alpha', 'wide.txt': 'charlie'}}},
         'fallback': 'self'},
    ],

    'quiz': [
        {'id': 'ajq-loop', 'type': 'mcq',
         'prompt': "Why does `awk '{print $1}'` need no loop?",
         'answer': 'awk runs the program once per input record automatically.',
         'distractors': ['print iterates over all lines itself.',
                         'The braces are a loop.',
                         'It only prints the first line.'],
         'teach': 'The implicit loop is the thing to internalise. You describe '
                  'what to do to one record.'},
        {'id': 'ajq-default-action', 'type': 'mcq',
         'prompt': "What does `awk '/ERROR/'` do?",
         'answer': 'Prints lines containing ERROR, like grep.',
         'distractors': ['Nothing; there is no action.',
                         'Prints the word ERROR once per match.',
                         'Counts the matches.'],
         'teach': 'A pattern with no action defaults to { print }, and an '
                  'action with no pattern runs on every line.'},
        {'id': 'ajq-cut', 'type': 'mcq',
         'prompt': 'Why does `cut -d\' \' -f2` fail on `ps aux` output where '
                   'awk succeeds?',
         'answer': 'cut treats each space as a separator; awk collapses runs of '
                   'whitespace.',
         'distractors': ['cut cannot read from a pipe.',
                         'ps uses tabs, not spaces.',
                         'cut counts fields from zero.'],
         'teach': 'This alone justifies learning awk.'},
        {'id': 'ajq-nf', 'type': 'mcq',
         'prompt': 'What is the difference between NF and $NF?',
         'answer': 'NF is how many fields there are; $NF is the last field.',
         'distractors': ['They are the same.',
                         'NF is the last field; $NF is its value.',
                         '$NF only works inside END.'],
         'teach': 'Dropping the dollar is a very common typo and produces a '
                  'number where you wanted text.'},
        {'id': 'ajq-dedupe', 'type': 'mcq',
         'prompt': "How does `awk '!seen[$0]++'` differ from `sort -u`?",
         'answer': 'It keeps first occurrences in the original order.',
         'distractors': ['It is the same, just faster.',
                         'It keeps the last occurrence instead.',
                         'It only works on sorted input.'],
         'teach': 'sort -u destroys the order. Often the order was the point.'},
    ],
}
