"""awk and jq: two small languages, one job, different data shapes.

Taught together on purpose. Both look like utilities and are actually
languages; both take a stream, apply a filter to each piece, and emit
something; and both are the tool you reach for when `cut` and `grep` stop being
enough. The difference is the shape of the data, and putting them side by side
makes each one clearer than teaching either alone would.

Fully verified, with no new adapter. Both binaries are ordinary programs that
read a file and write to stdout, so a challenge is "process this input and
write the result", and the sandbox adapter already reads the result back.

regex is a prerequisite. awk patterns are regexes, and `test` in jq takes one.
"""

MODULE = {
    'id': 'awkjq',
    'title': 'awk and jq',
    'group': 'Text processing',
    'blurb': 'Filtering columns and filtering JSON, with the same shape of mind.',
    'context': 'You are at a shell, writing the command that would go on the right-hand side of a pipe.',
    'needs': ('awk', 'jq'),
    'prereqs': ['regex'],
    'adapter': 'sandbox',
    'estimate': '5-7 hours',
    'order': 31,

    'lessons': [
        {
            'id': 'aj-two',
            'title': 'Why these two together',
            'next': 'aj-awk-model',
            'concept': (
                'Both are small languages that people mistake for commands, and '
                'both answer the same question: given a stream of records, keep '
                'the interesting ones and reshape them.\n\n'
                'awk\'s records are LINES and its fields are columns, which is '
                'the shape of `/etc/passwd`, of `ps` output, and of every log '
                'file ever written. jq\'s records are JSON VALUES and its fields '
                'are keys, which is the shape of every modern API and most '
                'structured logs.\n\n'
                'The reason to learn them at the same time is that the mental '
                'move is identical. You write a filter, it runs once per '
                'record, and what it emits becomes the output. Once that clicks '
                'in one of them the other is mostly syntax.'
            ),
            'examples': [
                {
                    'label': 'The same question, two shapes',
                    'code': ('columns:\n'
                             "  awk '$3 > 100 {print $1}' access.log\n"
                             '\n'
                             'JSON:\n'
                             "  jq '.[] | select(.size > 100) | .host' access.json\n"
                             '\n'
                             'both: keep some records, emit one field'),
                    'note': 'Read both out loud and they are the same sentence.',
                },
            ],
            'misconceptions': [
                'Neither is a replacement for the other. Feeding JSON to awk '
                'works right up until a value contains a space or a brace.',
                'Both are worth reaching for earlier than people do. The moment '
                'you are chaining three cuts and a grep, one of these is '
                'shorter and clearer.',
                'Neither needs to be learned fully. Ten percent of awk and ten '
                'percent of jq covers almost everything anyone actually types.',
            ],
            'try_it': [
                'Run `awk -F: \'{print $1}\' /etc/passwd` and notice it is the '
                'same answer `cut -d: -f1` gives, with room to grow.',
            ],
        },
        {
            'id': 'aj-awk-model',
            'title': 'awk: pattern, action, and the loop you do not write',
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
                'so `-F.` splits on any character and `-F\'\\.\'` splits on '
                'dots.',
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
            'next': 'aj-jq-model',
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
        {
            'id': 'aj-jq-model',
            'title': 'jq: a pipeline of filters',
            'next': 'aj-jq-select',
            'concept': (
                'jq looks like a JSON path selector and is a functional '
                'language. Every jq program is a FILTER: it takes one input, '
                'produces zero or more outputs, and `|` connects them exactly '
                'like a shell pipe.\n\n'
                '`.` is the identity filter, which is why `jq .` pretty-prints. '
                '`.name` extracts a key. `.[]` takes an array and produces its '
                'elements **as separate outputs**, which is the single most '
                'important idea in jq and the one that makes the rest make '
                'sense.\n\n'
                'That last point is worth dwelling on. `.[]` does not give you '
                'an array of things; it gives you several things. Everything '
                'downstream then runs once per thing, which is exactly awk\'s '
                'implicit loop wearing different clothes.'
            ),
            'examples': [
                {
                    'label': 'Filters and pipes',
                    'code': ('jq .                    pretty-print\n'
                             'jq .name                one key\n'
                             'jq .user.email          nested\n'
                             'jq \'.items[]\'          each element, separately\n'
                             "jq '.items[] | .id'     and take a key from each\n"
                             'jq \'.items | length\'   how many'),
                    'note': 'Quote the program in single quotes. It is full of '
                            'characters the shell wants.',
                },
                {
                    'label': 'Streams versus arrays',
                    'code': ('.items      ->  [ {..}, {..} ]     one output\n'
                             '.items[]    ->  {..}\n'
                             '                {..}               two outputs\n'
                             '\n'
                             '[ .items[] ] ->  back into one array'),
                    'note': 'Wrapping in square brackets collects a stream into '
                            'an array, which is how you get back.',
                },
            ],
            'misconceptions': [
                '`.[]` is not "the array". It is each element as a separate '
                'output, and forgetting that is why a later filter seems to run '
                'the wrong number of times.',
                '`.foo` on missing data gives `null` rather than an error. '
                '`.foo?` suppresses errors on wrong types, which matters on '
                'ragged data.',
                'A key with a hyphen or a space needs quoting: `.["content-'
                'type"]`.',
            ],
            'try_it': [
                'Run `echo \'{"a":[1,2,3]}\' | jq \'.a\'` and then `jq \'.a[]\'` '
                'and look at the difference in the output.',
            ],
        },
        {
            'id': 'aj-jq-select',
            'title': 'select, map, and reshaping',
            'next': 'aj-jq-output',
            'concept': (
                '`select(condition)` keeps an input if the condition is true '
                'and produces nothing otherwise, which makes it jq\'s filter and '
                'the direct analogue of an awk pattern.\n\n'
                '`map(f)` applies a filter to every element of an array and '
                'gives back an array, so it is `[.[] | f]` written shorter. Use '
                'it when you want to stay inside an array; use `.[]` when you '
                'want a stream.\n\n'
                'Building new shapes is done with object and array construction: '
                '`{name: .user.name, when: .ts}` makes a new object from parts '
                'of the old one. That is how you turn an API response into '
                'something a shell script can read.\n\n'
                '`to_entries` turns an object into an array of `{key, value}` '
                'pairs, which is the standard trick for iterating over an object '
                'whose keys you do not know.'
            ),
            'examples': [
                {
                    'label': 'Filtering and reshaping',
                    'code': ("jq '.[] | select(.status >= 400)'\n"
                             "jq '.[] | select(.name | test(\"^adm\"))'\n"
                             "jq 'map(.size) | add'              sum a field\n"
                             "jq '.[] | {host: .client, code: .status}'\n"
                             "jq 'to_entries | .[] | .key'       object keys\n"
                             "jq 'group_by(.host) | map({h: .[0].host,"
                             " n: length})'"),
                    'note': '`test()` takes a regex, which is why regex is a '
                            'prerequisite for this module.',
                },
            ],
            'misconceptions': [
                '`select` is not `if`. It emits its input unchanged or emits '
                'nothing, which is why it composes in a pipeline.',
                '`map` needs an array as input. On a stream it fails, and `.[] '
                '| f` is what you wanted.',
                '`add` on an empty array is `null`, not `0`, which breaks '
                'arithmetic downstream unless you handle it.',
            ],
            'try_it': [
                'Take any JSON API response you have and turn it into a flat '
                'object with three keys you care about.',
            ],
        },
        {
            'id': 'aj-jq-output',
            'title': 'Getting jq output into a shell script',
            'concept': (
                'By default jq prints JSON, which means strings come out with '
                'quotes around them. That is correct and almost never what you '
                'want when the next thing in the pipeline is a shell command.\n\n'
                '`-r` is raw output: strings print without quotes, so '
                '`jq -r \'.[].name\'` gives you a plain list you can loop over. '
                'It is the flag you will use most.\n\n'
                '`-c` is compact, one JSON value per line, which is the right '
                'shape for feeding another tool or for `while read`. `-s` '
                '"slurps" a stream of separate JSON values into one array, '
                'which is how you handle a file with one object per line. And '
                '`@tsv` or `@csv` after a pipe formats an array as columns, '
                'which hands off cleanly to awk or cut.'
            ),
            'examples': [
                {
                    'label': 'The flags that matter',
                    'code': ("jq -r '.[].name'         no quotes\n"
                             "jq -c '.[]'              one line per value\n"
                             'jq -s \'.\'               slurp a stream into an array\n'
                             "jq -r '.[] | [.host, .status] | @tsv'\n"
                             'jq -e \'.ok\'             exit non-zero if false/null'),
                    'note': '`-e` makes jq usable in an `if`, which is how you '
                            'test a field from a script.',
                },
                {
                    'label': 'Handing off to the shell',
                    'code': ("jq -r '.[].host' hosts.json | while read -r h; do\n"
                             '  echo "checking $h"\n'
                             'done\n'
                             '\n'
                             "jq -r '.[] | [.a, .b] | @tsv' | awk '{print $2}'"),
                    'note': 'That last line is the whole point of learning both '
                            'in one module.',
                },
            ],
            'misconceptions': [
                'Without `-r` every string has quotes, which will silently break '
                'the next command in your pipeline.',
                '`-s` and `--slurp` read the entire input into memory, so it is '
                'the wrong choice for a very large stream.',
                'jq exits 0 even when the filter produced nothing. `-e` is what '
                'changes that.',
            ],
            'try_it': [
                'Run a jq filter with and without `-r` and pipe both into `wc '
                '-c` to see the quotes you were about to pass along.',
            ],
        },
    ],

    'drills': [
        # awk
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

        # jq
        {'id': 'aj-cmd-jq-pretty', 'type': 'command', 'answer': 'jq .',
         'prompt': 'Pretty-print a JSON document.',
         'teach': '. is the identity filter, so this says "give me the input, '
                  'formatted".'},
        {'id': 'aj-cmd-jq-key', 'type': 'command', 'answer': "jq '.name'",
         'prompt': 'Extract the name key from a JSON object.',
         'teach': 'A missing key yields null rather than an error. Use .name? '
                  'when the input might not be an object at all.'},
        {'id': 'aj-cmd-jq-nested', 'type': 'command', 'answer': "jq '.user.email'",
         'prompt': 'Extract a nested key.',
         'teach': 'Each dot walks one level. If any level is missing you get '
                  'null, with nothing to say which one it was.'},
        {'id': 'aj-cmd-jq-each', 'type': 'command', 'answer': "jq '.items[]'",
         'prompt': 'Produce each element of the items array as a separate '
                   'output.',
         'teach': 'Not "the array". Several outputs, which is why everything '
                  'downstream runs once per element.'},
        {'id': 'aj-cmd-jq-raw', 'type': 'command', 'answer': "jq -r '.[].name'",
         'prompt': 'Print every name from an array of objects, without the JSON '
                   'quotes.',
         'teach': 'The flag you will use most. Without it the next command in '
                  'your pipeline gets quoted strings.'},
        {'id': 'aj-cmd-jq-select', 'type': 'command',
         'answer': "jq '.[] | select(.status >= 400)'",
         'prompt': 'Keep only the array elements whose status is 400 or more.',
         'teach': 'The empty brackets unwrap the array into a stream of '
                  'elements, and select keeps the ones whose expression is '
                  'true.'},
        {'id': 'aj-cmd-jq-test', 'type': 'command',
         'answer': "jq '.[] | select(.name | test(\"^adm\"))'",
         'prompt': 'Keep elements whose name matches a regex.',
         'teach': 'test takes a regex; contains takes a substring. Reaching '
                  'for contains when you meant a pattern is the usual '
                  'mistake.'},
        {'id': 'aj-cmd-jq-map', 'type': 'command', 'answer': "jq 'map(.size) | add'",
         'prompt': 'Sum the size field across an array.',
         'teach': 'map works on the array itself, so there is no unwrapping '
                  'here. add sums a list and returns null for an empty one.'},
        {'id': 'aj-cmd-jq-len', 'type': 'command', 'answer': "jq '.items | length'",
         'prompt': 'Count how many items an array has.',
         'teach': 'length means different things by type: elements of an '
                  'array, characters of a string, keys of an object.'},
        {'id': 'aj-cmd-jq-shape', 'type': 'command',
         'answer': "jq '.[] | {host: .client, code: .status}'",
         'prompt': 'Build a new object from two fields of each element.',
         'teach': 'Braces build a new object and the keys are yours to name. '
                  "This is how you turn someone else's JSON into columns."},
        {'id': 'aj-cmd-jq-entries', 'type': 'command',
         'answer': "jq 'to_entries | .[] | .key'",
         'prompt': 'List the keys of an object whose key names you do not know '
                   'in advance.',
         'teach': "to_entries turns {a: 1} into [{key: 'a', value: 1}], which "
                  'is what makes unknown key names walkable.'},
        {'id': 'aj-cmd-jq-tsv', 'type': 'command',
         'answer': "jq -r '.[] | [.host, .status] | @tsv'",
         'prompt': 'Emit two fields per element as tab-separated columns, ready '
                   'for awk.',
         'teach': 'This is the handoff that makes learning both in one module '
                  'worth it.'},
        {'id': 'aj-cmd-jq-compact', 'type': 'command', 'answer': "jq -c '.[]'",
         'prompt': 'Emit each element on one line of compact JSON.',
         'teach': '-c is what makes jq output usable in a pipeline, because '
                  'one JSON value per line is what every line-based tool '
                  'expects.'},
        {'id': 'aj-cmd-jq-slurp', 'type': 'command', 'answer': "jq -s '.'",
         'prompt': 'Read a stream of separate JSON values and collect them into '
                   'one array.',
         'teach': '-s reads the whole stream before doing anything, so it '
                  'needs the input to end and it holds all of it in memory.'},
        {'id': 'aj-cmd-jq-exit', 'type': 'command', 'answer': "jq -e '.ok'",
         'prompt': 'Test a JSON field from a shell script, so the exit code '
                   'reflects the result.',
         'teach': '-e exits non-zero when the result is false or null, which '
                  'is the only way to branch on jq inside a shell if.'},
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
        {
            'id': 'aj-jq-filter',
            'title': 'Filter and reshape JSON',
            'goal': 'Use select to keep some records and object construction to '
                    'reshape them.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'events.json': ('[{"client":"10.0.0.1","status":200,"size":512},'
                                '{"client":"10.0.0.2","status":404,"size":128},'
                                '{"client":"10.0.0.3","status":500,"size":2048}]'),
            }},
            'solution': {'shell': "jq '[.[] | select(.status >= 400) | "
                                  "{host: .client, code: .status}]' events.json "
                                  "> failures.json"},
            'steps': [
                {'instruction': 'Take each element of the array.',
                 'hint': '.[]'},
                {'instruction': 'Keep only those with a status of 400 or more.',
                 'hint': 'select(.status >= 400)'},
                {'instruction': 'Reshape each into an object with host and code '
                                'keys, and collect them back into an array in '
                                'failures.json.',
                 'hint': 'wrap the whole filter in [ ] to get an array back'},
            ],
            'free': 'Write failures.json containing an array of {host, code} '
                    'objects for every event with status 400 or more.',
            'verify': {'kind': 'sandbox', 'expect': {
                'exists': ['failures.json'],
                'file_contains': {'failures.json': ['host', 'code', '10.0.0.2',
                                                    '404', '500']},
                'file_lacks': {'failures.json': ['10.0.0.1', 'size']}}},
            'fallback': 'self',
        },
        {
            'id': 'aj-handoff',
            'title': 'Hand jq off to awk',
            'goal': 'Use -r and @tsv to turn JSON into columns, then process '
                    'those with awk. This is why the two are one module.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'events.json': ('[{"client":"10.0.0.1","size":512},'
                                '{"client":"10.0.0.2","size":128},'
                                '{"client":"10.0.0.1","size":2048}]'),
            }},
            'solution': {'shell': "jq -r '.[] | [.client, .size] | @tsv' events.json "
                                  "| awk '{s[$1] += $2} END {for (k in s) "
                                  "print s[k], k}' | sort -rn > bytes.txt"},
            'steps': [
                {'instruction': 'Emit client and size as tab-separated columns.',
                 'hint': "jq -r '.[] | [.client, .size] | @tsv'"},
                {'instruction': 'Sum the sizes per client with awk.',
                 'hint': "awk '{s[$1] += $2} END {for (k in s) print s[k], k}'"},
                {'instruction': 'Sort by total, largest first, into bytes.txt.'},
            ],
            'free': 'Write bytes.txt containing the total bytes per client, '
                    'largest first, by piping jq into awk.',
            'verify': {'kind': 'sandbox', 'expect': {
                'exists': ['bytes.txt'],
                'file_contains': {'bytes.txt': ['2560 10.0.0.1',
                                                '128 10.0.0.2']}}},
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
        {'id': 'aj-jq-reshape',
         'title': 'Turn JSON into columns',
         'goal': 'jq builds new JSON, and with the right flags it builds '
                 'text that other tools can read.',
         'setup': {'kind': 'sandbox',
                   'tree': {'events.json': '[{"client":"10.0.0.1","status":200,"path":"/"},{"client":"10.0.0.2","status":404,"path":"/nope"},{"client":"10.0.0.3","status":500,"path":"/boom"}]\n'}},
         'solution': {'shell': "jq -r '.[] | select(.status >= 400) | "
                               '"\\(.client) \\(.status)"\' events.json > '
                               'bad.txt'},
         'steps': [{'instruction': 'Unwrap the array into a stream of '
                                   'objects.',
                    'hint': '.[]'},
                   {'instruction': 'Keep only the ones whose status is 400 '
                                   'or more.',
                    'hint': 'select(.status >= 400)'},
                   {'instruction': 'Print the client and status as one '
                                   'plain line, not as JSON.',
                    'hint': '-r drops the quotes; "\\(.client) '
                            '\\(.status)" interpolates'}],
         'free': 'Write "client status" into bad.txt for every event with '
                 'a status of 400 or more, as plain text.',
         'verify': {'kind': 'sandbox',
                    'expect': {'file_contains': {'bad.txt': ['10.0.0.2 404',
                                                             '10.0.0.3 '
                                                             '500']},
                               'file_lacks': {'bad.txt': '10.0.0.1'}}},
         'fallback': 'self'},
        {'id': 'aj-jq-group',
         'title': 'Count by key, in JSON',
         'goal': 'The JSON equivalent of sort | uniq -c, which is the '
                 'thing you reach for most often.',
         'setup': {'kind': 'sandbox',
                   'tree': {'hits.json': '[{"path":"/a"},{"path":"/b"},{"path":"/a"},{"path":"/a"},{"path":"/b"}]\n'}},
         'solution': {'shell': "jq -r 'group_by(.path) | .[] | "
                               '"\\(.[0].path) \\(length)"\' hits.json > '
                               'counts.txt'},
         'steps': [{'instruction': 'Group the array by the path field.',
                    'hint': 'group_by(.path) gives an array of arrays'},
                   {'instruction': 'For each group, take the path from its '
                                   'first element and the size of the '
                                   'group.',
                    'hint': '.[0].path and length'},
                   {'instruction': 'Print each as a plain "path count" '
                                   'line into counts.txt.',
                    'hint': '-r again'}],
         'free': 'Write "path count" for each distinct path in hits.json '
                 'into counts.txt.',
         'verify': {'kind': 'sandbox',
                    'expect': {'file_contains': {'counts.txt': ['/a 3',
                                                                '/b 2']}}},
         'fallback': 'self'},
        {'id': 'aj-pipeline-both',
         'title': 'JSON in, columns out, awk on the end',
         'goal': 'The real skill is knowing where jq stops and awk starts. '
                 'Use both in one pipeline.',
         'setup': {'kind': 'sandbox',
                   'tree': {'requests.json': '[{"host":"a","bytes":100},{"host":"b","bytes":250},{"host":"a","bytes":400}]\n'}},
         'solution': {'shell': 'jq -r \'.[] | "\\(.host) \\(.bytes)"\' '
                               "requests.json | awk '{s += $2} END {print "
                               "s}' > bytes.txt"},
         'steps': [{'instruction': 'Use jq to turn each object into a '
                                   'plain "host bytes" line.',
                    'hint': 'jq -r \'.[] | "\\(.host) \\(.bytes)"\''},
                   {'instruction': 'Pipe that into awk and total the '
                                   'second column.',
                    'hint': "awk '{s += $2} END {print s}'"},
                   {'instruction': 'Put the total in bytes.txt.',
                    'hint': 'jq could have done this alone with '
                            'map(.bytes) | add. Knowing both is the '
                            'point'}],
         'free': 'Total the bytes field across requests.json using jq and '
                 'awk together, into bytes.txt.',
         'verify': {'kind': 'sandbox',
                    'expect': {'file_contains': {'bytes.txt': '750'}}},
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

        {'id': 'ajq-jq-stream', 'type': 'mcq',
         'prompt': 'What does `.items[]` produce from `{"items":[1,2,3]}`?',
         'answer': 'Three separate outputs.',
         'distractors': ['One array containing three numbers.',
                         'The number 3.',
                         'An error, because items is not an object.'],
         'teach': 'The single most important idea in jq. Everything downstream '
                  'then runs once per output.'},

        {'id': 'ajq-jq-collect', 'type': 'mcq',
         'prompt': 'How do you turn a stream of jq outputs back into one array?',
         'answer': 'Wrap the filter in square brackets.',
         'distractors': ['Use -s on the command line.',
                         'Use map() at the end.',
                         'Pipe it to add.'],
         'teach': '`[ ... ]` collects. `-s` slurps separate *inputs*, which is a '
                  'different problem.'},

        {'id': 'ajq-jq-raw', 'type': 'mcq',
         'prompt': 'Your jq output breaks the next command in the pipeline. What '
                   'is missing?',
         'answer': '-r, so strings come out without JSON quotes.',
         'distractors': ['-c, to keep it on one line.',
                         '-s, to slurp the input.',
                         '-e, to set the exit code.'],
         'teach': 'The flag you will use most, and the one whose absence fails '
                  'silently rather than loudly.'},

        {'id': 'ajq-select', 'type': 'mcq',
         'prompt': 'What does select() do when its condition is false?',
         'answer': 'Emits nothing, so that input disappears from the stream.',
         'distractors': ['Emits null.', 'Emits the input unchanged.',
                         'Raises an error.'],
         'teach': 'That is why it composes in a pipeline and why it is the '
                  'direct analogue of an awk pattern.'},

        {'id': 'ajq-which', 'type': 'mcq',
         'prompt': 'You have one JSON object per line and want them as a single '
                   'array. Which flag?',
         'answer': '-s, which slurps separate inputs into one array.',
         'distractors': ['-c, which compacts them.',
                         '-r, which strips quotes.',
                         '-n, which reads no input.'],
         'teach': '-s reads everything into memory, so it is the wrong choice '
                  'for a very large stream.'},
    ],
}
