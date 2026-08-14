"""Linux Advanced: the deep model, and where the pentest-relevant material is.

Basics taught the permission bits, the three streams and what a process is.
This module goes back to each of those and shows the part that was deliberately
left out: the fourth permission digit, what a file descriptor actually is, what
signals really do, and the two subsystems that own everything else on a modern
machine, which are systemd and the network stack.

Two things here are worth the whole module on their own. The **setuid family**
is the answer to half of "how did they get root", and `2>&1` **ordering** is
the most commonly half-understood thing in shell redirection, which is why it
was introduced in Basics and is finished properly here.

Challenges use the sandbox adapter, and the ones that can be verified offline
are. systemd and network state belong to the machine rather than to a
directory, so those are self-marked and say so.
"""

MODULE = {
    'id': 'linuxadv',
    'title': 'Linux Advanced',
    'group': 'Linux',
    'blurb': 'Special bits, descriptors, signals, mounts, systemd, network state.',
    'context': 'You are at a shell prompt on a systemd machine, with sudo available where a task needs it.',
    'prereqs': ['linux'],
    'adapter': 'sandbox',
    'estimate': '6-8 hours',
    'order': 42,

    'lessons': [
        {
            'id': 'la-setuid',
            'title': 'The fourth digit',
            'next': 'la-caps',
            'concept': (
                'Basics said permissions were three digits. There is a fourth, '
                'in front, and it holds three bits that change who a program '
                'runs as and how a directory behaves.\n\n'
                '**setuid (4)** on an executable makes it run as its owner '
                'rather than as you. That is how `passwd` can edit '
                '`/etc/shadow` while you cannot. **setgid (2)** does the same '
                'for the group, and on a DIRECTORY it means new files inherit '
                'that directory\'s group, which is how shared project '
                'directories work. **sticky (1)** on a directory means only the '
                'owner of a file may delete it, which is why `/tmp` is `1777` '
                'and you cannot remove someone else\'s temp file.\n\n'
                'setuid is the one to understand properly. A setuid-root binary '
                'that can be made to run arbitrary commands, read arbitrary '
                'files or write arbitrary paths is a root shell, and finding '
                'them is the first thing anyone does on a machine they just '
                'landed on.'
            ),
            'examples': [
                {
                    'label': 'Reading them',
                    'code': ('-rwsr-xr-x  root root  /usr/bin/passwd\n'
                             '   ^ s where owner x would be: SETUID\n'
                             '\n'
                             'drwxrwsr-x  me  team   shared/\n'
                             '      ^ s in the group slot: SETGID\n'
                             '\n'
                             'drwxrwxrwt  root root  /tmp\n'
                             '         ^ t at the end: STICKY'),
                    'note': 'A capital S or T means the bit is set but the '
                            'underlying x is not, which is usually a mistake.',
                },
                {
                    'label': 'Setting and finding',
                    'code': ('chmod 4755 prog     setuid\n'
                             'chmod 2775 dir      setgid directory\n'
                             'chmod 1777 dir      sticky\n'
                             'chmod u+s / g+s / +t   the symbolic forms\n'
                             '\n'
                             'find / -perm -4000 -type f 2>/dev/null\n'
                             '  every setuid binary on the machine'),
                    'note': 'That find is the single most-run command in '
                            'privilege escalation, in both directions.',
                },
            ],
            'misconceptions': [
                'setuid on a shell script does nothing on Linux. The kernel '
                'ignores it for interpreted files, which is a deliberate '
                'defence.',
                'setuid means "run as the OWNER", not "run as root". It is only '
                'a root escalation when root owns the file.',
                'The sticky bit on a file is meaningless on modern Linux. It '
                'only does anything on directories.',
                'A capital `S` in the listing means setuid without execute, '
                'which is almost always a chmod typo rather than a clever '
                'trick.',
            ],
            'try_it': [
                'Run `find /usr/bin -perm -4000 -type f 2>/dev/null` and look '
                'at what is setuid on your own machine.',
            ],
        },
        {
            'id': 'la-caps',
            'title': 'ACLs and capabilities',
            'next': 'la-fds',
            'concept': (
                'Two systems exist because the classic owner-group-other model '
                'is too coarse for real machines.\n\n'
                '**ACLs** let you grant a specific user access to a specific '
                'file without changing its group. `getfacl` reads them, '
                '`setfacl` writes them, and a `+` at the end of an `ls -l` '
                'permission string is the clue that a file has one. If '
                'permissions look right and access still fails, check for a '
                '`+`.\n\n'
                '**Capabilities** split root\'s powers into pieces, so a '
                'program that only needs to bind port 80 can be given '
                '`cap_net_bind_service` instead of being setuid root. `getcap` '
                'reads them. This is strictly better than setuid and is why '
                'modern distributions have fewer setuid binaries than they used '
                'to, but it also means a machine can have a privilege path that '
                '`find -perm -4000` does not show.'
            ),
            'examples': [
                {
                    'label': 'ACLs',
                    'code': ('ls -l file\n'
                             '-rw-r--r--+ 1 me me ...    <- note the +\n'
                             '\n'
                             'getfacl file               read them\n'
                             'setfacl -m u:alice:rw file grant alice\n'
                             'setfacl -x u:alice file    remove her'),
                    'note': 'The `+` is easy to miss and is the whole clue.',
                },
                {
                    'label': 'Capabilities',
                    'code': ('getcap -r / 2>/dev/null    every file with caps\n'
                             'getcap /usr/bin/ping\n'
                             '  cap_net_raw=ep\n'
                             '\n'
                             'setcap cap_net_bind_service=+ep ./server'),
                    'note': '`cap_dac_read_search` on anything that reads files '
                            'is effectively read-anything, and is worth looking '
                            'for.',
                },
            ],
            'misconceptions': [
                'A capability is not the same as setuid. It grants one specific '
                'power rather than the whole identity, which is the point.',
                'Copying a file does not copy its capabilities, and often not '
                'its ACL either, so a "why does it work in place but not after '
                'I moved it" question usually ends here.',
                '`find -perm -4000` misses capability-based privilege entirely. '
                'Check `getcap -r /` as well.',
            ],
            'try_it': [
                'Run `getcap -r /usr/bin 2>/dev/null` and see which of your '
                'binaries hold specific powers.',
            ],
        },
        {
            'id': 'la-fds',
            'title': 'File descriptors, properly',
            'next': 'la-signals',
            'concept': (
                'Basics said 0, 1 and 2 are stdin, stdout and stderr. What they '
                'actually are is indexes into a per-process table of open '
                'files, and once you hold that, redirection stops being '
                'special syntax.\n\n'
                '`2>&1` means "make entry 2 a copy of entry 1", and copies are '
                'taken at the moment the redirection is processed, left to '
                'right. That is the whole reason `cmd > f 2>&1` and `cmd 2>&1 > '
                'f` differ: in the second, entry 1 still pointed at the '
                'terminal when entry 2 was copied from it.\n\n'
                'You can open your own descriptors with `exec`, which is how a '
                'script keeps a log file open for its whole life. And '
                '**here-documents** feed literal text to stdin without a '
                'temporary file, which is how scripts write config files '
                'without quoting nightmares.'
            ),
            'examples': [
                {
                    'label': 'Why the order matters',
                    'code': ('cmd > f 2>&1     1 -> f, then 2 copies 1 -> f\n'
                             'cmd 2>&1 > f     2 copies 1 -> tty, then 1 -> f\n'
                             '\n'
                             'left to right, and >& takes a snapshot'),
                    'note': 'Say "copy where 1 is pointing right now" out loud '
                            'and the asymmetry becomes obvious.',
                },
                {
                    'label': 'Your own descriptors, and here-docs',
                    'code': ('exec 3> run.log       open fd 3 on a file\n'
                             'echo "started" >&3    write to it\n'
                             'exec 3>&-             close it\n'
                             '\n'
                             'cat > config.ini <<\'EOF\'\n'
                             '[main]\n'
                             'path = $HOME\n'
                             'EOF\n'
                             '\n'
                             'quoted EOF means do NOT expand $HOME'),
                    'note': "Quoting the delimiter is the difference between a "
                            "literal template and one the shell fills in.",
                },
            ],
            'misconceptions': [
                '`2>&1` is not a fixed phrase meaning "both". It is a copy '
                'operation with an order, which is why moving it changes the '
                'result.',
                '`<<EOF` expands variables and `<<\'EOF\'` does not. Getting '
                'this backwards produces config files full of empty values.',
                '`<<<"text"` is a here-STRING and feeds one line to stdin, '
                'which is often what you wanted instead of `echo | cmd`.',
            ],
            'try_it': [
                'Run `ls /nope 2>&1 > out.txt` and then `ls /nope > out.txt '
                '2>&1`, and look at where the error went each time.',
            ],
        },
        {
            'id': 'la-signals',
            'title': 'Signals, orphans and zombies',
            'next': 'la-mounts',
            'concept': (
                'A signal is a number delivered to a process, and most of them '
                'can be caught, blocked or ignored. Two cannot: **SIGKILL (9)** '
                'and **SIGSTOP (19)**, which is exactly why `kill -9` always '
                'works and why it never gives the process a chance to clean '
                'up.\n\n'
                'The ones worth knowing by name are SIGTERM (15, the polite '
                'default), SIGINT (2, Ctrl-C), SIGHUP (1, historically "your '
                'terminal went away", now widely reused to mean "reload your '
                'config"), and SIGSTOP/SIGCONT for pausing.\n\n'
                'Two process states confuse people. An **orphan** has lost its '
                'parent and is adopted by init, which is normal. A **zombie** '
                'has exited but its parent has not collected its exit status, '
                'so the entry stays in the table. A zombie uses no resources '
                'and cannot be killed, because it is already dead; you fix the '
                'parent or the parent exits and init reaps it.'
            ),
            'examples': [
                {
                    'label': 'The ones worth knowing',
                    'code': ('1   SIGHUP    terminal gone, or "reload config"\n'
                             '2   SIGINT    Ctrl-C\n'
                             '9   SIGKILL   cannot be caught. Last resort\n'
                             '15  SIGTERM   the polite default\n'
                             '18  SIGCONT   resume\n'
                             '19  SIGSTOP   pause, cannot be caught\n'
                             '\n'
                             'kill -l          list them all\n'
                             'kill -HUP 1234   by name, which is clearer'),
                    'note': 'Many daemons reload configuration on SIGHUP rather '
                            'than restarting, which keeps connections alive.',
                },
                {
                    'label': 'Trapping one in a script',
                    'code': ('cleanup() { rm -f "$tmp"; }\n'
                             'trap cleanup EXIT INT TERM\n'
                             '\n'
                             'tmp=$(mktemp)\n'
                             '# ... work ...'),
                    'note': '`trap ... EXIT` is the reliable way to clean up, '
                            'because it fires however the script ends.',
                },
            ],
            'misconceptions': [
                'You cannot kill a zombie. It has already exited; the entry '
                'exists only so its parent can read the exit status.',
                'A high zombie count is a bug in the parent, not a resource '
                'leak. They cost one process-table slot each.',
                '`kill` sends a signal; it does not necessarily kill. `kill '
                '-STOP` pauses and `kill -CONT` resumes.',
                'A backgrounded job still receives SIGHUP when the terminal '
                'closes. `disown` removes it from the shell\'s job table so it '
                'does not.',
            ],
            'try_it': [
                'Run `sleep 300 &`, then `kill -STOP %1`, check `jobs`, then '
                '`kill -CONT %1`, then `kill %1`.',
            ],
        },
        {
            'id': 'la-mounts',
            'title': 'Mounts, and where the space went',
            'next': 'la-systemd',
            'concept': (
                'Mounting attaches a filesystem at a directory. Everything '
                'under that path then belongs to the new filesystem, and '
                'whatever was there before is hidden rather than deleted, which '
                'is worth knowing before you panic.\n\n'
                '`df -h` shows filesystems and how full they are; `du -sh *` '
                'shows what is using space within one. They disagree constantly, '
                'and the usual reason is a **deleted file still held open** by a '
                'running process: `du` cannot see it because it has no name, '
                'and `df` counts it because the blocks are still allocated. '
                '`lsof +L1` finds them.\n\n'
                'Bind mounts and loop mounts are worth knowing exist: a bind '
                'mount makes a directory appear in a second place, and a loop '
                'mount attaches a file as if it were a disk, which is how you '
                'read an ISO or a disk image.'
            ),
            'examples': [
                {
                    'label': 'Looking',
                    'code': ('df -h             filesystems and usage\n'
                             'df -i             inodes: the other way to run out\n'
                             'du -sh *          what is big in here\n'
                             'du -sh * 2>/dev/null | sort -h\n'
                             'findmnt           mounts, as a tree\n'
                             'lsof +L1          deleted but still open'),
                    'note': 'Running out of inodes with space free is a real '
                            'and confusing failure, usually from millions of '
                            'tiny files.',
                },
                {
                    'label': 'Attaching things',
                    'code': ('mount /dev/sdb1 /mnt\n'
                             'mount -o loop disk.img /mnt      a file as a disk\n'
                             'mount --bind /src /dst           a second name\n'
                             'umount /mnt\n'
                             'umount -l /mnt                   lazy, if busy'),
                    'note': '"target is busy" means something has a file open '
                            'or a shell is cd\'d inside. `lsof /mnt` names it.',
                },
            ],
            'misconceptions': [
                'Mounting over a non-empty directory hides its contents rather '
                'than destroying them. Unmount and they are back.',
                'df and du disagreeing is usually a deleted-but-open file, not '
                'a bug. Restarting the holder frees the space.',
                'Deleting files does not always free space, for the same '
                'reason. `lsof +L1` is the tool.',
            ],
            'try_it': [
                'Run `df -h` and `df -i` and compare how full each is. They can '
                'be very different.',
            ],
        },
        {
            'id': 'la-systemd',
            'title': 'systemd, journalctl, and timers',
            'next': 'la-network',
            'concept': (
                'On a modern Linux machine systemd starts everything, restarts '
                'what dies, and owns the logs. Four commands cover most of '
                'it.\n\n'
                '`systemctl status name` is the one to run first: it shows '
                'whether the unit is running, whether it is enabled at boot, '
                'and the last few log lines, which is often the whole answer. '
                'Note that **started and enabled are different**: `start` runs '
                'it now, `enable` makes it run at boot, and forgetting the '
                'second is why a service vanishes after a reboot.\n\n'
                '`journalctl` reads the log. `-u name` filters to one unit, '
                '`-f` follows, `-b` is this boot only, and `--since "1 hour '
                'ago"` takes human times. Together those four flags answer '
                'almost every log question.\n\n'
                'Timers are systemd\'s cron. They are more verbose to write and '
                'better in every other way: they log, they can catch up after '
                'downtime, and `systemctl list-timers` shows what will run '
                'next, which crontab cannot.'
            ),
            'examples': [
                {
                    'label': 'Services',
                    'code': ('systemctl status nginx    is it running, why not\n'
                             'systemctl start nginx     now\n'
                             'systemctl enable nginx    at boot\n'
                             'systemctl enable --now nginx   both\n'
                             'systemctl restart nginx\n'
                             'systemctl daemon-reload   after editing a unit\n'
                             'systemctl list-units --failed'),
                    'note': '`--failed` on a machine you have just been handed '
                            'tells you a lot in one line.',
                },
                {
                    'label': 'Logs and timers',
                    'code': ('journalctl -u nginx -f          follow one unit\n'
                             'journalctl -b -p err            errors, this boot\n'
                             'journalctl --since "1 hour ago"\n'
                             'journalctl -u nginx --since today\n'
                             '\n'
                             'systemctl list-timers           what runs next\n'
                             'crontab -l                      the old way'),
                    'note': '`-p err` filters by priority and cuts an enormous '
                            'amount of noise.',
                },
            ],
            'misconceptions': [
                'start and enable are unrelated. A service can be running and '
                'not enabled, which works perfectly until the next reboot.',
                'Editing a unit file does nothing until `systemctl '
                'daemon-reload`, which is the systemd version of the `doom '
                'sync` trap.',
                'cron and systemd timers both exist on most machines, so a '
                'scheduled job you cannot find may be in the other one. Check '
                'both.',
                'A cron job runs with a nearly empty environment and a '
                'different PATH, which is why "it works when I run it" is the '
                'most common cron complaint.',
            ],
            'try_it': [
                'Run `systemctl list-units --failed` and `journalctl -b -p err '
                '| tail -20` on your own machine.',
            ],
        },
        {
            'id': 'la-network',
            'title': 'Local network state',
            'concept': (
                'This is what your own machine thinks the network looks like, '
                'and it is a different question from whether a remote host is '
                'reachable.\n\n'
                '`ip` replaced `ifconfig` and `route`, and three subcommands '
                'cover it: `ip a` for addresses, `ip r` for routes, `ip l` for '
                'links. `ss` replaced `netstat`, and `ss -tulpn` is the one '
                'invocation worth memorising: TCP, UDP, listening, with '
                'process names and numeric ports.\n\n'
                '`ss -tulpn` is the fastest way to answer "what is listening on '
                'this box", which is the first question in an incident and the '
                'first question when a port is unexpectedly in use.\n\n'
                'Name resolution has more than one source. `/etc/hosts` is '
                'checked before DNS on most configurations, and '
                '`/etc/nsswitch.conf` decides the order, which is why a host '
                'can resolve differently for `ping` and for `dig`: dig asks DNS '
                'directly and skips the rest.'
            ),
            'examples': [
                {
                    'label': 'The three questions',
                    'code': ('ip a                what addresses do I have\n'
                             'ip r                where does traffic go\n'
                             'ip -br a            the brief version\n'
                             '\n'
                             'ss -tulpn           what is listening, with pids\n'
                             'ss -tp state established   who am I talking to'),
                    'note': '-t tcp, -u udp, -l listening, -p processes, -n '
                            'numeric. Memorise the whole string as one word.',
                },
                {
                    'label': 'Why dig and ping can disagree',
                    'code': ('/etc/hosts          checked first, usually\n'
                             '/etc/nsswitch.conf  decides the order\n'
                             '/etc/resolv.conf    which DNS servers\n'
                             '\n'
                             'getent hosts name   resolves the way programs do\n'
                             'dig +short name     asks DNS directly'),
                    'note': '`getent hosts` is the honest answer to "what will '
                            'my applications actually get".',
                },
            ],
            'misconceptions': [
                'ifconfig may still be installed and may show incomplete '
                'information on a modern kernel. Use `ip`.',
                'A port shown by `ss` as listening on 127.0.0.1 is not '
                'reachable from anywhere else, and that distinction is the '
                'answer to a large fraction of "the firewall is broken" '
                'reports.',
                '`dig` bypasses /etc/hosts, so a host that pings and does not '
                'dig is usually in your hosts file.',
            ],
            'try_it': [
                'Run `ss -tulpn` and identify every listening port on your '
                'machine. Anything you cannot explain is worth explaining.',
            ],
        },
    ],

    'drills': [
        {'id': 'lav-cmd-setuid', 'type': 'command', 'answer': 'chmod 4755 prog',
         'prompt': 'Make prog run as its owner rather than as whoever runs it.',
         'teach': 'The leading 4 is setuid. This is how passwd edits '
                  '/etc/shadow while you cannot.'},
        {'id': 'lav-cmd-setgid', 'type': 'command', 'answer': 'chmod 2775 shared',
         'prompt': 'Make new files in the shared directory inherit its group.',
         'teach': 'The leading 2 is setgid on a directory, which makes new '
                  "files take the directory's group rather than yours."},
        {'id': 'lav-cmd-sticky', 'type': 'command', 'answer': 'chmod 1777 drop',
         'prompt': 'Make a world-writable directory where only a file\'s owner '
                   'may delete it, like /tmp.',
         'teach': 'The leading 1 is the sticky bit. Without it, '
                  "world-writable means anyone can delete anyone else's "
                  'files.'},
        {'id': 'lav-cmd-findsuid', 'type': 'command',
         'answer': 'find / -perm -4000 -type f 2>/dev/null',
         'prompt': 'Find every setuid binary on the machine, discarding '
                   'permission errors.',
         'teach': 'The single most-run command in privilege escalation, in both '
                  'directions.'},
        {'id': 'lav-cmd-getcap', 'type': 'command', 'answer': 'getcap -r / 2>/dev/null',
         'prompt': 'Find every file holding a capability, which the setuid '
                   'search misses entirely.',
         'teach': "Capabilities split root's power into pieces, so a binary "
                  'can bind a low port without being setuid. A search for '
                  'setuid bits never sees them.'},
        {'id': 'lav-cmd-getfacl', 'type': 'command', 'answer': 'getfacl file',
         'prompt': 'Read the access control list on a file, after noticing a + '
                   'in its ls -l output.',
         'teach': 'The plus sign in ls -l is the only hint an ACL exists, and '
                  'the mode column on its own will lie to you about who has '
                  'access.'},
        {'id': 'lav-cmd-both-order', 'type': 'command',
         'answer': 'cmd > out.txt 2>&1',
         'prompt': 'Send both streams to out.txt, in the order that actually '
                   'works. Use "cmd".',
         'teach': 'Left to right, and >& copies where the target points at that '
                  'moment.'},
        {'id': 'lav-cmd-exec-fd', 'type': 'command', 'answer': 'exec 3> run.log',
         'prompt': 'Open file descriptor 3 on run.log for the rest of the '
                   'script.',
         'teach': 'exec with no command applies the redirection to the shell '
                  'itself, so the descriptor stays open until you close it '
                  'with exec 3>&-.'},
        {'id': 'lav-cmd-heredoc-literal', 'type': 'command',
         'answer': "cat > config.ini <<'EOF'",
         'prompt': 'Start a here-document writing config.ini, where variables '
                   'must NOT be expanded.',
         'teach': 'Quoting the delimiter is the difference between a literal '
                  'template and one the shell fills in.'},
        {'id': 'lav-cmd-herestring', 'type': 'command', 'answer': 'grep foo <<< "$text"',
         'prompt': 'Feed the contents of a variable to grep as one line of '
                   'input, without echo and a pipe.',
         'teach': 'It feeds one string on stdin. That saves a process and, '
                  'more usefully, keeps a loop in the current shell rather '
                  'than a subshell.'},
        {'id': 'lav-cmd-killhup', 'type': 'command', 'answer': 'kill -HUP 1234',
         'prompt': 'Tell a daemon to reload its configuration without '
                   'restarting.',
         'teach': "HUP means 'reread your configuration' only by convention, "
                  "so check the daemon's own documentation before relying on "
                  'it.'},
        {'id': 'lav-cmd-killstop', 'type': 'command', 'answer': 'kill -STOP 1234',
         'prompt': 'Pause a running process without ending it.',
         'teach': 'STOP cannot be caught or ignored, which is what makes it '
                  'reliable. CONT resumes the process.'},
        {'id': 'lav-cmd-killlist', 'type': 'command', 'answer': 'kill -l',
         'prompt': 'List every signal name and number.',
         'teach': 'Worth knowing because scripts see numbers and humans write '
                  'names, and the mapping is not identical on every platform.'},
        {'id': 'lav-cmd-trap', 'type': 'command', 'answer': 'trap cleanup EXIT INT TERM',
         'prompt': 'Arrange for a cleanup function to run however the script '
                   'ends.',
         'teach': 'EXIT alone covers a normal end and most errors; the other '
                  'two add Ctrl-C and a polite kill. Nothing catches KILL.'},
        {'id': 'lav-cmd-disown', 'type': 'command', 'answer': 'disown -h %1',
         'prompt': 'Stop a background job from receiving SIGHUP when the '
                   'terminal closes.',
         'teach': '-h marks the job so it is not sent HUP, without removing '
                  'it from the job table. nohup does the same thing at launch '
                  'time.'},
        {'id': 'lav-cmd-dfi', 'type': 'command', 'answer': 'df -i',
         'prompt': 'Check whether you have run out of inodes rather than space.',
         'teach': 'A filesystem with free space and no inodes left fails '
                  "every write, and the error says 'no space left' either "
                  'way.'},
        {'id': 'lav-cmd-lsofdeleted', 'type': 'command', 'answer': 'lsof +L1',
         'prompt': 'Find files that have been deleted but are still held open, '
                   'which is why df and du disagree.',
         'teach': 'Space comes back only when the last handle closes, which '
                  'is why deleting a log a process still holds frees nothing '
                  'at all.'},
        {'id': 'lav-cmd-findmnt', 'type': 'command', 'answer': 'findmnt',
         'prompt': 'Show every mount as a tree.',
         'teach': "It reads the kernel's own mount table, so it shows bind "
                  'mounts and namespaces that the plain mount command '
                  'flattens together.'},
        {'id': 'lav-cmd-bind', 'type': 'command', 'answer': 'mount --bind /src /dst',
         'prompt': 'Make a directory appear at a second path without copying '
                   'it.',
         'teach': 'The same directory at two paths, one inode. Unlike a '
                  'symlink it survives a chroot and looks like a real '
                  'directory to everything.'},
        {'id': 'lav-cmd-status', 'type': 'command', 'answer': 'systemctl status nginx',
         'prompt': 'Find out whether a service is running, whether it starts at '
                   'boot, and what it last said.',
         'teach': 'The last lines are recent log entries. That is the part '
                  'people scroll past and usually the part with the answer in '
                  'it.'},
        {'id': 'lav-cmd-enable-now', 'type': 'command',
         'answer': 'systemctl enable --now nginx',
         'prompt': 'Start a service and also make it start at boot, in one '
                   'command.',
         'teach': 'start and enable are unrelated, which is why a service can '
                  'work perfectly until the next reboot.'},
        {'id': 'lav-cmd-daemon-reload', 'type': 'command',
         'answer': 'systemctl daemon-reload',
         'prompt': 'Apply a change you made to a unit file.',
         'teach': 'Editing a unit does nothing until this runs.'},
        {'id': 'lav-cmd-failed', 'type': 'command',
         'answer': 'systemctl list-units --failed',
         'prompt': 'List everything that has failed on this machine.',
         'teach': 'The first command to run on a machine someone has just '
                  'handed you. It is short, and everything on it is a real '
                  'problem.'},
        {'id': 'lav-cmd-jrn-follow', 'type': 'command', 'answer': 'journalctl -u nginx -f',
         'prompt': 'Follow the log of one service as it happens.',
         'teach': '-u scopes it to one unit, which is what makes the journal '
                  'usable at all on a busy machine.'},
        {'id': 'lav-cmd-jrn-err', 'type': 'command', 'answer': 'journalctl -b -p err',
         'prompt': 'Show only errors from the current boot.',
         'teach': '-p filters by priority and cuts an enormous amount of '
                  'noise.'},
        {'id': 'lav-cmd-jrn-since', 'type': 'command',
         'answer': 'journalctl --since "1 hour ago"',
         'prompt': 'Show log entries from the last hour, using a human time.',
         'teach': "It accepts ordinary phrases like 'yesterday' and '09:00', "
                  'not only full timestamps.'},
        {'id': 'lav-cmd-timers', 'type': 'command', 'answer': 'systemctl list-timers',
         'prompt': 'Find out what scheduled jobs will run next, and when.',
         'teach': 'Timers are where cron jobs went. Looking only in crontab '
                  'on a current machine misses them completely.'},
        {'id': 'lav-cmd-ss', 'type': 'command', 'answer': 'ss -tulpn',
         'prompt': 'Show every listening TCP and UDP port with the process '
                   'holding it, without resolving names.',
         'teach': 'Memorise the whole string as one word. It is the first '
                  'question in an incident.'},
        {'id': 'lav-cmd-ipa', 'type': 'command', 'answer': 'ip -br a',
         'prompt': 'Show this machine\'s addresses, briefly.',
         'teach': '-br is the brief form, one line per interface. ifconfig is '
                  'not installed on most current distributions.'},
        {'id': 'lav-cmd-ipr', 'type': 'command', 'answer': 'ip r',
         'prompt': 'Show where traffic from this machine will go.',
         'teach': 'The route table picks the interface and source address for '
                  "every connection, which answers most 'it works from here "
                  "but not there' questions."},
        {'id': 'lav-cmd-getent', 'type': 'command', 'answer': 'getent hosts example.com',
         'prompt': 'Resolve a name the way ordinary programs will, respecting '
                   '/etc/hosts.',
         'teach': 'dig asks DNS directly and skips /etc/hosts, which is why the '
                  'two can disagree.'},
    ],

    'challenges': [
        {
            'id': 'lav-special-bits',
            'title': 'Set all three special bits',
            'goal': 'Produce a setuid binary, a setgid directory and a sticky '
                    'directory, and be able to read them back in ls -l.',
            'setup': {'kind': 'sandbox', 'tree': {
                'prog': {'content': '#!/bin/sh\necho hi\n', 'mode': '755'},
                'shared/': None,
                'drop/': None,
            }},
            'solution': {'shell': 'chmod 4755 prog && chmod 2775 shared '
                                  '&& chmod 1777 drop'},
            'steps': [
                {'instruction': 'Make prog setuid, keeping 755 underneath.',
                 'hint': 'chmod 4755 prog'},
                {'instruction': 'Make shared setgid so new files inherit its '
                                'group.', 'hint': 'chmod 2775 shared'},
                {'instruction': 'Make drop sticky, like /tmp.',
                 'hint': 'chmod 1777 drop'},
            ],
            'free': 'Set prog to 4755, shared to 2775 and drop to 1777.',
            'verify': {'kind': 'sandbox', 'expect': {
                'mode': {'prog': '4755', 'shared': '2775', 'drop': '1777'}}},
            'fallback': 'self',
        },
        {
            'id': 'lav-fd-order',
            'title': 'Prove the redirection order matters',
            'goal': 'Run the same command with the two orderings and capture '
                    'the difference, rather than taking it on faith.',
            'setup': {'kind': 'sandbox', 'tree': {'good.txt': 'here\n'}},
            'solution': {'shell': 'ls good.txt nope 2>&1 > wrong.txt 2> wrong-err.txt; '
                                  'ls good.txt nope > right.txt 2>&1; true'},
            'steps': [
                {'instruction': 'Run ls on one file that exists and one that '
                                'does not, with the redirect AFTER 2>&1, '
                                'sending stdout to wrong.txt and stderr to '
                                'wrong-err.txt.',
                 'hint': 'ls good.txt nope 2>&1 > wrong.txt 2> wrong-err.txt'},
                {'instruction': 'Run it again with the redirect FIRST, into '
                                'right.txt.',
                 'hint': 'ls good.txt nope > right.txt 2>&1'},
            ],
            'free': 'Produce wrong.txt containing only the good filename, '
                    'wrong-err.txt containing the error, and right.txt '
                    'containing both.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'wrong.txt': 'good.txt',
                                  'wrong-err.txt': 'nope',
                                  'right.txt': ['good.txt', 'nope']},
                'file_lacks': {'wrong.txt': 'nope'}}},
            'fallback': 'self',
        },
        {
            'id': 'lav-heredoc',
            'title': 'Write a config with a here-document',
            'goal': 'Use both forms and see the difference the quoted delimiter '
                    'makes.',
            'setup': {'kind': 'sandbox', 'shell': 'bash',
                      'tree': {'.keep': ''}},
            'solution': {'shell': "NAME=trainer; cat > literal.ini <<'EOF'\n"
                                  "user = $NAME\nEOF\n"
                                  "cat > expanded.ini <<EOF\n"
                                  "user = $NAME\nEOF"},
            'steps': [
                {'instruction': 'Set a variable NAME to trainer.',
                 'hint': 'NAME=trainer'},
                {'instruction': 'Write literal.ini with a QUOTED delimiter, so '
                                'the file contains the text $NAME.',
                 'hint': "cat > literal.ini <<'EOF'"},
                {'instruction': 'Write expanded.ini with an UNQUOTED delimiter, '
                                'so the file contains trainer.',
                 'hint': 'cat > expanded.ini <<EOF'},
            ],
            'free': 'Produce literal.ini containing the raw text $NAME and '
                    'expanded.ini containing its value, using here-documents.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'literal.ini': '$NAME',
                                  'expanded.ini': 'trainer'},
                'file_lacks': {'expanded.ini': '$NAME'}}},
            'fallback': 'self',
        },
        {
            'id': 'lav-machine-state',
            'title': 'Read your own machine',
            'goal': 'Everything above was a sandbox. This is about the real '
                    'machine, so the trainer cannot check it.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'List everything listening, with the processes '
                                'holding it.', 'hint': 'ss -tulpn'},
                {'instruction': 'Explain every line. Anything you cannot '
                                'explain is worth explaining.'},
                {'instruction': 'Check for failed units and recent errors.',
                 'hint': 'systemctl list-units --failed; journalctl -b -p err'},
                {'instruction': 'Find every setuid binary and every file with a '
                                'capability.',
                 'hint': 'find / -perm -4000 -type f 2>/dev/null; '
                         'getcap -r / 2>/dev/null'},
            ],
            'free': 'On your own machine: account for every listening port, '
                    'check for failed units and boot errors, and inventory the '
                    'setuid binaries and capabilities.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
        {
            'id': 'lav-signals-trap',
            'title': 'Catch a signal and clean up after yourself',
            'goal': 'Write a script that traps a signal, and prove which '
                    'signal cannot be trapped at all.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {'.keep': ''}},
            'solution': {'shell':
                'cat > catcher.sh <<\'EOF\'\n'
                '#!/bin/bash\n'
                'cleanup() { echo "cleaning up" >> caught.txt; exit 0; }\n'
                'trap cleanup TERM INT\n'
                'echo "started $$" > running.txt\n'
                'sleep 30 &\n'
                'wait\n'
                'EOF\n'
                'chmod +x catcher.sh\n'
                # The chmod is its own statement on purpose: with `chmod &&
                # ./catcher.sh &` the ampersand backgrounds the whole list, so
                # $! is the subshell rather than the script, and the TERM
                # never reaches the trap.
                './catcher.sh &\n'
                'pid=$!; sleep 1; kill -TERM $pid; sleep 1\n'
                './catcher.sh &\n'
                'pid2=$!; sleep 1; kill -KILL $pid2; sleep 1\n'
                'echo "KILL cannot be trapped" > uncatchable.txt\n'
                'true'},
            'steps': [
                {'instruction': 'Write catcher.sh: it should trap TERM and '
                                'INT, append "cleaning up" to caught.txt when '
                                'either arrives, then exit.',
                 'hint': 'trap cleanup TERM INT'},
                {'instruction': 'Have it record its own pid in running.txt '
                                'and then wait.',
                 'hint': 'echo "started $$" > running.txt'},
                {'instruction': 'Run it in the background and send it TERM. '
                                'Check that caught.txt appeared.',
                 'hint': './catcher.sh & kill -TERM $!'},
                {'instruction': 'Run it again and send KILL instead. Write to '
                                'uncatchable.txt what you observed about '
                                'signal 9.'},
            ],
            'free': 'Produce catcher.sh trapping TERM and INT, caught.txt '
                    'written by the trap, and uncatchable.txt recording what '
                    'KILL does differently.',
            'verify': {'kind': 'sandbox', 'expect': {
                'executable': ['catcher.sh'],
                'file_contains': {'catcher.sh': ['trap', 'TERM'],
                                  'caught.txt': 'cleaning up',
                                  'uncatchable.txt': 'KILL'}}},
            'fallback': 'self',
        },
        {
            'id': 'lav-acls',
            'title': 'Give one user access without touching the group',
            'goal': 'ACLs are the answer to the question the three permission '
                    'triads cannot express, and the plus sign in ls is how '
                    'you know they are there.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'shared/report.txt': 'quarterly numbers\n',
            }},
            'solution': {'shell':
                'setfacl -m u:nobody:rw shared/report.txt 2>/dev/null; '
                'getfacl -p shared/report.txt > acl.txt 2>/dev/null; '
                'ls -l shared/report.txt > listing.txt; '
                'setfacl -d -m u:nobody:rw shared 2>/dev/null; '
                'getfacl -p shared > diracl.txt 2>/dev/null; true'},
            'steps': [
                {'instruction': 'Grant the user nobody read and write on '
                                'shared/report.txt without changing its owner '
                                'or group.',
                 'hint': 'setfacl -m u:nobody:rw shared/report.txt'},
                {'instruction': 'Save the full ACL to acl.txt and the '
                                'ordinary listing to listing.txt.',
                 'hint': 'getfacl -p shared/report.txt > acl.txt'},
                {'instruction': 'Look at listing.txt for the plus sign after '
                                'the mode. That is the only hint ls gives '
                                'you.'},
                {'instruction': 'Set a default ACL on the directory so new '
                                'files inherit it, and save it to diracl.txt.',
                 'hint': 'setfacl -d -m u:nobody:rw shared'},
            ],
            'free': 'Produce acl.txt showing a named user entry on the file, '
                    'listing.txt showing the plus sign, and diracl.txt showing '
                    'a default ACL on the directory.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'acl.txt': 'user:nobody:rw',
                                  'listing.txt': '+',
                                  'diracl.txt': 'default:user:nobody'}}},
            'fallback': 'self',
        },
        {
            'id': 'lav-fds-open',
            'title': 'Open a descriptor and write to it by number',
            'goal': 'Descriptors are not only 0, 1 and 2. Open your own, use '
                    'it, and close it.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {'.keep': ''}},
            'solution': {'shell':
                'exec 3> extra.log && '
                'echo "line via fd 3" >&3 && '
                'echo "second line" >&3 && '
                'exec 3>&- && '
                'exec 4< extra.log && read -r first <&4 && '
                'echo "$first" > readback.txt && exec 4<&- && '
                'ls /proc/self/fd > fdlist.txt 2>/dev/null; true'},
            'steps': [
                {'instruction': 'Open file descriptor 3 for writing to '
                                'extra.log.',
                 'hint': 'exec 3> extra.log'},
                {'instruction': 'Write two lines through it, by number rather '
                                'than by filename.',
                 'hint': 'echo "line via fd 3" >&3'},
                {'instruction': 'Close it, then open descriptor 4 for reading '
                                'and read the first line back into '
                                'readback.txt.',
                 'hint': 'exec 3>&-  then  exec 4< extra.log'},
                {'instruction': 'List /proc/self/fd into fdlist.txt and see '
                                'what a process descriptor table looks like.'},
            ],
            'free': 'Produce extra.log written through descriptor 3, '
                    'readback.txt holding its first line read through '
                    'descriptor 4, and fdlist.txt from /proc.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'extra.log': ['line via fd 3',
                                                'second line'],
                                  'readback.txt': 'line via fd 3'},
                'is_file': ['fdlist.txt']}},
            'fallback': 'self',
        },
        {
            'id': 'lav-proc',
            'title': 'Read a process out of /proc',
            'goal': '/proc is the kernel answering questions as files. Ask it '
                    'about a process you started.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {'.keep': ''}},
            'solution': {'shell':
                'sleep 60 & pid=$!; sleep 0.3; '
                'tr "\\0" " " < /proc/$pid/cmdline > cmdline.txt 2>/dev/null; '
                'ls -l /proc/$pid/cwd > cwd.txt 2>/dev/null; '
                'grep -E "^(Name|State|PPid)" /proc/$pid/status > status.txt '
                '2>/dev/null; '
                'ls /proc/$pid/fd > fds.txt 2>/dev/null; '
                'kill $pid; true'},
            'steps': [
                {'instruction': 'Start a sleep in the background and keep its '
                                'pid.',
                 'hint': 'sleep 60 & pid=$!'},
                {'instruction': 'Read its command line out of /proc. The '
                                'arguments are separated by null bytes, so '
                                'translate them to spaces.',
                 'hint': 'tr "\\0" " " < /proc/$pid/cmdline > cmdline.txt'},
                {'instruction': 'Record where it thinks it is, from the cwd '
                                'symlink, into cwd.txt.',
                 'hint': 'ls -l /proc/$pid/cwd'},
                {'instruction': 'Pull the Name, State and PPid lines out of '
                                'its status file into status.txt, and list '
                                'its open descriptors into fds.txt.'},
                {'instruction': 'Kill it when you are done.'},
            ],
            'free': 'Produce cmdline.txt, cwd.txt, status.txt and fds.txt for '
                    'a background process you started, all read from /proc.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'cmdline.txt': 'sleep',
                                  'status.txt': ['Name:', 'State:', 'PPid:']},
                'is_file': ['cwd.txt', 'fds.txt']}},
            'fallback': 'self',
        },
        {
            'id': 'lav-nohup',
            'title': 'Outlive the shell that started it',
            'goal': 'nohup and disown solve the same problem differently, and '
                    'knowing which one you needed is the lesson.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {'.keep': ''}},
            'solution': {'shell':
                'nohup sleep 20 > nohup-out.txt 2>&1 & '
                'echo $! > nohup.pid; '
                'sleep 30 & echo $! > disowned.pid; disown; '
                'jobs > jobs.txt 2>&1; '
                'ps -o pid= -p "$(cat nohup.pid)" > still-there.txt 2>/dev/null; '
                'kill "$(cat nohup.pid)" "$(cat disowned.pid)" 2>/dev/null; '
                'true'},
            'steps': [
                {'instruction': 'Start something under nohup in the '
                                'background, redirecting its output, and '
                                'record its pid in nohup.pid.',
                 'hint': 'nohup sleep 20 > nohup-out.txt 2>&1 & echo $! > '
                         'nohup.pid'},
                {'instruction': 'Start a second background job and disown it '
                                'instead, recording its pid in '
                                'disowned.pid.',
                 'hint': 'sleep 30 & echo $! > disowned.pid; disown'},
                {'instruction': 'Write the current jobs table to jobs.txt. '
                                'The disowned one should be gone from it.'},
                {'instruction': 'Confirm the nohup process is still running, '
                                'into still-there.txt.',
                 'hint': 'ps -o pid= -p "$(cat nohup.pid)"'},
                {'instruction': 'nohup decides before it starts; disown '
                                'changes a job you already have. That is the '
                                'whole difference.'},
            ],
            'free': 'Produce nohup.pid, disowned.pid, jobs.txt and '
                    'still-there.txt, showing one process started detached '
                    'and one detached after the fact.',
            'verify': {'kind': 'sandbox', 'expect': {
                'is_file': ['nohup.pid', 'disowned.pid', 'jobs.txt',
                            'still-there.txt']}},
            'fallback': 'self',
        },
        {
            'id': 'lav-systemd-unit',
            'title': 'Write a unit and a timer that would work',
            'goal': 'systemd units are text files with a known shape. Write '
                    'both halves in the sandbox, where getting it wrong costs '
                    'nothing.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {'.keep': ''}},
            'solution': {'shell':
                'cat > backup.service <<\'EOF\'\n'
                '[Unit]\n'
                'Description=Nightly backup\n'
                'After=network-online.target\n'
                '\n'
                '[Service]\n'
                'Type=oneshot\n'
                'ExecStart=/usr/local/bin/backup.sh\n'
                'User=backup\n'
                'EOF\n'
                'cat > backup.timer <<\'EOF\'\n'
                '[Unit]\n'
                'Description=Run the nightly backup\n'
                '\n'
                '[Timer]\n'
                'OnCalendar=daily\n'
                'Persistent=true\n'
                '\n'
                '[Install]\n'
                'WantedBy=timers.target\n'
                'EOF'},
            'steps': [
                {'instruction': 'Write backup.service with a Unit section '
                                'carrying a Description and an After, and a '
                                'Service section that is Type=oneshot.',
                 'hint': '[Unit] then [Service] with Type=oneshot'},
                {'instruction': 'Give it an ExecStart and a User so it does '
                                'not run as root by default.'},
                {'instruction': 'Write backup.timer with a Timer section '
                                'using OnCalendar=daily and Persistent=true.',
                 'hint': '[Timer] with OnCalendar=daily'},
                {'instruction': 'Give the timer an Install section wanted by '
                                'timers.target. Note the service needs no '
                                'Install section, because the timer starts '
                                'it.'},
                {'instruction': 'Persistent=true is why a timer beats cron on '
                                'a laptop: it runs the missed job at next '
                                'boot.'},
            ],
            'free': 'Produce backup.service as a oneshot unit and '
                    'backup.timer running it daily with Persistent set.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'backup.service': ['[Unit]', '[Service]',
                                                     'Type=oneshot',
                                                     'ExecStart='],
                                  'backup.timer': ['[Timer]', 'OnCalendar=',
                                                   'Persistent=true',
                                                   'WantedBy=timers.target']}}},
            'fallback': 'self',
        },
    ],

    'quiz': [
        {'id': 'laq-setuid-script', 'type': 'mcq',
         'prompt': 'You chmod 4755 a shell script. What happens when someone '
                   'else runs it?',
         'answer': 'It runs as them; Linux ignores setuid on interpreted files.',
         'distractors': ['It runs as the owner, like any setuid binary.',
                         'It refuses to run at all.',
                         'It runs as root regardless of the owner.'],
         'teach': 'A deliberate defence, because setuid scripts are almost '
                  'impossible to write safely.'},

        {'id': 'laq-sticky', 'type': 'mcq',
         'prompt': 'Why can you not delete another user\'s file in /tmp, even '
                   'though /tmp is world-writable?',
         'answer': 'The sticky bit restricts deletion to the file\'s owner.',
         'distractors': ['The files are mode 600.',
                         '/tmp is on a read-only filesystem.',
                         'Deletion needs execute permission you do not have.'],
         'teach': '1777 is the mode. Without the sticky bit, anyone could '
                  'delete anyone\'s temp file.'},

        {'id': 'laq-2gt1-order', 'type': 'mcq',
         'prompt': 'Why does `cmd 2>&1 > f` send errors to the terminal?',
         'answer': 'Redirections apply left to right, and 2 copied 1 while it '
                   'still pointed at the terminal.',
         'distractors': ['Because 2>&1 only works at the end of a line.',
                         'Because > f resets both streams.',
                         'Because stderr is unbuffered.'],
         'teach': '>& is a copy taken at that moment, not a permanent link. '
                  'This is the most commonly half-understood thing in shell '
                  'redirection.'},

        {'id': 'laq-heredoc', 'type': 'mcq',
         'prompt': "What is the difference between <<EOF and <<'EOF'?",
         'answer': 'The quoted form does not expand variables.',
         'distractors': ['The quoted form allows indentation.',
                         'The quoted form reads from a file instead.',
                         'There is none; both are the same.'],
         'teach': 'Getting this backwards produces config files full of empty '
                  'values.'},

        {'id': 'laq-zombie', 'type': 'mcq',
         'prompt': 'How do you kill a zombie process?',
         'answer': 'You cannot; it has already exited. Fix or kill the parent.',
         'distractors': ['kill -9 on its PID.',
                         'kill -HUP on its PID.',
                         'Wait for the OOM killer to collect it.'],
         'teach': 'A zombie is a process-table entry kept so the parent can '
                  'read the exit status. It uses no resources.'},

        {'id': 'laq-uncatchable', 'type': 'mcq',
         'prompt': 'Which signals cannot be caught or ignored?',
         'answer': 'SIGKILL and SIGSTOP.',
         'distractors': ['SIGKILL and SIGTERM.',
                         'SIGINT and SIGKILL.',
                         'Only SIGKILL.'],
         'teach': 'That is exactly why kill -9 always works and why it never '
                  'lets the process clean up.'},

        {'id': 'laq-df-du', 'type': 'mcq',
         'prompt': 'df says the disk is full but du finds nothing. Why?',
         'answer': 'A deleted file is still held open by a running process.',
         'distractors': ['du does not count hidden files.',
                         'The filesystem needs fsck.',
                         'df counts the journal and du does not.'],
         'teach': 'The blocks are allocated but the file has no name, so du '
                  'cannot see it. lsof +L1 finds it.'},

        {'id': 'laq-enable', 'type': 'mcq',
         'prompt': 'A service works now but is gone after a reboot. What was '
                   'missed?',
         'answer': 'systemctl enable, which is separate from start.',
         'distractors': ['systemctl daemon-reload.',
                         'The unit file needed [Install] removed.',
                         'The service crashed and was not restarted.'],
         'teach': 'start and enable are unrelated. `enable --now` does both.'},

        {'id': 'laq-mount-over', 'type': 'mcq',
         'prompt': 'You mount a disk over a directory that already had files in '
                   'it. What happened to them?',
         'answer': 'They are hidden, and reappear when you unmount.',
         'distractors': ['They were deleted.',
                         'They were copied onto the new filesystem.',
                         'The mount would have failed.'],
         'teach': 'Worth knowing before you panic, and also worth knowing '
                  'because it is a good place to hide things.'},

        {'id': 'laq-ss', 'type': 'mcq',
         'prompt': 'ss shows a service listening on 127.0.0.1:5432. Can another '
                   'machine reach it?',
         'answer': 'No, regardless of the firewall.',
         'distractors': ['Yes, if the firewall allows it.',
                         'Yes, since 127.0.0.1 means all interfaces.',
                         'Only over IPv6.'],
         'teach': 'This distinction is the answer to a large fraction of "the '
                  'firewall is broken" reports.'},

        {'id': 'laq-dig-hosts', 'type': 'mcq',
         'prompt': 'A name pings fine but `dig` returns nothing. Where is it '
                   'defined?',
         'answer': '/etc/hosts, which dig bypasses.',
         'distractors': ['A stale DNS cache.',
                         'The name is IPv6 only.',
                         'nsswitch.conf has DNS disabled.'],
         'teach': 'dig asks DNS directly. `getent hosts` resolves the way your '
                  'programs actually will.'},
    ],
}
