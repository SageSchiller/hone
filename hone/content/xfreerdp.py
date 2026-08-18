"""xfreerdp: the command-line RDP client for reaching Windows.

Same problem as ssh, different operating system. xfreerdp is the CLI RDP client, worth knowing because the graphical ones give you no way to script a connection or record what you did. The shape mirrors ssh: identify yourself, name the host, and add the options that make the session usable, which is the part nobody remembers, so it is drilled here: dynamic resolution, clipboard sharing, drive redirection, and the gateway hop that works like ProxyJump.

RDP needs a Windows host to connect to, and D1 forbids the trainer from reaching one, so anything that opens a session is honestly self-marked. A throwaway Windows VM is the cheap lab. What does not need a host is assembling the command line from a set of requirements, which is the part nobody remembers, so that is sandbox-verified.
"""

MODULE = {
    'id': 'xfreerdp',
    'title': 'xfreerdp',
    'group': 'Network',
    'blurb': 'Connecting, dynamic resolution, clipboard and drive redirection, and the RD Gateway hop.',
    'context': 'You are at a Linux shell opening a graphical session on a Windows host.',
    'needs': [
        'xfreerdp',
    ],
    'prereqs': [
        'ssh',
    ],
    'adapter': 'sandbox',
    'estimate': '1 hour',
    'order': 55,
    'lessons': [
        {
            'id': 'rdp-what',
            'title': 'What RDP is, and how it differs from ssh',
            'next': 'rm-rdp',
            'concept': (
                'ssh gives you a shell on another machine: text in, text '
                'out. **RDP gives you the screen.** Mouse, windows, the '
                'actual desktop, as though you were sitting at it. That '
                'difference sounds cosmetic and is not, because it changes '
                'what a session *is*.\n\n'
                '**RDP is Microsoft\'s Remote Desktop Protocol**, it listens '
                'on TCP 3389, and it is how Windows machines are '
                'administered remotely almost everywhere. `xfreerdp` is a '
                'client for it that runs on Linux, from FreeRDP, an open '
                'source implementation.\n\n'
                '**A session is a logged-in user, not a connection.** This is '
                'the part that catches ssh users out. In ssh, closing the '
                'terminal ends the shell. In RDP, closing the window '
                'disconnects you and **leaves your session running**, with '
                'your programs open and your work in memory. Reconnect and '
                'you are back where you were. Logging off is a separate act '
                'that actually ends it.\n\n'
                'That is a feature and a trap in equal measure: a '
                'disconnected session keeps holding files, licences and '
                'memory, and on a shared server the disconnected sessions of '
                'people who thought they had left are a genuine operational '
                'problem.\n\n'
                '**Why bother with a command-line client at all**, when '
                'Windows ships a perfectly good graphical one? Because a '
                'command line can be scripted, recorded, put in a runbook, '
                'and given exactly the options you meant. A GUI cannot tell '
                'you six months later what you connected with.'
            ),
            'examples': [
                {
                    'label': 'Two ways to be on another machine',
                    'code': ('ssh      a shell        text, one program\n'
                             '         port 22        closing ends it\n'
                             '\n'
                             'RDP      a desktop      screen, mouse, all of '
                             'it\n'
                             '         port 3389      closing leaves it '
                             'running'),
                    'note': 'The last line is the one to remember. RDP '
                            'disconnect and logoff are different, and only '
                            'one of them frees anything.',
                },
                {
                    'label': 'The smallest useful connection',
                    'code': ('xfreerdp /u:alice /v:10.0.0.20\n'
                             '\n'
                             '/u: the user, /v: the machine.\n'
                             'it will prompt for the password,\n'
                             'which is where you want it prompted.'),
                    'note': 'FreeRDP uses slashes for options rather than '
                            'dashes, which looks wrong to a Unix eye and is '
                            'correct here.',
                },
                {
                    'label': 'Disconnect versus log off',
                    'code': ('close the window     session keeps running,\n'
                             '                     programs still open\n'
                             '\n'
                             'log off inside       session ends,\n'
                             '                     memory released'),
                    'note': 'On a shared server, always log off. On your own '
                            'box, disconnecting on purpose is how you leave '
                            'a long job running and come back to it.',
                },
            ],
            'misconceptions': [
                'RDP is not ssh with pictures. It is a full desktop session '
                'with its own lifetime, which continues after you '
                'disconnect.',
                'Closing the RDP window does not log you out. It disconnects '
                'you, and everything you had open stays open and stays '
                'consuming memory.',
                'xfreerdp is not a Microsoft tool. It is FreeRDP, an '
                'independent implementation, which is why it runs on Linux '
                'at all.',
            ],
            'try_it': [
                'If you have a Windows VM, connect, open something, close the '
                'window, and reconnect. Note that it is exactly as you left '
                'it.',
                'Then log off properly from inside and reconnect. Note that '
                'this time it is not.',
            ],
        },
        {
            'id': 'rm-rdp',
            'title': 'The Windows side',
            'next': 'rdp-usage',
            'concept': (
                'xfreerdp is how you open a Windows desktop from a Linux '
                'shell. That is why it is the client to reach for when a '
                'graphical one cannot be scripted or recorded.\n\n'
                '**Check the name before anything else.** FreeRDP 3 renamed '
                'every binary with a version suffix, so the command is '
                '`xfreerdp3` there and plain `xfreerdp` on FreeRDP 2. If '
                '`xfreerdp` says command not found on a machine that clearly '
                'has FreeRDP, that is why: run `ls /usr/bin/*freerdp*` and use '
                'whichever name is there. Everything below is identical either '
                'way.\n\n'
                'The shape is the same as ssh: identify yourself, name the '
                'host, and add the options that make the session usable. The '
                'options are the part nobody remembers, so this is drill '
                'material rather than concept material. Slash options take a '
                'value (`/u:alice`); plus and minus switch a feature on or '
                'off (`+clipboard`). Mixing the two shapes is how a flag is '
                'silently ignored.\n\n'
                'The three worth memorising are dynamic resolution so the '
                'session resizes with the window, clipboard sharing, and drive '
                'redirection so you can move files without a second tool. The '
                'next lesson is the rest of those flags, including the gateway '
                'hop that works like ProxyJump.'
            ),
            'examples': [
                {
                    'label': 'A usable session',
                    'code': 'xfreerdp /u:user /p:pass /v:host\nxfreerdp /u:user /v:host /dynamic-resolution \\\n         +clipboard /drive:share,/home/me/share\n\n/u: user   /p: password   /v: host\n/d: domain          for a domain account',
                    'note': 'Prefer leaving `/p:` off and being prompted, so the password does not land in your shell history.',
                },
                {
                    'label': 'Which binary is on this box',
                    'code': 'ls /usr/bin/*freerdp*\n  /usr/bin/xfreerdp3     FreeRDP 3\n  /usr/bin/wlfreerdp3    Wayland build\n\nxfreerdp3 /u:alice /v:10.0.0.20',
                    'note': 'The missing command is usually a renamed binary, not a missing package.',
                },
            ],
            'misconceptions': [
                'A password on the command line is visible in `ps` output to every user on the machine, and in your history afterwards.',
                'RDP is not ssh with pictures. It is a full desktop session, so disconnecting and logging off are different things and leave the session in different states.',
            ],
            'try_it': [
                'If you have a Windows host to hand, connect once with `/dynamic-resolution` and once without, and resize the window.',
            ],
        },
        {
            'id': 'rdp-usage',
            'title': 'The flags that make an RDP session usable',
            'concept': (
                'These flags are how you make an RDP session usable. That is '
                'why you reach for `/dynamic-resolution`, `+clipboard` and '
                '`/drive` first.\n\n'
                'xfreerdp has a lot of options and you will use about eight. '
                'The connection itself is `/u`, `/p` and `/v` for user, '
                'password and the host, with `/d` for a domain account. Leave '
                '`/p` off and xfreerdp prompts, which keeps the password out '
                'of `ps` and your shell history.\n\n'
                'Three options make the session pleasant rather than painful. '
                '`/dynamic-resolution` resizes the remote desktop as you resize '
                'the window instead of leaving you scrolling. `+clipboard` '
                'shares copy and paste both ways. `/drive:share,/local/path` '
                'maps a local directory into the session so you can move files '
                'without a second tool. These three are the ones to memorise. '
                'Note the two shapes: `+x` and `-x` switch a feature on or '
                'off, while `/x:value` passes a setting.\n\n'
                'The rest are situational but worth knowing. `/cert:tofu` '
                'trusts the host certificate the first time and remembers it, '
                'which is the check you actually want on a lab you will '
                'return to. `/cert:ignore` skips the check every time, so a '
                'different certificate later is silent. NLA and CredSSP '
                'authenticate before the desktop appears, and they often want '
                '`/d:` even when the account looks local: without a domain '
                'the server treats the user as a machine-local account and '
                'the handshake fails with a generic credential error. '
                '`/dynamic-resolution` is not on every server. When the '
                'session will not resize, `/scale:140` zooms the fixed '
                'desktop and `/size:1920x1080` picks the desktop size '
                'instead. `/g:gateway` connects through an RD Gateway the way '
                '`ProxyJump` hops through a bastion (a jump host you go '
                'through to reach machines you cannot reach directly), '
                '`/sound` and `/microphone` redirect audio, and `/f` starts '
                'fullscreen.'
            ),
            'examples': [
                {
                    'label': 'A session worth having',
                    'code': 'xfreerdp /u:user /v:host /dynamic-resolution \\\n         +clipboard /drive:share,/home/me/share\n\n/u: user   /p: password   /v: host\n/d: domain          for a domain account',
                    'note': 'Prefer leaving /p: off so xfreerdp prompts, keeping the password out of ps and history.',
                },
                {
                    'label': 'Getting in to awkward hosts',
                    'code': 'xfreerdp /u:user /v:host /cert:tofu      trust first cert\nxfreerdp /u:user /v:host /cert:ignore    skip every check\nxfreerdp /u:user /d:CORP /v:host         NLA often wants /d:\nxfreerdp /u:user /v:host /scale:140      zoom a fixed desktop\nxfreerdp /u:user /v:host /size:1920x1080 pick the desktop size\nxfreerdp /u:user /v:internal /g:gw.example.com  via gateway',
                    'note': '/cert:tofu remembers the first certificate. /cert:ignore will not notice if it changes. /g is the RD Gateway hop, the RDP equivalent of jumping through a bastion with ssh.',
                },
            ],
            'misconceptions': [
                'A password in `/p:` is visible in ps output to every user on the machine, and lands in your shell history. Let xfreerdp prompt.',
                'Without `/dynamic-resolution` the session is a fixed size and you scroll. It is the single flag that most changes the experience.',
                '/cert:ignore is for a lab, not for a machine that matters. It skips the check that a real certificate would give you.',
            ],
            'try_it': [
                'If you have a Windows host, connect once with /dynamic-resolution and once without, and resize the window to feel the difference.',
            ],
            'next': None,
        },
    ],
    'drills': [
        {
            'id': 'rm-cmd-xfreerdp',
            'type': 'command',
            'answer': 'xfreerdp /u:user /v:host /dynamic-resolution +clipboard',
            'prompt': 'Open an RDP session that resizes and shares the clipboard, with no password on the command line.',
            'teach': 'A password in /p: is visible in ps output to every user on the machine.',
        },
        {
            'id': 'rdpd-drive',
            'type': 'command',
            'answer': 'xfreerdp /u:user /v:host /drive:share,/home/me/share',
            'prompt': 'Map a local directory into the RDP session.',
            'teach': '/drive:name,path shares a folder both ways, so you move files without scp or a second tool.',
        },
        {
            'id': 'rdpd-gateway',
            'type': 'command',
            'answer': 'xfreerdp /u:user /v:internal /g:gw.example.com',
            'prompt': 'Reach an internal host through an RD Gateway.',
            'teach': '/g is the RDP equivalent of ProxyJump: the gateway hops you to a host you cannot reach directly.',
        },
        {
            'id': 'rdpd-cert',
            'type': 'command',
            'answer': 'xfreerdp /u:user /v:host /cert:ignore',
            'prompt': 'Connect to a lab host with a self-signed certificate.',
            'teach': '/cert:ignore skips the certificate check. Fine for a lab, not for a host that matters.',
        },
    ],
    'challenges': [
        {
            'id': 'rdp-build-cmd',
            'title': 'Build the connection line from a set of requirements',
            'goal': 'Six requirements, one command line. This is the part of xfreerdp nobody remembers, so it is worth assembling deliberately once rather than copying a line whose flags you cannot account for.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {
                    'requirements.txt': (
                        'connect to 10.0.0.20\n'
                        'as the user alice in domain corp\n'
                        'resize the session when the window resizes\n'
                        'share the clipboard both ways\n'
                        'share /home/me/transfer as a drive called work\n'
                        'do not put the password on the command line\n'
                    ),
                },
            },
            'solution': {
                'shell': "printf '%s\\n' 'xfreerdp /v:10.0.0.20 /u:alice /d:corp /dynamic-resolution +clipboard /drive:work,/home/me/transfer' > connect.sh",
            },
            'steps': [
                {
                    'instruction': 'Read requirements.txt. Each line maps to exactly one option, except the last, which maps to leaving one out.',
                },
                {
                    'instruction': 'Start with the host and the identity: /v: for the machine, /u: for the user, /d: for the domain.',
                    'hint': 'xfreerdp /v:10.0.0.20 /u:alice /d:corp',
                },
                {
                    'instruction': 'Add dynamic resolution and clipboard sharing. Note that one is a slash option and one is a plus option.',
                    'hint': '/dynamic-resolution +clipboard',
                },
                {
                    'instruction': 'Add the drive redirection as name,path.',
                    'hint': '/drive:work,/home/me/transfer',
                },
                {
                    'instruction': 'Write the finished line to connect.sh. Leave /p: off entirely: xfreerdp will prompt, and the password stays out of ps and your history.',
                },
            ],
            'free': 'Write connect.sh containing one xfreerdp command line that satisfies every requirement in requirements.txt, including the last one.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_contains': {
                        'connect.sh': [
                            '/v:10.0.0.20',
                            '/u:alice',
                            '/d:corp',
                            '/dynamic-resolution',
                            '+clipboard',
                            '/drive:work,/home/me/transfer',
                        ],
                    },
                    'file_lacks': {'connect.sh': '/p:'},
                },
            },
            'fallback': 'self',
        },

        {
            'id': 'rdp-connect',
            'title': 'Open a usable RDP session',
            'goal': 'RDP needs a Windows host to reach, which the trainer has not got, so this one is yours to run.',
            'setup': {
                'kind': 'self',
            },
            'steps': [
                {
                    'instruction': 'Find or start a Windows host or VM with RDP enabled, and note its address.',
                    'hint': 'a throwaway Windows VM is the cheap lab',
                },
                {
                    'instruction': 'Connect with your user and the host, leaving the password to be prompted.',
                    'hint': 'xfreerdp /u:user /v:host',
                },
                {
                    'instruction': 'Add dynamic resolution, clipboard sharing and a mapped drive, and confirm each works.',
                    'hint': 'xfreerdp /u:user /v:host /dynamic-resolution +clipboard /drive:share,/home/me/share',
                },
                {
                    'instruction': 'Resize the window and copy a file through the mapped drive, so you have used all three.',
                },
            ],
            'free': 'On a real Windows host: connect with a prompted password, then again with dynamic resolution, clipboard and a mapped drive, and use each.',
            'verify': {
                'kind': 'self',
            },
            'fallback': 'self',
        },
        {
            'id': 'rdp-gateway-cmd',
            'title': 'Reach an internal host through a gateway',
            'goal': 'Write the one line that hops through an RD Gateway the way ssh hops through a bastion, without putting a password on the command line.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {
                    'note.txt': (
                        'internal host: files.corp.internal\n'
                        'gateway: gw.corp.example\n'
                        'user: bob\n'
                        'domain: corp\n'
                    ),
                },
            },
            'solution': {
                'shell': "printf '%s\\n' 'xfreerdp /u:bob /d:corp /v:files.corp.internal /g:gw.corp.example' > hop.sh",
            },
            'steps': [
                {
                    'instruction': 'Read note.txt. The host you want is not the host you can reach.',
                },
                {
                    'instruction': 'Put the user, domain and internal host on the line first.',
                    'hint': 'xfreerdp /u:bob /d:corp /v:files.corp.internal',
                },
                {
                    'instruction': 'Add the gateway with /g:. That is the hop. Leave /p: off.',
                    'hint': '/g:gw.corp.example',
                },
                {
                    'instruction': 'Write the finished line to hop.sh.',
                },
            ],
            'free': 'Write hop.sh containing one xfreerdp line that reaches files.corp.internal through gw.corp.example as corp\\bob, with no password on the line.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_contains': {
                        'hop.sh': [
                            '/u:bob',
                            '/d:corp',
                            '/v:files.corp.internal',
                            '/g:gw.corp.example',
                        ],
                    },
                    'file_lacks': {'hop.sh': '/p:'},
                },
            },
            'fallback': 'self',
        },
    ],
    'quiz': [
        {
            'id': 'rdpq-password',
            'type': 'mcq',
            'prompt': 'Why leave /p: off an xfreerdp command?',
            'answer': 'A password on the command line shows in ps to every user and lands in your shell history; omitting it prompts instead.',
            'distractors': [
                '/p: only accepts domain passwords.',
                'The connection is faster without it.',
                'xfreerdp encrypts the password only when prompted.',
            ],
            'teach': 'Prompted secrets stay out of ps and history. It is the same reason you do not put passwords in any command line.',
        },
        {
            'id': 'rdpq-resolution',
            'type': 'mcq',
            'prompt': 'What does /dynamic-resolution change?',
            'answer': 'The remote desktop resizes with the window instead of staying a fixed size you scroll around.',
            'distractors': [
                'It lowers the color depth to speed up the link.',
                'It picks the resolution automatically at login only.',
                'It disables the remote screensaver.',
            ],
            'teach': 'It is the one flag that most changes how usable the session feels.',
        },
        {
            'id': 'rdpq-nature',
            'type': 'mcq',
            'prompt': 'How does an RDP session differ from ssh?',
            'answer': 'It is a full graphical desktop session, so logging off and disconnecting leave it in different states.',
            'distractors': [
                'It runs over the same port and protocol as ssh.',
                'It cannot share files or a clipboard.',
                'It is text only, like ssh with pictures.',
            ],
            'teach': 'Disconnecting leaves your programs running; logging off ends them. The distinction does not exist the same way in ssh.',
        },
        {
            'id': 'rdpq-gateway',
            'type': 'mcq',
            'prompt': 'What does /g:gw.example.com do on an xfreerdp command?',
            'answer': 'It hops through that RD Gateway to reach a host you cannot reach directly, the same job ProxyJump does for ssh.',
            'distractors': [
                'It sets the window title to the gateway name.',
                'It shares a local directory called gw.example.com.',
                'It ignores the gateway certificate the way /cert:ignore does.',
            ],
            'teach': '/g is the RDP equivalent of ssh -J. The host after /v: is still the one you want; the gateway is only the hop.',
        },
    ],
}
