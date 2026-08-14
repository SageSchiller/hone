"""gobuster: mode-first web and DNS discovery.

Its shape is that the mode comes first: dir for paths, dns for subdomains, vhost for virtual hosts. The response-signal thinking is the same as any discovery tool, and its flags (no-dot extensions, status show and blacklist) are what differ from ffuf. gobuster is not installed here, so its challenge is self-marked (D8). Scope: the tool, never the engagement.
"""

MODULE = {
    'id': 'gobuster',
    'title': 'gobuster',
    'group': 'Security',
    'blurb': 'Mode-first discovery: dir, dns and vhost, with status and extension flags.',
    'context': 'You are probing a web server or domain you have permission to test.',
    'needs': [
        'gobuster',
    ],
    'prereqs': [
        'curl',
        'bash',
    ],
    'adapter': None,
    'estimate': '2 hours',
    'order': 75,
    'lessons': [
        {
            'id': 'gob-what',
            'title': 'What gobuster is, and its modes',
            'concept': "gobuster is a fast content-discovery tool whose defining shape is that the **mode comes first**: `gobuster dir` brute-forces paths, `gobuster dns` enumerates subdomains, `gobuster vhost` finds virtual hosts, and there are others. Where ffuf has one placeholder you move around, gobuster has one position per mode, which some people find simpler to reason about.\n\nThe idea underneath is the same as any discovery tool: take words from a list, ask the server for each, and read what comes back. So the response-signal thinking, status codes, size, and the soft-404 problem, transfers directly, and the wordlist choice matters exactly as much.\n\nIts flags are less symmetrical than ffuf's: `-w` for the wordlist, `-x` for extensions without dots, `-s` and `-b` for status codes to show and to blacklist, `-t` for threads, `-k` to skip TLS verification. **Set one of `-s` or `-b`, never both**: current gobuster ships a `-b 404` blacklist by default, so adding `-s` on its own aborts before it scans, and you clear the blacklist with an empty `-b` to use a show-list instead. Hiding 404 is the modern default, and it is not the same as filtering by size.\n\nScope, as everywhere: probe only servers you own or are permitted to test.",
            'examples': [
                {
                    'label': 'The mode-first shape',
                    'code': 'gobuster dir  -u http://target -w words.txt -x php,html\ngobuster dns  -d target.com -w subs.txt\ngobuster vhost -u http://10.0.0.5 -w subs.txt --append-domain',
                    'note': 'Mode first, then the flags. Extensions take no leading dot, unlike ffuf.',
                },
                {
                    'label': 'Show the codes that matter',
                    'code': 'gobuster dir -u http://target -w words.txt \\\n  -s 200,204,301,302,307,401,403 -b ""',
                    'note': '401 and 403 belong on that list: both mean the path is really there. The -b "" clears the default 404 blacklist, which -s will not run alongside.',
                },
            ],
            'misconceptions': [
                'gobuster dir is not ffuf syntax. The mode comes first and the extension flag takes no dots.',
                'Hiding 404 is not the same as filtering a soft 404. If the app returns 200 for misses, a status filter shows you everything.',
                'The alternatives (feroxbuster, dirsearch) do the same job with different defaults. Switching tools sometimes fixes an awkward case faster than fighting flags.',
            ],
            'try_it': [
                'Run the same wordlist through gobuster dir and note how its output and defaults differ from ffuf on a target you own.',
            ],
            'next': 'wd-gobuster',
        },
        {
            'id': 'wd-gobuster',
            'title': 'Directories, dns and vhost modes',
            'concept': "gobuster takes a mode as its first argument, and that shape is the thing to remember: `gobuster dir` for paths, `gobuster dns` for subdomains, `gobuster vhost` for virtual hosts, `gobuster s3` and others besides. Where ffuf has one placeholder and many positions, gobuster has one position per mode.\n\nIts flags are less symmetrical than ffuf's: -w for the wordlist, -x for extensions without dots, -s and -b for status codes to show and to blacklist, -t for threads, -k to skip TLS verification, -o for output. Current gobuster defaults to a -b 404 blacklist, and -s and -b are mutually exclusive, so a bare -s aborts with a set-only-one error and you clear the blacklist with an empty -b first. Hiding 404 is a reasonable default and not the same as filtering by size.\n\nferoxbuster is the recursive one by default, written in Rust, and its recursion behaviour is genuinely better thought through than bolting -recursion onto a flat scan. dirsearch is the Python one with a good built-in wordlist and sensible defaults for someone who does not want to think about filters yet.\n\nAll of them do the same job. The reason to know more than one is that each has a different default behaviour on the awkward cases, TLS errors, redirects, rate limits, and switching tools is sometimes faster than fighting the one you started with.",
            'examples': [
                {
                    'label': 'gobuster, directories with extensions',
                    'code': 'gobuster dir -u http://target -w words.txt -x php,html -t 20',
                    'note': 'Mode first. Extensions without leading dots, unlike ffuf.',
                },
                {
                    'label': 'gobuster, virtual hosts',
                    'code': 'gobuster vhost -u http://target -w subdomains.txt --append-domain',
                    'note': 'A different mode rather than a different flag position.',
                },
                {
                    'label': 'Show only the codes you care about',
                    'code': 'gobuster dir -u http://target -w words.txt -s 200,204,301,302,307,401,403 -b ""',
                    'note': '401 and 403 belong on that list: they mean the path is there. Without the empty -b, gobuster refuses to run -s at all.',
                },
                {
                    'label': 'feroxbuster, recursive by default',
                    'code': 'feroxbuster -u http://target -w words.txt -d 2',
                    'note': 'Recursion is the design rather than an option, and -d bounds it.',
                },
            ],
            'misconceptions': [
                'gobuster dir is not interchangeable with ffuf syntax. The mode comes first and the extension flag takes no dots.',
                'Hiding 404 is not the same as filtering a soft 404. If the app returns 200 for misses, a status filter shows you everything.',
                'Switching tools does not find different paths by magic. It changes the defaults, which sometimes is the fix.',
            ],
            'try_it': [
                'Run the same wordlist through ffuf and gobuster against a target you own and compare the output.',
                'Add 401 and 403 to the shown status codes and see what appears that was hidden.',
            ],
            'next': None,
        },
    ],
    'drills': [
        {
            'id': 'wdd-gobuster-dir',
            'type': 'command',
            'prompt': 'Use gobuster to find directories on http://target with words.txt.',
            'answer': 'gobuster dir -u http://target -w words.txt',
            'teach': 'The mode comes first. gobuster has one position per mode where ffuf has one placeholder anywhere.',
        },
        {
            'id': 'wdd-gobuster-x',
            'type': 'command',
            'prompt': 'Run gobuster on http://target also trying php and html files.',
            'answer': 'gobuster dir -u http://target -w words.txt -x php,html',
            'teach': 'No leading dots here, unlike ffuf. A small difference that costs everyone one confused run.',
        },
        {
            'id': 'wdd-gobuster-status',
            'type': 'command',
            'prompt': 'Run gobuster on http://target showing 200, 301, 401 and 403.',
            'answer': 'gobuster dir -u http://target -w words.txt -s 200,301,401,403 -b ""',
            'teach': '401 and 403 belong on the list: both mean the path is really there. -s and -b are mutually exclusive and -b defaults to 404, so clear it with -b "" or gobuster aborts.',
        },
        {
            'id': 'wdd-gobuster-vhost',
            'type': 'command',
            'prompt': 'Use gobuster to find virtual hosts on http://10.0.0.5.',
            'answer': 'gobuster vhost -u http://10.0.0.5 -w subs.txt',
            'teach': 'Varies the Host header, never asks DNS, which is why it finds hosts with no public record.',
        },
        {
            'id': 'wdd-gobuster-dns',
            'type': 'command',
            'prompt': 'Use gobuster to enumerate subdomains of target.com.',
            'answer': 'gobuster dns -d target.com -w subs.txt',
            'teach': 'A DNS question, not an HTTP one. It misses anything without a public record.',
        },
        {
            'id': 'wdd-feroxbuster',
            'type': 'command',
            'prompt': 'Scan http://target with feroxbuster to a depth of two.',
            'answer': 'feroxbuster -u http://target -w words.txt -d 2',
            'teach': 'Recursion is the design here rather than an added flag, which shows in how it schedules requests.',
        },
    ],
    'challenges': [
        {
            'id': 'gobc-run',
            'title': 'Run gobuster against a target you own',
            'goal': 'gobuster is not installed here, so this is on a lab you own: discover paths, then subdomains, and read the signals.',
            'setup': {
                'kind': 'self',
            },
            'steps': [
                {
                    'instruction': 'Stand up a small web server you own, or use a lab you have permission for.',
                    'hint': 'python3 -m http.server 8000',
                },
                {
                    'instruction': 'Run gobuster dir with a small wordlist and extensions, and read which codes come back.',
                    'hint': 'gobuster dir -u http://127.0.0.1:8000 -w words.txt -x txt,html',
                },
                {
                    'instruction': 'Add 401 and 403 to the shown codes and note what appears that was hidden.',
                },
                {
                    'instruction': 'On a domain you own, try gobuster dns for subdomains, and gobuster vhost, and note that they find different things.',
                },
            ],
            'free': 'On a target you own: run gobuster dir with extensions and a status filter, then compare gobuster dns and vhost.',
            'verify': {
                'kind': 'self',
            },
            'fallback': 'self',
        },
    ],
    'quiz': [
        {
            'id': 'wdq-gobuster-x',
            'type': 'mcq',
            'prompt': 'How does gobuster want extensions written, compared with ffuf?',
            'answer': "Without leading dots: -x php,html against ffuf's -e .php,.html.",
            'distractors': [
                'With leading dots, the same as ffuf.',
                'One -x flag per extension.',
                'As a wordlist file rather than a flag.',
            ],
            'teach': 'A tiny difference that costs everyone exactly one confused run, which is why it is worth drilling.',
        },
        {
            'id': 'gobq-mode',
            'type': 'mcq',
            'prompt': 'You want to enumerate subdomains that resolve in DNS. Which gobuster mode?',
            'answer': 'gobuster dns, which queries DNS rather than making HTTP requests.',
            'distractors': [
                'gobuster dir, with a subdomain wordlist.',
                'gobuster vhost, which varies the Host header.',
                'gobuster s3.',
            ],
            'teach': 'dns resolves names; vhost varies the Host header and finds hosts with no public DNS record. They answer different questions.',
        },
        {
            'id': 'gobq-403',
            'type': 'mcq',
            'prompt': 'Why add 401 and 403 to the shown status codes?',
            'answer': 'Both usually mean the path exists but access is restricted, which is more informative than a 404.',
            'distractors': [
                'They are needed for gobuster to run.',
                'They speed up the scan.',
                'They are the only codes dns mode returns.',
            ],
            'teach': 'A 403 says the path is real and you are not allowed in, which is often the interesting result.',
        },
    ],
}
