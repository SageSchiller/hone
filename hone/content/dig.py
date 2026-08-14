"""dig: reading the DNS, and finding out who answered.

DNS is the first rung of "can I reach it", and dig is how you ask it a precise question and read the whole reply. The module covers the query forms that matter, +short for a scriptable line and the record types beyond A, then the troubleshooting half: +trace to walk the delegation from the root and @server to pin which resolver answered, which is how you tell a broken record from a stale cache.

D1 forbids the trainer from touching a network, and DNS needs a resolver, so the practice here is honestly self-marked: the drills build the commands and the one challenge is a real lookup you run yourself. No packet is faked and none is checked.
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
    'adapter': None,
    'estimate': '1-2 hours',
    'order': 52,
    'lessons': [
        {
            'id': 'dig-basics',
            'title': 'dig: asking the DNS a precise question',
            'concept': 'dig looks up DNS records and prints them in full, and it is the tool to reach for over `nslookup` because it shows you exactly what it asked and exactly what came back. The bare form `dig example.com` prints a page; `dig +short example.com` prints just the answer, which is the form to build muscle memory for.\n\nDNS is more than names to addresses. The record TYPE decides what you get: `A` and `AAAA` are IPv4 and IPv6 addresses, `MX` names the mail servers, `NS` the nameservers, `TXT` holds SPF and verification strings, `CNAME` is an alias to another name, and `SOA` is the zone summary. You put the type at the end: `dig example.com MX`.\n\nTwo options earn their keep beyond `+short`. `-x ADDR` does the reverse lookup, turning an address back into a name without you writing the in-addr.arpa form by hand. And `dig +noall +answer` keeps the answer section with its types and TTLs while dropping the header and authority noise, which is the readable middle ground between the full page and the bare line.',
            'examples': [
                {
                    'label': 'The forms worth knowing',
                    'code': 'dig +short example.com          just the address\ndig example.com MX              the mail servers\ndig example.com TXT             SPF and tokens\ndig +noall +answer example.com  the answer, readably\ndig -x 1.1.1.1                  which name is that',
                    'note': 'The type goes at the end. With no type you get A records.',
                },
                {
                    'label': 'Reading an answer line',
                    'code': 'example.com.  276  IN  A  93.184.216.34\n\nname          TTL  class type value\nthe 276 is seconds left before the cache expires',
                    'note': 'The TTL is how long a resolver may keep the answer, which is why a change can take that long to be seen everywhere.',
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
            'concept': 'When a name resolves to the wrong thing, or resolves for you but not for someone else, the question is usually "who answered". dig has two tools for that, and between them they settle most DNS arguments.\n\n`dig +trace example.com` starts at the root servers and walks the delegation down, querying each level itself rather than asking your resolver. It shows the real chain from root to TLD to the zone\'s own nameservers, and because it bypasses every cache on the way, it shows the authoritative answer rather than whatever was remembered.\n\n`dig @SERVER example.com` asks one specific resolver. If a public resolver like 1.1.1.1 gives a different answer from your default, the problem is caching or split-horizon DNS rather than the record itself. That one comparison turns "the site is down" into "my resolver has a stale record", which is a completely different fix.\n\nThe habit to build: when DNS looks wrong, ask a second resolver before you touch anything, because half the time the record is fine and a cache is lying to you.',
            'examples': [
                {
                    'label': 'Where did that answer come from',
                    'code': 'dig +trace example.com      root -> TLD -> zone\ndig @1.1.1.1 example.com     ask a public resolver\ndig @8.8.8.8 example.com     and a second opinion\ndig NS example.com           who is authoritative',
                    'note': '+trace shows the delegation; @server pins who you asked. Disagreement between them is almost always caching.',
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
