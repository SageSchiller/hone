"""jq: a small functional language for JSON.

jq looks like a JSON path selector and is a functional language. It is the tool
you reach for the moment JSON needs more than an eye can parse: every modern API
and most structured logs are JSON, and jq filters, reshapes and extracts from
them the way awk does for columns. The one idea to hold is that a jq program is
a filter that takes one input and produces zero or more outputs, and `|` chains
filters exactly like a shell pipe.

Fully verified, no new adapter. jq reads JSON and writes to stdout, so a
challenge is "process this input and write the result", and the sandbox adapter
reads the result back.

regex is a prerequisite: `test` in jq takes a regex.
"""

MODULE = {
    'id': 'jq',
    'title': 'jq',
    'group': 'Text processing',
    'blurb': 'Filters and pipes over JSON: select, map, reshape, and hand off to the shell.',
    'context': 'You are at a shell, writing the command that would go on the right-hand side of a pipe.',
    'needs': ('jq',),
    'prereqs': ['regex'],
    'adapter': 'sandbox',
    'estimate': '3-4 hours',
    'order': 32,

    'lessons': [
        {
            'id': 'jq-what',
            'title': 'What jq is for',
            'next': 'aj-jq-model',
            'concept': (
                'jq is a small language people mistake for a path selector, and '
                'it answers one question: given JSON, keep the interesting parts '
                'and reshape them. Its records are JSON values and its fields '
                'are keys, which is the shape of every modern API response and '
                'most structured logs.\n\n'
                'The reason to learn it is that JSON is everywhere and text '
                'tools choke on it: feeding JSON to grep or awk works right up '
                'until a value contains a space, a brace or a newline. jq '
                'understands the structure, so it never breaks on the data. You '
                'do not need to learn it fully; ten percent of jq covers almost '
                'everything anyone actually types.\n\n'
                'Single-quote the program, for the same reason as awk: a jq '
                'filter is full of characters, dollars and pipes and brackets, '
                'that the shell wants to interpret first.'
            ),
            'examples': [
                {
                    'label': 'Structure, not text',
                    'code': ("curl -s api/users | jq '.[] | .name'\n"
                             '  each user, then their name\n'
                             '\n'
                             'grep would break the moment a name has a space,\n'
                             'a comma, or a brace in it. jq never does.'),
                    'note': 'jq parses the JSON, so a value with awkward '
                            'characters in it is just a value.',
                },
            ],
            'misconceptions': [
                'jq is not a replacement for awk. It is awk\'s counterpart for '
                'the other shape of data: trees of JSON rather than columns of '
                'text.',
                'Single-quote the program. A jq filter is full of shell '
                'metacharacters, and double quotes let the shell eat them.',
                'jq does not need the whole manual. select, map, the pipe, and '
                'the output flags are most of real use.',
            ],
            'try_it': [
                'Run `echo \'{"a":[1,2,3]}\' | jq \'.a\'`, then `jq \'.a[]\'`, '
                'and look at how the second one gives you three outputs.',
            ],
        },
        {
            'id': 'aj-jq-model',
            'title': 'A pipeline of filters',
            'next': 'aj-jq-select',
            'concept': (
                'Every jq program is a FILTER: it takes one input, produces '
                'zero or more outputs, and `|` connects them exactly like a '
                'shell pipe.\n\n'
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
                '`map` needs an array. On a stream of scalars it errors, and on a stream of objects it quietly maps the values of each object, which is worse than failing. `.[] | f` was what you wanted, and `.[] '
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
                    'note': 'jq extracts and reshapes; awk and the shell take '
                            'the columns from there.',
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
         'teach': 'This is the handoff to the column tools: jq reshapes JSON '
                  'into rows, awk or cut takes it from there.'},
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
        {'id': 'jqd-interp', 'type': 'command',
         'answer': 'jq -r \'"\\(.client) \\(.status)"\' log.json',
         'prompt': 'Build one text line out of two fields of each object.',
         'teach': 'String interpolation is backslash-paren inside a jq string, and with -r it is how you get plain text out rather than JSON.'},
        {'id': 'jqd-sortby', 'type': 'command',
         'answer': 'jq \'sort_by(-.count)\' data.json',
         'prompt': 'Sort an array by a field, largest first.',
         'teach': 'sort_by orders by any expression, and negating a number reverses it without a separate reverse step.'},
        {'id': 'jqd-groupby', 'type': 'command',
         'answer': 'jq \'group_by(.status)\' log.json',
         'prompt': 'Collect array elements into groups by a shared field.',
         'teach': 'group_by returns an array of arrays, one per distinct value, and it expects the input sorted on the same key.'},
    ],

    'challenges': [
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
        {'id': 'aj-jq-entries',
         'title': 'Turn an object inside out with to_entries',
         'goal': 'to_entries, map and from_entries are how you work on an '
                 'object whose keys you do not know in advance.',
         'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
             'counts.json': '{"alpha": 3, "bravo": 12, "charlie": 7, '
                            '"delta": 1}\n'}},
         'solution': {'shell':
             'jq -r \'to_entries | .[] | "\\(.key) \\(.value)"\' '
             'counts.json > pairs.txt && '
             'jq -r \'to_entries | sort_by(-.value) | .[0].key\' '
             'counts.json > largest.txt && '
             'jq -c \'to_entries | map(select(.value > 5)) | from_entries\' '
             'counts.json > filtered.json'},
         'steps': [{'instruction': 'Turn the object into key and value lines '
                                   'in pairs.txt.',
                    'hint': 'to_entries then interpolate .key and .value'},
                   {'instruction': 'Find the key with the largest value and '
                                   'write just that key to largest.txt.',
                    'hint': 'sort_by(-.value) then take .[0].key'},
                   {'instruction': 'Keep only the entries above 5 and rebuild '
                                   'an object from them, into filtered.json.',
                    'hint': 'map(select(.value > 5)) | from_entries'}],
         'free': 'Produce pairs.txt with key and value per line, largest.txt '
                 'naming the biggest key, and filtered.json holding only the '
                 'entries above five.',
         'verify': {'kind': 'sandbox', 'expect': {
             'file_contains': {'pairs.txt': ['alpha 3', 'bravo 12'],
                               'filtered.json': ['bravo', 'charlie']},
             'file_equals': {'largest.txt': 'bravo'},
             'file_lacks': {'filtered.json': 'delta'}}},
         'fallback': 'self'},
        {'id': 'aj-jq-slurp',
         'title': 'Read a stream of objects as one array',
         'goal': 'JSON lines is not JSON. Slurping is how you treat a stream '
                 'of objects as a list you can aggregate.',
         'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
             'events.jsonl': '{"user":"alice","ms":120}\n'
                             '{"user":"bob","ms":80}\n'
                             '{"user":"alice","ms":200}\n'
                             '{"user":"carol","ms":50}\n'}},
         'solution': {'shell':
             'jq -s \'length\' events.jsonl > count.txt && '
             'jq -s \'map(.ms) | add\' events.jsonl > total.txt && '
             'jq -s -r \'group_by(.user) | .[] | "\\(.[0].user) \\(length)"\' '
             'events.jsonl > byuser.txt'},
         'steps': [{'instruction': 'Slurp the stream and write the number of '
                                   'records to count.txt.',
                    'hint': 'jq -s with length'},
                   {'instruction': 'Sum the ms field across all records into '
                                   'total.txt.',
                    'hint': 'map(.ms) | add'},
                   {'instruction': 'Group by user and write a count per user '
                                   'to byuser.txt.',
                    'hint': 'group_by(.user), then interpolate the name and '
                            'the length'}],
         'free': 'Produce count.txt holding 4, total.txt holding 450, and '
                 'byuser.txt with a count per user.',
         'verify': {'kind': 'sandbox', 'expect': {
             'file_equals': {'count.txt': '4', 'total.txt': '450'},
             'file_contains': {'byuser.txt': ['alice 2', 'bob 1', 'carol 1']}}},
         'fallback': 'self'},
        {'id': 'aj-handoff',
         'title': 'Hand jq off to awk',
         'goal': 'Use -r and @tsv to turn JSON into columns, then process '
                 'those with awk. jq reshapes; the column tools finish the job.',
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
         'fallback': 'self'},
    ],

    'quiz': [
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
