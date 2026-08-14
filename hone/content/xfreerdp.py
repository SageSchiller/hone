"""xfreerdp: the command-line RDP client for reaching Windows.

Same problem as ssh, different operating system. xfreerdp is the CLI RDP client, worth knowing because the graphical ones give you no way to script a connection or record what you did. The shape mirrors ssh: identify yourself, name the host, and add the options that make the session usable, which is the part nobody remembers, so it is drilled here: dynamic resolution, clipboard sharing, drive redirection, and the gateway hop that works like ProxyJump.

RDP needs a Windows host to connect to, and D1 forbids the trainer from reaching one, so the challenge is honestly self-marked. A throwaway Windows VM is the cheap lab.
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
    'adapter': None,
    'estimate': '1 hour',
    'order': 55,
    'lessons': [
        {
            'id': 'rm-rdp',
            'title': 'The Windows side',
            'next': 'rdp-usage',
            'concept': 'Same problem, different operating system. `xfreerdp` is the CLI RDP client, and it is worth knowing because the graphical ones give you no way to script or to record what you did.\n\n**Check the name before anything else.** FreeRDP 3 renamed every binary with a version suffix, so the command is `xfreerdp3` there and plain `xfreerdp` on FreeRDP 2. If `xfreerdp` says command not found on a machine that clearly has FreeRDP, that is why: run `ls /usr/bin/*freerdp*` and use whichever name is there. Everything below is identical either way.\n\nThe shape is the same as ssh: identify yourself, name the host, and add the options that make the session usable. The options are the part nobody remembers, so this is drill material rather than concept material.\n\nThe three worth memorising are dynamic resolution so the session resizes with the window, clipboard sharing, and drive redirection so you can move files without a second tool.',
            'examples': [
                {
                    'label': 'A usable session',
                    'code': 'xfreerdp /u:user /p:pass /v:host\nxfreerdp /u:user /v:host /dynamic-resolution \\\n         +clipboard /drive:share,/home/me/share\n\n/u: user   /p: password   /v: host\n/d: domain          for a domain account',
                    'note': 'Prefer leaving `/p:` off and being prompted, so the password does not land in your shell history.',
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
            'concept': 'xfreerdp has a lot of options and you will use about eight. The connection itself is `/u`, `/p` and `/v` for user, password and the host, with `/d` for a domain account. Leave `/p` off and xfreerdp prompts, which keeps the password out of `ps` and your shell history.\n\nThree options make the session pleasant rather than painful. `/dynamic-resolution` resizes the remote desktop as you resize the window instead of leaving you scrolling. `+clipboard` shares copy and paste both ways. `/drive:share,/local/path` maps a local directory into the session so you can move files without a second tool. These three are the ones to memorise. Note the two shapes: `+x` and `-x` switch a feature on or off, while `/x:value` passes a setting.\n\nThe rest are situational but worth knowing. `/cert:ignore` gets past the self-signed certificate on a lab machine, `/g:gateway` connects through an RD Gateway the way `ProxyJump` hops through a bastion (a jump host you go through to reach machines you cannot reach directly), `/sound` and `/microphone` redirect audio, and `/f` starts fullscreen. A session that resizes, shares a clipboard and a folder is the difference between usable and unusable.',
            'examples': [
                {
                    'label': 'A session worth having',
                    'code': 'xfreerdp /u:user /v:host /dynamic-resolution \\\n         +clipboard /drive:share,/home/me/share\n\n/u: user   /p: password   /v: host\n/d: domain          for a domain account',
                    'note': 'Prefer leaving /p: off so xfreerdp prompts, keeping the password out of ps and history.',
                },
                {
                    'label': 'Getting in to awkward hosts',
                    'code': 'xfreerdp /u:user /v:host /cert:ignore     lab certificate\nxfreerdp /u:user /v:internal /g:gw.example.com  via gateway\nxfreerdp /u:user /v:host /sound /f         audio, fullscreen',
                    'note': '/g is the RD Gateway hop, the RDP equivalent of jumping through a bastion with ssh.',
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
    ],
}
