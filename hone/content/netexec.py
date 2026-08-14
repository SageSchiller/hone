"""netexec: one front-end over SMB, LDAP, WinRM and more.

Formerly crackmapexec, netexec runs the same enumeration across a range of hosts and reports it in a table, with [+] for valid credentials and (Pwn3d!) for local admin. Its value is breadth, plus the safety warning that a wrong-password sweep locks out a domain, so you read the password policy first. This module also folds in Kerberos enumeration (kerbrute userenum, and why it dodges lockout) and the clock-skew gotcha.

Parsing sweep output is sandbox-verified; the live runs need a domain and netexec (a pipx install), so they are self-marked. Scope: the tool, never the engagement.
"""

MODULE = {
    'id': 'netexec',
    'title': 'netexec',
    'group': 'Security',
    'blurb': 'One tool over many protocols, the pass-pol warning, RID brute, and Kerberos enum.',
    'context': 'You are enumerating a Windows domain you have permission to test.',
    'needs': [
        'netexec',
    ],
    'prereqs': [
        'smbenum',
        'ldapsearch',
    ],
    'adapter': 'sandbox',
    'estimate': '2-3 hours',
    'order': 87,
    'lessons': [
        {
            'id': 'sa-netexec',
            'title': 'netexec: one tool over many protocols',
            'concept': 'netexec, which everyone still calls crackmapexec because that was its name until recently, is a single front end over SMB, LDAP, WinRM, MSSQL, SSH and more. Its value is that it does the same thing across a range of hosts and reports it in a table.\n\nThe shape is always `netexec <protocol> <target> <auth> <action>`. The protocol comes first, the target can be a range or a file, authentication is -u and -p or -H for a hash, and the action is a flag like --shares or --users.\n\nThe output convention is worth learning because it is dense. `[+]` means the credentials worked. `(Pwn3d!)` means they worked and the account is a local administrator, which is the difference between access and control. The header line reports the OS, the domain and whether SMB signing is required.\n\nThe actions that matter most: --shares for what is readable, --users and --groups for the directory, --pass-pol for the policy, --sessions for who is logged on, --loggedon-users, and --rid-brute for the RID cycling described earlier.\n\nThe genuine risk to be aware of, and the reason for care rather than an engagement lesson: **running it across a range with a wrong password locks out every account in that range**. Check the lockout policy first, with --pass-pol against one host, before doing anything wide. That is a tool-proficiency fact, not a tactic.',
            'examples': [
                {
                    'label': 'The shape of every netexec command',
                    'code': 'netexec smb 10.0.0.0/24 -u alice -p pass --shares',
                    'note': 'Protocol, target, auth, action. The range is the point of the tool.',
                },
                {
                    'label': 'Check the policy before anything wide',
                    'code': 'netexec smb 10.0.0.10 -u alice -p pass --pass-pol',
                    'note': 'Lockout threshold first, always. One wrong sweep locks out a domain.',
                },
                {
                    'label': 'Just confirm which hosts are alive and signed',
                    'code': 'netexec smb 10.0.0.0/24',
                    'note': 'With no credentials it still reports OS, domain and signing per host.',
                },
                {
                    'label': 'Authenticate with a hash rather than a password',
                    'code': 'netexec smb 10.0.0.10 -u admin -H "aad3b435...:31d6cfe0..."',
                    'note': 'The LM:NT form. Why NTLM hashes are treated as credentials rather than as hashes.',
                },
                {
                    'label': 'Query LDAP through the same tool',
                    'code': 'netexec ldap 10.0.0.10 -u alice -p pass --trusted-for-delegation',
                    'note': 'The LDAP protocol module wraps the queries you would otherwise write by hand.',
                },
            ],
            'misconceptions': [
                'A [+] is not the same as (Pwn3d!). The first means the credentials are valid, the second means local admin.',
                'netexec is not only a credential checker. Most of its value is enumeration across many hosts at once.',
                'crackmapexec and netexec are the same lineage. Old write-ups use the old name and the syntax is largely unchanged.',
            ],
            'try_it': [
                'Run netexec against one lab host with no credentials and read every field of the header line.',
                'Retrieve a password policy and work out how many attempts you would get.',
            ],
            'next': 'sa-kerberos',
        },
        {
            'id': 'sa-kerberos',
            'title': 'Kerberos: names, tickets and two enumeration facts',
            'concept': "Kerberos is the authentication protocol, and for enumeration purposes two properties of it matter more than the protocol detail.\n\n**Username enumeration through pre-authentication.** When a client asks for a ticket for an account that does not exist, the KDC answers differently from when the account exists but the pre-authentication fails. That difference makes it possible to test whether a username is valid without ever attempting a password, which means no failed logon and no lockout counter. `kerbrute userenum` is the tool, and this is why username lists are worth building carefully.\n\n**Accounts that do not require pre-authentication** are the second fact. Where DONT_REQ_PREAUTH is set, the KDC will hand out an AS-REP encrypted with a key derived from the account password, to anybody who asks. That is an offline crackable artefact obtained without credentials, and finding those accounts is a single LDAP filter.\n\nService principal names are the related third thing. Any authenticated user can request a service ticket for any SPN, and that ticket is encrypted with the service account's key, which is again offline crackable. So an SPN list is a list of accounts whose passwords can be attacked without touching the account.\n\nThe enumeration lesson underneath all three is the same: **Kerberos is designed to answer questions from unauthenticated and lightly authenticated parties**, and the answers carry more information than they look like they do.",
            'examples': [
                {
                    'label': 'Which of these usernames exist',
                    'code': 'kerbrute userenum -d corp.local --dc 10.0.0.10 users.txt',
                    'note': 'No password attempted, so no lockout counter moves.',
                },
                {
                    'label': 'Find the accounts that skip pre-auth',
                    'code': '"(&(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=4194304))"',
                    'note': 'Bit 4194304 is DONT_REQ_PREAUTH. One filter, and the answer is a list of offline targets.',
                },
                {
                    'label': 'List service principal names',
                    'code': 'ldapsearch ... "(servicePrincipalName=*)" samAccountName servicePrincipalName',
                    'note': 'Every one of these is an account whose ticket any authenticated user can request.',
                },
                {
                    'label': 'Clock skew, which breaks everything',
                    'code': 'ntpdate -q 10.0.0.10',
                    'note': 'Kerberos rejects requests more than five minutes out. Most mysterious Kerberos failures are this.',
                },
            ],
            'misconceptions': [
                'Username enumeration through Kerberos does not attempt a password, so lockout policies do not stop it.',
                'An SPN is not a vulnerability. It is a name, and the issue is that a ticket for it is crackable offline.',
                'Kerberos failing with an unhelpful error is usually clock skew, not credentials.',
            ],
            'try_it': [
                'Check the time difference between your machine and a lab DC before doing anything Kerberos.',
                'Write the LDAP filter for DONT_REQ_PREAUTH from memory, then check it.',
            ],
            'next': 'sa-lab',
        },
        {
            'id': 'sa-lab',
            'title': 'Building somewhere to practise this',
            'concept': 'This module cannot be practised without a domain, and building one is a legitimate part of learning it. The trainer will not build it for you, and D1 is why: the app creates its own sandbox and nothing else.\n\nThe cheapest real option is a Windows Server evaluation installed in a virtual machine and promoted to a domain controller, with one or two joined clients. The evaluation licence is 180 days and is enough for this. Promotion is a wizard, and the whole build is an afternoon.\n\nThe scripted option is GOAD, Game of Active Directory, which builds a deliberately vulnerable multi-domain forest from configuration. It is large, it wants real resources, and it is the closest thing to a realistic environment that you can rebuild after breaking it.\n\nThe cheap Linux option is Samba configured as an AD domain controller. It speaks LDAP, Kerberos and SMB well enough for nearly every enumeration exercise in this module, runs in a container, and costs nothing. It is not Windows, so some behaviours differ, and it is more than adequate for learning the query languages.\n\nWhatever you build, build it on a network of its own. That is not caution, it is the difference between a lab and an incident: enumeration tools sweep ranges, and a tool pointed at your home network will happily lock out accounts on anything else that answers.',
            'examples': [
                {
                    'label': 'Promote a Windows Server to a DC',
                    'code': 'Install-WindowsFeature AD-Domain-Services -IncludeManagementTools\nInstall-ADDSForest -DomainName corp.local',
                    'note': 'Two commands after the install. The evaluation licence gives you 180 days.',
                },
                {
                    'label': 'Samba as a domain controller',
                    'code': 'samba-tool domain provision --realm=CORP.LOCAL --domain=CORP --server-role=dc',
                    'note': 'Speaks LDAP, Kerberos and SMB. Enough for nearly every exercise here.',
                },
                {
                    'label': 'Populate it so enumeration finds something',
                    'code': 'samba-tool user create alice Passw0rd!\nsamba-tool group addmembers "Domain Admins" alice',
                    'note': 'An empty directory teaches nothing. Make accounts, groups and a share.',
                },
                {
                    'label': 'Keep it off your real network',
                    'code': 'virsh net-define isolated.xml',
                    'note': 'A host-only or isolated network. A sweep that escapes the lab is how a lab becomes an incident.',
                },
            ],
            'misconceptions': [
                'A single domain controller with no users is not a lab. Enumeration of an empty directory teaches nothing.',
                'Samba AD is not identical to Windows AD. It is close enough for the query languages and not for every behaviour.',
                'Running a lab on your normal network is not a small shortcut. Sweeping tools do not know where the lab ends.',
            ],
            'try_it': [
                'Build a Samba AD container, create five users and two groups, and enumerate them with ldapsearch.',
                'Put the lab on an isolated network and confirm from the host that it cannot reach anything else.',
            ],
            'next': None,
        },
    ],
    'drills': [
        {
            'id': 'sad-nxc-shares',
            'type': 'command',
            'prompt': 'Enumerate shares on 10.0.0.10 with netexec as alice.',
            'answer': 'netexec smb 10.0.0.10 -u alice -p pass --shares',
            'teach': 'Reports READ and WRITE per share, which is the answer smbclient -L does not give you.',
        },
        {
            'id': 'sad-nxc-passpol',
            'type': 'command',
            'prompt': 'Read the password policy from 10.0.0.10 with netexec.',
            'answer': 'netexec smb 10.0.0.10 -u alice -p pass --pass-pol',
            'teach': 'Do this before anything wide. One sweep with a wrong password locks out every account it touches.',
        },
        {
            'id': 'sad-nxc-sweep',
            'type': 'command',
            'prompt': 'Identify every SMB host in 10.0.0.0/24 with no credentials.',
            'answer': 'netexec smb 10.0.0.0/24',
            'teach': 'Even unauthenticated it reports OS, domain and whether SMB signing is required.',
        },
        {
            'id': 'sad-nxc-hash',
            'type': 'command',
            'prompt': 'Authenticate to 10.0.0.10 with an NTLM hash instead of a password.',
            'answer': 'netexec smb 10.0.0.10 -u admin -H "aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0"',
            'teach': 'The LM:NT form. This is why an NTLM hash is treated as a credential rather than as a hash.',
        },
        {
            'id': 'sad-nxc-ridbrute',
            'type': 'command',
            'prompt': 'Recover usernames from 10.0.0.10 by cycling RIDs with netexec.',
            'answer': 'netexec smb 10.0.0.10 -u alice -p pass --rid-brute',
            'teach': 'The lookup interface often answers where the enumerate interface is blocked.',
        },
        {
            'id': 'sad-nxc-users',
            'type': 'command',
            'prompt': 'List domain users from 10.0.0.10 with netexec.',
            'answer': 'netexec smb 10.0.0.10 -u alice -p pass --users',
            'teach': 'Same question as enumdomusers, different door. Which door works depends on what is permitted.',
        },
        {
            'id': 'sad-kerbrute',
            'type': 'command',
            'prompt': 'Test which names in users.txt exist in corp.local at 10.0.0.10.',
            'answer': 'kerbrute userenum -d corp.local --dc 10.0.0.10 users.txt',
            'teach': 'No password is attempted, so no lockout counter moves. That is what makes it worth doing first.',
        },
        {
            'id': 'sad-clockskew',
            'type': 'command',
            'prompt': 'Check the clock difference between you and the DC at 10.0.0.10.',
            'answer': 'ntpdate -q 10.0.0.10',
            'teach': 'Kerberos rejects anything more than five minutes out, and most mysterious Kerberos failures are exactly this.',
        },
    ],
    'challenges': [
        {
            'id': 'sac-netexec-parse',
            'title': 'Find the hosts worth going back to',
            'goal': 'Reduce a sweep of real netexec output to the two facts that matter: where you have admin, and where signing is off.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {
                    'sweep.txt': 'SMB 10.0.0.10 445 DC01 [*] Windows Server 2022 (domain:corp.local) (signing:True) (SMBv1:False)\nSMB 10.0.0.10 445 DC01 [+] corp.local\\alice:pass\nSMB 10.0.0.21 445 WS01 [*] Windows 10 (domain:corp.local) (signing:False) (SMBv1:False)\nSMB 10.0.0.21 445 WS01 [+] corp.local\\alice:pass (Pwn3d!)\nSMB 10.0.0.22 445 WS02 [*] Windows 10 (domain:corp.local) (signing:False) (SMBv1:True)\nSMB 10.0.0.22 445 WS02 [-] corp.local\\alice:pass STATUS_LOGON_FAILURE\n',
                },
            },
            'solution': {
                'shell': "grep 'Pwn3d' sweep.txt | awk '{print $2}' > admin-on.txt && grep 'signing:False' sweep.txt | awk '{print $2}' | sort -u > unsigned.txt && grep 'SMBv1:True' sweep.txt | awk '{print $2}' | sort -u > smbv1.txt",
            },
            'steps': [
                {
                    'instruction': 'Find the hosts where the credentials gave local admin, and write their addresses to admin-on.txt.',
                    'hint': "grep 'Pwn3d' sweep.txt | awk '{print $2}'",
                },
                {
                    'instruction': 'List the hosts where SMB signing is not required, into unsigned.txt.',
                },
                {
                    'instruction': 'List the hosts still speaking SMBv1 into smbv1.txt.',
                },
                {
                    'instruction': 'Note the difference between [+] and (Pwn3d!). One is valid credentials, the other is control.',
                },
            ],
            'free': 'Produce admin-on.txt, unsigned.txt and smbv1.txt from the sweep output, each holding just the addresses.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_equals': {
                        'admin-on.txt': '10.0.0.21',
                    },
                    'file_contains': {
                        'unsigned.txt': [
                            '10.0.0.21',
                            '10.0.0.22',
                        ],
                        'smbv1.txt': '10.0.0.22',
                    },
                    'file_lacks': {
                        'unsigned.txt': '10.0.0.10',
                    },
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'sac-lab',
            'title': 'Build a domain and enumerate it',
            'goal': 'There is no way to practise the live half without a domain. Build one, on its own network, and run the real tools against it.',
            'setup': {
                'kind': 'self',
            },
            'steps': [
                {
                    'instruction': 'Stand up a domain controller: a Windows Server evaluation, a Samba AD container, or GOAD. Put it on an isolated network.',
                },
                {
                    'instruction': 'Create at least five users, two groups and a share, so there is something to find.',
                },
                {
                    'instruction': 'Find the DC by SRV record, then scan it and account for every open port.',
                },
                {
                    'instruction': 'Retrieve the password policy before anything else, and write down the lockout threshold.',
                    'hint': 'netexec smb DC -u user -p pass --pass-pol',
                },
                {
                    'instruction': 'Enumerate users three ways: rpcclient, ldapsearch and netexec. Normalise all three into one list and diff them.',
                },
                {
                    'instruction': 'Write the LDAP filter for accounts with an SPN and run it against your own directory.',
                },
            ],
            'free': 'On a lab domain you built, on an isolated network: find the DC by DNS, read the password policy first, enumerate users through three different interfaces, and reconcile the results.',
            'verify': {
                'kind': 'self',
            },
            'fallback': 'self',
        },
    ],
    'quiz': [
        {
            'id': 'saq-kerbenum',
            'type': 'mcq',
            'prompt': 'Why does Kerberos username enumeration not trigger account lockouts?',
            'answer': 'It never attempts a password, so no failed logon is recorded against the account.',
            'distractors': [
                'Kerberos has no lockout mechanism at all.',
                'The KDC only counts failures from domain-joined hosts.',
                'Lockout applies to NTLM authentication only.',
            ],
            'teach': 'The KDC answers differently for a name that does not exist, and that difference is the whole technique.',
        },
        {
            'id': 'saq-pwn3d',
            'type': 'mcq',
            'prompt': 'In netexec output, what does (Pwn3d!) add to a [+]?',
            'answer': 'The credentials are not just valid, they are local administrator on that host.',
            'distractors': [
                'A shell was opened on the host.',
                'The password was cracked rather than supplied.',
                'The host has SMB signing disabled.',
            ],
            'teach': '[+] is access, (Pwn3d!) is control. The distinction is the whole reason the marker exists.',
        },
        {
            'id': 'saq-lockout',
            'type': 'mcq',
            'prompt': 'What is the first thing to check before running netexec across a range with credentials?',
            'answer': 'The account lockout policy, with --pass-pol against one host.',
            'distractors': [
                'Whether SMB signing is required.',
                'The domain functional level.',
                'Whether SMBv1 is enabled anywhere.',
            ],
            'teach': 'A sweep with a wrong password locks out every account it touches. This is tool proficiency, not tactics.',
        },
        {
            'id': 'saq-clock',
            'type': 'mcq',
            'prompt': 'Kerberos operations fail against a DC with an unhelpful error. What do you check first?',
            'answer': 'Clock skew between your machine and the domain controller.',
            'distractors': [
                'Whether the account is disabled.',
                'Whether LDAP signing is enforced.',
                'Whether the DNS SRV records are correct.',
            ],
            'teach': 'More than five minutes out and the KDC refuses. Most mysterious Kerberos failures are exactly this.',
        },
    ],
}
