"""Remote access and network tooling: one arc through three questions.

Not a leftovers bin. Each stage consumes the previous one's answer: can I reach
the service, can I get a session, can I move data and traffic. Port forwarding
is the climax because it is the hardest material here, the worst taught
elsewhere, and it only makes sense once the first two stages are solid.

**This module is the weakest in the roster for verification, and says so.**
D1 forbids the trainer from touching anything on a network, and most of what
this teaches needs a second machine. So the split is deliberate and visible:

* **verified** covers only the genuinely offline parts. Writing an ssh config,
  generating a keypair with the right permissions, running rsync between two
  directories the trainer owns, building and inspecting a certificate. All of
  that is real work, checked for real, with no packet leaving the machine.
* **graded** covers the predictions, which is where the misconceptions live:
  which files rsync's trailing slash actually moves, and which direction `-L`
  and `-R` point.
* **self** covers anything needing a second machine, and the module says so
  rather than pretending. A throwaway container is the cheap lab.

Several tools taught here may not be installed on any given machine, `socat`,
`nc`, `xfreerdp`, `proxychains` and `sshfs` among them. That is fine: the
lessons teach them, and no challenge depends on them.
"""

MODULE = {
    'id': 'remote',
    'title': 'Remote access',
    'group': 'Network',
    'blurb': 'Reaching machines, getting a session, and moving data and traffic.',
    'context': 'You are at a shell on your own machine, reaching out to somewhere else.',
    'needs': ('ssh', 'curl'),
    'prereqs': ['linux'],
    'adapter': 'sandbox',
    'estimate': '6-8 hours',
    'order': 51,

    'lessons': [
        {
            'id': 'rm-reach',
            'title': 'Can I reach the service at all?',
            'next': 'rm-tls',
            'concept': (
                'Before anything else, four questions in order, each cheap and '
                'each ruling something out.\n\n'
                'Does the name resolve? `dig +short host`. Does the host '
                'answer? `ping`, though plenty of hosts drop it deliberately. '
                'Is the port open and what is behind it? `nc -zv host port`, or '
                '`nc host port` to read the banner. Does the application '
                'answer? `curl -I` for HTTP, `openssl s_client` for TLS.\n\n'
                'Working down that list turns "the server is broken" into a '
                'specific claim, and the specific claim is usually enough to '
                'fix it. Skipping to the last step is why people spend an hour '
                'on a DNS problem.'
            ),
            'examples': [
                {
                    'label': 'The ladder',
                    'code': ('dig +short example.com        does it resolve\n'
                             'dig +trace example.com        where did that come from\n'
                             'ping -c 3 example.com         does it answer\n'
                             'nc -zv example.com 443        is the port open\n'
                             'curl -sS -o /dev/null -w "%{http_code}\\n" URL\n'
                             'openssl s_client -connect host:443'),
                    'note': '`dig +short` is the one to build muscle memory for. '
                            'Plain dig prints a page when you wanted a line.',
                },
                {
                    'label': 'curl worth knowing',
                    'code': ('curl -I URL          headers only\n'
                             'curl -L URL          follow redirects\n'
                             'curl -sS URL         quiet, but still show errors\n'
                             'curl -d @file URL    POST a file\n'
                             'curl -H "X: y" URL   add a header\n'
                             'curl -k URL          skip certificate checks'),
                    'note': '`-sS` together is the useful pair: silent progress, '
                            'loud failures. `-s` alone hides real errors.',
                },
            ],
            'misconceptions': [
                'A failed ping does not mean the host is down. ICMP is dropped '
                'by default on plenty of networks and by most cloud firewalls.',
                '`curl -k` does not fix a certificate problem, it ignores it. '
                'Fine for a five-second diagnosis, never in a script.',
                '`dig` reads your resolver by default, so a stale cache can lie '
                'to you. `dig @1.1.1.1 host` asks someone else.',
            ],
            'try_it': [
                'Run the whole ladder against a site you use, and notice how '
                'fast each step is.',
            ],
        },
        {
            'id': 'rm-tls',
            'title': 'Certificates, and the format maze',
            'next': 'rm-keys',
            'concept': (
                'openssl is cryptic mostly because its subcommands are '
                'unrelated programs sharing a name. Two of them earn their '
                'keep.\n\n'
                '`openssl s_client -connect host:443` opens a TLS connection '
                'and prints the whole handshake, which is how you find out '
                'which certificate is actually being served and whether the '
                'chain is complete. `openssl x509 -text -noout` reads a '
                'certificate file and prints it in a form a human can check.\n\n'
                'The format confusion is worth ten seconds. **PEM** is base64 '
                'text with `-----BEGIN` lines and is what you almost always '
                'have. **DER** is the same data in binary. **PKCS12** or `.p12` '
                'bundles a certificate and its private key together, usually '
                'for something Windows-shaped. They convert freely, and knowing '
                'that is most of the battle.'
            ),
            'examples': [
                {
                    'label': 'Reading things',
                    'code': ('openssl x509 -in cert.pem -text -noout\n'
                             'openssl x509 -in cert.pem -noout -dates\n'
                             'openssl x509 -in cert.pem -noout -subject\n'
                             '\n'
                             'openssl s_client -connect host:443 -servername host\n'
                             'openssl s_client ... </dev/null 2>/dev/null \\\n'
                             '  | openssl x509 -noout -dates'),
                    'note': '`-servername` matters: without it you may get the '
                            'default certificate rather than the one for the '
                            'name you asked about.',
                },
                {
                    'label': 'Converting',
                    'code': ('PEM   base64 text, -----BEGIN CERTIFICATE-----\n'
                             'DER   the same thing, binary\n'
                             'P12   cert plus private key in one file\n'
                             '\n'
                             'openssl x509 -in c.der -inform der -out c.pem\n'
                             'openssl pkcs12 -in bundle.p12 -nodes -out all.pem'),
                    'note': '`-noout` means "do not print the certificate '
                            'itself", which is almost always what you want '
                            'alongside `-text`.',
                },
            ],
            'misconceptions': [
                'An expired certificate and an untrusted one are different '
                'failures with different fixes. `-noout -dates` settles the '
                'first in one command.',
                'A missing intermediate certificate looks like a broken server '
                'to some clients and fine to others, because some clients '
                'cache intermediates. `s_client` shows you the chain actually '
                'sent.',
                '`.crt`, `.cer` and `.pem` are file extensions, not formats. '
                'Open the file and look for `-----BEGIN`.',
            ],
            'try_it': [
                'Run `openssl s_client -connect example.com:443 -servername '
                'example.com </dev/null | openssl x509 -noout -dates`.',
            ],
        },
        {
            'id': 'rm-keys',
            'title': 'SSH keys, and why permissions matter',
            'next': 'rm-config',
            'concept': (
                'A key pair is two files: a private key you never move, and a '
                '`.pub` you copy anywhere. Authentication happens by proving '
                'you hold the private one without sending it.\n\n'
                'Generate with `ssh-keygen -t ed25519`. Use ed25519 rather than '
                'RSA unless something old refuses it: the keys are shorter, '
                'faster and at least as strong. Give it a passphrase; the agent '
                'in the next lesson is what stops that being annoying.\n\n'
                'ssh refuses to use a private key that others can read, and the '
                'error is blunt about it. `chmod 600` on the key and `700` on '
                '`~/.ssh` is the fix, and the reason the check exists is that a '
                'world-readable private key is not a secret.'
            ),
            'examples': [
                {
                    'label': 'Making and installing one',
                    'code': ('ssh-keygen -t ed25519 -C "you@machine"\n'
                             'ssh-copy-id user@host        install the public key\n'
                             '\n'
                             'chmod 700 ~/.ssh\n'
                             'chmod 600 ~/.ssh/id_ed25519\n'
                             'chmod 644 ~/.ssh/id_ed25519.pub'),
                    'note': '`ssh-copy-id` appends to the remote '
                            '`~/.ssh/authorized_keys` and fixes its permissions '
                            'for you, which is why it beats doing it by hand.',
                },
            ],
            'misconceptions': [
                'The `.pub` file is the one you copy. Copying the other one is '
                'the mistake this lesson exists to prevent.',
                '"Permissions 0644 for key are too open" is not a bug. Fix the '
                'mode rather than looking for a flag to silence it.',
                'A passphrase does not mean typing it constantly. That is what '
                'the agent is for.',
            ],
            'try_it': [
                'Run `ls -l ~/.ssh` and check every private key is 600 and the '
                'directory is 700.',
            ],
        },
        {
            'id': 'rm-config',
            'title': 'The config file that makes everything short',
            'next': 'rm-agent',
            'concept': (
                '`~/.ssh/config` is the highest-value file in this module. It '
                'turns a command nobody can remember into a word.\n\n'
                'Each `Host` block names an alias and the settings that apply '
                'to it: the real hostname, the user, the port, which key. After '
                'that, `ssh web` is the whole command, and so is `scp file '
                'web:`, and so is `rsync -a dir web:`, because everything that '
                'speaks ssh reads this file.\n\n'
                '`ProxyJump` is the one that earns its place fastest. A host '
                'reachable only through a bastion becomes one word too, and ssh '
                'sets up the hop itself.'
            ),
            'examples': [
                {
                    'label': 'A config worth having',
                    'code': ('Host web\n'
                             '    HostName 203.0.113.10\n'
                             '    User deploy\n'
                             '    IdentityFile ~/.ssh/id_ed25519\n'
                             '\n'
                             'Host db\n'
                             '    HostName 10.0.0.5\n'
                             '    User admin\n'
                             '    ProxyJump web\n'
                             '\n'
                             'Host *\n'
                             '    ServerAliveInterval 60'),
                    'note': '`ssh db` now hops through web automatically. The '
                            '`Host *` block sets defaults for everything.',
                },
            ],
            'misconceptions': [
                'The first matching setting wins, not the last, so put specific '
                'hosts above `Host *`. This surprises people who expect the '
                'later value to override.',
                'The config is read by scp, sftp, rsync and git over ssh too, '
                'so one alias fixes all of them at once.',
                '`ProxyJump` replaces the old `ProxyCommand ssh -W` incantation '
                'you will find in older answers.',
            ],
            'try_it': [
                'Add a `Host` block for a machine you use and confirm `ssh '
                'alias` works with nothing else typed.',
            ],
        },
        {
            'id': 'rm-agent',
            'title': 'The agent, and why forwarding is dangerous',
            'next': 'rm-rdp',
            'concept': (
                'The agent holds your decrypted private key in memory so you '
                'type the passphrase once per session rather than once per '
                'connection. `ssh-add` puts a key in; `ssh-add -l` lists what '
                'is loaded.\n\n'
                'Agent **forwarding**, `ssh -A`, makes your local agent '
                'reachable from the machine you connect to, so you can hop '
                'onward without copying keys. It is convenient and it is a real '
                'risk: anyone with root on that intermediate machine can use '
                'your agent, for as long as you are connected, to authenticate '
                'as you anywhere your key works.\n\n'
                'The safer answer is almost always `ProxyJump`, which builds '
                'the hop locally and never exposes the agent to the middle '
                'machine at all. Reach for `-A` only on machines you already '
                'trust completely, and prefer to set it per-host rather than '
                'globally.'
            ),
            'examples': [
                {
                    'label': 'Using the agent',
                    'code': ('ssh-add ~/.ssh/id_ed25519    load a key\n'
                             'ssh-add -l                    what is loaded\n'
                             'ssh-add -D                    forget everything\n'
                             'ssh-add -t 1h key             expire it after an hour'),
                    'note': '`-t` is a good habit on a laptop: the key stops '
                            'being usable after an hour rather than until '
                            'reboot.',
                },
                {
                    'label': 'Forwarding, and the better answer',
                    'code': ('ssh -A bastion       forwards your agent (risky)\n'
                             'ssh -J bastion db    ProxyJump instead (safe)\n'
                             '\n'
                             'in config:\n'
                             '  Host db\n'
                             '      ProxyJump bastion'),
                    'note': 'ProxyJump does the hop from your machine, so the '
                            'bastion never sees your agent.',
                },
            ],
            'misconceptions': [
                'Agent forwarding does not copy your key. It exposes the '
                'ability to use it, which is nearly as bad and lasts as long as '
                'the connection.',
                '`ForwardAgent yes` inside `Host *` is a common and bad idea. '
                'Scope it to the one host that needs it, or use ProxyJump.',
            ],
            'try_it': [
                'Run `ssh-add -l`. If it says the agent has no identities, '
                'that is why you are being asked for a passphrase.',
            ],
        },
        {
            'id': 'rm-rdp',
            'title': 'The Windows side',
            'next': 'rm-transfer',
            'concept': (
                'Same problem, different operating system. `xfreerdp` is the '
                'CLI RDP client, and it is worth knowing because the graphical '
                'ones give you no way to script or to record what you did.\n\n'
                'The shape is the same as ssh: identify yourself, name the '
                'host, and add the options that make the session usable. The '
                'options are the part nobody remembers, so this is drill '
                'material rather than concept material.\n\n'
                'The three worth memorising are dynamic resolution so the '
                'session resizes with the window, clipboard sharing, and drive '
                'redirection so you can move files without a second tool.'
            ),
            'examples': [
                {
                    'label': 'A usable session',
                    'code': ('xfreerdp /u:user /p:pass /v:host\n'
                             'xfreerdp /u:user /v:host /dynamic-resolution \\\n'
                             '         +clipboard /drive:share,/home/me/share\n'
                             '\n'
                             '/u: user   /p: password   /v: host\n'
                             '/d: domain          for a domain account'),
                    'note': 'Prefer leaving `/p:` off and being prompted, so '
                            'the password does not land in your shell history.',
                },
            ],
            'misconceptions': [
                'A password on the command line is visible in `ps` output to '
                'every user on the machine, and in your history afterwards.',
                'RDP is not ssh with pictures. It is a full desktop session, so '
                'disconnecting and logging off are different things and leave '
                'the session in different states.',
            ],
            'try_it': [
                'If you have a Windows host to hand, connect once with '
                '`/dynamic-resolution` and once without, and resize the window.',
            ],
        },
        {
            'id': 'rm-transfer',
            'title': 'Moving data, and the trailing slash',
            'next': 'rm-forwarding',
            'concept': (
                '`scp` copies a file and is fine for one file. `rsync` copies '
                'only differences, resumes, preserves permissions, and can '
                'delete things on the destination that no longer exist on the '
                'source. For anything more than one file, rsync.\n\n'
                'The trailing slash on the SOURCE is the thing that catches '
                'everyone, and it is worth learning deliberately rather than by '
                'accident. `rsync -a src dest/` copies the directory **into** '
                'dest, giving `dest/src/`. `rsync -a src/ dest/` copies the '
                '**contents** of src into dest. One character, completely '
                'different result.\n\n'
                '`--delete` makes the destination match the source exactly, '
                'including removing files. Combined with a wrong trailing slash '
                'it will happily delete a great deal. `--dry-run` first, every '
                'time: it is a habit rather than a flag.'
            ),
            'examples': [
                {
                    'label': 'The trailing slash',
                    'code': ('src/  contains  a.txt  b.txt\n'
                             '\n'
                             'rsync -a src  dest/   ->  dest/src/a.txt\n'
                             'rsync -a src/ dest/   ->  dest/a.txt\n'
                             '\n'
                             'the slash means "the contents of"'),
                    'note': 'Say it out loud once: slash means contents. It is '
                            'the single most useful sentence in this module.',
                },
                {
                    'label': 'Using it safely',
                    'code': ('rsync -av --dry-run src/ host:dest/   look first\n'
                             'rsync -av src/ host:dest/            then do it\n'
                             '\n'
                             '-a  archive: recursive, keeps permissions,\n'
                             '    times, symlinks\n'
                             '-v  verbose      -z  compress in transit\n'
                             '--delete  make dest match src exactly\n'
                             '-P  progress and resume partial files'),
                    'note': '`-avP --dry-run` is the combination to type by '
                            'reflex before anything with --delete.',
                },
            ],
            'misconceptions': [
                'The trailing slash on the DESTINATION does almost nothing. It '
                'is the source slash that changes the result.',
                '`--delete` deletes on the destination, not the source, and '
                'with the wrong source slash that can be everything.',
                'rsync over ssh reads your `~/.ssh/config`, so an alias works '
                'here exactly as it does for ssh.',
            ],
            'try_it': [
                'Make two directories and run rsync both ways, with and '
                'without the source slash. Look at the result each time.',
            ],
        },
        {
            'id': 'rm-forwarding',
            'title': 'Port forwarding: the climax',
            'concept': (
                'This is the hardest material in the module and the reason the '
                'first two stages came first. Three flags, and the trick is to '
                'read them as "which end does the listening".\n\n'
                '**`-L` is local**: ssh listens on YOUR machine and forwards to '
                'somewhere reachable from the remote. `ssh -L 8080:localhost:80 '
                'host` means your `localhost:8080` becomes the remote\'s port '
                '80. Use it to reach something you cannot reach directly.\n\n'
                '**`-R` is remote**: ssh listens on the REMOTE machine and '
                'forwards back to you. Use it to expose something of yours to '
                'the far side.\n\n'
                '**`-D` is dynamic**: ssh opens a SOCKS proxy on your machine '
                'and sends anything through it out of the remote. That is not '
                'one port, it is a general route, and `proxychains cmd` is how '
                'you push an arbitrary program through it.\n\n'
                'The mnemonic that sticks: Local listens locally, Remote '
                'listens remotely, Dynamic listens locally and goes anywhere.'
            ),
            'examples': [
                {
                    'label': 'The three',
                    'code': ('ssh -L 8080:db.internal:5432 bastion\n'
                             '   your  localhost:8080  ->  db.internal:5432\n'
                             '\n'
                             'ssh -R 9000:localhost:3000 host\n'
                             '   their localhost:9000  ->  your  localhost:3000\n'
                             '\n'
                             'ssh -D 1080 host\n'
                             '   a SOCKS proxy on 1080, out via host'),
                    'note': 'In `-L A:B:C`, A is the port you open, and B:C is '
                            'resolved FROM THE REMOTE, which is why '
                            '`localhost` there means the remote machine.',
                },
                {
                    'label': 'Using the dynamic one',
                    'code': ('ssh -D 1080 -N -f bastion      open it, no shell\n'
                             '\n'
                             '# /etc/proxychains.conf\n'
                             'socks5 127.0.0.1 1080\n'
                             '\n'
                             'proxychains curl http://internal/\n'
                             'proxychains nmap -sT internal'),
                    'note': '`-N` means no command, `-f` means background. '
                            'Together they are "just the tunnel".',
                },
            ],
            'misconceptions': [
                '`localhost` in the middle of `-L` is resolved on the REMOTE '
                'machine. This is the single most common port-forwarding '
                'confusion.',
                '`-R` on a public interface needs `GatewayPorts` enabled on the '
                'remote sshd, and is off by default for good reason.',
                'proxychains cannot proxy UDP or raw sockets, so an nmap SYN '
                'scan through it does not work. `-sT` does.',
            ],
            'try_it': [
                'Run `ssh -L 8080:localhost:80 localhost` against your own '
                'machine and fetch `http://localhost:8080`. It is a tunnel to '
                'yourself, and it makes the shape obvious.',
            ],
        },
    ],

    'drills': [
        {'id': 'rm-cmd-dig', 'type': 'command', 'answer': 'dig +short example.com',
         'prompt': 'Resolve a name and print just the answer, not a page of it.',
         'teach': '+short prints just the record data, which is what a script '
                  'wants. nslookup is the tool people reach for and the one '
                  'that hides which server answered.'},
        {'id': 'rm-cmd-digtrace', 'type': 'command', 'answer': 'dig +trace example.com',
         'prompt': 'Follow a name resolution from the root servers down, to see '
                   'where the answer actually came from.',
         'teach': 'It queries each level itself instead of asking your '
                  'resolver, so it shows the real delegation chain and '
                  'bypasses every cache on the way.'},
        {'id': 'rm-cmd-digat', 'type': 'command', 'answer': 'dig @1.1.1.1 example.com',
         'prompt': 'Ask a specific resolver rather than your own, to rule out a '
                   'stale cache.',
         'teach': 'If a public resolver gives a different answer from your '
                  'default, the problem is caching or split-horizon DNS '
                  'rather than the record itself.'},
        {'id': 'rm-cmd-curl-i', 'type': 'command', 'answer': 'curl -I https://example.com',
         'prompt': 'Fetch only the response headers from a URL.',
         'teach': '-I sends HEAD, and some servers answer HEAD differently '
                  'from GET. Use -sD - -o /dev/null when that difference '
                  'matters.'},
        {'id': 'rm-cmd-curl-ss', 'type': 'command', 'answer': 'curl -sS https://example.com',
         'prompt': 'Fetch a URL quietly, but still show errors if it fails.',
         'teach': '-s alone hides real failures. The pair is what you want in '
                  'a script.'},
        {'id': 'rm-cmd-curl-l', 'type': 'command', 'answer': 'curl -L https://example.com',
         'prompt': 'Fetch a URL, following any redirects.',
         'teach': 'curl does not follow redirects by default, which is why an '
                  'unexplained empty response is usually a 301 you never saw.'},
        {'id': 'rm-cmd-sclient', 'type': 'command',
         'answer': 'openssl s_client -connect example.com:443',
         'prompt': 'Open a TLS connection and print the handshake, to see which '
                   'certificate is really being served.',
         'teach': 'It prints the whole chain the server actually sent, which '
                  'is how you catch a missing intermediate certificate that '
                  'browsers quietly paper over.'},
        {'id': 'rm-cmd-x509', 'type': 'command',
         'answer': 'openssl x509 -in cert.pem -text -noout',
         'prompt': 'Print a certificate file in a form a human can read.',
         'teach': '-noout means "do not also dump the certificate itself", '
                  'which is almost always what you want with -text.'},
        {'id': 'rm-cmd-dates', 'type': 'command',
         'answer': 'openssl x509 -in cert.pem -noout -dates',
         'prompt': 'Check only when a certificate becomes valid and when it '
                   'expires.',
         'teach': '-noout suppresses the certificate body so you get the two '
                  'lines you asked for. Add -subject and -issuer for who it '
                  'is and who signed it.'},
        {'id': 'rm-cmd-keygen', 'type': 'command',
         'answer': 'ssh-keygen -t ed25519', 'accepts': ['ssh-keygen -t ed25519 -C "you@machine"'],
         'prompt': 'Generate a modern SSH key pair.',
         'teach': 'ed25519 rather than RSA: shorter, faster, at least as '
                  'strong, unless something old refuses it.'},
        {'id': 'rm-cmd-copyid', 'type': 'command', 'answer': 'ssh-copy-id user@host',
         'prompt': 'Install your public key on a remote machine.',
         'teach': 'It appends to the remote authorized_keys and fixes the '
                  'permissions, which is the step people get wrong doing it '
                  'by hand.'},
        {'id': 'rm-cmd-chmod-key', 'type': 'command', 'answer': 'chmod 600 ~/.ssh/id_ed25519',
         'prompt': 'Fix the permissions ssh complains about on a private key.',
         'teach': 'ssh refuses a private key others can read, and the error '
                  'names the file rather than the mode, so it reads like a '
                  'missing key.'},
        {'id': 'rm-cmd-agent-add', 'type': 'command', 'answer': 'ssh-add -t 1h ~/.ssh/id_ed25519',
         'prompt': 'Load a key into the agent, but only for an hour.',
         'teach': 'A good laptop habit: the key stops being usable after an '
                  'hour rather than until reboot.'},
        {'id': 'rm-cmd-agent-l', 'type': 'command', 'answer': 'ssh-add -l',
         'prompt': 'List which keys the agent currently holds.',
         'teach': 'If this comes back empty, every key-based login will fail '
                  'and the reason is the agent, not the server.'},
        {'id': 'rm-cmd-jump', 'type': 'command', 'answer': 'ssh -J bastion db',
         'prompt': 'Reach a machine through a bastion, without exposing your '
                   'agent to the bastion.',
         'teach': 'The safer answer than ssh -A. The hop is built on your '
                  'machine, so the middle never sees your agent.'},
        {'id': 'rm-cmd-local', 'type': 'command',
         'answer': 'ssh -L 8080:db.internal:5432 bastion',
         'prompt': 'Make db.internal:5432, reachable only from the bastion, appear on your port 8080.',
         'teach': 'Local listens locally. The middle host:port is resolved from '
                  'the remote, which is the usual confusion.'},
        {'id': 'rm-cmd-remote', 'type': 'command',
         'answer': 'ssh -R 9000:localhost:3000 host',
         'prompt': 'Expose your own local port 3000 as port 9000 on the remote '
                   'machine.',
         'teach': 'Remote listens remotely. This is the direction people get '
                  'backwards.'},
        {'id': 'rm-cmd-dynamic', 'type': 'command', 'answer': 'ssh -D 1080 -N -f bastion',
         'prompt': 'Open a SOCKS proxy on port 1080 routed through a bastion, '
                   'with no shell and in the background.',
         'teach': '-N is no command, -f is background. Together: just the '
                  'tunnel.'},
        {'id': 'rm-cmd-proxychains', 'type': 'command',
         'answer': 'proxychains curl http://internal/',
         'prompt': 'Push an ordinary command through the SOCKS proxy you just '
                   'opened.',
         'teach': "It preloads a library that redirects the program's "
                  'connections, so it works on anything dynamically linked '
                  'and not at all on static binaries.'},
        {'id': 'rm-cmd-rsync-dry', 'type': 'command',
         'answer': 'rsync -av --dry-run src/ host:dest/',
         'prompt': 'Show what an rsync would do, without doing it.',
         'teach': 'Type this by reflex before anything with --delete.'},
        {'id': 'rm-cmd-rsync-contents', 'type': 'command',
         'answer': 'rsync -av src/ dest/',
         'prompt': 'Copy the CONTENTS of src into dest, so dest/a.txt rather '
                   'than dest/src/a.txt.',
         'teach': 'The trailing slash on the source means "the contents of". '
                  'One character, completely different result.'},
        {'id': 'rm-cmd-rsync-into', 'type': 'command',
         'answer': 'rsync -av src dest/',
         'prompt': 'Copy the directory src INTO dest, so you end up with '
                   'dest/src/.',
         'teach': 'A trailing slash on the SOURCE copies its contents '
                  'instead. That one character is the difference between '
                  'dest/src/ and dest/.'},
        {'id': 'rm-cmd-scp', 'type': 'command', 'answer': 'scp file.txt host:',
         'prompt': 'Copy one file to your home directory on a remote host.',
         'teach': 'The bare colon means the remote home directory. Leave the '
                  'colon off and you have quietly made a local copy instead.'},
        {'id': 'rm-cmd-xfreerdp', 'type': 'command',
         'answer': 'xfreerdp /u:user /v:host /dynamic-resolution +clipboard',
         'prompt': 'Open an RDP session that resizes and shares the clipboard, with no password on the command line.',
         'teach': 'A password in /p: is visible in ps output to every user on '
                  'the machine.'},
    ],

    'challenges': [
        {
            'id': 'rm-ssh-config',
            'title': 'Write an ssh config',
            'goal': 'Turn a command nobody can remember into a word, including '
                    'a host reached through a bastion.',
            'setup': {'kind': 'sandbox', 'tree': {'README': 'Write config here.\n'}},
            'solution': {'shell': "printf '%s\\n' 'Host web' "
                                  "'    HostName 203.0.113.10' "
                                  "'    User deploy' '' 'Host db' "
                                  "'    HostName 10.0.0.5' '    User admin' "
                                  "'    ProxyJump web' > config"},
            'steps': [
                {'instruction': 'Create a file called config with a Host block '
                                'named web.',
                 'hint': 'Host web, then indented HostName and User'},
                {'instruction': 'Add a second block named db reached through '
                                'web.', 'hint': 'ProxyJump web'},
            ],
            'free': 'Write an ssh config file called "config" defining a host '
                    '"web" with a HostName and User, and a host "db" that '
                    'reaches it via ProxyJump through web.',
            'verify': {'kind': 'sandbox', 'expect': {
                'exists': ['config'],
                'file_contains': {'config': ['Host web', 'HostName', 'User',
                                             'Host db', 'ProxyJump web']}}},
            'fallback': 'self',
        },
        {
            'id': 'rm-keypair',
            'title': 'Generate a key with the right permissions',
            'goal': 'Make a real ed25519 pair and get the modes ssh insists on. '
                    'Nothing leaves the machine.',
            'setup': {'kind': 'sandbox', 'tree': {'.keep': ''}},
            'solution': {'shell': 'ssh-keygen -q -t ed25519 -N "" -f id_ed25519 '
                                  '&& chmod 600 id_ed25519 '
                                  '&& chmod 644 id_ed25519.pub'},
            'steps': [
                {'instruction': 'Generate an ed25519 key pair called '
                                'id_ed25519 in this directory.',
                 'hint': 'ssh-keygen -t ed25519 -f id_ed25519'},
                {'instruction': 'Set the private key to 600 and the public key '
                                'to 644.',
                 'hint': 'ssh refuses a private key others can read'},
            ],
            'free': 'Generate an ed25519 key pair named id_ed25519 here, with '
                    'the private key mode 600 and the public key 644.',
            'verify': {'kind': 'sandbox', 'expect': {
                'exists': ['id_ed25519', 'id_ed25519.pub'],
                'mode': {'id_ed25519': '600', 'id_ed25519.pub': '644'},
                'file_contains': {'id_ed25519.pub': 'ssh-ed25519'}}},
            'fallback': 'self',
        },
        {
            'id': 'rm-trailing-slash',
            'title': 'The trailing slash, for real',
            'goal': 'Run rsync both ways between two local directories and see '
                    'the difference the slash makes. This is the misconception '
                    'the whole module is built around.',
            'setup': {'kind': 'sandbox', 'tree': {
                'src/': None, 'src/a.txt': 'alpha\n', 'src/b.txt': 'bravo\n',
                'into/': None, 'contents/': None,
            }},
            'solution': {'shell': 'rsync -a src into/ && rsync -a src/ contents/'},
            'steps': [
                {'instruction': 'Copy the src DIRECTORY into into/, so you end '
                                'up with into/src/a.txt.',
                 'hint': 'rsync -a src into/    with no slash on src'},
                {'instruction': 'Copy the CONTENTS of src into contents/, so '
                                'you end up with contents/a.txt.',
                 'hint': 'rsync -a src/ contents/    with the slash'},
            ],
            'free': 'Using rsync twice, produce into/src/a.txt and also '
                    'contents/a.txt, from the same source directory.',
            'verify': {'kind': 'sandbox', 'expect': {
                'exists': ['into/src/a.txt', 'into/src/b.txt',
                           'contents/a.txt', 'contents/b.txt'],
                'missing': ['contents/src', 'into/a.txt']}},
            'fallback': 'self',
        },
        {
            'id': 'rm-certificate',
            'title': 'Build and inspect a certificate',
            'goal': 'Make a self-signed certificate and read it back, entirely '
                    'offline.',
            'setup': {'kind': 'sandbox', 'tree': {'.keep': ''}},
            'solution': {'shell': 'openssl req -x509 -newkey rsa:2048 -nodes '
                                  '-keyout key.pem -out cert.pem -days 30 '
                                  '-subj "/CN=trainer.example" 2>/dev/null '
                                  '&& openssl x509 -in cert.pem -noout -text '
                                  '> details.txt'},
            'steps': [
                {'instruction': 'Generate a self-signed certificate and its key.',
                 'hint': 'openssl req -x509 -newkey rsa:2048 -nodes '
                         '-keyout key.pem -out cert.pem -days 30 '
                         '-subj "/CN=trainer.example"'},
                {'instruction': 'Write a human-readable dump of the certificate '
                                'to details.txt.',
                 'hint': 'openssl x509 -in cert.pem -noout -text > details.txt'},
            ],
            'free': 'Create a self-signed cert.pem with CN=trainer.example and '
                    'write its readable form to details.txt.',
            'verify': {'kind': 'sandbox', 'expect': {
                'exists': ['cert.pem', 'key.pem', 'details.txt'],
                'file_contains': {'cert.pem': 'BEGIN CERTIFICATE',
                                  'details.txt': ['Certificate:',
                                                  'trainer.example']}}},
            'fallback': 'self',
        },
        {
            'id': 'rm-second-machine',
            'title': 'Reach a real machine',
            'goal': 'Everything above was offline. This one needs somewhere to '
                    'connect to, so the trainer cannot check it.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'Start a throwaway container or VM with sshd, '
                                'or use any machine you already have.',
                 'hint': 'a container is the cheap lab'},
                {'instruction': 'Install your public key on it.',
                 'hint': 'ssh-copy-id user@host'},
                {'instruction': 'Add a Host block for it and connect using only '
                                'the alias.', 'hint': 'ssh myhost'},
                {'instruction': 'Open a local forward to something on it and '
                                'reach that through your own port.',
                 'hint': 'ssh -L 8080:localhost:80 myhost'},
            ],
            'free': 'On a real second machine: install your key, reach it by '
                    'ssh config alias alone, and open a working -L forward.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
    ],

    'quiz': [
        {'id': 'nq-slash', 'type': 'mcq',
         'prompt': 'src/ contains a.txt. What does `rsync -a src dest/` produce?',
         'answer': 'dest/src/a.txt',
         'distractors': ['dest/a.txt', 'Both dest/a.txt and dest/src/a.txt',
                         'Nothing; the source needs a trailing slash.'],
         'teach': 'No slash means the directory itself. The slash means "the '
                  'contents of". This is the misconception the module is built '
                  'around.'},

        {'id': 'nq-slash2', 'type': 'mcq',
         'prompt': 'Which one puts a.txt directly into dest?',
         'answer': 'rsync -a src/ dest/',
         'distractors': ['rsync -a src dest/', 'rsync -a src dest',
                         'rsync -a src/ dest'],
         'teach': 'The slash that matters is on the SOURCE. The destination '
                  'slash does almost nothing.'},

        {'id': 'nq-L', 'type': 'mcq',
         'prompt': 'You run `ssh -L 8080:db:5432 bastion`. Where is port 8080 '
                   'listening?',
         'answer': 'On your own machine.',
         'distractors': ['On the bastion.', 'On db.',
                         'On whichever end connects first.'],
         'teach': 'Local listens locally. Use it to reach something you cannot '
                  'reach directly.'},

        {'id': 'nq-R', 'type': 'mcq',
         'prompt': 'You run `ssh -R 9000:localhost:3000 host`. What becomes '
                   'reachable, and where?',
         'answer': 'Your local port 3000, reachable as port 9000 on the remote.',
         'distractors': ['The remote port 3000, reachable locally on 9000.',
                         'Your port 9000, forwarded to the remote 3000.',
                         'Both ends, symmetrically.'],
         'teach': 'Remote listens remotely. This is the direction people get '
                  'backwards.'},

        {'id': 'nq-localhost', 'type': 'mcq',
         'prompt': 'In `ssh -L 8080:localhost:80 host`, which machine does '
                   '"localhost" mean?',
         'answer': 'The remote machine, because the middle part is resolved '
                   'there.',
         'distractors': ['Your machine.', 'Neither; it must be an IP.',
                         'Whichever one has port 80 open.'],
         'teach': 'The single most common port-forwarding confusion. The middle '
                  'host:port is resolved from the far end.'},

        {'id': 'nq-agent', 'type': 'mcq',
         'prompt': 'Why is `ssh -A` to an untrusted host dangerous?',
         'answer': 'Anyone with root there can use your agent to authenticate '
                   'as you elsewhere.',
         'distractors': ['It copies your private key to that host.',
                         'It disables host key checking.',
                         'It stores your passphrase in the remote shell '
                         'history.'],
         'teach': 'It exposes the ability to use the key, not the key itself, '
                  'which is nearly as bad. ProxyJump avoids it entirely.'},

        {'id': 'nq-config-order', 'type': 'mcq',
         'prompt': 'In ~/.ssh/config, a setting appears in both a `Host web` '
                   'block and a `Host *` block. Which wins?',
         'answer': 'Whichever appears first in the file.',
         'distractors': ['The more specific block, wherever it is.',
                         'Whichever appears last.',
                         'Host * always wins, since it is a default.'],
         'teach': 'First match wins, which is why specific hosts go above '
                  '`Host *`. It surprises people who expect later to override.'},

        {'id': 'nq-ping', 'type': 'mcq',
         'prompt': 'ping gets no reply. What have you learned?',
         'answer': 'Almost nothing; ICMP is widely blocked.',
         'distractors': ['The host is down.',
                         'The name did not resolve.',
                         'The port you want is closed.'],
         'teach': 'Most cloud firewalls drop ICMP by default. Work down the '
                  'ladder: resolve, then port, then application.'},

        {'id': 'nq-curl-k', 'type': 'mcq',
         'prompt': 'What does `curl -k` do about a certificate problem?',
         'answer': 'Ignores it. The problem is still there.',
         'distractors': ['Fixes the trust chain for that request.',
                         'Downloads and installs the missing intermediate.',
                         'Falls back to plain HTTP.'],
         'teach': 'Fine for a five-second diagnosis, never in a script.'},

        {'id': 'nq-pem', 'type': 'mcq',
         'prompt': 'A file starts with `-----BEGIN CERTIFICATE-----`. What '
                   'format is it?',
         'answer': 'PEM, whatever the extension says.',
         'distractors': ['DER, since it is a certificate.',
                         'PKCS12, because it has a header.',
                         'It depends on whether it is .crt or .cer.'],
         'teach': '.crt, .cer and .pem are extensions, not formats. Open the '
                  'file and look.'},
    ],
}
