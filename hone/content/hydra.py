"""hydra: online password guessing, which is a different game from offline cracking.

The one fact that shapes the whole tool is that the service sets the rate: lockouts, rate limits and logging mean a few guesses a minute, not billions a second. So the strategy inverts to spraying, a few likely passwords across many accounts. hydra's interface follows the protocol, and HTTP forms need you to name what a failure looks like.

Everything here is self-marked (D8): it needs a live service you own, which the trainer cannot provide. Scope, hard: only services you own or are permitted to test.
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
    'adapter': None,
    'estimate': '2-3 hours',
    'order': 83,
    'lessons': [
        {
            'id': 'hyd-what',
            'title': 'Online guessing is a different game',
            'concept': "hydra guesses passwords against a live service, and that one fact, live rather than offline, changes everything. Offline, you hold the hash and the only limit is your hardware, measured in billions of guesses a second. Online, the rate is set by the service: lockouts, rate limits, CAPTCHAs, alerting, and every attempt logged. You get a handful of tries a minute before something notices.\n\nThat inverts the strategy. Offline you throw millions of passwords at one hash. Online, the only thing that works within the limits is a few very likely passwords against many accounts, which is called spraying, and is rate management rather than a clever trick.\n\nhydra's interface is shaped by the protocol: `-l` or `-L` for the user or a user list, `-p` or `-P` for a password or a list, `-t` for parallel tasks, then the target and the service as `protocol://host`. For HTTP forms the syntax gets genuinely awkward, because you must tell hydra what a failed login looks like.\n\nScope, hard here because it touches live services: only ones you own or are explicitly permitted to test.",
            'examples': [
                {
                    'label': 'The shape, and the spray',
                    'code': 'hydra -l admin -P passwords.txt ssh://10.0.0.5\n  many passwords, one user, one service\n\nhydra -L users.txt -p "Spring2026!" -t 4 -W 5 ssh://10.0.0.5\n  one password, many users, slowly: the online shape',
                    'note': 'Lowercase for a single value, uppercase for a list. -t sets how many tries run at once (the default is 16), so a low -t 4 with a -W wait is what keeps you slow, not -t itself.',
                },
                {
                    'label': 'A web form needs the failure string',
                    'code': 'hydra -l admin -P pw.txt 10.0.0.5 http-post-form \\\n  "/login:user=^USER^&pass=^PASS^:Invalid"',
                    'note': 'The last field is how hydra recognises a failed login. Get it wrong and it reports every attempt as a success.',
                },
            ],
            'misconceptions': [
                'Online guessing is not offline cracking with a network hop. The rate limit changes the entire strategy.',
                'A lockout policy does not stop guessing. It changes it from many passwords per account to one password across many accounts.',
                'hydra reporting many successes on a web form usually means the failure string is wrong, not that you found many passwords.',
            ],
            'try_it': [
                'On a service you own, find how many attempts you get before a lockout, and read a failed login response for the string that marks it.',
            ],
            'next': 'ck-defence',
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
    ],
}
