"""Linux Basics: what you need before bash makes sense.

Deliberately first. bash assumes the filesystem, the permission bits, and the
file-descriptor model, and trying to learn quoting before you know what `2>`
even refers to is why shell scripting feels arbitrary.

Concept and tool are taught **together** throughout: permissions arrive with
`chmod`, redirection arrives with the descriptor numbers, processes arrive with
signals. Splitting the idea from the command across two modules is the mistake
this roster's boundary rule exists to prevent.

Challenges use the sandbox adapter and your own shell, because everything here
behaves identically in fish, bash and zsh. The bash module is where the shell
starts to matter, and it asks for bash explicitly.
"""

MODULE = {
    'id': 'linux',
    'title': 'Linux Basics',
    'group': 'Linux',
    'blurb': 'The filesystem, permissions, redirection and processes.',
    'context': 'You are at a shell prompt in your own home directory.',
    'prereqs': [],
    'adapter': 'sandbox',
    'estimate': '5-7 hours',
    'order': 40,

    'lessons': [
        {
            'id': 'lx-tree',
            'title': 'One tree, and where things live',
            'next': 'lx-paths',
            'concept': (
                'There are no drive letters. Everything hangs off a single root '
                'called `/`, including other disks, USB sticks and network '
                'shares, which are attached at some directory rather than given '
                'a letter of their own.\n\n'
                'The top-level directories are not arbitrary, and knowing six of '
                'them removes most of the mystery. `/etc` is system '
                'configuration, all text. `/home` is people. `/var` is data that '
                'changes, including logs. `/usr` is installed software. `/tmp` '
                'is scratch space that may vanish on reboot.\n\n'
                'Two are special because they are not really files at all. '
                '`/proc` and `/sys` are the kernel pretending to be a '
                'filesystem, so reading a file there asks the kernel a question. '
                'That is why `cat /proc/cpuinfo` works.'
            ),
            'examples': [
                {
                    'label': 'The parts worth knowing',
                    'code': ('/etc     configuration, text files\n'
                             '/home    user directories\n'
                             '/var     changing data: /var/log lives here\n'
                             '/usr     installed software\n'
                             '/tmp     scratch, cleared periodically\n'
                             '/proc    the kernel, shaped like files\n'
                             '/dev     devices, also shaped like files'),
                    'note': '"Everything is a file" is not a slogan. A disk, a '
                            'terminal and a running process all appear as paths.',
                },
            ],
            'misconceptions': [
                'A mounted disk is not a separate world. It appears at a path '
                'like `/mnt/backup`, and nothing about using it differs.',
                '`/usr` does not mean user. It is where installed software '
                'lives, and `/home` is where you live.',
                'Files in `/proc` have size zero and are not stored anywhere. '
                'They are generated when you read them.',
            ],
            'try_it': [
                'Run `ls /` and then `cat /proc/uptime`. The second one is the '
                'kernel answering a question, not a file being read.',
            ],
        },
        {
            'id': 'lx-paths',
            'title': 'Paths, and reading ls -l',
            'next': 'lx-files',
            'concept': (
                'A path starting with `/` is absolute and means the same thing '
                'from anywhere. Anything else is relative to where you are '
                'standing, which `pwd` will tell you.\n\n'
                'Three shorthands do most of the work: `.` is here, `..` is the '
                'parent, and `~` is your home directory. `cd -` returns to '
                'wherever you were last, which is the navigation equivalent of '
                'alt-tab.\n\n'
                '`ls -l` is the command you will read most often, so it repays '
                'learning properly. The first character is the type, the next '
                'nine are permissions in three groups of three, and then come '
                'the link count, owner, group, size, time and name.'
            ),
            'examples': [
                {
                    'label': 'Reading a long listing',
                    'code': ('-rw-r--r-- 1 sage users 1024 Aug 12 09:00 notes.txt\n'
                             'drwxr-xr-x 2 sage users 4096 Aug 12 09:00 work\n'
                             'lrwxrwxrwx 1 sage users    8 Aug 12 09:00 cur -> notes\n'
                             '^^^^^^^^^^\n'
                             '|+--+--+--  owner, group, everyone else\n'
                             '+ type: - file, d directory, l symlink'),
                    'note': 'Once you can read this line you can answer most '
                            '"why can I not open that" questions yourself.',
                },
                {
                    'label': 'Moving about',
                    'code': ('pwd        where am I\n'
                             'cd ~       home        cd ..    up one\n'
                             'cd -       back to the previous directory\n'
                             'ls -lah    long, all, human-readable sizes\n'
                             'ls -lt     newest first, which is often what\n'
                             '           you actually wanted'),
                    'note': '`ls -lt` and `ls -ltr` (oldest last) are worth '
                            'muscle memory.',
                },
            ],
            'misconceptions': [
                'Hidden files are not protected. A leading dot means `ls` skips '
                'them by default, and `-a` shows them. That is the whole '
                'mechanism.',
                'Filenames are case sensitive and may contain spaces. `My File` '
                'is two arguments unless you quote it, which is the first hint '
                'of the bash module.',
                'The size of a directory in `ls -l` is not the size of its '
                'contents. Use `du -sh` for that.',
            ],
            'try_it': [
                'Run `ls -la ~` and find one file whose permissions differ from '
                'its neighbours. Work out why.',
            ],
        },
        {
            'id': 'lx-files',
            'title': 'Creating, moving and destroying',
            'concept': (
                'Five commands cover almost everything: `mkdir`, `touch`, `cp`, '
                '`mv` and `rm`.\n\n'
                'The one that surprises people is `mv`, which is both move and '
                'rename, because on a filesystem those are the same operation: '
                'you are changing where a name points, not moving bytes. '
                'Renaming a huge file is instant for exactly that reason.\n\n'
                '`rm` deserves respect. There is no trash and no undo. `rm -r` '
                'recurses, `rm -f` stops asking, and `rm -rf` combined with a '
                'typo or an unquoted variable is how people lose work. The habit '
                'worth building is to `ls` the thing first, then run the same '
                'pattern with `rm`.'
            ),
            'examples': [
                {
                    'label': 'The five',
                    'code': ('mkdir -p a/b/c   make the whole path\n'
                             'touch f          create empty, or bump the time\n'
                             'cp a b           copy      cp -r  for directories\n'
                             'mv a b           move, or rename\n'
                             'rm f             delete    rm -r  for directories'),
                    'note': '`-p` on mkdir also means "do not complain if it '
                            'already exists", which is why scripts use it.',
                },
                {
                    'label': 'The habit that saves you',
                    'code': ('ls  old/*.log     look at exactly what matches\n'
                             'rm  old/*.log     then run the same pattern'),
                    'note': 'One extra second, and it has saved everyone who '
                            'does it.',
                },
            ],
            'misconceptions': [
                '`mv` overwrites the destination without asking. `mv -i` asks, '
                'and `mv -n` refuses.',
                '`cp` without `-r` will not copy a directory, and the error '
                'saying "omitting directory" is what that means.',
                'Deleting a file does not free space if a running process still '
                'has it open. `lsof` is how you find that out.',
            ],
            'try_it': [
                'Create a directory, put a file in it, rename the directory, and '
                'confirm the file is still inside.',
            ],
            'next': 'lx-viewing',
        },
        {
            'id': 'lx-viewing',
            'title': 'Reading a file without opening an editor',
            'next': 'lx-permissions',
            'concept': (
                'Most of what you do on a Linux machine is look at files you are '
                'not editing: a log, a config, the top of a huge data file. '
                'Opening an editor for that is slow and, on a ten-gigabyte log, '
                'a mistake. There are four tools, and each answers a different '
                'question.\n\n'
                '`cat` dumps the whole file to the screen. It is right for '
                'something short, and wrong for anything long, because it all '
                'scrolls past. `less` is the answer for long files: it opens a '
                'pager you can scroll and search and then leave, and it loads '
                'only what it shows, so it opens a huge file instantly. The '
                'reason it is worth learning first is that its keys are vi\'s '
                'keys: `/` searches, `n` repeats, `g` and `G` jump to the ends, '
                '`q` quits. Learning `less` reinforces the vim module for free.\n\n'
                '`head` and `tail` show the ends. `head` is the first ten lines, '
                '`tail` the last ten, and both take `-n` to change the count. '
                'The one worth building into muscle memory is `tail -f`, which '
                'follows a file as it grows: point it at a log and watch new '
                'lines appear live. That is how you watch a service while you '
                'poke it.\n\n'
                '`wc` counts: `wc -l` is lines, which answers "how big is this" '
                'faster than reading it, and it is the end of a great many '
                'pipelines.'
            ),
            'examples': [
                {
                    'label': 'The four, and when each fits',
                    'code': ('cat f            dump it all (short files only)\n'
                             'less f           page through it: / to search, q\n'
                             'head f           first ten lines\n'
                             'tail f           last ten lines\n'
                             'tail -n 50 f     last fifty\n'
                             'tail -f log      follow it live as it grows\n'
                             'wc -l f          count the lines'),
                    'note': 'less loads only what it shows, so it opens a '
                            'ten-gigabyte file instantly where cat would flood '
                            'the terminal.',
                },
                {
                    'label': 'less is vi',
                    'code': ('/pattern   search forward     n   next match\n'
                             'g   G      top / bottom\n'
                             'Space      down a page        b   up a page\n'
                             'q          quit'),
                    'note': 'The same keys as the vim module, which is why less '
                            'feels familiar the moment you have met vim.',
                },
            ],
            'misconceptions': [
                'cat is not for reading long files. It has no paging, so '
                'everything scrolls past; that is what less is for.',
                'Piping cat into another command is usually pointless. '
                '`cat f | grep x` should be `grep x f`; the joke name for the '
                'habit is a "useless use of cat".',
                'less does not load the whole file. That is exactly why it is '
                'safe on a file too big to fit in memory.',
                'tail -f follows the file, so it does not return on its own. '
                'Ctrl-C leaves it.',
            ],
            'try_it': [
                'Run `less /etc/services`, search for `http` with `/http`, press '
                '`n` a couple of times, then `q`. Then `tail -n 5 /etc/passwd`.',
            ],
        },
        {
            'id': 'lx-permissions',
            'title': 'Permissions, ownership, and becoming root',
            'next': 'lx-redirection',
            'concept': (
                'Every file has an owner, a group, and three sets of three bits: '
                'read, write and execute, for the owner, the group, and everyone '
                'else.\n\n'
                'Written as numbers each set is a digit from 0 to 7, where read '
                'is 4, write is 2 and execute is 1. So `755` is "owner may do '
                'everything, everyone else may read and execute", and `644` is '
                'the normal setting for a document.\n\n'
                'The bit that trips people is what those mean on a DIRECTORY, '
                'where they are not the same idea at all. Read means you can '
                'list the names in it. Execute means you can pass through it to '
                'reach what is inside. A directory with read but not execute '
                'lets you see the names and open nothing, which is a genuinely '
                'confusing state until you know it exists.\n\n'
                'All of this has one exception, and it is called **root**. Root '
                'is the administrative user, user id 0, and the permission bits '
                'simply do not apply to it: root reads, writes and traverses '
                'anything. You should not log in as root, and on a modern '
                'system you usually cannot. Instead you borrow root for one '
                'command with `sudo`. `sudo` runs a single command as root '
                'after checking you are allowed and asking for your own '
                'password, so the danger is scoped to that one line rather than '
                'a whole session. `sudo -i` gives you a root shell when you '
                'genuinely need several commands, and in bash or zsh `sudo !!` '
                'reruns the last command with sudo, which is the muscle-memory '
                'fix for "permission denied" (fish has no history expansion, so '
                'press Up and edit the line instead). Editing a system file '
                'wants `sudoedit '
                'file` rather than `sudo vim file`, because the former keeps '
                'your own editor config and drops root the moment you are done.'
            ),
            'examples': [
                {
                    'label': 'The arithmetic',
                    'code': ('r = 4   w = 2   x = 1\n'
                             '\n'
                             '755 = rwxr-xr-x   a program, or a directory\n'
                             '644 = rw-r--r--   an ordinary file\n'
                             '600 = rw-------   private: keys, secrets\n'
                             '700 = rwx------   a private directory'),
                    'note': 'ssh refuses to use a private key that is not 600, '
                            'and this is why.',
                },
                {
                    'label': 'Changing them',
                    'code': ('chmod 755 script.sh     absolute\n'
                             'chmod +x script.sh      add execute for everyone\n'
                             'chmod u+w,go-w file     per-set, relative\n'
                             'chown user:group file   change ownership\n'
                             'umask                   the bits new files do NOT\n'
                             '                        get, usually 022'),
                    'note': 'umask is subtractive, which is why the default of '
                            '022 produces 755 directories and 644 files.',
                },
                {
                    'label': 'Borrowing root, scoped to one command',
                    'code': ('sudo systemctl restart nginx   run one as root\n'
                             'sudo !!                        rerun the last\n'
                             '                               command with sudo\n'
                             'sudo -i                        a root shell, when\n'
                             '                               you need several\n'
                             'sudoedit /etc/hosts            edit a system file\n'
                             '                               without editing as\n'
                             '                               root'),
                    'note': 'sudo asks for YOUR password, not root\'s, and logs '
                            'what it ran. That audit trail is half the reason it '
                            'exists.',
                },
            ],
            'misconceptions': [
                'On a directory, `x` is not "run it". It is permission to '
                'traverse into it, and without it you cannot reach anything '
                'inside even if you can list the names.',
                'Making a script executable does not make it runnable. It also '
                'needs a shebang line, or to be passed to an interpreter.',
                'Permissions are on the file, not on the name. A symlink to a '
                'file you cannot read does not help you read it.',
                'root is not bound by the permission bits at all. They are a '
                'rule for everyone except user id 0, which is why a stray '
                '`sudo rm -rf` has nothing to stop it.',
                '`sudo command > /etc/file` does not write the file as root: '
                'the shell opens the redirect as YOU, before sudo runs. That is '
                'what `sudo tee` and `sudoedit` are for.',
                'setuid, setgid and the sticky bit exist and are a fourth digit. '
                'They are the Linux Advanced module\'s problem, not yours yet.',
            ],
            'try_it': [
                'Make a directory `chmod 600`, then try to `cd` into it. The '
                'error is the lesson.',
            ],
        },
        {
            'id': 'lx-redirection',
            'title': 'Three streams, and where they go',
            'next': 'lx-processes',
            'concept': (
                'Every process starts with three open file descriptors, and '
                'almost everything about shell plumbing follows from knowing '
                'their numbers. **0 is stdin**, **1 is stdout**, **2 is '
                'stderr**.\n\n'
                'Redirection points a descriptor somewhere else. `> file` sends '
                'stdout to a file, replacing it. `>>` appends instead. `2>` '
                'sends stderr. `<` reads stdin from a file. A pipe `|` connects '
                'one command\'s stdout to the next one\'s stdin.\n\n'
                'The reason errors keep appearing on your screen when you '
                'redirect output is that `>` only moves stream 1. Stream 2 is '
                'separate on purpose, so that a progress message and an error '
                'can go to different places. `2>&1` means "send stream 2 '
                'wherever stream 1 is currently going", and the ordering of that '
                'phrase is exactly why it must come after the redirect.'
            ),
            'examples': [
                {
                    'label': 'Pointing streams',
                    'code': ('cmd > out.txt        stdout to a file (replace)\n'
                             'cmd >> out.txt       append instead\n'
                             'cmd 2> err.txt       stderr to a file\n'
                             'cmd > out 2>&1       both to one file\n'
                             'cmd &> out           the same, bash shorthand\n'
                             'cmd < in.txt         stdin from a file\n'
                             'cmd 2>/dev/null      discard errors\n'
                             'a | b                a stdout into b stdin'),
                    'note': '/dev/null is a real file that discards everything '
                            'written to it and is empty when read.',
                },
                {
                    'label': 'Why ordering matters',
                    'code': ('cmd > file 2>&1     both go to file\n'
                             'cmd 2>&1 > file     stderr goes to the TERMINAL\n'
                             '\n'
                             'because 2>&1 copies where 1 points AT THAT MOMENT'),
                    'note': 'This is the most commonly half-understood thing in '
                            'shell redirection.',
                },
            ],
            'misconceptions': [
                '`2>&1` is not "and". It is "make 2 point where 1 currently '
                'points", which is why it must come after the redirect of 1.',
                '`>` truncates the file before the command runs, which is why '
                '`sort file > file` produces an empty file.',
                'A pipe connects stdout only. Errors still go to your terminal '
                'unless you redirect stream 2 as well.',
            ],
            'try_it': [
                'Run `ls /nope > out.txt` and see the error still on screen. '
                'Then `ls /nope > out.txt 2>&1` and see it in the file.',
            ],
        },
        {
            'id': 'lx-processes',
            'title': 'Processes, jobs and signals',
            'next': 'lx-env',
            'concept': (
                'A process is a running program with an ID, an owner, a parent, '
                'and those three streams. `ps aux` lists everything; `pgrep` '
                'finds one by name.\n\n'
                'Your shell manages foreground and background JOBS. `Ctrl-Z` '
                'suspends what is running, `bg` resumes it in the background, '
                '`fg` brings it back, and `jobs` lists them. Ending a command '
                'with `&` starts it in the background directly.\n\n'
                'Signals are how you talk to a process. `Ctrl-C` sends SIGINT, '
                'which politely asks it to stop and which a program may handle. '
                '`kill` sends SIGTERM, also polite. `kill -9` sends SIGKILL, '
                'which the process cannot catch and does not get to clean up '
                'from, which is why it should be the second thing you try, not '
                'the first.'
            ),
            'examples': [
                {
                    'label': 'Finding and stopping',
                    'code': ('ps aux | grep nginx   the portable way\n'
                             'pgrep -a nginx        the better way\n'
                             'kill 1234             ask it to stop (SIGTERM)\n'
                             'kill -9 1234          make it stop (SIGKILL)\n'
                             'pkill -f "python foo" match the whole command'),
                    'note': '`kill` does not mean kill. It means send a signal, '
                            'and the default one is a polite request.',
                },
                {
                    'label': 'Jobs in your shell',
                    'code': ('long-thing &     start in the background\n'
                             'Ctrl-Z           suspend the foreground job\n'
                             'bg               resume it in the background\n'
                             'fg               bring it back\n'
                             'jobs             list them\n'
                             'nohup cmd &      survive the terminal closing'),
                    'note': 'For anything that must survive a dropped '
                            'connection, tmux is a better answer than nohup.',
                },
            ],
            'misconceptions': [
                '`kill -9` is not the normal way to stop something. It denies '
                'the process any chance to flush buffers or remove lock files.',
                'A background job still dies when its terminal closes, unless '
                'you used nohup or disown. This is the problem tmux exists to '
                'solve.',
                '`ps aux | grep foo` always matches the grep itself. `pgrep` '
                'does not, which is the reason to prefer it.',
            ],
            'try_it': [
                'Run `sleep 300`, press Ctrl-Z, run `bg`, then `jobs`, then '
                '`fg`, then Ctrl-C.',
            ],
        },
        {
            'id': 'lx-env',
            'title': 'The environment, and PATH',
            'next': 'lx-help',
            'concept': (
                'Every process carries a set of environment variables, '
                'inherited from its parent. `env` shows them; `echo $HOME` '
                'reads one.\n\n'
                '`PATH` is the one that matters most. It is a colon-separated '
                'list of directories the shell searches, in order, when you type '
                'a command name. That is the entire mechanism, and it explains '
                'both "command not found" for a program you know is installed, '
                'and why `./script.sh` needs the `./`: the current directory is '
                'deliberately not on your PATH.\n\n'
                '`which` and `type` tell you what would actually run, which is '
                'the fastest way to settle an argument about versions.'
            ),
            'examples': [
                {
                    'label': 'Looking and setting',
                    'code': ('env                     everything\n'
                             'echo $PATH              the search list\n'
                             'which python3           what would run\n'
                             'type ls                 also finds aliases\n'
                             '\n'
                             'export FOO=bar          bash: set for children\n'
                             'set -x FOO bar          fish: the same idea'),
                    'note': 'Without export, a bash variable is not passed to '
                            'the commands you run.',
                },
            ],
            'misconceptions': [
                'The current directory is not on PATH, on purpose. If it were, '
                'a file called `ls` in a directory you cd into could hijack the '
                'real one.',
                'Changing a variable in a shell affects only that shell and what '
                'it starts afterwards. There is no way to reach back into the '
                'parent.',
                '`which` may disagree with what your shell runs, because aliases '
                'and functions come first. `type` sees those.',
            ],
            'try_it': [
                'Run `type -a python3` and see every version on your PATH, in '
                'the order they would be found.',
            ],
        },
        {
            'id': 'lx-help',
            'title': 'Answering your own questions',
            'concept': (
                'The single most useful habit is knowing where the answer lives '
                'before you reach for a search engine.\n\n'
                '`man cmd` is the manual, and the parts worth reading are '
                'SYNOPSIS at the top and EXAMPLES at the bottom, in that order. '
                'Press `/` to search inside it and `q` to leave, which are vi '
                'keys because `man` uses `less`.\n\n'
                '`cmd --help` is usually shorter and often enough. `apropos '
                'word` searches the manual descriptions when you know what you '
                'want but not what it is called, which is the case a search '
                'engine handles badly and this handles well.'
            ),
            'examples': [
                {
                    'label': 'Where to look',
                    'code': ('man ls          the manual\n'
                             'man 5 passwd    section 5: file formats\n'
                             'ls --help       usually shorter\n'
                             'apropos compress   find it by description\n'
                             'type cmd        is it a program, alias, builtin'),
                    'note': 'Sections matter: `man 1 printf` is the command, '
                            '`man 3 printf` is the C function.',
                },
                {
                    'label': 'Reading a synopsis',
                    'code': ('SYNOPSIS\n'
                             '  ls [OPTION]... [FILE]...\n'
                             '\n'
                             '[ ] optional    ... may repeat\n'
                             'plain text must be typed literally'),
                    'note': 'This notation is consistent across every man page, '
                            'so learning it once pays out forever.',
                },
            ],
            'misconceptions': [
                'A man page is not meant to be read top to bottom. Jump to '
                'EXAMPLES first; most of them have one.',
                'Some commands have no man page because they are shell builtins. '
                '`help cd` in bash is where those live.',
            ],
            'try_it': [
                'Run `man ls`, press `/` and search for `-t`, then press `q`. '
                'Those are the same keys `less` uses.',
            ],
        },
    ],

    'drills': [
        {'id': 'lx-cmd-mkdirp', 'type': 'command', 'answer': 'mkdir -p a/b/c',
         'prompt': 'Create the nested directory a/b/c in one command.',
         'teach': '-p makes intermediate directories and does not complain if '
                  'they already exist, which is why scripts always use it.'},
        {'id': 'lx-cmd-lsl', 'type': 'command', 'answer': 'ls -la',
         'accepts': ['ls -al', 'ls -l -a'],
         'prompt': 'List everything in this directory including hidden files, '
                   'in long form.',
         'teach': '-a is what includes dotfiles. Anything starting with a dot '
                  'is hidden by convention only, and half of what configures '
                  'a machine lives there.'},
        {'id': 'lx-cmd-lst', 'type': 'command', 'answer': 'ls -lt',
         'prompt': 'List in long form with the newest files first.',
         'teach': 'ls -ltr reverses it, putting the newest last, which is what '
                  'you want when the list is longer than your screen.'},
        {'id': 'lx-cmd-cpr', 'type': 'command', 'answer': 'cp -r src dst',
         'prompt': 'Copy the directory src to dst.',
         'teach': 'Without -r, cp refuses and says "omitting directory".'},

        # viewing files
        {'id': 'lx-cmd-less', 'type': 'command', 'answer': 'less /var/log/syslog',
         'prompt': 'Page through the log file /var/log/syslog.',
         'teach': 'less loads only what it shows, so it opens a huge file '
                  'instantly. Its keys are vi keys: / searches, q quits.'},
        {'id': 'lx-cmd-head', 'type': 'command', 'answer': 'head -n 20 access.log',
         'prompt': 'Show the first 20 lines of access.log.',
         'teach': 'head is the top, tail is the bottom, and -n sets how many.'},
        {'id': 'lx-cmd-tailf', 'type': 'command', 'answer': 'tail -f access.log',
         'prompt': 'Watch access.log live as new lines are written.',
         'teach': 'tail -f follows the file and does not return; Ctrl-C leaves '
                  'it. This is how you watch a service while you poke it.'},
        {'id': 'lx-cmd-wc', 'type': 'command', 'answer': 'wc -l access.log',
         'prompt': 'Count the lines in access.log.',
         'teach': 'wc -l answers "how big is this" faster than reading it, and '
                  'it ends a great many pipelines.'},
        {'id': 'lx-cmd-back', 'type': 'command', 'answer': 'cd -',
         'prompt': 'Return to the directory you were in before this one.',
         'teach': 'The dash means the previous directory, and it prints where '
                  'it took you. Same convention as git switch -.'},
        {'id': 'lx-cmd-sudo', 'type': 'command',
         'answer': 'sudo systemctl restart nginx',
         'prompt': 'Restart the nginx service, which needs root.',
         'teach': 'sudo runs one command as root after asking for your own '
                  'password. The danger is scoped to that single line.'},
        {'id': 'lx-cmd-sudo-bang', 'type': 'command', 'answer': 'sudo !!',
         'prompt': 'Rerun the command you just ran, this time as root.',
         'teach': 'The muscle-memory fix for "permission denied": !! is the '
                  'previous command, and sudo puts root in front of it.'},
        {'id': 'lx-cmd-sudoedit', 'type': 'command', 'answer': 'sudoedit /etc/hosts',
         'prompt': 'Edit the system file /etc/hosts with elevated rights.',
         'teach': 'sudoedit keeps your own editor config and drops root the '
                  'moment you finish, unlike sudo vim which runs the editor '
                  'itself as root.'},
        {'id': 'lx-cmd-chmod-x', 'type': 'command', 'answer': 'chmod +x script.sh',
         'prompt': 'Make script.sh executable.',
         'teach': '+x adds execute for everyone without touching the other '
                  'bits. A script that will not run despite being right there '
                  'is almost always missing it.'},
        {'id': 'lx-cmd-chmod-600', 'type': 'command', 'answer': 'chmod 600 key',
         'prompt': 'Make the file "key" readable and writable only by its '
                   'owner, using the numeric form.',
         'teach': 'ssh refuses to use a private key with looser permissions '
                  'than this.'},
        {'id': 'lx-cmd-chmod-755', 'type': 'command', 'answer': 'chmod 755 bin',
         'prompt': 'Give the directory "bin" the usual permissions: all may enter and read, only you may change.',
         'teach': 'Read as three digits: 7 for you, 5 for group, 5 for '
                  'others. Each is r=4 w=2 x=1 summed, and x on a directory '
                  'means may enter.'},
        {'id': 'lx-cmd-du', 'type': 'command', 'answer': 'du -sh .',
         'prompt': 'Show the total size of the current directory, in a '
                   'human-readable form.',
         'teach': 'The size shown by ls -l for a directory is not this.'},
        {'id': 'lx-cmd-redirect', 'type': 'command', 'answer': 'cmd > out.txt',
         'prompt': "Send cmd's normal output to out.txt, replacing whatever was there.",
         'teach': 'One angle bracket truncates the file before the command '
                  'even runs, which is why redirecting a file onto itself '
                  'empties it.'},
        {'id': 'lx-cmd-append', 'type': 'command', 'answer': 'cmd >> out.txt',
         'prompt': "Append cmd's normal output to out.txt instead of replacing it.",
         'teach': 'Doubling the bracket is the difference between adding to a '
                  'log and destroying it.'},
        {'id': 'lx-cmd-stderr', 'type': 'command', 'answer': 'cmd 2> err.txt',
         'prompt': 'Send only the error stream to err.txt. Use "cmd".',
         'teach': 'Stream 2 is separate on purpose, so progress and errors can '
                  'go to different places.'},
        {'id': 'lx-cmd-both', 'type': 'command', 'answer': 'cmd > out.txt 2>&1',
         'prompt': 'Send both output and errors to out.txt, in the portable '
                   'order. Use "cmd".',
         'teach': 'The order matters: 2>&1 copies wherever 1 points at that '
                  'moment, so putting it first sends errors to the terminal.'},
        {'id': 'lx-cmd-devnull', 'type': 'command', 'answer': 'cmd 2>/dev/null',
         'accepts': ['cmd 2> /dev/null'],
         'prompt': 'Throw away only the error output of cmd.',
         'teach': "The 2 is stderr's file descriptor. Errors flow separately "
                  'from output, which is why they still reach your screen '
                  'through a pipe.'},
        {'id': 'lx-cmd-pgrep', 'type': 'command', 'answer': 'pgrep -a nginx',
         'prompt': 'Find the running nginx processes, showing their command '
                   'lines, without matching your own search.',
         'teach': 'ps aux | grep always matches the grep itself. pgrep does '
                  'not.'},
        {'id': 'lx-cmd-kill', 'type': 'command', 'answer': 'kill 1234',
         'prompt': 'Politely ask process 1234 to stop.',
         'teach': 'That is SIGTERM. kill -9 is SIGKILL and denies it any chance '
                  'to clean up, so it is the second thing you try.'},
        {'id': 'lx-cmd-bg', 'type': 'command', 'answer': 'sleep 300 &',
         'prompt': 'Start a 300 second sleep in the background.',
         'teach': 'The ampersand starts it without waiting. jobs lists what '
                  'you have running, fg brings one back, and closing the '
                  'terminal still kills it.'},
        {'id': 'lx-cmd-which', 'type': 'command', 'answer': 'type -a python3',
         'prompt': 'Show every python3 that would be found, aliases and builtins included.',
         'teach': 'which misses aliases and shell functions; type sees them.'},
        {'id': 'lx-cmd-path', 'type': 'command', 'answer': 'echo $PATH',
         'prompt': 'Print the list of directories your shell searches for '
                   'commands.',
         'teach': 'Searched left to right, first hit wins. When the wrong '
                  'version of something runs, the answer is almost always in '
                  "this list's order."},
        {'id': 'lx-cmd-apropos', 'type': 'command', 'answer': 'apropos compress',
         'prompt': 'Find commands whose manual description mentions compress, '
                   'when you do not know the command name.',
         'teach': 'It searches the one-line descriptions of every manual '
                  'page, which is the only way in when you know the task and '
                  'not the name.'},
        {'id': 'lx-cmd-mansection', 'type': 'command', 'answer': 'man 5 passwd',
         'prompt': 'Read the manual page for the passwd FILE FORMAT rather than '
                   'the passwd command.',
         'teach': 'Section 1 is commands, 5 is file formats, 8 is admin. '
                  '`man 3 printf` versus `man 1 printf` is the classic case.'},
        {'id': 'lx-cmd-lnsym', 'type': 'command', 'answer': 'ln -s target link',
         'prompt': 'Create a symbolic link called "link" pointing at "target".',
         'teach': 'Without -s you get a hard link, which is a second name for '
                  'the same data rather than a pointer to a path.'},
    ],

    'challenges': [
        {
            'id': 'lx-tidy',
            'title': 'Tidy a directory',
            'goal': 'Use mkdir, mv and rm to reorganise a small tree.',
            'setup': {'kind': 'sandbox', 'tree': {
                'notes.txt': 'keep me\n',
                'draft.tmp': 'delete me\n',
                'report.log': 'log line\n',
                'old.log': 'older\n',
            }},
            'solution': {'shell': 'mkdir -p logs && mv *.log logs/ '
                                  '&& rm draft.tmp'},
            'steps': [
                {'instruction': 'Make a directory called logs.',
                 'hint': 'mkdir logs'},
                {'instruction': 'Move both .log files into it.',
                 'hint': 'mv *.log logs/'},
                {'instruction': 'Delete draft.tmp.',
                 'hint': 'rm draft.tmp, after ls-ing it first'},
            ],
            'free': 'Move both .log files into a new logs/ directory and delete '
                    'draft.tmp, leaving notes.txt alone.',
            'verify': {'kind': 'sandbox', 'expect': {
                'is_dir': ['logs'],
                'exists': ['logs/report.log', 'logs/old.log', 'notes.txt'],
                'missing': ['draft.tmp', 'report.log'],
            }},
            'fallback': 'self',
        },
        {
            'id': 'lx-permissions',
            'title': 'Set permissions correctly',
            'goal': 'Make a script runnable and a key private, using both forms '
                    'of chmod.',
            'setup': {'kind': 'sandbox', 'tree': {
                'run.sh': {'content': '#!/bin/sh\necho hi\n', 'mode': '644'},
                'id_key': {'content': 'PRIVATE KEY\n', 'mode': '644'},
                'public/': None,
            }},
            'solution': {'shell': 'chmod +x run.sh && chmod 600 id_key '
                                  '&& chmod 755 public'},
            'steps': [
                {'instruction': 'Make run.sh executable.',
                 'hint': 'chmod +x run.sh'},
                {'instruction': 'Make id_key readable and writable only by its '
                                'owner.',
                 'hint': 'chmod 600 id_key'},
                {'instruction': 'Give the public directory 755.',
                 'hint': 'everyone may enter and list, only you may change'},
            ],
            'free': 'Make run.sh executable, id_key mode 600, and public mode '
                    '755.',
            'verify': {'kind': 'sandbox', 'expect': {
                'executable': ['run.sh'],
                'mode': {'id_key': '600', 'public': '755'},
            }},
            'fallback': 'self',
        },
        {
            'id': 'lx-links',
            'title': 'Make a symbolic link',
            'goal': 'Create a stable name that points at a versioned file, '
                    'which is how most of /usr works.',
            'setup': {'kind': 'sandbox', 'tree': {
                'app-1.2.0/': None,
                'app-1.2.0/run': {'content': 'v1.2.0\n', 'mode': '755'},
            }},
            'solution': {'shell': 'ln -s app-1.2.0 current'},
            'steps': [
                {'instruction': 'Create a symbolic link called current that '
                                'points at the versioned directory.',
                 'hint': 'ln -s app-1.2.0 current'},
            ],
            'free': 'Create a symlink named current pointing at app-1.2.0.',
            'verify': {'kind': 'sandbox',
                       'expect': {'is_symlink': {'current': 'app-1.2.0'}}},
            'fallback': 'self',
        },
        {'id': 'lx-find-and-count',
         'title': 'Count what you found',
         'goal': 'Compose two commands with a pipe: list the matching '
                 'files, then count the lines. Write the number into a '
                 'file.',
         'setup': {'kind': 'sandbox',
                   'tree': {'a.log': 'x\n',
                            'b.log': 'y\n',
                            'c.txt': 'z\n',
                            'sub/d.log': 'w\n',
                            'sub/e.md': 'v\n'}},
         'solution': {'shell': 'find . -name "*.log" | wc -l > count.txt'},
         'steps': [{'instruction': 'List every .log file underneath this '
                                   'directory, including the one in sub/.',
                    'hint': 'find . -name "*.log"'},
                   {'instruction': 'Pipe that into something that counts '
                                   'lines.',
                    'hint': 'wc -l'},
                   {'instruction': 'Redirect the number into count.txt.',
                    'hint': 'the whole pipeline, then > count.txt'}],
         'free': 'Put the number of .log files under this directory, '
                 'including sub/, into count.txt.',
         'verify': {'kind': 'sandbox',
                    'expect': {'file_contains': {'count.txt': '3'}}},
         'fallback': 'self'},
        {'id': 'lx-script-runnable',
         'title': 'Make a script runnable',
         'goal': 'A script you cannot execute is a text file. Give it a '
                 'shebang and the execute bit, and prove it runs.',
         'setup': {'kind': 'sandbox', 'tree': {'greet.sh': 'echo hello\n'}},
         'solution': {'shell': 'printf "#!/bin/sh\\necho hello\\n" > '
                               'greet.sh && chmod +x greet.sh && '
                               './greet.sh > out.txt'},
         'steps': [{'instruction': 'Give greet.sh a shebang line so the '
                                   'kernel knows what runs it.',
                    'hint': '#!/bin/sh as the first line'},
                   {'instruction': 'Add the execute bit.',
                    'hint': 'chmod +x greet.sh'},
                   {'instruction': 'Run it with ./greet.sh and send its '
                                   'output to out.txt.',
                    'hint': './greet.sh > out.txt'}],
         'free': 'Make greet.sh a runnable script and capture its output '
                 'in out.txt.',
         'verify': {'kind': 'sandbox',
                    'expect': {'executable': ['greet.sh'],
                               'file_contains': {'greet.sh': '#!',
                                                 'out.txt': 'hello'}}},
         'fallback': 'self'},
        {'id': 'lx-streams',
         'title': 'Separate the errors from the output',
         'goal': 'stdout and stderr are two different streams. Send them '
                 'to two different files from one command.',
         'setup': {'kind': 'sandbox', 'tree': {'there.txt': 'here\n'}},
         'solution': {'shell': 'ls there.txt missing.txt > found.txt 2> '
                               'errors.txt'},
         'steps': [{'instruction': 'Run ls on two names: there.txt, which '
                                   'exists, and missing.txt, which does '
                                   'not.',
                    'hint': 'ls there.txt missing.txt'},
                   {'instruction': 'Send the normal output to found.txt.',
                    'hint': '> found.txt'},
                   {'instruction': 'Send the error to errors.txt in the '
                                   'same command.',
                    'hint': '2> errors.txt'}],
         'free': 'From one ls of there.txt and missing.txt, put the output '
                 'in found.txt and the error in errors.txt.',
         'verify': {'kind': 'sandbox',
                    'expect': {'file_contains': {'found.txt': 'there.txt',
                                                 'errors.txt': 'missing.txt'},
                               'file_lacks': {'found.txt': 'missing.txt'}}},
         'fallback': 'self'},
        {'id': 'lx-copy-tree',
         'title': 'Copy a directory, and know why -r',
         'goal': 'Copy a whole directory and then prove the copy is '
                 'independent of the original.',
         'setup': {'kind': 'sandbox',
                   'tree': {'src/one.txt': 'first\n',
                            'src/two.txt': 'second\n'}},
         'solution': {'shell': 'cp -r src backup && echo changed > '
                               'src/one.txt'},
         'steps': [{'instruction': 'Copy the whole src directory to a new '
                                   'one called backup.',
                    'hint': 'cp -r src backup. Without -r, cp refuses a '
                            'directory'},
                   {'instruction': 'Change src/one.txt so it says changed.',
                    'hint': 'echo changed > src/one.txt'},
                   {'instruction': 'The copy should still say first. A '
                                   'copy is not a link.',
                    'hint': 'cat backup/one.txt to check'}],
         'free': 'Copy src to backup, then change src/one.txt, leaving the '
                 'backup as it was.',
         'verify': {'kind': 'sandbox',
                    'expect': {'is_dir': ['backup'],
                               'file_contains': {'backup/one.txt': 'first',
                                                 'backup/two.txt': 'second',
                                                 'src/one.txt': 'changed'}}},
         'fallback': 'self'},
        {'id': 'lx-hidden',
         'title': 'The files ls does not show you',
         'goal': 'Most of what configures a machine is hidden. Find a '
                 'dotfile you were not shown and read a value out of it.',
         'setup': {'kind': 'sandbox',
                   'tree': {'.settings': 'theme=dark\n'
                                         'font=mono\n'
                                         'speed=fast\n',
                            'readme.txt': 'nothing useful here\n'}},
         'solution': {'shell': 'grep font .settings | cut -d= -f2 > '
                               'answer.txt'},
         'steps': [{'instruction': 'List everything here, hidden files '
                                   'included, and find the dotfile.',
                    'hint': 'ls -a'},
                   {'instruction': 'Pull out the line that mentions font.',
                    'hint': 'grep font .settings'},
                   {'instruction': 'Put only the value, not the whole '
                                   'line, into answer.txt.',
                    'hint': 'cut -d= -f2'}],
         'free': 'Write the value of the font setting, and nothing else, '
                 'into answer.txt.',
         'verify': {'kind': 'sandbox',
                    'expect': {'file_contains': {'answer.txt': 'mono'},
                               'file_lacks': {'answer.txt': 'font='}}},
         'fallback': 'self'},
        {'id': 'lx-rename-many',
         'title': 'Rename a batch without a loop you regret',
         'goal': 'Rename several files at once using a shell loop and '
                 'parameter expansion rather than typing each one.',
         'setup': {'kind': 'sandbox',
                   'tree': {'one.bak': 'a\n',
                            'two.bak': 'b\n',
                            'three.bak': 'c\n'}},
         'solution': {'shell': 'for f in *.bak; do mv "$f" '
                               '"${f%.bak}.txt"; done'},
         'steps': [{'instruction': 'Loop over every .bak file in this '
                                   'directory.',
                    'hint': 'for f in *.bak; do ... done'},
                   {'instruction': 'Inside the loop, build the new name by '
                                   'stripping the old suffix.',
                    'hint': '${f%.bak} removes .bak from the end'},
                   {'instruction': 'Move each file to its new name, '
                                   'quoting the variable.',
                    'hint': 'mv "$f" "${f%.bak}.txt"'}],
         'free': 'Rename every .bak file here to the same name with .txt '
                 'instead.',
         'verify': {'kind': 'sandbox',
                    'expect': {'exists': ['one.txt',
                                          'two.txt',
                                          'three.txt'],
                               'missing': ['one.bak',
                                           'two.bak',
                                           'three.bak']}},
         'fallback': 'self'},

        {'id': 'lx-read-log',
         'title': 'Answer questions about a file without editing it',
         'goal': 'A file too long to read at once. Pull the answer out of it '
                 'with head, tail and wc rather than opening an editor.',
         'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {'.keep': ''}},
         'solution': {'shell':
             'for i in $(seq 1 200); do echo "line $i"; done > big.log && '
             'head -n 3 big.log > first.txt && '
             'tail -n 3 big.log > last.txt && '
             'wc -l big.log | awk \'{print $1}\' > count.txt'},
         'steps': [{'instruction': 'Make a 200-line file to work on.',
                    'hint': 'for i in $(seq 1 200); do echo "line $i"; done '
                            '> big.log'},
                   {'instruction': 'Write its first three lines to first.txt '
                                   'and its last three to last.txt.',
                    'hint': 'head -n 3 big.log; tail -n 3 big.log'},
                   {'instruction': 'Write just the line count to count.txt.',
                    'hint': 'wc -l, then pull off the number'}],
         'free': 'Produce first.txt with the first three lines, last.txt with '
                 'the last three, and count.txt holding just the line count of '
                 'a 200-line file.',
         'verify': {'kind': 'sandbox', 'expect': {
             'file_contains': {'first.txt': 'line 1', 'last.txt': 'line 200'},
             'file_equals': {'count.txt': '200'},
             'file_lacks': {'first.txt': 'line 200'}}},
         'fallback': 'self'},

        {'id': 'lx-umask',
         'title': 'Work out what umask did',
         'goal': 'umask subtracts from the default permissions of new files. '
                 'Set one, create things, and read the result back.',
         'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {'.keep': ''}},
         'solution': {'shell':
             'umask 077 && touch private.txt && mkdir privatedir && '
             'umask 022 && touch shared.txt && mkdir shareddir && '
             'stat -c "%n %a" private.txt privatedir shared.txt shareddir '
             '> modes.txt && umask > current.txt'},
         'steps': [{'instruction': 'Set the umask to 077, then create a file '
                                   'and a directory.',
                    'hint': 'umask 077; touch private.txt; mkdir privatedir'},
                   {'instruction': 'Set it to 022 and create another of '
                                   'each.'},
                   {'instruction': 'Record the mode of all four with stat, '
                                   'into modes.txt.',
                    'hint': 'stat -c "%n %a" private.txt privatedir ...'},
                   {'instruction': 'Save the current umask to current.txt, '
                                   'and note that files start from 666 and '
                                   'directories from 777.'}],
         'free': 'Produce modes.txt showing a 600 file and 700 directory made '
                 'under umask 077, and a 644 file and 755 directory made '
                 'under 022.',
         'verify': {'kind': 'sandbox', 'expect': {
             'file_contains': {'modes.txt': ['private.txt 600',
                                             'privatedir 700',
                                             'shared.txt 644',
                                             'shareddir 755']},
             'mode': {'private.txt': '600', 'shared.txt': '644'}}},
         'fallback': 'self'},

        {'id': 'lx-jobs-signals',
         'title': 'Background it, then signal it',
         'goal': 'Job control is a few commands and one number. Use them on '
                 'processes you started yourself.',
         'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {'.keep': ''}},
         'solution': {'shell':
             'sleep 40 &\n'
             'first=$!\n'
             'sleep 41 &\n'
             'second=$!\n'
             'jobs > jobs.txt 2>&1\n'
             'echo "$first" > firstpid.txt\n'
             'kill -TERM "$first"\n'
             'sleep 1\n'
             'ps -o pid= -p "$first" > gone.txt 2>/dev/null\n'
             'ps -o pid= -p "$second" > alive.txt 2>/dev/null\n'
             'kill "$second" 2>/dev/null\n'
             'kill -l > signals.txt\n'
             'true'},
         'steps': [{'instruction': 'Start two background sleeps and record '
                                   'the first pid.',
                    'hint': 'sleep 40 & first=$!'},
                   {'instruction': 'Write the jobs table to jobs.txt.',
                    'hint': 'jobs > jobs.txt'},
                   {'instruction': 'Send TERM to the first one only, then '
                                   'check which of the two is still there.',
                    'hint': 'kill -TERM "$first"; ps -o pid= -p "$first"'},
                   {'instruction': 'List every signal name into signals.txt.',
                    'hint': 'kill -l'}],
         'free': 'Produce jobs.txt, firstpid.txt, an empty gone.txt, a '
                 'non-empty alive.txt, and signals.txt listing the signal '
                 'names.',
         'verify': {'kind': 'sandbox', 'expect': {
             'is_file': ['jobs.txt', 'firstpid.txt', 'gone.txt', 'alive.txt'],
             'file_equals': {'gone.txt': ''},
             'file_contains': {'signals.txt': ['TERM', 'KILL', 'HUP']}}},
         'fallback': 'self'},

        {'id': 'lx-env-path',
         'title': 'Put your own directory on PATH',
         'goal': 'Environment and PATH are how the shell decides what runs. '
                 'Change both deliberately, and prove which one won.',
         'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {'.keep': ''}},
         'solution': {'shell':
             'mkdir -p bin\n'
             'printf "#!/bin/bash\\necho custom greeting\\n" > bin/greet\n'
             'chmod +x bin/greet\n'
             'PATH="$PWD/bin:$PATH" greet > ran.txt\n'
             'PATH="$PWD/bin:$PATH" command -v greet > which.txt\n'
             'MYVAR=hello bash -c \'echo "$MYVAR"\' > exported.txt\n'
             'bash -c \'echo "MYVAR is [${MYVAR:-unset}]"\' > notexported.txt\n'
             'true'},
         'steps': [{'instruction': 'Make a bin directory and put an '
                                   'executable script called greet in it.',
                    'hint': 'printf into bin/greet, then chmod +x bin/greet'},
                   {'instruction': 'Run it by name with your bin directory '
                                   'prepended to PATH, saving output to '
                                   'ran.txt.',
                    'hint': 'PATH="$PWD/bin:$PATH" greet > ran.txt'},
                   {'instruction': 'Record where the shell resolved it to, in '
                                   'which.txt.',
                    'hint': 'command -v greet'},
                   {'instruction': 'Show a variable set for one command '
                                   'reaching its child, and the same variable '
                                   'absent from a separate command.',
                    'hint': 'MYVAR=hello bash -c ...'}],
         'free': 'Produce ran.txt from a script found via a modified PATH, '
                 'which.txt showing where it resolved, and exported.txt and '
                 'notexported.txt showing a variable reaching one child and '
                 'not another.',
         'verify': {'kind': 'sandbox', 'expect': {
             'executable': ['bin/greet'],
             'file_equals': {'ran.txt': 'custom greeting',
                             'exported.txt': 'hello'},
             'file_contains': {'which.txt': 'bin/greet',
                               'notexported.txt': 'unset'}}},
         'fallback': 'self'},
                  ],

    'quiz': [
        {'id': 'lq-dir-x', 'type': 'mcq',
         'prompt': 'A directory is mode 600. You own it. What can you do?',
         'answer': 'List the names in it, but not open anything inside.',
         'distractors': ['Everything, since you own it.',
                         'Nothing at all; you cannot even list it.',
                         'Open files inside, but not list them.'],
         'teach': 'On a directory, x means traverse. Read without execute lets '
                  'you see the names and reach none of them.'},

        {'id': 'lq-2gt1', 'type': 'mcq',
         'prompt': 'What does `cmd 2>&1 > file` do?',
         'answer': 'Errors go to the terminal, normal output goes to the file.',
         'distractors': ['Both go to the file.',
                         'Both go to the terminal.',
                         'It is a syntax error.'],
         'teach': '2>&1 copies where 1 points at that moment, and at that moment '
                  'it still points at the terminal. Put it after the redirect.'},

        {'id': 'lq-mv', 'type': 'mcq',
         'prompt': 'Why is renaming a 10GB file instant?',
         'answer': 'A rename changes where a name points; no data moves.',
         'distractors': ['The filesystem copies it in the background.',
                         'It is not instant; it just appears to be.',
                         'Only on SSDs, because of the way they write.'],
         'teach': 'Move and rename are the same operation, which is why one '
                  'command does both. Moving across filesystems does copy.'},

        {'id': 'lq-path', 'type': 'mcq',
         'prompt': 'Why do you have to type ./script.sh rather than script.sh?',
         'answer': 'The current directory is deliberately not on PATH.',
         'distractors': ['The file is not executable.',
                         'Scripts always need a path prefix.',
                         'PATH only contains system directories.'],
         'teach': 'If . were on PATH, a file called ls in a directory you cd '
                  'into could hijack the real one.'},

        {'id': 'lq-kill9', 'type': 'mcq',
         'prompt': 'Why should kill -9 be the second thing you try?',
         'answer': 'SIGKILL cannot be caught, so the process cannot clean up.',
         'distractors': ['It requires root.',
                         'It is slower than a plain kill.',
                         'It kills the parent process too.'],
         'teach': 'Plain kill sends SIGTERM, which asks. -9 removes the process '
                  'without letting it flush buffers or remove lock files.'},

        {'id': 'lq-truncate', 'type': 'mcq',
         'prompt': 'Why does `sort file > file` leave you with an empty file?',
         'answer': 'The shell truncates the file before sort ever reads it.',
         'distractors': ['sort cannot read and write the same file.',
                         'The redirect happens after sort finishes.',
                         'It works; the file is only empty until sort exits.'],
         'teach': 'Redirection is set up by the shell before the command runs. '
                  'Write to a different file, or use a tool with -i.'},

        {'id': 'lq-hidden', 'type': 'mcq',
         'prompt': 'What makes a file hidden?',
         'answer': 'Its name starts with a dot, and ls skips those by default.',
         'distractors': ['A hidden attribute in the filesystem.',
                         'Permissions that deny read to others.',
                         'Being inside a directory beginning with a dot.'],
         'teach': 'That is the whole mechanism. There is nothing protective '
                  'about it.'},

        {'id': 'lq-pgrep', 'type': 'mcq',
         'prompt': 'Why prefer pgrep over `ps aux | grep name`?',
         'answer': 'The grep pipeline always matches itself.',
         'distractors': ['pgrep is faster on large systems.',
                         'ps aux does not show other users.',
                         'grep cannot match a command line.'],
         'teach': 'You have seen the extra line and wondered which one was '
                  'real. pgrep removes the question.'},

        {'id': 'lq-umask', 'type': 'mcq',
         'prompt': 'A umask of 022 produces what mode for a new directory?',
         'answer': '755',
         'distractors': ['022', '644', '777'],
         'teach': 'umask is subtractive: it names the bits new things do NOT '
                  'get. 777 minus 022 is 755.'},
    ],
}
