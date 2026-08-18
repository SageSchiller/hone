"""ssh: keys, config, the agent, and forwarding.

The anchor of the network group. ssh is also a whole suite: ssh itself, ssh-keygen, ssh-copy-id and ssh-add, plus the config and known_hosts files that make it short and safe. The arc is deliberate. Keys and permissions first, because everything else assumes them; then the config that turns a command nobody remembers into a word; then the agent and why forwarding it is dangerous; and finally port forwarding, which is the hardest material here and only makes sense once the rest is solid.

The offline parts verify for real: writing a config, generating a key with the modes ssh insists on, building a known_hosts entry, choosing the right -L / -R / -D for a scenario. Anything that needs a second machine is marked self and says so, because D1 forbids the trainer from touching a network. A throwaway container is the cheap lab.
"""

MODULE = {
    'id': 'ssh',
    'title': 'ssh',
    'group': 'Network',
    'blurb': 'Keys and permissions, the config file, the agent, and -L / -R / -D forwarding.',
    'context': 'You are at a shell on your own machine, reaching out to somewhere else.',
    'needs': [
        'ssh',
    ],
    'prereqs': [
        'linux',
    ],
    'adapter': 'sandbox',
    'estimate': '4-5 hours',
    'order': 50,
    'lessons': [
        {
            'id': 'ssh-basics',
            'title': 'Connecting, and the four files ssh reads',
            'concept': (
                'ssh gives you a shell on another machine over an encrypted '
                'connection, and it is the tool the rest of this group leans '
                'on. The command is `ssh user@host`; add `-p PORT` when the '
                'server does not listen on 22, and put a command on the end '
                'to run only that and come straight back instead of opening '
                'a shell.\n\n'
                '**What ssh actually gives you is an encrypted channel**, and '
                'a shell is only the most common thing sent down it. That is '
                'worth knowing on day one, because it explains why one tool '
                'also copies files, forwards ports, mounts filesystems and '
                'runs graphical programs: those are the same connection '
                'carrying a different passenger. scp and rsync are not '
                'separate protocols, they are ssh with something else on '
                'board.\n\n'
                '**Two identities are checked, in opposite directions, and '
                'confusing them causes most ssh bewilderment.** The *server* '
                'proves who it is with its host key, which is what the '
                'fingerprint prompt on a first connection is about. *You* '
                'prove who you are with a password or a key. Separate '
                'mechanisms, separate files, and an error about one reads '
                'very much like an error about the other.\n\n'
                'The first connection asks you to confirm the host key '
                'fingerprint, and after that ssh records it in '
                '`~/.ssh/known_hosts` and warns very loudly indeed if it ever '
                'changes. That warning is doing its job: a changed host key '
                'means the server was rebuilt, or something is sitting in the '
                'middle. The fix is finding out which. `ssh-keygen -R '
                'hostname` is the sanctioned repair: it removes that one '
                'host from `known_hosts` and leaves the rest.\n\n'
                '**`-v` is the first thing to reach for when a login '
                'misbehaves.** It prints what ssh is actually attempting, and '
                'a second or third `-v` prints more. A login that "just '
                'hangs" is nearly always visible in the first twenty lines, '
                'usually as a DNS lookup timing out or an authentication '
                'method being offered and refused.\n\n'
                'Everything else in this module fills in the four files under '
                '`~/.ssh`: a key so you stop typing passwords, a config so '
                'you stop typing long commands, the agent so you type a '
                'passphrase once, and forwarding so a port on one machine '
                'appears on another.'
            ),
            'examples': [
                {
                    'label': 'Connecting',
                    'code': 'ssh user@host\nssh -p 2222 user@host      non-standard port\nssh user@host uptime       run one command and exit\nssh -v user@host           show what it is doing\nssh-keygen -R oldhost      drop one stale host key',
                    'note': 'A command on the end runs without an interactive shell, which is what scripts and cron jobs want. ssh-keygen -R is the sanctioned known_hosts repair after a rebuilt host.',
                },
                {
                    'label': 'The four files that are the whole client',
                    'code': '~/.ssh/config          your aliases and options\n~/.ssh/known_hosts     host keys you have accepted\n~/.ssh/id_ed25519      your private key\n~/.ssh/id_ed25519.pub  the public half you hand out',
                    'note': '`ssh -G host` prints the effective options ssh would use for a host, which is how you check the config without connecting.',
                },
            ],
            'misconceptions': [
                'A password prompt is not an error, it is the fallback: when no key is accepted, ssh quietly asks for a password instead. Add `-v` to see which keys it actually offered.',
                'The warning on a changed host key is not noise. It is the one check that catches a machine in the middle, so read it before deleting the known_hosts line by reflex.',
            ],
            'try_it': [
                'Run `ssh -G github.com` and read the user, port and identity files ssh would use, without opening any connection.',
            ],
            'next': 'rm-keys',
        },
        {
            'id': 'rm-keys',
            'title': 'SSH keys, and why permissions matter',
            'next': 'rm-config',
            'concept': (
                'An SSH key pair is how you prove who you are without sending '
                'a password. That is why the secret never crosses the wire.\n\n'
                'The server sends a challenge. Your client signs '
                'it with the private key. The server checks the signature '
                'against the public key it already has on file. The private '
                'key never crosses the network, which is why this is safe on '
                'a hostile one and why a password is not.\n\n'
                '**The public key lives in `~/.ssh/authorized_keys` on the '
                'server**, one key per line. That file is the whole of "who '
                'may log in as this user": adding a line grants access, '
                'removing it revokes access, and nothing else is consulted. '
                '`ssh-copy-id user@host` appends yours correctly, which is '
                'worth using over a manual copy that mangles the line '
                'endings or loses the trailing newline.\n\n'
                'Generate with `ssh-keygen -t ed25519`. Use ed25519 rather '
                'than RSA unless something old refuses it: the keys are '
                'shorter, faster and at least as strong. Give it a '
                'passphrase; the agent in the next lesson is what stops that '
                'being annoying.\n\n'
                '**A passphrase protects the file, not the connection.** It '
                'encrypts the private key on disk, so someone who steals the '
                'file still cannot use it. It does nothing about a machine '
                'you are already logged into, which is what the agent '
                'discussion in two lessons is really about.\n\n'
                '**ssh refuses to use a private key that others can read**, '
                'and the error is blunt about it: UNPROTECTED PRIVATE KEY '
                'FILE, in capitals, followed by a refusal. `chmod 600` on '
                'the key and `700` on `~/.ssh` is the fix. The check exists '
                'because a world-readable private key is not a secret, and '
                'the same rule applies on the server: a group-writable home '
                'directory there will cause sshd to ignore '
                '`authorized_keys` entirely, silently, and log the reason '
                'somewhere you are not looking.'
            ),
            'examples': [
                {
                    'label': 'Making and installing one',
                    'code': 'ssh-keygen -t ed25519 -C "you@machine"\nssh-copy-id user@host        install the public key\nssh -i key.pem user@host     use one key file, by path\n\nchmod 700 ~/.ssh\nchmod 600 ~/.ssh/id_ed25519\nchmod 644 ~/.ssh/id_ed25519.pub',
                    'note': '`ssh-copy-id` appends to the remote `~/.ssh/authorized_keys` and fixes its permissions for you, which is why it beats doing it by hand.',
                },
                {
                    'label': 'What the server actually checks',
                    'code': 'client signs a challenge with the private key\nserver checks the signature against authorized_keys\n\nthe private key never leaves the client\na stolen .pub file grants nothing',
                    'note': 'That is why permissions on the private file matter and permissions on the .pub file barely do.',
                },
            ],
            'misconceptions': [
                'The `.pub` file is the one you copy. Copying the other one is the mistake this lesson exists to prevent.',
                'A cloud VM hands you a `.pem` file rather than putting a key in `~/.ssh`. `ssh -i key.pem user@host` is how you use it, and it still wants mode 600.',
                '"Permissions 0644 for key are too open" is not a bug. Fix the mode rather than looking for a flag to silence it.',
                'A passphrase does not mean typing it constantly. That is what the agent is for.',
            ],
            'try_it': [
                'Run `ls -l ~/.ssh` and check every private key is 600 and the directory is 700.',
            ],
        },
        {
            'id': 'rm-config',
            'title': 'The config file that makes everything short',
            'next': 'rm-agent',
            'concept': (
                '`~/.ssh/config` is the highest-value file in this module. It '
                'turns a command nobody can remember into a word. The previous '
                'lesson left you typing `-i` and a user and a host every time. '
                'This file is where those stop being flags.\n\n'
                'Each `Host` block names an alias and the settings that apply '
                'to it: the real hostname, the user, the port, which key. After '
                'that, `ssh web` is the whole command, and so is `scp file '
                'web:`, and so is `rsync -a dir web:`, because everything that '
                'speaks ssh reads this file. One alias fixes git-over-ssh at '
                'the same time, which is why a working `ssh web` and a failing '
                '`git pull` is almost always a URL that is not using the '
                'alias.\n\n'
                '`Host` is the name you type. `HostName` is where the packet '
                'goes. Mixing them up is the usual typo, and it looks like the '
                'server is down, because ssh is connecting to a name that is '
                'not on the network. The first matching `Host` wins, not the '
                'last, so put specific names above `Host *`. People who expect '
                'later values to override lose an hour to a catch-all they put '
                'at the top.\n\n'
                '`ProxyJump` is the one that earns its place fastest. A host '
                'reachable only through a bastion becomes one word too, and '
                'ssh sets up the hop itself, rather than you nesting two '
                'commands.\n\n'
                '`ControlMaster auto` reuses one TCP connection for later '
                '`ssh`, `scp` and `rsync` to the same host. `ControlPath` is '
                'the socket those sessions share; include `%r`, `%h` and `%p` '
                'so two users or two ports cannot collide. `ControlPersist '
                '10m` keeps the master up after the first session ends, so '
                'the next command skips the handshake. A leftover socket '
                'from a crash or a changed IP makes the next `ssh` hang on a '
                'dead file. `ssh -O exit alias` closes a healthy master; if '
                'it still hangs, remove the socket under `ControlPath` and '
                'try once more.\n\n'
                'The next lesson is the agent: how keys stay '
                'unlocked, and why `-A` is a trust decision.'
            ),
            'examples': [
                {
                    'label': 'A config worth having',
                    'code': 'Host web\n    HostName 203.0.113.10\n    User deploy\n    IdentityFile ~/.ssh/id_ed25519\n\nHost db\n    HostName 10.0.0.5\n    User admin\n    ProxyJump web\n\nHost *\n    ServerAliveInterval 60',
                    'note': '`ssh db` now hops through web automatically. The `Host *` block sets defaults for everything.',
                },
                {
                    'label': 'Same alias, three tools',
                    'code': 'ssh web\nscp file.txt web:/tmp/\nrsync -a ./site/ web:/var/www/\ngit remote set-url origin git@web:repo.git\n\none Host block, four commands shorter',
                    'note': 'If scp works and git does not, the remote URL is not using the alias. The config is not the bug.',
                },
                {
                    'label': 'One connection, many commands',
                    'code': 'Host *\n    ControlMaster auto\n    ControlPath ~/.ssh/cm-%r@%h:%p\n    ControlPersist 10m\n\nssh -O check web     is the master up\nssh -O exit web      close it cleanly\n# a later ssh that hangs: remove the socket',
                    'note': 'A stale socket from a crash or a changed address is why the next ssh sits there doing nothing. -O exit first; delete the file if that does not clear it.',
                },
            ],
            'misconceptions': [
                'The first matching setting wins, not the last, so put specific hosts above `Host *`. This surprises people who expect the later value to override.',
                'The config is read by scp, sftp, rsync and git over ssh too, so one alias fixes all of them at once.',
                '`ProxyJump` replaces the old `ProxyCommand ssh -W` incantation you will find in older answers.',
            ],
            'try_it': [
                'Add a `Host` block for a machine you use and confirm `ssh alias` works with nothing else typed.',
            ],
        },
        {
            'id': 'rm-agent',
            'title': 'The agent, and why forwarding is dangerous',
            'next': 'rm-forwarding',
            'concept': (
                'The agent holds your decrypted private key in memory so you '
                'type the passphrase once per session rather than once per '
                'connection. `ssh-add` puts a key in; `ssh-add -l` lists '
                'what is loaded.\n\n'
                'A desktop session often already has an agent. `ssh-add -l` '
                'talks to it through `SSH_AUTH_SOCK`, which is a path to a '
                'socket. If that variable is unset, this shell has no '
                'agent. `eval "$(ssh-agent -s)"` starts one and prints the '
                'export lines the shell needs. Starting a second agent by '
                'habit hides the desktop one and loses every key already '
                'loaded.\n\n'
                '`IdentitiesOnly yes` in the config stops the agent from '
                'offering every loaded key to every host. Without it, ssh '
                'walks the agent list first, and a host that allows three '
                'failures will reject a valid key because two other keys '
                'were tried first. `-i` names a file. IdentitiesOnly makes '
                'that file the only offer.\n\n'
                'Agent **forwarding**, `ssh -A`, makes your local agent '
                'reachable from the machine you connect to, so you can hop '
                'onward without copying keys. It is convenient and it is a '
                'real risk: anyone with root on that intermediate machine '
                'can use your agent, for as long as you are connected, to '
                'authenticate as you anywhere your key works.\n\n'
                'The safer answer is almost always `ProxyJump`, which '
                'builds the hop locally and never exposes the agent to the '
                'middle machine at all. Reach for `-A` only on machines you '
                'already trust completely, and prefer to set it per-host '
                'rather than globally.\n\n'
                '`ssh-add -l` saying it cannot connect means `SSH_AUTH_SOCK` '
                'is empty or dead, not that the key files are missing. The '
                'next lesson is forwarding: which end listens, and why '
                '`localhost` in `-L` is the remote.'
            ),
            'examples': [
                {
                    'label': 'Using the agent',
                    'code': 'echo "$SSH_AUTH_SOCK"         path to the agent socket\n                             empty means this shell has no agent\neval "$(ssh-agent -s)"        start one, if none is running\nssh-add ~/.ssh/id_ed25519    load a key\nssh-add -l                    what is loaded\nssh-add -D                    forget everything\nssh-add -t 1h key             expire it after an hour',
                    'note': 'A desktop login often already exported SSH_AUTH_SOCK. Starting a second agent hides that one. `-t` is a good habit on a laptop: the key stops being usable after an hour rather than until reboot.',
                },
                {
                    'label': 'Forwarding, and the better answer',
                    'code': 'ssh -A bastion       forwards your agent (risky)\nssh -J bastion db    ProxyJump instead (safe)\n\nin config:\n  Host db\n      ProxyJump bastion\n      IdentityFile ~/.ssh/id_ed25519\n      IdentitiesOnly yes',
                    'note': 'ProxyJump does the hop from your machine, so the bastion never sees your agent. IdentitiesOnly stops the agent offering every other loaded key first.',
                },
            ],
            'misconceptions': [
                'Agent forwarding does not copy your key. It exposes the ability to use it, which is nearly as bad and lasts as long as the connection.',
                '`ForwardAgent yes` inside `Host *` is a common and bad idea. Scope it to the one host that needs it, or use ProxyJump.',
                'An empty `SSH_AUTH_SOCK` means this shell has no agent, not that the key files are gone. A desktop session often already started one.',
                '`IdentitiesOnly` is not optional once the agent holds several keys. Without it, ssh offers them in order and a server with a low MaxAuthTries rejects the right key after the wrong ones.',
            ],
            'try_it': [
                'Run `ssh-add -l`. If it says the agent has no identities, that is why you are being asked for a passphrase. If it says it cannot connect to your authentication agent, there is no agent running at all: `eval "$(ssh-agent -s)"` starts one.',
            ],
        },
        {
            'id': 'rm-forwarding',
            'title': 'Port forwarding: the climax',
            'concept': 'Port forwarding is how you make a port on one machine appear on another. That is why `-L`, `-R` and `-D` are the way to reach a database you cannot hit directly, or to expose a local service to the far side. Three flags, and the trick is to read them as "which end does the listening".\n\n**`-L` is local**: ssh listens on YOUR machine and forwards to somewhere reachable from the remote. `ssh -L 8080:localhost:80 host` means your `localhost:8080` becomes the remote\'s port 80. Use it to reach something you cannot reach directly.\n\n**`-R` is remote**: ssh listens on the REMOTE machine and forwards back to you. Use it to expose something of yours to the far side.\n\n**`-D` is dynamic**: ssh opens a SOCKS proxy on your machine and sends anything through it out of the remote. That is not one port, it is a general route. Driving an arbitrary program through that proxy is `proxychains`, which the netcat and socat module covers.\n\nThe mnemonic that sticks: Local listens locally, Remote listens remotely, Dynamic listens locally and goes anywhere.\n\n`localhost` in the middle of `-L` is resolved on the remote. That is why `-L 8080:localhost:5432 bastion` reaches the database on the bastion, not on your laptop. Mix that up and you tunnel to yourself and wonder why the app is empty.',
            'examples': [
                {
                    'label': 'The three',
                    'code': 'ssh -L 8080:db.internal:5432 bastion\n   your  localhost:8080  ->  db.internal:5432\n\nssh -R 9000:localhost:3000 host\n   their localhost:9000  ->  your  localhost:3000\n\nssh -D 1080 host\n   a SOCKS proxy on 1080, out via host',
                    'note': 'In `-L A:B:C`, A is the port you open, and B:C is resolved FROM THE REMOTE, which is why `localhost` there means the remote machine.',
                },
                {
                    'label': 'Just the tunnel, no shell',
                    'code': 'ssh -L 8080:db.internal:5432 -N -f bastion\nssh -D 1080 -N -f bastion\n\n-N   run no remote command\n-f   drop into the background once connected',
                    'note': '`-N -f` together are "open the forward and get out of the way", which is what you want for a tunnel you leave running.',
                },
            ],
            'misconceptions': [
                '`localhost` in the middle of `-L` is resolved on the REMOTE machine. This is the single most common port-forwarding confusion.',
                '`-R` on a public interface needs `GatewayPorts` enabled on the remote sshd, and is off by default for good reason.',
                'A forward stays up only as long as the ssh connection does. `-f` backgrounds it but does not make it survive a dropped link, which is what autossh is for.',
            ],
            'try_it': [
                'Run `ssh -L 8080:localhost:22 -N localhost` against your own machine and then `ssh -p 8080 localhost`. It is a tunnel to yourself, and it makes the shape obvious.',
            ],
            'next': None,
        },
    ],
    'drills': [
        {
            'id': 'rm-cmd-ssh',
            'type': 'command',
            'answer': 'ssh user@host',
            'prompt': 'Open a shell on host as user.',
            'teach': 'Add -p PORT when it is not 22. Add a command on the end to run only that.',
        },
        {
            'id': 'rm-cmd-sshv',
            'type': 'command',
            'answer': 'ssh -v user@host',
            'prompt': 'Connect with debug output, to see where a hang is.',
            'teach': '-v is the first thing when a login sits there. -vvv if that is not enough.',
        },
        {
            'id': 'rm-cmd-keygen',
            'type': 'command',
            'answer': 'ssh-keygen -t ed25519',
            'accepts': [
                'ssh-keygen -t ed25519 -C "you@machine"',
            ],
            'prompt': 'Generate a modern SSH key pair.',
            'teach': 'ed25519 rather than RSA: shorter, faster, at least as strong, unless something old refuses it.',
        },
        {
            'id': 'rm-cmd-sshi',
            'type': 'command',
            'answer': 'ssh -i key.pem user@host',
            'prompt': 'Log in as user@host using the private key in key.pem.',
            'teach': 'Cloud VMs hand you a .pem. chmod 600 it first or ssh refuses.',
        },
        {
            'id': 'rm-cmd-cm-check',
            'type': 'command',
            'answer': 'ssh -O check web',
            'prompt': 'Ask whether the ControlMaster socket for alias web is up.',
            'teach': '-O check talks to the master, it does not open a shell.',
        },
        {
            'id': 'rm-cmd-cm-exit',
            'type': 'command',
            'answer': 'ssh -O exit web',
            'prompt': 'Close the ControlMaster for alias web cleanly.',
            'teach': 'If the next ssh still hangs, the socket file is stale: remove it.',
        },
        {
            'id': 'rm-cmd-copyid',
            'type': 'command',
            'answer': 'ssh-copy-id user@host',
            'prompt': 'Install your public key on a remote machine.',
            'teach': 'It appends to the remote authorized_keys and fixes the permissions, which is the step people get wrong doing it by hand.',
        },
        {
            'id': 'sshd-known-hosts-r',
            'type': 'command',
            'answer': 'ssh-keygen -R oldhost.example.com',
            'prompt': 'Remove one host key from known_hosts, the sanctioned way.',
            'teach': 'After a rebuilt VM or a reinstalled container the warning is expected, and this is how you clear that one entry rather than deleting the file or editing it by hand.',
        },
        {
            'id': 'rm-cmd-chmod-key',
            'type': 'command',
            'answer': 'chmod 600 ~/.ssh/id_ed25519',
            'prompt': 'Fix the permissions ssh complains about on a private key.',
            'teach': 'ssh refuses a private key others can read. It prints WARNING: UNPROTECTED PRIVATE KEY FILE, names the mode (Permissions 0644 are too open), skips the key and asks for a password. The fix is the mode, not a new key.',
        },
        {
            'id': 'rm-cmd-agent-add',
            'type': 'command',
            'answer': 'ssh-add -t 1h ~/.ssh/id_ed25519',
            'prompt': 'Load a key into the agent, but only for an hour.',
            'teach': 'A good laptop habit: the key stops being usable after an hour rather than until reboot.',
        },
        {
            'id': 'rm-cmd-agent-l',
            'type': 'command',
            'answer': 'ssh-add -l',
            'prompt': 'List which keys the agent currently holds.',
            'teach': 'If this comes back empty, every key-based login will fail and the reason is the agent, not the server.',
        },
        {
            'id': 'rm-cmd-agent-sock',
            'type': 'command',
            'answer': 'echo "$SSH_AUTH_SOCK"',
            'prompt': 'Print the path to this shell\'s ssh-agent socket.',
            'teach': 'Empty means this shell has no agent, not that the key files are gone.',
        },
        {
            'id': 'rm-cmd-agent-start',
            'type': 'command',
            'answer': 'eval "$(ssh-agent -s)"',
            'prompt': 'Start an agent and export its socket into this shell.',
            'teach': 'Without eval the printed variables never land in this shell. A desktop session often already has one.',
        },
        {
            'id': 'rm-cmd-jump',
            'type': 'command',
            'answer': 'ssh -J bastion db',
            'prompt': 'Reach a machine through a bastion, without exposing your agent to the bastion.',
            'teach': 'The safer answer than ssh -A. The hop is built on your machine, so the middle never sees your agent.',
        },
        {
            'id': 'rm-cmd-local',
            'type': 'command',
            'answer': 'ssh -L 8080:db.internal:5432 bastion',
            'prompt': 'Make db.internal:5432, reachable only from the bastion, appear on your port 8080.',
            'teach': 'Local listens locally. The middle host:port is resolved from the remote, which is the usual confusion.',
        },
        {
            'id': 'rm-cmd-remote',
            'type': 'command',
            'answer': 'ssh -R 9000:localhost:3000 host',
            'prompt': 'Expose your own local port 3000 as port 9000 on the remote machine.',
            'teach': 'Remote listens remotely. This is the direction people get backwards.',
        },
        {
            'id': 'rm-cmd-dynamic',
            'type': 'command',
            'answer': 'ssh -D 1080 -N -f bastion',
            'prompt': 'Open a SOCKS proxy on port 1080 routed through a bastion, with no shell and in the background.',
            'teach': '-N is no command, -f is background. Together: just the tunnel.',
        },
    ],
    'challenges': [
        {
            'id': 'rm-ssh-config',
            'title': 'Write an ssh config',
            'goal': 'Turn a command nobody can remember into a word, including a host reached through a bastion.',
            'setup': {
                'kind': 'sandbox',
                'tree': {
                    'README': 'Write config here.\n',
                },
            },
            'solution': {
                'shell': "printf '%s\\n' 'Host web' '    HostName 203.0.113.10' '    User deploy' '' 'Host db' '    HostName 10.0.0.5' '    User admin' '    ProxyJump web' > config",
            },
            'steps': [
                {
                    'instruction': 'Create a file called config with a Host block named web.',
                    'hint': 'Host web, then indented HostName and User',
                },
                {
                    'instruction': 'Add a second block named db reached through web.',
                    'hint': 'ProxyJump web',
                },
            ],
            'free': 'Write an ssh config file called "config" defining a host "web" with a HostName and User, and a host "db" that reaches it via ProxyJump through web.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'exists': [
                        'config',
                    ],
                    'file_contains': {
                        'config': [
                            'Host web',
                            'HostName',
                            'User',
                            'Host db',
                            'ProxyJump web',
                        ],
                    },
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'rm-ssh-cm',
            'title': 'Reuse one connection',
            'goal': 'ControlMaster is how later ssh, scp and rsync skip the '
                    'handshake. Write the block, including the socket path.',
            'setup': {'kind': 'sandbox', 'tree': {}},
            'solution': {
                'shell': (
                    "printf '%s\\n' "
                    "'Host *' "
                    "'    ControlMaster auto' "
                    "'    ControlPath ~/.ssh/cm-%r@%h:%p' "
                    "'    ControlPersist 10m' "
                    '> config'
                ),
            },
            'steps': [
                {'instruction': 'Write config with Host * turning on '
                                'ControlMaster, a ControlPath that includes '
                                '%r %h %p, and ControlPersist.',
                 'hint': 'ControlMaster auto, ControlPath ~/.ssh/cm-%r@%h:%p'},
            ],
            'free': 'config: Host * with ControlMaster auto and a per-user '
                    'per-host ControlPath.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_contains': {
                        'config': ['ControlMaster auto', 'ControlPath',
                                   '%r', '%h', '%p', 'ControlPersist'],
                    },
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'rm-keypair',
            'title': 'Generate a key with the right permissions',
            'goal': 'Make a real ed25519 pair and get the modes ssh insists on. Nothing leaves the machine.',
            'setup': {
                'kind': 'sandbox',
                'tree': {
                    '.keep': '',
                },
            },
            'solution': {
                'shell': 'ssh-keygen -q -t ed25519 -N "" -f id_ed25519 && chmod 600 id_ed25519 && chmod 644 id_ed25519.pub',
            },
            'steps': [
                {
                    'instruction': 'Generate an ed25519 key pair called id_ed25519 in this directory.',
                    'hint': 'ssh-keygen -t ed25519 -f id_ed25519',
                },
                {
                    'instruction': 'Set the private key to 600 and the public key to 644.',
                    'hint': 'ssh refuses a private key others can read',
                },
            ],
            'free': 'Generate an ed25519 key pair named id_ed25519 here, with the private key mode 600 and the public key 644.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'exists': [
                        'id_ed25519',
                        'id_ed25519.pub',
                    ],
                    'mode': {
                        'id_ed25519': '600',
                        'id_ed25519.pub': '644',
                    },
                    'file_contains': {
                        'id_ed25519.pub': 'ssh-ed25519',
                    },
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'rm-proxyjump',
            'title': 'Write the config that makes a bastion invisible',
            'goal': 'One ssh config with a jump host, key selection and per-host settings, so every later command is short.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {
                    '.ssh': {
                        'dir': True,
                        'mode': '700',
                    },
                },
            },
            'solution': {
                'shell': "cat > .ssh/config <<'EOF'\nHost *\n    ServerAliveInterval 60\n    HashKnownHosts yes\n\nHost bastion\n    HostName bastion.example.com\n    User jump\n    IdentityFile ~/.ssh/id_ed25519\n    IdentitiesOnly yes\n\nHost internal-web\n    HostName 10.0.0.20\n    User deploy\n    ProxyJump bastion\n    IdentityFile ~/.ssh/id_ed25519\n    IdentitiesOnly yes\nEOF\nchmod 600 .ssh/config",
            },
            'steps': [
                {
                    'instruction': 'Write .ssh/config starting with a Host * block carrying settings you want everywhere.',
                    'hint': 'Host *\\n    ServerAliveInterval 60',
                },
                {
                    'instruction': 'Add a bastion host with a HostName, a User and an explicit IdentityFile.',
                },
                {
                    'instruction': 'Add an internal host reached through it with ProxyJump, so a plain ssh internal-web works.',
                    'hint': 'ProxyJump bastion',
                },
                {
                    'instruction': 'Set IdentitiesOnly yes on both, so the agent does not offer every key you own to every host.',
                },
                {
                    'instruction': 'Give the config file mode 600. ssh refuses to use one that is group or world writable.',
                    'hint': 'chmod 600 .ssh/config',
                },
            ],
            'free': 'Produce .ssh/config with a global block, a bastion host, and an internal host reached via ProxyJump, all with explicit identities and mode 600.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_contains': {
                        '.ssh/config': [
                            'Host *',
                            'Host bastion',
                            'ProxyJump bastion',
                            'IdentitiesOnly yes',
                            'HostName',
                        ],
                    },
                    'mode': {
                        '.ssh/config': '600',
                        '.ssh': '700',
                    },
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'rm-known-hosts',
            'title': 'Read a host key and decide about it',
            'goal': 'Fingerprints, known_hosts, and what the warning about a changed key is really telling you.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {
                    '.ssh': {
                        'dir': True,
                        'mode': '700',
                    },
                },
            },
            'solution': {
                'shell': 'ssh-keygen -q -t ed25519 -N "" -f hostkey -C "fake host key" && ssh-keygen -lf hostkey.pub > fingerprint.txt && printf "example.host " > .ssh/known_hosts && cat hostkey.pub >> .ssh/known_hosts && chmod 600 .ssh/known_hosts && ssh-keygen -lf .ssh/known_hosts > known-fp.txt && echo "a changed key means the host or the path changed" > meaning.txt',
            },
            'steps': [
                {
                    'instruction': 'Generate an ed25519 keypair called hostkey, with no passphrase, to stand in for a server host key.',
                    'hint': 'ssh-keygen -q -t ed25519 -N "" -f hostkey',
                },
                {
                    'instruction': 'Print its fingerprint into fingerprint.txt. That is the string you would compare out of band.',
                    'hint': 'ssh-keygen -lf hostkey.pub',
                },
                {
                    'instruction': 'Build a known_hosts entry for the name example.host using that public key, mode 600.',
                },
                {
                    'instruction': 'Print the fingerprints of everything in known_hosts into known-fp.txt.',
                    'hint': 'ssh-keygen -lf .ssh/known_hosts',
                },
                {
                    'instruction': 'Write in meaning.txt what a changed host key warning actually indicates, in one line.',
                },
            ],
            'free': 'Produce hostkey and hostkey.pub, fingerprint.txt, a known_hosts entry for example.host at mode 600, known-fp.txt, and meaning.txt.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'is_file': [
                        'hostkey',
                        'hostkey.pub',
                        'meaning.txt',
                    ],
                    'file_contains': {
                        'fingerprint.txt': 'SHA256:',
                        '.ssh/known_hosts': [
                            'example.host',
                            'ssh-ed25519',
                        ],
                        'known-fp.txt': 'SHA256:',
                    },
                    'mode': {
                        '.ssh/known_hosts': '600',
                    },
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'rm-forward-direction',
            'title': 'Say which forward you need, before typing it',
            'goal': 'Three scenarios, three flags. Getting -L, -R and -D the right way round is the hardest recall in the module.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {
                    'scenarios.txt': '1 A database on the remote network, port 5432, that you want to reach from your own laptop.\n2 A web server on your laptop that a colleague on the remote network needs to reach.\n3 A browser on your laptop that should send all its traffic through the remote network.\n',
                },
            },
            'solution': {
                'shell': "cat > answers.txt <<'EOF'\n1 -L 5432:dbhost:5432 user@bastion\n2 -R 8080:localhost:3000 user@bastion\n3 -D 1080 user@bastion\nEOF\ncat > why.txt <<'EOF'\n-L opens a local port that tunnels out to a remote service\n-R opens a remote port that tunnels back to a local service\n-D opens a local SOCKS proxy with no fixed destination\nEOF",
            },
            'steps': [
                {
                    'instruction': 'Read scenarios.txt. For each one, decide which side the listening port has to be on.',
                },
                {
                    'instruction': 'Write answers.txt with the full ssh flag and arguments for each numbered scenario.',
                    'hint': '1 -L 5432:dbhost:5432 user@bastion',
                },
                {
                    'instruction': 'Write why.txt with one line per flag saying where the listener opens and where the traffic goes.',
                },
                {
                    'instruction': 'The rule that survives: the letter names where the listening port is, Local or Remote, and -D is the one with no fixed destination at all.',
                },
            ],
            'free': 'Produce answers.txt matching each scenario to -L, -R or -D with plausible arguments, and why.txt explaining where each opens its listener.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_contains': {
                        'answers.txt': [
                            '1 -L',
                            '2 -R',
                            '3 -D',
                        ],
                        'why.txt': [
                            '-L',
                            '-R',
                            '-D',
                            'SOCKS',
                        ],
                    },
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'rm-second-machine',
            'title': 'Reach a real machine',
            'goal': 'Everything above was offline. This one needs somewhere to connect to, so the trainer cannot check it.',
            'setup': {
                'kind': 'self',
            },
            'steps': [
                {
                    'instruction': 'Start a throwaway container or VM with sshd, or use any machine you already have.',
                    'hint': 'a container is the cheap lab',
                },
                {
                    'instruction': 'Install your public key on it.',
                    'hint': 'ssh-copy-id user@host',
                },
                {
                    'instruction': 'Add a Host block for it and connect using only the alias.',
                    'hint': 'ssh myhost',
                },
                {
                    'instruction': 'Open a local forward to something on it and reach that through your own port.',
                    'hint': 'ssh -L 8080:localhost:80 myhost',
                },
            ],
            'free': 'On a real second machine: install your key, reach it by ssh config alias alone, and open a working -L forward.',
            'verify': {
                'kind': 'self',
            },
            'fallback': 'self',
        },
    ],
    'quiz': [
        {
            'id': 'sshq-keytype',
            'type': 'mcq',
            'prompt': 'Why prefer ed25519 over RSA for a new SSH key?',
            'answer': 'The keys are shorter and faster and at least as strong, so the only reason to use RSA is software too old to accept ed25519.',
            'distractors': [
                'ed25519 keys do not need a passphrase.',
                'RSA keys cannot be used with an agent.',
                'ed25519 is symmetric and therefore faster to verify.',
            ],
            'teach': 'Generate with `ssh-keygen -t ed25519`. Reach for RSA only when something refuses the modern type.',
        },
        {
            'id': 'sshq-pub',
            'type': 'mcq',
            'prompt': 'Which file do you copy to a server to log in with a key?',
            'answer': 'The .pub file, appended to the remote authorized_keys.',
            'distractors': [
                'The private key, kept at mode 600.',
                'Both halves, so the server can rebuild the pair.',
                'The known_hosts entry for the server.',
            ],
            'teach': 'ssh-copy-id installs the public half and fixes the remote permissions. The private key never leaves your machine.',
        },
        {
            'id': 'sshq-perms',
            'type': 'mcq',
            'prompt': 'ssh says your private key permissions are too open. The fix?',
            'answer': 'chmod 600 the key and 700 the ~/.ssh directory.',
            'distractors': [
                'Pass -o StrictModes=no to silence the check.',
                'Move the key out of ~/.ssh so the check does not apply.',
                'chmod 644 so the key is readable by ssh.',
            ],
            'teach': 'A world-readable private key is not a secret, so ssh refuses it. Fix the mode rather than looking for a flag.',
        },
        {
            'id': 'sshq-config-order',
            'type': 'mcq',
            'prompt': 'In ~/.ssh/config, which value wins when two blocks match a host?',
            'answer': 'The first matching value, so specific hosts go above Host *.',
            'distractors': [
                'The last matching value, as in most config files.',
                'The one in the block with the most settings.',
                'Whichever block comes alphabetically first.',
            ],
            'teach': 'First match wins. Putting Host * at the top quietly overrides everything below it.',
        },
        {
            'id': 'sshq-agent',
            'type': 'mcq',
            'prompt': 'Why prefer ProxyJump over agent forwarding (-A) to reach a host through a bastion?',
            'answer': 'ProxyJump builds the hop on your machine, so the bastion never gets access to your agent.',
            'distractors': [
                'ProxyJump is faster because it skips encryption on the first hop.',
                'Agent forwarding does not work with ed25519 keys.',
                'ProxyJump copies the key to the bastion so later hops are quicker.',
            ],
            'teach': 'With -A, anyone with root on the bastion can use your agent as you for as long as you are connected. ProxyJump avoids that.',
        },
        {
            'id': 'sshq-forward',
            'type': 'mcq',
            'prompt': 'You want a database on the remote network to appear on your own laptop. Which flag?',
            'answer': '-L, because the listening port opens locally.',
            'distractors': [
                '-R, because the database is remote.',
                '-D, because it is a database connection.',
                '-A, to forward the connection through the agent.',
            ],
            'teach': 'Local listens locally. -R is for exposing something of yours to the far side; -D is a general SOCKS route.',
        },
        {
            'id': 'sshq-agent-eval',
            'type': 'mcq',
            'prompt': 'Why is it `eval "$(ssh-agent -s)"` and not just `ssh-agent -s`?',
            'answer': 'ssh-agent prints export lines. eval runs them in this shell so SSH_AUTH_SOCK is set here.',
            'distractors': [
                'eval makes the agent start as root.',
                'ssh-agent -s is fish syntax; eval translates it to bash.',
                'Without eval the agent refuses to hold any keys.',
            ],
            'teach': 'The agent is a separate process. This shell only talks to it if SSH_AUTH_SOCK is in its own environment. A desktop login often already exported one.',
        },
    ],
}
