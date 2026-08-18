"""curl: fetching URLs and sending requests from the shell.

The HTTP swiss army knife, split into its two halves. First fetching: reading headers with -I, following redirects with -L, saving bodies, and the -sS pair that scripts need. Then sending: -d for bodies, -H for headers including the content type curl will not guess, -u for auth and -F for uploads, which together reproduce almost any request a browser makes.

The practice verifies for real without breaking D1: the trainer serves a small site on loopback and reads back what you fetched, so the curl challenges run against a real HTTP server that never leaves the machine. The one live-internet exercise is marked self.
"""

MODULE = {
    'id': 'curl',
    'title': 'curl',
    'group': 'Network',
    'blurb': 'Fetching with -I, -L and -o, and sending with -d, -H, -u and the write-out format.',
    'context': 'You are at a shell speaking HTTP to a server, local or remote.',
    'needs': [
        'curl',
    ],
    'prereqs': [
        'linux',
    ],
    'adapter': 'weblab',
    'estimate': '2-3 hours',
    'order': 53,
    'lessons': [
        {
            'id': 'curl-http',
            'title': 'A request, a response, and nothing else',
            'next': 'curl-basics',
            'concept': (
                'curl is how you speak HTTP from the shell and see the raw '
                'request and reply. That is why it is the tool for finding '
                'out what a server actually said, rather than what a browser '
                'decided to display. HTTP is one of the simplest protocols '
                'in wide use, and you can hold all of it in your head.\n\n'
                '**A client sends a request. A server sends a response. That '
                'is the entire protocol.** There is no session, no ongoing '
                'conversation and no memory: each request stands alone, which '
                'is why every login system has to invent cookies or tokens to '
                'fake continuity.\n\n'
                '**A request is a method, a path, some headers, and '
                'optionally a body.** The method is the verb: GET to fetch, '
                'POST to send, PUT to replace, DELETE to remove. The headers '
                'are metadata, one `Name: value` per line. The body is the '
                'payload, and a GET usually has none.\n\n'
                '**A response is a status code, some headers, and a body.** '
                'The code is three digits and the first one tells you the '
                'category: 2xx worked, 3xx go somewhere else, 4xx you got it '
                'wrong, 5xx the server got it wrong. The body is the page, '
                'the JSON, the image, whatever was asked for.\n\n'
                'A browser does this and then renders the result, which hides '
                'everything interesting. **curl does it and shows you the '
                'result**, which is why it is the tool for finding out what a '
                'server actually said rather than what a browser decided to '
                'display.'
            ),
            'examples': [
                {
                    'label': 'The whole protocol, on one screen',
                    'code': ('GET /index.html HTTP/1.1        <- request\n'
                             'Host: example.com\n'
                             'User-Agent: curl/8.5.0\n'
                             '\n'
                             'HTTP/1.1 200 OK                 <- response\n'
                             'Content-Type: text/html\n'
                             'Content-Length: 1256\n'
                             '\n'
                             '<html>...                       <- body'),
                    'note': 'A blank line separates headers from body, in '
                            'both directions. That blank line is the only '
                            'structure the format has.',
                },
                {
                    'label': 'Status codes, by first digit',
                    'code': ('2xx   it worked            200 OK\n'
                             '3xx   look somewhere else  301, 302\n'
                             '4xx   your fault           404, 403, 401\n'
                             '5xx   their fault          500, 502, 503\n'
                             '\n'
                             '404 is not found. 403 is found,\n'
                             'and you may not have it.'),
                    'note': 'The 403 versus 404 distinction is the one worth '
                            'internalising: a 403 is a positive statement '
                            'that something is there.',
                },
                {
                    'label': 'Seeing it happen',
                    'code': ('curl -v https://example.com\n'
                             '\n'
                             '> lines are what curl sent\n'
                             '< lines are what came back\n'
                             '* lines are curl talking to you'),
                    'note': 'Run this once on any site and read the whole '
                            'thing. Every other lesson here is a way of '
                            'controlling one of those lines.',
                },
            ],
            'misconceptions': [
                'HTTP has no concept of being logged in. Cookies and tokens '
                'are how applications fake a session over a protocol that '
                'forgets you between every request.',
                'A URL is not the whole request. The host, the path and the '
                'query string come from it; the method, the headers and the '
                'body do not.',
                '404 and 403 are not both "no". 404 says nothing is there; '
                '403 says something is there and you cannot have it, which is '
                'considerably more information.',
            ],
            'try_it': [
                'Run `curl -v https://example.com` and read every line, '
                'matching each to the request or response above.',
                'Find a URL that returns a 301 and one that returns a 404, '
                'and look at how little the bodies matter next to the codes.',
            ],
        },
        {
            'id': 'curl-basics',
            'title': 'curl: fetching a URL and reading the reply',
            'concept': 'curl speaks HTTP from the command line, and its first job is to fetch a URL and let you see exactly what came back. `curl URL` prints the body; the flags decide what else you see and where it goes.\n\nFour carry most of the weight. `-I` sends a HEAD request and prints only the response headers, which is how you check a status code or a redirect without pulling the whole body. `-L` follows redirects, which curl does not do by default, so an unexplained empty response is usually a 301 you never saw. `-o file` saves the body to a name you choose and `-O` reuses the name from the URL. And `-sS` together are the pair for scripts: silent progress, but still loud on a real error, where `-s` alone would hide the failure too.\n\nWhat that empty response actually looks like is worth seeing once. Without `-L`, a 301 is still a successful transfer: curl prints a short HTML body that says the page moved, or nothing at all, and exits 0. The Location header is sitting in the response you did not print. `-I` or `-v` is how you notice; `-L` is how you follow it.\n\nThe one to write out in full at least once is the status check: `curl -s -o /dev/null -w "%{http_code}\\n" URL`. It throws the body away and prints just the code, and `-w` can print far more than that, which the next lesson builds on.',
            'examples': [
                {
                    'label': 'The everyday forms',
                    'code': 'curl -I URL              headers only\ncurl -L URL              follow redirects\ncurl -o page.html URL    save to a named file\ncurl -sS URL             quiet, but still show errors\ncurl -v URL              show the whole request and reply\ncurl -k URL              skip certificate checks',
                    'note': '`-v` is the one to reach for when something is wrong: it prints the request line, every header sent and received, and the TLS handshake. `-sS` is the pair for scripts: silent progress, loud failures.',
                },
                {
                    'label': 'Just the status code',
                    'code': 'curl -s -o /dev/null -w "%{http_code}\\n" URL\n\n-s          no progress meter\n-o /dev/null   throw the body away\n-w          print chosen fields after the transfer',
                    'note': 'This is the line to check whether something is up from a script, and the basis for the write-out format later.',
                },
            ],
            'misconceptions': [
                'curl does not follow redirects on its own. Without `-L`, a 301 or 302 gives you the short redirect body and nothing else.',
                '`curl -k` does not fix a certificate problem, it ignores it. Fine for a five-second diagnosis, never in a script.',
                '`-o` and `-O` are different. Lowercase names the file yourself; uppercase takes the name from the URL path.',
            ],
            'try_it': [
                'Run `curl -I` against a site that redirects http to https and read the Location header, then add `-L` and watch it follow.',
            ],
            'next': 'curl-requests',
        },
        {
            'id': 'curl-requests',
            'title': 'Sending data: methods, headers and bodies',
            'concept': 'Fetching is half of curl. The other half is sending, and it is where curl becomes an API client you can drive from a script.\n\n`-d` sends a body and, by doing so, turns the request into a POST and sets the form content type. `-d @file` reads the body from a file, and `--data-urlencode` escapes a value that has special characters. `-H "Header: value"` adds or overrides one header and can be repeated, which is how you set an Authorization token or, crucially, the Content-Type: curl does not make a body JSON just because it looks like JSON, so you say so with a header. `-X` names the method explicitly when it is not GET or POST, PUT and DELETE and the rest.\n\nThe JSON miss is easy to overlook. A body that looks like JSON still goes out as `Content-Type: application/x-www-form-urlencoded` when you send it with `-d`. A picky API returns 400 or 415; a sloppy one stores the JSON string as a form field, and the body you posted is not the body it parsed. The header is what the server reads, not the braces.\n\nCookies are how a login survives the next request. `curl -c jar.txt` writes every `Set-Cookie` the server sent into a file. `curl -b jar.txt` sends that file back. A POST that looks like it worked and then a 302 to `/login` usually means the cookie was not stored: the login response set it, and the next request went out without it. `-c` and `-b` on the same jar keep the session across commands. `-b "name=value"` still works for a cookie you already know; the jar is for the ones the server invents.\n\nTwo more round it out. `-u user:pass` sends HTTP basic auth, and leaving the password off prompts for it so it stays out of your shell history. `-F` posts a real multipart form, which is what file uploads use, `-F "file=@photo.jpg"`. Between `-d`, `-H`, `-u` and `-F` you can reproduce almost any request a browser makes.',
            'examples': [
                {
                    'label': 'Posting data',
                    'code': 'curl -d "user=me&pw=secret" URL/login\ncurl -d @body.json -H "Content-Type: application/json" URL\ncurl --json @body.json URL      the one-flag shorthand\ncurl -X DELETE URL/item/42\ncurl -F "file=@report.pdf" URL/upload',
                    'note': '`-d` implies POST. The JSON content type is not automatic, so the explicit -H header is what the server reads. A recent curl also has `--json`, which sets the content type and accept header for you, but `-H` is the form that works on any version.',
                },
                {
                    'label': 'Headers and auth',
                    'code': 'curl -H "Authorization: Bearer TOKEN" URL\ncurl -u alice URL          prompts for the password\ncurl -b "session=abc" URL  send a cookie\ncurl -A "myclient/1.0" URL  set the user agent',
                    'note': 'Leaving the password off `-u` keeps it out of ps output and your history, and curl asks for it instead.',
                },
                {
                    'label': 'A cookie jar, write then send',
                    'code': 'curl -c jar.txt -d "user=me&pw=secret" URL/login\ncurl -b jar.txt URL/dashboard\n\n-c writes Set-Cookie into the file\n-b sends that file on the next request\n\na 302 back to /login means the cookie\nnever landed in the jar',
                    'note': 'Use the same jar for both flags. A login POST that redirects to /login is almost always a missing -c, not a wrong password.',
                },
            ],
            'misconceptions': [
                '`-d` does not send JSON by default. It sets the form content type, so a JSON API needs an explicit Content-Type header.',
                'Putting a password in `-u user:pass` on the command line leaves it in your shell history and in ps. Let curl prompt instead.',
                '`-d` already implies POST, so adding `-X POST` is redundant. Use `-X` only for the methods curl would not choose on its own.',
            ],
            'try_it': [
                'POST a small JSON body to a request-inspector service and read back exactly which headers and body it received.',
            ],
            'next': 'curl-measure',
        },
        {
            'id': 'curl-measure',
            'title': 'Measuring, retrying, and curl as an instrument',
            'concept': (
                'The last third of curl is not about fetching anything. It is '
                'about turning a request into a number you can act on, which '
                'is what makes it a monitoring and debugging tool rather than '
                'a downloader.\n\n'
                '**`-w` is the write-out format**, and it prints chosen '
                'fields after the transfer finishes. `%{http_code}` is the '
                'one everyone starts with, and the timing fields are the ones '
                'worth learning: `%{time_namelookup}`, `%{time_connect}`, '
                '`%{time_appconnect}` for the TLS handshake, '
                '`%{time_starttransfer}` for the first byte, and '
                '`%{time_total}`.\n\n'
                'Those five in one line tell you **which part is slow**, which '
                'is a different question from whether it is slow. Slow name '
                'lookup is DNS. A long gap before appconnect is TLS. A long '
                'gap before starttransfer with everything else fast is the '
                'application thinking, and no amount of network tuning will '
                'help.\n\n'
                '**Retries and timeouts turn a script from optimistic to '
                'correct.** `--retry 3` retries transient failures, '
                '`--max-time 10` caps the whole operation, and '
                '`--connect-timeout 5` caps only the connection phase. A '
                'script without at least `--max-time` will one day hang '
                'forever on a half-open socket and take your pipeline with '
                'it.\n\n'
                '**Two flags for when the network itself is the question.** '
                '`-x http://proxy:8080` routes everything through a proxy so '
                'you can watch it in something else. `--resolve '
                'host:443:10.0.0.5` pins a hostname to an address without '
                'touching DNS or /etc/hosts, which is how you test one '
                'backend behind a load balancer.'
            ),
            'examples': [
                {
                    'label': 'Where the time actually went',
                    'code': ('curl -s -o /dev/null -w "dns %{time_namelookup} '
                             'tcp %{time_connect} tls %{time_appconnect} '
                             'ttfb %{time_starttransfer} total %{time_total}\\n" '
                             'https://example.com'),
                    'note': 'Each number is cumulative from the start, so '
                            'subtract to get each phase. The gap that is '
                            'large is the thing to fix.',
                },
                {
                    'label': 'A request that cannot hang forever',
                    'code': ('curl -sS --max-time 10 --connect-timeout 5 \\\n'
                             '     --retry 3 --retry-delay 2 URL\n'
                             '\n'
                             '--max-time caps everything\n'
                             '--connect-timeout caps only the connect'),
                    'note': 'Any curl inside a cron job or a health check '
                            'wants these three. The default is to wait '
                            'patiently and indefinitely.',
                },
                {
                    'label': 'Talking to one specific backend',
                    'code': ('curl --resolve example.com:443:10.0.0.5 \\\n'
                             '     https://example.com/health\n'
                             '\n'
                             'right hostname, right TLS name,\n'
                             'the address you chose'),
                    'note': 'This is how you test one server behind a load '
                            'balancer without editing /etc/hosts and '
                            'forgetting you did.',
                },
                {
                    'label': 'Exit codes, for scripts',
                    'code': ('curl -sf URL || echo "request failed"\n'
                             '\n'
                             '-f makes an HTTP 404 or 500 a failure\n'
                             '   rather than a successfully fetched\n'
                             '   error page'),
                    'note': 'Without -f, curl exits 0 for a 500, because it '
                            'successfully retrieved the server\'s apology. -f '
                            'is what makes `||` behave.',
                },
            ],
            'misconceptions': [
                'curl does not fail on an HTTP error by default. A 500 is a '
                'successful transfer of an error page as far as the exit code '
                'is concerned, until you add `-f`.',
                'The timing fields are not durations, they are cumulative '
                'timestamps from the start of the request. Subtract '
                'consecutive ones to get each phase.',
                '`--retry` does not retry a 404. It retries transient '
                'failures, and a 404 is a perfectly clear permanent answer.',
            ],
            'try_it': [
                'Run the timing line against a site far away and a site '
                'nearby, and see which phase actually differs.',
                'Fetch a URL that 404s, with and without `-f`, and print `$?` '
                'each time.',
            ],
        },
    ],
    'drills': [
        {
            'id': 'rm-cmd-curl-i',
            'type': 'command',
            'answer': 'curl -I https://example.com',
            'prompt': 'Fetch only the response headers from a URL.',
            'teach': '-I sends HEAD, and some servers answer HEAD differently from GET. Use -sD - -o /dev/null when that difference matters.',
        },
        {
            'id': 'rm-cmd-curl-ss',
            'type': 'command',
            'answer': 'curl -sS https://example.com',
            'prompt': 'Fetch a URL quietly, but still show errors if it fails.',
            'teach': '-s alone hides real failures. The pair is what you want in a script.',
        },
        {
            'id': 'rm-cmd-curl-l',
            'type': 'command',
            'answer': 'curl -L https://example.com',
            'prompt': 'Fetch a URL, following any redirects.',
            'teach': 'curl does not follow redirects by default, which is why an unexplained empty response is usually a 301 you never saw.',
        },
        {
            'id': 'curld-v',
            'type': 'command',
            'answer': 'curl -v url',
            'prompt': 'Fetch url and show the request and response headers on stderr.',
            'teach': '-v is the debug view. > sent, < received, * about the connection.',
        },
        {
            'id': 'curld-f',
            'type': 'command',
            'answer': 'curl -f url',
            'prompt': 'Fetch url and fail the exit code on HTTP 4xx or 5xx.',
            'teach': 'Without -f, a 404 still exits 0. That is why || never runs.',
        },
        {
            'id': 'curld-o',
            'type': 'command',
            'answer': 'curl -o page.html https://example.com',
            'prompt': 'Save a URL body to a file you name.',
            'teach': '-o names the file; -O reuses the name from the URL path. Lowercase picks, uppercase takes.',
        },
        {
            'id': 'curld-header',
            'type': 'command',
            'answer': 'curl -H "Authorization: Bearer TOKEN" https://example.com',
            'prompt': 'Send a custom request header.',
            'teach': '-H adds one header and can be repeated, overriding the default curl would send for the same name.',
        },
        {
            'id': 'curld-post',
            'type': 'command',
            'answer': 'curl -d "user=me&pw=secret" https://example.com/login',
            'prompt': 'POST a form body to a URL.',
            'teach': '-d implies POST and sets the form content type. -d @file reads the body from a file.',
        },
        {
            'id': 'curld-json',
            'type': 'command',
            'answer': 'curl -H "Content-Type: application/json" -d @body.json https://example.com/api',
            'prompt': 'POST a JSON body with the content type set.',
            'teach': '-d does not choose JSON for you; the explicit Content-Type header is what the server actually reads.',
        },
        {
            'id': 'curld-code',
            'type': 'command',
            'answer': 'curl -s -o /dev/null -w "%{http_code}\\n" https://example.com',
            'prompt': 'Print only the HTTP status code of a URL.',
            'teach': '-w writes chosen variables after the transfer; -o /dev/null discards the body so only the code prints.',
        },
        {
            'id': 'curld-auth',
            'type': 'command',
            'answer': 'curl -u alice https://example.com',
            'prompt': 'Send basic auth, prompting for the password.',
            'teach': 'Leaving the password off -u keeps it out of ps and your shell history, and curl asks for it.',
        },
        {
            'id': 'curld-cookie-c',
            'type': 'command',
            'answer': 'curl -c jar.txt URL/login',
            'prompt': 'Save Set-Cookie headers from URL/login into jar.txt.',
            'teach': '-c writes the jar. Without it the next request has no session.',
        },
        {
            'id': 'curld-cookie-b',
            'type': 'command',
            'answer': 'curl -b jar.txt URL/dashboard',
            'prompt': 'Send the cookies stored in jar.txt to URL/dashboard.',
            'teach': '-b sends the jar. Use the same file -c wrote.',
        },
        {
            'id': 'curld-maxtime',
            'type': 'command',
            'answer': 'curl --max-time 10 URL',
            'prompt': 'Fetch URL, giving up after ten seconds.',
            'teach': 'Without --max-time a half-open socket hangs the pipeline.',
        },
        {
            'id': 'curld-w-total',
            'type': 'command',
            'answer': 'curl -s -o /dev/null -w "%{time_total}\\n" URL',
            'prompt': 'Print only the total transfer time for URL.',
            'teach': '-w prints after the transfer. time_total is the last of the cumulative clocks.',
        },
    ],
    'challenges': [
        {
            'id': 'curl-fetch-save',
            'title': 'Fetch, save, and read the status',
            'goal': 'Point curl at the practice site the trainer is serving, save what you get, and capture the status code the scriptable way.',
            'setup': {
                'kind': 'weblab',
            },
            'solution': {
                'shell': 'curl -s "$TARGET/" > index.html && curl -s "$TARGET/robots.txt" > robots.txt && curl -s -o /dev/null -w "%{http_code}\\n" "$TARGET/" > code.txt',
            },
            'steps': [
                {
                    'instruction': 'Save the site home page to index.html.',
                    'hint': 'curl -s "$TARGET/" > index.html',
                },
                {
                    'instruction': 'Save robots.txt, which lists paths the site would rather you did not crawl.',
                    'hint': 'curl -s "$TARGET/robots.txt" > robots.txt',
                },
                {
                    'instruction': 'Write just the status code of the home page to code.txt, throwing the body away.',
                    'hint': 'curl -s -o /dev/null -w "%{http_code}\\n" "$TARGET/"',
                },
            ],
            'free': 'Produce index.html and robots.txt from the served site, and code.txt holding the home page status code alone.',
            'verify': {
                'kind': 'weblab',
                'expect': {
                    'is_file': [
                        'index.html',
                        'robots.txt',
                        'code.txt',
                    ],
                    'file_contains': {
                        'index.html': 'hone lab',
                        'robots.txt': 'Disallow',
                        'code.txt': '200',
                    },
                    'requested': [
                        '/',
                        '/robots.txt',
                    ],
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'curl-cookie-jar',
            'title': 'Write the login, then the next request',
            'goal': 'A session is two curls and one jar. The trainer cannot '
                    'log you into a real site, so the check is the command '
                    'file.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {}},
            'solution': {
                'shell': (
                    "printf '%s\\n' "
                    "'curl -c jar.txt -d user=me URL/login' "
                    "'curl -b jar.txt URL/dashboard' "
                    '> session.sh'
                ),
            },
            'steps': [
                {'instruction': 'Write session.sh with two lines: store '
                                'cookies from a login POST, then fetch '
                                '/dashboard with that jar.',
                 'hint': 'curl -c jar.txt -d ... URL/login then curl -b jar.txt URL/dashboard'},
            ],
            'free': 'session.sh: -c on the login, -b on the next request, '
                    'same jar.txt.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_contains': {
                        'session.sh': ['-c jar.txt', '-b jar.txt',
                                       '/login', '/dashboard'],
                    },
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'curl-status-codes',
            'title': 'Tell present, forbidden and absent apart',
            'goal': 'Use the headers and status code to distinguish three kinds of response, which is the whole game in probing a site.',
            'setup': {
                'kind': 'weblab',
            },
            'solution': {
                'shell': 'curl -sI "$TARGET/" > root-headers.txt && curl -s -o /dev/null -w "%{http_code}\\n" "$TARGET/uploads/" > forbidden.txt && curl -s -o /dev/null -w "%{http_code}\\n" "$TARGET/nope-9x/" > missing.txt',
            },
            'steps': [
                {
                    'instruction': 'Save the home page response headers with a HEAD request to root-headers.txt.',
                    'hint': 'curl -sI "$TARGET/" > root-headers.txt',
                },
                {
                    'instruction': 'Record the status code of the uploads directory, which exists but is forbidden.',
                    'hint': 'curl -s -o /dev/null -w "%{http_code}\\n" "$TARGET/uploads/"',
                },
                {
                    'instruction': 'Record the status code of a path that is not there at all.',
                    'hint': 'a made-up path returns 404',
                },
                {
                    'instruction': 'Compare: 200 is here, 403 is here but off limits, 404 is not here. That difference is what a directory scanner filters on to tell real paths from missing ones.',
                },
            ],
            'free': 'Produce root-headers.txt, forbidden.txt holding 403, and missing.txt holding 404.',
            'verify': {
                'kind': 'weblab',
                'expect': {
                    'is_file': [
                        'root-headers.txt',
                        'forbidden.txt',
                        'missing.txt',
                    ],
                    'file_contains': {
                        'root-headers.txt': [
                            '200',
                            'text/html',
                        ],
                        'forbidden.txt': '403',
                        'missing.txt': '404',
                    },
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'curl-real-site',
            'title': 'Read a real site the same way',
            'goal': 'The lab only runs on this machine (loopback, the 127.0.0.1 address). Point the same commands at a site you use, where the trainer cannot follow.',
            'setup': {
                'kind': 'self',
            },
            'steps': [
                {
                    'instruction': 'Fetch the headers of a site that redirects, and find the Location line.',
                    'hint': 'curl -I http://example.com',
                },
                {
                    'instruction': 'Add -L and confirm curl follows the redirect to the final page.',
                    'hint': 'curl -sIL http://example.com',
                },
                {
                    'instruction': 'Print just the final status code with the write-out format.',
                    'hint': 'curl -s -o /dev/null -w "%{http_code}\\n" -L URL',
                },
            ],
            'free': 'On a real site: read its headers, follow a redirect with -L, and print the final status code alone.',
            'verify': {
                'kind': 'self',
            },
            'fallback': 'self',
        },
    ],
    'quiz': [
        {
            'id': 'curlq-ss',
            'type': 'mcq',
            'prompt': 'Why use curl -sS rather than -s in a script?',
            'answer': '-sS hides the progress meter but still prints real errors, while -s alone swallows the errors too.',
            'distractors': [
                '-sS is twice as fast because it skips buffering.',
                '-sS follows redirects and -s does not.',
                '-sS retries failed requests automatically.',
            ],
            'teach': 'Silent progress, loud failures. A -s-only script fails invisibly when the request does.',
        },
        {
            'id': 'curlq-redirect',
            'type': 'mcq',
            'prompt': 'curl returns almost nothing for a URL you know serves a page. Likely cause?',
            'answer': 'The URL redirects and curl did not follow it, so add -L.',
            'distractors': [
                'The server requires HTTP/2, which curl lacks.',
                'curl needs -k to read any https page.',
                'The body is compressed and needs --compressed.',
            ],
            'teach': 'curl does not follow redirects by default. The short body you got was the 301 itself.',
        },
        {
            'id': 'curlq-head',
            'type': 'mcq',
            'prompt': 'What does curl -I do?',
            'answer': 'Sends a HEAD request and prints only the response headers.',
            'distractors': [
                'Prints the request headers curl is sending.',
                'Ignores the body and saves the headers to a file.',
                'Shows verbose connection information like -v.',
            ],
            'teach': 'Handy for a status code or a redirect. Note some servers answer HEAD differently from GET.',
        },
        {
            'id': 'curlq-k',
            'type': 'mcq',
            'prompt': 'What does curl -k actually do about a bad certificate?',
            'answer': 'Nothing to fix it; it tells curl to ignore the validation failure and connect anyway.',
            'distractors': [
                'Installs the missing certificate into the trust store.',
                'Downgrades to http so the certificate does not matter.',
                'Fetches a fresh certificate from the server.',
            ],
            'teach': 'Fine for a quick diagnosis, never in a script. It disables the check that would catch an interceptor.',
        },
        {
            'id': 'curlq-json',
            'type': 'mcq',
            'prompt': 'You POST with -d @body.json but the API rejects it as not JSON. Why?',
            'answer': '-d sets the form content type, so JSON needs an explicit Content-Type: application/json header.',
            'distractors': [
                '-d cannot read from a file, only inline data.',
                'The file needs a .txt extension for curl to send it.',
                'You must add -X POST for JSON to work.',
            ],
            'teach': 'curl does not sniff the body type. Say it with -H, and -d already makes the request a POST.',
        },
    ],
}
