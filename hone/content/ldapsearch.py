"""ldapsearch: querying Active Directory directly.

LDAP is the directory itself and the richest source, and the syntax is the barrier: the base DN (corp.local is DC=corp,DC=local), the parenthesised prefix filters, and the bitwise userAccountControl rule that finds disabled or pre-auth-not-required accounts. The module is those filters and reading the LDIF that comes back.

Writing filters and decoding UAC values are sandbox-verified; the live queries need a directory, which the lab modules describe. Scope: the tool, never the engagement.
"""

MODULE = {
    'id': 'ldapsearch',
    'title': 'ldapsearch',
    'group': 'Security',
    'blurb': 'The base DN, LDAP filters, the bitwise UAC rule, and decoding what comes back.',
    'context': 'You are querying an Active Directory LDAP service you may test.',
    'needs': [
        'ldapsearch',
    ],
    'prereqs': [
        'ssh',
        'linux',
    ],
    'adapter': 'sandbox',
    'estimate': '2-3 hours',
    'order': 79,
    'lessons': [
        {
            'id': 'sa-ldap',
            'title': 'Querying the directory with ldapsearch',
            'concept': 'LDAP is the directory itself, and it is the richest source by a wide margin. The syntax is the barrier, and it is smaller than it looks once three things are clear.\n\n**The base DN** is where in the tree to start, and it is the domain name in LDAP form: corp.local becomes "DC=corp,DC=local". Get this wrong and you get nothing, with no useful error.\n\n**The filter** is a parenthesised prefix expression, which is what makes it look strange. `(objectClass=user)` is one condition. `(&(a=1)(b=2))` is and, `(|(a=1)(b=2))` is or, `(!(a=1))` is not. Wildcards are asterisks, and an attribute existing at all is `(attr=*)`.\n\n**Bitwise conditions** are how the userAccountControl flags are queried, and they look alarming: `(userAccountControl:1.2.840.113556.1.4.803:=2)` means the account-disabled bit is set. That OID is the LDAP_MATCHING_RULE_BIT_AND, it is always the same, and it is worth copying rather than remembering.\n\nThe queries that pay off are a short list: all users, all computers, members of a privileged group, accounts with a servicePrincipalName, accounts with DONT_REQ_PREAUTH set, accounts whose password never expires, and anything with a description field, because administrators put passwords in description fields with remarkable consistency.\n\nAnonymous binds are usually refused on modern AD; authenticated reads are usually permitted broadly. The global catalog on 3268 answers forest-wide questions that 389 answers only for one domain.',
            'examples': [
                {
                    'label': 'What is this directory, before you know anything',
                    'code': 'ldapsearch -x -H ldap://10.0.0.10 -s base namingContexts',
                    'note': 'The RootDSE is readable anonymously far more often than anything else, and it tells you the base DN.',
                },
                {
                    'label': 'Every user, one attribute',
                    'code': 'ldapsearch -x -H ldap://10.0.0.10 -D "alice@corp.local" -w pass -b "DC=corp,DC=local" "(objectClass=user)" samAccountName',
                    'note': 'Naming the attributes you want keeps the output readable. Omit them and you get everything.',
                },
                {
                    'label': 'Accounts with a service principal name',
                    'code': '"(&(objectClass=user)(servicePrincipalName=*))"',
                    'note': 'Service accounts. The asterisk means the attribute exists at all.',
                },
                {
                    'label': 'The bitwise one, worth copying',
                    'code': '"(userAccountControl:1.2.840.113556.1.4.803:=2)"',
                    'note': 'Disabled accounts. Bit 2 is ACCOUNTDISABLE and the OID never changes.',
                },
                {
                    'label': 'Where administrators hide passwords',
                    'code': '"(&(objectClass=user)(description=*))" description',
                    'note': 'Unreasonably productive, and it costs one query.',
                },
            ],
            'misconceptions': [
                'The base DN is not the hostname. corp.local is "DC=corp,DC=local", and getting it wrong returns nothing rather than an error.',
                'LDAP filters are prefix notation, so the operator comes first: (&(a)(b)), never (a & b).',
                'Anonymous bind being refused does not mean LDAP is closed. Authenticated reads are usually wide open.',
            ],
            'try_it': [
                'Query the RootDSE of a lab DC and recover its base DN from namingContexts.',
                'Write a filter combining two conditions with and, then negate one of them.',
            ],
            'next': None,
        },
    ],
    'drills': [
        {
            'id': 'sad-ldap-rootdse',
            'type': 'command',
            'prompt': 'Read the naming contexts from 10.0.0.10 without authenticating.',
            'answer': 'ldapsearch -x -H ldap://10.0.0.10 -s base namingContexts',
            'teach': 'The RootDSE is readable anonymously far more often than anything else, and it hands you the base DN.',
        },
        {
            'id': 'sad-ldap-users',
            'type': 'command',
            'prompt': 'List samAccountName for every user in DC=corp,DC=local as alice.',
            'answer': 'ldapsearch -x -H ldap://10.0.0.10 -D "alice@corp.local" -w pass -b "DC=corp,DC=local" "(objectClass=user)" samAccountName',
            'teach': 'Naming the attributes keeps the output readable. Omit them and you get every attribute of every object.',
        },
        {
            'id': 'sad-ldap-computers',
            'type': 'command',
            'prompt': 'Write the LDAP filter that selects computer objects.',
            'answer': '(objectClass=computer)',
            'teach': 'A computer is a kind of account object, which is why it has a password and can be attacked like one.',
        },
        {
            'id': 'sad-ldap-and',
            'type': 'command',
            'prompt': 'Write a filter for users that have a servicePrincipalName.',
            'answer': '(&(objectClass=user)(servicePrincipalName=*))',
            'teach': 'Prefix notation: the operator comes first. The asterisk means the attribute exists at all.',
        },
        {
            'id': 'sad-ldap-not',
            'type': 'command',
            'prompt': 'Write a filter for users without a description attribute.',
            'answer': '(&(objectClass=user)(!(description=*)))',
            'teach': 'Negation wraps a whole condition. The interesting query is usually the other way round.',
        },
        {
            'id': 'sad-ldap-disabled',
            'type': 'command',
            'prompt': 'Write the bitwise filter for accounts that are disabled.',
            'answer': '(userAccountControl:1.2.840.113556.1.4.803:=2)',
            'teach': 'That OID is LDAP_MATCHING_RULE_BIT_AND and never changes. Bit 2 is ACCOUNTDISABLE.',
        },
        {
            'id': 'sad-ldap-preauth',
            'type': 'command',
            'prompt': 'Write the bitwise filter for accounts not requiring pre-authentication.',
            'answer': '(userAccountControl:1.2.840.113556.1.4.803:=4194304)',
            'teach': 'DONT_REQ_PREAUTH. Each of these is an offline crackable artefact obtainable with no credentials.',
        },
        {
            'id': 'sad-ldap-descr',
            'type': 'command',
            'prompt': 'Write a filter for users whose description field is set.',
            'answer': '(&(objectClass=user)(description=*))',
            'teach': 'Unreasonably productive. Administrators put passwords in description fields with great consistency.',
        },
        {
            'id': 'sad-ldap-gc',
            'type': 'command',
            'prompt': 'Query the global catalog on 10.0.0.10 rather than plain LDAP.',
            'answer': 'ldapsearch -x -H ldap://10.0.0.10:3268 -b "DC=corp,DC=local" "(objectClass=user)"',
            'teach': '3268 answers forest-wide with a partial attribute set; 389 answers one domain completely.',
        },
        {
            'id': 'sad-parse-ldap',
            'type': 'command',
            'prompt': 'Extract lowercase samAccountName values from ldap.raw.',
            'answer': "grep -i '^samaccountname:' ldap.raw | awk '{print tolower($2)}' | sort -u",
            'teach': 'Normalise case and order early, or three tools will disagree about whether a name matches.',
        },
    ],
    'challenges': [
        {
            'id': 'sac-uac',
            'title': 'Decode the userAccountControl flags',
            'goal': 'Given real UAC values, work out which accounts are disabled, which never expire, and which skip pre-authentication.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {
                    'uac.txt': 'alice 512\nbob 514\nsvc_sql 66048\noldsvc 4194816\n',
                },
            },
            'solution': {
                'shell': 'awk \'{ v=$2; d=(int(v/2)%2==1) ? "DISABLED" : "-"; n=(int(v/65536)%2==1) ? "NEVER_EXPIRES" : "-"; p=(int(v/4194304)%2==1) ? "NO_PREAUTH" : "-"; print $1, d, n, p }\' uac.txt > flags.txt && grep DISABLED flags.txt > disabled.txt && grep NO_PREAUTH flags.txt > no-preauth.txt',
            },
            'steps': [
                {
                    'instruction': 'Bit 2 is ACCOUNTDISABLE, bit 65536 is DONT_EXPIRE_PASSWORD, bit 4194304 is DONT_REQ_PREAUTH. Test each value against each bit.',
                },
                {
                    'instruction': 'Write one line per account to flags.txt naming which flags are set.',
                },
                {
                    'instruction': 'Split out the disabled accounts into disabled.txt and the pre-auth ones into no-preauth.txt.',
                    'hint': 'grep DISABLED flags.txt > disabled.txt',
                },
            ],
            'free': 'Produce flags.txt decoding each account, plus disabled.txt and no-preauth.txt containing the accounts with those bits set.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_contains': {
                        'flags.txt': [
                            'alice',
                            'svc_sql',
                        ],
                        'disabled.txt': 'bob',
                        'no-preauth.txt': 'oldsvc',
                    },
                    'file_lacks': {
                        'disabled.txt': 'alice',
                    },
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'sac-filters',
            'title': 'Write the LDAP filters from the questions',
            'goal': 'Six questions, six filters. Prefix notation, and the bitwise form for the flag ones.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {
                    'questions.txt': '1 every user object\n2 every computer object\n3 users that have a servicePrincipalName\n4 users that are disabled\n5 users that do not require pre-authentication\n6 users with a description set\n',
                },
            },
            'solution': {
                'shell': "printf '%s\\n' '1 (objectClass=user)' '2 (objectClass=computer)' '3 (&(objectClass=user)(servicePrincipalName=*))' '4 (userAccountControl:1.2.840.113556.1.4.803:=2)' '5 (userAccountControl:1.2.840.113556.1.4.803:=4194304)' '6 (&(objectClass=user)(description=*))' > filters.txt",
            },
            'steps': [
                {
                    'instruction': 'Read questions.txt. Write one filter per line into filters.txt, numbered to match.',
                },
                {
                    'instruction': 'Remember prefix notation: the operator comes first, as in (&(a)(b)).',
                },
                {
                    'instruction': 'For the two flag questions, use the bitwise matching rule OID with the right bit value.',
                    'hint': '(userAccountControl:1.2.840.113556.1.4.803:=2)',
                },
            ],
            'free': 'Produce filters.txt with a correct LDAP filter for each of the six numbered questions.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_contains': {
                        'filters.txt': [
                            '(objectClass=user)',
                            '(objectClass=computer)',
                            'servicePrincipalName=*',
                            '1.2.840.113556.1.4.803:=2',
                            '1.2.840.113556.1.4.803:=4194304',
                            'description=*',
                        ],
                    },
                },
            },
            'fallback': 'self',
        },
    ],
    'quiz': [
        {
            'id': 'saq-basedn',
            'type': 'mcq',
            'prompt': 'What is the base DN for the domain corp.local?',
            'answer': 'DC=corp,DC=local',
            'distractors': [
                'CN=corp.local',
                'OU=corp,OU=local',
                'DN=corp.local',
            ],
            'teach': 'Each dotted component becomes a DC= element. Getting it wrong returns nothing rather than an error, which is worse than failing.',
        },
        {
            'id': 'saq-filter-syntax',
            'type': 'mcq',
            'prompt': 'Which is a valid LDAP filter for users with an SPN?',
            'answer': '(&(objectClass=user)(servicePrincipalName=*))',
            'distractors': [
                '(objectClass=user & servicePrincipalName=*)',
                '(objectClass=user AND servicePrincipalName)',
                '(objectClass=user)&(servicePrincipalName=*)',
            ],
            'teach': 'Prefix notation: the operator leads, and every condition is parenthesised.',
        },
        {
            'id': 'saq-uac-bit',
            'type': 'mcq',
            'prompt': 'What does userAccountControl bit 4194304 indicate?',
            'answer': 'The account does not require Kerberos pre-authentication.',
            'distractors': [
                'The account is disabled.',
                'The password never expires.',
                'The account is trusted for delegation.',
            ],
            'teach': 'DONT_REQ_PREAUTH, and each such account yields an offline crackable AS-REP to anyone who asks.',
        },
    ],
}
