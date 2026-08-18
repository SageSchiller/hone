"""dig: reading the DNS, and finding out who answered.

DNS is the first rung of "can I reach it", and dig is how you ask it a precise question and read the whole reply. The module covers the query forms that matter, +short for a scriptable line and the record types beyond A, then the troubleshooting half: +trace to walk the delegation from the root and @server to pin which resolver answered, which is how you tell a broken record from a stale cache.

D1 forbids the trainer from touching a network and DNS needs a resolver, so no
lookup here is ever performed by the trainer. That was read for a long time as
"therefore nothing can be checked", and it does not follow. **Most of what this
module teaches is reading, not asking**: pulling the A records out of an
answer, sorting mail exchangers by priority, and building an in-addr.arpa name
by hand are all offline skills, and they are the skills the live query was only
ever a delivery mechanism for. Those are sandbox-verified against a captured
answer. The one challenge that genuinely needs a resolver stays self-marked and
says so, which is D8 doing its job rather than a blanket surrender.
"""

MODULE = {
    'id': 'dig',
    'title': 'dig',
    'group': 'Network',
    'blurb': 'Record types, +short, reverse lookups, and tracing resolution from the root.',
    'context': 'You are at a shell asking the DNS what a name resolves to.',
    'needs': [
        'dig',
    ],
    'prereqs': [
        'linux',
    ],
    # Was None, on the reasoning that DNS needs a resolver and D1 forbids
    # touching one. Both halves of that are still true and neither implies
    # the module cannot check anything: reading an answer, extracting records
    # from it and building a reverse name are all offline skills, and they are
    # the skills the live lookups were only ever a delivery mechanism for. The
    # one challenge that genuinely needs a resolver stays self-marked and says
    # so, which is D8 working as intended rather than a blanket surrender.
    'adapter': 'sandbox',
    'estimate': '1-2 hours',
    'order': 52,
    'lessons': [
        {
            'id': 'dig-what',
            'title': 'What the DNS is, and who answers you',
            'next': 'dig-basics',
            'concept': (
                'Almost nothing you type is an address. `example.com` is a '
                'name, and something has to turn it into `93.184.215.14` '
                'before a single packet can go anywhere. That translation is '
                'the DNS, and dig is how you watch it happen.\n\n'
                '**The DNS is a distributed database with no single copy of '
                'anything.** It is arranged as a tree, read right to left: '
                '`www.example.com` is the root, then `com`, then `example`, '
                'then `www`. Each level knows only where to ask about the '
                'level below it, which is why no one machine has to hold the '
                'internet.\n\n'
                '**A lookup is a chain of delegations.** Your resolver asks a '
                'root server, which says "ask the com servers". It asks '
                'those, which say "ask example.com\'s own servers". It asks '
                'those, which finally answer. Four questions, and you '
                'experience it as none.\n\n'
                '**Almost every answer is cached, and that is where the pain '
                'lives.** Each record carries a TTL, a number of seconds it '
                'may be remembered. Change a record and the old value keeps '
                'being served by everything that cached it, for up to that '
                'long. This is why "it works for me" is a genuine and '
                'maddening state of affairs rather than someone being '
                'careless.\n\n'
                'So there are two questions dig answers, and they are '
                'different: **what does this name resolve to**, and **who told '
                'you that**. Most real DNS problems are the second one.'
            ),
            'examples': [
                {
                    'label': 'The tree, read right to left',
                    'code': ('www.example.com.\n'
                             ' |    |      |  |\n'
                             ' |    |      |  the root, usually unwritten\n'
                             ' |    |      the com TLD\n'
                             ' |    the domain someone registered\n'
                             ' a host, or anything the owner likes'),
                    'note': 'The trailing dot is the root, and it is really '
                            'there. dig prints it in every answer, which is '
                            'the first thing people find odd.',
                },
                {
                    'label': 'Who is actually involved',
                    'code': ('you  ->  your resolver  ->  root\n'
                             '                        ->  com\n'
                             '                        ->  example.com\n'
                             '\n'
                             'your resolver does the walking\n'
                             'and remembers the results'),
                    'note': 'Your resolver is usually your router or your ISP '
                            'or something like 1.1.1.1. It is the thing whose '
                            'memory you will end up blaming.',
                },
                {
                    'label': 'The record types worth knowing on day one',
                    'code': ('A      a name to an IPv4 address\n'
                             'AAAA   a name to an IPv6 address\n'
                             'CNAME  this name is really that name\n'
                             'MX     where mail for this domain goes\n'
                             'NS     which servers are authoritative\n'
                             'TXT    arbitrary text: SPF, DKIM, proofs'),
                    'note': 'A name can have several types at once. Asking '
                            'for one type and getting nothing does not mean '
                            'the name does not exist.',
                },
            ],
            'misconceptions': [
                'DNS is not a phone book you can read. There is no way to '
                'list every name in a domain, and the tree structure is what '
                'prevents it.',
                'A DNS change is not instant, and nothing you do makes it so. '
                'The TTL was chosen before you made the change, and it '
                'governs how long the old answer survives.',
                'Your resolver is not authoritative. It is repeating '
                'something it was told, possibly a while ago, which is '
                'exactly what makes `+trace` and `@server` useful.',
            ],
            'try_it': [
                'Run `dig example.com` with no other arguments and find the '
                'QUESTION and ANSWER sections in the output.',
                'Run the same query twice in a row and watch the TTL count '
                'down. That is your resolver\'s memory, ticking.',
            ],
        },
        {
            'id': 'dig-basics',
            'title': 'dig: asking the DNS a precise question',
            'concept': 'dig looks up DNS records and prints them in full, and it is the tool to reach for over `nslookup` because it shows you exactly what it asked and exactly what came back. The bare form `dig example.com` prints a page; `dig +short example.com` prints just the answer, which is the form to build muscle memory for.\n\nDNS is more than names to addresses. The record TYPE decides what you get: `A` and `AAAA` are IPv4 and IPv6 addresses, `MX` names the mail servers, `NS` the nameservers, `TXT` holds SPF and verification strings, `CNAME` is an alias to another name, and `SOA` is the zone summary. You put the type at the end: `dig example.com MX`.\n\nTwo options earn their keep beyond `+short`. `-x ADDR` does the reverse lookup, turning an address back into a name without you writing the in-addr.arpa form by hand. And `dig +noall +answer` keeps the answer section with its types and TTLs while dropping the header and authority noise, which is the readable middle ground between the full page and the bare line.\n\n`+short` is also the form that hides the finding. An empty line can mean NXDOMAIN (that name does not exist), or NODATA (NOERROR with no record of that type: the name exists, that type does not), or a timeout your resolver turned into nothing. The full page has a `status:` line that tells those apart. When `+short` is empty, drop it and read `status:` before you change anything else.\n\nA large answer over UDP comes back with the `TC` flag set, meaning truncated. `+short` hides that too, so the short form looks empty or cut off. Drop `+short`, look for `tc` in `flags:`, and ask again with `+tcp`.\n\nThat still leaves the second question from the first lesson: who told you that. The next lesson is `+trace` and `@server`, which is how a stale cache is told from a wrong record.',
            'examples': [
                {
                    'label': 'The forms worth knowing',
                    'code': 'dig +short example.com          just the address\ndig example.com MX              the mail servers\ndig example.com TXT             SPF and tokens\ndig +noall +answer example.com  the answer, readably\ndig -x 1.1.1.1                  which name is that',
                    'note': 'The type goes at the end. With no type you get A records.',
                },
                {
                    'label': 'Reading an answer line',
                    'code': 'example.com.  276  IN  A  203.0.113.10\n\nname          TTL  class type value\nthe 276 is seconds left before the cache expires\nclass is always IN in practice',
                    'note': 'The TTL is how long a resolver may keep the answer, which is why a change can take that long to be seen everywhere.',
                },
                {
                    'label': 'The two lines worth reading in full output',
                    'code': 'status: NOERROR   the question was answered\nstatus: NXDOMAIN  that name does not exist\nNOERROR + ANSWER: 0  NODATA: exists, not that type\n\nflags: qr rd ra tc   tc means truncated\ndig +tcp example.com TXT    same question over TCP\n\n;; SERVER: 1.1.1.1#53(1.1.1.1)\n   which resolver actually answered',
                    'note': 'NXDOMAIN and NODATA are different findings. An empty +short is a prompt to read status: and flags:, not a result.',
                },
            ],
            'misconceptions': [
                'dig +short and dig are the same query with different output. +short strips the type, TTL and everything but the record data.',
                'A name having no A record is not an error. It may have only AAAA, or only MX, and dig will show you which by asking for the type.',
                'dig reads /etc/resolv.conf for its resolver by default, so it can return a cached answer. `dig @1.1.1.1` asks someone else.',
            ],
            'try_it': [
                'Run `dig +short` for a site you use, then `dig` for the same name, and see how much the full output was hiding under one line.',
            ],
            'next': 'dig-trace',
        },
        {
            'id': 'dig-trace',
            'title': 'Tracing resolution and ruling out a cache',
            'concept': 'When a name resolves to the wrong thing, or resolves for you but not for someone else, the question is usually "who answered". dig has two tools for that, and between them they settle most DNS arguments.\n\n`dig +trace example.com` starts at the root servers and walks the delegation down, querying each level itself rather than asking your resolver. It shows the real chain from root to TLD to the zone\'s own nameservers, and because it bypasses every cache on the way, it shows the authoritative answer rather than whatever was remembered.\n\n`dig @SERVER example.com` asks one specific resolver. If a public resolver like 1.1.1.1 gives a different answer from your default, the problem is caching or split-horizon DNS rather than the record itself. That one comparison turns "the site is down" into "my resolver has a stale record", which is a completely different fix.\n\nThe disagreement is the whole finding. Your resolver still has hundreds of seconds of TTL left on the old address, so every application on this machine keeps going there, while 1.1.1.1 already has the new one. Waiting out the TTL, or flushing that one resolver, is the fix; editing the zone would change a record that is already right.\n\nThe habit to build: when DNS looks wrong, ask a second resolver before you touch anything, because half the time the record is fine and a cache is lying to you.',
            'examples': [
                {
                    'label': 'Where did that answer come from',
                    'code': 'dig +trace example.com      root -> TLD -> zone\ndig @1.1.1.1 example.com     ask a public resolver\ndig @8.8.8.8 example.com     and a second opinion\ndig NS example.com           who is authoritative',
                    'note': '+trace shows the delegation; @server pins who you asked. Disagreement between them is almost always caching.',
                },
                {
                    'label': 'When two resolvers disagree',
                    'code': 'dig +short example.com           203.0.113.10\ndig @1.1.1.1 +short example.com  203.0.113.40\ndig +trace example.com           walks to 203.0.113.40\n\nyour resolver is stale; the zone is not',
                    'note': 'The fix is the resolver that is wrong, or waiting out its TTL. Editing the zone would change a record that is already right.',
                },
            ],
            'misconceptions': [
                '+trace does not use your resolver, so its answer can differ from what your applications get. That difference is the finding, not a bug.',
                'A slow or partial +trace often means a firewall is dropping direct DNS to the root or TLD servers, not that the zone is broken.',
                'Flushing your local cache does not help if the stale record lives in your ISP resolver. Query a different resolver to prove where it is.',
            ],
            'try_it': [
                'Run `dig +trace` for a domain and follow it from the root dot down to the nameservers that actually hold the record.',
            ],
            'next': None,
        },
    ],
    'drills': [
        {
            'id': 'rm-cmd-dig',
            'type': 'command',
            'answer': 'dig +short example.com',
            'prompt': 'Resolve a name and print just the answer, not a page of it.',
            'teach': '+short prints just the record data, which is what a script wants. nslookup gives you an answer and hides the rest; dig shows the whole exchange, the question, the flags and the TTLs, which is what you need the day the answer is wrong.',
        },
        {
            'id': 'rm-cmd-digtrace',
            'type': 'command',
            'answer': 'dig +trace example.com',
            'prompt': 'Follow a name resolution from the root servers down, to see where the answer actually came from.',
            'teach': 'It queries each level itself instead of asking your resolver, so it shows the real delegation chain and bypasses every cache on the way.',
        },
        {
            'id': 'rm-cmd-digat',
            'type': 'command',
            'answer': 'dig @1.1.1.1 example.com',
            'prompt': 'Ask a specific resolver rather than your own, to rule out a stale cache.',
            'teach': 'If a public resolver gives a different answer from your default, the problem is caching or split-horizon DNS rather than the record itself.',
        },
        {
            'id': 'digd-mx',
            'type': 'command',
            'answer': 'dig example.com MX',
            'prompt': 'Look up the mail servers for a domain.',
            'teach': 'MX records name the mail exchangers and their priorities, and the lowest priority number is tried first.',
        },
        {
            'id': 'digd-reverse',
            'type': 'command',
            'answer': 'dig -x 1.1.1.1',
            'prompt': 'Find the name an address maps back to.',
            'teach': '-x builds the reverse in-addr.arpa query for you instead of making you reverse the octets by hand.',
        },
        {
            'id': 'digd-answer',
            'type': 'command',
            'answer': 'dig +noall +answer example.com',
            'prompt': 'Print only the answer section, keeping type and TTL.',
            'teach': '+short drops the type and TTL; +noall +answer keeps them while dropping the header and authority sections.',
        },
        {
            'id': 'digd-txt',
            'type': 'command',
            'answer': 'dig example.com TXT',
            'prompt': "Read a domain's TXT records, where SPF and tokens live.",
            'teach': 'TXT is where SPF policy, DKIM keys and domain-ownership proofs are published for anyone to read.',
        },
    ],
    'challenges': [
        {
            'id': 'dig-read-answer',
            'title': 'Read an answer somebody else captured',
            'goal': 'A saved dig answer with six records of four types in it. Pull each type out separately, which is the skill the live query was only ever delivering.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {
                    'dig.out': (
                        '; <<>> DiG 9.20.26 <<>> example.com ANY\n'
                        ';; global options: +cmd\n'
                        ';; Got answer:\n'
                        ';; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 41234\n'
                        ';; flags: qr rd ra; QUERY: 1, ANSWER: 6, AUTHORITY: 0\n'
                        '\n'
                        ';; QUESTION SECTION:\n'
                        ';example.com.\t\t\tIN\tANY\n'
                        '\n'
                        ';; ANSWER SECTION:\n'
                        'example.com.\t\t276\tIN\tA\t93.184.215.14\n'
                        'example.com.\t\t276\tIN\tA\t93.184.215.15\n'
                        'example.com.\t\t3600\tIN\tMX\t10 mail.example.com.\n'
                        'example.com.\t\t3600\tIN\tMX\t20 backup.example.com.\n'
                        'example.com.\t\t86400\tIN\tNS\tns1.example.com.\n'
                        'example.com.\t\t300\tIN\tTXT\t"v=spf1 include:_spf.example.com ~all"\n'
                        '\n'
                        ';; Query time: 24 msec\n'
                    ),
                },
            },
            'solution': {
                'shell': 'awk \'$4=="A" {print $5}\' dig.out | sort > addrs.txt && awk \'$4=="MX" {print $5, $6}\' dig.out | sort -n > mx.txt && awk \'$4=="TXT\" {print}\' dig.out > txt.txt',
            },
            'steps': [
                {
                    'instruction': 'Every answer line has the same five fields: name, TTL, class, type, value. The type is field four.',
                    'hint': 'awk \'{print $4}\' dig.out | sort -u',
                },
                {
                    'instruction': 'Write just the A record addresses, sorted, to addrs.txt.',
                    'hint': 'awk \'$4=="A" {print $5}\' dig.out | sort > addrs.txt',
                },
                {
                    'instruction': 'Write the MX records with their priorities to mx.txt, lowest priority first, since that is the one tried first.',
                    'hint': 'awk \'$4=="MX" {print $5, $6}\' dig.out | sort -n > mx.txt',
                },
                {
                    'instruction': 'Write the TXT record line to txt.txt. That one is an SPF policy.',
                },
            ],
            'free': 'From dig.out produce addrs.txt (the A record addresses), mx.txt (the mail exchangers, lowest priority first) and txt.txt (the TXT record).',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_equals': {'addrs.txt': '93.184.215.14\n93.184.215.15\n'},
                    'file_contains': {
                        'mx.txt': ['10 mail.example.com.', '20 backup.example.com.'],
                        'txt.txt': 'v=spf1',
                    },
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'dig-reverse-name',
            'title': 'Build the reverse names by hand, once',
            'goal': 'dig -x writes the in-addr.arpa name for you. Doing it manually once is what makes the reverse tree make sense rather than being a flag you copy.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {
                    'addrs.txt': '93.184.215.14\n8.8.4.4\n10.0.0.1\n',
                },
            },
            'solution': {
                'shell': "awk -F. '{print $4\".\"$3\".\"$2\".\"$1\".in-addr.arpa\"}' addrs.txt > reverse.txt",
            },
            'steps': [
                {
                    'instruction': 'A reverse lookup is an ordinary lookup of a name built from the address with the octets reversed, ending in in-addr.arpa.',
                },
                {
                    'instruction': 'So 1.2.3.4 becomes 4.3.2.1.in-addr.arpa. Work out why the reversal is necessary given how DNS names are read.',
                    'hint': 'DNS names go from most specific on the left to least specific on the right. Addresses go the other way.',
                },
                {
                    'instruction': 'Convert every line of addrs.txt into its reverse name, in order, into reverse.txt.',
                    'hint': "awk -F. '{print $4\".\"$3\".\"$2\".\"$1\".in-addr.arpa\"}' addrs.txt",
                },
            ],
            'free': 'Produce reverse.txt: one in-addr.arpa name per address in addrs.txt, in the same order.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_equals': {
                        'reverse.txt': '14.215.184.93.in-addr.arpa\n4.4.8.8.in-addr.arpa\n1.0.0.10.in-addr.arpa\n',
                    },
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'dig-investigate',
            'title': 'Walk a name from cache to root',
            'goal': 'DNS needs a resolver, so the trainer cannot check this. Run the lookup ladder against a real domain and read what each step tells you.',
            'setup': {
                'kind': 'self',
            },
            'steps': [
                {
                    'instruction': 'Resolve a domain you use with +short, then again with no options, and note what the full output added.',
                    'hint': 'dig +short example.com',
                },
                {
                    'instruction': 'Ask its MX and TXT records, and see what the domain publishes beyond an address.',
                    'hint': 'dig example.com MX',
                },
                {
                    'instruction': 'Query a public resolver and your default, and check they agree.',
                    'hint': 'dig @1.1.1.1 example.com',
                },
                {
                    'instruction': 'Trace the name from the root and watch the delegation hand off level by level.',
                    'hint': 'dig +trace example.com',
                },
            ],
            'free': 'Against a real domain: resolve it, read its MX and TXT, compare two resolvers, and trace it from the root.',
            'verify': {
                'kind': 'self',
            },
            'fallback': 'self',
        },
    ],
    'quiz': [
        {
            'id': 'digq-short',
            'type': 'mcq',
            'prompt': 'What does dig +short give you that plain dig does not?',
            'answer': 'Only the record data, with the type, TTL and header stripped away.',
            'distractors': [
                'A faster query that skips the resolver.',
                'The authoritative answer, bypassing the cache.',
                'Every record type at once instead of just A.',
            ],
            'teach': 'Same query, terser output. For type and TTL without the full page, use +noall +answer.',
        },
        {
            'id': 'digq-mx',
            'type': 'mcq',
            'prompt': "You want to know which servers receive a domain's mail. Which record type?",
            'answer': 'MX, which lists the mail exchangers and their priorities.',
            'distractors': [
                'A, since mail servers still need an address.',
                'TXT, where SPF records live.',
                'NS, the domain nameservers.',
            ],
            'teach': 'dig example.com MX. Lowest priority number is tried first.',
        },
        {
            'id': 'digq-trace',
            'type': 'mcq',
            'prompt': 'Why does dig +trace sometimes disagree with a plain dig?',
            'answer': '+trace queries from the root down and bypasses caches, so it shows the authoritative answer rather than a remembered one.',
            'distractors': [
                '+trace uses TCP, which returns fresher data.',
                '+trace queries IPv6 servers only.',
                'Plain dig ignores the answer section.',
            ],
            'teach': 'When they differ, a cache between you and the zone is holding an old record. That is the finding.',
        },
        {
            'id': 'digq-resolver',
            'type': 'mcq',
            'prompt': 'dig gives a stale answer. How do you tell if your resolver is at fault?',
            'answer': 'Query a different resolver with dig @1.1.1.1 and compare.',
            'distractors': [
                'Rerun dig until the answer changes.',
                'Add +short to force a fresh lookup.',
                'Reboot to clear the local cache.',
            ],
            'teach': 'By default dig uses the resolver in /etc/resolv.conf. Asking another one isolates a caching problem from a record problem.',
        },
    ],
}
