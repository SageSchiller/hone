"""mimikatz: how Windows credentials leave memory, and how to stop them.

mimikatz is the tool that taught the industry how Windows single sign-on
actually stores credentials, and learning it changes how you think about a
Windows network: **local administrator on a machine means access to the
credentials of everyone who has logged into it.** That one fact reorganises
everything about how a domain is attacked and defended, which is exactly the
boundary rule's test.

**Scope, stated hard because this is the sharpest tool here.** This module
teaches how the credential-theft mechanisms work and how to detect and defend
against them. It does not teach when to use any of it during an engagement, and
the practice is on a lab domain you built and own, never anything else. This is
the same scope line the whole Security group carries, D27's "the tool, never
the engagement", and it matters most here. The module deliberately ends on
detection and defence, because for this author's DFIR work that is the point of
learning the offence at all.

**Verification: none, and the module says so.** mimikatz is a Windows tool, it
is flagged instantly by every endpoint product, and it needs a domain to be
meaningful. There is no honest offline lab a Linux trainer can build for it, so
every challenge is self-marked per D8 and shaped around a Windows AD lab you
stand up yourself, exactly as the SMB and AD module described.
"""

MODULE = {
    'id': 'mimikatz',
    'title': 'mimikatz',
    'group': 'Security',
    'blurb': 'LSASS and credentials, pass-the-hash, Kerberos tickets, DCSync, and the defence.',
    'context': 'You are studying Windows credential theft against a lab domain you own.',
    'needs': [],
    'prereqs': ['smbenum', 'dfirwin'],
    'adapter': None,
    'estimate': '4-5 hours',
    'order': 90,

    'lessons': [
        {
            'id': 'mk-model',
            'title': 'What mimikatz reads, and why it is there to read',
            'next': 'mk-running',
            'concept': (
                'Windows does not ask for your password every time you reach a '
                'file share or a service; that is single sign-on, and it works '
                'because Windows keeps your credential material in memory after '
                'you log in. The process that holds it is LSASS, the Local '
                'Security Authority Subsystem Service, and what it holds is '
                'more than you might hope: your NTLM password hash, your '
                'Kerberos tickets, and on older or misconfigured systems your '
                'password in plaintext.\n\n'
                'mimikatz reads LSASS memory and pulls all of that out. That is '
                'the whole tool in one sentence, and the consequence is the '
                'thing to internalise: **whoever is local administrator on a '
                'machine can read the credentials of everyone who has logged '
                'into it since it booted.** A shared workstation an '
                'administrator once logged into is a place their credentials '
                'are sitting in memory, and mimikatz is how they leave.\n\n'
                'This reframes a Windows domain from a collection of separate '
                'machines into one connected credential surface. An attacker '
                'who is admin on a laptop does not stay stuck on that laptop; '
                'they harvest whatever credentials are cached there and use '
                'them to reach the next machine, and the one after that. The '
                'defence, which the last lesson is about, is entirely shaped by '
                'this: keep privileged credentials off machines where they can '
                'be harvested, and stop LSASS being readable in the first '
                'place.\n\n'
                'Everything after this is the specific mechanisms: what forms '
                'the credential takes, how the hash alone is enough, and how '
                'Kerberos tickets can be forged. Hold the one idea and the rest '
                'is detail.'
            ),
            'examples': [
                {
                    'label': 'Where the credentials live',
                    'code': ('you log in\n'
                             '  -> LSASS caches, in memory:\n'
                             '       NTLM hash of your password\n'
                             '       your Kerberos tickets (TGT, TGS)\n'
                             '       sometimes the plaintext (WDigest)\n'
                             '\n'
                             'local admin -> read LSASS -> all of the above'),
                    'note': 'Single sign-on is why it is cached. mimikatz is '
                            'how it is read.',
                },
            ],
            'misconceptions': [
                'mimikatz does not crack anything. It reads credential material '
                'that Windows is already holding in memory for single sign-on.',
                'The credentials it finds belong to everyone logged in since '
                'boot, not just the current user. A domain admin who logged in '
                'an hour ago left their credentials behind.',
                'This is a domain problem, not a single-machine problem. The '
                'harvested credential is a key to the next machine, which is '
                'why credential hygiene matters more than any one host.',
            ],
            'try_it': [
                'On a lab machine only: log in as one user, then as another, '
                'and note that both sets of credentials are now resident in '
                'the same LSASS until reboot.',
            ],
        },
        {
            'id': 'mk-running',
            'title': 'Running it: privilege, and why it rarely just works',
            'next': 'mk-sekurlsa',
            'concept': (
                'mimikatz speaks in `module::command` pairs, so '
                '`sekurlsa::logonpasswords` runs the logonpasswords command of '
                'the sekurlsa module. You will type dozens of those, and the '
                'first two are always the same setup.\n\n'
                'To read LSASS you need to be local administrator and you need '
                'the debug privilege, which lets a process touch another '
                'process\'s memory. `privilege::debug` enables it, and it '
                'either says OK or tells you that you are not admin. On some '
                'operations you also want `token::elevate` to act as SYSTEM, '
                'the highest local account, which is often required to reach '
                'everything in LSASS. Those two lines open almost every '
                'session.\n\n'
                'The honest part, and the reason this module is calmer than the '
                'reputation suggests: **mimikatz.exe run from disk on a modern '
                'patched Windows machine is caught instantly.** Every endpoint '
                'product has signatured it for a decade. In practice it is run '
                'in memory, from a loader, or its techniques are reimplemented '
                'inside other tools, and even then modern protections may stop '
                'it reading LSASS at all. Learning the commands teaches you the '
                'mechanisms; getting them to run on a defended target is a '
                'separate and often losing battle, which is itself the '
                'defensive lesson.\n\n'
                'For learning, run it on a lab VM with Defender turned off, '
                'from the official gentilkiwi releases. Everything below assumes '
                'that lab, and nothing below assumes anything you do not own.'
            ),
            'examples': [
                {
                    'label': 'The two lines that open a session',
                    'code': ('privilege::debug        enable SeDebugPrivilege\n'
                             '                        (must be local admin)\n'
                             'token::elevate          act as SYSTEM\n'
                             '\n'
                             'then:  sekurlsa::logonpasswords'),
                    'note': 'privilege::debug then token::elevate is the '
                            'standard preamble to reading LSASS.',
                },
            ],
            'misconceptions': [
                'mimikatz needs local admin and the debug privilege. Running it '
                'as an ordinary user gets you nothing from LSASS.',
                'mimikatz.exe from disk is not a working attack on a defended '
                'machine; it is caught on sight. The real use is in memory or '
                'reimplemented, and often blocked anyway.',
                'The `module::command` syntax is not shell. It is mimikatz\'s '
                'own prompt, so these are not commands you type at cmd or '
                'PowerShell.',
            ],
            'try_it': [
                'In a lab, start mimikatz, run `privilege::debug`, and read '
                'whether it reports OK or refuses because you are not admin.',
            ],
        },
        {
            'id': 'mk-sekurlsa',
            'title': 'sekurlsa: pulling credentials out of memory',
            'next': 'mk-pth',
            'concept': (
                'The sekurlsa module reads credential material from LSASS, and '
                'its headline command is `sekurlsa::logonpasswords`, which for '
                'every logged-on session prints the username, the domain, the '
                'NTLM hash, and, where it is present, the plaintext password '
                'and the Kerberos keys. On a machine several people have used, '
                'that is several people\'s credentials in one command.\n\n'
                'The plaintext comes from WDigest, an old authentication '
                'protocol that kept the password in memory in a reversible '
                'form. Modern Windows disables it by default precisely because '
                'mimikatz made the consequence famous, so on a current, '
                'hardened machine `logonpasswords` shows hashes but not '
                'plaintext. Finding plaintext is therefore also a finding about '
                'the machine: WDigest is on, which it should not be.\n\n'
                'The narrower commands target one thing. `sekurlsa::msv` gives '
                'the NTLM hashes specifically. `sekurlsa::wdigest` and '
                '`sekurlsa::kerberos` target those providers. '
                '`sekurlsa::tickets` lists the Kerberos tickets held in memory, '
                'and `sekurlsa::ekeys` gives the Kerberos encryption keys, '
                'which matter for the ticket forging two lessons on. There is '
                'also `sekurlsa::minidump` to run all of this against a saved '
                'LSASS memory dump rather than a live process, which is how the '
                'analysis happens offline: dump LSASS on the target, carry the '
                'dump away, and read it at leisure.'
            ),
            'examples': [
                {
                    'label': 'The one command, and the narrow ones',
                    'code': ('sekurlsa::logonpasswords   everything, per '
                             'session\n'
                             'sekurlsa::msv              just the NTLM hashes\n'
                             'sekurlsa::tickets          Kerberos tickets in '
                             'memory\n'
                             'sekurlsa::ekeys            Kerberos encryption '
                             'keys\n'
                             '\n'
                             'sekurlsa::minidump lsass.dmp   read a saved dump'),
                    'note': 'minidump reads a dumped LSASS offline, which is '
                            'how the harvest and the analysis get separated.',
                },
            ],
            'misconceptions': [
                'Finding plaintext passwords is not guaranteed. On modern '
                'Windows WDigest is off, so you get hashes; plaintext means the '
                'machine is misconfigured.',
                'sekurlsa reads live LSASS by default, but the same commands '
                'work on a saved minidump, which is how the reading is done off '
                'the target machine.',
                'The NTLM hash is not a hashed-and-therefore-safe artefact. As '
                'the next lesson shows, for NTLM authentication the hash is the '
                'credential.',
            ],
            'try_it': [
                'In a lab, log in as two different users, then run '
                '`sekurlsa::logonpasswords` and find both of their NTLM hashes '
                'in the output.',
            ],
        },
        {
            'id': 'mk-pth',
            'title': 'Pass-the-hash: the hash is the credential',
            'next': 'mk-tickets',
            'concept': (
                'Here is the fact that makes the NTLM hash so dangerous: for '
                'NTLM authentication, you never need the plaintext password, '
                'because the protocol proves you know the password by using its '
                'hash. So possessing the hash is exactly as good as possessing '
                'the password. You do not crack it; you use it directly. That '
                'is **pass-the-hash**.\n\n'
                '`sekurlsa::pth` does it: given a username, a domain and an '
                'NTLM hash, it starts a new process whose network '
                'authentication will use that hash, so anything that process '
                'does on the network happens as that user. Point it at a shell '
                'and you have a session as someone whose hash you dumped but '
                'whose password you never knew.\n\n'
                'The Kerberos version is **over-pass-the-hash**, sometimes '
                'called pass-the-key. Instead of using the hash for NTLM, you '
                'use it to request a Kerberos ticket-granting ticket, which '
                'then gets you Kerberos service tickets like any normal logon. '
                'It is stealthier, because the traffic looks like ordinary '
                'Kerberos rather than NTLM, and it sets up the ticket attacks '
                'in the next lesson.\n\n'
                'The reason this works, and the reason it is hard to fix, is '
                'that it is not a bug. It is how NTLM was designed: the hash is '
                'the shared secret. The defences are not a patch but a '
                'strategy, keep high-value hashes off reachable machines, and '
                'the Protected Users group and credential tiering that the '
                'defence lesson covers.'
            ),
            'examples': [
                {
                    'label': 'Using a hash you never cracked',
                    'code': ('sekurlsa::pth /user:Administrator /domain:corp\n'
                             '  /ntlm:aad3b435... /run:cmd.exe\n'
                             '\n'
                             '  -> a cmd whose network auth is that user\'s,\n'
                             '     using only their hash'),
                    'note': 'No plaintext involved. For NTLM, the hash proves '
                            'you know the password, so it is the password.',
                },
            ],
            'misconceptions': [
                'Pass-the-hash does not crack the hash. It uses the hash '
                'directly, because NTLM proves knowledge of the password with '
                'the hash, not the plaintext.',
                'This is not a vulnerability to be patched. It is how NTLM '
                'works, which is why the defence is credential hygiene rather '
                'than an update.',
                'Over-pass-the-hash is not the same as pass-the-hash: the first '
                'gets a Kerberos ticket from the hash and looks like normal '
                'Kerberos, the second uses the hash for NTLM directly.',
            ],
            'try_it': [
                'In a lab, dump a local admin hash on one machine and use '
                '`sekurlsa::pth` to open a session that authenticates to a '
                'second machine as that admin.',
            ],
        },
        {
            'id': 'mk-tickets',
            'title': 'Kerberos tickets: golden and silver',
            'next': 'mk-dcsync',
            'concept': (
                'Kerberos is where credential theft becomes domain persistence, '
                'and the idea rests on one design fact: a Kerberos '
                'ticket-granting ticket is encrypted and signed with the hash '
                'of a single special account, `krbtgt`, which exists on every '
                'domain and whose password almost never changes. If you have '
                'the krbtgt hash, you can forge a TGT for anyone.\n\n'
                'That is a **golden ticket**, `kerberos::golden`. Given the '
                'domain, its security identifier, and the krbtgt hash, mimikatz '
                'mints a TGT claiming to be any user, in any groups, including '
                'Domain Admins, and valid for as long as you like, ten years by '
                'default. Inject it with `kerberos::ptt` and you are that user '
                'across the whole domain, and because you forged it rather than '
                'requested it, the domain controller was never asked and has no '
                'record of the logon. It is the closest thing to a domain '
                'skeleton key, and it is why the krbtgt hash is the crown '
                'jewel.\n\n'
                'A **silver ticket** is narrower and quieter. Instead of the '
                'krbtgt hash it uses the hash of a single service account, and '
                'it forges a service ticket for that one service rather than a '
                'TGT. It reaches only that service, but it never talks to the '
                'domain controller at all, so it is stealthier, and a service '
                'account\'s hash is far easier to obtain than krbtgt\'s.\n\n'
                'The remediation is specific and worth knowing: because a '
                'golden ticket is valid until the krbtgt password changes, and '
                'because Kerberos keeps the two most recent krbtgt passwords, '
                'you must rotate the krbtgt password **twice** to invalidate '
                'existing golden tickets. Rotating it once is not enough, and '
                'that detail catches incident responders out.'
            ),
            'examples': [
                {
                    'label': 'A golden ticket, and injecting it',
                    'code': ('kerberos::golden /user:Administrator\n'
                             '  /domain:corp.local /sid:S-1-5-21-...\n'
                             '  /krbtgt:<ntlm hash> /ptt\n'
                             '\n'
                             '  -> a forged TGT as a Domain Admin, injected,\n'
                             '     never requested from the DC'),
                    'note': 'The krbtgt hash makes it possible; /ptt injects it '
                            'into the current session. The DC was never asked.',
                },
            ],
            'misconceptions': [
                'A golden ticket is forged, not requested, so the domain '
                'controller has no logon record of it. That is what makes it '
                'both powerful and a specific detection problem.',
                'Rotating the krbtgt password once does not kill existing '
                'golden tickets, because the previous password is still '
                'accepted. Rotate it twice.',
                'A silver ticket needs only a service account\'s hash, not '
                'krbtgt, and never contacts the DC, which makes it easier to '
                'get and harder to see.',
            ],
            'try_it': [
                'In a lab, obtain the krbtgt hash (the DCSync lesson is how), '
                'forge a golden ticket for a made-up admin, inject it, and '
                'access a resource as that non-existent user.',
            ],
        },
        {
            'id': 'mk-dcsync',
            'title': 'DCSync and the other credential sources',
            'next': 'mk-defence',
            'concept': (
                'You do not have to touch a domain controller\'s LSASS to get '
                'its secrets. Domain controllers replicate password data to '
                'each other constantly, and `lsadump::dcsync` **impersonates a '
                'domain controller and asks a real one to replicate a '
                'user\'s** credentials. Given the replication right, which '
                'Domain Admins have and which is sometimes delegated too '
                'broadly, you can ask for any user\'s NTLM hash, including '
                'krbtgt, from anywhere on the network, with nothing running on '
                'the DC at all.\n\n'
                'That is the clean way to get the krbtgt hash for a golden '
                'ticket, and it is quiet because replication is normal '
                'traffic, though it has a specific signature the defence lesson '
                'names. `lsadump::dcsync /user:krbtgt` is the request that '
                'unlocks domain persistence, and `/all` pulls everyone.\n\n'
                'The other lsadump commands read credential stores on a machine '
                'you already control. `lsadump::sam` reads the local SAM '
                'database, the local accounts and their hashes. `lsadump::lsa` '
                'reads deeper LSA secrets. `lsadump::secrets` pulls the LSA '
                'secrets that include service account passwords, sometimes in '
                'plaintext, and cached domain credentials. Each is a different '
                'drawer of the same cabinet.\n\n'
                'And DPAPI, the Data Protection API, is the one that reaches '
                'into saved secrets: browser passwords, saved RDP credentials, '
                'and more are encrypted with DPAPI keys that mimikatz can '
                'recover once it has the right material, which is why "the '
                'browser remembered it" is not the safety it sounds like on a '
                'compromised machine.'
            ),
            'examples': [
                {
                    'label': 'DCSync, and the local stores',
                    'code': ('lsadump::dcsync /user:krbtgt\n'
                             '  ask a real DC to replicate krbtgt\'s hash\n'
                             '  (needs replication rights; DC runs nothing)\n'
                             '\n'
                             'lsadump::sam        local account hashes\n'
                             'lsadump::secrets    LSA secrets, service '
                             'passwords'),
                    'note': 'DCSync gets krbtgt from anywhere with the right '
                            'privilege. The sam and secrets commands read a '
                            'machine you already hold.',
                },
            ],
            'misconceptions': [
                'DCSync does not run code on the domain controller. It '
                'impersonates a DC and uses normal replication, which is why it '
                'is quiet and why it only needs the replication right.',
                'The replication right is not only Domain Admins. It is '
                'sometimes delegated to accounts or groups that should not have '
                'it, which is a common real finding.',
                'A password saved by the browser is protected by DPAPI, not by '
                'nothing, but on a machine an attacker controls DPAPI is '
                'recoverable, so saved credentials are exposed.',
            ],
            'try_it': [
                'In a lab, with a Domain Admin context, run `lsadump::dcsync '
                '/user:krbtgt` and confirm you have retrieved the hash without '
                'anything running on the DC.',
            ],
        },
        {
            'id': 'mk-defence',
            'title': 'Reading it backwards: detection and defence',
            'concept': (
                'Every mechanism above has a defence, and for a DFIR reader '
                'this is the reason to have learned the offence. They divide '
                'into stopping the read, removing the target, and seeing the '
                'attempt.\n\n'
                '**Stop the read.** Credential Guard uses virtualisation to '
                'isolate LSASS secrets in a separate protected environment that '
                'ordinary admin cannot reach, which breaks '
                'sekurlsa::logonpasswords outright. Running LSASS as a '
                'protected process (PPL) raises the bar further. And disabling '
                'WDigest, which modern Windows already does, removes the '
                'plaintext. These are the controls that make the famous '
                'commands come back empty.\n\n'
                '**Remove the target.** The strategic defence is credential '
                'hygiene: do not put privileged credentials where they can be '
                'harvested. Administrative tiering keeps domain admin logons '
                'off ordinary workstations. LAPS gives every machine a '
                'different local administrator password, so one dumped local '
                'hash does not unlock the fleet. The Protected Users group '
                'stops its members\' credentials being cached in the vulnerable '
                'ways. None of these stop mimikatz reading a machine; they make '
                'what it reads worthless for reaching anything else.\n\n'
                '**See the attempt.** This ties straight to the Windows and '
                'Sysmon module. Sysmon event 10, process access, flags a '
                'process opening a handle to lsass.exe, which is the signature '
                'of a credential dump. DCSync shows up as directory service '
                'replication, event 4662 with the replication GUIDs, from a '
                'host that is not a domain controller, which is deeply '
                'abnormal. Forged and anomalous tickets leave traces in the '
                '4768 and 4769 Kerberos events. A golden ticket for a user that '
                'does not exist, or with a lifetime of ten years, is visible if '
                'you are looking.\n\n'
                'That is the whole arc closing: you learned how the credentials '
                'leave so you can tell when they are leaving, and arrange your '
                'domain so that when they do, it does not matter.'
            ),
            'examples': [
                {
                    'label': 'The three lines of defence',
                    'code': ('stop the read:   Credential Guard, LSASS PPL,\n'
                             '                 WDigest off\n'
                             'remove target:   tiering, LAPS, Protected Users\n'
                             'see the attempt: Sysmon 10 (handle to lsass),\n'
                             '                 4662 DCSync, 4768/4769 tickets'),
                    'note': 'Credential Guard makes logonpasswords empty; LAPS '
                            'makes a dumped local hash useless elsewhere; '
                            'Sysmon 10 catches the dump.',
                },
            ],
            'misconceptions': [
                'Credential Guard does not stop mimikatz running; it makes '
                'sekurlsa come back with nothing, because the secrets are '
                'isolated where admin cannot reach.',
                'LAPS and tiering do not prevent a credential dump. They make '
                'the dumped credential useless for reaching another machine, '
                'which is the part that matters.',
                'A credential dump is detectable. A process opening a handle to '
                'lsass.exe is Sysmon event 10, and DCSync from a non-DC is '
                'event 4662; both are strong signals if you collect them.',
            ],
            'try_it': [
                'In a lab, enable Credential Guard and run '
                '`sekurlsa::logonpasswords` again to see it return nothing. '
                'Then dump LSASS and find the Sysmon event 10 it generated.',
            ],
        },
    ],

    'drills': [
        {'id': 'mkd-debug', 'type': 'command', 'answer': 'privilege::debug',
         'prompt': 'Enable the debug privilege so mimikatz can read another '
                   'process\'s memory.',
         'teach': 'The first line of almost every session. It needs local '
                  'admin, and either reports OK or refuses.'},
        {'id': 'mkd-elevate', 'type': 'command', 'answer': 'token::elevate',
         'prompt': 'Elevate the token to act as SYSTEM.',
         'teach': 'Often required to reach everything in LSASS. It follows '
                  'privilege::debug.'},
        {'id': 'mkd-logonpasswords', 'type': 'command',
         'answer': 'sekurlsa::logonpasswords',
         'prompt': 'Dump credentials for every logged-on session from LSASS.',
         'teach': 'The headline command: usernames, NTLM hashes, and plaintext '
                  'where WDigest is on.'},
        {'id': 'mkd-msv', 'type': 'command', 'answer': 'sekurlsa::msv',
         'prompt': 'Extract just the NTLM hashes from LSASS.',
         'teach': 'The narrow form when you want hashes specifically rather '
                  'than the whole dump.'},
        {'id': 'mkd-tickets', 'type': 'command', 'answer': 'sekurlsa::tickets',
         'prompt': 'List the Kerberos tickets held in memory.',
         'teach': 'sekurlsa::ekeys gives the encryption keys, which the ticket '
                  'attacks need.'},
        {'id': 'mkd-minidump', 'type': 'command',
         'answer': 'sekurlsa::minidump lsass.dmp',
         'prompt': 'Point sekurlsa at a saved LSASS dump instead of the live '
                   'process.',
         'teach': 'This is how the harvest and the analysis are separated: '
                  'dump on the target, read the dump elsewhere.'},
        {'id': 'mkd-pth', 'type': 'command',
         'answer': 'sekurlsa::pth /user:Administrator /domain:corp '
                   '/ntlm:HASH /run:cmd.exe',
         'prompt': 'Launch a cmd that authenticates on the network as '
                   'Administrator using only their NTLM hash.',
         'teach': 'Pass-the-hash: for NTLM the hash is the credential, so no '
                  'plaintext is needed.'},
        {'id': 'mkd-golden', 'type': 'command',
         'answer': 'kerberos::golden /user:Administrator /domain:corp.local '
                   '/sid:S-1-5-21-X /krbtgt:HASH /ptt',
         'prompt': 'Forge and inject a golden ticket as Administrator using '
                   'the krbtgt hash.',
         'teach': 'Forged, not requested, so the DC has no logon record. /ptt '
                  'injects it into the current session.'},
        {'id': 'mkd-ptt', 'type': 'command',
         'answer': 'kerberos::ptt ticket.kirbi',
         'prompt': 'Inject a saved Kerberos ticket into the current session.',
         'teach': 'ptt is pass-the-ticket: it loads a ticket you forged or '
                  'stole so the session uses it.'},
        {'id': 'mkd-dcsync', 'type': 'command',
         'answer': 'lsadump::dcsync /user:krbtgt',
         'prompt': 'Ask a real domain controller to replicate the krbtgt '
                   'account\'s hash to you.',
         'teach': 'DCSync impersonates a DC. It needs replication rights and '
                  'runs nothing on the DC, which is why it is quiet.'},
        {'id': 'mkd-sam', 'type': 'command', 'answer': 'lsadump::sam',
         'prompt': 'Read the local SAM database of account hashes.',
         'teach': 'Local accounts on the machine you already control. '
                  'lsadump::secrets reads service account passwords.'},
        {'id': 'mkd-secrets', 'type': 'command', 'answer': 'lsadump::secrets',
         'prompt': 'Read the LSA secrets, including service account passwords.',
         'teach': 'Sometimes plaintext, often the key to a service account you '
                  'can then silver-ticket.'},
    ],

    'challenges': [
        {
            'id': 'mkc-lab',
            'title': 'Build the lab this needs',
            'goal': 'None of this is meaningful without a Windows domain you '
                    'own. Stand one up, isolated, before anything else.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'Build a small AD lab on an isolated network: '
                                'a domain controller and a joined workstation, '
                                'the same lab the SMB and AD module described.'},
                {'instruction': 'Create a domain admin and a couple of '
                                'ordinary users, and log the admin into the '
                                'workstation at least once so credentials are '
                                'cached there.'},
                {'instruction': 'On the lab machines only, disable Defender so '
                                'mimikatz will run, and get mimikatz from the '
                                'official gentilkiwi releases.'},
                {'instruction': 'Confirm the network is isolated and cannot '
                                'reach anything real. Everything else in this '
                                'module happens only here.'},
            ],
            'free': 'Build an isolated Windows AD lab with a DC and a '
                    'workstation, a domain admin logged into the workstation, '
                    'and mimikatz available, all on a network that reaches '
                    'nothing real.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
        {
            'id': 'mkc-dump',
            'title': 'Dump credentials from memory',
            'goal': 'The core read: pull the resident credentials out of LSASS '
                    'and understand what forms they take.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'On the workstation, as local admin, open '
                                'mimikatz and run the standard preamble.',
                 'hint': 'privilege::debug then token::elevate'},
                {'instruction': 'Run sekurlsa::logonpasswords and find the '
                                'NTLM hash of every logged-on user, including '
                                'the domain admin.'},
                {'instruction': 'Note whether any plaintext appears. If it '
                                'does, WDigest is on, which is itself a '
                                'finding.'},
                {'instruction': 'Dump LSASS to a file and re-read it offline '
                                'with sekurlsa::minidump, to see how the '
                                'harvest and analysis separate.',
                 'hint': 'sekurlsa::minidump lsass.dmp'},
            ],
            'free': 'On the lab: dump LSASS credentials with '
                    'sekurlsa::logonpasswords, identify the domain admin hash, '
                    'and re-read a saved LSASS dump offline.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
        {
            'id': 'mkc-pth',
            'title': 'Move with a hash you never cracked',
            'goal': 'Prove to yourself that the hash is the credential by using '
                    'one to reach a second machine.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'Dump a local or domain admin NTLM hash on the '
                                'workstation.'},
                {'instruction': 'Use sekurlsa::pth to launch a process that '
                                'authenticates as that user with only the '
                                'hash.',
                 'hint': 'sekurlsa::pth /user:... /domain:... /ntlm:... '
                         '/run:cmd.exe'},
                {'instruction': 'From that process, reach a share or run a '
                                'command on the domain controller, and confirm '
                                'you never used a password.'},
                {'instruction': 'Note that this is not a vulnerability being '
                                'exploited; it is how NTLM was designed to '
                                'work.'},
            ],
            'free': 'On the lab: pass a dumped hash with sekurlsa::pth and use '
                    'the resulting session to authenticate to a second machine '
                    'without ever knowing the password.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
        {
            'id': 'mkc-golden',
            'title': 'Forge domain persistence, then remediate it',
            'goal': 'The full chain: get krbtgt with DCSync, forge a golden '
                    'ticket, and then do the remediation that kills it.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'With a domain admin context, use '
                                'lsadump::dcsync /user:krbtgt to get the '
                                'krbtgt hash without touching the DC directly.'},
                {'instruction': 'Forge a golden ticket for a user that does '
                                'not exist, in Domain Admins, and inject it.',
                 'hint': 'kerberos::golden /user:notreal /domain:... /sid:... '
                         '/krbtgt:... /ptt'},
                {'instruction': 'Access a domain resource as that non-existent '
                                'user, and note that the DC has no logon '
                                'record of it.'},
                {'instruction': 'Now remediate: rotate the krbtgt password '
                                'TWICE, and confirm the golden ticket stops '
                                'working. Rotating once is not enough.'},
            ],
            'free': 'On the lab: DCSync the krbtgt hash, forge and use a golden '
                    'ticket for a non-existent admin, then rotate krbtgt twice '
                    'and confirm the ticket is dead.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
        {
            'id': 'mkc-defend',
            'title': 'Turn the defences on and watch them work',
            'goal': 'The reason to learn all of it: make the famous commands '
                    'come back empty, and catch the attempt.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'Enable Credential Guard on the workstation, '
                                'then run sekurlsa::logonpasswords again and '
                                'see it return nothing.'},
                {'instruction': 'Confirm WDigest is off and, if you have it, '
                                'that LSASS is running as a protected '
                                'process.'},
                {'instruction': 'With Sysmon installed (from the Windows and '
                                'Sysmon module), dump LSASS and find the event '
                                '10 that records a process opening a handle to '
                                'lsass.exe.'},
                {'instruction': 'Run DCSync again and find the event 4662 with '
                                'the replication GUIDs from a non-DC host.'},
                {'instruction': 'Write down which control stopped which '
                                'technique. That table is the point of the '
                                'whole module.'},
            ],
            'free': 'On the lab: enable Credential Guard and see the dump come '
                    'back empty, then detect a dump via Sysmon event 10 and a '
                    'DCSync via event 4662, and map each control to the '
                    'technique it defeats.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
    ],

    'quiz': [
        {'id': 'mkq-what', 'type': 'mcq',
         'prompt': 'What does mimikatz fundamentally do?',
         'answer': 'Reads credential material Windows keeps in LSASS memory '
                   'for single sign-on.',
         'distractors': ['Cracks Windows password hashes offline.',
                         'Exploits a vulnerability in the login screen.',
                         'Brute-forces domain accounts over the network.'],
         'teach': 'It reads what is already there. The credentials are cached '
                  'so you do not retype your password; mimikatz reads the '
                  'cache.'},
        {'id': 'mkq-admin', 'type': 'mcq',
         'prompt': 'What access does reading LSASS with sekurlsa require?',
         'answer': 'Local administrator with the debug privilege.',
         'distractors': ['Any logged-in user.',
                         'Domain admin specifically.',
                         'Physical access to the machine.'],
         'teach': 'privilege::debug then token::elevate, and it needs local '
                  'admin. An ordinary user gets nothing.'},
        {'id': 'mkq-plaintext', 'type': 'mcq',
         'prompt': 'sekurlsa::logonpasswords shows plaintext passwords. What '
                   'does that tell you about the machine?',
         'answer': 'WDigest is enabled, which modern Windows disables by '
                   'default.',
         'distractors': ['The passwords are weak.',
                         'The machine is a domain controller.',
                         'mimikatz cracked them.'],
         'teach': 'Plaintext comes from WDigest. On a hardened machine you get '
                  'hashes, so plaintext is itself a misconfiguration finding.'},
        {'id': 'mkq-pth', 'type': 'mcq',
         'prompt': 'Why is an NTLM hash as good as the password for pass-the-'
                   'hash?',
         'answer': 'NTLM proves knowledge of the password using the hash, so '
                   'the hash is the shared secret.',
         'distractors': ['The hash can be reversed to the password.',
                         'Windows accepts the hash as a typed password.',
                         'The hash is only good for cracking.'],
         'teach': 'This is a design property of NTLM, not a bug, which is why '
                  'the defence is hygiene rather than a patch.'},
        {'id': 'mkq-golden', 'type': 'mcq',
         'prompt': 'What makes a golden ticket possible?',
         'answer': 'Possession of the krbtgt hash, which signs every '
                   'ticket-granting ticket.',
         'distractors': ['Domain admin group membership.',
                         'A vulnerability in Kerberos.',
                         'Access to the domain controller\'s LSASS at ticket '
                         'time.'],
         'teach': 'The krbtgt hash is the crown jewel because every TGT is '
                  'signed with it, so it forges a ticket for anyone.'},
        {'id': 'mkq-golden-record', 'type': 'mcq',
         'prompt': 'Why does the domain controller have no logon record of a '
                   'golden ticket?',
         'answer': 'The ticket is forged locally, not requested from the DC.',
         'distractors': ['mimikatz deletes the logon event.',
                         'Golden tickets bypass logging entirely.',
                         'The DC only logs failed logons.'],
         'teach': 'Forged not requested. That is what makes it powerful and a '
                  'specific detection challenge, addressed by ticket anomaly '
                  'hunting.'},
        {'id': 'mkq-krbtgt-twice', 'type': 'mcq',
         'prompt': 'You found a golden ticket in your domain. How many times '
                   'do you rotate the krbtgt password?',
         'answer': 'Twice, because Kerberos still accepts the previous '
                   'password.',
         'distractors': ['Once is enough.',
                         'Three times, once per key type.',
                         'You cannot rotate krbtgt.'],
         'teach': 'Kerberos keeps the two most recent krbtgt passwords, so a '
                  'single rotation leaves existing golden tickets valid.'},
        {'id': 'mkq-dcsync', 'type': 'mcq',
         'prompt': 'What does DCSync need, and what does it run on the DC?',
         'answer': 'Replication rights, and it runs nothing on the DC; it '
                   'impersonates one.',
         'distractors': ['Admin on the DC, and it runs a service there.',
                         'Physical access to the DC.',
                         'Nothing; anyone can run it.'],
         'teach': 'It uses normal replication, which is why it is quiet and '
                  'why over-broad replication delegation is a real risk.'},
        {'id': 'mkq-credguard', 'type': 'mcq',
         'prompt': 'What does Credential Guard do to sekurlsa::logonpasswords?',
         'answer': 'Makes it return nothing, by isolating LSASS secrets where '
                   'admin cannot reach them.',
         'distractors': ['Blocks mimikatz from starting.',
                         'Deletes the credentials after each logon.',
                         'Encrypts the output.'],
         'teach': 'It does not stop mimikatz running; it makes what it reads '
                  'empty. That is the strongest single control against the '
                  'dump.'},
        {'id': 'mkq-detect', 'type': 'mcq',
         'prompt': 'Which Sysmon event signals a credential dump?',
         'answer': 'Event 10, a process opening a handle to lsass.exe.',
         'distractors': ['Event 1, process creation.',
                         'Event 3, a network connection.',
                         'Event 11, file creation.'],
         'teach': 'Ties straight to the Windows and Sysmon module: a handle to '
                  'lsass is the signature, and DCSync shows as event 4662.'},
    ],
}
