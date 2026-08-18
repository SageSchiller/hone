"""gdb: a process you can stop.

strace showed the program as a sequence of syscalls. gdb shows it as a
process you can pause, inspect, and step. The same program, one level up:
not "what did it ask the kernel", but "where is it, what is in this
variable, how did it get here".

The habit is: build with -g, start gdb on the binary, put a breakpoint on
main, run, then look around. Everything else in the module is a finer
version of that.

Sandbox-verified where a command file or a batch run writes a log the
trainer can read. An interactive session is honestly self-marked. Scope:
your own programs, built with symbols, not attaching to something you
did not start.
"""

MODULE = {
    'id': 'gdb',
    'title': 'gdb',
    'group': 'Security',
    'blurb': 'Stop a program you built, look at values, walk the stack.',
    'context': 'You are at a gdb prompt on a program you built with -g.',
    'needs': ('gdb',),
    'prereqs': ['linux', 'strace'],
    'adapter': 'sandbox',
    'estimate': '3-4 hours',
    'order': 76,

    'lessons': [
        {
            'id': 'gd-what',
            'title': 'A process you can stop',
            'next': 'gd-start',
            'concept': (
                'gdb is a debugger. It starts a program you built, pauses it, '
                'and lets you look. A breakpoint is an address where the '
                'program will stop. From that pause you print a variable, '
                'walk the stack, step one line, then continue. The program is '
                'still the real program. gdb is a second process that '
                'controls it through ptrace, the same interface strace uses.\n\n'
                'That is the skill that turns "it crashed" or "this value is '
                'wrong" from a guess into a look. printf needs a rebuild and '
                'changes the source. gdb does not. strace tells you which '
                'file the program asked the kernel to open. gdb tells you '
                'what is in this variable and which calls stacked up to get '
                'here. Those are the questions a segfault actually asks, and '
                'they are why the tool is worth an afternoon.\n\n'
                '**It is not printf.** A print in the source is fine until '
                'the bug vanishes when you add it, or the program is not '
                'yours to edit. A breakpoint does not change the source.\n\n'
                '**It is not a replacement for reading the binary.** readelf '
                'and objdump print the map while the file sits still. gdb is '
                'what you do once you want that map to move. You can use gdb '
                'without readelf. You will use it better with a name for main.\n\n'
                'ptrace is also a permission: on many boxes '
                '`/proc/sys/kernel/yama/ptrace_scope` stops you attaching to '
                'a process you did not start. That is why this module stays '
                'on programs you built.\n\n'
                'The next lesson is getting in and getting out, which is the '
                'part that strands people.'
            ),
            'examples': [
                {
                    'label': 'Two views of the same program',
                    'code': ('strace ./hello\n'
                             '  openat(..., "config") = -1 ENOENT\n'
                             '\n'
                             'gdb ./hello\n'
                             '  break main\n'
                             '  run\n'
                             '  print argv[1]'),
                    'note': 'strace answers which file was opened. gdb '
                            'answers what is in argv[1] at the moment of '
                            'the open. That second question is why you learn '
                            'it.',
                },
                {
                    'label': 'What it is not',
                    'code': ('printf debugging   edit, rebuild, rerun\n'
                             'gdb                stop, look, continue\n'
                             '\n'
                             'the binary is the same one either way'),
                    'note': 'Use printf when you own the source and the bug '
                            'is patient. Use gdb when either of those is false.',
                },
            ],
            'misconceptions': [
                'gdb does not rewrite the program. It stops it. The '
                'instructions are the ones you built.',
                'You do not need to know assembly to start. A line of C and '
                'a variable name are enough for the first hour.',
            ],
            'try_it': [
                'If you have a small C file, compile it with gcc -g -o hello '
                'hello.c and leave it. The next lesson starts gdb on it.',
            ],
        },
        {
            'id': 'gd-start',
            'title': 'Getting in, running, getting out',
            'next': 'gd-break',
            'concept': (
                'This lesson is getting in and getting out. gdb will not help '
                'if you cannot start it, cannot leave it, or think Ctrl-C '
                'quit the debugger. That first session is why people bounce '
                'off the tool.\n\n'
                '`gdb ./hello` opens the file and does not run it. The prompt '
                'is `(gdb)`. `run` starts the program. `run arg1 arg2` passes '
                'arguments. `start` is run plus a temporary breakpoint on '
                'main, which is the usual first session. `quit` or `q` leaves '
                'gdb. If the program is still running, gdb asks; `quit` again '
                'or `kill` then `quit` is the way out. Ctrl-C in gdb stops '
                'the *program*, not gdb. That is the opposite of a shell, and '
                'it is the first surprise.\n\n'
                '**Build with `-g`.** `gcc -g -o hello hello.c` writes extra '
                'information so gdb can name lines and variables. Without '
                '`-g`, you still get assembly and raw memory, and you lose '
                'the line numbers this module spends on. A stripped binary '
                'is the same loss, on purpose.\n\n'
                '`gdb -q` skips the license banner. `gdb -batch -ex cmd` '
                'runs commands and exits, which is how a script, and the '
                'challenges here, drive gdb without a prompt.\n\n'
                'Two first-session failures look like gdb is broken. `gdb '
                'hello` without `./` searches PATH, and a file in this '
                'directory is not on PATH, so gdb says it cannot find the '
                'file you can see. `gdb ./hello` on a binary whose '
                'interpreter is missing (wrong architecture, or a broken '
                'INTERP) opens the file and then `run` fails with "No such '
                'file or directory", which is the interpreter, not hello. '
                'The other surprise is a debuginfod prompt asking whether to '
                'download symbols over the network. Answer n, or set '
                '`DEBUGINFOD_URLS` empty, because a trainer that phones out '
                'is not a trainer you hand to a stranger.\n\n'
                'The next lesson is breakpoints: the pause you actually use.'
            ),
            'examples': [
                {
                    'label': 'The first session',
                    'code': ('gcc -g -o hello hello.c\n'
                             'gdb -q ./hello\n'
                             '(gdb) start\n'
                             '(gdb) quit'),
                    'note': 'start runs to main and stops. run would run to '
                            'the end if you set no breakpoint.',
                },
                {
                    'label': 'No prompt, for a script',
                    'code': ('gdb -q -batch \\\n'
                             '    -ex "break main" \\\n'
                             '    -ex run \\\n'
                             '    -ex bt \\\n'
                             '    -ex quit \\\n'
                             '    ./hello'),
                    'note': '-ex is one command. Several -ex flags are a '
                            'session. The output is a log you can save.',
                },
            ],
            'misconceptions': [
                'Ctrl-C inside gdb interrupts the program, not gdb. quit is '
                'how you leave. That is why it feels stuck the first time.',
                'gdb ./hello does not run hello. run does. The file is open '
                'and waiting.',
            ],
            'try_it': [
                'Compile a tiny program with -g, start gdb -q on it, type '
                'start, then quit. Confirm you can leave.',
            ],
        },
        {
            'id': 'gd-break',
            'title': 'Breakpoints: where the pause happens',
            'next': 'gd-step',
            'concept': (
                'A breakpoint is the pause you actually use. Without one, '
                '`run` goes to the end and you see nothing. That is why '
                '`break main` is the first real skill, not a flag to '
                'memorise. It is an address where gdb will stop before the '
                'instruction runs.\n\n'
                '`break main` is the first one to set. `break file.c:12` is a '
                'line. `break function` is a name from the symbol table. '
                '`info break` lists them, with numbers. `delete 1` removes '
                'number 1. `disable 1` keeps it and turns it off. `enable 1` '
                'brings it back.\n\n'
                'A breakpoint on a name you do not have is a silent waste: '
                'gdb says it will set it when the library loads, or says the '
                'function is unknown. `break main` on a stripped binary will '
                'not find main. Stop on `*_start` or on an address you got '
                'from objdump instead.\n\n'
                '`tbreak` is a breakpoint that deletes itself after one hit. '
                '`start` is "tbreak main" plus run. `watch var` stops when '
                'that variable changes, which is slower and worth it when '
                'the bug is a write you cannot see.\n\n'
                'A breakpoint on a line that generated no code is a silent '
                'miss: a comment, a declaration, a line the optimiser '
                'removed. gdb will pick a nearby address or say the line is '
                'out of range. Rebuild with `-O0 -g` before deciding the '
                'tool is wrong. A breakpoint on a name in a library that is '
                'not loaded yet becomes *pending*; it looks set in `info '
                'break` and only becomes real when the `.so` arrives. That '
                'is useful and it is also how `break printf` appears to work '
                'on a file that has not run yet.\n\n'
                'The next lesson is moving after the pause: next, step, '
                'continue, finish.'
            ),
            'examples': [
                {
                    'label': 'Set, list, remove',
                    'code': ('(gdb) break main\n'
                             'Breakpoint 1 at 0x401136: file hello.c, line 4.\n'
                             '(gdb) break hello.c:10\n'
                             '(gdb) info break\n'
                             '(gdb) delete 2'),
                    'note': 'The number is how you talk about the breakpoint '
                            'later. info break is the inventory.',
                },
                {
                    'label': 'When the name is missing',
                    'code': ('(gdb) break main\n'
                             'Function "main" not defined.\n'
                             '\n'
                             'the binary is stripped, or was built without -g\n'
                             'break *0x401136     an address from objdump'),
                    'note': 'The star means "this address", not a name. That '
                            'is the bridge from the elf module.',
                },
            ],
            'misconceptions': [
                'A breakpoint on a line is "before that line runs", not after. '
                'The variables that line is about to write are still old.',
                'break main on a stripped file will not invent the name. The '
                'name is gone. The instructions are not.',
            ],
            'try_it': [
                'In gdb, break main, info break, run, and confirm it stops. '
                'Then delete the breakpoint and run again, and watch it '
                'finish.',
            ],
        },
        {
            'id': 'gd-step',
            'title': 'Stepping: next, step, continue, finish',
            'next': 'gd-stack',
            'concept': (
                'Stepping is how you watch a run without losing the pause. '
                '`next` against `step` is the difference between staying in '
                'your code and vanishing into libc, which is why the pair is '
                'worth learning as a decision, not as synonyms.\n\n'
                '`continue` (or `c`) runs until the next breakpoint, or the '
                'end. `next` (or `n`) runs the current *line* and stops on '
                'the next one, stepping over function calls. `step` (or `s`) '
                'steps into the call. `finish` runs until the current '
                'function returns, and prints what it returned.\n\n'
                'That split is the whole skill. `step` into libc is how a '
                'session vanishes into assembly you did not write. `next` '
                'over a call you trust, `step` into a call you do not. '
                '`finish` is the way back when you stepped too far.\n\n'
                '`nexti` and `stepi` are the same pair, one instruction at a '
                'time. Use them when the source line is a macro or a single '
                'line that is really twenty instructions.\n\n'
                'A program waiting for input is not stuck. It is blocked in a '
                'read. continue will sit there until you give it stdin, or '
                'until you Ctrl-C and land back at the gdb prompt.\n\n'
                '`finish` is not `return`. `finish` lets the function run to '
                'its real return, so destructors and `unlock` still happen. '
                '`return` in gdb forces a return now and can skip that '
                'cleanup, which is a fine experiment and a bad habit in a '
                'program that holds locks. `step` into `printf` or `operator '
                'new` is how a session vanishes into libc++ for twenty '
                'minutes; `finish` is the way home, and `next` is how you '
                'avoid the trip the next time.\n\n'
                'The next lesson is the stack: how you got here, and the '
                'frames above this one.'
            ),
            'examples': [
                {
                    'label': 'Over, into, back out',
                    'code': ('(gdb) next      this line, including any call\n'
                             '(gdb) step      into the call\n'
                             '(gdb) finish    run to the return\n'
                             '(gdb) continue  until the next breakpoint'),
                    'note': 'next is the default walk through your own code. '
                            'step is a decision, not a habit.',
                },
                {
                    'label': 'The session that vanished',
                    'code': ('(gdb) step\n'
                             'printf () at printf.c:...\n'
                             '\n'
                             '(gdb) finish\n'
                             'back in main'),
                    'note': 'You stepped into libc. finish is the way home. '
                            'next would have skipped the trip.',
                },
            ],
            'misconceptions': [
                'step and next are not synonyms. next treats a call as one '
                'line. step does not.',
                'continue is not quit. The program keeps running under gdb '
                'until it hits something or exits.',
            ],
            'try_it': [
                'Break on main, run, next a few lines, then step into one '
                'function you wrote and finish out of it.',
            ],
        },
        {
            'id': 'gd-stack',
            'title': 'The stack: backtrace and frames',
            'next': 'gd-data',
            'concept': (
                'A backtrace is the answer to how this run got here. After a '
                'crash it is the first command, and the reason gdb is better '
                'than staring at a segfault line. Frames let you look at the '
                'caller without rewinding.\n\n'
                'Each call pushes a **frame**: the return '
                'address, the arguments, the locals. `backtrace` (or `bt`) '
                'prints the frames from here up to main.\n\n'
                'Frame 0 is where you stopped. `frame 2` selects that frame '
                'so `print` and `info locals` talk about *that* function, not '
                'the one you broke in. `up` and `down` move one frame. The '
                'program is still paused in frame 0. You are only changing '
                'which frame you inspect.\n\n'
                '`info args` and `info locals` list what gdb still has names '
                'for. Optimised builds lie here: a local can be in a register, '
                'or gone. `-g` plus `-O0` is the honest build. `-O2 -g` is '
                'possible and the locals will disappoint you.\n\n'
                'A crash under gdb is just a stop. `bt` is the first command '
                'after a SIGSEGV. The top frame is where it died. The frames '
                'below are why it was there.\n\n'
                'A missing frame is often a tail call, or `-O2`, not a gdb '
                'bug: the compiler reused the caller\'s frame and there is '
                'nothing left to print. `info locals` saying `<optimized '
                'out>` is the same fact from the other side. Rebuild with '
                '`-O0 -g` when the names matter. Selecting `frame 2` does '
                'not rewind the program, which is why `continue` after a '
                'tour of frames still resumes in frame 0. You were looking, '
                'not moving.\n\n'
                'The next lesson is print: looking at the values those frames '
                'hold.'
            ),
            'examples': [
                {
                    'label': 'A backtrace',
                    'code': ('(gdb) bt\n'
                             '#0  helper (n=3) at hello.c:8\n'
                             '#1  0x40115a in main () at hello.c:15\n'
                             '\n'
                             '(gdb) frame 1\n'
                             '(gdb) info locals'),
                    'note': 'frame 1 is main. The program is still inside '
                            'helper. You are only looking.',
                },
                {
                    'label': 'After a crash',
                    'code': ('Program received signal SIGSEGV, Segmentation '
                             'fault.\n'
                             '(gdb) bt\n'
                             '#0  0x401140 in walk () at walk.c:12\n'
                             '#1  0x401160 in main () at walk.c:20'),
                    'note': 'The signal is the stop. bt is the question. Do '
                            'not quit and rerun until you have the frames.',
                },
            ],
            'misconceptions': [
                'Selecting a frame does not rewind the program. It changes '
                'which names print talks about.',
                'A missing local is often -O2, not a gdb bug. Rebuild with '
                '-O0 -g when you need the names.',
            ],
            'try_it': [
                'Write two functions, break in the inner one, run, and bt. '
                'Then frame 1 and info locals in main.',
            ],
        },
        {
            'id': 'gd-data',
            'title': 'print, examine, and changing a value',
            'next': 'gd-batch',
            'concept': (
                'print is why you stopped. A breakpoint with no look at a '
                'value is just a slower crash. This is how you see what `n` '
                'actually is, and how you test a branch without rebuilding.\n\n'
                '`print expr` (or `p`) evaluates an expression in the current '
                'frame. `print n`, `print *p`, `print s[0]@4` for four '
                'elements. `print /x n` is hex. `print /t n` is binary. The '
                'expression is C, more or less, so `print a+b` works when a '
                'and b are in scope.\n\n'
                '`x` examines raw memory. `x/16xb ptr` is sixteen bytes in '
                'hex. `x/8i $pc` is eight instructions at the program '
                'counter. `x/s ptr` is a string. The format letter is the '
                'same family as xxd: you are looking at bytes, with a count '
                'and a unit.\n\n'
                '`set var n = 5` changes a value and continues with that '
                'value. That is how you test a branch without rebuilding. It '
                'is also how you lie to yourself about the bug. Use it as an '
                'experiment, then go fix the source.\n\n'
                '`display expr` reprints the expression on every stop. '
                '`undisplay` kills it. That is the watch you actually want '
                'while you step.\n\n'
                '`list` prints source around the stop. `info registers` and '
                '`disassemble` are the first look when names are gone. '
                '`watch var` stops on a write, which is slower than a '
                'breakpoint and worth it when the bug is a store you cannot '
                'see.\n\n'
                '`print` on an optimised-out local is `<optimized out>`, not '
                'zero, and treating that as a value is how a session lies. '
                '`x` on a bad pointer is just another SIGSEGV, caught by gdb, '
                'so you get a prompt back rather than a crash; the address '
                'was still wrong. `set var` writes a register or a stack slot '
                'for this run only. It is the right tool for "what if this '
                'branch were taken" and the wrong tool for a fix, because the '
                'next `run` loads the source again.\n\n'
                'The next lesson is batch mode and core files: gdb without a '
                'prompt, and a crash after the fact.'
            ),
            'examples': [
                {
                    'label': 'Names, then bytes',
                    'code': ('(gdb) print n\n'
                             '$1 = 3\n'
                             '(gdb) print /x n\n'
                             '$2 = 0x3\n'
                             '(gdb) x/16xb buf\n'
                             '(gdb) x/s buf'),
                    'note': '$1 is a history value. print $1+1 reuses it. '
                            'That is a convenience, not a variable in the '
                            'program.',
                },
                {
                    'label': 'Change it and continue',
                    'code': ('(gdb) print ready\n'
                             '$3 = 0\n'
                             '(gdb) set var ready = 1\n'
                             '(gdb) continue'),
                    'note': 'The source still says ready = 0. This run does '
                            'not. Rebuild after you have learned what you '
                            'needed.',
                },
            ],
            'misconceptions': [
                'print n shows the current frame\'s n. up first if you meant '
                'the caller\'s n.',
                'set var is not a fix. It is a one-run experiment. The next '
                'run is the source again.',
            ],
            'try_it': [
                'Stop in a function, print a local, print it in hex, then '
                'set var it to something else and continue.',
            ],
        },
        {
            'id': 'gd-batch',
            'title': 'Batch mode, and a core file',
            'concept': (
                'Batch mode is gdb you can put in a script. A core file is '
                'gdb after the process already died. Both are why the tool '
                'is not only an interactive afternoon: you can save a '
                'session, or inspect a crash you were not attached to.\n\n'
                '**Batch mode** is gdb without a conversation. `gdb -q '
                '-batch -ex "break main" -ex run -ex bt -ex quit ./hello` '
                'is a session you can put in a script and save. `-ex` is one '
                'command. Order is the order they run. This is how the '
                'challenges here check a backtrace without taking the '
                'keyboard.\n\n'
                '**A core file** is a snapshot of a process that already '
                'died. `ulimit -c unlimited` then a crash writes `core` or '
                '`core.<pid>`. `gdb ./hello core` opens the program and the '
                'snapshot. You cannot continue. You can bt, print, x. The '
                'bug is frozen. On many boxes core files are off by default, '
                'or systemd puts them in a journal, so "there is no core" is '
                'usually a limit, not a clean crash.\n\n'
                '`layout src` in a capable terminal splits source and '
                'command. TUI can confuse a small screen; `Ctrl-X a` toggles '
                'it off. It is comfort, not a different debugger.\n\n'
                'Two things make a batch session noisy. Pagination waits for '
                'a key, so a script hangs; `set pagination off` first. '
                'debuginfod may ask, or try the network, before any `-ex` '
                'runs; `-iex "set debuginfod enabled off"` is an early '
                'command that happens before the file is loaded, which is '
                'why it is `-iex` and not `-ex`. A command file is the same '
                'session without remembering flag order: one command per '
                'line, then `gdb -q -batch -x cmds.txt ./hello`.\n\n'
                'That is enough to stop a program you built, see how it got '
                'there, and look at the values. Attaching to a process you '
                'did not start is the same tool and a different permission, '
                'and it is not a challenge in this module.'
            ),
            'examples': [
                {
                    'label': 'A session as a command line',
                    'code': ('gdb -q -batch \\\n'
                             '    -ex "break main" \\\n'
                             '    -ex run \\\n'
                             '    -ex "info locals" \\\n'
                             '    -ex quit \\\n'
                             '    --args ./hello one two'),
                    'note': '--args is how you pass program arguments after '
                            'the flags that belong to gdb.',
                },
                {
                    'label': 'After the fact',
                    'code': ('ulimit -c unlimited\n'
                             './hello\n'
                             '  Segmentation fault (core dumped)\n'
                             'gdb -q ./hello core\n'
                             '(gdb) bt'),
                    'note': 'If there is no core, run ulimit -c and check '
                            'where the system writes dumps before assuming '
                            'the program did not crash.',
                },
            ],
            'misconceptions': [
                'A core file is not a replay. You cannot continue or step. '
                'You can only look.',
                'batch mode is still the real gdb. The same commands work. '
                'There is just no prompt to save you from a typo.',
            ],
            'try_it': [
                'Drive your hello program with gdb -batch and a break on '
                'main, and save the output. Then, if your box will write a '
                'core, crash a tiny program and open the core.',
            ],
        },
    ],

    'drills': [
        {'id': 'gdd-start', 'type': 'command',
         'answer': 'gdb -q ./hello',
         'prompt': 'Start gdb on ./hello with no license banner.',
         'teach': '-q skips the banner. The program is loaded, not running.'},
        {'id': 'gdd-quit', 'type': 'command',
         'answer': 'quit',
         'accepts': ['q'],
         'prompt': 'Leave gdb.',
         'teach': 'Ctrl-C stops the program, not gdb. quit leaves.'},
        {'id': 'gdd-run', 'type': 'command',
         'answer': 'run',
         'accepts': ['r'],
         'prompt': 'Start the loaded program from inside gdb.',
         'teach': 'run starts it. start is run plus a temporary break on main.'},
        {'id': 'gdd-startcmd', 'type': 'command',
         'answer': 'start',
         'prompt': 'Run the program and stop at main.',
         'teach': 'start is tbreak main, then run. The usual first session.'},
        {'id': 'gdd-break', 'type': 'command',
         'answer': 'break main',
         'accepts': ['b main'],
         'prompt': 'Stop when main is about to run.',
         'teach': 'A name from the symbol table. Needs -g, and fails if stripped.'},
        {'id': 'gdd-info-b', 'type': 'command',
         'answer': 'info break',
         'accepts': ['i b', 'info breakpoints'],
         'prompt': 'List the breakpoints that are set.',
         'teach': 'The numbers in this list are what delete and disable take.'},
        {'id': 'gdd-continue', 'type': 'command',
         'answer': 'continue',
         'accepts': ['c'],
         'prompt': 'Resume until the next breakpoint or the end.',
         'teach': 'continue is not quit. The process keeps running under gdb.'},
        {'id': 'gdd-next', 'type': 'command',
         'answer': 'next',
         'accepts': ['n'],
         'prompt': 'Run the current line, stepping over calls.',
         'teach': 'next treats a call as one line. step enters it.'},
        {'id': 'gdd-step', 'type': 'command',
         'answer': 'step',
         'accepts': ['s'],
         'prompt': 'Run the next line, entering any call.',
         'teach': 'step into libc is how a session vanishes. finish comes back.'},
        {'id': 'gdd-finish', 'type': 'command',
         'answer': 'finish',
         'prompt': 'Run until the current function returns.',
         'teach': 'The way home after an accidental step into a library.'},
        {'id': 'gdd-bt', 'type': 'command',
         'answer': 'backtrace',
         'accepts': ['bt'],
         'prompt': 'Print the call stack from here to main.',
         'teach': 'Frame 0 is the stop. The frames below are how you got here.'},
        {'id': 'gdd-list', 'type': 'command',
         'answer': 'list',
         'accepts': ['l'],
         'prompt': 'Print source around the current stop.',
         'teach': 'list is the first look when you have -g. disassemble when you do not.'},
        {'id': 'gdd-watch', 'type': 'command',
         'answer': 'watch n',
         'prompt': 'Stop when the variable n is written.',
         'teach': 'Slower than a breakpoint. Worth it when the bug is a store you cannot see.'},
        {'id': 'gdd-x', 'type': 'command',
         'answer': 'x/16xb ptr',
         'prompt': 'Examine sixteen bytes at ptr, in hex.',
         'teach': 'x is raw memory. print is a named value in this frame.'},
        {'id': 'gdd-print', 'type': 'command',
         'answer': 'print n',
         'accepts': ['p n'],
         'prompt': 'Print the value of n in the current frame.',
         'teach': 'The expression is C. Add /x for hex.'},
        {'id': 'gdd-batch', 'type': 'command',
         'answer': 'gdb -q -batch -ex run -ex quit ./hello',
         'prompt': 'Run ./hello under gdb with no prompt, then leave.',
         'teach': '-ex is one command. batch exits when the list is done.'},
        {'id': 'gdd-gccg', 'type': 'command',
         'answer': 'gcc -g -o hello hello.c',
         'prompt': 'Compile hello.c with debug symbols to ./hello.',
         'teach': '-g writes the names gdb needs. Without it you get assembly.'},
    ],

    'challenges': [
        {
            'id': 'gdc-compile',
            'title': 'Build with symbols, then break on main',
            'goal': 'A debugger without -g is a listing. Build a tiny '
                    'program the way this module expects, then write the '
                    'batch session that stops on main.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'env': {'DEBUGINFOD_URLS': ''},
                'tree': {
                    'hello.c': (
                        '#include <stdio.h>\n'
                        'int main(void) {\n'
                        '    puts("hi");\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                },
            },
            'solution': {
                'shell': (
                    'gcc -g -o hello hello.c && '
                    'gdb -q -batch -iex "set debuginfod enabled off" '
                    '-ex "break main" -ex run -ex bt -ex quit '
                    './hello > session.txt'
                ),
            },
            'steps': [
                {'instruction': 'Compile hello.c with debug symbols to ./hello.',
                 'hint': 'gcc -g -o hello hello.c'},
                {'instruction': 'Run gdb in batch: break main, run, bt, quit. '
                                'Save the output as session.txt.',
                 'hint': 'gdb -q -batch -iex "set debuginfod enabled off" '
                         '-ex "break main" -ex run -ex bt '
                         '-ex quit ./hello > session.txt'},
            ],
            'free': 'Build hello with -g and write session.txt from a gdb '
                    'batch session that breaks on main and prints a backtrace.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'is_file': ['hello'],
                    'file_contains': {
                        'session.txt': ['Breakpoint', 'main'],
                    },
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'gdc-script',
            'title': 'Write the commands, not the session',
            'goal': 'A command file is the same session without remembering '
                    '-ex order. gdb reads it with -x.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {}},
            'solution': {
                'shell': (
                    "printf '%s\\n' 'break main' 'run' 'backtrace' 'quit' "
                    '> cmds.txt'
                ),
            },
            'steps': [
                {'instruction': 'Write cmds.txt with four gdb commands: '
                                'break main, run, backtrace, quit.',
                 'hint': 'one command per line'},
            ],
            'free': 'Write cmds.txt that gdb -x could use to stop on main '
                    'and print a backtrace.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_contains': {
                        'cmds.txt': ['break main', 'run', 'quit'],
                    },
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'gdc-live',
            'title': 'Drive a live session yourself',
            'goal': 'Batch mode is a check. The prompt is the skill. This '
                    'one is yours, because a conversation is not a file.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'Compile a small program with gcc -g.'},
                {'instruction': 'gdb -q ./prog, start, next a few lines, '
                                'print a local, bt, quit.'},
                {'instruction': 'Step into a function on purpose, then '
                                'finish back out.'},
                {'instruction': 'Set a breakpoint on a line, continue to it, '
                                'and info break.'},
            ],
            'free': 'On this machine: a real gdb session with start, next, '
                    'step, finish, print and bt.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
    ],

    'quiz': [
        {
            'id': 'gdq-ctrlc',
            'type': 'mcq',
            'prompt': 'You press Ctrl-C at a (gdb) prompt while the program is running. What stops?',
            'answer': 'The program. gdb stays, and you get a prompt again.',
            'distractors': [
                'gdb exits, like a shell.',
                'Both gdb and the program exit.',
                'Nothing; Ctrl-C is ignored inside gdb.',
            ],
            'teach': 'Ctrl-C is for the inferior. quit is for gdb.',
        },
        {
            'id': 'gdq-next',
            'type': 'mcq',
            'prompt': 'What is the difference between next and step?',
            'answer': 'next treats a call as one line; step enters the call.',
            'distractors': [
                'step skips loops; next does not.',
                'next is one instruction; step is one line.',
                'They are aliases.',
            ],
            'teach': 'step into libc is how a session vanishes. finish comes back.',
        },
        {
            'id': 'gdq-g',
            'type': 'mcq',
            'prompt': 'What does gcc -g add that gdb wants?',
            'answer': 'Debug symbols: names for lines, functions and locals.',
            'distractors': [
                'A second copy of the source inside the binary.',
                'A guarantee the program will not be optimised.',
                'Permission for gdb to attach.',
            ],
            'teach': 'Without -g you still get assembly and memory. You lose the names.',
        },
        {
            'id': 'gdq-frame',
            'type': 'mcq',
            'prompt': 'You type frame 2. What changed?',
            'answer': 'Which frame print and info locals talk about. The program is still paused where it stopped.',
            'distractors': [
                'The program rewound to that function.',
                'The next continue will resume in that frame.',
                'Breakpoint 2 is now the only one enabled.',
            ],
            'teach': 'Selecting a frame is looking, not rewinding.',
        },
        {
            'id': 'gdq-core',
            'type': 'mcq',
            'prompt': 'What can you do with gdb ./prog core that you cannot do with a live process?',
            'answer': 'Nothing extra: a core is a frozen look. You cannot continue or step.',
            'distractors': [
                'Replay the crash one instruction at a time.',
                'Restart the program from the crashing line.',
                'Edit the source and resume.',
            ],
            'teach': 'bt, print and x still work. run and continue do not.',
        },
        {
            'id': 'gdq-stripped',
            'type': 'mcq',
            'prompt': 'break main fails on a stripped binary. Why?',
            'answer': 'The name main is gone from the symbol table. The instructions are still there.',
            'distractors': [
                'Stripped binaries cannot be debugged at all.',
                'gdb refuses to open a stripped file.',
                'main was inlined into the ELF header.',
            ],
            'teach': 'Use an address from objdump, or rebuild with -g and do not strip.',
        },
    ],
}
