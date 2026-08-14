"""netcat and socat: raw connections, relays, and routing.

The blunt-instrument end of the network group. netcat opens or listens on a TCP port and moves bytes with nothing added, which is how you test whether a port is open, read a banner, or move a file with a listener on one side. socat is the same idea with both ends named and far more they can be: relays, forking listeners, and the pty trick that upgrades a dumb shell. proxychains rounds it out by pushing a program with no proxy option through a SOCKS proxy, with the one limit that it carries TCP only.

nc and socat both need a peer to talk to, and D1 forbids the trainer from being one, so those exercises are marked self and say so. The one verified challenge is the offline half: writing a proxychains config and the rule that governs it. nc, socat and proxychains may not be installed on any given machine, and that is fine: the lessons teach them and no verified challenge depends on them.
"""

MODULE = {
    'id': 'ncsocat',
    'title': 'netcat and socat',
    'group': 'Network',
    'blurb': 'Port probes and banners with nc, relays and shell upgrades with socat, and routing through proxychains.',
    'context': 'You are at a shell making raw connections to ports and relaying between them.',
    'needs': [
        'nc',
        'socat',
    ],
    'prereqs': [
        'linux',
    ],
    'adapter': 'sandbox',
    'estimate': '2 hours',
    'order': 54,
    'lessons': [
        {
            'id': 'nc-basics',
            'title': 'netcat: a raw connection to a port',
            'concept': 'netcat, `nc`, opens or listens on a TCP connection and pipes bytes across it with nothing added. That bluntness is the point: it is how you ask "is this port open, and what is behind it" without a protocol-specific client getting in the way.\n\n`nc -zv host port` just checks whether the port is open, `-z` for a zero-payload probe and `-v` so it says what it found. Drop `-z` and `nc host port` connects and sits there, so a service that greets you shows its banner, which is where version detection starts. `nc -l PORT` listens instead of connecting, and a listener on one side with a connection on the other is a two-line file transfer or a chat.\n\nOne rung above netcat sits `ping`, which asks only "is the host up" over ICMP. It is worth a mention and one caveat: a failed ping does not mean the host is down, because ICMP is dropped by default on plenty of networks and most cloud firewalls, so a port probe with nc is often the more honest test of reachability.',
            'examples': [
                {
                    'label': 'Is it open, and what is it',
                    'code': 'nc -zv host 443         is the port open\nnc -zv host 20-25       a small range\nnc host 22              connect and read the banner\nping -c 3 host          is the host answering ICMP',
                    'note': 'A banner on connect is the cheapest form of version detection, and often all you need.',
                },
                {
                    'label': 'Listener and sender',
                    'code': '# on the receiver\nnc -l 9000 > incoming.bin\n\n# on the sender\nnc -N host 9000 < outgoing.bin',
                    'note': 'One side listens, the other connects, and bytes flow. The sender needs -N (shut down after end of file) or OpenBSD nc holds the connection open and the receiver never sees the transfer finish.',
                },
            ],
            'misconceptions': [
                'A failed ping does not mean the host is down. ICMP is filtered so often that an open TCP port is better evidence it is alive.',
                'netcat is not one program. The traditional, OpenBSD and Nmap (`ncat`) builds differ in flags, so -z, -N and -e are not guaranteed to be present.',
                'nc adds nothing to the bytes, so it is not an HTTP or TLS client. It shows you the raw conversation, which is exactly its value.',
            ],
            'try_it': [
                'Run `nc -zv localhost 22` and then against a closed port, and read the difference between open and refused.',
            ],
            'next': 'nc-socat-relays',
        },
        {
            'id': 'nc-socat-relays',
            'title': 'socat and proxychains: relays and routing',
            'concept': "When netcat runs out, two tools take over. `socat` is netcat with both ends named and far more they can be: it joins any two byte streams, so a listening TCP port on one side and a connection to another host on the other is a relay in one line. It is also the usual way to upgrade a dumb reverse shell into a proper terminal, because it can put your side into raw mode and allocate a pty on the far side.\n\n`proxychains` solves a different problem: pushing a program that has no proxy option through a SOCKS proxy, such as the one `ssh -D` opens. It preloads a library that redirects the program's connections, so it works on anything dynamically linked and not at all on a static binary. You point it at the proxy in a config file and prefix the command.\n\nOne limit decides half of proxychains questions: it can carry TCP and nothing else. UDP and raw sockets do not go through it, which is why an nmap SYN scan (`-sS`) fails through a proxy and a TCP connect scan (`-sT`) works.",
            'examples': [
                {
                    'label': 'socat as a relay and a shell upgrade',
                    'code': 'socat TCP-LISTEN:8080,fork TCP:db.internal:5432\n   anything hitting 8080 here goes to the db\n\n# upgrade a shell, on your side:\nsocat file:$(tty),raw,echo=0 TCP-LISTEN:4444',
                    'note': '`fork` lets it take more than one connection. socat names both ends, which is what makes it a relay rather than a single pipe.',
                },
                {
                    'label': 'Driving a tool through a SOCKS proxy',
                    'code': 'ssh -D 1080 -N -f bastion       open the proxy\n\n# /etc/proxychains.conf  (proxychains4.conf on ng)\n[ProxyList]\nsocks5 127.0.0.1 1080\n\nproxychains curl http://internal/\nproxychains nmap -sT -Pn internal',
                    'note': '`-sT`, not `-sS`: proxychains carries TCP only, so a connect scan works and a SYN scan does not.',
                },
            ],
            'misconceptions': [
                'proxychains cannot proxy UDP or raw sockets. An nmap SYN scan or a DNS query over UDP will not travel through it; a TCP connect scan will.',
                'socat is not just a fancier nc. Naming both endpoints is what lets it relay, fork for multiple clients and allocate a pty, none of which nc does.',
                'A preloaded library only redirects a dynamically linked program, so proxychains does nothing for a static binary.',
            ],
            'try_it': [
                'Relay a local port to another with `socat TCP-LISTEN:8080,fork TCP:localhost:22` and connect through 8080 to prove the hop.',
            ],
            'next': None,
        },
    ],
    'drills': [
        {
            'id': 'rm-cmd-proxychains',
            'type': 'command',
            'answer': 'proxychains curl http://internal/',
            'prompt': 'Push an ordinary command through the SOCKS proxy you just opened.',
            'teach': "It preloads a library that redirects the program's connections, so it works on anything dynamically linked and not at all on static binaries.",
        },
        {
            'id': 'ncd-z',
            'type': 'command',
            'answer': 'nc -zv host 443',
            'prompt': 'Check whether a single port is open.',
            'teach': '-z sends no data and -v reports the result. Drop -z to connect and read a banner instead.',
        },
        {
            'id': 'ncd-banner',
            'type': 'command',
            'answer': 'nc host 22',
            'prompt': 'Connect to a port and read the banner it greets you with.',
            'teach': 'With no -z, nc holds the connection open, so a service that announces itself shows its version.',
        },
        {
            'id': 'ncd-listen',
            'type': 'command',
            'answer': 'nc -l 9000',
            'prompt': 'Listen on a port for an incoming connection.',
            'teach': 'A listener here plus a connection there moves a file or a chat. Redirect with > or < to capture the bytes.',
        },
        {
            'id': 'ncd-socat-relay',
            'type': 'command',
            'answer': 'socat TCP-LISTEN:8080,fork TCP:db.internal:5432',
            'prompt': 'Relay a local port to a service on another host.',
            'teach': 'socat names both ends. fork lets it accept more than one connection rather than serving a single client and exiting.',
        },
    ],
    'challenges': [
        {
            'id': 'nc-proxychains-conf',
            'title': 'Write a proxychains config and its caveat',
            'goal': 'Point proxychains at a SOCKS proxy the offline way: write the config and the one rule that decides which scans work through it.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {
                    '.keep': '',
                },
            },
            'solution': {
                'shell': "printf '%s\\n' '[ProxyList]' 'socks5 127.0.0.1 1080' > proxychains.conf && printf '%s\\n' 'proxychains carries TCP only, no UDP or ICMP' 'so nmap -sT works through it and -sS does not' > notes.txt",
            },
            'steps': [
                {
                    'instruction': 'Write proxychains.conf with a ProxyList naming a socks5 proxy on 127.0.0.1 port 1080.',
                    'hint': "printf '%s\\n' '[ProxyList]' 'socks5 127.0.0.1 1080' > proxychains.conf",
                },
                {
                    'instruction': 'Write notes.txt recording that it carries TCP only, and which nmap scan type that allows.',
                    'hint': 'a connect scan is -sT',
                },
            ],
            'free': 'Produce proxychains.conf pointing at socks5 127.0.0.1 1080, and notes.txt stating the TCP-only limit and that -sT works.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'exists': [
                        'proxychains.conf',
                        'notes.txt',
                    ],
                    'file_contains': {
                        'proxychains.conf': [
                            '[ProxyList]',
                            'socks5',
                            '1080',
                        ],
                        'notes.txt': [
                            'TCP',
                            'sT',
                        ],
                    },
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'nc-banner-grab',
            'title': 'Grab a banner from a live service',
            'goal': 'netcat needs something to connect to, so the trainer cannot check this. Read a banner off a service you can reach.',
            'setup': {
                'kind': 'self',
            },
            'steps': [
                {
                    'instruction': 'Start any service locally, or use one you already run, and note its port.',
                    'hint': 'even an ssh daemon on 22 has a banner',
                },
                {
                    'instruction': 'Check the port is open with a zero-payload probe.',
                    'hint': 'nc -zv localhost PORT',
                },
                {
                    'instruction': 'Connect without -z and read the greeting the service sends.',
                    'hint': 'nc localhost 22',
                },
                {
                    'instruction': 'Try the same against a closed port and read the refusal, so you know both outcomes.',
                },
            ],
            'free': 'Against a real listener: confirm the port is open, then connect and capture the banner it greets you with.',
            'verify': {
                'kind': 'self',
            },
            'fallback': 'self',
        },
    ],
    'quiz': [
        {
            'id': 'ncq-z',
            'type': 'mcq',
            'prompt': 'What does nc -zv host 443 tell you?',
            'answer': 'Whether the port is open, with -z sending no payload and -v reporting the result.',
            'distractors': [
                'The service version running on the port.',
                'Whether the host answers ICMP.',
                'The TLS certificate the port presents.',
            ],
            'teach': 'Drop -z and nc connects so you can read a banner. -z is just the open-or-not probe.',
        },
        {
            'id': 'ncq-ping',
            'type': 'mcq',
            'prompt': 'A host does not answer ping. What can you conclude?',
            'answer': 'Little on its own, because ICMP is widely filtered; a probe to an open TCP port is better evidence.',
            'distractors': [
                'The host is definitely down.',
                'DNS for the host has failed.',
                'The host is up but has no open ports.',
            ],
            'teach': 'Most cloud firewalls drop ICMP by default. Reachability is better judged with nc against a port.',
        },
        {
            'id': 'ncq-proxychains',
            'type': 'mcq',
            'prompt': 'Why does nmap -sS fail through proxychains while -sT works?',
            'answer': 'proxychains carries TCP only, and a SYN scan uses raw packets while a connect scan uses ordinary TCP.',
            'distractors': [
                '-sS needs root and proxychains drops privileges.',
                '-sT is faster so it beats the proxy timeout.',
                'SYN scans are blocked by every SOCKS server.',
            ],
            'teach': 'No UDP, no raw sockets. Anything that is a normal TCP connect goes through; anything below that does not.',
        },
        {
            'id': 'ncq-socat',
            'type': 'mcq',
            'prompt': 'What can socat do that plain nc cannot?',
            'answer': 'Name both endpoints to relay between them, fork for multiple clients, and allocate a pty to upgrade a shell.',
            'distractors': [
                'Encrypt the connection without any certificate.',
                'Scan a range of ports in one command.',
                'Resolve DNS names that nc cannot.',
            ],
            'teach': 'socat joins any two byte streams. That is why it relays and upgrades shells where nc only pipes one connection.',
        },
    ],
}
