"""hashcat: the GPU-first password cracker, taught as guessing at speed.

The one idea the tool rests on is that cracking is guessing, not reversing: hashcat generates candidates, hashes each, and compares. Everything it offers is either a faster hash or a better guess. Two numbers run it, -m for the hash type and -a for the attack, and the module is built around getting those right and around masks and rules, which are where good guesses come from.

Verification is honest per D8: generating hashes, identifying formats and computing a keyspace are sandbox-verified; running hashcat itself is self-marked, since it is not installed here. Scope: the tool, never the engagement.
"""

MODULE = {
    'id': 'hashcat',
    'title': 'hashcat',
    'group': 'Security',
    'blurb': 'Hash modes, attack modes, masks, wordlists and rules, and the potfile.',
    'context': 'You are at a shell prompt with hashes you are permitted to crack.',
    'needs': [
        'hashcat',
    ],
    'prereqs': [
        'linux',
        'bash',
    ],
    'adapter': 'sandbox',
    'estimate': '3-4 hours',
    'order': 81,
    'lessons': [
        {
            'id': 'hc-what',
            'title': 'What hashcat is, and what cracking is',
            'concept': 'hashcat is the fast, GPU-first password cracker, and to use it you have to hold one fact: cracking is not reversing a hash. It is guessing, hashing the guess, and comparing. hashcat is a very fast loop that generates candidates, hashes each one, and checks it against the target, and everything it does is either "generate better guesses" or "hash them faster".\n\nTwo numbers run the whole tool and confusing them is the classic first error. `-m` is the hash mode: what kind of hash you have, where 0 is MD5, 1000 is NTLM, 3200 is bcrypt, 1800 is SHA-512-crypt. `-a` is the attack mode: how candidates are generated, where 0 is a straight wordlist, 3 is a brute-force mask, and 6 and 7 are hybrids. Get `-m` from what the hash is and `-a` from your strategy.\n\nScope, as everywhere in this group: how the tool works, never who to point it at. Crack hashes you generated or are permitted to crack, and nothing else.',
            'examples': [
                {
                    'label': 'The shape of every hashcat run',
                    'code': 'hashcat -m 0 -a 0 hashes.txt rockyou.txt\n        ^     ^   ^          ^\n     hash    how what        wordlist\n     mode  attack you crack',
                    'note': '-m is what the hash is, -a is how you guess. That split is the whole command line.',
                },
            ],
            'misconceptions': [
                'hashcat does not decrypt anything. Every "hash decrypter" is a lookup of hashes someone already cracked.',
                '-m and -a are not interchangeable. -m is the target format, -a is the strategy.',
                'A longer hash output does not make a password harder to guess. The cost per guess does, which is the salt-and-cost lesson.',
            ],
            'try_it': [
                'Run `hashcat -b -m 0` and `hashcat -b -m 3200` and compare the two benchmark numbers. That difference is the whole argument for slow hashes.',
            ],
            'next': 'ck-identify',
        },
        {
            'id': 'ck-identify',
            'title': 'Identifying what you are looking at',
            'concept': 'Before you can crack anything you have to know what it is, and the format is usually written on the front.\n\nBare hex strings are identified by length: 32 hex characters is MD5 or NTLM, 40 is SHA-1, 64 is SHA-256, 128 is SHA-512. Length alone cannot separate MD5 from NTLM, which is why context matters: a 32 character hash out of a Windows SAM is NTLM, and one out of a web application is probably MD5.\n\nModular crypt format is the one with dollar signs, and it tells you outright. $1$ is MD5-crypt, $5$ is SHA-256-crypt, $6$ is SHA-512-crypt, $2a$ / $2b$ / $2y$ is bcrypt, $y$ is yescrypt, and $argon2id$ is argon2. The fields between the dollars are the algorithm, then usually a cost parameter, then the salt, then the hash.\n\nA Linux shadow entry is colon separated, and the second field is the whole modular crypt string. That is what `unshadow` merges with passwd for john, and what you cut out by hand for hashcat.\n\nTools exist, `hashid` and `hash-identifier`, and they guess from the same signals you can read yourself. Reading it yourself is faster and does not produce a list of nine possibilities.',
            'examples': [
                {
                    'label': 'Modular crypt, read left to right',
                    'code': '$6$abcdefgh$M/eYsB4rVXAm3ZNc88J...',
                    'note': 'Algorithm 6 is SHA-512-crypt, salt abcdefgh, then the hash. Everything you need is in the string.',
                },
                {
                    'label': 'bcrypt, with its cost in the open',
                    'code': '$2b$12$LongSaltAndHashHere...',
                    'note': '12 is the work factor: 2 to the 12 iterations. Raising it by one doubles the cost per guess.',
                },
                {
                    'label': 'Pull the hash out of a shadow line',
                    'code': 'cut -d: -f2 shadow.txt',
                    'note': 'Field two is the whole crypt string. Field one is the user, and hashcat does not want it.',
                },
                {
                    'label': 'The tool version',
                    'code': 'hashid "$6$abcdefgh$M/eYsB..."',
                    'note': 'Guesses from the same signals. Useful, and no substitute for recognising the common ones.',
                },
            ],
            'misconceptions': [
                'A 32 character hex hash is not necessarily MD5. NTLM is the same length, and the difference matters enormously for speed.',
                'The dollar-sign fields are not a hash you can compare directly. They contain the algorithm and salt as well.',
                'An empty second field in a shadow line is not a hash. It is an account with no password.',
            ],
            'try_it': [
                'Generate hashes with openssl passwd -1, -5 and -6 and read the prefix on each.',
                'Take a shadow-format line and extract just the hash with cut.',
            ],
            'next': 'ck-salt',
        },
        {
            'id': 'ck-salt',
            'title': 'Salts, cost, and what each one defeats',
            'concept': "Two defences get confused constantly, and they stop completely different attacks.\n\n**A salt is a unique random value stored with the hash.** It means the same password produces a different hash for every user, which destroys precomputation: a rainbow table built for one salt is worthless for another, and identical passwords are no longer visible as identical hashes. What a salt does not do is slow anyone down. Guessing one salted hash costs exactly what guessing an unsalted one costs.\n\n**Cost, or work factor, or iterations, makes each guess expensive.** That is the defence against guessing, and it is the only one. bcrypt's cost parameter, PBKDF2's iteration count and argon2's time and memory parameters are all the same idea: make the legitimate login take a few milliseconds and the attacker's billion guesses take forever.\n\nArgon2 adds a third axis: memory hardness. GPUs get their advantage from thousands of small parallel cores with little memory each, so a function that demands a lot of memory per guess removes most of that advantage. That is the reason argon2id is the current recommendation rather than simply more bcrypt rounds.\n\nPepper is the less common one: a secret value added to every hash and stored somewhere other than the database, so a database dump alone is not enough.",
            'examples': [
                {
                    'label': 'Same password, different salts',
                    'code': 'openssl passwd -6 -salt aaaaaaaa hunter2\nopenssl passwd -6 -salt bbbbbbbb hunter2',
                    'note': 'Two different hashes. That is precomputation dead, and guessing entirely unaffected.',
                },
                {
                    'label': 'Cost, visible in the hash',
                    'code': '$2b$04$...   vs   $2b$14$...',
                    'note': 'Ten doublings apart. The second is roughly a thousand times more expensive per guess.',
                },
                {
                    'label': 'What a modern hash costs',
                    'code': 'time openssl passwd -6 hunter2',
                    'note': 'Milliseconds for one. Multiply by a billion and the design argument is obvious.',
                },
            ],
            'misconceptions': [
                'A salt does not slow down cracking. It stops precomputation and stops identical passwords looking identical.',
                'A salt is not a secret. It is stored in plain sight next to the hash, by design.',
                'More hash output length does not increase cost. Iterations and memory do.',
            ],
            'try_it': [
                'Hash the same password with two different salts and compare the outputs.',
                'Time openssl passwd -6 and work out how many guesses per second one core manages.',
            ],
            'next': 'ck-hashcat',
        },
        {
            'id': 'ck-hashcat',
            'title': 'Modes, attacks and masks',
            'concept': 'hashcat is the GPU-first cracker and it asks you to be explicit. Two numbers do most of the work and confusing them is the classic error.\n\n**-m is the hash mode**, which is what kind of hash you have. 0 is MD5, 100 is SHA-1, 1400 is SHA-256, 1000 is NTLM, 1800 is SHA-512-crypt, 3200 is bcrypt, 22000 is WPA. There are hundreds, and `--help` lists them all.\n\n**-a is the attack mode**, which is how candidates are generated. 0 is straight from a wordlist, 1 is combinator joining two lists, 3 is brute force over a mask, 6 and 7 are hybrids of a wordlist with a mask on one end.\n\nThe mask language is the part worth memorising: ?l lower, ?u upper, ?d digit, ?s special, ?a all of those, ?b any byte. So ?u?l?l?l?l?d?d?d is a capitalised five letter word with three digits, which is a very common real password shape and a keyspace small enough to exhaust.\n\nLike john, hashcat keeps a potfile and refuses to redo work. --show reads it, --potfile-disable ignores it. And the status screen matters: it prints the estimated time, which is how you find out that your mask is a decade wide before you commit to it.',
            'examples': [
                {
                    'label': 'Wordlist against NTLM',
                    'code': 'hashcat -m 1000 -a 0 hashes.txt rockyou.txt',
                    'note': 'Hash mode, attack mode, hashes, wordlist. That order is the pattern.',
                },
                {
                    'label': 'Wordlist plus rules',
                    'code': 'hashcat -m 0 -a 0 hashes.txt rockyou.txt -r rules/best64.rule',
                    'note': 'The highest value attack per unit of effort, on almost any real hash set.',
                },
                {
                    'label': 'A mask for a known shape',
                    'code': 'hashcat -m 0 -a 3 hashes.txt ?u?l?l?l?l?d?d?d',
                    'note': 'Capital, four lowercase, three digits. Small keyspace, extremely common shape.',
                },
                {
                    'label': 'How long would that take',
                    'code': 'hashcat -m 0 -a 3 --keyspace ?a?a?a?a?a?a?a?a',
                    'note': 'Print the keyspace before starting. Eight of ?a is not a plan.',
                },
                {
                    'label': 'What did it already crack',
                    'code': 'hashcat -m 0 --show hashes.txt',
                    'note': 'The potfile again. Same trap as john, same fix.',
                },
            ],
            'misconceptions': [
                '-m and -a are not interchangeable. -m is what the hash is, -a is how you guess.',
                'A mask is not a wildcard match against the password. It is a description of the keyspace to enumerate.',
                'hashcat printing nothing on a second run usually means the potfile has the answer, not that cracking failed.',
            ],
            'try_it': [
                'Run --keyspace on three masks and compare the numbers.',
                'Crack an MD5 you generated, then run --show to see it come back from the potfile.',
            ],
            'next': 'ck-wordlists',
        },
        {
            'id': 'ck-wordlists',
            'title': 'Wordlists and rules: better guesses win',
            'concept': 'Given a fixed number of guesses, the winner is whoever guesses better. That is what rules are for, and why a practitioner with a curated list and a good rule file outperforms one with a hundred gigabyte dump.\n\nrockyou.txt is the reference wordlist for a reason: it is fourteen million real passwords from a real breach, so it encodes what people actually choose rather than what a dictionary contains.\n\nRules are transformations applied to every word: capitalise, append digits, substitute letters for symbols, reverse, duplicate. best64 is the standard small set, and it is small deliberately, because a rule file multiplies your keyspace by its own size. One word plus a 64 rule file is 64 candidates, so fourteen million words becomes nearly a billion.\n\nThe insight underneath is that human password mangling is predictable. Password1! is not a clever variation, it is the single most common mangling pattern there is, and a rule file covers it in one line.\n\nTargeted lists still beat everything on a specific target: company names, product names, local sports teams, and the year. `cewl` builds one from a website, and it routinely finds what rockyou does not.',
            'examples': [
                {
                    'label': 'The standard opener',
                    'code': 'hashcat -m 0 -a 0 hashes.txt rockyou.txt -r rules/best64.rule',
                    'note': 'Fourteen million real passwords, times sixty four human manglings.',
                },
                {
                    'label': 'Build a list from the target site',
                    'code': 'cewl -d 2 -m 6 https://example.com -w custom.txt',
                    'note': 'Words from their own pages. Finds what a generic list cannot.',
                },
                {
                    'label': 'Combine two lists',
                    'code': 'hashcat -m 0 -a 1 hashes.txt words.txt years.txt',
                    'note': 'Combinator mode. Every word joined to every other.',
                },
                {
                    'label': 'Wordlist with digits stuck on the end',
                    'code': 'hashcat -m 0 -a 6 hashes.txt words.txt ?d?d?d?d',
                    'note': 'Hybrid: a real word plus a year, which is most passwords ever chosen.',
                },
            ],
            'misconceptions': [
                'A bigger wordlist is not automatically better. Rules on a good list beat raw size almost every time.',
                'Rules do not make cracking slower per candidate. They make more candidates, which is a different cost.',
                'Substituting 3 for e is not a defence. It is line one of every rule file in existence.',
            ],
            'try_it': [
                'Count the lines in a rule file and multiply by your wordlist size to get the real keyspace.',
                'Build a small custom wordlist for a site and compare it against a generic list.',
            ],
            'next': None,
        },
    ],
    'drills': [
        {
            'id': 'ckd-sha256-line',
            'type': 'command',
            'prompt': 'Hash the word hunter2 with SHA-256 and no trailing newline.',
            'answer': 'echo -n hunter2 | sha256sum',
            'teach': 'Without -n you hash the newline too and get a different answer, which wastes an afternoon exactly once.',
        },
        {
            'id': 'ckd-openssl-6',
            'type': 'command',
            'prompt': 'Produce a SHA-512-crypt hash of hunter2 with salt abcdefgh.',
            'answer': 'openssl passwd -6 -salt abcdefgh hunter2',
            'teach': 'The $6$ prefix names the algorithm, and the salt is stored in the open right after it.',
        },
        {
            'id': 'ckd-openssl-1',
            'type': 'command',
            'prompt': 'Produce an MD5-crypt hash of hunter2 with salt abcdefgh.',
            'answer': 'openssl passwd -1 -salt abcdefgh hunter2',
            'teach': '$1$ is MD5-crypt: obsolete, and still found in old configuration files everywhere.',
        },
        {
            'id': 'ckd-hashid',
            'type': 'command',
            'prompt': 'Ask a tool to identify the hash in hash.txt.',
            'answer': 'hashid hash.txt',
            'teach': 'It guesses from length and prefix, the same signals you can read. Reading them yourself is faster.',
        },
        {
            'id': 'ckd-hc-md5',
            'type': 'command',
            'prompt': 'Run hashcat against MD5 hashes in hashes.txt with rockyou.txt.',
            'answer': 'hashcat -m 0 -a 0 hashes.txt rockyou.txt',
            'teach': 'Hash mode, attack mode, hashes, wordlist. -m is what it is, -a is how you guess.',
        },
        {
            'id': 'ckd-hc-ntlm',
            'type': 'command',
            'prompt': 'Run hashcat against NTLM hashes in hashes.txt with rockyou.txt.',
            'answer': 'hashcat -m 1000 -a 0 hashes.txt rockyou.txt',
            'teach': '1000 is NTLM. Same 32 hex characters as MD5 and a completely different mode number.',
        },
        {
            'id': 'ckd-hc-bcrypt',
            'type': 'command',
            'prompt': 'Run hashcat against bcrypt hashes in hashes.txt with rockyou.txt.',
            'answer': 'hashcat -m 3200 -a 0 hashes.txt rockyou.txt',
            'teach': '3200 is bcrypt, and it will be many orders of magnitude slower than mode 0. That is the design working.',
        },
        {
            'id': 'ckd-hc-rules',
            'type': 'command',
            'prompt': 'Run hashcat on MD5 with rockyou.txt and the best64 rule file.',
            'answer': 'hashcat -m 0 -a 0 hashes.txt rockyou.txt -r rules/best64.rule',
            'teach': 'The highest value attack per unit of effort on almost any real hash set.',
        },
        {
            'id': 'ckd-hc-mask',
            'type': 'command',
            'prompt': 'Brute force MD5 hashes with a capital, four lowercase and three digits.',
            'answer': 'hashcat -m 0 -a 3 hashes.txt ?u?l?l?l?l?d?d?d',
            'teach': '?l ?u ?d ?s ?a ?b. A very common real password shape with a small enough keyspace to exhaust.',
        },
        {
            'id': 'ckd-hc-keyspace',
            'type': 'command',
            'prompt': 'Print how many candidates the mask ?a?a?a?a?a?a?a?a covers.',
            'answer': 'hashcat -a 3 --keyspace ?a?a?a?a?a?a?a?a',
            'teach': 'Check before you commit. Eight of ?a is not a plan, it is a number with too many digits.',
        },
        {
            'id': 'ckd-hc-hybrid',
            'type': 'command',
            'prompt': 'Attack MD5 with words.txt followed by four digits.',
            'answer': 'hashcat -m 0 -a 6 hashes.txt words.txt ?d?d?d?d',
            'teach': 'Hybrid mode: a real word plus a year, which describes most passwords ever chosen.',
        },
        {
            'id': 'ckd-hc-combinator',
            'type': 'command',
            'prompt': 'Attack MD5 by joining every word in a.txt to every word in b.txt.',
            'answer': 'hashcat -m 0 -a 1 hashes.txt a.txt b.txt',
            'teach': 'Combinator mode. Useful for two-word passphrases people think are clever.',
        },
        {
            'id': 'ckd-hc-show',
            'type': 'command',
            'prompt': 'Show what hashcat already cracked for MD5 hashes.txt.',
            'answer': 'hashcat -m 0 --show hashes.txt',
            'teach': 'The potfile again. Same trap as john and the same fix.',
        },
        {
            'id': 'ckd-hc-bench',
            'type': 'command',
            'prompt': 'Benchmark this machine against bcrypt.',
            'answer': 'hashcat -b -m 3200',
            'teach': 'Compare it against -m 0 and the entire argument for slow hashes is two numbers.',
        },
        {
            'id': 'ckd-cewl',
            'type': 'command',
            'prompt': 'Build a wordlist from example.com, depth 2, minimum six letters.',
            'answer': 'cewl -d 2 -m 6 https://example.com -w custom.txt',
            'teach': "A target's own vocabulary routinely finds what a generic list cannot.",
        },
        {
            'id': 'ckd-wc-rules',
            'type': 'command',
            'prompt': 'Count how many rules are in best64.rule.',
            'answer': 'wc -l rules/best64.rule',
            'teach': 'Multiply by your wordlist size to get the real keyspace before you start.',
        },
    ],
    'challenges': [
        {
            'id': 'ckc-identify',
            'title': 'Name five hashes on sight',
            'goal': 'Given a file of hashes in different formats, work out what each one is and write your answers down.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {
                    'hashes.txt': '5f4dcc3b5aa765d61d8327deb882cf99\n5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8\n$1$abcdefgh$vhxKZ/s1ygZHyCEDPyqtQ/\n$6$abcdefgh$M/eYsB4rVXAm3ZNc88J.UD9rCKAT6FB1\n$2b$12$LongSaltAndHashGoesRightHereOk\n',
                },
            },
            'solution': {
                'shell': 'printf "1 md5-or-ntlm 32 hex\\n2 sha1 40 hex\\n3 md5crypt \\$1\\$\\n4 sha512crypt \\$6\\$\\n5 bcrypt \\$2b\\$ cost 12\\n" > answers.txt',
            },
            'steps': [
                {
                    'instruction': 'Read hashes.txt and count the characters in the two bare hex lines.',
                    'hint': "awk '{print length($0), $0}' hashes.txt",
                },
                {
                    'instruction': 'Read the dollar prefixes on the other three. Each one names its own algorithm.',
                },
                {
                    'instruction': 'Write one line per hash into answers.txt naming the format, and for bcrypt include the cost.',
                },
            ],
            'free': 'Produce answers.txt identifying all five hashes by format, noting the bcrypt cost factor.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_contains': {
                        'answers.txt': [
                            'md5',
                            'sha1',
                            'bcrypt',
                            '12',
                        ],
                    },
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'ckc-salt',
            'title': 'Show what a salt does and does not do',
            'goal': 'Hash one password twice with different salts, and prove the outputs differ while the password did not.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {
                    '.keep': '',
                },
            },
            'solution': {
                'shell': 'openssl passwd -6 -salt aaaaaaaa hunter2 > salt-a.txt && openssl passwd -6 -salt bbbbbbbb hunter2 > salt-b.txt && openssl passwd -6 -salt aaaaaaaa hunter2 > salt-a-again.txt',
            },
            'steps': [
                {
                    'instruction': 'Hash hunter2 with salt aaaaaaaa into salt-a.txt.',
                    'hint': 'openssl passwd -6 -salt aaaaaaaa hunter2 > salt-a.txt',
                },
                {
                    'instruction': 'Hash the same password with salt bbbbbbbb into salt-b.txt.',
                },
                {
                    'instruction': 'Hash it a third time with the first salt into salt-a-again.txt, and compare all three.',
                    'hint': 'diff salt-a.txt salt-a-again.txt',
                },
            ],
            'free': 'Produce salt-a.txt, salt-b.txt and salt-a-again.txt: the same password hashed with two salts, and one of them repeated.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_contains': {
                        'salt-a.txt': '$6$aaaaaaaa$',
                        'salt-b.txt': '$6$bbbbbbbb$',
                        'salt-a-again.txt': '$6$aaaaaaaa$',
                    },
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'ckc-be-the-cracker',
            'title': 'Be the cracker',
            'goal': 'Write the loop yourself: candidate, hash, compare. Once you have, no cracking tool is mysterious again.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {
                    'target.txt': 'f52fbd32b2b3b86ff88ef6c490628285f482af15ddcb29541f94bcf526a3f6c7\n',
                    'words.txt': 'password\nletmein\nhunter2\ndragon\n',
                },
            },
            'solution': {
                'shell': 'target=$(cat target.txt) && while read w; do h=$(printf "%s" "$w" | sha256sum | cut -d" " -f1); echo "$w $h" >> tried.txt; if [ "$h" = "$target" ]; then echo "$w" > cracked.txt; fi; done < words.txt',
            },
            'steps': [
                {
                    'instruction': 'Read the SHA-256 in target.txt. That is the hash of one of the words in words.txt.',
                },
                {
                    'instruction': 'Loop over words.txt, hashing each candidate and logging the pair to tried.txt.',
                    'hint': 'printf "%s" "$w" | sha256sum | cut -d" " -f1',
                },
                {
                    'instruction': 'When a hash matches the target, write that word alone into cracked.txt.',
                    'hint': 'if [ "$h" = "$target" ]; then echo "$w" > cracked.txt; fi',
                },
                {
                    'instruction': 'You have now written hashcat. Everything else it does is speed and better guesses.',
                },
            ],
            'free': 'Produce tried.txt logging every candidate with its hash, and cracked.txt containing only the password that matched.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_equals': {
                        'cracked.txt': 'hunter2',
                    },
                    'file_contains': {
                        'tried.txt': [
                            'password',
                            'dragon',
                        ],
                    },
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'ckc-keyspace',
            'title': 'Work out whether the attack is even possible',
            'goal': 'Compute the size of three keyspaces and decide which of them is worth starting.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {
                    '.keep': '',
                },
            },
            'solution': {
                'shell': 'python3 -c "print(\'mask ?u?l?l?l?l?d?d?d\', 26*26**4*10**3); print(\'mask ?a x8\', 95**8); print(\'four dice words\', 7776**4)" > keyspace.txt && python3 -c "rate=1e10; print(\'seconds at 10G/s for ?a x8:\', 95**8/rate)" > estimate.txt',
            },
            'steps': [
                {
                    'instruction': 'Compute the keyspace of ?u?l?l?l?l?d?d?d: 26 uppercase, four lowercase, three digits.',
                    'hint': 'python3 -c "print(26*26**4*10**3)"',
                },
                {
                    'instruction': 'Compute 95 to the eighth for a fully random eight character password, and 7776 to the fourth for four dice words. Put all three in keyspace.txt.',
                },
                {
                    'instruction': 'Divide the largest by ten billion guesses per second and write the answer in seconds to estimate.txt.',
                },
                {
                    'instruction': 'Note which of the three is smallest. It is not the one that looks most complicated.',
                },
            ],
            'free': 'Produce keyspace.txt with three keyspace sizes and estimate.txt with a time estimate at ten billion guesses per second.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_contains': {
                        'keyspace.txt': [
                            'mask',
                            'dice',
                        ],
                        'estimate.txt': 'seconds',
                    },
                },
            },
            'fallback': 'self',
        },
    ],
    'quiz': [
        {
            'id': 'ckq-reverse',
            'type': 'mcq',
            'prompt': 'What does a cracking tool do with a hash?',
            'answer': 'Hashes candidate passwords and compares, until one matches.',
            'distractors': [
                'Reverses the hash function using its known structure.',
                "Looks the hash up in the algorithm's inverse table.",
                'Removes the salt and then decrypts the remainder.',
            ],
            'teach': 'Guessing, not reversing. Every other fact in this module follows from that one.',
        },
        {
            'id': 'ckq-salt-does',
            'type': 'mcq',
            'prompt': 'What does adding a salt prevent?',
            'answer': 'Precomputed tables, and seeing that two users share a password.',
            'distractors': [
                'Guessing attacks, by slowing each attempt down.',
                'The hash being cracked at all, once salted.',
                'GPUs from being used, since salts are sequential.',
            ],
            'teach': 'Salts kill precomputation. Cost parameters are what slow guessing, and they are a separate defence.',
        },
        {
            'id': 'ckq-bcrypt-cost',
            'type': 'mcq',
            'prompt': 'A bcrypt hash reads $2b$12$. What does the 12 mean?',
            'answer': 'A work factor of 2 to the 12 iterations.',
            'distractors': [
                'The salt length in bytes.',
                'The bcrypt version number.',
                'The maximum password length accepted.',
            ],
            'teach': 'Each increment doubles the cost per guess, for the attacker and for your login handler alike.',
        },
        {
            'id': 'ckq-m-vs-a',
            'type': 'mcq',
            'prompt': 'In hashcat, what is the difference between -m and -a?',
            'answer': '-m is what kind of hash it is, -a is how candidates are generated.',
            'distractors': [
                '-m is the mask, -a is the algorithm.',
                '-m sets memory limits, -a sets the attack rate.',
                'They are aliases, and either works.',
            ],
            'teach': 'Mode numbers describe the target, attack numbers describe your strategy. Mixing them is the classic first error.',
        },
        {
            'id': 'ckq-mask',
            'type': 'mcq',
            'prompt': 'What does the mask ?u?l?l?l?d?d describe?',
            'answer': 'One uppercase, three lowercase, two digits, in that order.',
            'distractors': [
                'Any password containing those character types.',
                'A wordlist filtered to that pattern.',
                'Six characters from the full printable set.',
            ],
            'teach': 'A mask is an exact description of the keyspace to enumerate, position by position.',
        },
        {
            'id': 'ckq-rules',
            'type': 'mcq',
            'prompt': 'Why does a rule file often beat a much larger wordlist?',
            'answer': 'It generates the predictable manglings humans apply to real words.',
            'distractors': [
                'It removes duplicate candidates before hashing.',
                'It reorders the wordlist by likelihood.',
                'It compresses the wordlist so more fits in memory.',
            ],
            'teach': 'Password1! is one rule, not a clever variation. Better guesses beat more guesses.',
        },
        {
            'id': 'ckq-length',
            'type': 'mcq',
            'prompt': 'Which is stronger: eight random printable characters, or four random dice words?',
            'answer': 'They are close, and six dice words is far beyond both.',
            'distractors': [
                'Eight characters, by a large margin, because of the symbols.',
                'Four words, by a large margin, because of the length.',
                'Neither: length and character set contribute equally.',
            ],
            'teach': '95^8 is about 6.6e15 and 7776^4 is about 3.7e15. Keyspace grows exponentially with length and only linearly with character set size.',
        },
    ],
}
