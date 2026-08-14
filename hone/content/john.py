"""John the Ripper: the CPU-first cracker that guesses well by default.

john's trait is sensible defaults: point it at a file and it detects the format and runs single crack, then a wordlist, then incremental. This module is its modes, its pot file (the cache that makes it 'refuse' to re-crack), and its formats. Cracking is guessing here as everywhere.

Preparing hashes and reading the pot are sandbox-verified; running john itself is self-marked, since it is not installed here. Scope: the tool, never the engagement.
"""

MODULE = {
    'id': 'john',
    'title': 'John the Ripper',
    'group': 'Security',
    'blurb': 'Autodetection, single/wordlist/incremental modes, the pot file, and formats.',
    'context': 'You are at a shell prompt with hashes you are permitted to crack.',
    'needs': [
        'john',
    ],
    'prereqs': [
        'linux',
        'bash',
    ],
    'adapter': 'sandbox',
    'estimate': '2-3 hours',
    'order': 77,
    'lessons': [
        {
            'id': 'jtr-what',
            'title': 'What John the Ripper is',
            'concept': 'John the Ripper is the CPU-first password cracker, and its defining trait is that it tries to be sensible without being told much. Point it at a file of hashes and it works out the format, then runs its modes in order: single crack, then a wordlist, then incremental. Where hashcat asks you to be explicit, john guesses well by default, which makes it the faster tool to reach for on an unknown file.\n\nLike all cracking, it is guessing: generate a candidate, hash it, compare. What john adds is good defaults and a huge format library in its "jumbo" build, which handles not just password hashes but archives, disk encryption and much more.\n\nScope, as everywhere in this group: crack hashes you generated or are permitted to crack, and nothing else.',
            'examples': [
                {
                    'label': 'The whole default flow',
                    'code': 'john hashes.txt\n  single, then wordlist, then incremental\n\njohn --show hashes.txt\n  what it has already cracked, from the pot file',
                    'note': 'Point it at a file and it does something sensible. --show reads back the results.',
                },
            ],
            'misconceptions': [
                'john does not need to be told the format most of the time; it autodetects. You override with --format only when it is ambiguous.',
                'john is not only for Unix hashes. The jumbo build cracks hundreds of formats, including archives and disk images.',
                'Cracking is guessing here too. john is a good guess generator with good defaults, not a hash reverser.',
            ],
            'try_it': [
                'Make a hash you know, crack it with john, then run john again and watch it say there is nothing left: that is the pot file.',
            ],
            'next': 'jtr-modes',
        },
        {
            'id': 'jtr-modes',
            'title': 'Modes, the pot file, and formats',
            'concept': 'john runs three modes, and knowing them means knowing what it is doing when you just type `john hashes.txt`.\n\n**Single crack** uses information from the file itself, the username and GECOS fields, as candidates. It is first because it is cheap and works far more often than anyone expects. **Wordlist** mode takes `--wordlist` and optionally `--rules`, and is where most real cracking happens. **Incremental** is brute force over a character set, ordered by frequency from john\'s own statistics rather than alphabetically, which makes it much better than a plain counter.\n\nThe pot file is the thing beginners trip over. Cracked passwords go into `~/.john/john.pot`, and john will never crack the same hash twice: run it again and it says "No password hashes left to crack". That is the cache, not a failure, and `--show` prints what it already knows. Deleting the pot file starts over.\n\n`--format` matters when autodetection is ambiguous, which is exactly the 32-hex MD5-versus-NTLM case, and `unshadow` merges `/etc/passwd` and `/etc/shadow` so single crack has the usernames it wants.',
            'examples': [
                {
                    'label': 'The modes and the pot',
                    'code': 'john hashes.txt                     all three modes\njohn --wordlist=rockyou.txt --rules=best64 hashes.txt\njohn --incremental hashes.txt        pure brute force\njohn --show hashes.txt               read the pot file\njohn --format=nt hashes.txt          force NTLM',
                    'note': '"No hashes left to crack" means the pot already has them. Run --show.',
                },
                {
                    'label': 'Getting the hashes in',
                    'code': 'unshadow /etc/passwd /etc/shadow > combined.txt\njohn combined.txt\n\njohn --list=formats     the hundreds it knows',
                    'note': 'unshadow gives single crack the usernames, which is where a surprising share of real cracks come from.',
                },
            ],
            'misconceptions': [
                '"No password hashes left to crack" usually means the pot file already has them. Run --show.',
                'Single crack mode is not a weak first attempt. It is the highest yield per second of any mode on real data.',
                'Autodetection cannot separate MD5 from NTLM by length, so a 32-character hash may need --format to be cracked correctly.',
            ],
            'try_it': [
                'Crack a hash, then run john again and see it refuse. Run --show and find your result in the pot file.',
            ],
            'next': None,
        },
    ],
    'drills': [
        {
            'id': 'ckd-john-basic',
            'type': 'command',
            'prompt': 'Run john with its default sequence against hashes.txt.',
            'answer': 'john hashes.txt',
            'teach': 'Single, then wordlist, then incremental. Sensible defaults, and often enough on real data.',
        },
        {
            'id': 'ckd-john-wordlist',
            'type': 'command',
            'prompt': 'Run john against hashes.txt using rockyou.txt with best64 rules.',
            'answer': 'john --wordlist=rockyou.txt --rules=best64 hashes.txt',
            'teach': 'Where most real cracking happens. Rules multiply each word into dozens of human manglings.',
        },
        {
            'id': 'ckd-john-show',
            'type': 'command',
            'prompt': 'Show the passwords john has already cracked for hashes.txt.',
            'answer': 'john --show hashes.txt',
            'teach': 'Reads the pot file, which is what to run when john says there is nothing left to crack.',
        },
        {
            'id': 'ckd-john-format',
            'type': 'command',
            'prompt': 'Force john to treat hashes.txt as NTLM.',
            'answer': 'john --format=nt hashes.txt',
            'teach': 'Autodetection cannot separate MD5 from NTLM by length, so you tell it.',
        },
        {
            'id': 'ckd-john-formats',
            'type': 'command',
            'prompt': 'List every hash format john knows about.',
            'answer': 'john --list=formats',
            'teach': 'Hundreds in the jumbo build, including archives and disk encryption, not just password hashes.',
        },
        {
            'id': 'ckd-john-incremental',
            'type': 'command',
            'prompt': 'Run john in pure brute force mode against hashes.txt.',
            'answer': 'john --incremental hashes.txt',
            'teach': 'Ordered by character frequency from real data rather than alphabetically, which makes it far better than a counter.',
        },
        {
            'id': 'ckd-unshadow',
            'type': 'command',
            'prompt': 'Merge passwd and shadow into combined.txt for john.',
            'answer': 'unshadow /etc/passwd /etc/shadow > combined.txt',
            'teach': 'Gives single crack mode the usernames, which is where a surprising share of real cracks come from.',
        },
        {
            'id': 'ckd-cut-shadow',
            'type': 'command',
            'prompt': 'Extract just the hash field from every line of shadow.txt.',
            'answer': 'cut -d: -f2 shadow.txt',
            'teach': 'Field two is the whole crypt string. hashcat wants that alone; john prefers the username with it.',
        },
    ],
    'challenges': [
        {
            'id': 'ckc-shadow',
            'title': 'Get the hashes out of the file they live in',
            'goal': 'Take a shadow-format file apart into the two shapes the two tools want.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {
                    'shadow.txt': 'alice:$6$aaaaaaaa$abcdefghijklmnop:19000:0:99999:7:::\nbob:$6$bbbbbbbb$qrstuvwxyz012345:19000:0:99999:7:::\ndaemon:*:19000:0:99999:7:::\nsync:!:19000:0:99999:7:::\n',
                },
            },
            'solution': {
                'shell': 'grep -E ":\\\\$" shadow.txt | cut -d: -f1,2 > for-john.txt && grep -E ":\\\\$" shadow.txt | cut -d: -f2 > for-hashcat.txt && grep -Ev ":\\\\$" shadow.txt | cut -d: -f1 > no-hash.txt',
            },
            'steps': [
                {
                    'instruction': 'Keep only the lines whose second field is a real crypt hash, and write user:hash pairs to for-john.txt.',
                    'hint': 'grep -E ":\\$" shadow.txt | cut -d: -f1,2',
                },
                {
                    'instruction': 'Write the bare hashes alone to for-hashcat.txt.',
                    'hint': 'cut -d: -f2',
                },
                {
                    'instruction': 'List the accounts that have no crackable hash at all into no-hash.txt, and note what * and ! mean.',
                },
            ],
            'free': 'Produce for-john.txt with user:hash pairs, for-hashcat.txt with bare hashes, and no-hash.txt naming the accounts with no password hash.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_contains': {
                        'for-john.txt': [
                            'alice:$6$',
                            'bob:$6$',
                        ],
                        'for-hashcat.txt': '$6$aaaaaaaa$',
                        'no-hash.txt': [
                            'daemon',
                            'sync',
                        ],
                    },
                    'file_lacks': {
                        'for-hashcat.txt': 'alice',
                    },
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'ckc-real-tools',
            'title': 'Run the real thing, on hashes you made',
            'goal': 'Install a cracker if you have not, and crack hashes you generated yourself. Nothing else.',
            'setup': {
                'kind': 'self',
            },
            'steps': [
                {
                    'instruction': 'Generate a few hashes of passwords you chose and can verify.',
                    'hint': 'echo -n hunter2 | md5sum',
                },
                {
                    'instruction': 'Crack them with john, then run john again and see the pot file behaviour.',
                    'hint': 'john --format=raw-md5 mine.txt; john --show --format=raw-md5 mine.txt',
                },
                {
                    'instruction': 'Benchmark md5 and bcrypt on your hardware and write down the ratio.',
                    'hint': 'hashcat -b -m 0; hashcat -b -m 3200',
                },
                {
                    'instruction': 'Try a mask attack on a password whose shape you know, and check --keyspace first.',
                },
                {
                    'instruction': 'Only ever your own hashes, or a lab you have permission for.',
                },
            ],
            'free': 'On your own machine: generate hashes, crack them with a real tool, benchmark a fast hash against a slow one, and run one mask attack after checking its keyspace.',
            'verify': {
                'kind': 'self',
            },
            'fallback': 'self',
        },
    ],
    'quiz': [
        {
            'id': 'ckq-potfile',
            'type': 'mcq',
            'prompt': 'john says "No password hashes left to crack". What is the usual reason?',
            'answer': 'It already cracked them and the results are in the pot file.',
            'distractors': [
                'The hash format was not recognised.',
                'The wordlist was exhausted with no matches.',
                'The file has the wrong permissions.',
            ],
            'teach': 'Run --show. This confuses everyone exactly once, and deleting the pot file starts over.',
        },
        {
            'id': 'ckq-32hex',
            'type': 'mcq',
            'prompt': 'You have a 32 character hex hash. What can you conclude?',
            'answer': 'It is MD5 or NTLM, and context has to decide which.',
            'distractors': [
                'It is definitely MD5.',
                'It is definitely NTLM, since MD5 is 16 bytes.',
                'It is SHA-1 truncated to 128 bits.',
            ],
            'teach': 'Where it came from decides. A Windows SAM gives NTLM; a web application database usually gives MD5.',
        },
    ],
}
