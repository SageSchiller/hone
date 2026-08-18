"""make: a graph of files, not a script.

A Makefile is a list of files and the files they are made from. make walks
that graph, compares timestamps, and runs only the recipes whose outputs are
missing or older than their inputs. That is why a second make does nothing,
and why touching one header rebuilds half a tree.

Not a shell script with extra colons. A script runs every line. make decides
which lines are still needed.

Sandbox-verified with real make on tiny graphs of text files, so gcc is not
required for the checked work. A C or LaTeX project is the self-marked end.
"""

MODULE = {
    'id': 'make',
    'title': 'make',
    'group': 'Scripting',
    'blurb': 'A graph of files: rebuild only what is stale.',
    'context': 'You are at a shell in a directory that contains a Makefile.',
    'needs': ('make',),
    'prereqs': ['linux', 'bash'],
    'adapter': 'sandbox',
    'estimate': '3-4 hours',
    'order': 62,

    'lessons': [
        {
            'id': 'mf-what',
            'title': 'A graph of files, not a script',
            'next': 'mf-rules',
            'concept': (
                'make reads a Makefile and brings named files up to date. '
                'That is the program that runs when you type `make` in a C '
                'tree, a kernel checkout, or a directory that builds a PDF '
                'from a `.tex` file. It looks at which outputs are missing '
                'or older than their inputs, and it runs only those recipes.\n\n'
                'That is why it is worth learning even if you never write a '
                'Makefile of your own. Almost every compiled thing you clone '
                'expects that one word. Without the model, a recipe that does '
                'not fire looks like a broken file, and a second `make` that '
                'prints `Nothing to be done` looks like a failure. With it, '
                'both are information: the graph is already current. A shell '
                'script cannot say that, because a script runs every line '
                'every time.\n\n'
                'The decision is a **graph**. A node is a file, called a '
                'target. An edge is "this file needs that file", a '
                'dependency. A recipe is the shell lines that build the '
                'target from those dependencies. make walks from the target '
                'you named back to files that already exist.\n\n'
                'The file is `Makefile` or `makefile` in the current '
                'directory. `make` with no arguments builds the first target, '
                'which by convention is a target named `all` that depends on '
                'the real products. A `clean` rule placed at the top becomes '
                'the default, which is how a first Makefile deletes the tree '
                'it was meant to build.\n\n'
                'The next lesson is the rule: one target, its dependencies, '
                'and the recipe lines that must start with a tab.'
            ),
            'examples': [
                {
                    'label': 'A script versus a graph',
                    'code': ('# a script always does both\n'
                             'cc -c a.c\n'
                             'cc -c b.c\n'
                             'cc -o prog a.o b.o\n'
                             '\n'
                             '# make does the ones that are stale'),
                    'note': 'Change a.c and make recompiles a.c and relinks. '
                            'b.o is left alone. That saved rebuild is the '
                            'reason the tool exists.',
                },
                {
                    'label': 'The default file',
                    'code': ('make              first target in Makefile\n'
                             'make prog         that target, and what it needs\n'
                             'make -f other.mk  a different file'),
                    'note': '-f is how a project ships more than one graph: '
                            'a Makefile for the build, another for release.',
                },
            ],
            'misconceptions': [
                'make is not "run these commands". It is "bring this file up '
                'to date". The commands are how, not whether.',
                'The second make doing nothing is success. It means the graph '
                'already matches the files on disk.',
            ],
            'try_it': [
                'Run `make` in a directory with no Makefile and read the '
                'error. Then the next lesson writes one.',
            ],
        },
        {
            'id': 'mf-rules',
            'title': 'A rule: target, dependencies, recipe',
            'next': 'mf-stale',
            'concept': (
                'A rule is how you tell make one fact: this file is made '
                'from those files, by these commands. That is the whole '
                'language. Learn the three parts and every Makefile you open '
                'is the same shape, which is why `missing separator` is worth '
                'understanding on purpose rather than as a random error.\n\n'
                'The first line is `target: dep1 dep2`. The target is the '
                'file this rule knows how to build. The names after the colon '
                'are files that must exist, and be up to date, first. The '
                'following lines are the **recipe**, and each recipe line '
                'must start with a real tab character. Spaces will not do. '
                'make prints `missing separator` and stops. Editors that '
                'convert tabs to spaces will ruin a Makefile you cannot see '
                'is ruined.\n\n'
                'The recipe is a shell. Each line is a separate shell by '
                'default, so `cd dir` on one line does not change the next '
                'line. A backslash at the end of a line continues it. `set '
                '-e` is not on unless you write it, so a failed command does '
                'stop the recipe (make checks the exit of each line) but a '
                'pipeline needs the same care it needs in bash.\n\n'
                'A comment is `#`. There is no header. The first rule is the '
                'default goal unless you set `.DEFAULT_GOAL`.\n\n'
                'Two prefixes on a recipe line are worth knowing early. `@` '
                'hides the command itself, so only its output prints. `-` '
                'tells make to ignore a non-zero exit, which is how `clean` '
                'can `rm` a file that is not there. Neither is a substitute '
                'for a tab. If make says `missing separator` and you are sure '
                'you typed a tab, the file on disk still has spaces: `cat -A` '
                'shows `^I` for a tab and blanks for spaces.\n\n'
                'The next lesson is stale: the timestamp rule that decides '
                'whether a recipe runs at all.'
            ),
            'examples': [
                {
                    'label': 'One rule, written out',
                    'code': ('out.txt: in.txt\n'
                             '\tcat in.txt > out.txt\n'
                             '\n'
                             'the line with cat starts with a tab'),
                    'note': 'make out.txt builds it if out.txt is missing or '
                            'older than in.txt. make with no arguments does '
                            'the same, because this is the first rule.',
                },
                {
                    'label': 'Each line is a new shell',
                    'code': ('wrong:\n'
                             '\tcd build\n'
                             '\tcc -o prog *.c\n'
                             '\n'
                             'right:\n'
                             '\tcd build && cc -o prog *.c'),
                    'note': 'The cd in the first version evaporates with the '
                            'shell that ran it. The next line starts at the '
                            'original directory.',
                },
            ],
            'misconceptions': [
                'Spaces are not tabs. missing separator is almost always a '
                'recipe line that starts with spaces.',
                'A recipe line is not run in the same shell as the line '
                'above it. && is how you keep a directory change.',
            ],
            'try_it': [
                'Write the out.txt rule, run make, run make again, and read '
                'the second output.',
            ],
        },
        {
            'id': 'mf-stale',
            'title': 'Stale: missing, or older than a dependency',
            'next': 'mf-vars',
            'concept': (
                'Stale is the decision make actually makes: should this '
                'recipe run. That is why the second `make` does nothing, and '
                'why one header edit rebuilds half a tree. Learn it and a '
                'silent skip is information, not a broken file.\n\n'
                'A target is stale if it does not exist, or if any dependency '
                'has a newer modification time. That is the whole decision. '
                'make does not look inside the files. Touch a header, and '
                'every file that lists that header is stale, even if the '
                'edit was a comment.\n\n'
                'A dependency that does not exist is itself a target. make '
                'looks for a rule that builds it, and walks further back. If '
                'there is no rule and no file, make stops with `No rule to '
                'make target`. That error means the graph is broken, not that '
                'the recipe failed.\n\n'
                '`make -n` prints the recipes it *would* run, and runs none '
                'of them. That is the dry run, and it is the first flag to '
                'reach for in a Makefile you did not write. `make -B` treats '
                'every target as stale, which is how you force a rebuild '
                'without deleting the products.\n\n'
                'make does not hash contents, which is why a comment in a '
                'header still rebuilds every file that lists that header, and '
                'why a generated file with an old timestamp can hide a real '
                'change. Clock skew between two machines, or an unpack that '
                'preserves mtimes, is the usual way a tree looks up to date '
                'when it is not. `touch` is the hammer: it updates the time '
                'without changing the bytes, so it is both the way you test '
                'a rule and the way you force one. `make -d` prints every '
                '"considering" decision when you are sure a rule should have '
                'fired and it did not.\n\n'
                'The next lesson is variables: the names that keep a recipe '
                'from repeating a compiler line ten times.'
            ),
            'examples': [
                {
                    'label': 'What a second make does',
                    'code': ('$ make\n'
                             'cat in.txt > out.txt\n'
                             '$ make\n'
                             'make: \'out.txt\' is up to date.\n'
                             '$ touch in.txt\n'
                             '$ make\n'
                             'cat in.txt > out.txt'),
                    'note': 'touch updates the timestamp without changing '
                            'the bytes. make only sees the time.',
                },
                {
                    'label': 'Look before you run',
                    'code': ('make -n          print, do not run\n'
                             'make -B          treat everything as stale\n'
                             'make -d          a flood of "considering" lines'),
                    'note': '-n is the one to type first in a foreign tree. '
                            '-d is how you debug a rule you are sure should '
                            'have fired.',
                },
            ],
            'misconceptions': [
                'make does not hash the contents. A comment in a header still '
                'rebuilds every file that lists that header.',
                'No rule to make target is not a recipe error. It is a missing '
                'file that nothing in the Makefile knows how to build.',
            ],
            'try_it': [
                'Build out.txt, touch in.txt, run make -n, then make, then '
                'make again. Three different answers from the same graph.',
            ],
        },
        {
            'id': 'mf-vars',
            'title': 'Variables, and the automatic ones',
            'next': 'mf-phony',
            'concept': (
                'Variables are how one compile line serves every file. The '
                'automatic ones (`$@`, `$<`, `$^`) are why a pattern rule can '
                'exist at all. Learn them and a Makefile stops looking like '
                'line noise and starts looking like one recipe reused.\n\n'
                '`CC = gcc` and `CFLAGS = -g -Wall` are ordinary variables. '
                '`$(CC)` expands them. `=` is recursively expanded, which is '
                'why a variable can refer to one defined later. `:=` is '
                'expanded now. Use `:=` when the right-hand side is a '
                'command you do not want to run twice.\n\n'
                '**Automatic variables** are the ones you did not set. `$@` '
                'is the target. `$<` is the first dependency. `$^` is every '
                'dependency, unique. `$?` is only the ones newer than the '
                'target. A recipe that says `$(CC) -c $< -o $@` works for '
                'every object file, because make fills in the names from the '
                'rule it is running.\n\n'
                'Those sigils are why a Makefile looks like line noise. They '
                'are also why one pattern rule, in the next lesson but one, '
                'can replace twenty copies of the same compile line.\n\n'
                '`$(CC)` with a missing variable expands to empty, so the '
                'recipe starts with `-c` and fails in a way that looks like a '
                'broken compiler. Set CC. `=` is recursive, which is why a '
                'variable can mention one defined later, and why a cycle is a '
                'real error rather than a leftover name. `:=` is the safer '
                'default when the right-hand side is a command: `$(shell '
                'date)` with `=` runs date every time the variable is used. '
                '`$(CC)` and `${CC}` are the same to make; pick one. The '
                'shell never sees `$@`. make expands it first, which is why '
                'a recipe that quotes $@ still works and a recipe that '
                'expects the shell\'s $@ does not.\n\n'
                'The next lesson is .PHONY: targets that are names for '
                'actions, not files.'
            ),
            'examples': [
                {
                    'label': 'Write the names once',
                    'code': ('CC := gcc\n'
                             'CFLAGS := -g -Wall\n'
                             '\n'
                             'hello.o: hello.c\n'
                             '\t$(CC) $(CFLAGS) -c $< -o $@'),
                    'note': '$< is hello.c. $@ is hello.o. Change the rule '
                            'and the recipe still points at the right files.',
                },
                {
                    'label': 'The four you actually type',
                    'code': ('$@    the target\n'
                             '$<    the first dependency\n'
                             '$^    all dependencies\n'
                             '$?    only the newer ones'),
                    'note': 'Linking wants $^, because every .o belongs on '
                            'the command line. Compiling one file wants $<.',
                },
            ],
            'misconceptions': [
                '$@ is not a shell PID. In a recipe it is the target. The '
                'shell never sees the sigil; make expands it first.',
                '$(CC) with a missing variable expands to empty, so the '
                'recipe starts with -c and fails in a confusing way. Set CC.',
            ],
            'try_it': [
                'Rewrite the out.txt rule using $@ and $<, then run make -n '
                'and confirm the expanded line is still cat in.txt > out.txt.',
            ],
        },
        {
            'id': 'mf-phony',
            'title': '.PHONY: a target that is not a file',
            'next': 'mf-patterns',
            'concept': (
                '`.PHONY` is how you name an action rather than a file. '
                'Without it, `make clean` can no-op because a file named '
                'clean exists. That is why every Makefile you will live with '
                'lists `clean`, `test`, and `all` as phony.\n\n'
                'If a file called `clean` ever appears in the directory, make '
                'sees a target that exists and has no dependencies, decides '
                'it is up to date, and refuses to run the recipe.\n\n'
                '`.PHONY: clean test all` tells make those names are not '
                'files. It will run their recipes whenever you ask, and it '
                'will not look for a file of that name. `all` is usually '
                'phony and depends on the real products, so `make` with no '
                'arguments still means "build the things" even if a file '
                'called `all` shows up.\n\n'
                '`clean` is a recipe that deletes products. It should depend '
                'on nothing, so it is always stale as an action, and it '
                'should be phony, so a file named clean cannot shadow it. '
                '`make clean` then `make` is a full rebuild without `-B`.\n\n'
                'The same trap eats `test`, `install`, and `all`. A file of '
                'that name, no dependencies, exists: make thinks the work is '
                'done. `.PHONY` is the fix, and it has to list every action '
                'name, not only `clean`. Marking a *real* file as phony is '
                'the opposite mistake: make will rebuild it every time, which '
                'is how a "I added .PHONY to be safe" change turns a two '
                'second tree into a full compile. A `FORCE` target with no '
                'recipe is the older pattern for the same idea; `.PHONY` is '
                'the one to write now.\n\n'
                'The next lesson is pattern rules: one recipe for every file '
                'that matches a shape.'
            ),
            'examples': [
                {
                    'label': 'The usual pair',
                    'code': ('.PHONY: all clean\n'
                             '\n'
                             'all: prog\n'
                             '\n'
                             'prog: a.o b.o\n'
                             '\t$(CC) -o $@ $^\n'
                             '\n'
                             'clean:\n'
                             '\trm -f prog a.o b.o'),
                    'note': 'all is the default because it is first. It is '
                            'phony so a file named all cannot steal it.',
                },
                {
                    'label': 'What goes wrong without .PHONY',
                    'code': ('$ touch clean\n'
                             '$ make clean\n'
                             'make: \'clean\' is up to date.'),
                    'note': 'A file named clean, no dependencies, exists: '
                            'make thinks the work is done. .PHONY stops that.',
                },
            ],
            'misconceptions': [
                'all is not a reserved word. It is a convention. make builds '
                'the first target, whatever you called it.',
                'clean is not implied. If you do not write the rule, make '
                'has no idea what to delete.',
            ],
            'try_it': [
                'Add a phony clean that deletes out.txt. Run make, touch '
                'clean, run make clean, and confirm out.txt still goes away.',
            ],
        },
        {
            'id': 'mf-patterns',
            'title': 'Pattern rules: one recipe, many files',
            'next': 'mf-flags',
            'concept': (
                'A pattern rule is one recipe for a shape, not a file. That '
                'is how a real C project stays a list of names plus three '
                'lines, instead of a recipe per object. Learn it and adding '
                'a `.c` is adding a word, not copying a compile line.\n\n'
                '`%.o: %.c` means "a '
                'file ending in .o is made from the file with the same stem '
                'ending in .c". The recipe uses `$<` and `$@` and works for '
                'every match.\n\n'
                'make applies a pattern when it needs a file and no explicit '
                'rule names that file. An explicit rule still wins. That is '
                'how you share a compile line and still special-case one '
                'object.\n\n'
                '`%.o: %.c` plus a list of objects is a whole C project. You '
                'do not write a recipe for each file. You write the list, '
                'the pattern, and the link line. Adding a .c is adding a '
                'name to the list.\n\n'
                'A pattern that matches too much is a surprise rebuild. Keep '
                'the stem simple. `src/%.o: src/%.c` is the usual way to '
                'keep objects next to sources without compiling the whole '
                'disk.\n\n'
                'make also has built-in implicit rules. A `hello` target with '
                'no recipe will try to build `hello` from `hello.c` using '
                'those, which is convenient in a one-file directory and a '
                'surprise when a leftover `.c` starts compiling. `make -r` '
                'turns the built-ins off, which is why a careful Makefile '
                'often starts with that in `.MAKEFLAGS` or just writes every '
                'recipe it actually wants. `%.o: %.c` does not compile every '
                '`.c` in the directory. It compiles the ones some other rule '
                'asked for. That is the difference between a pattern and a '
                'loop.\n\n'
                'The next lesson is the flags that make a foreign Makefile '
                'survivable, and a small complete file you can steal.'
            ),
            'examples': [
                {
                    'label': 'One compile line',
                    'code': ('OBJS := a.o b.o c.o\n'
                             '\n'
                             'prog: $(OBJS)\n'
                             '\t$(CC) -o $@ $^\n'
                             '\n'
                             '%.o: %.c\n'
                             '\t$(CC) $(CFLAGS) -c $< -o $@'),
                    'note': 'Need a.o? The pattern builds it from a.c. Need '
                            'prog? The explicit rule links the objects.',
                },
                {
                    'label': 'A header, listed once',
                    'code': ('$(OBJS): defs.h'),
                    'note': 'Every object depends on defs.h. Edit the header '
                            'and the pattern rebuilds every .o, then prog.',
                },
            ],
            'misconceptions': [
                'A pattern is not a loop in the Makefile. make instantiates '
                'it when it needs a file that matches.',
                '%.o: %.c does not compile every .c in the directory. It '
                'compiles the ones some other rule asked for.',
            ],
            'try_it': [
                'Write a pattern that builds %.txt from %.in by copying, then '
                'ask make for hello.txt and confirm it looks for hello.in.',
            ],
        },
        {
            'id': 'mf-flags',
            'title': 'Flags, and a Makefile you can live with',
            'concept': (
                'These flags are how you drive a Makefile you did not write. '
                '`make -n` before anything runs is the reason this lesson '
                'exists: a foreign tree should be readable before it is '
                'trusted. The tiny file at the end is a shape you can copy.\n\n'
                '`make -n` is the dry run. `make -C dir` runs as if the '
                'shell were already in that directory. `make -B` rebuilds everything. '
                '`make -j4` runs up to four recipes at once, which is how a '
                'large tree finishes in a sensible time and how a broken '
                'dependency shows up as a race. `make -k` keeps going after '
                'an error so you see more than the first failure. `make -f '
                'path` uses a different file. `make VAR=value` sets a '
                'variable for this run and overrides the file, which is how '
                '`make CC=clang` works without editing anything.\n\n'
                'A Makefile that builds text, C, or a LaTeX paper is the '
                'same graph. The recipes change. The stale rule does not. '
                'latexmk is a specialised make for TeX; make is the general '
                'one, and a `paper.pdf: paper.tex` rule is enough for a '
                'single document.\n\n'
                '`make -j` is not unsafe by nature. A recipe that needed a '
                'header you did not declare was always broken; `-j` just '
                'loses the lucky order that hid it. The race shows up as a '
                'missing `.h` on one core and a clean build on another, which '
                'is why the fix is the dependency, not "do not use -j". '
                '`make VAR=value` sets make\'s own variable for this run and '
                'is not an environment export unless the Makefile `export`s '
                'it. `include other.mk` pulls a second graph in, which is how '
                'generated dependency files (`gcc -MMD`) land in a real tree.\n\n'
                'That is enough to read a project Makefile, write a small '
                'one, and not fear `missing separator`. Parallel races as a '
                'subject of their own can wait until a tree is large enough '
                'to hurt.'
            ),
            'examples': [
                {
                    'label': 'Driving a foreign tree',
                    'code': ('make -n           what would run\n'
                             'make -j8          use the cores\n'
                             'make -k           do not stop at the first error\n'
                             'make CC=clang     override a variable\n'
                             'make -f release.mk'),
                    'note': '-n first, then -j. A race from -j is a missing '
                            'dependency, not a reason to avoid -j forever.',
                },
                {
                    'label': 'A complete tiny file',
                    'code': ('.PHONY: all clean\n'
                             'all: out.txt\n'
                             '\n'
                             'out.txt: in.txt\n'
                             '\tcat $< > $@\n'
                             '\n'
                             'clean:\n'
                             '\trm -f out.txt'),
                    'note': 'Replace cat with $(CC) or pdflatex and the graph '
                            'is a C program or a paper. The shape is the same.',
                },
            ],
            'misconceptions': [
                'make -j is not unsafe by nature. A recipe that needed a '
                'dependency you did not declare was always broken; -j just '
                'loses the lucky order.',
                'make VAR=value is not an environment export unless you '
                'export the variable in the Makefile. It sets make\'s own '
                'variable for this run.',
            ],
            'try_it': [
                'Write the tiny file above, run make -n, make, make -B, and '
                'make clean, and watch which recipes fire.',
            ],
        },
    ],

    'drills': [
        {'id': 'mfd-pat', 'type': 'command',
         'answer': '%.o: %.c',
         'prompt': 'Write the pattern rule that builds any .o from the matching .c.',
         'teach': 'One recipe for a shape. make fills $@ and $< from the match.'},
        {'id': 'mfd-make', 'type': 'command',
         'answer': 'make',
         'prompt': 'Build the first target in the Makefile in this directory.',
         'teach': 'No arguments means the first target. That is usually all.'},
        {'id': 'mfd-target', 'type': 'command',
         'answer': 'make prog',
         'prompt': 'Build the target named prog.',
         'teach': 'make walks prog\'s dependencies and runs only stale recipes.'},
        {'id': 'mfd-n', 'type': 'command',
         'answer': 'make -n',
         'prompt': 'Print the recipes make would run, without running them.',
         'teach': 'The dry run. First flag on a Makefile you did not write.'},
        {'id': 'mfd-B', 'type': 'command',
         'answer': 'make -B',
         'prompt': 'Rebuild every target, even those that look up to date.',
         'teach': '-B treats everything as stale. A rebuild without deleting.'},
        {'id': 'mfd-j', 'type': 'command',
         'answer': 'make -j4',
         'prompt': 'Run up to four recipes at once.',
         'teach': 'A race under -j is a missing dependency, not a make bug.'},
        {'id': 'mfd-f', 'type': 'command',
         'answer': 'make -f other.mk',
         'prompt': 'Use other.mk instead of Makefile.',
         'teach': '-f names the graph. The default names are Makefile and makefile.'},
        {'id': 'mfd-clean', 'type': 'command',
         'answer': 'make clean',
         'prompt': 'Run the clean target.',
         'teach': 'clean is a convention, and it should be .PHONY so a file '
                  'cannot shadow it.'},
        {'id': 'mfd-at', 'type': 'command',
         'answer': '$@',
         'prompt': 'Write the automatic variable that names this rule\'s target.',
         'teach': 'make expands $@ before the shell sees the line.'},
        {'id': 'mfd-lt', 'type': 'command',
         'answer': '$<',
         'prompt': 'Write the automatic variable for the first dependency.',
         'teach': 'Compiling one source wants $<. Linking many objects wants $^.'},
        {'id': 'mfd-hat', 'type': 'command',
         'answer': '$^',
         'prompt': 'Write the automatic variable for every dependency.',
         'teach': 'Unique, all of them. The link line is $(CC) -o $@ $^.'},
        {'id': 'mfd-C', 'type': 'command',
         'answer': 'make -C build',
         'prompt': 'Run make as if this shell were already in the build directory.',
         'teach': '-C changes directory first. The Makefile there is the one that runs.'},
        {'id': 'mfd-cc', 'type': 'command',
         'answer': 'make CC=clang',
         'prompt': 'Build with CC set to clang for this run only.',
         'teach': 'A command-line variable overrides the Makefile for this run.'},
    ],

    'challenges': [
        {
            'id': 'mfc-first',
            'title': 'A graph of two text files',
            'goal': 'The smallest Makefile that is actually a graph: one '
                    'product, one input, a recipe that copies.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {'in.txt': 'hello\n'},
            },
            'solution': {
                'shell': (
                    "cat > Makefile <<'END'\n"
                    "out.txt: in.txt\n"
                    "\tcat in.txt > out.txt\n"
                    "END\n"
                    "make"
                ),
            },
            'steps': [
                {'instruction': 'Write a Makefile that builds out.txt from '
                                'in.txt by copying.',
                 'hint': 'out.txt: in.txt  then a tab and cat in.txt > out.txt'},
                {'instruction': 'Run make so out.txt exists.'},
            ],
            'free': 'Produce out.txt via make from in.txt.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'is_file': ['out.txt', 'Makefile'],
                    'file_contains': {'out.txt': 'hello'},
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'mfc-phony',
            'title': 'all, the product, and a clean target',
            'goal': 'A Makefile people can live with: a phony all, a real '
                    'file, and a phony clean.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {'in.txt': 'hello\n'},
            },
            'solution': {
                'shell': (
                    "cat > Makefile <<'END'\n"
                    ".PHONY: all clean\n"
                    "all: out.txt\n"
                    "out.txt: in.txt\n"
                    "\tcat $< > $@\n"
                    "clean:\n"
                    "\trm -f out.txt\n"
                    "END\n"
                    "make"
                ),
            },
            'steps': [
                {'instruction': 'Write a Makefile with phony all and clean.',
                 'hint': '.PHONY: all clean'},
                {'instruction': 'all depends on out.txt. out.txt is built '
                                'from in.txt. clean deletes out.txt.'},
                {'instruction': 'Run make and leave out.txt in place so it '
                                'can be checked.'},
            ],
            'free': 'A Makefile with phony all and clean that builds out.txt.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'is_file': ['out.txt'],
                    'file_contains': {
                        'Makefile': ['.PHONY', 'all', 'clean', 'out.txt'],
                        'out.txt': 'hello',
                    },
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'mfc-n',
            'title': 'Dry-run a Makefile you did not write',
            'goal': 'The first flag on a foreign tree is -n. Capture what '
                    'make would do without doing it.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {
                    'in.txt': 'hello\n',
                    'Makefile': (
                        'out.txt: in.txt\n'
                        '\tcat in.txt > out.txt\n'
                    ),
                },
            },
            'solution': {
                'shell': 'make -n > would.txt',
            },
            'steps': [
                {'instruction': 'Run make -n and save the output as would.txt.',
                 'hint': 'make -n > would.txt'},
            ],
            'free': 'Write would.txt with the recipe make would run, without '
                    'creating out.txt.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_contains': {'would.txt': 'cat'},
                    'missing': ['out.txt'],
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'mfc-live',
            'title': 'Point make at a real project',
            'goal': 'Text files prove the model. Your own tree is the habit.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'Write a Makefile for a small C program or a '
                                'LaTeX paper: all, the product, clean.'},
                {'instruction': 'Run make -n, then make, then make again, and '
                                'confirm the second run does nothing.'},
                {'instruction': 'Change one source, run make, and confirm only '
                                'the stale steps fire.'},
                {'instruction': 'make clean && make, and confirm a full '
                                'rebuild.'},
            ],
            'free': 'On this machine: a real Makefile, a dry run, a no-op '
                    'second build, and a rebuild after a source change.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
    ],

    'quiz': [
        {
            'id': 'mfq-graph',
            'type': 'mcq',
            'prompt': 'What does make actually decide?',
            'answer': 'Which targets are stale, and therefore which recipes to run.',
            'distractors': [
                'The order of every line in the Makefile, every time.',
                'Which compiler flags produce the smallest binary.',
                'Whether the source code is correct.',
            ],
            'teach': 'A script runs every line. make runs the lines the timestamps still need.',
        },
        {
            'id': 'mfq-tab',
            'type': 'mcq',
            'prompt': 'make says missing separator. What is the usual cause?',
            'answer': 'A recipe line that starts with spaces instead of a tab.',
            'distractors': [
                'A missing colon on the target line.',
                'A variable that was never set.',
                'A phony target used as a file.',
            ],
            'teach': 'Recipe lines must start with a real tab. Editors that expand tabs cause this.',
        },
        {
            'id': 'mfq-stale',
            'type': 'mcq',
            'prompt': 'When is a target stale?',
            'answer': 'When it is missing, or any dependency is newer than it.',
            'distractors': [
                'When its contents differ from the last build.',
                'When it has not been built in this shell session.',
                'When the Makefile itself is newer than the target.',
            ],
            'teach': 'make compares timestamps. It does not hash the files.',
        },
        {
            'id': 'mfq-auto',
            'type': 'mcq',
            'prompt': 'In a recipe, what is $@ ?',
            'answer': 'The target of the rule make is running.',
            'distractors': [
                'The process id of make, as in the shell.',
                'Every dependency.',
                'The first dependency.',
            ],
            'teach': '$@ is the target, $< the first input, $^ all inputs. make expands them first.',
        },
        {
            'id': 'mfq-phony',
            'type': 'mcq',
            'prompt': 'Why mark clean as .PHONY?',
            'answer': 'So a file named clean cannot make make skip the recipe.',
            'distractors': [
                'So make deletes the Makefile afterwards.',
                'So clean runs before every other target.',
                'So the recipe can use automatic variables.',
            ],
            'teach': 'A file called clean with no dependencies looks up to date. .PHONY means the name is an action.',
        },
        {
            'id': 'mfq-n',
            'type': 'mcq',
            'prompt': 'What does make -n do?',
            'answer': 'Prints the recipes it would run, and runs none of them.',
            'distractors': [
                'Ignores the Makefile and uses defaults.',
                'Runs every recipe even if targets are current.',
                'Limits make to n parallel jobs.',
            ],
            'teach': '-n is the dry run. -B rebuilds everything. -j n is parallel.',
        },
    ],
}
