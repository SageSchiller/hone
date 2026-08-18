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
    'order': 82,
    'lessons': [
        {
            'id': 'jtr-cracking',
            'title': 'What cracking a password actually means',
            'next': 'jtr-what',
            'concept': (
                'Password cracking is how you recover a password from a hash '
                'by guessing, hashing the guess, and comparing. That is why '
                'a stolen password file is not a list of passwords.\n\n'
                '**Systems do not store your password.** They store a hash of '
                'it: a one-way function of the bytes you typed. When you log '
                'in, the system hashes what you typed and compares the two '
                'digests.\n\n'
                'That means a stolen password file contains no passwords. It '
                'contains digests, and there is no operation that turns a '
                'digest back into the input. **So cracking is guessing.** '
                'Take a candidate, hash it the same way, compare. Wrong? Next '
                'candidate. That loop is the entire activity, and every '
                'cracking tool is a very fast, very well-informed version of '
                'it.\n\n'
                'Which reframes the whole subject. You are not attacking the '
                'algorithm, you are **racing the space of likely passwords**, '
                'and everything that matters follows from that:\n\n'
                '**Good guesses beat fast guessing.** A wordlist of real '
                'leaked passwords finds more in a minute than brute force '
                'finds in a week, because humans pick from a small space and '
                'always have.\n\n'
                '**A salt is a per-password random value** mixed in before '
                'hashing. It does not make any one password harder to guess. '
                'It makes you guess *separately for every user*, which '
                'destroys precomputed tables and turns one attack into ten '
                'thousand.\n\n'
                '**Slow hashes exist on purpose.** bcrypt and argon2 are '
                'deliberately expensive, so each guess costs real time. '
                'Against a fast hash like raw MD5 you might try billions per '
                'second; against bcrypt, thousands.\n\n'
                '**Scope, and it is not decoration.** Crack hashes you '
                'generated, or ones you have written permission to crack. '
                'This module teaches the tool, never a target. The CPU-first '
                'tool that guesses well by default, without being told the '
                'format, is the next lesson.'
            ),
            'examples': [
                {
                    'label': 'The loop, in full',
                    'code': ('for each candidate:\n'
                             '    if hash(candidate) == stolen_digest:\n'
                             '        you have the password\n'
                             '\n'
                             'that is the whole of it. everything else\n'
                             'is choosing candidates well.'),
                    'note': 'No cleverness reverses a hash. The entire craft '
                            'is in the order you try things.',
                },
                {
                    'label': 'What a salt actually costs the attacker',
                    'code': ('no salt:  hash "password123" once,\n'
                             '          compare to all 10000 users\n'
                             '\n'
                             'salted:   hash "password123" with each\n'
                             '          user\'s salt. 10000 times.'),
                    'note': 'Same guess, ten thousand times the work. This is '
                            'why an unsalted password database is a much '
                            'worse leak than a salted one.',
                },
                {
                    'label': 'Why the algorithm choice dominates',
                    'code': ('raw MD5        billions of guesses/sec\n'
                             'SHA-256        hundreds of millions\n'
                             'bcrypt         tens of thousands\n'
                             'argon2         fewer still, by design'),
                    'note': 'The same password behind bcrypt and behind MD5 '
                            'are not equally exposed. The hash choice, not '
                            'the password, is usually the deciding factor.',
                },
            ],
            'misconceptions': [
                'Cracking does not reverse a hash. Nothing reverses a hash. '
                'It guesses inputs and checks them, which is a completely '
                'different activity with different limits.',
                'A salt does not make a password stronger. It makes each '
                'password have to be attacked separately, which is a '
                'statement about the set rather than about any one of them.',
                'Failing to crack a hash does not mean the password is '
                'strong. It means it was not in the space you searched, and '
                'those are not the same thing.',
            ],
            'try_it': [
                'Hash a word you choose with `echo -n word | md5sum`, then '
                'search for that digest online. Note how many "reverse MD5" '
                'sites are simply large lookup tables.',
                'Decide, before reading on, which would help more against a '
                'real password file: a machine ten times faster, or a '
                'wordlist ten times better.',
            ],
        },
        {
            'id': 'jtr-what',
            'title': 'What John the Ripper is',
            'concept': 'John the Ripper is how you crack a file of hashes on CPU without being told the format. That is why it is the faster tool to reach for on an unknown file: it detects the format and runs single, wordlist, then incremental on its own. Where hashcat asks you to be explicit, john guesses well by default, which makes it the faster tool to reach for on an unknown file.\n\nLike all cracking, it is guessing: generate a candidate, hash it, compare. What john adds is good defaults and a huge format library in its "jumbo" build, which handles not just password hashes but archives, disk encryption and much more.\n\nScope, as everywhere in this group: crack hashes you generated or are permitted to crack, and nothing else.\n\n`john --list=formats` is how you see what this build can eat. A hash it cannot parse is usually the wrong jumbo, or a line that is not a hash. The pot file remembers what already cracked, so a second run skips those.\n\nWhat a wrong autodetect looks like: a file of 32-hex strings from a Windows SAM is NTLM, and john may pick raw-MD5 because the length matches both. The run finishes fast, prints no cracks, and looks like a strong-password result. It is a format miss. `--format=nt` is the override.',
            'examples': [
                {
                    'label': 'The whole default flow',
                    'code': 'john hashes.txt\n  single, then wordlist, then incremental\n\njohn --show hashes.txt\n  what it has already cracked, from the pot file',
                    'note': 'Point it at a file and it does something sensible. --show reads back the results.',
                },
                {
                    'label': 'When autodetection cannot decide',
                    'code': '32 hex characters: MD5, or NTLM\n\njohn hashes.txt              may pick the wrong one\njohn --format=nt hashes.txt  force NTLM\njohn --list=formats          what this build can eat',
                    'note': 'Length cannot separate MD5 from NTLM. A hash it cannot parse at all is usually the wrong jumbo, or not a hash.',
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
            'concept': 'john runs three modes, and knowing them means knowing what it is doing when you just type `john hashes.txt`.\n\n**Single crack** uses information from the file itself, the username and GECOS fields, as candidates. It is first because it is cheap and works far more often than anyone expects. **Wordlist** mode takes `--wordlist` and optionally `--rules`, and is where most real cracking happens. **Incremental** is brute force over a character set, ordered by frequency from john\'s own statistics rather than alphabetically, which makes it much better than a plain counter.\n\nThe pot file is the thing beginners trip over. Cracked passwords go into `~/.john/john.pot`, and john will never crack the same hash twice: run it again and it says "No password hashes left to crack". That is the cache, not a failure, and `--show` prints what it already knows. Deleting the pot file starts over.\n\n`--format` matters when autodetection is ambiguous, which is exactly the 32-hex MD5-versus-NTLM case, and `unshadow` merges `/etc/passwd` and `/etc/shadow` so single crack has the usernames it wants.\n\nWhat missing usernames looks like: cut only field 2 and single crack has nothing to try first. It skips to the wordlist, and a password that was the username plus `1` is now a later find. Incremental has a different surprise: it does not start at `aaaaaa`. Frequency order tries common characters first, so `password` arrives much earlier than a counter would reach it.\n\nAn archive or a key is not a hash line. `zip2john secret.zip > zip.hash` and `ssh2john id_rsa > ssh.hash` turn the artefact into a line john will eat. Pointing john at the zip itself fails, because john reads a hash file rather than the container. The same family covers pdf2john, rar2john and keepass2john: convert first, then crack.\n\nA long run needs a name. `john --session=lab hashes.txt` writes resume state under that name, and `john --restore=lab` picks it up after a kill or a reboot. Without `--session`, a second john in another terminal fights the same default files. `--restore` is how a four-hour incremental job survives a closed laptop rather than starting over.',
            'examples': [
                {
                    'label': 'Getting the hash out of the file first',
                    'code': 'cut -d: -f2 shadow.txt      field 2, colon separated\n\nroot:$6$xyz$abc...:19000:0:99999:7:::\n     \\_____________/\n      that is field 2',
                    'note': '-d sets the delimiter and -f picks the field. A shadow line is nine colon-separated fields and only the second one is the hash.',
                },
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
                {
                    'label': 'An artefact, then a session you can restore',
                    'code': (
                        'zip2john secret.zip > zip.hash\n'
                        'ssh2john id_rsa > ssh.hash\n'
                        'john zip.hash\n'
                        '\n'
                        'john --session=lab hashes.txt\n'
                        'john --restore=lab'
                    ),
                    'note': 'The converter writes a line john can parse. '
                            '--session names the run so --restore can find '
                            'it after a kill, rather than starting over.',
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
            'id': 'jtr-prepare',
            'title': 'Prepare a hash file, dropping the locked accounts',
            'goal': 'Before john runs, someone has to build the file it reads. That is a text problem, it is where most of the mistakes happen, and it is entirely offline.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {
                    'passwd.txt': (
                        'root:x:0:0:root:/root:/bin/bash\n'
                        'alice:x:1000:1000::/home/alice:/bin/bash\n'
                        'bob:x:1001:1001::/home/bob:/bin/bash\n'
                    ),
                    'shadow.txt': (
                        'root:$6$abc$AAA:19000:0:99999:7:::\n'
                        'alice:$6$def$BBB:19100:0:99999:7:::\n'
                        'bob:!:19100:0:99999:7:::\n'
                    ),
                },
            },
            'solution': {
                'shell': "awk -F: 'NR==FNR{h[$1]=$2; next} h[$1] ~ /^\\$/ {print $1\":\"h[$1]}' shadow.txt passwd.txt > tocrack.txt && cut -d: -f2 tocrack.txt > hashes.txt",
            },
            'steps': [
                {
                    'instruction': 'Look at shadow.txt. Field two is the hash, and one account does not have one: bob has an exclamation mark, which means the account is locked.',
                    'hint': 'cut -d: -f1,2 shadow.txt',
                },
                {
                    'instruction': 'Build tocrack.txt as user:hash, one line per account that actually has a hash. A real hash starts with a dollar sign.',
                    'hint': 'A locked account is a wasted guess on every candidate in your wordlist.',
                },
                {
                    'instruction': 'Then extract just the hash column into hashes.txt.',
                    'hint': 'cut -d: -f2 tocrack.txt > hashes.txt',
                },
            ],
            'free': 'Produce tocrack.txt containing user:hash for the accounts that have a real hash, and hashes.txt containing just those hashes.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_contains': {
                        'tocrack.txt': ['root:$6$abc$AAA', 'alice:$6$def$BBB'],
                        'hashes.txt': '$6$def$BBB',
                    },
                    'file_lacks': {'tocrack.txt': 'bob'},
                },
            },
            'fallback': 'self',
        },

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
        {
            'id': 'ckq-single',
            'type': 'mcq',
            'prompt': 'What does john single crack mode use as candidates?',
            'answer': 'The username and GECOS fields from the hash file itself.',
            'distractors': [
                'The first 100 words of the default wordlist.',
                'Single-character brute force, then it stops.',
                'The pot file, replayed as a wordlist.',
            ],
            'teach': 'It is first because it is cheap and works more often than it should. unshadow exists so those username fields are actually there.',
        },
        {
            'id': 'ckq-incremental',
            'type': 'mcq',
            'prompt': 'How does john incremental mode order its guesses?',
            'answer': 'By character frequency from real passwords, not alphabetically.',
            'distractors': [
                'Alphabetically, then by length.',
                'Randomly, so every run covers a different space.',
                'By hash format, shortest digest first.',
            ],
            'teach': 'A plain counter wastes early guesses on AAAAAA. Frequency order is why incremental finds real passwords faster than brute force sounds.',
        },
    ],
}
