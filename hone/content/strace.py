"""strace: watching a program talk to the kernel.

The plan's own skip list named strace the strongest candidate for a sixteenth
module, and the boundary rule agrees: learning it changes how you think. Before
strace, a program that fails is a black box with an unhelpful error message.
After it, a program is a sequence of requests to the kernel, and the failure is
a line in that sequence with an errno on the end.

That reframe is the module. Everything a process does that touches the world
outside its own memory, every file it opens, every byte it reads, every socket,
every child, every signal, is a syscall, and a syscall is observable. "It says
config not found but I can see the file" stops being a mystery and becomes a
question with a mechanical answer: trace the openat calls and read which path
it actually asked for.

**Verification.** The sandbox adapter, because everything here produces a
trace file and a trace file is a file. That makes this one of the better
verified modules in the roster: you run the real strace, on a real process, and
the trainer reads the real output back.

**Scope.** Your own processes. Attaching to something you did not start is a
one-line lesson about `ptrace_scope` and root, not a challenge, because the
trainer will not ask you to escalate privileges to pass a drill.
"""

MODULE = {
    'id': 'strace',
    'title': 'strace',
    'group': 'Security',
    'blurb': 'Syscalls, filtering, following children, and why it cannot find the file.',
    'context': 'You are at a shell prompt on Linux, tracing processes you started yourself.',
    'needs': ['strace'],
    'prereqs': ['linux', 'linuxadv'],
    'adapter': 'sandbox',
    'estimate': '3-4 hours',
    'order': 71,

    'lessons': [
        {
            'id': 'st-model',
            'title': 'Everything interesting is a syscall',
            'concept':
                'A process can do two kinds of thing. It can compute, which '
                'happens entirely inside its own memory and which strace '
                'cannot see and does not care about. Or it can ask the kernel '
                'for something: open a file, read bytes, create a process, '
                'send a packet, allocate memory, exit. That request is a '
                'syscall, and it is a boundary the process cannot cross '
                'without being observed.\n\n'
                'This is why strace is the right tool for a whole class of '
                'problem. Anything about the outside world, files, sockets, '
                'permissions, other processes, is on the far side of that '
                'boundary. If the question is "what did it actually try to '
                'do", the answer is in the syscall list, and no amount of '
                'reading the program logs will be as direct.\n\n'
                'The cost is that strace is not free. It stops the traced '
                'process at every syscall, so a syscall-heavy program can run '
                'an order of magnitude slower under it. That is fine for '
                'diagnosis and misleading for benchmarking, and it is why '
                'timing questions get -c rather than a stopwatch.\n\n'
                'What "stops the process" means is ptrace: the kernel pauses '
                'the program on the way into each syscall and again on the '
                'way out, and strace prints what it sees in between. That is '
                'why the first dozen lines of `strace ls` are the dynamic '
                'loader opening `ld-linux` and `libc`, before `main` runs at '
                'all. People scroll past those looking for their program and '
                'miss that the failure already happened: a missing `.so` is '
                'an openat ENOENT in that prologue, not later.\n\n'
                'The next lesson is how to read a line of that list, '
                'because a syscall you cannot parse is a boundary you '
                'still cannot see.',
            'examples': [
                {
                    'label': 'Stopping a trace you attached to',
                    'code': 'strace ./prog        ends when prog does\nstrace -p 1234       runs until you stop it\n\nCtrl-C               detach and stop tracing\n\nthe traced process keeps running,\nwhich is the whole point of -p',
                    'note': 'Ctrl-C on an attached trace detaches cleanly and leaves the target alive. That is worth knowing before you attach to something in production for the first time.',
                },
                {'label': 'The whole tool, in one command',
                 'code': 'strace ls',
                 'note': 'Every syscall ls makes, in order, on stderr. Start '
                         'here and be overwhelmed once.'},
                {'label': 'Somewhere you can read it',
                 'code': 'strace -o trace.txt ls',
                 'note': 'Output goes to stderr by default, which is why '
                         'piping to less needs 2>&1 and -o does not.'},
            ],
            'misconceptions': [
                'strace does not show function calls inside the program. Only '
                'the requests it makes to the kernel. ltrace is the one for '
                'library calls.',
                'The output going missing when you pipe it is not a bug. It '
                'is on stderr, and -o is the fix.',
                'A program that does nothing under strace is not necessarily '
                'stuck. It may be computing, which is invisible here.',
            ],
            'try_it': [
                'Run strace ls and scroll to the top. The first dozen lines '
                'are the dynamic loader, before your program runs at all.',
                'Run strace -o t.txt ls and count the lines. Then count them '
                'for something bigger.',
            ],
            'next': 'st-reading',
        },
        {
            'id': 'st-reading',
            'title': 'Reading a line of output',
            'concept':
                'A strace line is how you read the name, the arguments, and '
                'the return of one syscall. That is why a -1 with ENOENT '
                'names the exact path that was missing, not the path you '
                'assumed.\n\n'
                'openat(AT_FDCWD, "/etc/hosts", O_RDONLY|O_CLOEXEC) = 3 says '
                'a file was opened relative to the current directory, read '
                'only, and got file descriptor 3. The same call ending in -1 '
                'ENOENT (No such file or directory) says the path is not '
                'there, and it tells you the exact path that was tried, which '
                'is usually not the path you assumed.\n\n'
                'Strings are truncated to 32 characters by default and marked '
                'with a trailing ellipsis. That default has hidden the answer '
                'from more people than any other, so -s is a flag worth '
                'reaching for early. Structures are abbreviated too, and -v '
                'prints them in full.\n\n'
                'Unfinished and resumed lines appear when tracing more than '
                'one process: a syscall that blocks is printed as unfinished, '
                'other processes get their turn, and the resumed half appears '
                'later with the return value.\n\n'
                'The path in the argument is the whole diagnosis. '
                '`openat(AT_FDCWD, "conf/app.cfg", ...)` means relative to '
                'the working directory at that moment, not relative to the '
                'binary, not relative to `$HOME`. A program started from the '
                'wrong directory will ENOENT a file that is sitting right '
                'next to it. `AT_FDCWD` is that working directory. A numeric '
                'first argument is a directory fd from an earlier open, and '
                '`-y` will name it so you do not have to walk the trace by '
                'hand.',
            'examples': [
                {'label': 'A success and a failure, side by side',
                 'code': 'openat(AT_FDCWD, "/etc/hosts", O_RDONLY) = 3\n'
                         'openat(AT_FDCWD, "/etc/hots", O_RDONLY) = -1 ENOENT '
                         '(No such file or directory)',
                 'note': 'The errno name is the diagnosis. ENOENT, EACCES and '
                         'EPERM answer three different questions.'},
                {'label': 'Stop truncating the interesting part',
                 'code': 'strace -s 2000 -e trace=write curl -s example.com',
                 'note': 'The default 32 characters hides most request '
                         'bodies and most config file contents.'},
                {'label': 'Show which file a descriptor is',
                 'code': 'strace -y -e trace=read,write cat note.txt',
                 'note': '-y annotates every fd with its path, so read(3, ...) '
                         'becomes read(3</home/you/note.txt>, ...).'},
            ],
            'misconceptions': [
                'A trailing ellipsis in a string is strace truncating at 32 '
                'characters, not the program sending a short buffer.',
                'ENOENT on a path that exists usually means a different path '
                'was tried. Read the argument, not your assumption.',
                'EACCES and EPERM are not the same. EACCES is permission on '
                'the object, EPERM is the operation not being allowed to you.',
            ],
            'try_it': [
                'Trace something that reads a config file and find the exact '
                'openat line for it.',
                'Run the same trace with -s 200 and see what the default was '
                'hiding.',
            ],
            'next': 'st-filter',
        },
        {
            'id': 'st-filter',
            'title': 'Filtering, which is what makes it usable',
            'concept':
                'An unfiltered trace of anything real is thousands of lines, '
                'most of them memory mapping and dynamic linking. The tool '
                'only becomes useful once you ask a narrower question, and '
                '-e is how you ask it.\n\n'
                '-e trace= takes a list of syscall names, or a class prefixed '
                'with a percent sign. The classes are the ones you want most '
                'of the time: %file for anything taking a filename, %process '
                'for fork, exec and exit, %network for sockets, %signal, '
                '%memory, %desc for file descriptor operations, %ipc.\n\n'
                '-e status= filters by outcome, and -e status=failed is the '
                'single highest value filter in the tool. Almost every '
                'question of the form "why did it not work" is answered by '
                'the failed syscalls alone, and there are usually about six '
                'of them in a trace of ten thousand lines.\n\n'
                '-e signal= selects which signals are reported, and -e '
                'inject= is the sharp one: it makes a chosen syscall fail on '
                'purpose, which turns strace from an observation tool into a '
                'fault injection tool for testing error handling.\n\n'
                'The trap with `-e status=failed` is the successful call that '
                'made the failure inevitable. A program chdirs to the wrong '
                'place and then fails to open `./config`: the failed open is '
                'what you see, the chdir is what you needed. Start with '
                'failures to find the errno, then widen to `%file` around '
                'that timestamp to see the setup. `-e` never makes the '
                'program faster. strace still stops it at every syscall and '
                'then throws away the lines you did not ask for.',
            'examples': [
                {'label': 'Only the file operations',
                 'code': 'strace -e trace=%file ls',
                 'note': '%file is every syscall that takes a filename '
                         'argument. The usual starting filter.'},
                {'label': 'Only what failed',
                 'code': 'strace -e status=failed -o fails.txt myprogram',
                 'note': 'The most valuable six lines in the trace, with the '
                         'ten thousand boring ones removed.'},
                {'label': 'Only the network',
                 'code': 'strace -f -e trace=%network curl -s example.com',
                 'note': 'socket, connect, sendto, recvfrom. Shows where it '
                         'connected even when the program will not say.'},
                {'label': 'Make it fail on purpose',
                 'code': 'strace -e inject=openat:error=EACCES myprogram',
                 'note': 'Fault injection. Tests the error path you can never '
                         'reproduce otherwise.'},
                # -q, -i and -u were all drilled and none of them appeared
                # anywhere in seven lessons.
                {'label': 'Three small flags that earn their place',
                 'code': ('strace -q myprogram         drop the attach and\n'
                          '                            exit chatter\n'
                          'strace -i myprogram         show the instruction\n'
                          '                            pointer per call\n'
                          'sudo strace -u nobody prog  run it as another user'),
                 'note': '-q is for when you are diffing two traces and the '
                         'preamble keeps changing. -i tells you where in the '
                         'program the call came from. -u needs root to drop '
                         'to someone else, which is the point of it.'},
                {'label': 'Why -u exists at all',
                 'code': ('sudo strace -u nobody ./deploy.sh\n'
                          '\n'
                          'reproduces "works for me, fails for the\n'
                          'service account" without logging in as it'),
                 'note': 'Half of all permission bugs are a program that has '
                         'only ever been run by someone with more rights than '
                         'the thing that will run it in production.'},
            ],
            'misconceptions': [
                '-e trace=file is not the same as -e trace=%file in older '
                'versions. The percent form is the documented one.',
                'Filtering does not make the program run faster. strace still '
                'stops it at every syscall and then discards the ones you did '
                'not ask for.',
                '-e status=failed hides successful calls, including the '
                'successful call that made the later failure inevitable.',
            ],
            'try_it': [
                'Trace a command with -e trace=%file, then with -e '
                'status=failed, and compare the line counts.',
                'Use -e inject to make a program see a permission error, and '
                'see whether it handles it well.',
            ],
            'next': 'st-follow',
        },
        {
            'id': 'st-follow',
            'title': 'Children, threads, and attaching',
            'concept':
                '`-f` is how you keep watching after a process forks, and it '
                'prefixes every line with the pid that made the call. That '
                'is why a shell-script trace without it ends at clone and '
                'shows none of the work.\n\n'
                'That prefix is what makes an '
                'interleaved trace readable, and it is why -f and -o together '
                'are the normal way to trace anything real.\n\n'
                '-ff goes further, and only makes sense with -o: instead of '
                'one interleaved file it writes trace.PID per process, which '
                'is far easier to read when a dozen processes are involved.\n\n'
                '-p attaches to a process that is already running, which is '
                'how you diagnose something already stuck. Detaching with '
                'Ctrl-C leaves the process running. On most distributions '
                'attaching to a process you did not start requires root or a '
                'relaxed /proc/sys/kernel/yama/ptrace_scope, which is a '
                'hardening setting rather than a bug.\n\n'
                'An interleaved `-f` trace without reading the pid column '
                'looks like one confused program. Two children open the same '
                'path, one succeeds and one gets EACCES, and the lines sit '
                'next to each other as if a single process contradicted '
                'itself. The number at the start of the line is which child. '
                '`-ff` splits that into files so the contradiction goes away. '
                'The attach failure is different: `Operation not permitted` '
                'on `-p` is almost always `ptrace_scope`, not a broken '
                'strace, and it is policy doing its job.\n\n'
                'Following and attaching answers who did it. The next '
                'lesson is where the time went, which is a different '
                'question and a different mode.',
            'examples': [
                {'label': 'Follow every child',
                 'code': 'strace -f -o trace.txt ./deploy.sh',
                 'note': 'Without -f, a script trace ends at the first clone '
                         'and tells you nothing.'},
                {'label': 'One file per process',
                 'code': 'strace -ff -o run ./server',
                 'note': 'Writes run.1234, run.1235 and so on. The readable '
                         'option once several processes are involved.'},
                {'label': 'Attach to something already stuck',
                 'code': 'sudo strace -p 4242',
                 'note': 'Ctrl-C detaches and leaves it running. Often the '
                         'only way to see what a hung daemon is waiting on.'},
                {'label': 'Attach to every thread of a process',
                 'code': 'sudo strace -f -p 4242',
                 'note': '-f applies to threads as well as forks.'},
            ],
            'misconceptions': [
                'A trace that stops at clone is not a crash. It is the '
                'default single-process behaviour, and -f is the fix.',
                'Detaching with Ctrl-C does not kill the traced process, '
                'though killing strace with SIGKILL can leave it stopped.',
                'ptrace_scope refusing to let you attach is a security '
                'setting doing its job, not a broken strace.',
            ],
            'try_it': [
                'Trace a shell script without -f, then with it, and compare '
                'what you learn.',
                'Start sleep 60 in the background and attach to it. Read what '
                'it is blocked in.',
            ],
            'next': 'st-timing',
        },
        {
            'id': 'st-timing',
            'title': 'Counting and timing: where the time went',
            'concept':
                '`-c` is how you get a summary of which syscalls took the '
                'time, instead of a line per call. That is why a nine-second '
                'program usually has its answer in the top row of that '
                'table.\n\n'
                '-c suppresses the per-line output entirely and prints a '
                'summary table when the process exits: calls, errors, time, '
                'and time per call, sorted by time. For "this program takes '
                'nine seconds and I do not know why", that table is usually '
                'the whole answer, because the top line is either a syscall '
                'you did not expect to be there or a count you did not expect '
                'to be that large.\n\n'
                '-w changes what is measured from time inside the kernel to '
                'wall clock time, which is what you want when the program is '
                'waiting rather than working. -C prints both the summary and '
                'the regular output.\n\n'
                'For per-line timing, -T appends the duration of each call, '
                '-tt puts a wall clock timestamp with microseconds at the '
                'front, and -r prints time relative to the previous call. A '
                'long -T on a read is a program waiting for something else, '
                'and that is a different problem from a million fast calls.\n\n'
                'The table under `-c` is empty until the process exits, so it '
                'is the wrong mode for a hang. Attach with `-p` and `-T` '
                'instead, and the blocked call is the last line, sitting '
                'there with no return. A program that sleeps for ten seconds '
                'shows almost nothing in the seconds column of a plain `-c`, '
                'because that column is time inside the kernel, not time on '
                'the clock. Add `-w` and the nanosleep line takes the ten '
                'seconds. The absolute numbers are inflated by the trace '
                'itself; the ranking is still the answer.',
            'examples': [
                {'label': 'Where did the time go',
                 'code': 'strace -c -o counts.txt ./slow-thing',
                 'note': 'A summary table sorted by time. Read the top line '
                         'and the calls column together.'},
                {'label': 'Count wall clock, not kernel time',
                 'code': 'strace -c -w ./slow-thing',
                 'note': 'The right measure when the program is blocked '
                         'waiting rather than busy in the kernel.'},
                {'label': 'How long did each call take',
                 'code': 'strace -T -e trace=read,write ./thing',
                 'note': 'Duration in angle brackets at the end of each line.'},
                {'label': 'When did each call happen',
                 'code': 'strace -tt -f -o trace.txt ./thing',
                 'note': 'Microsecond timestamps, which is how you line a '
                         'trace up against a log file.'},
            ],
            'misconceptions': [
                'The seconds column under -c is time in the kernel, not '
                'elapsed time, unless you add -w. A program sleeping shows '
                'almost no time either way.',
                'strace slows the program down substantially, so the absolute '
                'numbers are not a benchmark. The proportions are still '
                'informative.',
                '-c prints nothing until the process exits, so it is no use '
                'on something you have to kill.',
            ],
            'try_it': [
                'Run strace -c on a command that reads many small files and '
                'read the top of the table.',
                'Compare -c and -c -w on something that sleeps.',
            ],
            'next': 'st-cases',
        },
        {
            'id': 'st-cases',
            'title': 'The four questions strace answers best',
            'concept':
                'In practice almost every real use is one of four questions, '
                'and each has a standard command.\n\n'
                '**Which file did it actually look for?** The program says '
                'config not found and you can see the file. Trace the file '
                'calls and read the failed paths: nine times in ten it looked '
                'somewhere else, in the wrong working directory, or under a '
                'name with a different case.\n\n'
                '**Why is permission denied?** EACCES on a path names the '
                'object; a failed setuid or a capability check names the '
                'operation. The errno distinguishes them and the error message '
                'usually does not.\n\n'
                '**What did it talk to?** %network shows the connect calls, '
                'and with -yy the addresses are annotated, so a program that '
                'will not tell you where it phones home tells strace.\n\n'
                '**Why is it slow, or stuck?** -c for slow, -p for stuck. A '
                'hung process attached to shows the syscall it is blocked in, '
                'which is nearly always a read, a futex or a poll, and each '
                'of those means something different.\n\n'
                'A long run of ENOENT is not a broken program. It is a search '
                'path: `/etc/app/app.cfg`, then `~/.config/app.cfg`, then '
                '`./app.cfg`, each failing until one hits. That list, in '
                'order, is the configuration the author actually wrote, and '
                'it is often not the one in the man page. For a hang, the '
                'blocked syscall is the diagnosis. `read` means a peer or a '
                'file that has not sent data. `poll` or `select` means it is '
                'waiting on several fds. `futex` means another thread holds '
                'a lock, so the answer is in a different pid and `-f` is '
                'required.',
            'examples': [
                {'label': 'Which config did it really read',
                 'code': 'strace -f -e trace=%file -o t.txt myprogram; '
                         'grep -E "ENOENT|\\.conf" t.txt',
                 'note': 'The failed opens are the search path, in order. '
                         'That list is the answer.'},
                {'label': 'Where does it connect',
                 'code': 'strace -f -yy -e trace=%network -o net.txt ./client',
                 'note': '-yy annotates socket descriptors with the address, '
                         'so connect lines are readable without decoding.'},
                {'label': 'What is this hung process waiting on',
                 'code': 'sudo strace -p $(pgrep -f myservice)',
                 'note': 'One line, repeated or blocked, tells you whether it '
                         'is waiting on a lock, a peer or a disk.'},
            ],
            'misconceptions': [
                'A long list of ENOENT is usually normal. A search path is '
                'implemented as a series of failed opens.',
                'Seeing connect to an address does not prove data was sent. '
                'Check for the write or sendto that follows.',
                'A process blocked in futex is waiting on another thread, so '
                'the answer is in a different pid.',
            ],
            'try_it': [
                'Break a program by moving its config, and find the exact '
                'path it wanted using nothing but the trace.',
                'Trace something that resolves a hostname and identify every '
                'file the resolver reads.',
            ],
            'next': 'st-limits',
        },
        {
            'id': 'st-limits',
            'title': 'What strace cannot see, and what to use instead',
            'concept':
                'strace cannot see anything that is not a syscall. That is '
                'why library calls, internal computation, and work that '
                'finished before you attached all need a different look.\n\n'
                'Library calls that never reach the kernel are invisible; '
                'ltrace is the equivalent for those, and it is far less '
                'reliable on modern binaries. Anything a program computes '
                'internally, including all the interesting cryptography, is '
                'invisible.\n\n'
                'It also cannot see what happened before you attached, which '
                'is why -p answers "what is it doing now" and never "what did '
                'it do at startup". Restart under strace for that.\n\n'
                'The overhead is real and occasionally decisive: a program '
                'with a timing-sensitive protocol may behave differently under '
                'trace, which is the tracing equivalent of a heisenbug. When '
                'that bites, the modern answer is eBPF tooling, bpftrace and '
                'the bcc scripts, which hook the same events with a fraction '
                'of the cost and can watch every process on the machine at '
                'once instead of one.\n\n'
                'And in a container, strace needs the right capability. '
                'SYS_PTRACE is often dropped by default, which produces a '
                'permission error that looks like a bug and is a policy.\n\n'
                'The heisenbug is a timeout that only happens under strace. '
                'A protocol that expects a reply in 50ms will miss it when '
                'every syscall is paused for printing, and the program takes '
                'the error path you came to investigate, for a new reason. '
                'Inside a container the refusal is usually `Operation not '
                'permitted` with no mention of policy: add `SYS_PTRACE` or '
                'run the trace from the host against the container\'s pid.',
            'examples': [
                {'label': 'Library calls, not syscalls',
                 'code': 'ltrace ./program',
                 'note': 'The sibling tool. Useful, and much more fragile on '
                         'stripped or statically linked binaries.'},
                {'label': 'The low overhead modern option',
                 'code': 'sudo bpftrace -e '
                         '\'tracepoint:syscalls:sys_enter_openat '
                         '{ printf("%s\\n", str(args->filename)); }\'',
                 'note': 'Watches every process at once, at a cost strace '
                         'cannot match.'},
                {'label': 'Inside a container',
                 'code': 'docker run --cap-add=SYS_PTRACE ...',
                 'note': 'Without the capability, strace fails with a '
                         'permission error that is policy rather than a bug.'},
            ],
            'misconceptions': [
                'strace showing nothing does not mean the program is idle. It '
                'may be busy in userspace, where there is nothing to show.',
                'Attaching late and seeing no config reads does not mean it '
                'read no config. It read them before you attached.',
                'ltrace is not simply "strace for functions". It is far more '
                'easily defeated by how the binary was built.',
            ],
            'try_it': [
                'Trace a program that does heavy computation and note how few '
                'syscalls appear.',
                'Try attaching to a process inside a container and read the '
                'error you get.',
            ],
            'next': None,
        },
    ],

    'drills': [
        {'id': 'std-basic', 'type': 'command',
         'prompt': 'Trace every syscall that ls makes.',
         'answer': 'strace ls',
         'teach': 'Output goes to stderr, which is why it vanishes when you '
                  'pipe stdout somewhere.'},
        {'id': 'std-out', 'type': 'command',
         'prompt': 'Trace ls and write the trace to trace.txt.',
         'answer': 'strace -o trace.txt ls',
         'teach': '-o keeps the trace separate from the program output, and '
                  'saves you writing 2>&1 every time.'},
        {'id': 'std-follow', 'type': 'command',
         'prompt': 'Trace deploy.sh including everything it forks.',
         'answer': 'strace -f ./deploy.sh',
         'teach': 'Without -f the trace stops at the first clone, which for a '
                  'shell script means it tells you nothing.'},
        {'id': 'std-ff', 'type': 'command',
         'prompt': 'Trace ./server writing one file per process, named run.',
         'answer': 'strace -ff -o run ./server',
         'teach': '-ff only means anything with -o. You get run.PID per '
                  'process instead of one interleaved file.'},
        {'id': 'std-attach', 'type': 'command',
         'prompt': 'Attach to the already running process with pid 4242.',
         'answer': 'sudo strace -p 4242',
         'teach': 'Ctrl-C detaches and leaves it running. Attaching to '
                  'something you did not start usually needs root.'},
        {'id': 'std-attach-threads', 'type': 'command',
         'prompt': 'Attach to pid 4242 and every thread it has.',
         'answer': 'sudo strace -f -p 4242',
         'teach': '-f covers threads as well as forks, which matters for '
                  'anything that blocks in one thread only.'},
        {'id': 'std-file-class', 'type': 'command',
         'prompt': 'Trace only the syscalls that take a filename, for ls.',
         'answer': 'strace -e trace=%file ls',
         'teach': 'The percent classes are the usual starting filters: %file, '
                  '%process, %network, %signal, %memory, %desc.'},
        {'id': 'std-openat', 'type': 'command',
         'prompt': 'Trace only the openat calls made by cat note.txt.',
         'answer': 'strace -e trace=openat cat note.txt',
         'teach': 'Naming syscalls directly is the narrow version of a class '
                  'filter, and openat is the one you want most often.'},
        {'id': 'std-network', 'type': 'command',
         'prompt': 'Trace the network syscalls of curl and everything it forks.',
         'answer': 'strace -f -e trace=%network curl',
         'teach': 'socket, connect, sendto, recvfrom. Shows where a program '
                  'connected even when it will not say.'},
        {'id': 'std-process', 'type': 'command',
         'prompt': 'Trace only the process syscalls of ./deploy.sh.',
         'answer': 'strace -e trace=%process ./deploy.sh',
         'teach': '%process is fork, exec, wait and exit: the shape of what '
                  'ran, without the file noise.'},
        {'id': 'std-failed', 'type': 'command',
         'prompt': 'Trace only the syscalls that failed in myprogram.',
         'answer': 'strace -e status=failed myprogram',
         'teach': 'Usually about six lines out of ten thousand, and usually '
                  'the answer to "why did it not work".'},
        {'id': 'std-inject', 'type': 'command',
         'prompt': 'Make every openat in myprogram fail with a permission error.',
         'answer': 'strace -e inject=openat:error=EACCES myprogram',
         'teach': 'Fault injection: tests the error path you otherwise cannot '
                  'reproduce.'},
        {'id': 'std-count', 'type': 'command',
         'prompt': 'Print a summary of which syscalls myprogram spent time in.',
         'answer': 'strace -c myprogram',
         'teach': 'No per-line output, one table at exit, sorted by time. The '
                  'first thing to run on "why is this slow".'},
        {'id': 'std-count-wall', 'type': 'command',
         'prompt': 'Summarise myprogram by wall clock time rather than kernel time.',
         'answer': 'strace -c -w myprogram',
         'teach': 'Plain -c measures time in the kernel, so a program that '
                  'waits looks free until you add -w.'},
        {'id': 'std-count-both', 'type': 'command',
         'prompt': 'Show the per-line trace of myprogram and the summary table.',
         'answer': 'strace -C myprogram',
         'teach': '-C is both, where -c is the summary alone.'},
        {'id': 'std-strings', 'type': 'command',
         'prompt': 'Trace myprogram without truncating strings at 32 characters.',
         'answer': 'strace -s 2000 myprogram',
         'teach': 'The 32 character default has hidden the answer from more '
                  'people than any other setting in the tool.'},
        {'id': 'std-fdpaths', 'type': 'command',
         'prompt': 'Trace the reads and writes of cat note.txt, showing which '
                   'file each descriptor is.',
         'answer': 'strace -y -e trace=read,write cat note.txt',
         'teach': '-y turns read(3, ...) into read(3</path/to/file>, ...), '
                  'which removes the fd bookkeeping you would do by hand.'},
        {'id': 'std-sockets', 'type': 'command',
         'prompt': 'Trace ./client showing socket descriptors with their addresses.',
         'answer': 'strace -yy ./client',
         'teach': '-yy extends -y to sockets, so a connect line is readable '
                  'without decoding a sockaddr by eye.'},
        {'id': 'std-verbose', 'type': 'command',
         'prompt': 'Trace myprogram printing structures in full rather than '
                   'abbreviated.',
         'answer': 'strace -v myprogram',
         'teach': 'Abbreviation is the default for structs the way truncation '
                  'is for strings.'},
        {'id': 'std-time-call', 'type': 'command',
         'prompt': 'Trace myprogram showing how long each syscall took.',
         'answer': 'strace -T myprogram',
         'teach': 'Duration in angle brackets at the end of the line. One '
                  'slow read is a different problem from a million fast ones.'},
        {'id': 'std-timestamps', 'type': 'command',
         'prompt': 'Trace myprogram with microsecond wall clock timestamps.',
         'answer': 'strace -tt myprogram',
         'teach': 'How you line a trace up against a log file. -t is seconds, '
                  '-ttt is epoch.'},
        {'id': 'std-relative', 'type': 'command',
         'prompt': 'Trace myprogram showing time since the previous syscall.',
         'answer': 'strace -r myprogram',
         'teach': 'Relative timestamps make a gap obvious, which absolute '
                  'ones bury.'},
        {'id': 'std-signal', 'type': 'command',
         'prompt': 'Trace myprogram reporting only SIGSEGV and SIGKILL signals.',
         'answer': 'strace -e signal=SIGSEGV,SIGKILL myprogram',
         'teach': 'Signals are reported separately from syscalls, and have '
                  'their own filter.'},
        {'id': 'std-combined', 'type': 'command',
         'prompt': 'Trace ./app and its children, file calls only, into t.txt.',
         'answer': 'strace -f -e trace=%file -o t.txt ./app',
         'teach': 'The combination you will type most: follow, filter, and '
                  'save somewhere you can grep.'},
        {'id': 'std-quiet', 'type': 'command',
         'prompt': 'Trace myprogram without the attach and detach messages.',
         'answer': 'strace -q myprogram',
         'teach': 'Cosmetic, and worth knowing when the trace is being fed to '
                  'another program.'},
        {'id': 'std-instruction', 'type': 'command',
         'prompt': 'Trace myprogram printing the instruction pointer for each call.',
         'answer': 'strace -i myprogram',
         'teach': 'Useful when correlating a trace with a disassembly, and '
                  'noise otherwise.'},
        {'id': 'std-user', 'type': 'command',
         'prompt': 'Run and trace myprogram as the user nobody.',
         'answer': 'sudo strace -u nobody myprogram',
         'teach': '-u drops privileges for the traced command, which is how '
                  'you reproduce a permission failure that only that user '
                  'sees.'},
        {'id': 'std-ltrace', 'type': 'command',
         'prompt': 'Trace the library calls of ./program rather than its syscalls.',
         'answer': 'ltrace ./program',
         'teach': 'The sibling tool for the layer above, and much more easily '
                  'defeated by how the binary was built.'},
        {'id': 'std-ptrace-scope', 'type': 'command',
         'prompt': 'Read the kernel setting that decides who may attach to '
                   'what.',
         'answer': 'cat /proc/sys/kernel/yama/ptrace_scope',
         'teach': '0 is permissive, 1 restricts to descendants, 2 is admin '
                  'only, 3 forbids it entirely. A refusal here is policy, not '
                  'a bug.'},
    ],

    'challenges': [
        {
            'id': 'stc-what-opened',
            'title': 'Prove which file it opened',
            'goal': 'Trace a command and capture, in a file, the exact openat '
                    'call it made for a file you can name.',
            'setup': {'kind': 'sandbox', 'shell': 'bash',
                      'tree': {'note.txt': 'hello from the sandbox\n'}},
            'solution': {'shell': 'strace -e trace=openat -o trace.txt '
                                  'cat note.txt > /dev/null'},
            'steps': [
                {'instruction': 'Trace cat reading note.txt, filtering to '
                                'openat only.',
                 'hint': 'strace -e trace=openat cat note.txt'},
                {'instruction': 'Send the trace to trace.txt so it is not '
                                'mixed with the file contents.',
                 'hint': 'strace -e trace=openat -o trace.txt cat note.txt'},
                {'instruction': 'Read trace.txt. Note how many opens happened '
                                'before yours, and what they were.'},
            ],
            'free': 'Produce trace.txt containing the openat calls made by '
                    'cat while reading note.txt.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'trace.txt': ['openat', 'note.txt']}}},
            'fallback': 'self',
        },
        {
            'id': 'stc-enoent',
            'title': 'Find the path it actually wanted',
            'goal': 'Reproduce the commonest real use: a program cannot find '
                    'a file, and the trace names the path it looked for.',
            'setup': {'kind': 'sandbox', 'shell': 'bash',
                      'tree': {'config/app.conf': 'mode = real\n'}},
            'solution': {'shell': 'strace -e trace=%file -o miss.txt '
                                  'cat app.conf 2>/dev/null; true'},
            'steps': [
                {'instruction': 'Try to read app.conf from here, where it is '
                                'not. It is in config/.',
                 'hint': 'cat app.conf'},
                {'instruction': 'Now do it under strace, filtered to file '
                                'calls, saving to miss.txt.',
                 'hint': 'strace -e trace=%file -o miss.txt cat app.conf'},
                {'instruction': 'Find the ENOENT line and read the path in '
                                'the arguments. That is the whole technique.'},
            ],
            'free': 'Produce miss.txt containing the failed file syscall, '
                    'with its ENOENT, from reading a path that is not there.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'miss.txt': ['app.conf', 'ENOENT']}}},
            'fallback': 'self',
        },
        {
            'id': 'stc-count',
            'title': 'Answer "why is it slow" with the summary table',
            'goal': 'Produce a syscall summary and read which call dominates, '
                    'rather than guessing.',
            'setup': {'kind': 'sandbox', 'shell': 'bash',
                      'tree': {'data/': None}},
            'solution': {'shell': 'for i in $(seq 1 200); do echo x > '
                                  'data/f$i; done; '
                                  'strace -c -o counts.txt '
                                  'grep -r x data > /dev/null'},
            'steps': [
                {'instruction': 'Make a few hundred small files in data/ so '
                                'there is something to be slow about.',
                 'hint': 'for i in $(seq 1 200); do echo x > data/f$i; done'},
                {'instruction': 'Run a recursive grep over them under a '
                                'counting trace, into counts.txt.',
                 'hint': 'strace -c -o counts.txt grep -r x data'},
                {'instruction': 'Read the table. The calls column and the '
                                'time column tell different stories.'},
            ],
            'free': 'Produce counts.txt: an strace summary table for a '
                    'command that touches several hundred files.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'counts.txt': ['% time', 'total']}}},
            'fallback': 'self',
        },
        {
            'id': 'stc-follow',
            'title': 'See into the children',
            'goal': 'Trace a shell script with and without -f, and keep the '
                    'evidence that the default hides the work.',
            'setup': {'kind': 'sandbox', 'shell': 'bash',
                      'tree': {'work.sh': {'content': '#!/bin/bash\n'
                                                      'ls > /dev/null\n'
                                                      'wc -l < work.sh > '
                                                      'count.out\n',
                                           'mode': '755'}}},
            'solution': {'shell': 'strace -o alone.txt ./work.sh; '
                                  'strace -f -o followed.txt ./work.sh'},
            'steps': [
                {'instruction': 'Trace ./work.sh normally into alone.txt.',
                 'hint': 'strace -o alone.txt ./work.sh'},
                {'instruction': 'Trace it again with -f into followed.txt.',
                 'hint': 'strace -f -o followed.txt ./work.sh'},
                {'instruction': 'Compare their sizes, and find the execve of '
                                'ls in only one of them.',
                 'hint': 'wc -l alone.txt followed.txt; grep execve followed.txt'},
            ],
            'free': 'Produce alone.txt and followed.txt, tracing the same '
                    'script without and with fork following.',
            'verify': {'kind': 'sandbox', 'expect': {
                'is_file': ['alone.txt', 'followed.txt'],
                'file_contains': {'followed.txt': ['clone', 'execve']}}},
            'fallback': 'self',
        },
        {
            'id': 'stc-fdpaths',
            'title': 'Stop counting file descriptors by hand',
            'goal': 'Use -y so the trace names the file behind every '
                    'descriptor, and capture a read that shows it.',
            'setup': {'kind': 'sandbox', 'shell': 'bash',
                      'tree': {'note.txt': 'the quick brown fox\n'}},
            'solution': {'shell': 'strace -y -e trace=read,openat -o fds.txt '
                                  'cat note.txt > /dev/null'},
            'steps': [
                {'instruction': 'Trace cat note.txt filtered to read and '
                                'openat, into fds.txt, with -y.',
                 'hint': 'strace -y -e trace=read,openat -o fds.txt cat note.txt'},
                {'instruction': 'Find the read line and note that the '
                                'descriptor carries the path with it.'},
            ],
            'free': 'Produce fds.txt where the read calls are annotated with '
                    'the path of the file being read.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'fds.txt': ['note.txt', 'read(']}}},
            'fallback': 'self',
        },
        {
            'id': 'stc-real-program',
            'title': 'Trace something on your own machine',
            'goal': 'The sandbox is over. Take a program you actually use and '
                    'find out something about it you did not know.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'Pick a program with a config file. Trace its '
                                'file calls and list every path it tried.',
                 'hint': 'strace -f -e trace=%file -o t.txt yourprogram'},
                {'instruction': 'Extract just the failures. That list is its '
                                'search path, in order.',
                 'hint': 'grep ENOENT t.txt'},
                {'instruction': 'Now find something that makes a network '
                                'connection, and trace where it goes.',
                 'hint': 'strace -f -yy -e trace=%network -o net.txt yourprogram'},
                {'instruction': 'Start something long running, attach to it '
                                'with -p, and read what it is blocked in.'},
            ],
            'free': 'On your own machine: recover a program config search '
                    'path from a trace, find where something connects, and '
                    'attach to a running process to see what it waits on.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
    ],

    'quiz': [
        {'id': 'stq-stderr', 'type': 'mcq',
         'prompt': 'You run strace ls | grep openat and see no trace lines. '
                   'Why?',
         'answer': 'The trace goes to stderr, and the pipe only carries stdout.',
         'distractors': ['grep cannot match the parentheses in the output.',
                         'strace suppresses output when it is not a terminal.',
                         'openat is filtered out unless you ask for it.'],
         'teach': 'Use -o to a file, or 2>&1 into the pipe. This costs '
                  'everyone about ten minutes once.'},
        {'id': 'stq-truncation', 'type': 'mcq',
         'prompt': 'A write in the trace ends with three dots. What does that '
                   'mean?',
         'answer': 'strace truncated the string at 32 characters.',
         'distractors': ['The program sent a partial buffer.',
                         'The syscall was interrupted by a signal.',
                         'The rest of the string was binary and unprintable.'],
         'teach': '-s raises the limit. The default has hidden more answers '
                  'than any other setting in the tool.'},
        {'id': 'stq-noclone', 'type': 'mcq',
         'prompt': 'You trace a shell script and the output ends right after '
                   'a clone. What happened?',
         'answer': 'The work moved into a child, and strace follows only one '
                   'process by default.',
         'distractors': ['The script crashed at that point.',
                         'strace lost the trace because the child changed '
                         'privileges.',
                         'The remaining syscalls were filtered out as '
                         'uninteresting.'],
         'teach': '-f follows forks and prefixes each line with a pid, which '
                  'is why -f and -o are the normal pair.'},
        {'id': 'stq-errno', 'type': 'mcq',
         'prompt': 'openat returns -1 EACCES rather than -1 ENOENT. What is '
                   'the difference?',
         'answer': 'The path exists but you are not allowed to open it.',
         'distractors': ['The path does not exist, but a parent directory '
                         'does.',
                         'The file exists and is locked by another process.',
                         'The call was made with the wrong flags.'],
         'teach': 'ENOENT is not there, EACCES is not allowed. Two different '
                  'questions with two different fixes.'},
        {'id': 'stq-c-time', 'type': 'mcq',
         'prompt': 'A program sleeps for ten seconds. What does strace -c '
                   'show in its seconds column?',
         'answer': 'Almost nothing, because it measures time in the kernel, '
                   'not elapsed time.',
         'distractors': ['Ten seconds, against the nanosleep call.',
                         'Nothing at all, because sleeping makes no syscall.',
                         'Ten seconds spread across every call in the table.'],
         'teach': 'Add -w to measure wall clock instead. That distinction is '
                  'the whole reason -w exists.'},
        {'id': 'stq-status-failed', 'type': 'mcq',
         'prompt': 'What is the fastest way to answer "why did this program '
                   'not work" from a ten thousand line trace?',
         'answer': 'Re-run with -e status=failed and read the handful of '
                   'lines left.',
         'distractors': ['Re-run with -v to see the full structures.',
                         'Re-run with -c to see which call was slowest.',
                         'Grep the trace for the program name.'],
         'teach': 'Filtering to failures is the single highest value filter '
                  'in the tool, and it usually leaves about six lines.'},
        {'id': 'stq-attach-late', 'type': 'mcq',
         'prompt': 'You attach with -p to a running service and see no config '
                   'file reads. What may you conclude?',
         'answer': 'Nothing about startup: those reads happened before you '
                   'attached.',
         'distractors': ['That the service reads no config files.',
                         'That the config was cached by the kernel.',
                         'That the reads were filtered as uninteresting.'],
         'teach': '-p answers what it is doing now. For what it did at '
                  'startup, restart it under strace.'},
        {'id': 'stq-ptrace-scope', 'type': 'mcq',
         'prompt': 'strace -p on another user process fails with "Operation '
                   'not permitted", as root it works. What is that?',
         'answer': 'The ptrace_scope hardening setting doing its job.',
         'distractors': ['A bug in strace on that kernel version.',
                         'The process having dropped SYS_PTRACE.',
                         'SELinux blocking the attach specifically.'],
         'teach': '/proc/sys/kernel/yama/ptrace_scope: 0 permissive, 1 '
                  'descendants only, 2 admin, 3 never.'},
        {'id': 'stq-invisible', 'type': 'mcq',
         'prompt': 'A program does heavy work and its trace is nearly empty. '
                   'What is it doing?',
         'answer': 'Computing in userspace, which never crosses the syscall '
                   'boundary.',
         'distractors': ['Being blocked, since blocked processes make no '
                         'calls.',
                         'Using a syscall class strace does not decode.',
                         'Running in a thread that -f did not follow.'],
         'teach': 'strace is a boundary observer. Everything inside the '
                  'process is invisible to it by design.'},
        {'id': 'stq-y-flag', 'type': 'mcq',
         'prompt': 'You want read(3, ...) to say which file descriptor 3 is. '
                   'Which flag?',
         'answer': '-y, which annotates descriptors with their paths.',
         'distractors': ['-v, which prints structures in full.',
                         '-s, which stops strings being truncated.',
                         '-i, which prints the instruction pointer.'],
         'teach': '-y for files, -yy to extend it to socket addresses. Both '
                  'remove bookkeeping you would otherwise do by eye.'},
    ],
}
