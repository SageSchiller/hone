"""hydra: online password guessing, which is a different game from offline cracking.

The one fact that shapes the whole tool is that the service sets the rate: lockouts, rate limits and logging mean a few guesses a minute, not billions a second. So the strategy inverts to spraying, a few likely passwords across many accounts. hydra's interface follows the protocol, and HTTP forms need you to name what a failure looks like.

Running it is self-marked (D8): it needs a live service you own, which the trainer cannot provide. Building the http-post-form string is not, and that is the part people actually get wrong, so it is sandbox-verified against a captured failure page. Scope, hard: only services you own or are permitted to test.
"""

MODULE = {
    'id': 'hydra',
    'title': 'hydra',
    'group': 'Security',
    'blurb': 'Online password guessing, spraying, and why the rate limit changes everything.',
    'context': 'You are guessing against a live service you are permitted to test.',
    'needs': [
        'hydra',
    ],
    'prereqs': [
        'linux',
        'ssh',
    ],
    'adapter': 'sandbox',
    'estimate': '2-3 hours',
    'order': 83,
    'lessons': [
        {
            'id': 'hyd-what',
            'title': 'Online guessing is a different game',
            'concept': (
                'hydra guesses passwords against a live service, and that '
                'one fact, live rather than offline, changes everything.\n\n'
                'Offline, a stolen hash file is yours. The only limit is '
                'hardware, measured in billions of guesses a second. Nothing '
                'on the far side notices, because there is no far side: the '
                'loop is local. A lockout policy does not apply. A CAPTCHA '
                'does not apply. The log is yours.\n\n'
                'Online, each guess is a real login attempt against a service '
                'that is still running. The rate is set by that service: '
                'lockouts after a handful of failures, rate limits, CAPTCHAs, '
                'alerting, and every attempt written to a log someone else '
                'reads. A few tries a minute is typical before something '
                'notices. That is not a slower version of offline cracking. '
                'It is a different activity, because the defender is in the '
                'loop.\n\n'
                'That inverts the strategy. Offline you throw millions of '
                'passwords at one hash. Online, the only shape that survives '
                'the limits is a few very likely passwords against many '
                'accounts, which is called spraying. It is rate management '
                'rather than a clever trick.\n\n'
                'hydra\'s interface is shaped by the protocol: `-l` or `-L` '
                'for the user or a user list, `-p` or `-P` for a password or '
                'a list, `-t` for parallel tasks, then the target and the '
                'service as `protocol://host`.\n\n'
                'Scope, hard here because it touches live services: only '
                'ones you own or are explicitly permitted to test. The next '
                'lesson is the command line, including the HTTP form case '
                'where hydra cannot see failure on its own.'
            ),
            'examples': [
                {
                    'label': 'Live versus offline, the rate',
                    'code': (
                        'offline:  john hashes.txt\n'
                        '          billions of guesses, nothing logs them\n'
                        '\n'
                        'online:   hydra -L users.txt -p "Season2026" '
                        '-t 4 -W 5 ssh://10.0.0.5\n'
                        '          one likely password, many accounts, slowly'
                    ),
                    'note': 'The offline tool never talks to the service. '
                            'hydra does, which is why a lockout policy '
                            'reshapes the command rather than slowing it.',
                },
                {
                    'label': 'The shape, and the spray',
                    'code': 'hydra -l admin -P passwords.txt ssh://10.0.0.5\n  many passwords, one user, one service\n\nhydra -L users.txt -p "Spring2026!" -t 4 -W 5 ssh://10.0.0.5\n  one password, many users, slowly: the online shape',
                    'note': 'Lowercase for a single value, uppercase for a list. -t sets how many tries run at once (the default is 16), so a low -t 4 with a -W wait is what keeps you slow, not -t itself.',
                },
            ],
            'misconceptions': [
                'Online guessing is not offline cracking with a network hop. The rate limit changes the entire strategy.',
                'A lockout policy does not stop guessing. It changes it from many passwords per account to one password across many accounts.',
                'A slower hydra is not an offline cracker on a bad link. The service is in the loop, which is why spraying is the shape that survives.',
            ],
            'try_it': [
                'On a service you own, find how many attempts you get before a lockout, and read a failed login response for the string that marks it.',
            ],
            'next': 'hyd-syntax',
        },
        {
            'id': 'hyd-syntax',
            'title': 'The command line, and the awkward part',
            'next': 'ck-defence',
            'concept': (
                'hydra\'s flags are how you write the guess: user, password, '
                'rate, and protocol; `http-post-form` is how you name what a '
                'failed web login looks like. That is why SSH is one line '
                'and a form login is three colon fields you measure.\n\n'
                '**The regular part.** Lowercase means one, uppercase means a '
                'list, and that pattern holds throughout: `-l admin` is one '
                'username, `-L users.txt` is a file of them. `-p` and `-P` do '
                'the same for passwords. `-t` sets parallel tasks and `-W` '
                'puts a wait between them, which is how you stay under a rate '
                'limit rather than discovering one.\n\n'
                'The target comes last, written `protocol://host`, and the '
                'protocol is what decides everything else. `ssh://10.0.0.5` '
                'needs nothing more. `ftp://`, `smb://`, `rdp://` and most of '
                'the fifty-odd others are the same: hydra knows what a '
                'failure looks like because the protocol says so.\n\n'
                '**Then there is HTTP, where it gets genuinely ugly**. '
                'A web login is not a protocol with a failure code. '
                'It is a form that returns a page, and a wrong password '
                'returns a perfectly successful HTTP 200 containing the words '
                '"invalid password". Nothing at the protocol level '
                'distinguishes success from failure, so **you have to tell '
                'hydra what failure looks like**.\n\n'
                'That is what the third field of `http-post-form` is: a string '
                'that appears on the failure page and not on the success '
                'page. Get it wrong and hydra reports every password as '
                'correct, or none.\n\n'
                '`hydra -U http-post-form` prints that module\'s syntax, which '
                'is how the colon fields are looked up rather than guessed. '
                '`-o found.txt` writes hits to a file so a '
                'disconnected terminal does not take the result with it. `-f` '
                'stops at the first valid pair on that host; `-F` stops the '
                'whole run, which only differs when `-M` is aiming at many '
                'hosts.'
            ),
            'examples': [
                {
                    'label': 'The regular case, which is most of them',
                    'code': ('hydra -l admin -P rockyou.txt ssh://10.0.0.5\n'
                             'hydra -L users.txt -p "Spring2026!" '
                             'smb://10.0.0.5\n'
                             '\n'
                             'lowercase = one, uppercase = a list'),
                    'note': 'One username against many passwords is the first '
                            'line. Many usernames against one password is the '
                            'second, and it is the one that survives a '
                            'lockout policy.',
                },
                {
                    'label': 'The HTTP form, taken apart',
                    'code': ('hydra -l admin -P words.txt 10.0.0.5 \\\n'
                             '  http-post-form '
                             '"/login:user=^USER^&pass=^PASS^:Invalid"\n'
                             '                  \\____/ \\______________/ '
                             '\\_____/\n'
                             '                   path      the body      what\n'
                             '                                          '
                             'failure\n'
                             '                                          looks '
                             'like'),
                    'note': '^USER^ and ^PASS^ are where hydra substitutes. '
                            'The three fields are separated by colons, which '
                            'is why a path containing a colon ruins your '
                            'evening.',
                },
                {
                    'label': 'Getting the failure string right, first',
                    'code': ('curl -s -d "user=x&pass=x" \\\n'
                             '     http://10.0.0.5/login | grep -i invalid\n'
                             '\n'
                             '  <p class="err">Invalid credentials</p>\n'
                             '\n'
                             'now you know what to put in field three'),
                    'note': 'Sixty seconds with curl before you start. Every '
                            'hour anyone has lost to hydra reporting nonsense '
                            'was this step skipped.',
                },
                {
                    'label': 'Staying under the limit on purpose',
                    'code': ('-t 4      four tasks at once, not sixteen\n'
                             '-W 5      wait 5 seconds between\n'
                             '-f        stop at the first valid pair\n'
                             '-V        show every attempt as it goes'),
                    'note': 'The default of sixteen parallel tasks is a good '
                            'way to lock out every account you were testing '
                            'and to appear in an alert while doing it.',
                },
                {
                    'label': 'Module help, extra guesses, and where hits go',
                    'code': ('hydra -U http-post-form\n'
                             '  that module\'s colon fields, from the tool\n'
                             '\n'
                             'hydra -l admin -P words.txt -e nsr \\\n'
                             '      -o found.txt -f ssh://10.0.0.5\n'
                             '\n'
                             '-e nsr   empty, same-as-login, login reversed\n'
                             '-o       write hits to a file\n'
                             '-f       stop this host; -F stops the whole run'),
                    'note': '-f and -F only differ with -M and several hosts. '
                            'On one target they stop at the same pair.',
                },
            ],
            'misconceptions': [
                'A wrong web login is not an HTTP error. It is usually a 200 '
                'with an error message in the page, which is exactly why '
                'hydra has to be told what failure reads like.',
                'The failure string is not a description of success. Give '
                'hydra a phrase that appears when the login *fails*, and it '
                'reports everything else as a hit.',
                'More parallel tasks do not mean faster results online. Past '
                'the service\'s tolerance they mean lockouts, alerts, and a '
                'result set you cannot trust.',
            ],
            'try_it': [
                'Against a lab login form, submit one deliberately wrong '
                'password with curl and pick out the phrase you would use as '
                'the third field.',
                'Write the full http-post-form string on paper before running '
                'anything. Counting the colons is the exercise.',
            ],
        },
        {
            'id': 'ck-defence',
            'title': 'Reading it backwards: what actually stops guessing',
            'concept': 'Everything above is also the argument for how to store and choose passwords, and it is worth stating explicitly because the popular advice is mostly wrong.\n\n**Storage.** Use argon2id, or bcrypt with a cost tuned so a hash takes a few hundred milliseconds on your hardware. Salt automatically, which every one of these does for you. Never MD5, never SHA-256 unsalted, never your own construction.\n\n**Choice.** Length beats complexity, because keyspace grows exponentially with length and only linearly with character set size. Four random words is stronger than eight random symbols and vastly easier to type. Complexity rules that force one uppercase, one digit and one symbol produce Password1! at scale, which is one rule in best64.\n\n**Reuse.** Credential stuffing is the highest yield attack there is and it does no cracking at all: it takes username and password pairs from one breach and tries them elsewhere. A password manager with unique passwords defeats it completely, and nothing else does.\n\n**Rotation.** Forced 90 day rotation makes people pick Summer2026 and then Autumn2026. Current guidance dropped it for exactly that reason: rotate on evidence of compromise, not on a calendar.\n\n**MFA** is the one that changes the calculation entirely, because a cracked password stops being sufficient.',
            'examples': [
                {
                    'label': 'Length against character set, arithmetic',
                    'code': '95^8  = about 6.6e15\n7776^4 = about 3.7e15   (four dice words)\n7776^6 = about 2.2e23   (six dice words)',
                    'note': 'Four words is already comparable to eight random symbols. Six is not close.',
                },
                {
                    'label': 'Generate something you did not choose',
                    'code': 'openssl rand -base64 24',
                    'note': 'A human choosing is the weak part. Removing the human is the fix.',
                },
                {
                    'label': 'Check exposure without sending the password',
                    'code': 'echo -n "hunter2" | sha1sum | tr a-z A-Z',
                    'note': 'The first five characters of that go to the range API, and the rest is compared locally.',
                },
            ],
            'misconceptions': [
                'Complexity requirements do not produce strong passwords. They produce predictable manglings of weak ones.',
                'Forced rotation makes passwords weaker, which is why current guidance dropped it.',
                'A strong password does not help if it is reused. Credential stuffing needs no cracking at all.',
            ],
            'try_it': [
                'Work out the keyspace of your own password shape and compare it to a four word passphrase.',
                'Time openssl passwd -6 and pick a bcrypt cost that would take a similar time.',
            ],
            'next': None,
        },
    ],
    'drills': [
        {
            'id': 'ckd-hydra-ssh',
            'type': 'command',
            'prompt': 'Guess the admin password on ssh at 10.0.0.5 from passwords.txt.',
            'answer': 'hydra -l admin -P passwords.txt ssh://10.0.0.5',
            'teach': 'Lowercase for a single value, uppercase for a list. That pattern holds across the tool.',
        },
        {
            'id': 'ckd-hydra-spray',
            'type': 'command',
            'prompt': 'Try one password across users.txt on ssh at 10.0.0.5, slowly.',
            'answer': 'hydra -L users.txt -p "Spring2026!" -t 4 -W 5 ssh://10.0.0.5',
            'teach': 'Many users, one password, rate limited. The shape that lockout policies force.',
        },
        {
            'id': 'ckd-rand-pass',
            'type': 'command',
            'prompt': 'Generate a random 24 byte password as base64.',
            'answer': 'openssl rand -base64 24',
            'teach': 'The human choosing is the weak part of a password. This removes the human.',
        },
    ],
    'challenges': [
        {
            'id': 'hyd-build-form',
            'title': 'Build the http-post-form string from a real response',
            'goal': 'The awkward part of hydra, done the way it should be: look at what a failed login actually returns, then write the three-field string from that rather than from memory.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {
                    'response.html': (
                        '<html><body>\n'
                        '<form action="/login" method="post">\n'
                        '  <input name="user">\n'
                        '  <input name="pass" type="password">\n'
                        '</form>\n'
                        '<p class="err">Invalid credentials</p>\n'
                        '</body></html>\n'
                    ),
                },
            },
            'solution': {
                'shell': "printf '%s\\n' '/login:user=^USER^&pass=^PASS^:Invalid credentials' > form.txt",
            },
            'steps': [
                {
                    'instruction': 'Read response.html. It is what the server returned for a deliberately wrong login.',
                    'hint': 'cat response.html',
                },
                {
                    'instruction': 'Find three things: the path the form posts to, the names of the two input fields, and a phrase that appears only on failure.',
                },
                {
                    'instruction': 'Write the hydra string into form.txt as path:body:failure-string, with ^USER^ and ^PASS^ where the values go.',
                    'hint': '/login:user=^USER^&pass=^PASS^:Invalid credentials',
                },
            ],
            'free': 'Write form.txt containing the http-post-form argument for this login: the path, the post body with ^USER^ and ^PASS^ placeholders, and the failure string, separated by colons.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_contains': {
                        'form.txt': ['/login', 'user=^USER^', 'pass=^PASS^', 'Invalid credentials'],
                    },
                },
            },
            'fallback': 'self',
        },

        {
            'id': 'hyc-online',
            'title': 'Guess against a service you own',
            'goal': 'Online guessing needs a live service and a rate you respect, so this one is on a target you own.',
            'setup': {
                'kind': 'self',
            },
            'steps': [
                {
                    'instruction': 'Stand up a service you own with a known account, or use a lab you have permission for. Nothing else.',
                },
                {
                    'instruction': 'Run hydra with a small list against one user, rate-limited, and watch it in the service logs.',
                    'hint': 'hydra -l youruser -P small.txt -t 4 -W 5 ssh://127.0.0.1',
                },
                {
                    'instruction': 'Now invert it: one likely password across several accounts, which is spraying.',
                    'hint': 'hydra -L users.txt -p "Season2026!" -t 4 ssh://127.0.0.1',
                },
                {
                    'instruction': 'Turn on a lockout policy and watch spraying become the only viable shape. Then note that MFA stops both.',
                },
            ],
            'free': 'On a service you own: run a rate-limited hydra guess against one account, then a spray across several, and observe how a lockout policy reshapes the attack.',
            'verify': {
                'kind': 'self',
            },
            'fallback': 'self',
        },
        {
            'id': 'hyd-write-spray',
            'title': 'Write the spray, not the brute force',
            'goal': 'Lockout after five failures. Write the hydra command that tries one likely password across the user list, slowly.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {
                    'users.txt': 'alice\nbob\ncarol\n',
                    'brief.txt': (
                        'service: ssh at 10.0.0.5\n'
                        'lockout: 5 failures per account\n'
                        'try: Spring2026!\n'
                    ),
                },
            },
            'solution': {
                'shell': 'printf \'%s\\n\' \'hydra -L users.txt -p "Spring2026!" -t 4 -W 5 ssh://10.0.0.5\' > spray.txt',
            },
            'steps': [
                {
                    'instruction': 'Read brief.txt. Five failures lock an account, so many passwords against one user is the wrong shape.',
                    'hint': 'cat brief.txt',
                },
                {
                    'instruction': 'Write the hydra command into spray.txt: the user list, one password, four tasks, a five second wait, against ssh on 10.0.0.5.',
                    'hint': 'hydra -L users.txt -p "Spring2026!" -t 4 -W 5 ssh://10.0.0.5',
                },
                {
                    'instruction': 'Check the case of each flag. Lowercase is one value; uppercase is a file of them.',
                },
            ],
            'free': 'Write spray.txt containing the hydra command that sprays Spring2026! across users.txt against ssh://10.0.0.5, rate limited with -t 4 and -W 5.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_contains': {
                        'spray.txt': [
                            'hydra',
                            '-L users.txt',
                            '-p',
                            'Spring2026',
                            '-t 4',
                            '-W 5',
                            'ssh://10.0.0.5',
                        ],
                    },
                    'file_lacks': {
                        'spray.txt': '-P',
                    },
                },
            },
            'fallback': 'self',
        },
    ],
    'quiz': [
        {
            'id': 'ckq-online',
            'type': 'mcq',
            'prompt': 'Why is online guessing a different strategy from offline cracking?',
            'answer': 'The service sets the rate, so few passwords across many accounts beats many passwords against one.',
            'distractors': [
                'Online services use stronger hash algorithms.',
                'Network latency makes GPUs useless.',
                'Online attacks cannot use wordlists.',
            ],
            'teach': 'Lockouts do not stop guessing, they reshape it. That is why spraying detection matters defensively.',
        },
        {
            'id': 'hyq-spray',
            'type': 'mcq',
            'prompt': 'A lockout policy locks an account after five bad guesses. How does an attacker adapt?',
            'answer': 'One likely password across many accounts, staying under the threshold per account.',
            'distractors': [
                'A bigger wordlist against one account.',
                'Cracking the hash offline instead.',
                'Nothing; lockouts stop all guessing.',
            ],
            'teach': 'Spraying. Lockouts reshape guessing rather than stopping it, which is why detecting many failures across many accounts matters.',
        },
        {
            'id': 'hyq-failstr',
            'type': 'mcq',
            'prompt': 'hydra reports every HTTP password as valid. What usually went wrong?',
            'answer': 'The failure string does not appear on the failure page, so every attempt looks like success.',
            'distractors': [
                'The wordlist was too short to contain misses.',
                '-t was set higher than the server allows.',
                'http-post-form cannot detect failure on a 200.',
            ],
            'teach': 'A wrong login is usually HTTP 200 with an error phrase in the body. Field three is that phrase, and guessing it from memory is how this happens.',
        },
        {
            'id': 'hyq-case',
            'type': 'mcq',
            'prompt': 'In hydra, what is the difference between -l and -L, or -p and -P?',
            'answer': 'Lowercase is one value; uppercase is a file of them.',
            'distractors': [
                'Lowercase is SSH; uppercase is HTTP.',
                'Lowercase is required; uppercase is a deprecated alias.',
                'Lowercase is slow and careful; uppercase is parallel.',
            ],
            'teach': 'The pattern holds across the tool. Mixing them is how a spray becomes a single-account brute force by accident.',
        },
    ],
}
