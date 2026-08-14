"""systemd: the thing every other Linux module already assumed.

The foundational modules mention `systemctl` and `journalctl` twenty-three
times between them and never teach either, which is the largest single hole in
the roster: a beginner is told to check a service and read a log with two
commands nobody explained.

**Why it earns a module under the boundary rule.** The mental model genuinely
changes how you see a running machine. Before it, "the service is broken" is a
sentence with nowhere to go. After it, a machine is a graph of units with
declared dependencies, each in three independent states (loaded, active,
enabled) that people collapse into one, and a log you can query by unit, by
boot, by priority and by time rather than grep a file and hope. Those two
facts, the state triple and the query language, resolve most of the category.

**journalctl is the payoff, and the reason this matters for DFIR.** It is a
query language, not `cat`. `-u`, `-b -1`, `-p err`, `--since`, `_PID=`, `-o
json`: on a machine that has just misbehaved, knowing those is the difference
between reading the answer and scrolling past it.

**Verification, which is better here than expected.** Loading units needs root
and the trainer has none, so the obvious reading is that nothing here is
checkable. But `systemd-analyze verify` validates a unit file as an ordinary
user, catches unknown keys and non-executable `ExecStart` paths, and exits
non-zero on real errors. So writing a correct unit is genuinely verified: the
challenge writes the file, runs the real validator against it, and the check
reads both. Only the parts that need a live system are self-marked.
"""

