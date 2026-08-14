"""nmap: what a port state actually means, and how you asked for it.

The roster skipped nmap once, on the grounds that pentest tooling is
engagement workflow rather than tool proficiency. That was half right. The
engagement half is still out of scope and this module does not teach when to
scan anything. What it teaches is the part that is pure tool proficiency and
is almost universally half-learned: **a port state is an inference, not an
observation**, and which inference you get depends on which packet you chose
to send.

`filtered` is the whole argument for the module. Nearly everyone reads it as
"closed", and it means the opposite of closed in the way that matters: nothing
came back at all, so something is deciding what reaches the host. A student who
cannot tell `closed` from `filtered` cannot read a scan, and no amount of
memorising flags fixes that.

**Verification.** D1 forbids touching a target on a network, so the trainer
builds one: `netlab` opens listening sockets on 127.0.0.1, tells you which
ports they are on, and reads your scan output back. The target is made of
sockets in this process, nothing leaves the machine, and they close with the
challenge. See the netlab adapter for the full argument.

**Unprivileged throughout.** Every challenge here works as your own user,
which means the connect scan rather than the SYN scan. The difference between
the two is taught as content, in the lesson where it belongs, rather than by
asking a trainer to escalate privileges.
"""

MODULE = {
    'id': 'nmap',
    'title': 'nmap',
    'group': 'Security',
    'blurb': 'Port states, scan types, service detection, NSE, and reading the output.',
    'context': 'You are at a shell prompt, scanning a host you are allowed to scan.',
    'needs': ['nmap'],
    'prereqs': ['linux', 'ncsocat'],
    'adapter': 'netlab',
    'estimate': '4-5 hours',
    'order': 70,

    'lessons': [
        {
            'id': 'nm-model',
            'title': 'A scan is a question, and a state is an answer',
            'concept':
                'nmap does not look at a host and see its ports. It sends a '
                'packet, waits, and infers a state from what came back or '
                'from the fact that nothing did. Every state name is the name '
                'of an inference.\n\n'
                'open means something answered and accepted: a SYN-ACK for '
                'TCP, a response for UDP. closed means the host answered and '
                'refused: a RST for TCP, an ICMP port-unreachable for UDP. '
                'Both of those are the host talking to you, which is why both '
                'are good news for mapping: a closed port proves the host is '
                'up and that nothing is dropping your packets.\n\n'
                'filtered is the one that matters. It means nothing came back, '
                'or something came back that was not from the host: an ICMP '
                'administratively-prohibited, or silence. Silence is not '
                'evidence of absence. A firewall dropping packets and a port '
                'with nothing behind it look identical from outside, and nmap '
                'refuses to guess between them.\n\n'
                'open|filtered exists for the same honesty. In a UDP scan or a '
                'FIN scan, an open port and a filtered port both say nothing, '
                'so nmap reports the ambiguity rather than resolving it.',
            'examples': [
                {'label': 'Ask why, and read the evidence',
                 'code': 'nmap --reason 127.0.0.1',
                 'note': 'Adds the packet that produced each state: syn-ack, '
                         'reset, no-response. The best habit in the tool.'},
                {'label': 'The six states nmap can report',
                 'code': 'open  closed  filtered  unfiltered  '
                         'open|filtered  closed|filtered',
                 'note': 'unfiltered means reachable but undecidable, which '
                         'only an ACK scan produces.'},
            ],
            'misconceptions': [
                'filtered does not mean closed. It means you learned nothing, '
                'and that itself is information about the network.',
                'A host with every port filtered is not necessarily down, and '
                'a host that is down is not necessarily filtered.',
                'No state is a statement about what software is listening. '
                'That is -sV, and it is a separate inference.',
            ],
            'try_it': [
                'Run nmap --reason on localhost and read the reason column '
                'before the state column.',
                'Scan a port you know nothing is on, then a port a firewall '
                'covers, and compare the reasons.',
            ],
            'next': 'nm-targets',
        },
        {
            'id': 'nm-targets',
            'title': 'Targets, and whether to ping first',
            'concept':
                'Before nmap scans a port it decides whether the host is '
                'worth scanning at all. That is host discovery, and it is the '
                'stage that silently loses people the most results.\n\n'
                'By default nmap pings first, and "ping" here is not just '
                'ICMP echo: as an unprivileged user it is a TCP connect to '
                '80 and 443, and as root it is an ICMP echo, a TCP SYN to '
                '443, a TCP ACK to 80 and an ICMP timestamp request. If none '
                'of those get an answer, nmap declares the host down and '
                'never scans a single port.\n\n'
                'That is why -Pn exists. It says skip discovery and scan '
                'anyway, treating every target as up. On a network that '
                'blocks pings, -Pn is the difference between an empty report '
                'and a real one. It is also much slower, because you are now '
                'scanning hosts that genuinely are not there.\n\n'
                'The inverse is -sn: discover hosts and stop. It is the right '
                'first command against a range you know nothing about, and it '
                'is the cheapest one.\n\n'
                'Target syntax is its own small language: a name, an address, '
                'CIDR, an octet range like 10.0.0.1-50, a comma list inside '
                'an octet, -iL to read a file, and --exclude to carve pieces '
                'back out.',
            'examples': [
                {'label': 'What is alive in this range',
                 'code': 'nmap -sn 192.168.1.0/24',
                 'note': 'Host discovery only. No ports are scanned.'},
                {'label': 'Scan even though it will not answer a ping',
                 'code': 'nmap -Pn 10.0.0.5',
                 'note': 'Assume up. Slower, and often the only way to see a '
                         'Windows host with the firewall on.'},
                {'label': 'Expand the target list without scanning anything',
                 'code': 'nmap -sL 10.0.0.0/28',
                 'note': 'Prints what would be scanned, and does reverse DNS. '
                         'Sends nothing to the hosts themselves.'},
                {'label': 'From a file, minus the ones you must not touch',
                 'code': 'nmap -iL targets.txt --exclude 10.0.0.1,10.0.0.2',
                 'note': 'The exclusion is the one flag worth typing before '
                         'you need it.'},
            ],
            'misconceptions': [
                'A "host seems down" report usually means discovery failed, '
                'not that the host is off. Try -Pn before believing it.',
                '-sn is not a ping in the icmp sense. It is a small discovery '
                'suite, and it changes depending on your privileges.',
                '-sL sends nothing to the targets, but it does query DNS, so '
                'it is not perfectly silent.',
            ],
            'try_it': [
                'Run nmap -sL on a small CIDR and count what it expands to.',
                'Scan localhost normally, then with -Pn, and time both.',
            ],
            'next': 'nm-scantypes',
        },
        {
            'id': 'nm-scantypes',
            'title': 'Connect, SYN, UDP, and who you have to be',
            'concept':
                'The scan type is the packet nmap chooses to send. Three of '
                'them cover almost everything.\n\n'
                '-sT is the connect scan. nmap asks the operating system to '
                'open a normal TCP connection, exactly as any program would, '
                'and reads whether it succeeded. It needs no privileges at '
                'all, which is why it is the default when you are not root. '
                'It is also the loudest: a completed handshake is a connection '
                'the target can log.\n\n'
                '-sS is the SYN scan, and it is the default when you are '
                'root. nmap builds the packets itself, sends a SYN, reads the '
                'reply, and sends a RST instead of completing the handshake. '
                'It is faster and less likely to be logged by an application, '
                'and it needs raw socket privileges, which is what "needs '
                'root" actually means here.\n\n'
                '-sU is UDP, and it is a different problem. There is no '
                'handshake, so an open UDP port usually says nothing at all, '
                'and nmap has to infer from the absence of an ICMP '
                'port-unreachable, which is itself rate limited by the '
                'target. That is why UDP scans are slow and why so much of '
                'the result is open|filtered rather than open.\n\n'
                'The rest, -sA, -sF, -sN, -sX, are specialised probes for '
                'working out what a firewall is doing rather than what is '
                'listening. Know they exist and what question they ask.',
            'examples': [
                {'label': 'Connect scan, no privileges needed',
                 'code': 'nmap -sT 127.0.0.1',
                 'note': 'What you get by default as an ordinary user.'},
                {'label': 'SYN scan, needs root',
                 'code': 'sudo nmap -sS 10.0.0.5',
                 'note': 'Half-open. The default when nmap can make its own '
                         'packets.'},
                {'label': 'UDP, and be patient',
                 'code': 'sudo nmap -sU --top-ports 20 10.0.0.5',
                 'note': 'Full UDP scans take hours. Top ports first, always.'},
                {'label': 'Ask what the firewall is doing, not what listens',
                 'code': 'sudo nmap -sA 10.0.0.5',
                 'note': 'ACK scan. Reports filtered or unfiltered, never '
                         'open: it maps rules, not services.'},
            ],
            'misconceptions': [
                'A SYN scan is not invisible. It is less likely to reach an '
                'application log, and every modern network sensor sees it.',
                '-sU without -sV mostly tells you which ports are not closed, '
                'which is weaker than it sounds.',
                'The default scan type is not fixed. It is -sS as root and '
                '-sT otherwise, so the same command differs by privilege.',
            ],
            'try_it': [
                'Scan localhost with -sT and note the time, then compare with '
                'sudo nmap -sS on the same ports.',
                'Run a UDP scan of the top 20 ports and watch how much of the '
                'result is open|filtered.',
            ],
            'next': 'nm-ports',
        },
        {
            'id': 'nm-ports',
            'title': 'Which ports get asked about',
            'concept':
                'nmap does not scan all 65535 ports by default. It scans the '
                '1000 most common, chosen from real measurement data that '
                'ships in nmap-services as a frequency for each port. That '
                'default is why a scan takes seconds and why it misses things.\n\n'
                '-p is explicit: a list, a range, a dash on its own for all '
                '65535, a protocol prefix, or a service name. -F is fast, '
                'meaning the top 100. --top-ports takes a number and uses '
                'the same frequency data.\n\n'
                'The habit worth building is two scans rather than one. A '
                'quick top-ports pass tells you what the host is for. A full '
                '-p- pass, run once and saved, tells you what it also has, '
                'which is where the interesting service is roughly half the '
                'time. Doing them in that order means you are reading useful '
                'output while the slow scan is still running.',
            'examples': [
                {'label': 'Everything, all 65535',
                 'code': 'nmap -p- 10.0.0.5',
                 'note': 'The lone dash is the whole range. Minutes, not '
                         'seconds.'},
                {'label': 'A specific set',
                 'code': 'nmap -p 22,80,443,8000-8100 10.0.0.5',
                 'note': 'Commas and ranges mix freely.'},
                {'label': 'Both protocols in one flag',
                 'code': 'sudo nmap -sS -sU -p T:80,443,U:53,161 10.0.0.5',
                 'note': 'T: and U: prefixes select which protocol the list '
                         'applies to.'},
                {'label': 'Only report what is open',
                 'code': 'nmap -p- --open 10.0.0.5',
                 'note': 'Hides the thousands of closed lines. The single '
                         'most useful readability flag.'},
            ],
            'misconceptions': [
                'The default is not "common ports" in the sense of the well '
                'known range 1-1023. It is the top 1000 by measured '
                'frequency, and it includes plenty above 1023.',
                '-F does not make the scan use a faster technique. It scans '
                'fewer ports.',
                'A port missing from the output is not closed unless you '
                'scanned it. Read the "not shown" line.',
            ],
            'try_it': [
                'Compare nmap -F localhost with nmap localhost and count the '
                'ports each says it scanned.',
                'Run a -p- scan against localhost with --open and see what '
                'the default 1000 would have missed.',
            ],
            'next': 'nm-version',
        },
        {
            'id': 'nm-version',
            'title': 'Service and version detection, and how sure it is',
            'concept':
                'A port number is a convention, not a fact. Without -sV, the '
                'service column is a lookup: nmap saw 22 open and printed '
                'ssh because that is what is usually on 22. With -sV it '
                'connects, reads whatever the service says, sends probes if '
                'the service says nothing, and matches the response against '
                'a database of signatures.\n\n'
                'That distinction is worth internalising, because the '
                'unversioned service column is the single most quoted wrong '
                'fact in scan reports. If the report does not have a version '
                'string, nmap did not check.\n\n'
                '--version-intensity from 0 to 9 controls how many probes it '
                'is willing to try; --version-light is 2 and --version-all is '
                '9. -O is operating system detection, which infers from TCP '
                'stack behaviour and needs root, and it is a guess that nmap '
                'labels with a confidence percentage for a reason.\n\n'
                '-A turns on -sV, -O, default scripts and traceroute in one '
                'flag. It is convenient and it is loud, and knowing what it '
                'switches on is the point.',
            'examples': [
                {'label': 'What is really listening',
                 'code': 'nmap -sV -p 22,80 10.0.0.5',
                 'note': 'Adds a VERSION column. Without this flag, the '
                         'SERVICE column is only a guess from the port number.'},
                {'label': 'Try harder on a stubborn port',
                 'code': 'nmap -sV --version-all -p 9999 10.0.0.5',
                 'note': 'Intensity 9. Slower, and the way to identify '
                         'something on a non-standard port.'},
                {'label': 'Everything at once',
                 'code': 'sudo nmap -A 10.0.0.5',
                 'note': 'Equivalent to -sV -O -sC --traceroute. Convenient, '
                         'not subtle.'},
            ],
            'misconceptions': [
                'The SERVICE column without -sV is a table lookup by port '
                'number, not a detection. It is wrong whenever anything is on '
                'a non-standard port.',
                '-O is inference from stack fingerprints, and nmap prints how '
                'confident it is. Quote the confidence with the guess.',
                '-A is not "aggressive" in the sense of dangerous options. It '
                'is a bundle, and the bundle includes default scripts.',
            ],
            'try_it': [
                'Scan a port with and without -sV and compare what the '
                'SERVICE column claims.',
                'Put netcat on a high port, scan it with -sV, and see what '
                'nmap makes of a service that says nothing.',
            ],
            'next': 'nm-nse',
        },
        {
            'id': 'nm-nse',
            'title': 'NSE: the scripts, and which ones are safe',
            'concept':
                'The scripting engine is where nmap stops being a port '
                'scanner. Scripts are Lua, they ship with nmap, and they run '
                'against ports whose state and service match a rule inside '
                'the script.\n\n'
                'Categories are the useful handle: auth, broadcast, brute, '
                'default, discovery, dos, exploit, external, fuzzer, '
                'intrusive, malware, safe, version, vuln. Two of those names '
                'are promises rather than descriptions. safe means the script '
                'should not crash a service or use much bandwidth. intrusive '
                'is everything that might.\n\n'
                '-sC is shorthand for --script=default, and default is a '
                'category, not a file. --script takes a name, a category, a '
                'wildcard like "http-*", or a boolean expression such as '
                '"default and safe". --script-args passes values in, and '
                '--script-help prints what a script does without running it.\n\n'
                'Reading --script-help before running anything from brute, '
                'dos or exploit is the whole of the safety practice here.',
            'examples': [
                {'label': 'The default set',
                 'code': 'nmap -sC -p 80 10.0.0.5',
                 'note': 'Same as --script=default. Safe, quick, and where '
                         'most of the everyday value is.'},
                {'label': 'One script by name',
                 'code': 'nmap --script http-title -p 80 10.0.0.5',
                 'note': 'The .nse extension is optional.'},
                {'label': 'A category, filtered by another',
                 'code': 'nmap --script "vuln and safe" 10.0.0.5',
                 'note': 'Boolean expressions over categories are supported '
                         'and are how you avoid the dangerous half.'},
                {'label': 'Read before you run',
                 'code': 'nmap --script-help smb-os-discovery',
                 'note': 'Prints the description and categories. Sends '
                         'nothing anywhere.'},
                {'label': 'Pass an argument in',
                 'code': 'nmap --script http-enum --script-args '
                         'http-enum.basepath=/app/ -p 80 10.0.0.5',
                 'note': 'Arguments are namespaced by script name.'},
            ],
            'misconceptions': [
                'default is a category, not "all the scripts". Most of the '
                'collection does not run unless you ask for it.',
                'safe is the author category, and it is a claim about intent. '
                'It is not a guarantee about your fragile target.',
                'A script does not run merely because you named it. Its rule '
                'must also match the port and service.',
            ],
            'try_it': [
                'Run --script-help on three scripts from the vuln category '
                'and read what they actually do.',
                'Compare nmap -p 80 with nmap -sC -p 80 against a web server '
                'you own.',
            ],
            'next': 'nm-timing',
        },
        {
            'id': 'nm-timing',
            'title': 'Timing, rate, and not breaking the thing you scan',
            'concept':
                'A scan has a speed, and the speed is a tradeoff between how '
                'long you wait and how much of the answer you lose. The '
                'templates -T0 to -T5 set a bundle of timeouts, parallelism '
                'and delay values at once.\n\n'
                '-T3 is the default. -T4 is what most people use on a local '
                'network and is a reasonable habit. -T5 sacrifices accuracy '
                'for speed and drops results on anything congested. -T0 and '
                '-T1 are measured in hours and exist for evading rate-based '
                'detection, which is exactly the kind of thing this module '
                'does not tell you when to do.\n\n'
                'Underneath the templates are the individual knobs, and they '
                'are what you reach for when a template is wrong: --min-rate '
                'and --max-rate in packets per second, --max-retries, '
                '--host-timeout, and --scan-delay.\n\n'
                'The practical warning is real. A fast scan against fragile '
                'embedded devices, printers, industrial gear or an overloaded '
                'firewall can take them out. Slow is not politeness, it is '
                'accuracy.',
            'examples': [
                {'label': 'The usual working speed',
                 'code': 'nmap -T4 -p- --open 10.0.0.5',
                 'note': 'Sensible on a LAN. Too fast for a congested WAN '
                         'link.'},
                {'label': 'Set a floor rather than a template',
                 'code': 'nmap --min-rate 1000 -p- 10.0.0.5',
                 'note': 'Packets per second. More predictable than -T5 and '
                         'less likely to lose results.'},
                {'label': 'Give up on a host that is wasting your time',
                 'code': 'nmap --host-timeout 5m 10.0.0.0/24',
                 'note': 'Move on rather than stalling the whole range.'},
            ],
            'misconceptions': [
                '-T5 is not simply "faster". It shortens timeouts, so slow '
                'hosts report closed or filtered ports that are actually open.',
                'The templates set several values at once, so mixing -T with '
                'individual knobs means the last flag wins, per knob.',
                'A slow scan is not always the quiet one. -T0 is slow and '
                'still completely visible to anything that keeps state.',
            ],
            'try_it': [
                'Run the same -p- scan at -T3 and -T4 and compare durations '
                'and results.',
                'Scan with --min-rate set low and watch the estimated time '
                'change in the progress line.',
            ],
            'next': 'nm-output',
        },
        {
            'id': 'nm-output',
            'title': 'Output formats, and why you keep the file',
            'concept':
                'A scan that exists only in your scrollback is a scan you '
                'will run again. nmap has four output formats and one flag '
                'that turns on three of them.\n\n'
                '-oN is normal, the same text you saw. -oX is XML, which is '
                'what every other tool reads. -oG is grepable, one host per '
                'line, which is what awk and grep read. -oA takes a basename '
                'and writes all three at once, and it is what to type by '
                'default.\n\n'
                'The grepable format is worth understanding on its own '
                'because it is what makes a scan feed a pipeline: one line '
                'per host, fields separated, so cutting out every host with '
                '443 open is one grep away.\n\n'
                '--resume takes a normal or grepable output file and picks up '
                'where an interrupted scan stopped, which turns a killed '
                'four hour scan from a disaster into an inconvenience. ndiff '
                'compares two XML files and prints what changed, which is how '
                'you scan the same network next month and see only what is '
                'new.',
            'examples': [
                {'label': 'The default habit',
                 'code': 'nmap -A -oA scan-internal 10.0.0.0/24',
                 'note': 'Writes scan-internal.nmap, .xml and .gnmap.'},
                {'label': 'Pull the open web hosts out of a grepable file',
                 'code': 'grep "443/open" scan.gnmap | cut -d" " -f2',
                 'note': 'One line per host is the entire point of -oG.'},
                {'label': 'Pick up an interrupted scan',
                 'code': 'nmap --resume scan.nmap',
                 'note': 'Works from the normal or the grepable file.'},
                {'label': 'What changed since last month',
                 'code': 'ndiff last-month.xml today.xml',
                 'note': 'Ships with nmap. The reason to keep the XML.'},
            ],
            'misconceptions': [
                '-oN is not the same as redirecting stdout. Redirection also '
                'captures the progress noise and loses the structure.',
                'The XML is not just for archiving. It is the interchange '
                'format every other tool expects.',
                '--resume needs the output file, so it only helps if you '
                'wrote one before the scan died.',
            ],
            'try_it': [
                'Scan localhost with -oA and open all three files.',
                'Write a one-line grep over a .gnmap file that lists only '
                'hosts with a given port open.',
            ],
            'next': None,
        },
    ],

    'drills': [
        {'id': 'nmd-default', 'type': 'command',
         'prompt': 'Scan the default 1000 ports of 10.0.0.5.',
         'answer': 'nmap 10.0.0.5',
         'teach': 'No flags is the top 1000 ports by measured frequency, not '
                  'all of them and not 1-1023.'},
        {'id': 'nmd-allports', 'type': 'command',
         'prompt': 'Scan every one of the 65535 TCP ports on 10.0.0.5.',
         'answer': 'nmap -p- 10.0.0.5',
         'accepts': ['nmap -p 1-65535 10.0.0.5'],
         'teach': 'The lone dash means the whole range. -p 1-65535 is the '
                  'same thing spelled out.'},
        {'id': 'nmd-fast', 'type': 'command',
         'prompt': 'Scan only the top 100 ports of 10.0.0.5.',
         'answer': 'nmap -F 10.0.0.5',
         'teach': '-F is fast because it asks about fewer ports, not because '
                  'it sends packets faster.'},
        {'id': 'nmd-topports', 'type': 'command',
         'prompt': 'Scan the 20 most common ports of 10.0.0.5.',
         'answer': 'nmap --top-ports 20 10.0.0.5',
         'teach': 'Same frequency data as the default, with the count in '
                  'your hands.'},
        {'id': 'nmd-portlist', 'type': 'command',
         'prompt': 'Scan ports 22, 80 and 8000 through 8100 on 10.0.0.5.',
         'answer': 'nmap -p 22,80,8000-8100 10.0.0.5',
         'teach': 'Commas and ranges mix freely inside one -p.'},
        {'id': 'nmd-open', 'type': 'command',
         'prompt': 'Scan all ports of 10.0.0.5 and report only the open ones.',
         'answer': 'nmap -p- --open 10.0.0.5',
         'teach': '--open hides the thousands of closed lines. The best '
                  'readability flag in the tool.'},
        {'id': 'nmd-connect', 'type': 'command',
         'prompt': 'Force a TCP connect scan of 10.0.0.5.',
         'answer': 'nmap -sT 10.0.0.5',
         'teach': 'The OS opens a real connection, so it needs no privileges '
                  'and the target can log it.'},
        {'id': 'nmd-syn', 'type': 'command',
         'prompt': 'Run a SYN scan of 10.0.0.5 as root.',
         'answer': 'sudo nmap -sS 10.0.0.5',
         'teach': 'Half open: SYN, read the reply, RST. Needs raw sockets, '
                  'which is what "needs root" means here.'},
        {'id': 'nmd-udp', 'type': 'command',
         'prompt': 'Scan the top 20 UDP ports of 10.0.0.5.',
         'answer': 'sudo nmap -sU --top-ports 20 10.0.0.5',
         'teach': 'UDP has no handshake, so results are slow and often '
                  'open|filtered. Never start with a full UDP range.'},
        {'id': 'nmd-ack', 'type': 'command',
         'prompt': 'Map firewall rules rather than services on 10.0.0.5.',
         'answer': 'sudo nmap -sA 10.0.0.5',
         'teach': 'The ACK scan reports filtered or unfiltered and never '
                  'open: it asks about rules, not listeners.'},
        {'id': 'nmd-ping-sweep', 'type': 'command',
         'prompt': 'Find which hosts are up in 192.168.1.0/24 without '
                   'scanning ports.',
         'answer': 'nmap -sn 192.168.1.0/24',
         'teach': 'Host discovery only. The cheapest first command against a '
                  'range you know nothing about.'},
        {'id': 'nmd-nopping', 'type': 'command',
         'prompt': 'Scan 10.0.0.5 even though it does not answer host discovery.',
         'answer': 'nmap -Pn 10.0.0.5',
         'teach': 'Skip discovery and assume up. The fix for "host seems '
                  'down", and much slower on ranges.'},
        {'id': 'nmd-list', 'type': 'command',
         'prompt': 'List what 10.0.0.0/28 expands to without scanning it.',
         'answer': 'nmap -sL 10.0.0.0/28',
         'teach': 'Sends nothing to the targets, though it does resolve '
                  'names, so it is not perfectly silent.'},
        {'id': 'nmd-iL', 'type': 'command',
         'prompt': 'Scan every target listed in targets.txt.',
         'answer': 'nmap -iL targets.txt',
         'teach': 'One target per line. Pairs with --exclude-file for the '
                  'hosts you must not touch.'},
        {'id': 'nmd-exclude', 'type': 'command',
         'prompt': 'Scan 10.0.0.0/24 but leave out 10.0.0.1 and 10.0.0.2.',
         'answer': 'nmap 10.0.0.0/24 --exclude 10.0.0.1,10.0.0.2',
         'teach': 'Worth typing before you need it. Exclusions are the one '
                  'flag people regret forgetting.'},
        {'id': 'nmd-version', 'type': 'command',
         'prompt': 'Identify what is really listening on ports 22 and 80 of '
                   '10.0.0.5.',
         'answer': 'nmap -sV -p 22,80 10.0.0.5',
         'teach': 'Without -sV the SERVICE column is a lookup by port number, '
                  'and it is wrong for anything on a non-standard port.'},
        {'id': 'nmd-version-all', 'type': 'command',
         'prompt': 'Try every version probe against port 9999 on 10.0.0.5.',
         'answer': 'nmap -sV --version-all -p 9999 10.0.0.5',
         'teach': 'Intensity 9. What to reach for when something on a high '
                  'port will not identify itself.'},
        {'id': 'nmd-os', 'type': 'command',
         'prompt': 'Fingerprint the operating system of 10.0.0.5.',
         'answer': 'sudo nmap -O 10.0.0.5',
         'teach': 'Inference from TCP stack behaviour, and nmap prints its '
                  'confidence for a reason. Quote the confidence.'},
        {'id': 'nmd-aggressive', 'type': 'command',
         'prompt': 'Turn on version, OS, default scripts and traceroute at once.',
         'answer': 'sudo nmap -A 10.0.0.5',
         'teach': '-A is a bundle, not a mood. Knowing what it switches on is '
                  'the point of it.'},
        {'id': 'nmd-sc', 'type': 'command',
         'prompt': 'Run the default script set against port 80 of 10.0.0.5.',
         'answer': 'nmap -sC -p 80 10.0.0.5',
         'accepts': ['nmap --script=default -p 80 10.0.0.5',
                     'nmap --script default -p 80 10.0.0.5'],
         'teach': '-sC is exactly --script=default, and default is a '
                  'category rather than the whole collection.'},
        {'id': 'nmd-script-name', 'type': 'command',
         'prompt': 'Run only the http-title script against port 80 of 10.0.0.5.',
         'answer': 'nmap --script http-title -p 80 10.0.0.5',
         'teach': 'The .nse extension is optional. The script still only '
                  'runs if its rule matches the port and service.'},
        {'id': 'nmd-script-cat', 'type': 'command',
         'prompt': 'Run the scripts that are in both the vuln and safe '
                   'categories on 10.0.0.5.',
         'answer': 'nmap --script "vuln and safe" 10.0.0.5',
         'teach': 'Boolean expressions over categories are how you get the '
                  'vuln checks without the half that might break things.'},
        {'id': 'nmd-script-help', 'type': 'command',
         'prompt': 'Read what the smb-os-discovery script does without running it.',
         'answer': 'nmap --script-help smb-os-discovery',
         'teach': 'Sends nothing anywhere. Doing this before anything from '
                  'brute, dos or exploit is the whole safety practice.'},
        {'id': 'nmd-script-args', 'type': 'command',
         'prompt': 'Run http-enum against port 80 of 10.0.0.5 with basepath /app/.',
         'answer': 'nmap --script http-enum --script-args '
                   'http-enum.basepath=/app/ -p 80 10.0.0.5',
         'teach': 'Script arguments are namespaced by script name, which is '
                  'why the prefix is repeated.'},
        {'id': 'nmd-reason', 'type': 'command',
         'prompt': 'Scan 10.0.0.5 and show the packet behind each port state.',
         'answer': 'nmap --reason 10.0.0.5',
         'teach': 'syn-ack, reset, no-response. Reading the reason is how a '
                  'state stops being a word and becomes evidence.'},
        {'id': 'nmd-timing', 'type': 'command',
         'prompt': 'Scan 10.0.0.5 at the timing template most people use on a LAN.',
         'answer': 'nmap -T4 10.0.0.5',
         'teach': '-T3 is the default and -T4 is the usual working speed. '
                  '-T5 loses results on anything congested.'},
        {'id': 'nmd-minrate', 'type': 'command',
         'prompt': 'Scan all ports of 10.0.0.5 at no fewer than 1000 packets '
                   'per second.',
         'answer': 'nmap --min-rate 1000 -p- 10.0.0.5',
         'teach': 'A rate floor is more predictable than -T5, because it does '
                  'not also shorten the timeouts.'},
        {'id': 'nmd-hosttimeout', 'type': 'command',
         'prompt': 'Scan 10.0.0.0/24, giving up on any host after five minutes.',
         'answer': 'nmap --host-timeout 5m 10.0.0.0/24',
         'teach': 'Moves on rather than letting one dead host stall the whole '
                  'range.'},
        {'id': 'nmd-oa', 'type': 'command',
         'prompt': 'Scan 10.0.0.5 and save all three output formats as scan.',
         'answer': 'nmap -oA scan 10.0.0.5',
         'teach': 'Writes scan.nmap, scan.xml and scan.gnmap. This is what to '
                  'type by default.'},
        {'id': 'nmd-ox', 'type': 'command',
         'prompt': 'Save the scan of 10.0.0.5 as XML in scan.xml.',
         'answer': 'nmap -oX scan.xml 10.0.0.5',
         'teach': 'XML is the interchange format every other tool reads, and '
                  'what ndiff compares.'},
        {'id': 'nmd-og', 'type': 'command',
         'prompt': 'Save the scan of 10.0.0.5 in the one-line-per-host format.',
         'answer': 'nmap -oG scan.gnmap 10.0.0.5',
         'teach': 'Grepable output is what makes a scan feed a pipeline: one '
                  'host per line, so grep and cut can read it.'},
        {'id': 'nmd-resume', 'type': 'command',
         'prompt': 'Continue the interrupted scan recorded in scan.nmap.',
         'answer': 'nmap --resume scan.nmap',
         'teach': 'Turns a killed four hour scan into an inconvenience, but '
                  'only if you wrote an output file first.'},
        {'id': 'nmd-ndiff', 'type': 'command',
         'prompt': 'Show what changed between last-month.xml and today.xml.',
         'answer': 'ndiff last-month.xml today.xml',
         'teach': 'Ships with nmap, and is the reason to keep the XML rather '
                  'than only the text.'},
        {'id': 'nmd-verbose', 'type': 'command',
         'prompt': 'Scan 10.0.0.5 with results reported as they are found.',
         'answer': 'nmap -v 10.0.0.5',
         'teach': 'Verbose prints open ports during the scan instead of only '
                  'in the final report. -vv for more.'},
        {'id': 'nmd-6', 'type': 'command',
         'prompt': 'Scan the IPv6 loopback rather than an IPv4 address.',
         'answer': 'nmap -6 ::1',
         'teach': 'IPv6 is never scanned implicitly, and a host that looks '
                  'closed on v4 is often wide open on v6.'},
        {'id': 'nmd-servicesfile', 'type': 'command',
         'prompt': 'Name the file whose frequency data decides the default '
                   '1000 ports.',
         'answer': 'nmap-services',
         'teach': 'nmap-services carries a measured frequency per port, which '
                  'is what --top-ports and the default both read.'},
    ],

    'challenges': [
        {
            'id': 'nmc-find-open',
            'title': 'Find the ports, and save the evidence',
            'goal': 'Scan the lab ports the trainer opened on loopback and '
                    'write normal output to scan.txt, so the result outlives '
                    'the scrollback.',
            'setup': {'kind': 'netlab', 'ports': [9101, 9102, 9103]},
            'solution': {'shell': 'nmap -sT -p 9090-9110 --open -oN scan.txt '
                                  '127.0.0.1'},
            'steps': [
                {'instruction': 'Read targets.txt to see which ports the '
                                'trainer opened.',
                 'hint': 'cat targets.txt'},
                {'instruction': 'Scan a range around them with a connect '
                                'scan, since you are not root.',
                 'hint': 'nmap -sT -p 9090-9110 127.0.0.1'},
                {'instruction': 'Add --open so the closed ports do not bury '
                                'the result, and -oN scan.txt to save it.',
                 'hint': 'nmap -sT -p 9090-9110 --open -oN scan.txt 127.0.0.1'},
            ],
            'free': 'Produce scan.txt: a connect scan of the lab ports on '
                    '127.0.0.1, showing only what is open.',
            'verify': {'kind': 'netlab', 'expect': {
                'scanned': True,
                'file_contains': {'scan.txt': ['{p1}/tcp', 'open']}}},
            'fallback': 'self',
        },
        {
            'id': 'nmc-version',
            'title': 'Ask what is actually listening',
            'goal': 'The lab ports answer with a banner. Get nmap to read it '
                    'rather than guessing from the port number.',
            'setup': {'kind': 'netlab', 'ports': [9201]},
            'solution': {'shell': 'nmap -sT -sV -p 9195-9205 -oN version.txt '
                                  '127.0.0.1'},
            'steps': [
                {'instruction': 'Scan the lab port without -sV and note what '
                                'the SERVICE column claims.',
                 'hint': 'nmap -sT -p 9195-9205 127.0.0.1'},
                {'instruction': 'Now add version detection and save it to '
                                'version.txt.',
                 'hint': 'nmap -sT -sV -p 9195-9205 -oN version.txt 127.0.0.1'},
                {'instruction': 'Compare the two SERVICE columns. Only one of '
                                'them was checked.'},
            ],
            'free': 'Produce version.txt: a version-detection scan of the lab '
                    'port on 127.0.0.1.',
            'verify': {'kind': 'netlab', 'expect': {
                'scanned': True,
                'file_contains': {'version.txt': ['{p1}/tcp', 'VERSION']}}},
            'fallback': 'self',
        },
        {
            'id': 'nmc-all-formats',
            'title': 'Save a scan every other tool can read',
            'goal': 'Write all three output formats in one command, and see '
                    'what each is shaped for.',
            'setup': {'kind': 'netlab', 'ports': [9301, 9302]},
            'solution': {'shell': 'nmap -sT -p 9295-9310 -oA lab 127.0.0.1'},
            'steps': [
                {'instruction': 'Scan the lab ports with -oA and the basename '
                                'lab.',
                 'hint': 'nmap -sT -p 9295-9310 -oA lab 127.0.0.1'},
                {'instruction': 'Look at all three files it wrote. Note that '
                                'the grepable one is a single line per host.',
                 'hint': 'ls lab.*; cat lab.gnmap'},
            ],
            'free': 'Produce lab.nmap, lab.xml and lab.gnmap from one scan of '
                    'the lab ports.',
            'verify': {'kind': 'netlab', 'expect': {
                'scanned': True,
                'is_file': ['lab.nmap', 'lab.xml', 'lab.gnmap'],
                'file_contains': {'lab.gnmap': '{p1}/open'}}},
            'fallback': 'self',
        },
        {
            'id': 'nmc-grepable',
            'title': 'Feed a scan into a pipeline',
            'goal': 'Use the grepable format for what it is for: pulling one '
                    'fact out of a scan with ordinary text tools.',
            'setup': {'kind': 'netlab', 'ports': [9401, 9402, 9403]},
            'solution': {'shell': 'nmap -sT -p 9395-9410 --open -oG lab.gnmap '
                                  '127.0.0.1 && '
                                  'grep -o "94[0-9][0-9]/open" lab.gnmap '
                                  '| cut -d/ -f1 | sort -u > open-ports.txt'},
            'steps': [
                {'instruction': 'Scan the lab ports, saving grepable output '
                                'to lab.gnmap.',
                 'hint': 'nmap -sT -p 9395-9410 --open -oG lab.gnmap 127.0.0.1'},
                {'instruction': 'Pull just the open port numbers out of it '
                                'into open-ports.txt, one per line.',
                 'hint': 'grep -o "94[0-9][0-9]/open" lab.gnmap | cut -d/ -f1'},
            ],
            'free': 'Produce open-ports.txt containing only the open port '
                    'numbers, extracted from grepable scan output.',
            'verify': {'kind': 'netlab', 'expect': {
                'scanned': True,
                'file_contains': {'open-ports.txt': ['{p1}', '{p2}']},
                'file_lacks': {'open-ports.txt': 'open'}}},
            'fallback': 'self',
        },
        {
            'id': 'nmc-reason',
            'title': 'Tell closed from filtered on evidence',
            'goal': 'Scan one port that is open and one that is not, with '
                    '--reason, and record which packet produced each state.',
            'setup': {'kind': 'netlab', 'ports': [9501]},
            'solution': {'shell': 'nmap -sT --reason -p 9501,9599 -oN why.txt '
                                  '127.0.0.1'},
            'steps': [
                {'instruction': 'Scan the lab port and one nearby port that '
                                'nothing is on, with --reason.',
                 'hint': 'nmap -sT --reason -p 9501,9599 127.0.0.1'},
                {'instruction': 'Save it to why.txt and read the REASON '
                                'column: syn-ack against conn-refused.',
                 'hint': 'nmap -sT --reason -p 9501,9599 -oN why.txt 127.0.0.1'},
                {'instruction': 'Note that neither of these is filtered. On '
                                'loopback nothing is dropping your packets.'},
            ],
            'free': 'Produce why.txt showing both an open and a closed lab '
                    'port with the reason for each state.',
            'verify': {'kind': 'netlab', 'expect': {
                'scanned': True,
                'file_contains': {'why.txt': ['{p1}/tcp', 'syn-ack',
                                              'conn-refused']}}},
            'fallback': 'self',
        },
        {
            'id': 'nmc-own-machine',
            'title': 'Scan your own machine and reconcile it',
            'goal': 'Everything above was a lab the trainer built. This is '
                    'your real machine, so the trainer cannot check it.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'List everything your machine is listening on, '
                                'from the inside.',
                 'hint': 'ss -tulpn'},
                {'instruction': 'Now scan yourself from the outside and save '
                                'it.',
                 'hint': 'nmap -sT -p- --open -oA self-scan 127.0.0.1'},
                {'instruction': 'Reconcile the two lists. Anything nmap sees '
                                'that ss did not explain is worth explaining.'},
                {'instruction': 'Scan your own machine on its LAN address too, '
                                'and note what the firewall changed.'},
            ],
            'free': 'Scan your own machine inside and out, and account for '
                    'every port that appears in one list and not the other.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
    ],

    'quiz': [
        {'id': 'nmq-filtered', 'type': 'mcq',
         'prompt': 'nmap reports a port as filtered. What did it observe?',
         'answer': 'Nothing came back, so it cannot tell open from blocked.',
         'distractors': ['A RST, meaning nothing is listening.',
                         'A SYN-ACK from a service that then hung up.',
                         'An open port that refused the version probe.'],
         'teach': 'closed is the host answering with a refusal. filtered is '
                  'silence, which is a fact about the network rather than '
                  'about the port.'},
        {'id': 'nmq-default-type', 'type': 'mcq',
         'prompt': 'You run plain nmap as an ordinary user. Which scan type '
                   'runs?',
         'answer': '-sT, the connect scan, because raw sockets need root.',
         'distractors': ['-sS, the SYN scan, which is always the default.',
                         '-sU, since TCP needs privileges and UDP does not.',
                         '-sA, because it is the only unprivileged option.'],
         'teach': 'The default depends on your privileges: -sS as root, -sT '
                  'otherwise. The same command differs by who runs it.'},
        {'id': 'nmq-default-ports', 'type': 'mcq',
         'prompt': 'How many ports does a default nmap scan actually cover?',
         'answer': 'The top 1000 by measured frequency, from nmap-services.',
         'distractors': ['All 65535.',
                         'The well known ports, 1 to 1023.',
                         'The 100 most common, the same set as -F.'],
         'teach': 'It is a frequency list rather than a range, so the default '
                  'includes plenty of high ports and misses plenty of low '
                  'ones.'},
        {'id': 'nmq-service-column', 'type': 'mcq',
         'prompt': 'A scan without -sV shows 8080 as http-proxy. What is that '
                   'claim based on?',
         'answer': 'A lookup of the port number in a table, with nothing '
                   'checked.',
         'distractors': ['A banner the service sent on connect.',
                         'A signature match against the response to a probe.',
                         'The HTTP response headers nmap parsed.'],
         'teach': 'This is the most quoted wrong fact in scan reports. No '
                  'version string means nothing was checked.'},
        {'id': 'nmq-udp', 'type': 'mcq',
         'prompt': 'Why is so much of a UDP scan reported as open|filtered?',
         'answer': 'An open UDP port often replies with nothing, which looks '
                   'exactly like being dropped.',
         'distractors': ['UDP scans are unprivileged, so nmap sees less.',
                         'nmap does not have UDP service signatures.',
                         'The kernel rate limits outgoing UDP packets.'],
         'teach': 'There is no handshake to succeed or fail, so the inference '
                  'rests on an ICMP port-unreachable that may never come.'},
        {'id': 'nmq-pn', 'type': 'mcq',
         'prompt': 'nmap says "Host seems down". You believe it is up. Which '
                   'flag do you reach for?',
         'answer': '-Pn, to skip host discovery and scan anyway.',
         'distractors': ['-sn, to do host discovery properly.',
                         '-v, to see what discovery actually sent.',
                         '-T5, since discovery probably timed out.'],
         'teach': '-Pn treats every target as up. It is the fix, and it is '
                  'much slower across a range because dead hosts get scanned '
                  'too.'},
        {'id': 'nmq-sc', 'type': 'mcq',
         'prompt': 'What exactly does -sC run?',
         'answer': 'The scripts in the default category, which is a small '
                   'subset.',
         'distractors': ['Every script that ships with nmap.',
                         'Every script marked safe.',
                         'The scripts matching the detected service, whatever '
                         'their category.'],
         'teach': '-sC is --script=default. default is a category, and most '
                  'of the collection stays put unless you ask for it.'},
        {'id': 'nmq-t5', 'type': 'mcq',
         'prompt': 'Why can -T5 produce fewer open ports than -T3 on the same '
                   'host?',
         'answer': 'It shortens timeouts, so slow replies are missed and read '
                   'as closed or filtered.',
         'distractors': ['It scans fewer ports to save time.',
                         'It skips the second retry of every probe only.',
                         'It disables service detection.'],
         'teach': 'Speed here is bought with accuracy. A rate floor with '
                  '--min-rate is usually the better trade.'},
        {'id': 'nmq-og', 'type': 'mcq',
         'prompt': 'You want to list every host in a scan with 443 open, using '
                   'grep. Which output format?',
         'answer': '-oG, because it puts one host per line.',
         'distractors': ['-oN, because it is the format you already read.',
                         '-oX, because XML is the machine readable one.',
                         '-oA, because it is the only one that keeps port '
                         'state.'],
         'teach': 'XML is for other tools, grepable is for your pipeline. -oA '
                  'gives you both and costs nothing.'},
        {'id': 'nmq-a-bundle', 'type': 'mcq',
         'prompt': 'Which set of things does -A switch on?',
         'answer': 'Version detection, OS detection, default scripts and '
                   'traceroute.',
         'distractors': ['A full 65535 port scan at -T4.',
                         'All scripts including the intrusive ones.',
                         'A SYN scan with maximum version intensity.'],
         'teach': '-A is a bundle rather than a mood, and the bundle does not '
                  'touch which ports get scanned.'},
        {'id': 'nmq-resume', 'type': 'mcq',
         'prompt': 'A four hour -p- scan was killed at hour three. What '
                   'decides whether you can pick it up?',
         'answer': 'Whether you wrote an output file, which nmap --resume '
                   'reads.',
         'distractors': ['Whether the scan was run under sudo.',
                         'Whether the target range was given as CIDR.',
                         'Nothing: a killed scan always restarts from the '
                         'beginning.'],
         'teach': '--resume reads a normal or grepable file. With no -oN or '
                  '-oG there is nothing to resume from, which is the real '
                  'argument for typing -oA by habit.'},
    ],
}
