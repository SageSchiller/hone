"""gobuster: mode-first web and DNS discovery.

Its shape is that the mode comes first: dir for paths, dns for subdomains, vhost for virtual hosts. The response-signal thinking is the same as any discovery tool, and its flags (no-dot extensions, status show and blacklist) are what differ from ffuf. gobuster is not installed here, so anything that runs it is self-marked (D8). What is not self-marked is reading its output: splitting a results file by status code is the finding, the scan was only the typing, and that half is sandbox-verified. Scope: the tool, never the engagement.
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
    'adapter': 'sandbox',
    'estimate': '2 hours',
    'order': 80,
    'lessons': [
        {
            'id': 'gob-why',
            'title': 'Why guessing paths finds anything at all',
            'next': 'gob-what',
            'concept': (
                'Path guessing is how you find URLs a server will not list, '
                'by asking one name at a time and reading the status code. '
                'That is why `/admin`, `/.git`, and `/backup` turn up: they '
                'have boring names, and the only way to know they exist is '
                'to ask.\n\n'
                'That is the entire premise of content discovery. **You '
                'cannot list, so you guess**, one path per request, and read '
                'the status codes. It sounds hopeless and is not, because the '
                'things worth finding have boring names: `/admin`, `/backup`, '
                '`/.git`, `/api/v1`, `/uploads`, `/config.php.bak`. A '
                'wordlist of a few thousand such names finds an alarming '
                'amount.\n\n'
                '**The status code is the answer.** 200 means it is there. '
                '**403 means it is there and you may not have it**, which is '
                'often the more interesting result: the server has just '
                'confirmed something exists. 404 means nothing is there. 301 '
                'or 302 means look elsewhere, and where it points is a '
                'finding of its own.\n\n'
                'Two things complicate that and both are worth knowing before '
                'you start. Some servers return **200 for everything**, '
                'including nonsense paths, which makes every result a hit '
                'unless you filter by response size instead. And this is '
                '**loud**: thousands of requests, every one logged, all from '
                'your address. There is no quiet way to do it, only slower '
                'ways.\n\n'
                '`gobuster` is one of two tools this trainer covers for it. '
                '`ffuf` is the other, and they differ mostly in shape rather '
                'than capability. The next lesson is that shape, and why the '
                'mode comes first.'
            ),
            'examples': [
                {
                    'label': 'What the server will tell you',
                    'code': ('/admin      403   it exists, you may not\n'
                             '/backup     200   it exists, help yourself\n'
                             '/nonsense   404   nothing there\n'
                             '/old        301   go and look at /old/'),
                    'note': 'A 403 is a positive finding. The server has '
                            'confirmed the path is real in the act of '
                            'refusing you.',
                },
                {
                    'label': 'The baseline check, before anything else',
                    'code': ('curl -s -o /dev/null -w "%{http_code} '
                             '%{size_download}\\n" \\\n'
                             '  http://target/definitely-not-here-9f2a\n'
                             '\n'
                             '404 0     good, 404s are honest\n'
                             '200 1256  every path will "exist"'),
                    'note': 'Sixty seconds of this saves an hour of reading '
                            'a results file where everything is a hit and '
                            'nothing is.',
                },
                {
                    'label': 'What you are actually doing, per word',
                    'code': ('for word in wordlist:\n'
                             '    GET http://target/$word\n'
                             '    record the status and size\n'
                             '\n'
                             'gobuster does this several\n'
                             'thousand times a minute'),
                    'note': 'The tools are fast loops with good filtering. '
                            'You could write one in ten lines of bash, and '
                            'the curl lesson in the ffuf module does.',
                },
            ],
            'misconceptions': [
                'There is no way to list a web server\'s contents. If there '
                'were, none of these tools would exist.',
                'A 404 does not always mean nothing is there. A server can be '
                'configured to return 404 for things it simply does not want '
                'to discuss.',
                'Content discovery is not stealthy and cannot be made so. '
                'Every request is logged, and the only variable is how fast '
                'they arrive.',
            ],
            'try_it': [
                'Run the baseline check against any site you own and see '
                'whether its 404s are honest.',
                'Before running any tool, write down five paths you would '
                'guess by hand. That instinct is what a wordlist automates.',
            ],
        },
        {
            'id': 'gob-what',
            'title': 'What gobuster is, and its modes',
            'concept': "gobuster is how you run that guess with the mode first: `dir` for paths, `dns` for names, `vhost` for Host headers. That is why people reach for it when they want one position per job rather than a placeholder they have to move.\n\ngobuster is a fast content-discovery tool whose defining shape is that the **mode comes first**: `gobuster dir` brute-forces paths, `gobuster dns` enumerates subdomains, `gobuster vhost` finds virtual hosts, and there are others. Where ffuf has one placeholder you move around, gobuster has one position per mode, which some people find simpler to reason about.\n\nThe idea underneath is the same as any discovery tool: take words from a list, ask the server for each, and read what comes back. So the response-signal thinking, status codes, size, and the soft-404 problem, transfers directly, and the wordlist choice matters exactly as much.\n\nIts flags are less symmetrical than ffuf's: `-w` for the wordlist, `-x` for extensions without dots, `-s` and `-b` for status codes to show and to blacklist, `-t` for threads, `-k` to skip TLS verification. **Set one of `-s` or `-b`, never both**: current gobuster ships a `-b 404` blacklist by default, so adding `-s` on its own aborts before it scans, and you clear the blacklist with an empty `-b` to use a show-list instead. Hiding 404 is the modern default, and it is not the same as filtering by size.\n\nScope, as everywhere: probe only servers you own or are permitted to test.",
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
            'title': 'dns versus vhost',
            'concept': (
                '`gobuster dns` is how you ask a resolver which labels '
                'exist; `gobuster vhost` is how you ask one server which '
                'Host headers it answers. That is why the same wordlist '
                'produces two different findings: one misses names with no '
                'public record, the other misses names this box does not '
                'serve.\n\n'
                '`gobuster dns` asks a resolver. It takes a domain and a '
                'wordlist of labels, builds names like `dev.target.com`, '
                'and queries DNS. A name that resolves is a finding. A name '
                'with no public record is invisible here, because the '
                'resolver never heard of it. That is why an internal-only '
                'host never appears in a dns scan.\n\n'
                '`gobuster vhost` never asks DNS. It sends HTTP requests to '
                'one address and varies the Host header. The server chooses '
                'a site by that header. A name that is not in public DNS '
                'can still be a virtual host on the box, which is why vhost '
                'finds things dns cannot.\n\n'
                'The catch on vhost is the default site. Many Host values '
                'return the same page, because the server falls back when '
                'it does not recognise the name. Those hits all share one '
                'size. Filter on that size, the same way a soft 404 is '
                'filtered, or the result file is a list of names that all '
                'mean "the default vhost". `--exclude-length` is the '
                'control: note the size of a nonsense Host, then drop it.\n\n'
                'So: dns finds names the world can resolve. vhost finds '
                'names one server will answer for. Run both on the same '
                'wordlist when the question is what else lives here, '
                'because each misses what the other is built to see.'
            ),
            'examples': [
                {
                    'label': 'dns: ask the resolver',
                    'code': 'gobuster dns -d target.com -w subs.txt',
                    'note': 'A DNS question, not an HTTP one. It misses '
                            'anything without a public record.',
                },
                {
                    'label': 'vhost: vary the Host header',
                    'code': (
                        'gobuster vhost -u http://10.0.0.5 -w subs.txt '
                        '--append-domain\n'
                        '\n'
                        '# a nonsense Host returned size 1256, so drop it\n'
                        'gobuster vhost -u http://10.0.0.5 -w subs.txt '
                        '--append-domain \\\n'
                        '  --exclude-length 1256'
                    ),
                    'note': 'vhost never queries DNS. The default site is '
                            'the noise: one size, many names. Filter that '
                            'size or every word looks like a hit.',
                },
                {
                    'label': 'Same wordlist, different findings',
                    'code': (
                        'gobuster dns   -d target.com   -w subs.txt\n'
                        'gobuster vhost -u http://10.0.0.5 -w subs.txt '
                        '--append-domain\n'
                        '\n'
                        'dns:    names that resolve\n'
                        'vhost:  names this server answers for'
                    ),
                    'note': 'A name can appear in one list and not the '
                            'other. That difference is the reason both '
                            'modes exist.',
                },
            ],
            'misconceptions': [
                'gobuster dns does not send HTTP. It asks a resolver, so a '
                'name with no public record is invisible to it.',
                'gobuster vhost does not ask DNS. It varies the Host header '
                'against one address, which is why it finds hosts with no '
                'public record.',
                'A vhost hit the same size as a nonsense Host is the '
                'default site, not a new virtual host. Filter that size.',
            ],
            'try_it': [
                'On a domain you own, run gobuster dns and gobuster vhost '
                'on the same wordlist and note which names appear in only '
                'one of the two.',
                'Hit a host with a nonsense Host header, record the size, '
                'and re-run vhost with --exclude-length set to that size.',
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
            'id': 'gob-read-results',
            'title': 'Read a scan you did not run',
            'goal': 'A saved results file with three status codes in it. Split it by what each code means, because the sorting is the finding and the scan was only the typing.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {
                    'scan.out': (
                        '/admin                (Status: 403) [Size: 278]\n'
                        '/backup               (Status: 200) [Size: 1043]\n'
                        '/images               (Status: 301) [Size: 0] [--> /images/]\n'
                        '/index.html           (Status: 200) [Size: 1256]\n'
                        '/secret               (Status: 403) [Size: 278]\n'
                        '/uploads              (Status: 301) [Size: 0] [--> /uploads/]\n'
                    ),
                },
            },
            'solution': {
                'shell': "grep 'Status: 403' scan.out | awk '{print $1}' | sort > forbidden.txt && grep 'Status: 200' scan.out | awk '{print $1}' | sort > readable.txt && grep 'Status: 301' scan.out | awk '{print $1}' | sort > redirects.txt",
            },
            'steps': [
                {
                    'instruction': 'Put the paths that returned 403 into forbidden.txt, sorted. These exist and you may not have them, which is a positive finding.',
                    'hint': "grep 'Status: 403' scan.out | awk '{print $1}' | sort > forbidden.txt",
                },
                {
                    'instruction': 'Put the 200s into readable.txt. These you can simply fetch.',
                },
                {
                    'instruction': 'Put the 301s into redirects.txt. Where each one points is a finding of its own, and the file records it.',
                },
                {
                    'instruction': 'Note that the two 403s share a size of 278. Identical sizes usually mean one shared error page, which is worth knowing before you get excited.',
                },
            ],
            'free': 'From scan.out produce forbidden.txt, readable.txt and redirects.txt: the paths for status 403, 200 and 301, each sorted.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_equals': {
                        'forbidden.txt': '/admin\n/secret\n',
                        'readable.txt': '/backup\n/index.html\n',
                        'redirects.txt': '/images\n/uploads\n',
                    },
                },
            },
            'fallback': 'self',
        },

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
        {
            'id': 'gob-soft404',
            'title': 'Filter the 200s that are really misses',
            'goal': 'Every path returned 200. The miss size is 1256. Split the real pages from the ones that are just the soft 404.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {
                    'scan.out': (
                        '/admin                (Status: 200) [Size: 1256]\n'
                        '/api                  (Status: 200) [Size: 1256]\n'
                        '/backup               (Status: 200) [Size: 8912]\n'
                        '/index.html           (Status: 200) [Size: 1256]\n'
                        '/robots.txt           (Status: 200) [Size: 84]\n'
                        '/uploads              (Status: 200) [Size: 1256]\n'
                    ),
                },
            },
            'solution': {
                'shell': "grep 'Size: 1256' scan.out | awk '{print $1}' | sort > misses.txt && grep -v 'Size: 1256' scan.out | awk '{print $1}' | sort > real.txt",
            },
            'steps': [
                {
                    'instruction': 'The nonsense path in this scan came back 200 with size 1256. Put every path of that size into misses.txt, sorted.',
                    'hint': "grep 'Size: 1256' scan.out | awk '{print $1}' | sort > misses.txt",
                },
                {
                    'instruction': 'Put the 200s whose size is not 1256 into real.txt. Those are the pages that actually differ from the miss.',
                    'hint': "grep -v 'Size: 1256' scan.out | awk '{print $1}' | sort > real.txt",
                },
                {
                    'instruction': 'A status filter of 200 would have shown every line. Size is what separates a hit from a polite lie.',
                },
            ],
            'free': 'From scan.out produce misses.txt (paths of size 1256) and real.txt (the other paths), both sorted.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_equals': {
                        'misses.txt': '/admin\n/api\n/index.html\n/uploads\n',
                        'real.txt': '/backup\n/robots.txt\n',
                    },
                },
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
        {
            'id': 'gobq-sb',
            'type': 'mcq',
            'prompt': 'You add -s 200,403 to gobuster dir and it aborts. Why?',
            'answer': '-s and -b are mutually exclusive, and -b already defaults to 404.',
            'distractors': [
                '-s requires a wordlist passed with -w first.',
                '403 cannot be shown unless 401 is also listed.',
                'dir mode has no status filter; only vhost does.',
            ],
            'teach': 'Clear the default blacklist with an empty -b when you want a show-list. Setting only -s is the abort that looks like a bug.',
        },
    ],
}
