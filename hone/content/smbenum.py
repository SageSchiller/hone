"""smbclient and rpcclient: enumerating a Windows domain over SMB and RPC.

A domain is a database that answers questions, and SMB is the usual way in: smbclient lists and reaches shares (and shows what a null session gets you), while rpcclient rides the same session to the old MS-RPC administrative calls, enumdomusers, getdompwinfo, and the RID-cycling trick that recovers users when enumeration is blocked. The module ends on turning that output into a clean username list.

Reading and reasoning about output are sandbox-verified; the live connections need a domain, which the lab modules describe. Scope: the tool, never the engagement.
"""

MODULE = {
    'id': 'smbenum',
    'title': 'smbclient and rpcclient',
    'group': 'Security',
    'blurb': 'Shares, null sessions, the RPC interfaces, RID cycling, and reading the output.',
    'context': 'You are enumerating a Windows domain you have permission to test.',
    'needs': [
        'smbclient',
        'rpcclient',
    ],
    'prereqs': [
        'ssh',
        'linux',
    ],
    'adapter': 'sandbox',
    'estimate': '3 hours',
    'order': 85,
    'lessons': [
        {
            'id': 'sa-model',
            'title': 'A domain is a database that answers questions',
            'concept': 'Active Directory is an LDAP directory with Kerberos bolted to the front and a great deal of Windows-specific schema inside. Everything in it is an object with attributes: a user has a samAccountName, a memberOf, a servicePrincipalName, a lastLogon, a userAccountControl. A group has members. A computer is a kind of user object.\n\nThe consequence people miss is that **the directory is meant to be readable.** Domain-joined machines and ordinary users constantly need to look up who is in which group, where a service lives, and what the password policy is, so by default an authenticated account can read a very large share of it. Enumeration is mostly not an exploit; it is using a query interface as designed.\n\nThere are four ways in, and they overlap: **SMB** for shares and files, **MS-RPC** over SMB for the old administrative interfaces, **LDAP** for the directory itself, and **Kerberos** for names and tickets. One tool often speaks several: netexec drives SMB and LDAP and WinRM, and rpcclient rides on top of an SMB session.\n\nThe questions worth asking almost always reduce to five: what accounts exist, what groups do they belong to, what machines are there, what is shared and readable, and what is the policy that governs all of it.',
            'examples': [
                {
                    'label': 'The same question, four doors',
                    'code': 'rpcclient -U "" -N -c enumdomusers 10.0.0.10\nldapsearch -x -H ldap://10.0.0.10 -b "DC=corp,DC=local" "(objectClass=user)" samAccountName\nnetexec smb 10.0.0.10 -u user -p pass --users',
                    'note': 'Three tools, one question: what accounts exist. Which one works depends on what is permitted.',
                },
                {
                    'label': 'Find the domain controller first',
                    'code': 'dig +short -t SRV _ldap._tcp.dc._msdcs.corp.local',
                    'note': 'Domain controllers advertise themselves in DNS. This is the cheapest first question there is.',
                },
                {
                    'label': 'Confirm what is even listening',
                    'code': 'nmap -sT -p 88,135,139,389,445,636,3268,5985 10.0.0.10',
                    'note': '88 Kerberos, 389 LDAP, 445 SMB, 3268 global catalog, 5985 WinRM. The port set identifies a DC.',
                },
            ],
            'misconceptions': [
                'Enumeration is not usually an exploit. Most of it is a query interface working exactly as designed.',
                'LDAP and SMB are not alternatives. They answer different questions and are commonly used together.',
                'A domain controller is not identified by one port. The combination of 88, 389 and 445 is the signature.',
            ],
            'try_it': [
                'On a lab domain, look up the DC by SRV record rather than by guessing its address.',
                'Scan a domain controller and name what each open port is for.',
            ],
            'next': 'sa-smb',
        },
        {
            'id': 'sa-smb',
            'title': 'SMB: shares, sessions and what anonymous gets you',
            'concept': "SMB is file sharing, and it is also the transport for a surprising amount of Windows administration. Port 445 is the modern one; 139 is NetBIOS-era SMB and its presence usually means something old.\n\nA **null session** is an anonymous connection with an empty username and password. On Windows 2000 it exposed almost everything, which is why every write-up mentions it, and on anything modern it is heavily restricted by default. It is still worth trying, because it costs one command and occasionally an old file server answers.\n\nThe shares themselves are the point. `IPC$` is the interprocess channel that RPC rides on and is not a file share. `ADMIN$` and `C$` are administrative shares that need administrative rights. Anything else is somebody's idea, and the interesting ones are the ones nobody remembers creating.\n\nTwo distinctions matter and get confused. **Share permissions and NTFS permissions are separate**, and the effective access is the more restrictive of the two, so a share you can list is not necessarily a share you can read. And **listing a share is not reading it**: the listing may be permitted while every file inside is denied.\n\nSMB signing is the other thing to record while you are there. Where it is not required, relay attacks become possible, and every enumeration tool reports it because it is a one-bit fact with large consequences.",
            'examples': [
                {
                    'label': 'What shares are there, anonymously',
                    'code': 'smbclient -L //10.0.0.10 -N',
                    'note': '-N is no password. The classic first command, and often refused on modern targets.',
                },
                {
                    'label': 'With credentials',
                    'code': 'smbclient -L //10.0.0.10 -U "corp\\\\alice"',
                    'note': 'Domain and user. The backslash needs escaping in a shell.',
                },
                {
                    'label': 'Connect to one share and look around',
                    'code': 'smbclient //10.0.0.10/Public -U alice',
                    'note': 'An ftp-like prompt: ls, cd, get, mget, recurse ON.',
                },
                {
                    'label': 'Enumerate shares and signing at once',
                    'code': 'netexec smb 10.0.0.10 -u alice -p pass --shares',
                    'note': 'Reports each share with READ and WRITE, which is the answer smbclient -L does not give you.',
                },
                {
                    'label': 'Mount it like a filesystem',
                    'code': 'sudo mount -t cifs //10.0.0.10/Public /mnt/x -o username=alice',
                    'note': 'Better than the interactive client when you want to grep through what is there.',
                },
            ],
            'misconceptions': [
                'Being able to list a share does not mean being able to read it. Share and NTFS permissions are separate and both apply.',
                'IPC$ is not a file share. It is the named pipe channel that RPC uses, which is why it appears everywhere.',
                'A null session failing does not mean the host is hardened. It means the modern default is in place.',
            ],
            'try_it': [
                'List shares on a lab host anonymously and then with credentials, and compare.',
                'Find a share you can list but not read, and note what the error actually says.',
            ],
            'next': 'sa-rpc',
        },
        {
            'id': 'sa-rpc',
            'title': 'RPC: the old interfaces that still answer',
            'concept': "`rpcclient` connects to the MS-RPC interfaces over SMB and gives you a command prompt onto the domain's own administrative calls. It is old, it is unglamorous, and it still answers questions nothing else answers as directly.\n\nThe commands worth knowing are few. `enumdomusers` lists accounts with their RIDs. `enumdomgroups` lists groups. `queryuser <rid>` gives detail on one account including logon times and flags. `querygroupmem` lists a group's members. `getdompwinfo` returns the password policy, which is genuinely important before any guessing: minimum length and lockout threshold decide whether an approach is viable at all. `srvinfo` gives the OS version. `netshareenumall` lists shares including hidden ones.\n\n**RID cycling** is the technique to understand rather than memorise. Every security principal has a relative identifier appended to the domain SID, and they are allocated sequentially from 1000 upward. Well-known ones are fixed: 500 is the built-in Administrator whatever it has been renamed to, 501 is Guest, 512 is Domain Admins. So even where enumdomusers is blocked, walking RIDs with `lookupsids` sometimes recovers the whole list, because the lookup call is permitted when the enumeration call is not.\n\nThat gap between two calls that expose the same information is the general lesson: hardening is applied per interface, and the interfaces are not consistent.",
            'examples': [
                {
                    'label': 'Try it anonymously',
                    'code': 'rpcclient -U "" -N 10.0.0.10',
                    'note': 'Drops to a prompt. Then type the commands rather than passing them.',
                },
                {
                    'label': 'One command, non-interactively',
                    'code': 'rpcclient -U "" -N -c "enumdomusers" 10.0.0.10',
                    'note': '-c is what makes rpcclient scriptable.',
                },
                {
                    'label': 'The policy question, before any guessing',
                    'code': 'rpcclient -U alice%pass -c "getdompwinfo" 10.0.0.10',
                    'note': 'Minimum length and lockout threshold. This decides whether spraying is even sensible.',
                },
                {
                    'label': 'Walk the RIDs when enumeration is blocked',
                    'code': 'for i in $(seq 500 1100); do rpcclient -U "" -N -c "lookupsids S-1-5-21-1-2-3-$i" 10.0.0.10; done',
                    'note': 'The lookup call is often permitted where the enumerate call is not.',
                },
                {
                    'label': 'Shares including hidden ones',
                    'code': 'rpcclient -U alice%pass -c "netshareenumall" 10.0.0.10',
                    'note': 'Sees more than smbclient -L on some configurations.',
                },
            ],
            'misconceptions': [
                'rpcclient is not a shell on the host. It is a client for specific remote procedure calls.',
                'RID 500 is the built-in administrator even after a rename, so renaming it is not a defence against identification.',
                'enumdomusers failing does not mean user enumeration is blocked. Another interface may still answer.',
            ],
            'try_it': [
                'Retrieve the password policy from a lab domain and write down the lockout threshold.',
                'Compare what enumdomusers gives you against what lookupsids RID cycling gives you.',
            ],
            'next': 'sa-reading',
        },
        {
            'id': 'sa-reading',
            'title': 'Turning output into something you can think with',
            'concept': 'The tools produce a great deal of text and the work is mostly in reducing it. This is the part that is entirely transferable, entirely offline, and almost never taught.\n\nThree shapes come up constantly. **A list of accounts** that needs to become a clean username file, with the RIDs and the decorations stripped, so it can feed the next tool. **A table of hosts and facts**, where you want to sort by one column, say every host without SMB signing. **A set of group memberships**, where the question is who is in a privileged group, transitively.\n\nThe tools for this are the ones already in the roster: grep to select, cut and awk to reshape, sort and uniq to aggregate, and jq when the tool can emit JSON. That is why this module lists bash and the text-processing modules as the real prerequisites rather than any security tool.\n\nThe habit worth building is to normalise early. Get every source into one username-per-line file, lowercase, sorted and unique, before doing anything with it. Half the frustration in this work is three tools disagreeing about whether a name has a domain prefix.\n\nAnd keep the raw output. The parsed version is what you think with; the raw version is what you go back to when the parsed version turns out to have dropped something.',
            'examples': [
                {
                    'label': 'rpcclient output into a username list',
                    'code': "grep -oP 'user:\\[\\K[^]]+' users.raw | sort -u > users.txt",
                    'note': 'enumdomusers prints user:[name] rid:[0x...]. Only the name is wanted downstream.',
                },
                {
                    'label': 'ldapsearch output into the same shape',
                    'code': "grep -i '^samaccountname:' ldap.raw | awk '{print tolower($2)}' | sort -u > users.txt",
                    'note': 'LDIF is colon separated. Normalise the case while you are there.',
                },
                {
                    'label': 'Hosts without SMB signing',
                    'code': "grep -i 'signing:False' netexec.raw | awk '{print $2}' > unsigned.txt",
                    'note': 'One fact per host, extracted into a list the next step can consume.',
                },
                {
                    'label': 'Compare two enumeration sources',
                    'code': 'comm -3 users-rpc.txt users-ldap.txt',
                    'note': 'What one source saw and the other did not is frequently the interesting part.',
                },
            ],
            'misconceptions': [
                'Parsing is not the boring part. It is where two sources disagreeing reveals something neither said alone.',
                'A username list with domain prefixes on some entries will silently fail against half the tools.',
                'Keeping only the parsed output means losing the field you did not know you needed.',
            ],
            'try_it': [
                'Take any tool output you have and reduce it to one clean value per line.',
                'Diff two username lists from different sources and account for every difference.',
            ],
            'next': None,
        },
    ],
    'drills': [
        {
            'id': 'sad-dns-srv',
            'type': 'command',
            'prompt': 'Find the domain controllers for corp.local via DNS.',
            'answer': 'dig +short -t SRV _ldap._tcp.dc._msdcs.corp.local',
            'teach': 'Domain controllers advertise themselves. The cheapest first question in the whole module.',
        },
        {
            'id': 'sad-dcports',
            'type': 'command',
            'prompt': 'Scan 10.0.0.10 for the ports that identify a domain controller.',
            'answer': 'nmap -sT -p 88,135,139,389,445,636,3268,5985 10.0.0.10',
            'teach': '88 Kerberos, 389 LDAP, 445 SMB, 3268 global catalog. The combination is the signature.',
        },
        {
            'id': 'sad-smb-list',
            'type': 'command',
            'prompt': 'List the shares on 10.0.0.10 with no credentials.',
            'answer': 'smbclient -L //10.0.0.10 -N',
            'teach': '-N means no password. The classic first command, and usually refused on anything modern.',
        },
        {
            'id': 'sad-smb-list-auth',
            'type': 'command',
            'prompt': 'List the shares on 10.0.0.10 as the user alice.',
            'answer': 'smbclient -L //10.0.0.10 -U alice',
            'teach': 'Listing shares is not reading them: share and NTFS permissions are separate and both apply.',
        },
        {
            'id': 'sad-smb-connect',
            'type': 'command',
            'prompt': 'Connect to the Public share on 10.0.0.10 as alice.',
            'answer': 'smbclient //10.0.0.10/Public -U alice',
            'teach': 'Drops to an ftp-like prompt: ls, cd, get, mget, and recurse ON for whole directories.',
        },
        {
            'id': 'sad-smb-mount',
            'type': 'command',
            'prompt': 'Mount the Public share on 10.0.0.10 at /mnt/x as alice.',
            'answer': 'sudo mount -t cifs //10.0.0.10/Public /mnt/x -o username=alice',
            'teach': 'Better than the interactive client when you want to grep through what is there.',
        },
        {
            'id': 'sad-smb-get',
            'type': 'command',
            'prompt': 'Inside smbclient, download every file in the current directory without prompting.',
            'answer': 'prompt OFF; mget *',
            'teach': 'prompt OFF stops it asking per file, and recurse ON pulls subdirectories too.',
        },
        {
            'id': 'sad-rpc-connect',
            'type': 'command',
            'prompt': 'Open an anonymous rpcclient session to 10.0.0.10.',
            'answer': 'rpcclient -U "" -N 10.0.0.10',
            'teach': 'A null session. Costs one command, and occasionally an old file server still answers.',
        },
        {
            'id': 'sad-rpc-users',
            'type': 'command',
            'prompt': 'List domain users from 10.0.0.10 in one rpcclient command.',
            'answer': 'rpcclient -U "" -N -c "enumdomusers" 10.0.0.10',
            'teach': '-c is what makes rpcclient scriptable rather than interactive.',
        },
        {
            'id': 'sad-rpc-groups',
            'type': 'command',
            'prompt': 'List domain groups from 10.0.0.10 as alice.',
            'answer': 'rpcclient -U alice -c "enumdomgroups" 10.0.0.10',
            'teach': 'Groups and their RIDs. querygroupmem takes the RID from here.',
        },
        {
            'id': 'sad-rpc-pwpol',
            'type': 'command',
            'prompt': 'Retrieve the domain password policy from 10.0.0.10 as alice.',
            'answer': 'rpcclient -U alice -c "getdompwinfo" 10.0.0.10',
            'teach': 'Minimum length and lockout threshold. Ask this before any guessing, every time.',
        },
        {
            'id': 'sad-rpc-srvinfo',
            'type': 'command',
            'prompt': 'Get the OS version of 10.0.0.10 through rpcclient as alice.',
            'answer': 'rpcclient -U alice -c "srvinfo" 10.0.0.10',
            'teach': 'Version and server type, which tells you which era of defaults you are dealing with.',
        },
        {
            'id': 'sad-rpc-shares',
            'type': 'command',
            'prompt': 'List all shares including hidden ones via rpcclient as alice.',
            'answer': 'rpcclient -U alice -c "netshareenumall" 10.0.0.10',
            'teach': 'Sees more than smbclient -L on some configurations, which is the general lesson about per-interface hardening.',
        },
        {
            'id': 'sad-parse-rpc',
            'type': 'command',
            'prompt': 'Extract just the usernames from rpcclient output in users.raw.',
            'answer': "grep -oP 'user:\\[\\K[^]]+' users.raw | sort -u",
            'teach': 'enumdomusers prints user:[name] rid:[0x...]. Downstream tools want only the name.',
        },
    ],
    'challenges': [
        {
            'id': 'sac-parse-users',
            'title': 'Turn two enumerations into one clean list',
            'goal': 'Real output from two different tools, in two different shapes. Normalise both into one username list and find what only one source saw.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {
                    'rpc.raw': 'user:[Administrator] rid:[0x1f4]\nuser:[Guest] rid:[0x1f5]\nuser:[alice] rid:[0x452]\nuser:[bob] rid:[0x453]\nuser:[svc_sql] rid:[0x454]\n',
                    'ldap.raw': 'dn: CN=Alice,CN=Users,DC=corp,DC=local\nsAMAccountName: alice\n\ndn: CN=Bob,CN=Users,DC=corp,DC=local\nsAMAccountName: bob\n\ndn: CN=Carol,CN=Users,DC=corp,DC=local\nsAMAccountName: carol\n',
                },
            },
            'solution': {
                'shell': "grep -oP 'user:\\[\\K[^]]+' rpc.raw | tr 'A-Z' 'a-z' | sort -u > users-rpc.txt && grep -i '^samaccountname:' ldap.raw | awk '{print tolower($2)}' | sort -u > users-ldap.txt && comm -3 users-rpc.txt users-ldap.txt > only-one-source.txt && cat users-rpc.txt users-ldap.txt | sort -u > users.txt",
            },
            'steps': [
                {
                    'instruction': 'Extract the usernames from rpc.raw, lowercase and sorted, into users-rpc.txt.',
                    'hint': "grep -oP 'user:\\[\\K[^]]+' rpc.raw | tr 'A-Z' 'a-z'",
                },
                {
                    'instruction': 'Do the same for the LDIF in ldap.raw into users-ldap.txt.',
                    'hint': "grep -i '^samaccountname:' ldap.raw | awk '{print tolower($2)}'",
                },
                {
                    'instruction': 'Write the names that appear in only one source to only-one-source.txt.',
                    'hint': 'comm -3 users-rpc.txt users-ldap.txt',
                },
                {
                    'instruction': 'Merge both into one deduplicated users.txt for the next tool to consume.',
                },
            ],
            'free': 'Produce users-rpc.txt, users-ldap.txt, only-one-source.txt and a merged users.txt, all lowercase and sorted.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_contains': {
                        'users-rpc.txt': [
                            'administrator',
                            'svc_sql',
                        ],
                        'users-ldap.txt': 'carol',
                        'only-one-source.txt': [
                            'svc_sql',
                            'carol',
                        ],
                        'users.txt': [
                            'alice',
                            'bob',
                            'carol',
                        ],
                    },
                    'file_lacks': {
                        'users-rpc.txt': 'rid',
                    },
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'sac-rid',
            'title': 'Read the RIDs and say what they are',
            'goal': 'Convert the hex RIDs in real rpcclient output to decimal and identify the well-known ones.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {
                    'rpc.raw': 'user:[Administrator] rid:[0x1f4]\nuser:[Guest] rid:[0x1f5]\nuser:[alice] rid:[0x452]\nuser:[svc_backup] rid:[0x454]\n',
                },
            },
            'solution': {
                'shell': 'grep -oP \'user:\\[\\K[^]]+(?=\\] rid:\\[)\' rpc.raw > names.txt; grep -oP \'rid:\\[0x\\K[0-9a-f]+\' rpc.raw | while read h; do printf \'%d\\n\' 0x$h; done > rids.txt && paste -d" " rids.txt names.txt > rid-table.txt && grep "^500 " rid-table.txt > builtin-admin.txt',
            },
            'steps': [
                {
                    'instruction': 'Extract the hex RIDs and convert each to decimal, into rids.txt.',
                    'hint': "grep -oP 'rid:\\[0x\\K[0-9a-f]+' rpc.raw | while read h; do printf '%d\\n' 0x$h; done",
                },
                {
                    'instruction': 'Pair each decimal RID with its username into rid-table.txt.',
                    'hint': 'paste -d" " rids.txt names.txt',
                },
                {
                    'instruction': 'Pull out the line for RID 500 into builtin-admin.txt. That account is the built-in Administrator whatever it is called.',
                },
            ],
            'free': 'Produce rid-table.txt pairing decimal RIDs with usernames, and builtin-admin.txt holding the RID 500 entry.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_contains': {
                        'rid-table.txt': [
                            '500 Administrator',
                            '1106 alice',
                            '1108 svc_backup',
                        ],
                        'builtin-admin.txt': '500',
                    },
                },
            },
            'fallback': 'self',
        },
    ],
    'quiz': [
        {
            'id': 'saq-listread',
            'type': 'mcq',
            'prompt': 'smbclient -L shows a share. What does that prove about your access to its files?',
            'answer': 'Nothing. Share and NTFS permissions are separate and both apply.',
            'distractors': [
                'That you can read every file in it.',
                'That you can read but not write.',
                'That the share is world readable by design.',
            ],
            'teach': 'Effective access is the more restrictive of the two. netexec --shares reports READ and WRITE, which is the question you actually had.',
        },
        {
            'id': 'saq-ipc',
            'type': 'mcq',
            'prompt': 'What is the IPC$ share for?',
            'answer': 'Named pipes, which is how RPC calls travel over SMB.',
            'distractors': [
                'Administrative access to the C drive.',
                'The printer spooler queue.',
                'A hidden share holding domain policy files.',
            ],
            'teach': 'It is not a file share, which is why a null session to IPC$ is about RPC rather than about files.',
        },
        {
            'id': 'saq-rid500',
            'type': 'mcq',
            'prompt': 'An account has RID 500 but is named "svcadmin". What is it?',
            'answer': 'The built-in Administrator, renamed.',
            'distractors': [
                'A service account created during domain build.',
                'The first user account created after promotion.',
                'A machine account for the domain controller.',
            ],
            'teach': 'Well-known RIDs are fixed: 500 Administrator, 501 Guest, 512 Domain Admins. Renaming does not change the RID.',
        },
    ],
}
