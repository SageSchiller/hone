"""Linux Utilities: openly a drill deck, not a course.

**This module has no lessons on purpose**, and it is the first one that does.
The roster's boundary rule says a tool earns its own module only if learning it
changes how you think; if the difficulty is "I know what I want and cannot
remember the flags", it is a drill deck instead. Everything here is that.

The Walkthrough view still renders, because D16 rule 1 says hiding a view makes
a deliberate choice look like a bug. It says what this module is and sends you
to Drill, which is exactly the empty state that rule was written for.

The teaching that does happen lives in the `teach` on each drill, where it can
be read at the moment it is relevant rather than in a lesson nobody would open.
That is the right shape for `tar`: nobody wants a page about it, everybody
wants the flags at the moment they need them.
"""

MODULE = {
    'id': 'linuxutils',
    'title': 'Linux Utilities',
    'group': 'Linux',
    'blurb': 'The flags you always forget. A drill deck, not a course.',
    'context': 'You are at a shell prompt. These are the flags, not the ideas: the answer is a command you would actually type.',
    'prereqs': ['linux'],
    'adapter': 'sandbox',
    'estimate': '2-3 hours, then repetition',
    'order': 43,

    # No lessons. See the module docstring: this is deliberate, and the
    # Walkthrough view says so rather than being hidden.
    'lessons': [],

    'drills': [
        # find and xargs
        {'id': 'lu-find-name', 'type': 'command',
         'answer': 'find . -name "*.log"',
         'prompt': 'Find every .log file under the current directory.',
         'teach': 'Quote the pattern, or the shell expands it before find sees '
                  'it and you search for whatever happens to be in this '
                  'directory.'},
        {'id': 'lu-find-type', 'type': 'command',
         'answer': 'find . -type d -name build',
         'prompt': 'Find directories called build, and not files of that name.',
         'teach': '-type d is directories, f is files. Without it, find '
                  'happily returns a file named build and you act on the '
                  'wrong thing.'},
        {'id': 'lu-find-mtime', 'type': 'command',
         'answer': 'find . -mtime -7',
         'prompt': 'Find everything modified in the last seven days.',
         'teach': '-7 is "less than seven days ago", +7 is "more than". A bare '
                  '7 means exactly the seventh day, which is almost never what '
                  'you wanted.'},
        {'id': 'lu-find-size', 'type': 'command',
         'answer': 'find . -size +100M',
         'prompt': 'Find files larger than 100 megabytes.',
         'teach': 'The plus means larger than; a minus means smaller. Leave '
                  'the sign off and it means exactly that size, which matches '
                  'almost nothing.'},
        {'id': 'lu-find-exec', 'type': 'command',
         'answer': 'find . -name "*.tmp" -exec rm {} +',
         'prompt': 'Delete every .tmp file, running rm as few times as '
                   'possible.',
         'teach': '-exec ... + batches the arguments into one invocation; '
                  '-exec ... \\; runs the command once per file and is much '
                  'slower.'},
        {'id': 'lu-find-delete', 'type': 'command',
         'answer': 'find . -name "*.tmp" -delete',
         'prompt': 'Delete every .tmp file using find\'s own action rather than '
                   'calling rm.',
         'teach': 'Put -delete last. find applies predicates left to right, and '
                  '-delete before -name deletes everything.'},
        {'id': 'lu-find-print0', 'type': 'command',
         'answer': 'find . -print0 | xargs -0 rm',
         'prompt': 'Pipe filenames to xargs safely, so that names containing '
                   'spaces survive.',
         'teach': 'Filenames may contain spaces and newlines. Null separation '
                  'is the only safe way to pass them through a pipe.'},
        {'id': 'lu-find-prune', 'type': 'command',
         'answer': 'find . -name .git -prune -o -name "*.py" -print',
         'prompt': 'Find .py files while skipping the .git directory entirely.',
         'teach': '-prune stops find descending. The -o -print is required '
                  'because -prune is itself an action.'},
        {'id': 'lu-xargs-n', 'type': 'command', 'answer': 'xargs -n1 echo',
         'prompt': 'Run a command once per input item rather than batching them.',
         'teach': 'By default xargs crams as many items as fit onto one '
                  'command line. -n1 forces one call each, which is what you '
                  'want when order or failure per item matters.'},
        {'id': 'lu-xargs-i', 'type': 'command',
         'answer': 'xargs -I{} mv {} /tmp/',
         'prompt': 'Use each input item in the middle of a command rather than '
                   'at the end.',
         'teach': '-I names a placeholder and substitutes it wherever it '
                  'appears, which also switches to one item per command.'},

        # lsof
        {'id': 'lu-lsof-port', 'type': 'command', 'answer': 'lsof -i :8080',
         'prompt': 'Find out what is using port 8080.',
         'teach': 'The colon is required: -i :8080 is a port, -i@host is an '
                  "address. This is the fastest answer to 'address already in "
                  "use'."},
        {'id': 'lu-lsof-deleted', 'type': 'command', 'answer': 'lsof +L1',
         'prompt': 'Find deleted files that are still held open and still using '
                   'disk.',
         'teach': 'DFIR gold, and also the answer to df and du disagreeing.'},
        {'id': 'lu-lsof-path', 'type': 'command', 'answer': 'lsof /mnt',
         'prompt': 'Find out what is keeping a mount busy so it will not '
                   'unmount.',
         'teach': 'Given a path it lists every process holding something open '
                  "under it, which is precisely the list 'target is busy' "
                  'refuses to give you.'},
        {'id': 'lu-lsof-pid', 'type': 'command', 'answer': 'lsof -p 1234',
         'prompt': 'List every file one process has open.',
         'teach': 'Open files include sockets, libraries and the working '
                  'directory, so this doubles as a picture of what a process '
                  'is actually doing.'},

        # tar: pure flag memory, which is exactly what a drill deck is for
        {'id': 'lu-tar-create', 'type': 'command',
         'answer': 'tar -czf archive.tar.gz dir',
         'prompt': 'Create a gzipped archive of a directory.',
         'teach': 'c create, z gzip, f file. The f must come last of the three '
                  'because the filename follows it.'},
        {'id': 'lu-tar-extract', 'type': 'command',
         'answer': 'tar -xzf archive.tar.gz',
         'prompt': 'Extract a gzipped archive.',
         'teach': 'x extract. Modern tar detects the compression, so -xf '
                  'usually works too.'},
        {'id': 'lu-tar-list', 'type': 'command', 'answer': 'tar -tzf archive.tar.gz',
         'prompt': 'List what is inside an archive without extracting it.',
         'teach': 'Do this before extracting anything you did not make. An '
                  'archive can contain absolute paths and ../.'},
        {'id': 'lu-tar-into', 'type': 'command',
         'answer': 'tar -xzf archive.tar.gz -C /tmp/target',
         'prompt': 'Extract an archive into a specific directory rather than '
                   'the current one.',
         'teach': '-C changes directory before extracting. Without it an '
                  'archive built with loose paths sprays files into wherever '
                  'you happened to stand.'},
        {'id': 'lu-tar-strip', 'type': 'command',
         'answer': 'tar -xzf archive.tar.gz --strip-components=1',
         'prompt': 'Extract an archive while discarding its top-level '
                   'directory.',
         'teach': 'The fix for an archive that wraps everything in a version '
                  'directory you do not want.'},

        # inspection
        {'id': 'lu-stat', 'type': 'command', 'answer': 'stat file.txt',
         'prompt': 'Show a file\'s size, permissions, inode and timestamps.',
         'teach': 'ls shows one timestamp; stat shows all three: modified, '
                  'accessed, and the inode change time, which cannot be set '
                  'by touch.'},
        {'id': 'lu-file', 'type': 'command', 'answer': 'file mystery.bin',
         'prompt': 'Work out what a file actually is, ignoring its extension.',
         'teach': 'It reads the leading bytes, not the name. Extensions are '
                  'decoration on Linux, and this is what tells you the .jpg '
                  'is actually a script.'},
        {'id': 'lu-strings', 'type': 'command', 'answer': 'strings -n 8 binary',
         'prompt': 'Pull printable text of at least eight characters out of a '
                   'binary.',
         'teach': 'The default minimum is 4, which produces mostly noise. Eight '
                  'is usually the readable setting.'},
        {'id': 'lu-xxd', 'type': 'command', 'answer': 'xxd file.bin | head',
         'prompt': 'Look at the first few lines of a file in hexadecimal.',
         'teach': 'The right side shows printable bytes, the left the '
                  'offsets. The first few bytes are the magic number that '
                  'file used to identify it.'},
        {'id': 'lu-xxd-seek', 'type': 'command', 'answer': 'xxd -s 512 -l 64 disk.img',
         'prompt': 'Dump 64 bytes starting at offset 512.',
         'teach': '-s seek, -l length. This is how you read a specific '
                  'structure out of an image without loading the whole thing.'},

        # space and watching
        {'id': 'lu-du-sort', 'type': 'command', 'answer': 'du -sh * | sort -h',
         'prompt': 'Show what is using space in this directory, smallest first.',
         'teach': 'sort -h understands the K, M and G suffixes that -h '
                  'produces.'},
        {'id': 'lu-df-h', 'type': 'command', 'answer': 'df -h',
         'prompt': 'Show how full each filesystem is, in human units.',
         'teach': 'df is per filesystem, du is per directory. When they '
                  'disagree, a deleted file is still held open somewhere.'},
        {'id': 'lu-watch', 'type': 'command', 'answer': 'watch -n 5 df -h',
         'prompt': 'Re-run a command every five seconds and watch the output '
                   'change in place.',
         'teach': 'It clears and redraws, so change is easy to spot; -d '
                  'highlights what differed. Quote the command if it has its '
                  'own flags.'},
        {'id': 'lu-tee', 'type': 'command', 'answer': 'cmd | tee out.txt',
         'prompt': 'Send output to a file AND to your screen at the same time. '
                   'Use "cmd".',
         'teach': 'tee -a appends. The classic use is `... | sudo tee /etc/...` '
                  'because a plain > redirect happens as your user, not as '
                  'root.'},
        {'id': 'lu-tee-sudo', 'type': 'command',
         'answer': 'echo text | sudo tee /etc/config',
         'prompt': 'Write to a root-owned file from an unprivileged shell.',
         'teach': '`sudo echo x > /etc/f` fails because the redirect is done by '
                  'your shell, not by sudo. This is the fix.'},

        # links and lookups
        {'id': 'lu-ln-s', 'type': 'command', 'answer': 'ln -s target link',
         'prompt': 'Create a symbolic link.',
         'teach': 'Target first, link second, the same order as cp. A symlink '
                  "to a relative target is resolved from the link's own "
                  'directory, which is the classic broken-link cause.'},
        {'id': 'lu-ln-hard', 'type': 'command', 'answer': 'ln target link',
         'prompt': 'Create a hard link, a second name for the same data.',
         'teach': 'A hard link shares the inode, so deleting either name leaves '
                  'the data reachable through the other. It cannot cross '
                  'filesystems.'},
        {'id': 'lu-readlink', 'type': 'command', 'answer': 'readlink -f path',
         'prompt': 'Resolve a path all the way through every symlink to the '
                   'real file.',
         'teach': '-f follows every link and prints an absolute path. It is '
                  'how a script finds its own real location when invoked '
                  'through a symlink.'},
        {'id': 'lu-type-a', 'type': 'command', 'answer': 'type -a python3',
         'prompt': 'Show every python3 that would be found, including aliases '
                   'and builtins.',
         'teach': 'which only searches PATH, so it misses aliases, functions '
                  'and builtins. type asks the shell itself, and -a shows '
                  'every candidate in order.'},

        # less, which reuses vi keys
        {'id': 'lu-less-search', 'type': 'keys', 'keys': ['/'],
         'prompt': 'Search forward inside less.',
         'teach': 'less uses vi keys, which is why this module reinforces the '
                  'vim one for free. n and N move between matches.'},
        {'id': 'lu-less-follow', 'type': 'keys', 'keys': ['S-f'],
         'prompt': 'In less, follow the file as it grows, like tail -f.',
         'teach': 'Ctrl-C stops following and leaves you in the pager, which '
                  'tail -f cannot do.'},
        {'id': 'lu-less-end', 'type': 'keys', 'keys': ['S-g'],
         'prompt': 'Jump to the end of the file in less.',
         'teach': 'Same as vim: G for the end, gg for the start.'},
        {'id': 'lu-less-chop', 'type': 'command', 'answer': 'less -S file.log',
         'prompt': 'Open a file in less without wrapping long lines.',
         'teach': 'Essential for wide log lines and for anything tabular.'},
    ],

    'challenges': [
        {
            'id': 'lu-find-xargs',
            'title': 'Find and act, safely',
            'goal': 'Use find and xargs on filenames containing spaces, which '
                    'is where the naive pipeline breaks.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'logs/': None,
                'logs/one.log': 'a\n',
                'logs/two three.log': 'b\n',
                'logs/keep.txt': 'c\n',
                'archive/': None,
            }},
            'solution': {'shell': 'find logs -name "*.log" -print0 | '
                                  'xargs -0 -I{} mv {} archive/'},
            'steps': [
                {'instruction': 'Find the .log files under logs, quoting the '
                                'pattern.',
                 'hint': 'find logs -name "*.log"'},
                {'instruction': 'Pass them to xargs so a name with a space '
                                'survives.',
                 'hint': '-print0 on find, -0 on xargs'},
                {'instruction': 'Move each one into archive/.',
                 'hint': 'xargs -0 -I{} mv {} archive/'},
            ],
            'free': 'Move both .log files, including the one with a space in '
                    'its name, into archive/. Leave keep.txt alone.',
            'verify': {'kind': 'sandbox', 'expect': {
                'exists': ['archive/one.log', 'archive/two three.log',
                           'logs/keep.txt'],
                'missing': ['logs/one.log', 'logs/two three.log']}},
            'fallback': 'self',
        },
        {
            'id': 'lu-tar-roundtrip',
            'title': 'Archive, inspect, extract elsewhere',
            'goal': 'Do the whole tar loop, including listing before extracting '
                    'and stripping a wrapper directory.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'project/': None,
                'project/a.txt': 'alpha\n',
                'project/b.txt': 'bravo\n',
                'out/': None,
            }},
            'solution': {'shell': 'tar -czf project.tar.gz project && '
                                  'tar -tzf project.tar.gz > listing.txt && '
                                  'tar -xzf project.tar.gz -C out '
                                  '--strip-components=1'},
            'steps': [
                {'instruction': 'Create project.tar.gz from the project '
                                'directory.', 'hint': 'tar -czf project.tar.gz project'},
                {'instruction': 'List its contents into listing.txt without '
                                'extracting.', 'hint': 'tar -tzf ... > listing.txt'},
                {'instruction': 'Extract it into out/, discarding the top-level '
                                'project directory.',
                 'hint': 'tar -xzf ... -C out --strip-components=1'},
            ],
            'free': 'Make project.tar.gz, write its listing to listing.txt, and '
                    'extract it into out/ so that out/a.txt exists rather than '
                    'out/project/a.txt.',
            'verify': {'kind': 'sandbox', 'expect': {
                'exists': ['project.tar.gz', 'listing.txt', 'out/a.txt',
                           'out/b.txt'],
                'missing': ['out/project'],
                'file_contains': {'listing.txt': 'project/a.txt'}}},
            'fallback': 'self',
        },
        {
            'id': 'lu-tee-and-links',
            'title': 'tee, and both kinds of link',
            'goal': 'Capture output while still seeing it, and make the two '
                    'kinds of link so the difference is concrete.',
            'setup': {'kind': 'sandbox', 'shell': 'bash',
                      'tree': {'data.txt': 'original\n'}},
            'solution': {'shell': 'echo "captured" | tee log.txt > /dev/null; '
                                  'ln data.txt hard.txt; ln -s data.txt soft.txt'},
            'steps': [
                {'instruction': 'Write the word captured into log.txt using '
                                'tee.', 'hint': 'echo captured | tee log.txt'},
                {'instruction': 'Make a hard link to data.txt called hard.txt.',
                 'hint': 'ln data.txt hard.txt'},
                {'instruction': 'Make a symbolic link to data.txt called '
                                'soft.txt.', 'hint': 'ln -s data.txt soft.txt'},
            ],
            'free': 'Produce log.txt containing "captured" via tee, a hard link '
                    'hard.txt and a symlink soft.txt, both pointing at '
                    'data.txt.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'log.txt': 'captured'},
                'is_symlink': {'soft.txt': 'data.txt'},
                'is_file': ['hard.txt'],
                'file_equals': {'hard.txt': 'original'}}},
            'fallback': 'self',
        },
    ],

    'quiz': [
        {'id': 'luq-exec', 'type': 'mcq',
         'prompt': 'What is the difference between `-exec cmd {} \\;` and '
                   '`-exec cmd {} +`?',
         'answer': 'The semicolon runs cmd once per file; the plus batches them.',
         'distractors': ['The plus runs in the background.',
                         'The semicolon is for files, the plus for directories.',
                         'They are the same; the plus is newer syntax.'],
         'teach': 'On ten thousand files that is ten thousand processes versus '
                  'a handful.'},

        {'id': 'luq-print0', 'type': 'mcq',
         'prompt': 'Why does `find . | xargs rm` break?',
         'answer': 'Filenames can contain spaces and newlines, which xargs '
                   'splits on.',
         'distractors': ['xargs cannot read from a pipe.',
                         'rm refuses more than one argument.',
                         'find prints relative paths that rm cannot resolve.'],
         'teach': '-print0 and -0 use a null separator, which cannot appear in '
                  'a filename. It is the only safe way.'},

        {'id': 'luq-delete-order', 'type': 'mcq',
         'prompt': 'What does `find . -delete -name "*.tmp"` do?',
         'answer': 'Deletes everything, because predicates apply left to right.',
         'distractors': ['Deletes only the .tmp files.',
                         'Nothing; the order is invalid.',
                         'Prompts before each deletion.'],
         'teach': 'Put -delete last. This is a genuinely destructive ordering '
                  'mistake.'},

        {'id': 'luq-tar-list', 'type': 'mcq',
         'prompt': 'Why list an archive before extracting one you did not make?',
         'answer': 'It can contain absolute paths or .. and write outside the '
                   'directory.',
         'distractors': ['Extraction is slow and listing is fast.',
                         'Listing verifies the checksum.',
                         'Extraction overwrites without asking.'],
         'teach': '`tar -tzf` costs a second. Modern tar strips leading slashes '
                  'but not every tar does.'},

        {'id': 'luq-hardlink', 'type': 'mcq',
         'prompt': 'You hard link a.txt to b.txt, then delete a.txt. What '
                   'happens to the data?',
         'answer': 'Nothing; b.txt still names it.',
         'distractors': ['It is deleted and b.txt breaks.',
                         'b.txt becomes an empty file.',
                         'b.txt is deleted too.'],
         'teach': 'Both names point at one inode. The data goes when the last '
                  'name does, which is also why a symlink behaves completely '
                  'differently here.'},

        {'id': 'luq-tee-sudo', 'type': 'mcq',
         'prompt': 'Why does `sudo echo hello > /etc/file` fail?',
         'answer': 'The shell performs the redirect as you, before sudo runs.',
         'distractors': ['echo cannot write to /etc.',
                         'sudo strips redirections for safety.',
                         '/etc is mounted read-only.'],
         'teach': '`echo hello | sudo tee /etc/file` is the fix, and it is why '
                  'tee earns its place.'},

        {'id': 'luq-lsof-deleted', 'type': 'mcq',
         'prompt': 'What does `lsof +L1` show?',
         'answer': 'Open files with no remaining name, so deleted but still '
                   'using space.',
         'distractors': ['Files opened more than once.',
                         'Files locked by another process.',
                         'Files on network filesystems.'],
         'teach': 'The answer to df and du disagreeing, and forensically '
                  'interesting for the same reason.'},

        {'id': 'luq-mtime', 'type': 'mcq',
         'prompt': 'What does `find . -mtime 7` match?',
         'answer': 'Files modified exactly seven days ago, to the day.',
         'distractors': ['Files modified in the last seven days.',
                         'Files older than seven days.',
                         'Files modified within seven hours.'],
         'teach': 'Almost never what you wanted. -7 is "less than", +7 is '
                  '"more than".'},
    ],
}
