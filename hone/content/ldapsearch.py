"""ldapsearch: querying Active Directory directly.

LDAP is the directory itself and the richest source, and the syntax is the
barrier: the base DN (corp.local is DC=corp,DC=local), the parenthesised prefix
filters, and the bitwise userAccountControl rule that finds disabled or
pre-auth-not-required accounts.

**Rebuilt from one lesson to seven.** The module arrived from the D31 split of
the smbad bundle with a single 3000-character lesson carrying ten drills, and
`ramp.py` found six of those drills demanding things the lesson never mentioned:
the computer filter, the negated filter, the pre-auth OID, and the whole
`grep | awk | sort -u` pipeline the parsing drill expects. That is not a pacing
problem, it is a module that sets an exam on material it did not cover.

The ramp now starts at "what is a directory and why is it not a database",
which is where someone who has never touched LDAP actually starts, and ends on
the global catalog and the matching-rule OIDs, which is further than the old
single lesson reached. Anyone who already knows what a DN is can skip the first
two lessons and lose nothing.

Writing filters and decoding UAC values are sandbox-verified; the live queries
need a directory, which the lab modules describe. Scope: the tool, never the
engagement.
"""

MODULE = {
    'id': 'ldapsearch',
    'title': 'ldapsearch',
    'group': 'Security',
    'blurb': 'The tree, the base DN, filters, the bitwise UAC rule, and reading LDIF back.',
    'context': 'You are querying an Active Directory LDAP service you may test.',
    'needs': [
        'ldapsearch',
    ],
    'prereqs': [
        'ssh',
        'linux',
    ],
    'adapter': 'sandbox',
    'estimate': '3-4 hours',
    'order': 86,
    'lessons': [
        {
            'id': 'sa-what',
            'title': 'What a directory is, and what it is not',
            'next': 'sa-dn',
            'concept': (
                'A directory is a database that has made peace with being '
                'read far more often than it is written. That single decision '
                'explains almost everything odd about LDAP: the tree shape, '
                'the strange query syntax, the fact that there are no joins '
                'and nobody misses them.\n\n'
                'The thing on the wire is **LDAP**, the Lightweight Directory '
                'Access Protocol, and the "lightweight" is a joke from 1993 '
                'about the thing it replaced. Active Directory is Microsoft\'s '
                'directory, and LDAP is how you talk to it. So is `net`, and '
                'so is PowerShell, and so are half the tools in this group. '
                'LDAP is the one that shows you what is actually stored.\n\n'
                '**Everything in the directory is an entry**, and every entry '
                'is a bag of attributes. A user is an entry. A computer is an '
                'entry. A group is an entry that keeps a list of other '
                'entries\' names. There is no schema flexibility crisis here '
                'and no migrations: an entry has whatever attributes its '
                'object classes allow, and that is that.\n\n'
                'What makes it worth querying directly is that **the '
                'directory answers honestly about itself**. It will tell you '
                'every user, every group membership, every machine, every '
                'account with an odd flag set, to anyone permitted to read, '
                'and in a default Active Directory that is very nearly '
                'everyone with a password.'
            ),
            'examples': [
                {
                    'label': 'One entry, as the directory holds it',
                    'code': ('dn: CN=Alice Smith,OU=Staff,DC=corp,DC=local\n'
                             'objectClass: user\n'
                             'samAccountName: alice\n'
                             'userAccountControl: 512\n'
                             'description: temp pw Summer2024!\n'
                             'memberOf: CN=Domain Admins,CN=Users,DC=corp,'
                             'DC=local'),
                    'note': 'Six attributes and two of them are already '
                            'interesting. The last line is a membership, and '
                            'the one above it is a resignation letter.',
                },
                {
                    'label': 'Why there are no joins',
                    'code': ('SQL      SELECT u.name FROM users u\n'
                             '         JOIN memberships m ON ...\n'
                             '\n'
                             'LDAP     the entry already carries memberOf\n'
                             '         the group already carries member'),
                    'note': 'Both sides store the relationship. That is '
                            'duplication, and a read-mostly store can afford '
                            'it in exchange for never joining anything.',
                },
            ],
            'misconceptions': [
                'LDAP is not a product. It is a protocol, and Active '
                'Directory, OpenLDAP and several others all speak it.',
                'A directory is not a relational database with worse syntax. '
                'It is optimised for reads and for hierarchy, and it drops '
                'joins and transactions to get there.',
                'Reading the directory is not an exotic privilege. In a '
                'default Active Directory any authenticated account can read '
                'most of it, which is the point of this module.',
            ],
            'try_it': [
                'Run `ldapsearch -VV` to confirm which implementation you '
                'have. OpenLDAP is the usual one on Linux and is what every '
                'example here assumes.',
                'Before reading on, guess how a directory would name an entry '
                'uniquely when there is no primary key. The next lesson is '
                'that answer.',
            ],
        },
        {
            'id': 'sa-dn',
            'title': 'The DN, and reading an address backwards',
            'next': 'sa-first',
            'concept': (
                'The distinguished name is how you address one entry in the '
                'tree. That is why a wrong base DN returns zero results with '
                'no error, and why you ask the RootDSE for namingContexts '
                'instead of guessing.\n\n'
                '`CN=Alice Smith,OU=Staff,DC=corp,DC=local` reads right to '
                'left: the domain corp.local, the Staff organisational unit '
                'inside it, and Alice inside that. It is a postal address '
                'with the country last, which is to say it is a postal '
                'address.\n\n'
                'Three prefixes carry almost all of it. **DC** is a domain '
                'component, one per dotted part of the domain name. **OU** is '
                'an organisational unit, which is a folder. **CN** is a common '
                'name, which is the object itself. There are others and you '
                'can go a long time without meeting them.\n\n'
                '**The base DN is where a search starts**, and for a whole '
                'domain it is just the domain name rewritten: corp.local '
                'becomes `DC=corp,DC=local`. Getting this wrong is the most '
                'common first failure, and the failure mode is cruel: you get '
                'zero results and no error, because "nothing exists below a '
                'branch that does not exist" is a perfectly good answer to a '
                'question nobody meant to ask.\n\n'
                'You do not have to guess it. Every server publishes a '
                '**RootDSE**, an unnamed entry above the tree describing the '
                'server, and it is readable without credentials far more '
                'often than anything else. Ask it for `namingContexts` and it '
                'hands you the base DN.\n\n'
                'You have the base DN. The next lesson is the first '
                'query, and the five flags that actually matter.'
            ),
            'examples': [
                {
                    'label': 'A DN, taken apart',
                    'code': ('CN=Alice Smith,OU=Staff,DC=corp,DC=local\n'
                             '\\_________/ \\______/ \\______________/\n'
                             '  the user   a folder   the domain\n'
                             '\n'
                             'read it right to left, like a postcode'),
                    'note': 'The leftmost part is the entry itself, and it is '
                            'called the RDN, the relative distinguished name.',
                },
                {
                    'label': 'Domain name to base DN',
                    'code': ('corp.local          DC=corp,DC=local\n'
                             'ad.example.com      DC=ad,DC=example,DC=com\n'
                             'lab.corp.local      DC=lab,DC=corp,DC=local\n'
                             '\n'
                             'one DC= per dot, same order'),
                    'note': 'Mechanical, once seen. This is worth converting '
                            'in your head a few times until it is automatic.',
                },
                {
                    'label': 'Asking the server instead of guessing',
                    'code': ('ldapsearch -x -H ldap://10.0.0.10 \\\n'
                             '           -s base namingContexts\n'
                             '\n'
                             'namingContexts: DC=corp,DC=local'),
                    'note': 'The RootDSE is the one thing a locked-down '
                            'directory usually still tells a stranger.',
                },
            ],
            'misconceptions': [
                'The base DN is not the hostname. corp.local as a base DN is '
                '`DC=corp,DC=local`, and typing the hostname returns nothing '
                'rather than an error.',
                'A wrong base DN does not produce an error message. It '
                'produces zero results, which looks exactly like a domain '
                'with no users in it.',
                'CN is not a username. `CN=Alice Smith` is usually the display '
                'name, and the login name lives in samAccountName, which is a '
                'different attribute entirely.',
            ],
            'try_it': [
                'Convert three domain names to base DNs on paper: '
                'example.org, corp.internal, and ad.lab.example.com.',
                'Query the RootDSE of a lab DC and recover its base DN from '
                'namingContexts, then use that value in the next lesson.',
            ],
        },
        {
            'id': 'sa-first',
            'title': 'Your first query, and the flags that matter',
            'next': 'sa-filters',
            'concept': (
                'The five flags on ldapsearch are how you name the server, '
                'the identity, the start point, the scope, and the '
                'attributes. That is why the same shape writes every query, '
                'and why omitting the attribute list dumps kilobytes you '
                'cannot pipe.\n\n'
                '**`-H`** is the server URL, `ldap://host` or `ldaps://host`. '
                '**`-b`** is the base DN to search from. **`-x`** means '
                'simple authentication rather than SASL, which is what you '
                'want unless you are doing Kerberos. **`-D`** is the identity '
                'to bind as and **`-w`** its password.\n\n'
                'Then two that pay for themselves immediately. **`-s`** sets '
                'the scope: `base` is that one entry, `one` is its direct '
                'children, `sub` is the whole subtree and is the default. '
                '**`-LLL`** strips the LDIF version comment and other noise, '
                'which turns output you have to skim into output you can '
                'pipe.\n\n'
                '**Anything after the filter is an attribute list**, and '
                'naming attributes is the difference between six lines and '
                'six hundred. Ask for `samAccountName` and you get names; ask '
                'for nothing and you get every attribute of every matching '
                'object, including the ones that are 4KB of binary security '
                'descriptor.\n\n'
                'A bare `-w` on the command line puts the password in your '
                'shell history and in `ps` output for every user on the box. '
                '`-W` prompts instead, and costs one keystroke.\n\n'
                'A directory will cut a large list. The server enforces a '
                'size limit and returns a partial result that looks complete '
                'if you do not notice the message at the end. `-E '
                'pr=1000/noprompt` asks for paged results, 1000 entries per '
                'page, and walks the pages without prompting. That is the '
                'form that finishes a user dump the default query truncated.'
            ),
            'examples': [
                {
                    'label': 'The shape of every query you will write',
                    'code': ('ldapsearch -x -H ldap://10.0.0.10 \\\n'
                             '  -D "alice@corp.local" -W \\\n'
                             '  -b "DC=corp,DC=local" \\\n'
                             '  "(objectClass=user)" samAccountName'),
                    'note': 'Server, identity, where to start, what to match, '
                            'what to show. Every query is those five things.',
                },
                {
                    'label': 'Scope, which is smaller than it sounds',
                    'code': ('-s base   this one entry only\n'
                             '-s one    its direct children\n'
                             '-s sub    everything below it (default)\n'
                             '\n'
                             '-s base is how you read the RootDSE'),
                    'note': 'Narrowing the scope is the cheapest way to make '
                            'a slow query fast on a large directory.',
                },
                {
                    'label': 'Readable output',
                    'code': ('-LLL          drop the LDIF boilerplate\n'
                             'samAccountName  ask for one attribute\n'
                             '\n'
                             'without both, one user is forty lines'),
                    'note': '-LLL is three Ls and each one removes a '
                            'different piece of clutter. Nobody remembers '
                            'which; everybody types three.',
                },
                {
                    'label': 'When the server cuts the list',
                    'code': ('ldapsearch -x -H ldap://10.0.0.10 \\\n'
                             '  -D "alice@corp.local" -W \\\n'
                             '  -b "DC=corp,DC=local" \\\n'
                             '  -E pr=1000/noprompt \\\n'
                             '  "(objectClass=user)" samAccountName'),
                    'note': 'Without paging, a size-limited result looks '
                            'finished. The message at the end is the only '
                            'hint you were cut off.',
                },
            ],
            'misconceptions': [
                '`-x` does not mean insecure. It means simple bind rather '
                'than SASL, and it is orthogonal to whether the connection is '
                'encrypted, which is what ldaps:// and StartTLS decide.',
                '`-w` and `-W` are not interchangeable in a shared '
                'environment. The lowercase one leaves the password in `ps` '
                'output and your history file.',
                'Omitting the attribute list does not give you a sensible '
                'default. It gives you everything, which on a user object '
                'includes several kilobytes you cannot read.',
            ],
            'try_it': [
                'Run the same query twice, once with `-LLL` and once without, '
                'and count the lines you did not want.',
                'Ask for a single attribute, then two, and watch the output '
                'stay in the shape you can pipe into something else.',
            ],
        },
        {
            'id': 'sa-filters',
            'title': 'Filters, from equality to boolean',
            'next': 'sa-uac',
            'concept': (
                'A filter is how you tell ldapsearch which entries to '
                'return. That is why equality, wildcards, and the three '
                'boolean wrappers are the whole query language rather than a '
                'syntax curiosity.\n\n'
                '**The base case is equality**: `(objectClass=user)` matches '
                'entries whose objectClass includes user. **An asterisk is a '
                'wildcard**, so `(cn=alice*)` is a prefix match, and '
                '`(description=*)` means the attribute exists at all, which '
                'turns out to be one of the most useful queries there is.\n\n'
                '**Three operators combine them**, and each one wraps its '
                'operands rather than sitting between them. `(&(a=1)(b=2))` '
                'is and. `(|(a=1)(b=2))` is or. `(!(a=1))` is not, and it '
                'takes exactly one operand, which is why negating a condition '
                'means wrapping the whole thing: `(!(description=*))`.\n\n'
                'They nest, and the nesting is where people go wrong. Every '
                'condition gets its own brackets, and the operator gets '
                'brackets around the whole group, so "users with no '
                'description" is `(&(objectClass=user)(!(description=*)))` '
                'and counting the closing brackets is a legitimate part of '
                'the job.\n\n'
                '**One Active Directory trap.** `(objectClass=user)` also '
                'matches computers, because in AD a computer account is a '
                'kind of user, with a password and a login and everything '
                'that implies. To get people only, use '
                '`(&(objectCategory=person)(objectClass=user))`, and to get '
                'machines deliberately, use `(objectClass=computer)`.\n\n'
                'Equality and wildcards cover most questions. The next '
                'lesson is the leftover one: a single bit inside '
                'userAccountControl.'
            ),
            'examples': [
                {
                    'label': 'The operators, which all read the same way',
                    'code': ('(objectClass=user)              equality\n'
                             '(cn=alice*)                     wildcard\n'
                             '(description=*)                 exists at all\n'
                             '\n'
                             '(&(a=1)(b=2))                   and\n'
                             '(|(a=1)(b=2))                   or\n'
                             '(!(a=1))                        not'),
                    'note': 'The operator leads and every operand is '
                            'bracketed. There is no precedence to remember '
                            'because there is nothing ambiguous to resolve.',
                },
                {
                    'label': 'Building one up',
                    'code': ('(objectClass=user)\n'
                             '(&(objectClass=user)(description=*))\n'
                             '(&(objectClass=user)(!(description=*)))\n'
                             '\n'
                             'users, then those with a description,\n'
                             'then those without'),
                    'note': 'Negation wraps a condition that was already '
                            'complete. That is why there are two closing '
                            'brackets in a row at the end.',
                },
                {
                    'label': 'Queries that repay the typing',
                    'code': ('(objectClass=computer)\n'
                             '(&(objectClass=user)(servicePrincipalName=*))\n'
                             '(&(objectClass=user)(description=*))\n'
                             '(&(objectCategory=person)(objectClass=user))'),
                    'note': 'The description one is unreasonably productive. '
                            'Administrators put passwords in description '
                            'fields with remarkable consistency.',
                },
            ],
            'misconceptions': [
                'Filters are not infix. `(a=1 & b=2)` is not a filter, and '
                'neither is `(a=1)&(b=2)`. The operator goes inside the '
                'brackets, in front.',
                '`(objectClass=user)` does not mean people. In Active '
                'Directory it includes every computer account, which is why '
                'the count is always higher than the staff list.',
                'Negation does not attach to an attribute. `(!description=*)` '
                'is malformed; the whole condition has to be wrapped, as '
                '`(!(description=*))`.',
            ],
            'try_it': [
                'Write, on paper, a filter for computer objects that have a '
                'description. Then negate it.',
                'Count the brackets in '
                '`(&(objectClass=user)(!(description=*)))` and satisfy '
                'yourself about which one closes what.',
            ],
        },
        {
            'id': 'sa-uac',
            'title': 'The bitwise rule, and userAccountControl',
            'next': 'sa-ldif',
            'concept': (
                'The bitwise match on userAccountControl is how you ask '
                'about a flag that is not its own attribute. That is why '
                'disabled, never-expires, and no-preauth accounts are one '
                'OID and a different number on the end.\n\n'
                '**userAccountControl is a bitfield.** One integer on every '
                'account, where each bit is a property: disabled, password '
                'never expires, no pre-authentication required, trusted for '
                'delegation. A normal enabled account is 512. Disable it and '
                'it becomes 514, because bit 2 went on.\n\n'
                'You cannot ask for that with equality, because you want '
                '"has this bit set" and not "equals this number". So there is '
                'an **extensible match** with a matching-rule OID:\n\n'
                '`(userAccountControl:1.2.840.113556.1.4.803:=2)`\n\n'
                'That OID is LDAP_MATCHING_RULE_BIT_AND. It never changes, it '
                'is the same on every Active Directory on earth, and you are '
                'not expected to remember it. Nobody remembers it. It is '
                'copied, forever, by everyone, and the only part you change '
                'is the number on the end.\n\n'
                '**The bits worth knowing** are 2 for ACCOUNTDISABLE, 65536 '
                'for DONT_EXPIRE_PASSWORD, 524288 for TRUSTED_FOR_DELEGATION '
                'and 4194304 for DONT_REQ_PREAUTH. That last one matters more '
                'than its obscurity suggests: an account with it set will '
                'hand an offline-crackable Kerberos response to anyone who '
                'asks, with no credentials at all.\n\n'
                'There is a sibling OID ending `.804` which is BIT_OR, '
                'matching if any of the named bits are set. It comes up '
                'rarely and reads identically.'
            ),
            'examples': [
                {
                    'label': 'The one to copy',
                    'code': ('(userAccountControl:1.2.840.113556.1.4.803:=2)\n'
                             ' \\______________/ \\__________________/  \\_/\n'
                             '   the attribute     BIT_AND, always     bit\n'
                             '\n'
                             'only the last number ever changes'),
                    'note': 'The 1.2.840.113556 prefix is Microsoft\'s OID '
                            'arc, which is why it turns up all over Active '
                            'Directory and nowhere else.',
                },
                {
                    'label': 'Bits worth recognising on sight',
                    'code': ('     2   ACCOUNTDISABLE\n'
                             '    16   LOCKOUT\n'
                             ' 65536   DONT_EXPIRE_PASSWORD\n'
                             '524288   TRUSTED_FOR_DELEGATION\n'
                             '4194304  DONT_REQ_PREAUTH'),
                    'note': 'A value of 512 is a normal enabled account. 514 '
                            'is 512 plus 2, which is that account disabled.',
                },
                {
                    'label': 'The two you will actually run',
                    'code': ('(userAccountControl:1.2.840.113556.1.4.803:=2)\n'
                             '  disabled accounts\n'
                             '\n'
                             '(userAccountControl:1.2.840.113556.1.4.803:'
                             '=4194304)\n'
                             '  no Kerberos pre-authentication'),
                    'note': 'Identical but for the last number, which is the '
                            'whole idea. The second is the one worth running '
                            'first on any directory you are allowed to test.',
                },
                {
                    'label': 'Reading a value by hand',
                    'code': ('66048 = 65536 + 512\n'
                             '      = DONT_EXPIRE_PASSWORD + normal account\n'
                             '\n'
                             '4194816 = 4194304 + 512\n'
                             '      = DONT_REQ_PREAUTH + normal account'),
                    'note': 'Subtract the largest bit you recognise and '
                            'repeat. The remainder is almost always 512.',
                },
            ],
            'misconceptions': [
                'userAccountControl is not a status code. It is a bitfield, '
                'so 514 is not "state 514", it is two flags added together.',
                'The OID is not per-domain or per-server. '
                '1.2.840.113556.1.4.803 is the same everywhere and can be '
                'copied without thought.',
                'A disabled account is not invisible. It is still an entry, '
                'still readable, and still tells you a name that once '
                'existed.',
            ],
            'try_it': [
                'Decode 66050 by hand. Which two flags are set on top of the '
                'normal account bit?',
                'Write the bitwise filter for accounts whose password never '
                'expires, changing only the last number.',
            ],
        },
        {
            'id': 'sa-ldif',
            'title': 'Reading LDIF back, and shaping it',
            'next': 'sa-ports',
            'concept': (
                'What comes back is **LDIF**, which is a plain-text format of '
                '`attribute: value` lines with a blank line between entries. '
                'It is designed to be read by humans and re-imported by '
                'servers, and it pipes into ordinary text tools without '
                'complaint.\n\n'
                'Two details will bite you. A **double colon** means the '
                'value is base64, which the server does whenever the value '
                'has leading spaces, non-ASCII characters or newlines, so '
                '`description:: UGFzc3dvcmQx` is not a weird attribute name, '
                'it is a value you need to decode. And **long values are '
                'wrapped** onto continuation lines that begin with a single '
                'space, so a naive grep can cut a value in half.\n\n'
                'The pipeline that follows almost every query is the same '
                'three moves: select the lines you want, take the value, and '
                'normalise. `grep -i` finds the attribute regardless of the '
                'case the server chose to send. `awk \'{print $2}\'` takes '
                'the value after the colon. `sort -u` puts it in a stable '
                'order and removes the duplicates you will otherwise '
                'discover much later.\n\n'
                '**Normalise case early.** Windows treats account names '
                'case-insensitively and LDAP will happily hand you `Alice`, '
                '`alice` and `ALICE` from three queries. Lowercase everything '
                'the moment it leaves the directory and the three tools you '
                'feed it into will agree with each other.'
            ),
            'examples': [
                {
                    'label': 'LDIF, and the two things that catch people',
                    'code': ('dn: CN=Alice,OU=Staff,DC=corp,DC=local\n'
                             'samAccountName: alice\n'
                             'description:: IHNwYWNlIGF0IHRoZSBmcm9udA==\n'
                             'memberOf: CN=A Very Long Group Name That Cont\n'
                             ' inues Here,OU=Groups,DC=corp,DC=local'),
                    'note': 'Double colon is base64. A line starting with one '
                            'space is a continuation of the line above it.',
                },
                {
                    'label': 'The pipeline you will type a hundred times',
                    'code': ("grep -i '^samaccountname:' ldap.raw \\\n"
                             "  | awk '{print tolower($2)}' \\\n"
                             '  | sort -u'),
                    'note': '-i because the server picks the case, tolower '
                            'because you want one canonical form, and -u '
                            'because duplicates are guaranteed.',
                },
                {
                    'label': 'Decoding a base64 value',
                    'code': ('echo UGFzc3dvcmQxMjMh | base64 -d\n'
                             'Password123!\n'
                             '\n'
                             'the :: was the only clue it was encoded'),
                    'note': 'Worth checking every double-colon value in a '
                            'description field, for reasons the previous '
                            'lesson made clear.',
                },
            ],
            'misconceptions': [
                'A double colon is not a typo or a different attribute. It '
                'marks a base64-encoded value, and the plain and encoded '
                'forms carry the same attribute name.',
                'Attribute names in output are not reliably the case you '
                'asked for. `grep -i` rather than `grep`, always.',
                '`sort -u` is not just tidiness. Group membership queries '
                'routinely return the same account several times, and '
                'counting the raw lines gives a number that is simply wrong.',
            ],
            'try_it': [
                'Save a query to a file with `-LLL`, then pull one attribute '
                'out of it with grep, awk and sort -u.',
                'Find a `::` line in real output and decode it with `base64 '
                '-d`. It is more often interesting than not.',
            ],
        },
        {
            'id': 'sa-ports',
            'title': 'Ports, binds, and what you may read',
            'concept': (
                'Ports 389, 636, 3268 and 3269 are how you choose what the '
                'directory will answer and whether the bind is encrypted. '
                'That is why an anonymous refusal on 389 is not a closed '
                'directory, and why the global catalog finds an account when '
                'you do not know which domain holds it.\n\n'
                '**389 is LDAP and 636 is LDAPS.** The first is plaintext '
                'unless you negotiate StartTLS on it, the second is TLS from '
                'the first byte. A bind on 389 with no TLS sends the password '
                'across the network in the clear, which many directories now '
                'refuse outright.\n\n'
                '**3268 is the global catalog, and 3269 is its TLS twin.** '
                'The distinction is genuinely useful: port 389 answers '
                'completely about one domain, while 3268 answers across the '
                'whole forest but only for a partial set of attributes. If '
                'you are looking for an account and do not know which domain '
                'holds it, the global catalog is the one that finds it.\n\n'
                '**Anonymous binds are usually refused** on a modern Active '
                'Directory, and this is where people conclude LDAP is closed '
                'and give up one step early. Authenticated reads are usually '
                'permitted very broadly indeed: any valid domain account can '
                'typically enumerate every user, every group and every '
                'machine. The lock is on the front door, not on any of the '
                'filing cabinets.\n\n'
                'The exception worth knowing is the RootDSE, which sits above '
                'the tree and is frequently readable with no credentials at '
                'all, because a client has to be able to discover the base DN '
                'before it can sensibly authenticate against it.'
            ),
            'examples': [
                {
                    'label': 'Four ports, two questions',
                    'code': ('389   LDAP        one domain, everything\n'
                             '636   LDAPS       same, wrapped in TLS\n'
                             '3268  GC          whole forest, some '
                             'attributes\n'
                             '3269  GC over TLS'),
                    'note': 'Use 3268 when you do not know which domain an '
                            'account lives in, and 389 when you need every '
                            'attribute of something you have already found.',
                },
                {
                    'label': 'The same query, forest-wide',
                    'code': ('ldapsearch -x -H ldap://10.0.0.10:3268 \\\n'
                             '  -b "DC=corp,DC=local" "(objectClass=user)"'),
                    'note': 'Note the port is on the URL. Everything else '
                            'about the command is unchanged.',
                },
                {
                    'label': 'What "it is closed" usually means',
                    'code': ('ldapsearch -x -H ldap://dc -b "DC=corp,DC=local"\n'
                             '  ldap_bind: Inappropriate authentication\n'
                             '\n'
                             'that is anonymous being refused,\n'
                             'not the directory being unreadable'),
                    'note': 'Add -D and -W and the same query usually returns '
                            'the entire directory.',
                },
            ],
            'misconceptions': [
                'An anonymous bind being refused does not mean LDAP is '
                'locked down. Authenticated reads are usually wide open, and '
                'that is the default configuration rather than a mistake.',
                'The global catalog is not a faster LDAP. It covers the whole '
                'forest but carries only a partial attribute set, so an '
                'attribute missing from a 3268 answer may exist on 389.',
                'ldaps:// on 636 and StartTLS on 389 are not the same thing, '
                'though they end up equally encrypted. Old clients often '
                'support only one of them.',
            ],
            'try_it': [
                'Query the same base DN on 389 and on 3268 and compare which '
                'attributes come back.',
                'Try an anonymous bind against a lab DC, read the error, then '
                'repeat it authenticated and notice how much changes.',
            ],
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
            'id': 'sad-ldap-basedn',
            'type': 'command',
            'prompt': 'Write the base DN for the domain ad.example.com.',
            'answer': 'DC=ad,DC=example,DC=com',
            'teach': 'One DC= per dotted component, in the same order. Mechanical once you have done it three times.',
        },
        {
            'id': 'sad-ldap-users',
            'type': 'command',
            'prompt': 'List samAccountName for every user in DC=corp,DC=local as alice.',
            'answer': 'ldapsearch -x -H ldap://10.0.0.10 -D "alice@corp.local" -w pass -b "DC=corp,DC=local" "(objectClass=user)" samAccountName',
            'teach': 'Naming the attributes keeps the output readable. Omit them and you get every attribute of every matching object.',
        },
        {
            'id': 'sad-ldap-quiet',
            'type': 'command',
            'prompt': 'Add the flag that strips LDIF boilerplate from output.',
            'answer': '-LLL',
            'teach': 'Three Ls, each removing a different piece of clutter. Nobody remembers which; everybody types three.',
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
            'teach': 'Negation wraps a whole condition, which is why the brackets double up at the end.',
        },
        {
            'id': 'sad-ldap-people',
            'type': 'command',
            'prompt': 'Write the filter that matches people but not computers.',
            'answer': '(&(objectCategory=person)(objectClass=user))',
            'teach': 'objectClass=user alone includes every machine account, which is why the user count always looks too high.',
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
            'teach': 'DONT_REQ_PREAUTH. Each of these hands an offline crackable artefact to anyone who asks, with no credentials.',
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
        {
            'id': 'sad-ldap-b64',
            'type': 'command',
            'prompt': 'Decode the base64 LDIF value UGFzc3dvcmQx.',
            'answer': 'echo UGFzc3dvcmQx | base64 -d',
            'teach': 'A double colon in LDIF means the value is base64. In a description field it is worth every keystroke.',
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
        {
            'id': 'sac-ldif-parse',
            'title': 'Turn raw LDIF into a clean list of names',
            'goal': 'Take the output of a real query and produce the sorted, lowercased, deduplicated account list every other tool will want.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {
                    'ldap.raw': (
                        'dn: CN=Alice,OU=Staff,DC=corp,DC=local\n'
                        'sAMAccountName: Alice\n'
                        '\n'
                        'dn: CN=Bob,OU=Staff,DC=corp,DC=local\n'
                        'samaccountname: bob\n'
                        '\n'
                        'dn: CN=Alice2,OU=Staff,DC=corp,DC=local\n'
                        'SAMAccountName: ALICE\n'
                        '\n'
                        'dn: CN=Carol,OU=Staff,DC=corp,DC=local\n'
                        'samAccountName: carol\n'
                    ),
                },
            },
            'solution': {
                'shell': "grep -i '^samaccountname:' ldap.raw | awk '{print tolower($2)}' | sort -u > names.txt",
            },
            'steps': [
                {
                    'instruction': 'Select the samAccountName lines. The server has sent the attribute name in three different cases, so match without regard to case.',
                    'hint': 'grep -i',
                },
                {
                    'instruction': 'Take the value after the colon and lowercase it.',
                    'hint': "awk '{print tolower($2)}'",
                },
                {
                    'instruction': 'Sort and remove duplicates into names.txt.',
                    'hint': 'sort -u',
                },
            ],
            'free': 'Produce names.txt: one lowercased account name per line, sorted, no duplicates.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_equals': {
                        'names.txt': 'alice\nbob\ncarol\n',
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
        {
            'id': 'saq-dn-order',
            'type': 'mcq',
            'prompt': 'In CN=Alice,OU=Staff,DC=corp,DC=local, which part is the domain?',
            'answer': 'DC=corp,DC=local, at the right-hand end.',
            'distractors': [
                'CN=Alice, since the entry names its own domain.',
                'OU=Staff, since organisational units are domains.',
                'The whole string, since a DN is a domain name.',
            ],
            'teach': 'A DN is written leaf first and read right to left, like a postal address with the country last.',
        },
        {
            'id': 'saq-anon',
            'type': 'mcq',
            'prompt': 'An anonymous bind is refused. What does that tell you?',
            'answer': 'Only that anonymous is refused. Authenticated reads are usually wide open.',
            'distractors': [
                'The directory is hardened and will not answer queries.',
                'LDAP is disabled and you should try the global catalog.',
                'Your base DN is wrong.',
            ],
            'teach': 'This is where people give up one step early. The lock is on the front door, not on the filing cabinets.',
        },
        {
            'id': 'saq-ldif-b64',
            'type': 'mcq',
            'prompt': 'An LDIF line reads `description:: UGFzc3dvcmQx`. What is the double colon telling you?',
            'answer': 'The value is base64 encoded.',
            'distractors': [
                'The attribute has two values.',
                'The attribute is a distinguished name reference.',
                'The value was truncated by the server.',
            ],
            'teach': 'The server encodes anything with leading spaces, newlines or non-ASCII. In a description field it is always worth decoding.',
        },
    ],
}
