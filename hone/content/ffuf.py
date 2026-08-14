"""ffuf: web content discovery, built on one idea and one placeholder.

The model is that every response is a signal, and not only the status code: length, word count and redirect target separate a real path from a miss, and a site that returns 200 for everything is beaten by size filtering rather than a bigger wordlist. ffuf's own trick is that FUZZ is positional, so the same tool does directory discovery, parameter fuzzing and virtual-host discovery by moving where you put it. This module also teaches doing it by hand with curl, because that is how you understand what the fuzzer is doing for you.

Verified against a site the trainer serves on loopback (the weblab adapter): the challenges probe it with curl, which is installed, so they run for real. Scope: the tool, never the engagement.
"""

MODULE = {
    'id': 'ffuf',
    'title': 'ffuf',
    'group': 'Security',
    'blurb': 'The FUZZ placeholder, filtering by size/status/words, recursion and vhosts.',
    'context': 'You are probing a web server you have permission to probe.',
    'needs': [
        'ffuf',
    ],
    'prereqs': [
        'curl',
        'bash',
    ],
    'adapter': 'weblab',
    'estimate': '3-4 hours',
    'order': 79,
    'lessons': [
        {
            'id': 'wd-model',
            'title': 'Every response is a signal',
            'concept': 'Content discovery is a loop: take a word, build a URL, send a request, decide whether the answer means the path is there. The interesting part is entirely in the last step.\n\nThe status code is the obvious signal and the weakest one. 200 means found, 404 means not found, in theory. In practice plenty of applications return 200 with a "not found" page, or 302 to a login for everything, or 500 for anything unexpected. A tool that only understands status codes is blind on all three.\n\nThe other signals are what make the technique reliable. **Length** in bytes distinguishes a real page from a constant error page. **Word count** and **line count** do the same thing more robustly when the error page contains the path you requested, so its length varies slightly. **Redirect target** matters: everything redirecting to /login is uninteresting, and the one path redirecting to /admin/dashboard is not. **Response time** occasionally gives away a path that does real work.\n\nSo the working method is: send one request for a path you are confident does not exist, record what a miss looks like, and then filter that out. Everything left is worth reading.\n\n403 deserves its own note. Forbidden usually means the path is real and you are not allowed in, which makes it more interesting than 200 rather than less.',
            'examples': [
                {
                    'label': 'Establish what a miss looks like first',
                    'code': 'curl -s -o /dev/null -w "%{http_code} %{size_download}\\n" http://target/definitely-not-here-9f2a',
                    'note': 'One request. Now you know the code and the size to filter out.',
                },
                {
                    'label': 'The same idea inside a fuzzer',
                    'code': 'ffuf -u http://target/FUZZ -w words.txt -fs 4242',
                    'note': '-fs filters out that exact body size, which is what defeats a soft 404.',
                },
                {
                    'label': 'Status codes are not enough on their own',
                    'code': 'ffuf -u http://target/FUZZ -w words.txt -mc all -fs 4242',
                    'note': 'Match every code, filter by the size a miss actually returns. Measure that size first with one request to a path you know is absent: -fs 0 only hides empty replies, which is no help when every miss returns the same chunky page.',
                },
            ],
            'misconceptions': [
                '404 is not the only way to say not found. Soft 404s return 200 with an error page, and size filtering is the answer.',
                '403 is not a dead end. It usually means the path exists, which is more information than a 404.',
                'A bigger wordlist does not fix a bad filter. It makes the noise longer.',
            ],
            'try_it': [
                'Request a path you invented on a site you own, and record the status and size of the miss.',
                'Find a site that returns 200 for a nonsense path, and work out which signal separates it from a real page.',
            ],
            'next': 'wd-wordlists',
        },
        {
            'id': 'wd-wordlists',
            'title': 'Wordlists, and choosing a smaller one',
            'concept': "The wordlist is the input, and the instinct to reach for the largest one is usually wrong. A list of two million entries against a slow target is hours of requests to find what a curated list of a thousand would have found in a minute.\n\nThe lists people actually use come from SecLists, and the important ones are small: raft-small-directories, directory-list-2.3-small, common.txt from dirb. Start there, read the results, and escalate only when the small list comes back empty.\n\nExtensions matter as much as words. A path that returns 404 as /admin may be /admin.php or /admin.aspx, and every tool takes an extension list for exactly this. Choose them from what you already know about the stack: guessing .php against an ASP.NET site doubles the requests and finds nothing.\n\nTargeted beats generic. A wordlist built from the site itself, from words on its pages, from its JavaScript, from its sitemap, will find things no generic list contains, because the interesting paths on a bespoke application are named after that application's own concepts.\n\nAnd read robots.txt first, always. It is a list of paths the owner specifically did not want indexed, published deliberately, at a known location, for free.",
            'examples': [
                {
                    'label': 'The free list nobody reads first',
                    'code': 'curl -s http://target/robots.txt',
                    'note': 'Paths the owner named themselves. Also sitemap.xml and .well-known/security.txt.',
                },
                {
                    'label': 'Add extensions to every word',
                    'code': 'ffuf -u http://target/FUZZ -w words.txt -e .php,.txt,.bak',
                    'note': 'Multiplies requests by the number of extensions plus one, so choose them from what the stack is.',
                },
                {
                    'label': 'The gobuster equivalent',
                    'code': 'gobuster dir -u http://target -w words.txt -x php,txt,bak',
                    'note': 'Same idea, no leading dot, and gobuster wants the mode as the first argument.',
                },
                {
                    'label': 'Build a list from the site itself',
                    'code': 'curl -s http://target/ | grep -oE "[a-z0-9_-]{3,}" | sort -u > custom.txt',
                    'note': "Crude and effective. The application's own vocabulary is where its own paths come from.",
                },
            ],
            'misconceptions': [
                'The biggest wordlist is not the best one. It is the slowest one, and it usually finds the same things.',
                'Extensions are not free. Each one multiplies the number of requests you send.',
                'robots.txt does not stop anyone reading those paths. It is a request to crawlers, and a published list of what the owner considers sensitive.',
            ],
            'try_it': [
                'Fetch robots.txt from three sites you use and see what they list.',
                'Compare how long a 1,000 word list takes against a 20,000 word list on the same target.',
            ],
            'next': 'wd-ffuf',
        },
        {
            'id': 'wd-ffuf',
            'title': 'ffuf: FUZZ goes wherever you put it',
            'concept': "ffuf's one idea is that the placeholder is positional. You write FUZZ somewhere in the request and it substitutes each word there. That somewhere does not have to be the path.\n\nIn the path it is directory discovery. In a parameter name or value it is parameter fuzzing. In the Host header it is virtual host discovery. In a POST body it is form fuzzing, and in a Cookie or Authorization header it is whatever you are testing there. One tool, one concept, many jobs, which is why it displaced the single-purpose tools.\n\nThe matching and filtering flags come in pairs, and knowing that the m-flags and f-flags mirror each other is most of the syntax: -mc and -fc for status codes, -ms and -fs for size, -mw and -fw for words, -ml and -fl for lines, -mr and -fr for a regex on the body.\n\nTwo more matter in practice. -ac turns on autocalibration, where ffuf sends its own junk requests first and works out the filter for you, which is right often enough to be the default habit. And -recursion follows what it finds, with -recursion-depth to stop it running forever.\n\nRate control is not optional politeness. -t sets threads and -rate caps requests per second, and the default of 40 threads will knock over a small application.",
            'examples': [
                {
                    'label': 'Directory discovery, the basic form',
                    'code': 'ffuf -u http://target/FUZZ -w words.txt',
                    'note': 'FUZZ in the path. ffuf already matches only interesting codes by default, so a real 404 is hidden for you: the noise on a first run is soft-404s answering 200, which is what -fs is for.',
                },
                {
                    'label': 'Let it work out the filter itself',
                    'code': 'ffuf -u http://target/FUZZ -w words.txt -ac',
                    'note': 'Autocalibration sends junk requests first and filters what they return.',
                },
                {
                    'label': 'Virtual hosts, by moving FUZZ into a header',
                    'code': 'ffuf -u http://target/ -H "Host: FUZZ.target" -w subdomains.txt -fs 4242',
                    'note': 'Same tool, different position. Filter out the default site size or everything matches.',
                },
                {
                    'label': 'Follow what it finds',
                    'code': 'ffuf -u http://target/FUZZ -w words.txt -recursion -recursion-depth 2 -o found.json',
                    'note': 'Depth matters: unbounded recursion on a large site does not finish.',
                },
                {
                    'label': 'Be slower than the default',
                    'code': 'ffuf -u http://target/FUZZ -w words.txt -t 10 -rate 20',
                    'note': '40 threads is the default and is too much for a small application.',
                },
            ],
            'misconceptions': [
                'FUZZ is not a fixed part of the URL syntax. It is a placeholder you can put in a header, a body or a parameter just as easily.',
                'Autocalibration is not always right. It fails on a target whose error responses vary, and then it hides real results.',
                'The m-flags and f-flags are not alternatives to each other. You commonly use both, matching broadly and filtering the known noise.',
            ],
            'try_it': [
                'Run the same scan with and without -ac on a target with a soft 404.',
                'Move FUZZ from the path into a Host header and see the tool do a different job unchanged.',
            ],
            'next': 'wd-vhost',
        },
        {
            'id': 'wd-vhost',
            'title': 'Virtual hosts: the same address, different sites',
            'concept': 'One IP address commonly serves many sites, and the server chooses between them using the Host header the client sent. That means a site can exist on an address you can reach and be completely invisible to you unless you ask for it by name.\n\nThis is a genuinely different search from directory discovery, and people conflate them. Directory discovery asks "what paths does this site have". Virtual host discovery asks "what other sites live at this address".\n\nDNS subdomain enumeration is a third, related thing again: it asks what names exist, by resolving them, and it will miss any host that has no public DNS record. Virtual host fuzzing finds exactly those, because it never asks DNS anything: it connects to the address you already have and varies the header.\n\nThe filtering problem is the same as before and bites harder. Every wrong Host header returns the default site, so the default site\'s size is the filter, and without it every single word appears to match.',
            'examples': [
                {
                    'label': 'By hand, one name',
                    'code': 'curl -s -H "Host: dev.target" http://10.0.0.5/ | head',
                    'note': 'Connect to the address, ask for the name. No DNS involved at all.',
                },
                {
                    'label': 'Fuzz the header with ffuf',
                    'code': 'ffuf -u http://10.0.0.5/ -H "Host: FUZZ.target" -w subs.txt -fs 1234',
                    'note': 'Filter out the size of the default site, or everything matches.',
                },
                {
                    'label': 'gobuster has a mode for it',
                    'code': 'gobuster vhost -u http://10.0.0.5 -w subs.txt --append-domain',
                    'note': 'Different tool shape, same request.',
                },
                {
                    'label': 'DNS enumeration is the other question',
                    'code': 'gobuster dns -d target.com -w subs.txt',
                    'note': 'Finds names that resolve. Misses anything with no public record, which vhost fuzzing catches.',
                },
            ],
            'misconceptions': [
                'Virtual host discovery and subdomain enumeration are not the same. One varies a header, the other queries DNS, and they find different things.',
                'A vhost scan with no size filter is not a scan. Every wrong name returns the default site and looks like a hit.',
                'Finding a vhost does not mean it is meant to be private. Plenty of internal names are simply names.',
            ],
            'try_it': [
                'Send a curl request with a Host header for a name that does not exist and see what the default site returns.',
                'Compare a DNS enumeration and a vhost scan against a target you own, and note what each misses.',
            ],
            'next': 'wd-curl',
        },
        {
            'id': 'wd-curl',
            'title': 'Doing it by hand with curl',
            'concept': 'Every fuzzer is a loop around a request, and being able to write that loop is worth more than any single tool. It is how you work on a machine with nothing installed, how you handle a target that needs an unusual request the fuzzer cannot express, and how you actually understand what -fs is filtering.\n\nThe flag that makes curl into a measuring instrument is -w, the write-out format. It prints response metadata after the request: %{http_code}, %{size_download}, %{time_total}, %{redirect_url}, %{num_redirects}. Pair it with -o /dev/null and -s and you get one clean line of signal per request.\n\nThe rest is a shell loop over a wordlist, which is why this module has bash as a prerequisite. Ten lines gets you status and size per path, sorted, with the noise filtered by a grep -v.\n\nA few curl flags earn their place here permanently: -I for a HEAD request when you only need the headers, -L to follow redirects and -i to see them, -k to ignore certificate errors on a lab host, -H to set any header, and -x to route the whole thing through a proxy so you can watch it.',
            'examples': [
                {
                    'label': 'One request, one line of signal',
                    'code': 'curl -s -o /dev/null -w "%{http_code} %{size_download} %{url_effective}\\n" http://target/admin',
                    'note': 'The building block. Everything else is a loop around this.',
                },
                {
                    'label': 'The loop, which is the whole tool',
                    'code': 'while read w; do\n  curl -s -o /dev/null -w "%{http_code} $w\\n" "http://target/$w"\ndone < words.txt | grep -v "^404"',
                    'note': 'Filter the miss code, read what is left. This is ffuf without the parallelism.',
                },
                {
                    'label': 'Headers only',
                    'code': 'curl -sI http://target/admin',
                    'note': 'HEAD. Cheaper, and some servers answer it differently from GET, which is itself a signal.',
                },
                {
                    'label': 'Watch the redirect chain',
                    'code': 'curl -s -o /dev/null -w "%{http_code} -> %{redirect_url}\\n" http://target/admin',
                    'note': 'Where a path redirects to is often more interesting than that it redirects.',
                },
            ],
            'misconceptions': [
                'curl does not follow redirects by default. Without -L you see the 301 and nothing behind it, which is often what you want.',
                '-I sends HEAD, not GET, and a server may answer the two differently. Confirm anything surprising with a real GET.',
                'The -w format needs a trailing newline in the string. Without it the output runs together.',
            ],
            'try_it': [
                'Write a five line loop that reports status and size for every word in a small list.',
                'Use %{redirect_url} to find where a login redirect actually sends you.',
            ],
            'next': 'wd-manners',
        },
        {
            'id': 'wd-manners',
            'title': 'Rate, noise, and reading what you found',
            'concept': 'Content discovery is the loudest thing in this roster. A default ffuf run is forty concurrent requests, thousands of them, all with an obvious user agent, and it appears in every log the target has. Two consequences follow.\n\nFirst, it can break things. Small applications, anything on shared hosting, and anything with a database behind it can fall over under a fast scan. -t and -rate exist for that, and starting slow costs you minutes while starting fast can cost you the target.\n\nSecond, the results need reading rather than collecting. A list of two hundred 200s is not a finding. The questions worth asking of each result: is this a page or a directory listing, does it need authentication, is it a backup file, is it a different application on the same host, and does its existence tell you what the stack is.\n\nSave the output. Every tool has -o and a format flag, and the second scan of the same target is much more useful when you can diff it against the first.\n\nBackup and temporary files deserve their own pass, because they are the highest value finding per request: .bak, .old, .swp, .zip, .tar.gz, and the editor leftovers like index.php~ and .index.php.swp.',
            'examples': [
                {
                    'label': 'Slower than the default, deliberately',
                    'code': 'ffuf -u http://target/FUZZ -w words.txt -t 10 -rate 20 -o scan.json',
                    'note': 'Minutes slower. Much less likely to take a small site down.',
                },
                {
                    'label': 'Hunt the leftovers specifically',
                    'code': 'ffuf -u http://target/indexFUZZ -w suffixes.txt',
                    'note': 'FUZZ appended rather than replacing: .bak, .old, ~, .swp against a name you already found.',
                },
                {
                    'label': 'Keep the output and diff it later',
                    'code': 'ffuf -u http://target/FUZZ -w words.txt -o today.json -of json',
                    'note': 'The second scan of a target is worth far more with the first one saved.',
                },
            ],
            'misconceptions': [
                'A long list of results is not progress. Reading twenty results properly beats collecting two hundred.',
                'Rate limiting yourself is not only politeness. A scan that takes the target down ends the work.',
                'Finding a directory listing is not the same as finding a directory. The listing is the higher value result.',
            ],
            'try_it': [
                'Run a scan against a target you own with default threads and watch its load.',
                'Take a path you found and fuzz suffixes onto it looking for backups.',
            ],
            'next': None,
        },
    ],
    'drills': [
        {
            'id': 'wdd-ffuf-basic',
            'type': 'command',
            'prompt': 'Fuzz directories on http://target with words.txt.',
            'answer': 'ffuf -u http://target/FUZZ -w words.txt',
            'teach': 'FUZZ is a placeholder wherever you put it. In the path, this is directory discovery.',
        },
        {
            'id': 'wdd-ffuf-ext',
            'type': 'command',
            'prompt': 'Fuzz http://target with words.txt, also trying .php and .bak.',
            'answer': 'ffuf -u http://target/FUZZ -w words.txt -e .php,.bak',
            'teach': 'ffuf wants the leading dots. Each extension multiplies the request count.',
        },
        {
            'id': 'wdd-ffuf-fs',
            'type': 'command',
            'prompt': 'Fuzz http://target and filter out responses of 4242 bytes.',
            'answer': 'ffuf -u http://target/FUZZ -w words.txt -fs 4242',
            'teach': 'Size filtering is what defeats a soft 404 that returns 200 for everything.',
        },
        {
            'id': 'wdd-ffuf-fc',
            'type': 'command',
            'prompt': 'Fuzz http://target and filter out 404 and 403 responses.',
            'answer': 'ffuf -u http://target/FUZZ -w words.txt -fc 404,403',
            'teach': 'Filtering 403 is usually a mistake: it means the path exists and you are not allowed in.',
        },
        {
            'id': 'wdd-ffuf-mc',
            'type': 'command',
            'prompt': 'Fuzz http://target matching every status code.',
            'answer': 'ffuf -u http://target/FUZZ -w words.txt -mc all',
            'teach': 'Match everything and filter by size instead, when the app returns 200 for misses.',
        },
        {
            'id': 'wdd-ffuf-fw',
            'type': 'command',
            'prompt': 'Fuzz http://target filtering out responses with 42 words.',
            'answer': 'ffuf -u http://target/FUZZ -w words.txt -fw 42',
            'teach': 'Word count is steadier than byte size when the error page echoes the path you asked for.',
        },
        {
            'id': 'wdd-ffuf-ac',
            'type': 'command',
            'prompt': 'Fuzz http://target letting ffuf calibrate its own filter.',
            'answer': 'ffuf -u http://target/FUZZ -w words.txt -ac',
            'teach': 'It sends junk requests first and filters what they return. Wrong when error responses vary.',
        },
        {
            'id': 'wdd-ffuf-recursion',
            'type': 'command',
            'prompt': 'Fuzz http://target recursively, no deeper than two levels.',
            'answer': 'ffuf -u http://target/FUZZ -w words.txt -recursion -recursion-depth 2',
            'teach': 'Unbounded recursion on a large site does not finish. Always set the depth.',
        },
        {
            'id': 'wdd-ffuf-vhost',
            'type': 'command',
            'prompt': 'Fuzz virtual hosts on http://10.0.0.5 with subs.txt.',
            'answer': 'ffuf -u http://10.0.0.5/ -H "Host: FUZZ.target" -w subs.txt',
            'teach': 'The placeholder moves into a header. Same tool, entirely different question.',
        },
        {
            'id': 'wdd-ffuf-rate',
            'type': 'command',
            'prompt': 'Fuzz http://target with 10 threads and 20 requests per second.',
            'answer': 'ffuf -u http://target/FUZZ -w words.txt -t 10 -rate 20',
            'teach': 'The default 40 threads will knock over a small application.',
        },
        {
            'id': 'wdd-ffuf-out',
            'type': 'command',
            'prompt': 'Fuzz http://target saving JSON output to scan.json.',
            'answer': 'ffuf -u http://target/FUZZ -w words.txt -o scan.json -of json',
            'teach': 'The second scan of a target is worth much more when the first was saved.',
        },
        {
            'id': 'wdd-ffuf-post',
            'type': 'command',
            'prompt': 'Fuzz a POST body parameter value on http://target/login.',
            'answer': 'ffuf -u http://target/login -X POST -d "user=FUZZ" -w words.txt',
            'teach': 'FUZZ in the body. The placeholder goes wherever the question is.',
        },
        {
            'id': 'wdd-robots',
            'type': 'command',
            'prompt': 'Fetch the file where the owner lists paths they hid.',
            'answer': 'curl -s http://target/robots.txt',
            'teach': 'Free, published deliberately, at a known location, and almost nobody reads it first.',
        },
        {
            'id': 'wdd-curl-signal',
            'type': 'command',
            'prompt': 'Print only the status code and body size for http://target/admin.',
            'answer': 'curl -s -o /dev/null -w "%{http_code} %{size_download}\\n" http://target/admin',
            'teach': 'The building block of every fuzzer. -w turns curl into a measuring instrument.',
        },
        {
            'id': 'wdd-curl-head',
            'type': 'command',
            'prompt': 'Fetch only the response headers for http://target/admin.',
            'answer': 'curl -sI http://target/admin',
            'teach': 'Sends HEAD. Cheaper, and some servers answer it differently from GET, which is itself a signal.',
        },
        {
            'id': 'wdd-curl-redirect',
            'type': 'command',
            'prompt': 'Show where http://target/admin redirects to, without following.',
            'answer': 'curl -s -o /dev/null -w "%{redirect_url}\\n" http://target/admin',
            'teach': 'Where a path redirects is often more interesting than that it redirects.',
        },
        {
            'id': 'wdd-curl-follow',
            'type': 'command',
            'prompt': 'Fetch http://target/admin following any redirects.',
            'answer': 'curl -sL http://target/admin',
            'teach': 'curl does not follow by default, which is usually what you want during discovery.',
        },
        {
            'id': 'wdd-curl-host',
            'type': 'command',
            'prompt': 'Request http://10.0.0.5/ asking for the host dev.target.',
            'answer': 'curl -s -H "Host: dev.target" http://10.0.0.5/',
            'teach': 'Connect to the address, ask for the name. No DNS is consulted at all.',
        },
        {
            'id': 'wdd-curl-proxy',
            'type': 'command',
            'prompt': 'Send a request to http://target through a proxy on port 8080.',
            'answer': 'curl -s -x http://127.0.0.1:8080 http://target',
            'teach': 'How you put a request in front of an intercepting proxy to watch or modify it.',
        },
        {
            'id': 'wdd-curl-insecure',
            'type': 'command',
            'prompt': 'Fetch https://target ignoring certificate errors.',
            'answer': 'curl -sk https://target',
            'teach': 'Fine on a lab host with a self-signed certificate, and a habit worth not carrying elsewhere.',
        },
        {
            'id': 'wdd-curl-loop',
            'type': 'command',
            'prompt': 'Loop over words.txt requesting each path from http://target.',
            'answer': 'while read w; do curl -s -o /dev/null -w "%{http_code} $w\\n" "http://target/$w"; done < words.txt',
            'teach': 'This is ffuf without the parallelism. Writing it once is how the filter flags stop being magic.',
        },
        {
            'id': 'wdd-sitemap',
            'type': 'command',
            'prompt': 'Fetch the site map a server publishes for crawlers.',
            'answer': 'curl -s http://target/sitemap.xml',
            'teach': 'Alongside robots.txt and .well-known/security.txt, one of three free lists people forget to read.',
        },
    ],
    'challenges': [
        {
            'id': 'wdc-robots',
            'title': 'Read the free list first',
            'goal': 'Before fuzzing anything, collect what the server already tells you, and confirm one of those paths exists.',
            'setup': {
                'kind': 'weblab',
            },
            'solution': {
                'shell': 'curl -s "$TARGET/robots.txt" > robots.txt && curl -s -o /dev/null -w "%{http_code} /admin/\\n" "$TARGET/admin/" > admin-status.txt',
            },
            'steps': [
                {
                    'instruction': 'The target URL is in target.txt and in $TARGET. Fetch robots.txt and save it.',
                    'hint': 'curl -s "$TARGET/robots.txt" > robots.txt',
                },
                {
                    'instruction': 'Read the Disallow lines. Those are paths the owner named themselves.',
                },
                {
                    'instruction': 'Confirm one of them exists, saving the status code to admin-status.txt.',
                    'hint': 'curl -s -o /dev/null -w "%{http_code} /admin/\\n" "$TARGET/admin/" > admin-status.txt',
                },
            ],
            'free': 'Produce robots.txt from the target, and admin-status.txt showing the status code of a path it disallows.',
            'verify': {
                'kind': 'weblab',
                'expect': {
                    'requested': [
                        '/robots.txt',
                        '/admin',
                    ],
                    'file_contains': {
                        'robots.txt': 'Disallow',
                        'admin-status.txt': '200',
                    },
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'wdc-establish-miss',
            'title': 'Find out what a miss looks like',
            'goal': 'Send one request for a path that cannot exist, and record the status and size that every later filter will be built on.',
            'setup': {
                'kind': 'weblab',
            },
            'solution': {
                'shell': 'curl -s -o /dev/null -w "%{http_code} %{size_download}\\n" "$TARGET/definitely-not-here-9f2a" > miss.txt && curl -s -o /dev/null -w "%{http_code} %{size_download}\\n" "$TARGET/robots.txt" > hit.txt',
            },
            'steps': [
                {
                    'instruction': 'Request a nonsense path and record its code and body size into miss.txt.',
                    'hint': 'curl -s -o /dev/null -w "%{http_code} %{size_download}\\n" "$TARGET/nonsense" > miss.txt',
                },
                {
                    'instruction': 'Do the same for a path you know exists, into hit.txt.',
                    'hint': 'curl -s -o /dev/null -w "%{http_code} %{size_download}\\n" "$TARGET/robots.txt" > hit.txt',
                },
                {
                    'instruction': 'Compare the two. Those two numbers are what -fs and -fc are made of.',
                },
            ],
            'free': 'Produce miss.txt and hit.txt recording status code and body size for a path that does not exist and one that does.',
            'verify': {
                'kind': 'weblab',
                'expect': {
                    'file_contains': {
                        'miss.txt': '404',
                        'hit.txt': '200',
                    },
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'wdc-by-hand',
            'title': 'Be the fuzzer',
            'goal': 'Write the loop yourself, over a small wordlist, and read the three different answers the server gives.',
            'setup': {
                'kind': 'weblab',
            },
            'solution': {
                'shell': 'printf "admin\\nbackup\\nuploads\\nnothing-here\\n" > words.txt && while read w; do curl -s -o /dev/null -w "%{http_code} $w\\n" "$TARGET/$w/" >> results.txt; done < words.txt',
            },
            'steps': [
                {
                    'instruction': 'Write a four word list into words.txt: admin, backup, uploads and something that does not exist.',
                    'hint': 'printf "admin\\nbackup\\nuploads\\nnothing-here\\n" > words.txt',
                },
                {
                    'instruction': 'Loop over it, appending the status code and the word to results.txt.',
                    'hint': 'while read w; do curl -s -o /dev/null -w "%{http_code} $w\\n" "$TARGET/$w/" >> results.txt; done < words.txt',
                },
                {
                    'instruction': 'Read results.txt. You should have a 200, a 403 and a 404, and the 403 is the interesting one.',
                },
            ],
            'free': 'Produce results.txt with a status code per word from your own loop, including at least one 200, one 403 and one 404.',
            'verify': {
                'kind': 'weblab',
                'expect': {
                    'requested': [
                        '/admin',
                        '/uploads',
                    ],
                    'file_contains': {
                        'results.txt': [
                            '200 admin',
                            '403 uploads',
                            '404 nothing-here',
                        ],
                    },
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'wdc-forbidden',
            'title': 'Treat 403 as a finding',
            'goal': 'Show that a forbidden path and a missing path are different answers, and record why that matters.',
            'setup': {
                'kind': 'weblab',
            },
            'solution': {
                'shell': 'curl -s -o /dev/null -w "%{http_code} %{size_download}\\n" "$TARGET/uploads/" > forbidden.txt && curl -s -o /dev/null -w "%{http_code} %{size_download}\\n" "$TARGET/uploads-not-real/" > missing.txt && curl -sI "$TARGET/uploads/" > forbidden-headers.txt',
            },
            'steps': [
                {
                    'instruction': 'Record the status and size of /uploads/, which exists and is not for you.',
                    'hint': 'curl -s -o /dev/null -w "%{http_code} %{size_download}\\n" "$TARGET/uploads/" > forbidden.txt',
                },
                {
                    'instruction': 'Record the same for a path that simply does not exist, into missing.txt.',
                },
                {
                    'instruction': 'Fetch just the headers of the forbidden path into forbidden-headers.txt.',
                    'hint': 'curl -sI "$TARGET/uploads/" > forbidden-headers.txt',
                },
            ],
            'free': 'Produce forbidden.txt, missing.txt and forbidden-headers.txt, showing that 403 and 404 are different answers about different things.',
            'verify': {
                'kind': 'weblab',
                'expect': {
                    'file_contains': {
                        'forbidden.txt': '403',
                        'missing.txt': '404',
                        'forbidden-headers.txt': '403',
                    },
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'wdc-vhost',
            'title': 'Find the site that only answers to its own name',
            'goal': 'Reach a virtual host at an address you already have, by varying the Host header rather than asking DNS.',
            'setup': {
                'kind': 'weblab',
            },
            'solution': {
                'shell': 'curl -s "$TARGET/" > default.html && curl -s -H "Host: dev.hone.lab" "$TARGET/" > vhost.html && curl -s -H "Host: nope.hone.lab" "$TARGET/" > wrong.html',
            },
            'steps': [
                {
                    'instruction': 'Fetch the default site and save it as default.html.',
                    'hint': 'curl -s "$TARGET/" > default.html',
                },
                {
                    'instruction': 'Ask the same address for dev.hone.lab using a Host header, into vhost.html.',
                    'hint': 'curl -s -H "Host: dev.hone.lab" "$TARGET/" > vhost.html',
                },
                {
                    'instruction': 'Try a name that is not configured, into wrong.html, and note that it returns the default site. That is why size filtering matters for vhost scans.',
                },
            ],
            'free': 'Produce default.html, vhost.html for dev.hone.lab, and wrong.html for a name that is not configured.',
            'verify': {
                'kind': 'weblab',
                'expect': {
                    'is_file': [
                        'default.html',
                        'vhost.html',
                        'wrong.html',
                    ],
                    'file_contains': {
                        'vhost.html': 'virtual host',
                    },
                    'file_lacks': {
                        'wrong.html': 'virtual host',
                    },
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'wdc-filter',
            'title': 'Build the filter from what you measured',
            'goal': 'Take the size of a miss and use it to separate real paths from noise, the way a fuzzer does internally.',
            'setup': {
                'kind': 'weblab',
            },
            'solution': {
                'shell': 'miss=$(curl -s -o /dev/null -w "%{size_download}" "$TARGET/no-such-path-here") && echo "miss size: $miss" > filter.txt && printf "admin\\nbackup\\nghost\\nrobots.txt\\n" > words.txt && while read w; do sz=$(curl -s -o /dev/null -w "%{size_download}" "$TARGET/$w"); if [ "$sz" != "$miss" ]; then echo "$w $sz" >> found.txt; fi; done < words.txt',
            },
            'steps': [
                {
                    'instruction': 'Measure the body size of a path that does not exist and record it in filter.txt.',
                    'hint': 'miss=$(curl -s -o /dev/null -w "%{size_download}" "$TARGET/no-such-path-here")',
                },
                {
                    'instruction': 'Loop over a small wordlist, and write only the paths whose size differs, into found.txt.',
                    'hint': 'if [ "$sz" != "$miss" ]; then echo "$w $sz" >> found.txt; fi',
                },
                {
                    'instruction': 'That comparison is exactly what ffuf -fs does for you, and now it is not magic.',
                },
            ],
            'free': 'Produce filter.txt with the size of a miss, and found.txt listing only the words whose response size differed from it.',
            'verify': {
                'kind': 'weblab',
                'expect': {
                    'file_contains': {
                        'filter.txt': 'miss size:',
                        'found.txt': 'robots.txt',
                    },
                    'file_lacks': {
                        'found.txt': 'ghost',
                    },
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'wdc-own-target',
            'title': 'Point a real tool at a target you own',
            'goal': 'The lab is a toy. Stand something real up, or use a target you are allowed to test, and run an actual fuzzer against it.',
            'setup': {
                'kind': 'self',
            },
            'steps': [
                {
                    'instruction': 'Stand up a web server you own, or use a lab target you have permission for. Nothing else.',
                    'hint': 'python3 -m http.server 8000',
                },
                {
                    'instruction': 'Read robots.txt, sitemap.xml and .well-known/security.txt first.',
                },
                {
                    'instruction': 'Run ffuf or gobuster with a small wordlist and a rate limit, saving the output.',
                    'hint': 'ffuf -u http://127.0.0.1:8000/FUZZ -w words.txt -t 10 -rate 20 -o scan.json -of json',
                },
                {
                    'instruction': 'Establish the miss signature first and build a filter from it, rather than accepting the defaults.',
                },
                {
                    'instruction': 'Read every result and say what each one is: page, listing, backup, or another application.',
                },
            ],
            'free': 'Against a target you own or are permitted to test: read the published files, establish a miss signature, run a rate-limited scan with a real tool, and read the results rather than collecting them.',
            'verify': {
                'kind': 'self',
            },
            'fallback': 'self',
        },
    ],
    'quiz': [
        {
            'id': 'wdq-soft404',
            'type': 'mcq',
            'prompt': 'An application returns 200 with a "page not found" body for every wrong path. What separates real hits?',
            'answer': 'Response size or word count, filtered with -fs or -fw.',
            'distractors': [
                'A larger wordlist, so real paths outnumber the noise.',
                'Matching only 200 responses with -mc 200.',
                'Following redirects with -r so the real page appears.',
            ],
            'teach': 'Measure a miss first, then filter it. This is the single most common real situation in the technique.',
        },
        {
            'id': 'wdq-403',
            'type': 'mcq',
            'prompt': 'Your scan returns a 403 for /backup/. What does that suggest?',
            'answer': 'The path exists and access is denied, which makes it more interesting than a 404.',
            'distractors': [
                'The path does not exist and the server is misconfigured.',
                'Your requests are being rate limited.',
                'The path exists but only over HTTPS.',
            ],
            'teach': 'Filtering 403 out of your results is a common and expensive habit.',
        },
        {
            'id': 'wdq-fuzz-position',
            'type': 'mcq',
            'prompt': 'What makes ffuf able to do virtual host discovery as well as directory discovery?',
            'answer': 'FUZZ is positional, so it can go in a header instead of the path.',
            'distractors': [
                'A separate vhost mode, like gobuster has.',
                'The -H flag automatically enumerates hosts.',
                'It reads DNS records when given a domain.',
            ],
            'teach': 'One placeholder, many positions: path, header, body, parameter, cookie. That is the whole design.',
        },
        {
            'id': 'wdq-vhost-vs-dns',
            'type': 'mcq',
            'prompt': 'What does virtual host fuzzing find that DNS enumeration cannot?',
            'answer': 'Sites with no public DNS record, since it only varies a header.',
            'distractors': [
                'Sites on a different IP address from the one you have.',
                'Subdomains protected by a wildcard record.',
                'Sites that only accept HTTPS connections.',
            ],
            'teach': 'DNS enumeration asks what names resolve. vhost fuzzing asks what names this server answers to, which is a different set.',
        },
        {
            'id': 'wdq-extensions',
            'type': 'mcq',
            'prompt': 'What is the cost of adding four extensions to a 10,000 word scan?',
            'answer': 'Fifty thousand requests instead of ten thousand.',
            'distractors': [
                'Ten thousand requests, since extensions are tried in the same request.',
                'Fourteen thousand requests, one pass per extension.',
                'No extra requests, since the server answers with a directory listing.',
            ],
            'teach': 'Each word is tried bare and once per extension, so choose extensions from what you know the stack to be.',
        },
        {
            'id': 'wdq-curl-w',
            'type': 'mcq',
            'prompt': 'Which curl flag turns it into a measuring instrument for discovery?',
            'answer': '-w, the write-out format, printing things like %{http_code} and %{size_download}.',
            'distractors': [
                '-v, which shows the full request and response.',
                '-i, which includes the response headers in the output.',
                '-s, which suppresses the progress meter.',
            ],
            'teach': 'Pair it with -o /dev/null and -s and you get one clean line of signal per request.',
        },
        {
            'id': 'wdq-redirect',
            'type': 'mcq',
            'prompt': 'Does curl follow a 302 by default?',
            'answer': 'No. Without -L you see the redirect itself, which is usually what you want while discovering.',
            'distractors': [
                'Yes, and -L only controls how many hops.',
                'Yes for GET and no for HEAD.',
                'Only when the target is on the same host.',
            ],
            'teach': 'Where a path redirects to is frequently the finding, and %{redirect_url} prints it without following.',
        },
        {
            'id': 'wdq-autocalibrate',
            'type': 'mcq',
            'prompt': 'When does ffuf autocalibration mislead you?',
            'answer': "When the target's error responses vary, so the learned filter hides real results.",
            'distractors': [
                'When the wordlist is larger than the calibration sample.',
                'When the target returns 404 correctly.',
                'When recursion is enabled at the same time.',
            ],
            'teach': '-ac is a good default habit and not a substitute for measuring a miss yourself when something looks wrong.',
        },
        {
            'id': 'wdq-rate',
            'type': 'mcq',
            'prompt': 'Why start a scan with -t 10 -rate 20 rather than the defaults?',
            'answer': 'Forty concurrent threads can take a small application down, ending the work.',
            'distractors': [
                'Slower scans are less likely to appear in logs.',
                'Lower rates improve the accuracy of size filtering.',
                'The defaults ignore the wordlist order.',
            ],
            'teach': 'Starting slow costs minutes. Starting fast can cost the target, and a broken target teaches nobody anything.',
        },
    ],
}