MODULE = {
    'id': 'systemd',
    'title': 'systemd',
    'group': 'Linux',
    'blurb': 'Units and their three states, writing them, timers, and journalctl as a query language.',
    'context': 'You are at a shell on a Linux machine that boots with systemd.',
    'needs': ['systemctl'],
    'prereqs': ['linux'],
    'adapter': 'sandbox',
    'estimate': '4-5 hours',
    'order': 44,

    'lessons': [
        {
            'id': 'sd-model',
            'title': 'Units, and the three states people collapse into one',
            'next': 'sd-systemctl',
            'concept': (
                'systemd manages a machine as a set of **units**, and a unit '
                'is anything it can start, stop or watch. The suffix tells you '
                'which kind: `.service` is a process, `.timer` starts '
                'something on a schedule, `.socket` starts something when a '
                'connection arrives, `.mount` is a filesystem, and `.target` '
                'is just a named group used as a milestone, which is what '
                '`multi-user.target` is.\n\n'
                'The idea that unlocks the rest is that a unit has **three '
                'independent states**, and almost every confusion here comes '
                'from treating them as one.\n\n'
                '**Loaded** means systemd has read the unit file and knows the '
                'unit exists. **Active** means it is running right now. '
                '**Enabled** means it will start at boot. A unit can be active '
                'and not enabled, which is a service you started by hand that '
                'will be gone after a reboot. It can be enabled and not '
                'active, which is a service that will come back at boot and is '
                'currently stopped or crashed. Those are different problems '
                'with different fixes, and `systemctl status` shows you all '
                'three at once.\n\n'
                'Units come from more than one place, and later wins: the '
                'vendor file in `/usr/lib/systemd/system/`, your override in '
                '`/etc/systemd/system/`, and drop-in fragments in a '
                '`<unit>.d/` directory beside either. `systemctl cat` prints '
                'what is actually in effect, which is the only honest answer '
                'to "what does this unit say".'
            ),
            'examples': [
                {
                    'label': 'The three states, in one line of output',
                    'code': ('Loaded: loaded (/usr/lib/systemd/system/'
                             'sshd.service; enabled; ...)\n'
                             'Active: active (running) since Tue ...\n'
                             '        ^                ^\n'
                             '        active now       enabled at boot\n'
                             '\n'
                             'loaded  = systemd has read the file\n'
                             'active  = it is running now\n'
                             'enabled = it starts at boot'),
                    'note': 'Read all three every time. "It is running" and '
                            '"it will be running tomorrow" are separate '
                            'claims.',
                },
                {
                    'label': 'Kinds of unit worth knowing',
                    'code': ('sshd.service       a process\n'
                             'backup.timer       a schedule\n'
                             'docker.socket      start on first connection\n'
                             'home.mount         a filesystem\n'
                             'multi-user.target  a milestone, not a thing'),
                    'note': 'A target starts nothing itself. It is a name that '
                            'other units attach themselves to.',
                },
            ],
            'misconceptions': [
                'Enabled and started are not the same thing, and this is the '
                'single most common systemd mistake. `enable` schedules it for '
                'boot and does not start it now; `start` runs it now and does '
                'not survive a reboot. `enable --now` does both.',
                'A unit file you edited is not in effect until `systemctl '
                'daemon-reload`. systemd is reading its own cached copy, and '
                'nothing warns you until the change appears not to work.',
                'The file in `/usr/lib/systemd/system/` is the vendor copy and '
                'a package update will overwrite it. Your changes belong in '
                '`/etc/systemd/system/`, or better, a drop-in.',
            ],
            'try_it': [
                'Run `systemctl status` on a service you have, and name all '
                'three states out loud before reading anything else.',
                'Run `systemctl cat sshd` (or any service) and see which files '
                'it is actually assembled from.',
            ],
        },
        {
            'id': 'sd-systemctl',
            'title': 'Driving it, and asking it questions',
            'next': 'sd-units',
            'concept': (
                '`systemctl` is one verb plus one unit name, and about eight '
                'verbs cover everything you will do.\n\n'
                '`status` is the one you type most and the one worth reading '
                'properly: it gives the three states, the main PID, and the '
                'last few log lines, which is often the whole diagnosis '
                'without going near the journal. `start`, `stop` and '
                '`restart` do what they say. `reload` asks the service to '
                'reread its configuration without dropping connections, and '
                'only works if the service supports it; `reload-or-restart` '
                'falls back.\n\n'
                '`enable` and `disable` control boot only. `enable --now` is '
                'the one you almost always want when installing something.\n\n'
                'For scripts there are two quiet verbs that answer with an '
                'exit status and no output: `is-active` and `is-enabled`. '
                'Those are what belongs in a check, not grepping the output of '
                '`status`.\n\n'
                'To find things: `list-units` shows what is loaded right now, '
                '`list-unit-files` shows everything installed whether loaded '
                'or not, and the difference matters when a unit you are sure '
                'exists does not appear. Add `--failed` to go straight to what '
                'is broken, and `--user` to work on your own session units '
                'rather than the system ones.'
            ),
            'examples': [
                {
                    'label': 'The verbs',
                    'code': ('systemctl status nginx        the three states\n'
                             'systemctl start|stop nginx\n'
                             'systemctl restart nginx       full bounce\n'
                             'systemctl reload nginx        reread config\n'
                             'systemctl enable --now nginx  boot AND now\n'
                             'systemctl daemon-reload       after editing a unit'),
                    'note': 'daemon-reload reloads systemd itself. `reload '
                            'nginx` reloads nginx. Different things, similar '
                            'names.',
                },
                {
                    'label': 'Asking, rather than reading',
                    'code': ('systemctl is-active nginx     exit 0 if running\n'
                             'systemctl is-enabled nginx    exit 0 if at boot\n'
                             'systemctl list-units --failed what is broken\n'
                             'systemctl list-unit-files     everything installed\n'
                             'systemctl --user list-units   your session'),
                    'note': 'is-active is the scriptable form. Parsing `status` '
                            'output in a script is how scripts break on the '
                            'next systemd release.',
                },
            ],
            'misconceptions': [
                '`restart` on a stopped unit starts it, which is usually fine '
                'and occasionally a surprise. `try-restart` is the one that '
                'restarts only if it is already running.',
                '`systemctl list-units` does not list everything. A unit that '
                'is installed but has never been loaded is missing from it, '
                'and `list-unit-files` is where it is.',
                '`--user` is a completely separate manager with its own units, '
                'its own journal and its own enable state. A user unit is not '
                'a system unit you happen to own.',
            ],
            'try_it': [
                'Run `systemctl list-units --failed`. On a healthy machine it '
                'is empty, and knowing that is worth the two seconds.',
                'Run `systemctl is-enabled` on something and then `echo $?`, '
                'so you see the answer is the exit status.',
            ],
        },
        {
            'id': 'sd-units',
            'title': 'Writing a unit, and the dependency trap',
            'next': 'sd-journal',
            'concept': (
                'A `.service` file has three sections and you need about six '
                'keys.\n\n'
                '`[Unit]` carries the description and the relationships. '
                '`[Service]` says how to run the thing: `ExecStart` is the '
                'command, given as an absolute path because there is no shell '
                'and no `PATH` lookup. `Type=` tells systemd how to know the '
                'service has started: `simple` means the process it launched '
                'is the service, `oneshot` means it runs and exits and that is '
                'correct, `forking` means the process daemonises and the child '
                'is the real one, and `notify` means the service tells systemd '
                'itself. Getting `Type=` wrong is why a service is reported '
                'started before it is ready, or reported failed when it '
                'succeeded. `Restart=on-failure` is the one that makes a '
                'service resilient. `[Install]` holds `WantedBy=`, which is '
                'what `enable` acts on: with no `[Install]` section, `enable` '
                'has nothing to do and says so.\n\n'
                '**The trap is that ordering and requirement are separate '
                'settings.** `Requires=postgresql.service` says "if I start, '
                'that starts too, and if it fails, I fail". It says nothing '
                'about *when*. Without `After=postgresql.service` as well, '
                'systemd is free to start both at the same instant, and your '
                'service races the database it depends on. The pair you almost '
                'always want is both keys naming the same unit. `Wants=` is '
                'the weak form: start it too, but carry on if it fails.\n\n'
                'Do not edit vendor files. `systemctl edit nginx` writes a '
                'drop-in under `/etc/systemd/system/nginx.service.d/`, which '
                'survives package updates and changes only the keys you name.'
            ),
            'examples': [
                {
                    'label': 'A service that works',
                    'code': ('[Unit]\n'
                             'Description=Nightly report\n'
                             'After=network-online.target\n'
                             'Wants=network-online.target\n'
                             '\n'
                             '[Service]\n'
                             'Type=oneshot\n'
                             'ExecStart=/usr/local/bin/report.sh\n'
                             'User=reports\n'
                             '\n'
                             '[Install]\n'
                             'WantedBy=multi-user.target'),
                    'note': 'ExecStart is an absolute path: there is no shell, '
                            'so no PATH, no globs and no pipes unless you '
                            'invoke a shell yourself.',
                },
                {
                    'label': 'Requirement and ordering are two settings',
                    'code': ('Requires=db.service    if I start, it starts\n'
                             'After=db.service       and it finishes first\n'
                             '\n'
                             'Requires= alone  ->  both start at once, race\n'
                             'After= alone     ->  ordered, but db not pulled in\n'
                             'Wants= + After=  ->  the polite version'),
                    'note': 'Name the same unit in both. This is the systemd '
                            'bug people ship most often and notice least.',
                },
                {
                    'label': 'Checking it before you install it',
                    'code': ('systemd-analyze verify ./report.service\n'
                             '\n'
                             'catches unknown keys, bad paths, missing\n'
                             'sections, and says nothing when it is fine'),
                    'note': 'Runs as an ordinary user against a file on disk, '
                            'so you can validate a unit you have not installed '
                            'and cannot install.',
                },
            ],
            'misconceptions': [
                '`Requires=` does not mean "after". It is a requirement, not '
                'an order, and the two are set separately. A unit with '
                '`Requires=` and no `After=` starts in parallel with the thing '
                'it needs.',
                '`ExecStart` is not a shell command. No pipes, no redirects, '
                'no globs, no `PATH`. If you need those, run `/bin/sh -c` '
                'explicitly and accept that you have done so.',
                'A unit with no `[Install]` section cannot be enabled. That is '
                'not a bug: a `.timer` usually carries the `[Install]` and its '
                'paired `.service` deliberately does not.',
            ],
            'try_it': [
                'Write a unit file in `/tmp` and run `systemd-analyze verify` '
                'on it. Then break one key deliberately and run it again.',
                'Run `systemctl cat` on a service you have and find which '
                'section each key sits in.',
            ],
        },
        {
            'id': 'sd-journal',
            'title': 'journalctl: a query language, not a log file',
            'next': 'sd-timers',
            'concept': (
                'The journal is a structured, indexed store, and `journalctl` '
                'queries it. Treating it as a file you `grep` is the mistake '
                'that makes people miss things.\n\n'
                'Four filters do nearly everything, and they combine. `-u '
                'nginx` is one unit. `-b` is this boot and `-b -1` the '
                'previous one, which is how you read the logs from before a '
                'crash. `-p err` filters by priority, and it means "this level '
                'and worse", not "exactly this". `--since` and `--until` take '
                'plain English: `--since "1 hour ago"`, `--since yesterday`, '
                '`--since "2026-08-13 09:00"`.\n\n'
                'Two flags shape the output rather than the selection. `-f` '
                'follows, like `tail -f`. `-n 50` limits to the last fifty. '
                '`-o` chooses the format, and `-o json` is the one that '
                'matters, because it hands you every structured field and you '
                'can pipe it into `jq`.\n\n'
                'Those fields are the part most people never reach. Every '
                'entry carries metadata systemd recorded itself, and you can '
                'match on it directly: `_PID=1234`, `_UID=1000`, '
                '`_SYSTEMD_UNIT=sshd.service`, `_COMM=sudo`. Because it is '
                'recorded rather than parsed out of a message, it cannot be '
                'spoofed by something writing a clever log line, which is '
                'exactly why it is worth knowing when you are working out what '
                'happened on a machine.\n\n'
                'The debugging incantation to memorise is `journalctl -xeu '
                'UNIT`: explain, jump to the end, one unit.'
            ),
            'examples': [
                {
                    'label': 'The filters, which combine',
                    'code': ('journalctl -u nginx              one unit\n'
                             'journalctl -b                    this boot\n'
                             'journalctl -b -1 -p err          last boot, errors\n'
                             'journalctl --since "1 hour ago"\n'
                             'journalctl -u ssh --since today -p warning\n'
                             'journalctl -k                    kernel only'),
                    'note': '-p err means err and worse, so it includes crit, '
                            'alert and emerg. The scale runs 0 emerg to 7 '
                            'debug.',
                },
                {
                    'label': 'Structured fields, which are the real power',
                    'code': ('journalctl _PID=1234\n'
                             'journalctl _UID=1000 --since today\n'
                             'journalctl _COMM=sudo -o json | jq -r .MESSAGE\n'
                             '\n'
                             'journalctl -o json-pretty -n 1   see every field'),
                    'note': 'systemd recorded these itself, so they are '
                            'trustworthy in a way that anything parsed out of '
                            'the message text is not.',
                },
                {
                    'label': 'When something just failed',
                    'code': ('journalctl -xeu nginx    explain, end, this unit\n'
                             'journalctl -f -u nginx   watch it live\n'
                             '\n'
                             'journalctl --disk-usage\n'
                             'sudo journalctl --vacuum-time=7d'),
                    'note': '-xeu is the one to have in your fingers. It is '
                            'the first thing to run after a failed start.',
                },
            ],
            'misconceptions': [
                '`-p err` is not an exact match. Priorities are a severity '
                'scale and the flag means "this level and everything worse", '
                'which is almost always what you wanted and occasionally not.',
                'The journal is not `/var/log/syslog`. It is a binary indexed '
                'store, which is why it can filter by unit and boot instantly, '
                'and why `grep` on a file is not the equivalent.',
                'A journal may not persist across reboots. If `-b -1` says '
                'there are no entries, storage is set to volatile, and '
                '`/var/log/journal` has to exist for it to be kept.',
            ],
            'try_it': [
                'Run `journalctl -o json-pretty -n 1` and read every field on '
                'one entry. Most of them you have never seen.',
                'Find the errors from your previous boot: `journalctl -b -1 -p '
                'err`.',
            ],
        },
        {
            'id': 'sd-timers',
            'title': 'Timers, and why they beat cron',
            'next': 'sd-debug',
            'concept': (
                'A timer is two units: a `.timer` that says when, and a '
                '`.service` with the same stem that says what. They pair by '
                'name, so `backup.timer` runs `backup.service` and neither '
                'needs to mention the other.\n\n'
                '`OnCalendar=` is the schedule, and its vocabulary is friendly: '
                '`daily`, `hourly`, `weekly`, `Mon *-*-* 06:00:00`, '
                '`*-*-01 03:00:00` for the first of every month. '
                '`OnBootSec=` and `OnUnitActiveSec=` schedule relative to boot '
                'or to the last run instead, which is what you want for '
                '"every 15 minutes from whenever this machine came up".\n\n'
                'Two keys are why timers beat cron. `Persistent=true` means a '
                'run missed because the machine was off happens at the next '
                'boot, which cron simply cannot do. `RandomizedDelaySec=` '
                'spreads a fleet out so a thousand machines do not all hit the '
                'same server at 03:00.\n\n'
                'The rest of the argument is operational. A timer\'s job is a '
                'service, so it gets the journal, the dependency graph, '
                '`Restart=`, resource limits and `systemctl status` for free, '
                'and its output goes somewhere you can query instead of into a '
                'mail nobody reads. `systemctl list-timers` shows the next and '
                'last run of everything, which crontab cannot answer at all.\n\n'
                'Only the timer is enabled. The service it triggers usually has '
                'no `[Install]` section, because it is not meant to start on '
                'its own.'
            ),
            'examples': [
                {
                    'label': 'The pair',
                    'code': ('# backup.service\n'
                             '[Unit]\n'
                             'Description=Run the backup\n'
                             '[Service]\n'
                             'Type=oneshot\n'
                             'ExecStart=/usr/local/bin/backup.sh\n'
                             '\n'
                             '# backup.timer\n'
                             '[Unit]\n'
                             'Description=Daily backup\n'
                             '[Timer]\n'
                             'OnCalendar=daily\n'
                             'Persistent=true\n'
                             '[Install]\n'
                             'WantedBy=timers.target'),
                    'note': 'Same stem, so they find each other. Enable the '
                            'timer, never the service.',
                },
                {
                    'label': 'Schedules, and checking one',
                    'code': ('OnCalendar=daily\n'
                             'OnCalendar=Mon *-*-* 06:00:00\n'
                             'OnCalendar=*-*-01 03:00:00\n'
                             'OnBootSec=15min\n'
                             'OnUnitActiveSec=1h\n'
                             '\n'
                             'systemd-analyze calendar "Mon *-*-* 06:00:00"\n'
                             'systemctl list-timers --all'),
                    'note': '`systemd-analyze calendar` prints the next few '
                            'times an expression fires, which beats waiting to '
                            'find out.',
                },
            ],
            'misconceptions': [
                'You enable the timer, not the service. Enabling the service '
                'as well makes it run at boot too, which is rarely what the '
                'schedule meant.',
                '`Persistent=true` is the feature cron does not have: a run '
                'missed while the machine was off is caught up at boot rather '
                'than silently skipped.',
                'A timer does not report failures itself. The failure lives on '
                'the service it triggered, so that is what you check with '
                '`systemctl status backup.service`.',
            ],
            'try_it': [
                'Run `systemctl list-timers` and read the NEXT and LAST '
                'columns for something already on your machine.',
                'Run `systemd-analyze calendar "Mon *-*-* 06:00:00"` and see '
                'the next elapse it prints.',
            ],
        },
        {
            'id': 'sd-debug',
            'title': 'When it will not start',
            'concept': (
                'A failed unit has a short, ordered diagnosis, and following '
                'it beats guessing every time.\n\n'
                'First, `systemctl status UNIT`. The three states tell you '
                'whether it is even loaded, and the last log lines are '
                'frequently the whole answer. Note the exit code and the '
                '`Result=` if there is one.\n\n'
                'Second, `journalctl -xeu UNIT`. The `-x` adds systemd\'s own '
                'explanatory text, which is genuinely useful for the standard '
                'failures, and `-e` puts you at the end where the failure is.\n\n'
                'Third, `systemctl cat UNIT` to see what the unit actually '
                'says once every drop-in has been applied, which is regularly '
                'not what you think you wrote. If you just edited it and '
                'nothing changed, you forgot `daemon-reload`.\n\n'
                'Fourth, `systemd-analyze verify` on the file, which catches '
                'the typos: an unknown key is ignored silently at load time, '
                'so `Typ=simple` does nothing and says nothing.\n\n'
                'For dependency problems, `systemctl list-dependencies UNIT` '
                'shows the tree, and for boot problems `systemd-analyze blame` '
                'ranks units by startup time while `systemd-analyze '
                'critical-chain` shows the path that actually delayed the '
                'boot. `systemctl is-system-running` gives the one-word '
                'summary, and the word `degraded` means something failed and '
                'you have not noticed.'
            ),
            'examples': [
                {
                    'label': 'The order to try things in',
                    'code': ('systemctl status nginx        states + last lines\n'
                             'journalctl -xeu nginx         explained, at the end\n'
                             'systemctl cat nginx           what it really says\n'
                             'systemd-analyze verify FILE   typos and bad paths\n'
                             'systemctl daemon-reload       if you just edited it'),
                    'note': 'Four commands in order. Most failures are answered '
                            'by the first two.',
                },
                {
                    'label': 'Dependencies and boot',
                    'code': ('systemctl list-dependencies nginx\n'
                             'systemctl is-system-running     degraded?\n'
                             'systemctl list-units --failed\n'
                             '\n'
                             'systemd-analyze blame           slowest units\n'
                             'systemd-analyze critical-chain  what delayed boot'),
                    'note': '`degraded` means something failed. It is the '
                            'quickest whole-machine health question there is.',
                },
            ],
            'misconceptions': [
                'An unknown key in a unit file is ignored, not rejected. '
                '`Typ=simple` fails silently and the service runs with the '
                'default type, which is why `systemd-analyze verify` exists.',
                'Editing a unit file changes nothing until `daemon-reload`. '
                'The most common "my change did not work" is not a wrong '
                'change, it is an unloaded one.',
                '`systemctl status` output is for humans and changes between '
                'releases. Script against `is-active`, `is-enabled` and exit '
                'codes instead.',
            ],
            'try_it': [
                'Run `systemctl is-system-running` on your machine. If it says '
                'degraded, run `systemctl list-units --failed` and find out '
                'what you have been ignoring.',
                'Run `systemd-analyze blame | head` and see what actually costs '
                'you time at boot.',
            ],
        },
    ],

    'drills': [
        {'id': 'sdd-status', 'type': 'command', 'answer': 'systemctl status nginx',
         'prompt': 'Show the full state of a service, with its recent log lines.',
         'teach': 'The three states plus the last few journal lines, which is '
                  'often the whole diagnosis without opening the journal.'},
        {'id': 'sdd-enable-now', 'type': 'command',
         'answer': 'systemctl enable --now nginx',
         'prompt': 'Start a service now and also have it start at boot.',
         'teach': 'enable is boot only and start is now only. --now is the '
                  'flag that stops you doing half the job.'},
        {'id': 'sdd-daemon-reload', 'type': 'command',
         'answer': 'systemctl daemon-reload',
         'prompt': 'Make systemd reread unit files after you edited one.',
         'teach': 'Until you run this, systemd is using its cached copy and '
                  'your edit appears to do nothing.'},
        {'id': 'sdd-is-active', 'type': 'command',
         'answer': 'systemctl is-active nginx',
         'prompt': 'Ask whether a service is running, scriptably.',
         'teach': 'The answer is the exit status, which is what a check should '
                  'use rather than grepping the output of status.'},
        {'id': 'sdd-failed', 'type': 'command',
         'answer': 'systemctl list-units --failed',
         'prompt': 'List everything on the machine that has failed.',
         'teach': 'Empty on a healthy machine. The fastest whole-system health '
                  'question there is.'},
        {'id': 'sdd-unit-files', 'type': 'command',
         'answer': 'systemctl list-unit-files',
         'prompt': 'List every installed unit, including ones never loaded.',
         'teach': 'list-units shows only what is loaded, so a unit you are '
                  'sure exists can be missing from it. This is where it is.'},
        {'id': 'sdd-cat', 'type': 'command', 'answer': 'systemctl cat nginx',
         'prompt': 'Show the effective unit, drop-ins included.',
         'teach': 'The only honest answer to what a unit says, because '
                  'drop-ins override the vendor file and are easy to forget.'},
        {'id': 'sdd-edit', 'type': 'command', 'answer': 'systemctl edit nginx',
         'prompt': 'Override one key of a packaged unit, update-safely.',
         'teach': 'Writes a drop-in under /etc/systemd/system/nginx.service.d/ '
                  'rather than editing the vendor file a package will replace.'},
        {'id': 'sdd-user', 'type': 'command',
         'answer': 'systemctl --user list-units',
         'prompt': 'List the units of your own session manager.',
         'teach': 'A separate manager with its own units, journal and enable '
                  'state. A user unit is not a system unit you happen to own.'},
        {'id': 'sdd-verify', 'type': 'command',
         'answer': 'systemd-analyze verify ./report.service',
         'prompt': 'Validate a unit file before installing it.',
         'teach': 'Runs unprivileged against a file on disk and catches '
                  'unknown keys and non-executable ExecStart paths.'},
        {'id': 'sdd-jrn-unit', 'type': 'command', 'answer': 'journalctl -u nginx',
         'prompt': 'Read the log for one service only.',
         'teach': 'The journal is indexed by unit, so this is a lookup rather '
                  'than a scan of everything.'},
        {'id': 'sdd-jrn-xeu', 'type': 'command', 'answer': 'journalctl -xeu nginx',
         'prompt': 'Jump to the end of one unit log, with explanations.',
         'teach': 'The incantation to have in your fingers: explain, end, unit. '
                  'The first thing to run after a failed start.'},
        {'id': 'sdd-jrn-boot', 'type': 'command', 'answer': 'journalctl -b -1',
         'prompt': 'Read the log from the previous boot.',
         'teach': 'How you see what happened before a crash. Needs persistent '
                  'storage: /var/log/journal must exist.'},
        {'id': 'sdd-jrn-prio', 'type': 'command', 'answer': 'journalctl -p err -b',
         'prompt': 'Show only errors and worse from this boot.',
         'teach': 'Priority is a severity scale, so -p err includes crit, '
                  'alert and emerg. It runs 0 emerg to 7 debug.'},
        {'id': 'sdd-jrn-since', 'type': 'command',
         'answer': 'journalctl --since "1 hour ago"',
         'prompt': 'Show journal entries from the last hour.',
         'teach': '--since and --until take plain English as well as '
                  'timestamps: yesterday, today, "2026-08-13 09:00".'},
        {'id': 'sdd-jrn-follow', 'type': 'command', 'answer': 'journalctl -f -u nginx',
         'prompt': 'Watch one service log live as it happens.',
         'teach': 'tail -f for the journal, filtered to a unit. Combine it '
                  'with a restart in another pane.'},
        {'id': 'sdd-jrn-json', 'type': 'command',
         'answer': 'journalctl -u nginx -o json',
         'prompt': 'Emit journal entries as JSON, one per line.',
         'teach': 'Gives every structured field, which is what makes the '
                  'journal pipeable into jq rather than merely readable.'},
        {'id': 'sdd-jrn-pid', 'type': 'command', 'answer': 'journalctl _PID=1234',
         'prompt': 'Show every entry logged by one process id.',
         'teach': 'A field match on metadata systemd recorded itself, so it '
                  'cannot be forged by a clever log message.'},
        {'id': 'sdd-jrn-kernel', 'type': 'command', 'answer': 'journalctl -k',
         'prompt': 'Show kernel messages only.',
         'teach': 'The dmesg equivalent, with the journal filters available on '
                  'top of it.'},
        {'id': 'sdd-jrn-disk', 'type': 'command', 'answer': 'journalctl --disk-usage',
         'prompt': 'Report how much disk the journal is using.',
         'teach': 'Pairs with --vacuum-time=7d or --vacuum-size=500M when the '
                  'answer is more than you expected.'},
        {'id': 'sdd-timers', 'type': 'command', 'answer': 'systemctl list-timers',
         'prompt': 'Show every timer with its next and last run.',
         'teach': 'The question crontab cannot answer. --all includes timers '
                  'that are not currently active.'},
        {'id': 'sdd-calendar', 'type': 'command',
         'answer': 'systemd-analyze calendar "Mon *-*-* 06:00:00"',
         'prompt': 'Check when a calendar expression will actually fire.',
         'teach': 'Prints the next elapse, which beats enabling a timer and '
                  'waiting a week to discover the syntax was wrong.'},
        {'id': 'sdd-deps', 'type': 'command',
         'answer': 'systemctl list-dependencies nginx',
         'prompt': 'Show the dependency tree of a unit.',
         'teach': 'Where an ordering or requirement problem becomes visible '
                  'rather than theoretical.'},
        {'id': 'sdd-running', 'type': 'command',
         'answer': 'systemctl is-system-running',
         'prompt': 'Ask for the one-word health summary of the machine.',
         'teach': 'The word degraded means something failed and nobody looked. '
                  'Follow it with list-units --failed.'},
        {'id': 'sdd-blame', 'type': 'command', 'answer': 'systemd-analyze blame',
         'prompt': 'Rank units by how long they took to start at boot.',
         'teach': 'critical-chain is the companion: blame ranks everything, '
                  'critical-chain shows what actually delayed the boot.'},
    ],

    'challenges': [
        {
            'id': 'sdc-write-unit',
            'title': 'Write a service unit that validates',
            'goal': 'Write a real unit file and prove it is correct with the '
                    'validator, without installing anything.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {'.keep': ''}},
            'solution': {'shell':
                'cat > report.service <<\'EOF\'\n'
                '[Unit]\n'
                'Description=Nightly report\n'
                'Wants=network-online.target\n'
                'After=network-online.target\n'
                '\n'
                '[Service]\n'
                'Type=oneshot\n'
                'ExecStart=/bin/echo generating the report\n'
                '\n'
                '[Install]\n'
                'WantedBy=multi-user.target\n'
                'EOF\n'
                'systemd-analyze verify ./report.service > verify.txt 2>&1; '
                'echo "exit $?" >> verify.txt'},
            'steps': [
                {'instruction': 'Write report.service with a Description, and '
                                'an ordering plus a want on '
                                'network-online.target.',
                 'hint': 'Wants= and After= naming the same unit'},
                {'instruction': 'Give it a [Service] section that runs once and '
                                'exits, with an absolute ExecStart path.',
                 'hint': 'Type=oneshot and ExecStart=/bin/echo something'},
                {'instruction': 'Add an [Install] section so it can be enabled '
                                'at all.',
                 'hint': 'WantedBy=multi-user.target'},
                {'instruction': 'Run the validator against the file and save '
                                'its output and exit status to verify.txt.',
                 'hint': 'systemd-analyze verify ./report.service > verify.txt '
                         '2>&1; echo "exit $?" >> verify.txt'},
            ],
            'free': 'Produce report.service with all three sections, a oneshot '
                    'ExecStart, Wants and After on network-online.target, and '
                    'verify.txt showing the validator exited 0.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'report.service': ['[Unit]', '[Service]',
                                                     '[Install]', 'Type=oneshot',
                                                     'ExecStart=/',
                                                     'After=network-online.target',
                                                     'WantedBy='],
                                  'verify.txt': 'exit 0'}}},
            'fallback': 'self',
        },
        {
            'id': 'sdc-fix-unit',
            'title': 'Find the typo systemd would ignore',
            'goal': 'A unit with a silent mistake in it. An unknown key is '
                    'ignored at load time, so the validator is the only thing '
                    'that will tell you.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'broken.service':
                    '[Unit]\n'
                    'Description=Broken example\n'
                    '\n'
                    '[Service]\n'
                    'Typ=simple\n'
                    'ExecStart=/nonexistent/binary --run\n'
                    '\n'
                    '[Install]\n'
                    'WantedBy=multi-user.target\n',
            }},
            'solution': {'shell':
                'systemd-analyze verify ./broken.service > before.txt 2>&1; '
                'sed -e "s|^Typ=simple|Type=simple|" '
                '-e "s|^ExecStart=.*|ExecStart=/bin/true|" broken.service '
                '> fixed.service && '
                'systemd-analyze verify ./fixed.service > after.txt 2>&1; '
                'echo "exit $?" >> after.txt'},
            'steps': [
                {'instruction': 'Run the validator on broken.service and save '
                                'the complaints to before.txt.',
                 'hint': 'systemd-analyze verify ./broken.service > before.txt '
                         '2>&1'},
                {'instruction': 'Read them. One is a misspelled key that '
                                'systemd would silently ignore, the other is a '
                                'command that does not exist.'},
                {'instruction': 'Write fixed.service with both corrected, '
                                'pointing ExecStart at something real.',
                 'hint': 'Type=simple, and ExecStart=/bin/true'},
                {'instruction': 'Validate the fixed one into after.txt with its '
                                'exit status, and confirm it is clean.',
                 'hint': 'systemd-analyze verify ./fixed.service > after.txt '
                         '2>&1; echo "exit $?" >> after.txt'},
            ],
            'free': 'Produce before.txt holding the validator complaints about '
                    'broken.service, and fixed.service with Type spelled '
                    'correctly and a real ExecStart, validating clean into '
                    'after.txt.',
            'verify': {'kind': 'sandbox', 'expect': {
                'is_file': ['before.txt', 'fixed.service', 'after.txt'],
                'file_contains': {'before.txt': 'Typ',
                                  'fixed.service': ['Type=simple', 'ExecStart=/'],
                                  'after.txt': 'exit 0'},
                'file_lacks': {'fixed.service': 'Typ=simple'}}},
            'fallback': 'self',
        },
        {
            'id': 'sdc-timer-pair',
            'title': 'Build a timer and the service it runs',
            'goal': 'A schedule is two units that pair by name. Write both, '
                    'and check the calendar expression means what you think.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {'.keep': ''}},
            'solution': {'shell':
                'cat > backup.service <<\'EOF\'\n'
                '[Unit]\n'
                'Description=Run the backup\n'
                '\n'
                '[Service]\n'
                'Type=oneshot\n'
                'ExecStart=/bin/true\n'
                'EOF\n'
                'cat > backup.timer <<\'EOF\'\n'
                '[Unit]\n'
                'Description=Daily backup\n'
                '\n'
                '[Timer]\n'
                'OnCalendar=*-*-* 03:00:00\n'
                'Persistent=true\n'
                '\n'
                '[Install]\n'
                'WantedBy=timers.target\n'
                'EOF\n'
                'systemd-analyze calendar "*-*-* 03:00:00" > when.txt 2>&1; '
                'systemd-analyze verify ./backup.timer > verify.txt 2>&1; '
                'echo "exit $?" >> verify.txt'},
            'steps': [
                {'instruction': 'Write backup.service as a oneshot with an '
                                'absolute ExecStart, and no [Install] section, '
                                'because it is not meant to start on its own.',
                 'hint': 'Type=oneshot and ExecStart=/bin/true'},
                {'instruction': 'Write backup.timer with the same stem, firing '
                                'daily at 03:00, catching up a run missed while '
                                'the machine was off.',
                 'hint': 'OnCalendar=*-*-* 03:00:00 and Persistent=true'},
                {'instruction': 'Give the timer the [Install] section, since the '
                                'timer is the half you enable.',
                 'hint': 'WantedBy=timers.target'},
                {'instruction': 'Save the next elapse of your calendar '
                                'expression to when.txt, and validate the timer '
                                'into verify.txt.',
                 'hint': 'systemd-analyze calendar "*-*-* 03:00:00" > when.txt'},
            ],
            'free': 'Produce backup.service (oneshot, no [Install]) and '
                    'backup.timer (OnCalendar at 03:00, Persistent, WantedBy '
                    'timers.target), plus when.txt from systemd-analyze '
                    'calendar and a clean verify.txt.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'backup.service': ['Type=oneshot', 'ExecStart=/'],
                                  'backup.timer': ['[Timer]', 'OnCalendar=',
                                                   'Persistent=true',
                                                   'WantedBy=timers.target'],
                                  'when.txt': 'Next elapse',
                                  'verify.txt': 'exit 0'},
                'file_lacks': {'backup.service': '[Install]'}}},
            'fallback': 'self',
        },
        {
            'id': 'sdc-journal-fields',
            'title': 'Query a journal export like a database',
            'goal': 'The journal is structured, so its JSON is the honest way '
                    'to see that. Filter an export by the fields systemd '
                    'recorded rather than by grepping message text.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'export.json':
                    '{"__REALTIME_TIMESTAMP":"1000","_PID":"901",'
                    '"_UID":"0","_COMM":"sshd","PRIORITY":"6",'
                    '"_SYSTEMD_UNIT":"sshd.service",'
                    '"MESSAGE":"Accepted publickey for deploy from 10.0.0.9"}\n'
                    '{"__REALTIME_TIMESTAMP":"2000","_PID":"901",'
                    '"_UID":"0","_COMM":"sshd","PRIORITY":"3",'
                    '"_SYSTEMD_UNIT":"sshd.service",'
                    '"MESSAGE":"Failed password for invalid user admin from 10.0.0.9"}\n'
                    '{"__REALTIME_TIMESTAMP":"3000","_PID":"1450",'
                    '"_UID":"1000","_COMM":"sudo","PRIORITY":"5",'
                    '"_SYSTEMD_UNIT":"session-3.scope",'
                    '"MESSAGE":"deploy : TTY=pts/0 ; PWD=/srv ; USER=root ; COMMAND=/bin/bash"}\n'
                    '{"__REALTIME_TIMESTAMP":"4000","_PID":"1450",'
                    '"_UID":"1000","_COMM":"sudo","PRIORITY":"3",'
                    '"_SYSTEMD_UNIT":"session-3.scope",'
                    '"MESSAGE":"deploy : 1 incorrect password attempt"}\n'
                    '{"__REALTIME_TIMESTAMP":"5000","_PID":"77",'
                    '"_UID":"0","_COMM":"kernel","PRIORITY":"4",'
                    '"_SYSTEMD_UNIT":"init.scope",'
                    '"MESSAGE":"usb 1-2: device descriptor read error"}\n',
            }},
            'solution': {'shell':
                'jq -r \'select((.PRIORITY|tonumber) <= 3) | .MESSAGE\' '
                'export.json > errors.txt && '
                'jq -r \'select(._COMM == "sudo") | .MESSAGE\' export.json '
                '> sudo.txt && '
                'jq -r \'._SYSTEMD_UNIT\' export.json | sort -u > units.txt'},
            'steps': [
                {'instruction': 'Write errors.txt holding the MESSAGE of every '
                                'entry at priority 3 or worse. Remember lower '
                                'numbers are more severe.',
                 'hint': 'jq -r \'select((.PRIORITY|tonumber) <= 3) | .MESSAGE\' '
                         'export.json'},
                {'instruction': 'Write sudo.txt holding the messages logged by '
                                'the sudo binary, matched on the recorded _COMM '
                                'field rather than on the text.',
                 'hint': 'select(._COMM == "sudo")'},
                {'instruction': 'Write units.txt listing each distinct '
                                '_SYSTEMD_UNIT once.',
                 'hint': 'jq -r ._SYSTEMD_UNIT export.json | sort -u'},
                {'instruction': 'Note what you just did: every filter used a '
                                'field systemd recorded itself, so none of it '
                                'could be faked by a crafted log line.'},
            ],
            'free': 'From export.json produce errors.txt (priority 3 or worse), '
                    'sudo.txt (entries whose _COMM is sudo), and units.txt '
                    '(each _SYSTEMD_UNIT once).',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'errors.txt': ['Failed password',
                                                 'incorrect password'],
                                  'sudo.txt': 'TTY=pts/0',
                                  'units.txt': ['sshd.service', 'init.scope']},
                'file_lacks': {'errors.txt': 'Accepted publickey',
                               'sudo.txt': 'Accepted publickey'}}},
            'fallback': 'self',
        },
        {
            'id': 'sdc-real-machine',
            'title': 'Diagnose your own machine',
            'goal': 'Everything above was a file. This one is the live system, '
                    'so the trainer cannot check it.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'Ask for the one-word health summary.',
                 'hint': 'systemctl is-system-running'},
                {'instruction': 'List anything that has failed, and read the '
                                'status of one of them.',
                 'hint': 'systemctl list-units --failed'},
                {'instruction': 'Read that unit log the proper way, with '
                                'explanations, at the end.',
                 'hint': 'journalctl -xeu UNIT'},
                {'instruction': 'Find the errors from your previous boot.',
                 'hint': 'journalctl -b -1 -p err'},
                {'instruction': 'Run systemctl cat on a service you use and '
                                'find out whether a drop-in is changing it '
                                'behind your back.'},
            ],
            'free': 'On your own machine: get the health summary, list failed '
                    'units, read one of them with journalctl -xeu, pull the '
                    'errors from the previous boot, and check one unit for '
                    'drop-ins.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
    ],

    'quiz': [
        {'id': 'sdq-enable', 'type': 'mcq',
         'prompt': 'You ran `systemctl enable nginx`. Is nginx running now?',
         'answer': 'No. enable only schedules it for boot; enable --now does '
                   'both.',
         'distractors': ['Yes, enable implies start.',
                         'Only if it was running before you enabled it.',
                         'Yes, but it stops again at the next reboot.'],
         'teach': 'enable is boot, start is now. They are separate, and the '
                  'confusion between them is the most common systemd mistake.'},
        {'id': 'sdq-requires', 'type': 'mcq',
         'prompt': 'A unit has `Requires=db.service` and no `After=`. What '
                   'happens?',
         'answer': 'db.service is pulled in, but both may start at the same '
                   'time, so your unit can race it.',
         'distractors': ['db.service is started first and fully, then yours.',
                         'Nothing; Requires implies After.',
                         'systemd refuses to load the unit.'],
         'teach': 'Requirement and ordering are separate settings. Name the '
                  'same unit in both Requires= and After= unless you have a '
                  'reason not to.'},
        {'id': 'sdq-priority', 'type': 'mcq',
         'prompt': 'What does `journalctl -p err` show?',
         'answer': 'Entries at err and everything more severe: crit, alert and '
                   'emerg.',
         'distractors': ['Only entries whose priority is exactly err.',
                         'err and everything less severe, down to debug.',
                         'Only entries from units that failed.'],
         'teach': 'Priority is a severity scale from 0 emerg to 7 debug, and '
                  '-p means this level and worse.'},
        {'id': 'sdq-reload', 'type': 'mcq',
         'prompt': 'You edited a unit file and the change had no effect. Why?',
         'answer': 'systemd is still using its cached copy; you need '
                   'daemon-reload.',
         'distractors': ['Unit files are read only at boot.',
                         'You edited the vendor file, which is ignored.',
                         'The unit needs to be disabled and enabled again.'],
         'teach': 'daemon-reload reloads systemd itself. It is a different '
                  'thing from `systemctl reload nginx`, which reloads nginx.'},
        {'id': 'sdq-unknown-key', 'type': 'mcq',
         'prompt': 'A unit says `Typ=simple` instead of `Type=simple`. What '
                   'does systemd do?',
         'answer': 'Ignores the unknown key silently and uses the default '
                   'type.',
         'distractors': ['Refuses to load the unit and logs an error.',
                         'Guesses that you meant Type and applies it.',
                         'Loads it but marks the unit as degraded.'],
         'teach': 'Silent is the problem. `systemd-analyze verify` is the thing '
                  'that will actually tell you, and it needs no root.'},
        {'id': 'sdq-timer-enable', 'type': 'mcq',
         'prompt': 'You wrote backup.timer and backup.service. Which do you '
                   'enable?',
         'answer': 'The timer. It triggers the service by name, and the '
                   'service usually has no [Install] at all.',
         'distractors': ['Both, or the schedule will not fire.',
                         'The service, since that is the thing doing the work.',
                         'Neither; timers are active as soon as the file '
                         'exists.'],
         'teach': 'Same stem is how they pair. Enabling the service too makes '
                  'it run at boot, which the schedule did not ask for.'},
        {'id': 'sdq-persistent', 'type': 'mcq',
         'prompt': 'What does `Persistent=true` give a timer that cron cannot?',
         'answer': 'A run missed while the machine was off happens at the next '
                   'boot instead of being skipped.',
         'distractors': ['The timer survives a systemd restart.',
                         'The schedule is written to disk rather than memory.',
                         'The service keeps running between firings.'],
         'teach': 'This is the strongest single argument for timers over cron '
                  'on a machine that is not always on.'},
        {'id': 'sdq-fields', 'type': 'mcq',
         'prompt': 'Why is matching `_COMM=sudo` better than grepping for '
                   '"sudo" in messages?',
         'answer': 'It is metadata systemd recorded itself, so a crafted log '
                   'line cannot fake it.',
         'distractors': ['It is faster, but otherwise equivalent.',
                         'It searches all boots and grep searches only this '
                         'one.',
                         'grep cannot read the journal at all.'],
         'teach': 'Trailing underscore fields are recorded by systemd, not '
                  'parsed out of the text, which is exactly why they are worth '
                  'knowing when working out what happened.'},
        {'id': 'sdq-states', 'type': 'mcq',
         'prompt': 'A unit is enabled but not active. What does that mean?',
         'answer': 'It will start at the next boot, and is stopped or crashed '
                   'right now.',
         'distractors': ['It is running but will not come back after a reboot.',
                         'The unit file is missing.',
                         'It is masked.'],
         'teach': 'Loaded, active and enabled are three independent questions. '
                  'Reading all three is most of what `status` is for.'},
        {'id': 'sdq-cat', 'type': 'mcq',
         'prompt': 'What does `systemctl cat nginx` show that reading the unit '
                   'file does not?',
         'answer': 'The vendor file plus every drop-in that overrides it, which '
                   'is what is actually in effect.',
         'distractors': ['The unit file with comments stripped out.',
                         'The current runtime state of the unit.',
                         'The unit file as it was at the last boot.'],
         'teach': 'Drop-ins under <unit>.d/ are easy to forget and are exactly '
                  'where a surprising setting usually lives.'},
    ],
}
