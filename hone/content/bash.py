"""bash: quoting and expansion first, because that is where the bugs are.

**The hard core gets top billing.** Most shell teaching starts with loops and
conditionals and leaves quoting to a footnote, which is backwards: nobody's
script breaks because they got a `for` loop wrong, and everybody's breaks
because a filename had a space in it. Lessons two and three are the module.

**The author's login shell is fish, and that matters here.** fish is
deliberately not POSIX, so daily typing does not reinforce any of this: `set`
instead of assignment, `$status` instead of `$?`, different function syntax, no
word splitting. Everything you will ever run on a server, in a container, in
CI, or on a box you just landed on is bash or close to it. Lesson one names
that gap rather than letting it quietly confuse you.

Challenges ask the sandbox adapter for **bash specifically** rather than your
login shell, because this module is about bash and running its challenges in
fish would teach the wrong thing.

Predict-the-output lives in the quiz rather than the drills, on purpose. "Write
a pipeline that does X" has too many correct answers to grade honestly, while
"what does this print" has exactly one.
"""

MODULE = {
    'id': 'bash',
    'title': 'bash',
    'group': 'Terminal',
    'blurb': 'Quoting, expansion, pipelines and scripts.',
    'context': 'You are writing bash, either at a prompt or in a script. Your login shell is fish, so none of this is muscle memory yet.',
    'prereqs': ['linux'],
    'adapter': 'sandbox',
    'estimate': '6-8 hours',
    'order': 41,

    'lessons': [
        {
            'id': 'sh-which-shell',
            'title': 'Which shell are you actually learning?',
            'next': 'sh-quoting',
            'concept': (
                'Your login shell and the shell your scripts run in are usually '
                'not the same thing, and if you use fish they are definitely '
                'not.\n\n'
                'fish is a genuinely nicer interactive shell and is '
                'deliberately not POSIX compatible. Variables are `set x y` '
                'rather than `x=y`. The exit status is `$status` rather than '
                '`$?`. There is no word splitting, no `export`, and a different '
                'function syntax. None of that transfers.\n\n'
                'It matters because bash is what exists everywhere else: on '
                'every server you ssh into, inside every container, in CI, in '
                '`#!/bin/bash` at the top of scripts other people wrote. So '
                'this module has to be learned deliberately rather than picked '
                'up, because your daily typing will not reinforce it.'
            ),
            'examples': [
                {
                    'label': 'The same idea, two shells',
                    'code': ('bash:  NAME=world            fish:  set NAME world\n'
                             'bash:  export PATH=...       fish:  set -x PATH ...\n'
                             'bash:  echo $?               fish:  echo $status\n'
                             'bash:  for f in *; do        fish:  for f in *\n'
                             'bash:    echo "$f"           fish:    echo $f\n'
                             'bash:  done                  fish:  end'),
                    'note': 'Note there is no space around bash\'s `=`. Adding '
                            'one is the classic first error.',
                },
            ],
            'misconceptions': [
                'A `#!/bin/bash` script does not care what shell you launched it '
                'from. The shebang decides, which is why testing a script by '
                'pasting it into fish proves nothing.',
                '`sh` is not always bash. On Debian and Ubuntu it is dash, which '
                'lacks arrays and `[[ ]]`, so `#!/bin/sh` plus a bashism is a '
                'classic portability bug.',
                'You do not need to switch to bash. You need to know that you '
                'are in a different language when you open a script.',
            ],
            'try_it': [
                'Run `echo $SHELL` and then `bash --version`. Those are two '
                'different programs and both are on your machine.',
            ],
        },
        {
            'id': 'sh-quoting',
            'title': 'Quoting, and word splitting',
            'next': 'sh-expansion',
            'concept': (
                'This is the lesson. Almost every shell bug in the world is '
                'here.\n\n'
                'After the shell expands a variable, it splits the result on '
                'whitespace and then expands any globs in the pieces. So if '
                '`f` holds `My File.txt`, then `rm $f` is **two** arguments and '
                'deletes neither of them. `rm "$f"` is one argument and works. '
                'That is the entire bug, and it is why the rule is: **quote '
                'every variable, every time**.\n\n'
                'Single quotes take everything literally. Double quotes still '
                'expand `$variables` and `$(commands)` but stop the splitting '
                'and globbing. So single when you mean the characters, double '
                'when you mean the value.'
            ),
            'examples': [
                {
                    'label': 'The bug, and the fix',
                    'code': ('f="My File.txt"\n'
                             '\n'
                             'rm $f      ->  rm My File.txt   (two arguments)\n'
                             'rm "$f"    ->  rm "My File.txt" (one argument)\n'
                             '\n'
                             'for x in $list      splits on whitespace\n'
                             'for x in "${arr[@]}"  one item per element'),
                    'note': 'The version without quotes appears to work until a '
                            'filename has a space, and then it deletes the '
                            'wrong thing.',
                },
                {
                    'label': 'Which quote',
                    'code': ("echo '$HOME'    ->  $HOME       literal\n"
                             'echo "$HOME"    ->  /home/sage  the value\n'
                             'echo "cost: \\$5"  ->  cost: $5    escaped\n'
                             '\n'
                             'grep \'^ERROR\'   single: the shell must not touch it\n'
                             'grep "^$name"   double: you need the variable'),
                    'note': 'Patterns go in single quotes so the shell does not '
                            'eat the metacharacters before the tool sees them.',
                },
            ],
            'misconceptions': [
                'Quoting is not about strings with spaces. It is about stopping '
                'the shell from re-parsing a value you already have.',
                '`"$@"` and `$@` are not the same, and `"$*"` is a third thing. '
                'Only `"$@"` passes your arguments through unchanged.',
                'Backslash escaping inside single quotes does nothing. `\'\\n\'` '
                'is a backslash and an n.',
                'A variable holding a glob will be expanded after substitution '
                'unless quoted, which is a subtle and nasty version of the same '
                'bug.',
            ],
            'try_it': [
                'Run `f="a b"; touch "$f"; ls`, then `rm $f` and read the error. '
                'Then `rm "$f"`.',
            ],
        },
        {
            'id': 'sh-expansion',
            'title': 'The order everything happens in',
            'next': 'sh-globs',
            'concept': (
                'The shell rewrites your command line in a fixed order before '
                'running anything, and knowing the order explains most '
                'surprises.\n\n'
                'Brace expansion first, then tilde, then parameters and command '
                'substitution and arithmetic, then **word splitting**, then '
                '**filename globbing**, and quote removal last.\n\n'
                'Two consequences matter. Word splitting happens **after** your '
                'variable is substituted, which is lesson two\'s bug. And '
                'globbing happens after that, which is why a variable '
                'containing `*` expands against your files unless it is quoted. '
                'Brace expansion happening first is why `{1..3}` works but '
                '`{1..$n}` does not.'
            ),
            'examples': [
                {
                    'label': 'The order',
                    'code': ('1  brace        {a,b}   a b\n'
                             '2  tilde        ~       /home/sage\n'
                             '3  parameter    $x  ${x:-default}\n'
                             '3  command      $(date)\n'
                             '3  arithmetic   $((2 + 2))\n'
                             '4  word split   on IFS, only unquoted\n'
                             '5  globbing     *  ?  [abc]\n'
                             '6  quote removal'),
                    'note': 'Steps 4 and 5 are the ones quoting turns off, which '
                            'is exactly why quoting fixes so much.',
                },
                {
                    'label': 'Useful forms',
                    'code': ('${name:-default}   value, or default if unset\n'
                             '${name:?message}   error out if unset\n'
                             '${#name}           length\n'
                             '${name%.txt}       strip a suffix\n'
                             '${name##*/}        basename, without calling it\n'
                             '$(( count + 1 ))   arithmetic\n'
                             'cp file{,.bak}     brace: cp file file.bak'),
                    'note': '`${var:?}` at the top of a script is the cheapest '
                            'way to fail loudly instead of doing something '
                            'terrible with an empty value.',
                },
            ],
            'misconceptions': [
                '`{1..$n}` does not work, because brace expansion happens before '
                'the variable exists. Use `seq` or a C-style loop.',
                'Command substitution strips trailing newlines. That is usually '
                'what you want and occasionally surprising.',
                'Backticks and `$()` are the same thing, but `$()` nests and is '
                'readable, so there is no reason to use backticks.',
            ],
            'try_it': [
                'Run `mkdir -p test/{a,b,c}` and then `echo $((2**10))`.',
            ],
        },
        {
            'id': 'sh-globs',
            'title': 'Globs are not regular expressions',
            'next': 'sh-vars',
            'concept': (
                'They share characters and mean different things, which is why '
                'people who know regex often get globs wrong.\n\n'
                'In a glob, `*` means any run of characters including none, `?` '
                'means exactly one, and `[abc]` is a character class. There is '
                'no `+`, no alternation without extglob, and crucially `*` does '
                'not mean "repeat the previous thing". Glob `*.log` and regex '
                '`.*\\.log` describe the same set.\n\n'
                'The other difference is who does the work. Globs are expanded '
                'by the SHELL before your command runs, so `grep *.log` hands '
                'grep a list of filenames. A regex is handed to the tool as a '
                'string, which is why it needs quoting and a glob does not.'
            ),
            'examples': [
                {
                    'label': 'Same characters, different language',
                    'code': ('glob   *.log        regex   .*\\.log\n'
                             'glob   file?.txt    regex   file.\\.txt\n'
                             'glob   [ab]*        regex   ^[ab]\n'
                             '\n'
                             'glob   *            regex   .*\n'
                             '                    regex   *  means "repeat"'),
                    'note': 'A bare `*` in a regex is a syntax error or a '
                            'literal, never "everything".',
                },
                {
                    'label': 'Who expands it',
                    'code': ('ls *.log          shell expands, ls sees names\n'
                             'grep "^ERROR" f   shell must NOT touch the pattern\n'
                             '\n'
                             'shopt -s globstar\n'
                             'ls **/*.log       recursive, bash only'),
                    'note': 'If a glob matches nothing, bash passes it through '
                            'literally by default, which is a classic source of '
                            'confusing errors.',
                },
            ],
            'misconceptions': [
                'A glob that matches nothing is not empty. bash hands the '
                'literal `*.log` to your command unless `nullglob` is set.',
                'Globs do not match a leading dot. `*` will not find '
                '`.bashrc`.',
                '`**` needs `shopt -s globstar` in bash, and is not portable to '
                'sh.',
            ],
            'try_it': [
                'Run `ls *.nothing` in an empty directory and read the error '
                'carefully. It contains the literal asterisk.',
            ],
        },
        {
            'id': 'sh-vars',
            'title': 'Variables, arguments and arrays',
            'next': 'sh-exit',
            'concept': (
                'Assignment has no spaces: `name=value`. A space makes it a '
                'command invocation and the error will not obviously say so.\n\n'
                'Inside a script your arguments are `$1`, `$2` and so on, `$#` '
                'is how many, and `"$@"` is all of them **as separate words**. '
                'That last one is the important one: `$@` unquoted re-splits '
                'every argument, and `"$*"` joins them into one string. Only '
                '`"$@"` passes what you were given through unchanged.\n\n'
                'Arrays exist in bash and not in sh: `arr=(a b c)`, and '
                '`"${arr[@]}"` iterates them safely. If you find yourself '
                'keeping a list in a space-separated string, you want an array.'
            ),
            'examples': [
                {
                    'label': 'The three forms',
                    'code': ('script.sh "a b" c\n'
                             '\n'
                             '"$@"   ->  "a b"  "c"     two args, correct\n'
                             '$@     ->  "a" "b" "c"    three, wrong\n'
                             '"$*"   ->  "a b c"        one, sometimes wanted'),
                    'note': 'If you only remember one thing: write "$@" with the '
                            'quotes, always.',
                },
                {
                    'label': 'Assignment traps',
                    'code': ('name=value        correct\n'
                             'name = value      runs the command "name"\n'
                             'name="two words"  quote it\n'
                             '\n'
                             'arr=(one two)     bash array\n'
                             'for x in "${arr[@]}"; do echo "$x"; done'),
                    'note': 'The no-spaces rule catches everyone once.',
                },
            ],
            'misconceptions': [
                'Variables have no types. Everything is a string, and `$(( ))` '
                'is where arithmetic happens.',
                'A variable set inside a pipeline stage is lost, because each '
                'stage runs in a subshell.',
                '`local` only exists inside functions, and forgetting it makes '
                'your loop variable global.',
            ],
            'try_it': [
                'Write a two-line script that echoes `"$@"` and run it with an '
                'argument containing a space.',
            ],
        },
        {
            'id': 'sh-exit',
            'title': 'Exit codes and failing loudly',
            'next': 'sh-vocabulary',
            'concept': (
                'Every command returns a number. Zero means success and '
                'anything else means failure, which is backwards from most '
                'languages and worth saying out loud. `$?` holds the last '
                'one.\n\n'
                'That is what `&&` and `||` read: `a && b` runs b only if a '
                'succeeded, `a || b` runs b only if a failed. It is also what '
                '`if` reads, which is why `if grep -q x f; then` is idiomatic '
                'and needs no comparison.\n\n'
                'By default a script keeps going after a command fails, which '
                'is almost never what you want. `set -euo pipefail` at the top '
                'changes that: exit on error, exit on an unset variable, and let '
                'a failure anywhere in a pipeline fail the pipeline. It is three '
                'words and it turns a script that silently does half the job '
                'into one that stops.'
            ),
            'examples': [
                {
                    'label': 'Reading the number',
                    'code': ('cmd; echo $?          0 is success\n'
                             'a && b                b only if a worked\n'
                             'a || echo "failed"    b only if a did not\n'
                             'if grep -q x f; then  no comparison needed\n'
                             '\n'
                             'set -euo pipefail     put this at the top'),
                    'note': 'Without pipefail, `false | true` succeeds, which is '
                            'how a broken pipeline reports success.',
                },
            ],
            'misconceptions': [
                'Zero is success. Non-zero is failure. This is the opposite of '
                'truthiness in every language you know.',
                '`set -e` does not catch everything. A failure inside `if`, `&&` '
                'or a subshell is deliberately exempt, which surprises people.',
                '`$?` is overwritten by the very next command, including an '
                '`echo`, so capture it immediately if you need it.',
            ],
            'try_it': [
                'Run `false | true; echo $?`, then `set -o pipefail` and run it '
                'again.',
            ],
        },
        {
            'id': 'sh-vocabulary',
            'title': 'The pipeline vocabulary',
            'next': 'sh-scripts',
            'concept': (
                'A small set of tools combine into most one-liners, and they '
                'are worth knowing as a vocabulary rather than individually.\n\n'
                '`cut` takes columns, `sort` orders, `uniq` collapses adjacent '
                'duplicates, `wc` counts, `head` and `tail` take the ends, and '
                '`tr` substitutes characters. The single most useful combination '
                'in existence is `sort | uniq -c | sort -rn`, which counts '
                'occurrences and ranks them.\n\n'
                'The one that catches people is `uniq`, which only removes '
                'ADJACENT duplicates. It needs sorted input, which is why it is '
                'always downstream of `sort`.'
            ),
            'examples': [
                {
                    'label': 'The vocabulary',
                    'code': ('cut -d: -f1 /etc/passwd    field 1, colon '
                             'separated\n'
                             'sort -u                    sort and dedupe\n'
                             'sort -rn                   reverse, numeric\n'
                             'uniq -c                    count adjacent runs\n'
                             'wc -l                      count lines\n'
                             'head -20 / tail -20        the ends\n'
                             'tail -f                    follow a growing file\n'
                             "tr -d '\\r'                 delete characters"),
                    'note': '`tr -d \'\\r\'` is the fix for a file that came from '
                            'Windows and behaves strangely.',
                },
                {
                    'label': 'The combination worth memorising',
                    'code': ("awk '{print $1}' access.log \\\n"
                             '  | sort | uniq -c | sort -rn | head\n'
                             '\n'
                             '-> the busiest client addresses, ranked'),
                    'note': 'sort, then count, then sort by count. This answers '
                            'a startling number of questions.',
                },
            ],
            'misconceptions': [
                '`uniq` without `sort` first does almost nothing useful, because '
                'it only collapses adjacent lines.',
                '`sort` is lexicographic by default, so 10 comes before 9. `-n` '
                'fixes it.',
                '`cut` cannot handle runs of spaces as one separator. That is '
                'awk\'s job, and it is the usual reason to reach for awk.',
            ],
            'try_it': [
                'Count the shells in use on your machine: '
                '`cut -d: -f7 /etc/passwd | sort | uniq -c | sort -rn`.',
            ],
        },
        {
            'id': 'sh-scripts',
            'title': 'Writing a script that will not embarrass you',
            'concept': (
                'A script is the same commands in a file, plus four habits that '
                'separate one that works from one that works reliably.\n\n'
                'Start with `#!/usr/bin/env bash` so it finds bash wherever it '
                'lives. Follow with `set -euo pipefail`. Quote every variable. '
                'Check your arguments before doing anything destructive, and '
                '`${1:?usage: ...}` does that in one line.\n\n'
                'Then the ordinary constructs: `if`, `for`, `while`, and '
                'functions. Use `[[ ]]` rather than `[ ]` in bash, because it '
                'does not word-split and has proper `&&`, `||` and pattern '
                'matching.'
            ),
            'examples': [
                {
                    'label': 'The skeleton',
                    'code': ('#!/usr/bin/env bash\n'
                             'set -euo pipefail\n'
                             '\n'
                             'dir="${1:?usage: tidy.sh DIRECTORY}"\n'
                             '\n'
                             'for f in "$dir"/*.log; do\n'
                             '  [[ -e "$f" ]] || continue\n'
                             '  echo "processing $f"\n'
                             'done'),
                    'note': 'The `[[ -e ]] || continue` handles the glob that '
                            'matched nothing and came through literally.',
                },
                {
                    'label': 'Tests worth knowing',
                    'code': ('[[ -f path ]]     a regular file\n'
                             '[[ -d path ]]     a directory\n'
                             '[[ -z "$x" ]]     empty string\n'
                             '[[ -n "$x" ]]     non-empty\n'
                             '[[ "$a" == "$b" ]]  string equal\n'
                             '(( n > 3 ))       arithmetic comparison'),
                    'note': 'Use `[[ ]]` for strings and files, `(( ))` for '
                            'numbers, and never `[ ]` in bash.',
                },
            ],
            'misconceptions': [
                '`[` is a command, not syntax, which is why it needs spaces '
                'around everything and why `[[` exists.',
                'A shebang of `#!/bin/sh` means your bashisms may or may not '
                'work depending on the machine. Say `bash` if you mean bash.',
                'Making a script executable is not enough on a filesystem '
                'mounted `noexec`, which is a fun afternoon to debug.',
            ],
            'try_it': [
                'Write the skeleton above into a file, `chmod +x` it, and run it '
                'with no arguments to see the usage message fire.',
            ],
        },
    ],

    'drills': [
        {'id': 'sh-cmd-quote', 'type': 'command', 'answer': 'rm "$f"',
         'prompt': 'Delete the file whose name is in the variable f, safely, '
                   'even if it contains spaces.',
         'teach': 'Without the quotes the shell splits the value on whitespace '
                  'and you get two arguments, neither of which exists.'},
        {'id': 'sh-cmd-args', 'type': 'command', 'answer': 'echo "$@"',
         'prompt': 'Print all of a script\'s arguments, preserving each one '
                   'exactly as given.',
         'teach': 'Only "$@" with the quotes does this. $@ re-splits and "$*" '
                  'joins them into one string.'},
        {'id': 'sh-cmd-default', 'type': 'command', 'answer': 'echo "${name:-none}"',
         'prompt': 'Print the variable name, or the word none if it is unset or '
                   'empty.',
         'teach': 'The colon covers unset and empty. Without it only unset is '
                  'covered, so an empty variable passes straight through.'},
        {'id': 'sh-cmd-require', 'type': 'command', 'answer': 'dir="${1:?usage}"',
         'prompt': 'Assign the first argument to dir, but exit with a message if '
                   'it was not supplied.',
         'teach': 'The cheapest way to fail loudly instead of doing something '
                  'terrible with an empty value.'},
        {'id': 'sh-cmd-basename', 'type': 'command', 'answer': 'echo "${path##*/}"',
         'prompt': 'Get the filename out of a path held in the variable path, '
                   'without calling basename.',
         'teach': 'Two hashes strip the longest match from the front. One '
                  'strips the shortest, which here would remove only the '
                  'first directory.'},
        {'id': 'sh-cmd-suffix', 'type': 'command', 'answer': 'echo "${f%.txt}"',
         'prompt': 'Strip a .txt suffix from the variable f.',
         'teach': 'Percent strips from the end and hash strips from the '
                  'front. Mixing up the two is the usual slip.'},
        {'id': 'sh-cmd-arith', 'type': 'command', 'answer': 'echo $((n + 1))',
         'prompt': 'Print one more than the number in the variable n.',
         'teach': 'Inside the double parentheses you do not need a dollar on '
                  'variable names, and the result is integer only.'},
        {'id': 'sh-cmd-brace-bak', 'type': 'command', 'answer': 'cp file{,.bak}',
         'prompt': 'Copy "file" to "file.bak" using brace expansion, without '
                   'typing the name twice.',
         'teach': 'Brace expansion happens before anything else on the line, '
                  'so the shell writes out both names for you.'},
        {'id': 'sh-cmd-safety', 'type': 'command', 'answer': 'set -euo pipefail',
         'prompt': 'Write the three settings that belong at the top of every script.',
         'teach': 'Exit on error, exit on unset variable, and let a failure '
                  'anywhere in a pipeline fail the pipeline.'},
        {'id': 'sh-cmd-shebang', 'type': 'command',
         'answer': '#!/usr/bin/env bash',
         'prompt': 'Write the first line of a bash script so it finds bash wherever it lives.',
         'teach': 'Hardcoding /bin/bash breaks wherever bash lives somewhere '
                  'else, which is every BSD and every homebrew install.'},
        {'id': 'sh-cmd-and', 'type': 'command', 'answer': 'make && make install',
         'prompt': 'Run "make install" only if "make" succeeded.',
         'teach': 'Two ampersands run the second command only on success, two '
                  'pipes only on failure, and a semicolon runs it either way.'},
        {'id': 'sh-cmd-quiet-if', 'type': 'command',
         'answer': 'if grep -q pattern file; then', 'accepts': ['grep -q pattern file'],
         'prompt': 'Test whether a file contains a pattern, without printing '
                   'anything, in an if statement.',
         'teach': 'if reads the exit code directly, so no comparison is needed.'},
        {'id': 'sh-cmd-rank', 'type': 'command',
         'answer': 'sort | uniq -c | sort -rn',
         'prompt': 'Build the three-stage pipeline that counts occurrences and ranks them.',
         'teach': 'uniq only collapses adjacent lines, which is why sort must '
                  'come first.'},
        {'id': 'sh-cmd-cut', 'type': 'command', 'answer': 'cut -d: -f1 /etc/passwd',
         'prompt': 'Print the first colon-separated field of /etc/passwd.',
         'teach': 'cut splits on a single character, not a run of them, so it '
                  'is the wrong tool for whitespace-aligned output. Use awk '
                  'there.'},
        {'id': 'sh-cmd-sortn', 'type': 'command', 'answer': 'sort -rn',
         'prompt': 'Sort numerically, largest first.',
         'teach': 'Without -n, sort is lexicographic and 10 comes before 9.'},
        {'id': 'sh-cmd-wcl', 'type': 'command', 'answer': 'wc -l',
         'prompt': 'Count lines.',
         'teach': 'It counts newlines, so a final line with no newline on the '
                  'end is not counted.'},
        {'id': 'sh-cmd-tailf', 'type': 'command', 'answer': 'tail -f app.log',
         'prompt': 'Watch app.log as it grows.',
         'teach': 'Capital -F also survives the file being rotated or '
                  'replaced, which is usually what you want on a log.'},
        {'id': 'sh-cmd-trd', 'type': 'command', 'answer': "tr -d '\\r'",
         'prompt': 'Delete carriage returns from a stream, fixing a file that '
                   'came from Windows.',
         'teach': 'This is the fix for the trailing carriage return that '
                  "turns a shebang into 'bad interpreter'."},
        {'id': 'sh-cmd-testfile', 'type': 'command', 'answer': '[[ -f "$path" ]]',
         'prompt': 'Test that the path in $path is a regular file, using the '
                   'bash form rather than the portable one.',
         'teach': '[[ ]] does not word-split, which is why it is the right one '
                  'in bash. [ is actually a command.'},
        {'id': 'sh-cmd-loop', 'type': 'command',
         'answer': 'for f in *.log; do echo "$f"; done',
         'prompt': 'Loop over every .log file in this directory and echo each '
                   'name safely.',
         'teach': 'The quotes are the point: without them a filename with a '
                  'space becomes two arguments. If nothing matches, the glob '
                  'stays literal.'},
    ],

    'challenges': [
        {
            'id': 'sh-spaces',
            'title': 'Survive a filename with a space',
            'goal': 'Write a loop that handles a filename containing a space, '
                    'which is the bug quoting exists to prevent.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'My Notes.txt': 'alpha\n',
                'plain.txt': 'bravo\n',
                'other.log': 'ignore\n',
            }},
            'solution': {'shell': 'for f in *.txt; do cp "$f" "$f.bak"; done'},
            'steps': [
                {'instruction': 'Loop over every .txt file.',
                 'hint': 'for f in *.txt; do ... done'},
                {'instruction': 'Copy each one to the same name with .bak '
                                'appended, quoting the variable.',
                 'hint': 'cp "$f" "$f.bak"  and note both quotes matter'},
            ],
            'free': 'Make a .bak copy of every .txt file, including the one with '
                    'a space in its name. Leave the .log alone.',
            'verify': {'kind': 'sandbox', 'expect': {
                'exists': ['My Notes.txt.bak', 'plain.txt.bak'],
                'missing': ['other.log.bak'],
                'file_equals': {'My Notes.txt.bak': 'alpha'},
            }},
            'fallback': 'self',
        },
        {
            'id': 'sh-rank',
            'title': 'Count and rank',
            'goal': 'Build the sort-count-sort pipeline and capture its output.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'access.log': ('10.0.0.1 GET /\n10.0.0.2 GET /a\n'
                               '10.0.0.1 GET /b\n10.0.0.3 GET /\n'
                               '10.0.0.1 GET /c\n10.0.0.2 GET /d\n'),
            }},
            'solution': {'shell': "cut -d' ' -f1 access.log | sort | uniq -c "
                                  "| sort -rn > ranked.txt"},
            'steps': [
                {'instruction': 'Take the first field of every line.',
                 'hint': "cut -d' ' -f1 access.log"},
                {'instruction': 'Sort it, count adjacent duplicates, then sort '
                                'by that count descending.',
                 'hint': 'sort | uniq -c | sort -rn'},
                {'instruction': 'Write the result to ranked.txt.',
                 'hint': '> ranked.txt'},
            ],
            'free': 'Write the client addresses from access.log into '
                    'ranked.txt, ordered by how often each appears, most '
                    'frequent first.',
            'verify': {'kind': 'sandbox', 'expect': {
                'exists': ['ranked.txt'],
                'file_contains': {'ranked.txt': ['3 10.0.0.1', '2 10.0.0.2',
                                                 '1 10.0.0.3']},
            }},
            'fallback': 'self',
        },
        {
            'id': 'sh-script',
            'title': 'Write a script that fails loudly',
            'goal': 'Produce a runnable script with a shebang, safety settings, '
                    'and a required argument.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'README': 'Write tidy.sh here.\n',
            }},
            'solution': {'shell': (
                "printf '%s\\n' '#!/usr/bin/env bash' 'set -euo pipefail' "
                "'dir=\"${1:?usage: tidy.sh DIRECTORY}\"' 'echo \"$dir\"' "
                "> tidy.sh && chmod +x tidy.sh")},
            'steps': [
                {'instruction': 'Create tidy.sh with a bash shebang.',
                 'hint': '#!/usr/bin/env bash'},
                {'instruction': 'Add the three safety settings.',
                 'hint': 'set -euo pipefail'},
                {'instruction': 'Require a first argument, with a usage message.',
                 'hint': 'dir="${1:?usage: tidy.sh DIRECTORY}"'},
                {'instruction': 'Make it executable.', 'hint': 'chmod +x tidy.sh'},
            ],
            'free': 'Write an executable tidy.sh with a bash shebang, '
                    'set -euo pipefail, and a first argument required via the '
                    '${1:?...} form.',
            'verify': {'kind': 'sandbox', 'expect': {
                'executable': ['tidy.sh'],
                'file_contains': {'tidy.sh': ['#!/usr/bin/env bash',
                                              'set -euo pipefail', '${1:?']},
            }},
            'fallback': 'self',
        },
        {
            'id': 'sh-streams',
            'title': 'Keep the good output and the errors apart',
            'goal': 'Run something that both succeeds and fails, and file the '
                    'two streams separately.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'good.txt': 'here\n',
            }},
            'solution': {'shell': 'cat good.txt missing.txt > out.txt 2> err.txt; '
                                  'true'},
            'steps': [
                {'instruction': 'cat a file that exists and one that does not.',
                 'hint': 'cat good.txt missing.txt'},
                {'instruction': 'Send stdout to out.txt and stderr to err.txt.',
                 'hint': '> out.txt 2> err.txt'},
            ],
            'free': 'Run cat on good.txt and a nonexistent file, capturing '
                    'normal output in out.txt and the error in err.txt.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'out.txt': 'here', 'err.txt': 'missing.txt'},
                'file_lacks': {'out.txt': 'missing.txt'},
            }},
            'fallback': 'self',
        },
        {'id': 'sh-quoting-spaces',
         'title': 'A filename with a space in it',
         'goal': 'Unquoted expansion is the most common bug in shell '
                 'scripts. Write a loop that survives a space in a '
                 'filename.',
         'setup': {'kind': 'sandbox',
                   'shell': 'bash',
                   'tree': {'my report.txt': 'one\n',
                            'notes.txt': 'two\n'}},
         'solution': {'shell': 'for f in *.txt; do cp "$f" "copy of $f"; '
                               'done'},
         'steps': [{'instruction': 'Loop over every .txt file here. One of '
                                   'them has a space in its name.',
                    'hint': 'for f in *.txt; do ... done'},
                   {'instruction': 'Copy each one to "copy of " plus its '
                                   'name.',
                    'hint': 'cp "$f" "copy of $f". Both quotes matter'},
                   {'instruction': 'Check with ls that you got two copies '
                                   'and not four.',
                    'hint': 'unquoted, "my report.txt" becomes two '
                            'arguments'}],
         'free': 'Make a "copy of X" for each .txt file, including the one '
                 'with a space in its name.',
         'verify': {'kind': 'sandbox',
                    'expect': {'exists': ['copy of my report.txt',
                                          'copy of notes.txt']}},
         'fallback': 'self'},
        {'id': 'sh-exit-status',
         'title': 'Branch on whether a command worked',
         'goal': 'Every command returns a status and the shell can read '
                 'it. Write a script that acts on success and on failure.',
         'setup': {'kind': 'sandbox',
                   'shell': 'bash',
                   'tree': {'there.txt': 'exists\n'}},
         'solution': {'shell': "printf '#!/usr/bin/env bash\\nif [ -f "
                               '"$1" ]; then\\n  echo found\\nelse\\n  '
                               "echo missing\\nfi\\n' > check.sh && chmod "
                               '+x check.sh && ./check.sh there.txt > '
                               'a.txt && ./check.sh nope.txt > b.txt'},
         'steps': [{'instruction': 'Write check.sh, taking a filename as '
                                   'its first argument.',
                    'hint': '"$1" is the first argument, quoted'},
                   {'instruction': 'Print found if the file exists, '
                                   'missing if it does not.',
                    'hint': 'if [ -f "$1" ]; then ... else ... fi'},
                   {'instruction': 'Make it executable, then run it on '
                                   'there.txt into a.txt and on nope.txt '
                                   'into b.txt.',
                    'hint': 'chmod +x check.sh, then ./check.sh there.txt '
                            '> a.txt'}],
         'free': 'Write and run check.sh so a.txt says found and b.txt '
                 'says missing.',
         'verify': {'kind': 'sandbox',
                    'expect': {'executable': ['check.sh'],
                               'file_contains': {'a.txt': 'found',
                                                 'b.txt': 'missing'}}},
         'fallback': 'self'},
        {'id': 'sh-command-substitution',
         'title': "Use one command's output as another's argument",
         'goal': 'Command substitution is what turns a pipeline into a '
                 "program. Build a filename out of a command's output.",
         'setup': {'kind': 'sandbox',
                   'shell': 'bash',
                   'tree': {'data.txt': 'alpha\nbeta\ngamma\n'}},
         'solution': {'shell': 'cp data.txt "data-$(wc -l < '
                               'data.txt).txt"'},
         'steps': [{'instruction': 'Count the lines in data.txt without '
                                   'printing the filename.',
                    'hint': 'wc -l < data.txt. The redirect is why the '
                            'name is absent'},
                   {'instruction': 'Use that number inside a new filename.',
                    'hint': '$(...) substitutes the output. Backticks also '
                            'work and do not nest'},
                   {'instruction': 'Copy data.txt to data-3.txt, without '
                                   'typing the 3.',
                    'hint': 'cp data.txt "data-$(wc -l < data.txt).txt"'}],
         'free': 'Copy data.txt to a file named after its own line count, '
                 'without typing the number.',
         'verify': {'kind': 'sandbox',
                    'expect': {'exists': ['data-3.txt'],
                               'file_contains': {'data-3.txt': 'gamma'}}},
         'fallback': 'self'},
        {'id': 'sh-strict-mode',
         'title': 'A script that stops when something goes wrong',
         'goal': 'By default a shell script carries on after an error and '
                 'can do real damage. Turn that off.',
         'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {}},
         'solution': {'shell': "printf '#!/usr/bin/env bash\\nset -euo "
                               'pipefail\\ncd "$(dirname "$0")"\\necho '
                               "safe\\n' > run.sh && chmod +x run.sh && "
                               './run.sh > out.txt'},
         'steps': [{'instruction': 'Write run.sh with a shebang that finds '
                                   'bash wherever it lives.',
                    'hint': '#!/usr/bin/env bash'},
                   {'instruction': 'Add the three settings that make it '
                                   'stop on an error, an unset variable, '
                                   'and a failed pipe.',
                    'hint': 'set -euo pipefail, on its own line right '
                            'after the shebang'},
                   {'instruction': 'Have it echo safe, make it executable, '
                                   'and run it into out.txt.',
                    'hint': './run.sh > out.txt'}],
         'free': 'Write a strict-mode run.sh that echoes safe, and capture '
                 'its output in out.txt.',
         'verify': {'kind': 'sandbox',
                    'expect': {'executable': ['run.sh'],
                               'file_contains': {'run.sh': ['set -e',
                                                            'pipefail'],
                                                 'out.txt': 'safe'}}},
         'fallback': 'self'},
        {'id': 'sh-defaults',
         'title': 'A variable with a fallback',
         'goal': 'Parameter expansion gives a default without an if '
                 'statement. Use one, and prove it works both ways.',
         'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {}},
         'solution': {'shell': "printf '#!/usr/bin/env bash\\necho "
                               '"${NAME:-nobody}"\\n\' > hello.sh && chmod '
                               '+x hello.sh && ./hello.sh > unset.txt && '
                               'NAME=sage ./hello.sh > set.txt'},
         'steps': [{'instruction': 'Write hello.sh that echoes the NAME '
                                   'variable, falling back to nobody.',
                    'hint': 'echo "${NAME:-nobody}"'},
                   {'instruction': 'Run it with NAME unset, into '
                                   'unset.txt.',
                    'hint': './hello.sh > unset.txt'},
                   {'instruction': 'Run it again with NAME set to sage, '
                                   'into set.txt, without exporting '
                                   'anything.',
                    'hint': 'NAME=sage ./hello.sh > set.txt sets it for '
                            'that command only'}],
         'free': 'Write hello.sh with a default, then capture both cases '
                 'in unset.txt and set.txt.',
         'verify': {'kind': 'sandbox',
                    'expect': {'file_contains': {'unset.txt': 'nobody',
                                                 'set.txt': 'sage'}}},
         'fallback': 'self'},
        {'id': 'sh-here-doc',
         'title': 'Write a multi-line file from a script',
         'goal': 'A here-document writes a block of text without a pile of '
                 'echo lines, and without fighting quotes.',
         'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {}},
         'solution': {'shell': "cat > config.ini <<'EOF'\n"
                               '[server]\n'
                               'host = localhost\n'
                               'port = 8080\n'
                               'EOF'},
         'steps': [{'instruction': 'Start a here-document that writes into '
                                   'config.ini.',
                    'hint': "cat > config.ini <<'EOF'"},
                   {'instruction': 'Write the three lines: a [server] '
                                   'header, a host of localhost, and a '
                                   'port of 8080.',
                    'hint': 'type them plainly, one per line'},
                   {'instruction': 'End it with EOF on a line of its own.',
                    'hint': "quoting the delimiter as 'EOF' stops the "
                            'shell expanding anything inside'}],
         'free': 'Use a here-document to write config.ini with a [server] '
                 'section, host localhost and port 8080.',
         'verify': {'kind': 'sandbox',
                    'expect': {'file_contains': {'config.ini': ['[server]',
                                                                'localhost',
                                                                '8080']}}},
         'fallback': 'self'},
                  ],

    'quiz': [
        {'id': 'bq-split', 'type': 'mcq',
         'prompt': 'f holds `My File.txt`. What does `rm $f` do?',
         'answer': 'Tries to delete two files, "My" and "File.txt".',
         'distractors': ['Deletes My File.txt correctly.',
                         'Errors out before doing anything.',
                         'Deletes every file in the directory.'],
         'teach': 'Word splitting happens after the variable is substituted. '
                  'This is the bug quoting exists to prevent.'},

        {'id': 'bq-quotes', 'type': 'mcq',
         'prompt': "What does `echo '$HOME'` print?",
         'answer': 'The literal text $HOME.',
         'distractors': ['Your home directory path.',
                         'An empty line.',
                         'An error about an unset variable.'],
         'teach': 'Single quotes take everything literally. Double quotes still '
                  'expand variables but stop splitting and globbing.'},

        {'id': 'bq-at', 'type': 'mcq',
         'prompt': 'A script is called with `s.sh "a b" c`. Which form passes '
                   'both arguments through unchanged?',
         'answer': '"$@"',
         'distractors': ['$@', '"$*"', '$*'],
         'teach': 'Unquoted $@ re-splits "a b" into two. "$*" joins everything '
                  'into one string. Only "$@" is faithful.'},

        {'id': 'bq-brace-var', 'type': 'mcq',
         'prompt': 'Why does `echo {1..$n}` not work?',
         'answer': 'Brace expansion happens before the variable is substituted.',
         'distractors': ['Braces need quoting.',
                         '$n must be exported first.',
                         'It only works in sh, not bash.'],
         'teach': 'The expansion order explains most shell surprises. Brace is '
                  'first, parameter substitution is third.'},

        {'id': 'bq-exit', 'type': 'mcq',
         'prompt': 'A command returns 0. What happened?',
         'answer': 'It succeeded.',
         'distractors': ['It failed.', 'It produced no output.',
                         'It was killed by a signal.'],
         'teach': 'Zero is success, which is the opposite of truthiness '
                  'everywhere else and catches everyone once.'},

        {'id': 'bq-pipefail', 'type': 'mcq',
         'prompt': 'What does `false | true; echo $?` print by default?',
         'answer': '0, because only the last command in the pipeline counts.',
         'distractors': ['1, because false failed.',
                         'Nothing; the pipeline aborts.',
                         '2, one per command.'],
         'teach': 'That is exactly the hole `set -o pipefail` closes, and it is '
                  'how a broken pipeline reports success.'},

        {'id': 'bq-glob-vs-regex', 'type': 'mcq',
         'prompt': 'Which regex means the same as the glob `*.log`?',
         'answer': r'.*\.log',
         'distractors': [r'*.log', r'*\.log', r'.*.log$'],
         'teach': 'In a glob, * is "any run of characters". In a regex it means '
                  '"repeat the previous thing", which is why a bare * is not a '
                  'valid pattern on its own.'},

        {'id': 'bq-nomatch', 'type': 'mcq',
         'prompt': 'You run `ls *.nothing` in a directory with no such files. '
                   'What does ls receive?',
         'answer': 'The literal string *.nothing.',
         'distractors': ['Nothing; the glob expands to empty.',
                         'An error from the shell before ls runs.',
                         'Every file in the directory.'],
         'teach': 'bash passes an unmatched glob through literally unless '
                  'nullglob is set, which is why the error mentions an '
                  'asterisk.'},

        {'id': 'bq-uniq', 'type': 'mcq',
         'prompt': 'Why does `uniq` almost always follow `sort`?',
         'answer': 'It only collapses adjacent duplicate lines.',
         'distractors': ['It requires input on stdin.',
                         'sort removes the duplicates and uniq counts them.',
                         'It is a convention with no technical reason.'],
         'teach': 'Unsorted input means duplicates are not adjacent, so uniq '
                  'silently does almost nothing.'},

        {'id': 'bq-fish', 'type': 'mcq',
         'prompt': 'You use fish daily. Which of these transfers to bash?',
         'answer': 'Almost none of the syntax; pipes and redirection do.',
         'distractors': ['All of it; fish is a POSIX shell.',
                         'Variable assignment and exit status checking.',
                         'Functions and loops, but not variables.'],
         'teach': 'fish is deliberately not POSIX. `set x y`, `$status` and its '
                  'function syntax are all fish-only, which is why this module '
                  'has to be learned deliberately.'},

        {'id': 'bq-assign', 'type': 'mcq',
         'prompt': 'What does `name = value` do in bash?',
         'answer': 'Tries to run a command called name.',
         'distractors': ['Assigns value to name.',
                         'A syntax error at parse time.',
                         'Assigns, but only inside a function.'],
         'teach': 'Assignment takes no spaces around the equals sign. The error '
                  'message does not obviously say so.'},
    ],
}
