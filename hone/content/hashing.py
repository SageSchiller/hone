"""hashing: identity, integrity, and their limits.

A cryptographic hash is a fixed-length name for exact content: the same bytes
always give the same value, different bytes almost never do. That gives
identity (a name independent of filename and path) and integrity (compare now
against before). Sandbox-verified.

**Expanded from one lesson to four.** The module arrived from the D31 split of
the triage bundle as a single 1200-character lesson carrying six drills, which
is a reference card rather than a walkthrough. Everything it said was true and
none of it started at the beginning: it opened on "a cryptographic hash turns
any amount of data into a fixed length value", which is the sentence you write
for someone who already knows what a hash is.

The ramp now starts at what a hash even is and why one-way matters, and ends on
the places hashes stop working: fuzzy hashing, HMAC, and why password storage
is a different problem with a different tool. Anyone who already knows the
model can skip to lesson three and lose nothing.
"""

MODULE = {
    'context': 'You are at a shell prompt with an unknown file in front of you, and you will not run it.',
    'prereqs': [
        'linux',
        'linuxutils',
    ],
    'adapter': 'sandbox',
    'group': 'Security',
    'id': 'hashing',
    'title': 'hashing',
    'needs': [],
    'estimate': '2-3 hours',
    'order': 75,
    'blurb': 'What a digest is, identity and integrity, bulk verification, and where hashes stop.',
    'lessons': [
        {
            'id': 'tr-what',
            'title': 'What a hash actually is',
            'next': 'tr-hash',
            'concept': (
                'A hash is how you turn any amount of data into a fixed-size '
                'name for those exact bytes. That is why the same file hashes '
                'the same way on every machine, and why one changed bit looks '
                'nothing like the original. That is the whole interface, and '
                'three properties make it useful.\n\n'
                '**It is deterministic.** The same bytes always produce the '
                'same digest, on any machine, in any year, in any tool. This '
                'is the property everything else is built on.\n\n'
                '**It is one-way.** Given the digest you cannot work out the '
                'input. Not "it is hard", not "it takes a while": the output '
                'is smaller than the input, so the information is genuinely '
                'gone. You cannot un-hash something any more than you can '
                'un-print a fingerprint back into a person.\n\n'
                '**It avalanches.** Change one bit of the input and roughly '
                'half the output bits flip. There is no partial credit, no '
                '"close" digest, and no way to tell from two digests whether '
                'the files were nearly the same or entirely different.\n\n'
                'That last one surprises people, so it is worth doing once '
                'with your own hands: hash the word `hello`, then hash `hellp`, '
                'and look at how little the two results have in common.\n\n'
                '**A hash is not encryption.** Encryption has a key and is '
                'meant to be reversed by whoever holds it. A hash has no key '
                'and reverses for nobody, which is exactly why it is safe to '
                'publish one next to a download. The same digest does two '
                'different jobs, and keeping them apart is the next lesson.'
            ),
            'examples': [
                {
                    'label': 'One bit of difference',
                    'code': ('echo hello | sha256sum\n'
                             '5891b5b522d5df086d0ff0b110fbd9d2...\n'
                             '\n'
                             'echo hellp | sha256sum\n'
                             '9e5f0ad6c1a0e5d8e9c2ff9d0a09eae0...'),
                    'note': 'One letter changed. Nothing about the two '
                            'digests is closer than two random numbers would '
                            'be, and that is the design working.',
                },
                {
                    'label': 'Size in, size out',
                    'code': ('echo hi          | sha256sum   64 hex chars\n'
                             'cat 4gb-movie.mp4 | sha256sum   64 hex chars\n'
                             '\n'
                             '64 hex chars is 256 bits, always'),
                    'note': 'The digest length is a property of the algorithm '
                            'and has nothing to do with the input. SHA-256 is '
                            'named for it.',
                },
                {
                    'label': 'Hash, encryption, encoding',
                    'code': ('hash        one way, no key, fixed size\n'
                             'encryption  two way, needs a key\n'
                             'encoding    two way, no key, no secret\n'
                             '\n'
                             'base64 is encoding. It is not any\n'
                             'kind of protection and never was.'),
                    'note': 'These get muddled constantly. If someone says a '
                            'password was "encrypted with SHA-256", two of '
                            'those three words are wrong.',
                },
            ],
            'misconceptions': [
                'A hash cannot be reversed with the right tool. Cracking a '
                'hash means guessing inputs until one matches, which is a '
                'different activity with different limits.',
                'Hashing is not encryption. There is no key and no way back, '
                'which is a feature rather than a limitation.',
                'Two similar files do not have similar hashes. There is no '
                'such thing as a nearly-matching digest.',
            ],
            'try_it': [
                'Run `echo hello | sha256sum` and `echo hellp | sha256sum` and '
                'compare the two lines character by character.',
                'Hash a one-byte file and a large one, and confirm the output '
                'is the same length both times.',
            ],
        },
        {
            'id': 'tr-hash',
            'title': 'Identity and integrity, which are different jobs',
            'next': 'tr-verify',
            'concept': (
                'The same digest does two unrelated jobs, and keeping them '
                'apart is most of using hashes well.\n\n'
                '**Identity.** The hash is a name for exact content, '
                'independent of the filename, the path, the timestamps and '
                'the machine. It is how a malware sample is looked up, how '
                'two people confirm they are holding the same artefact, and '
                'what an indicator list is made of. Rename the file, move it '
                'to another continent, the name travels with the bytes.\n\n'
                '**Integrity.** Compare the hash now against the hash from '
                'before. Any difference means the bytes changed. This is the '
                'job that needs you to have written the hash down first, '
                'which is the part people skip and then regret.\n\n'
                'The output format matters more than it looks: the digest, '
                'two spaces, then the filename. That exact shape is what the '
                'verification tools read back, which is why every one of '
                'these commands prints the same layout.\n\n'
                'Anything on standard input can be hashed, which is how you '
                'fingerprint something with no file: a directory through '
                '`tar`, a download in flight, or the output of a command that '
                'you want to prove is stable. Comparing two hex strings by '
                'eye is how the integrity job goes wrong, and the next lesson '
                'is the check mode that replaces it.'
            ),
            'examples': [
                {
                    'label': 'The commands, and which one to reach for',
                    'code': ('sha256sum sample.bin     the default answer\n'
                             'md5sum sample.bin        fast, broken, still '
                             'everywhere\n'
                             'sha1sum sample.bin       also broken, also '
                             'everywhere\n'
                             '\n'
                             'all three print HASH  FILENAME'),
                    'note': 'md5 is cryptographically dead and still the '
                            'format every malware feed and every old advisory '
                            'quotes, so you read it far more than you write '
                            'it.',
                },
                {
                    'label': 'Identify a file by content',
                    'code': 'sha256sum sample.bin',
                    'note': 'The digest, then two spaces, then the name. That '
                            'exact format is what -c reads back.',
                },
                {
                    'label': 'Hash a stream, not a file',
                    'code': ('tar cf - dir/ | sha256sum\n'
                             'curl -s https://host/file | sha256sum'),
                    'note': 'Anything on stdin can be hashed, which is how a '
                            'directory or a download in flight gets a '
                            'fingerprint without touching the disk.',
                },
            ],
            'misconceptions': [
                'Identity and integrity are not the same use. Identity needs '
                'only the hash you have; integrity needs a hash somebody '
                'recorded before the thing you are worried about happened.',
                'The filename is not part of what is hashed. It is printed '
                'beside the digest, and hashing the same bytes under two '
                'names gives one digest twice.',
                'A published hash next to a download on the same server '
                'proves very little. Whoever replaced the file could replace '
                'the hash beside it.',
            ],
            'try_it': [
                'Hash a file, copy it to a new name, and hash the copy. Note '
                'that only the right-hand column changed.',
                'Hash a directory as a stream with `tar cf - dir/ | '
                'sha256sum`, add a file, and do it again.',
            ],
        },
        {
            'id': 'tr-verify',
            'title': 'Verifying in bulk, without reading hex',
            'next': 'tr-limits',
            'concept': (
                '`sha256sum -c` is how you verify a directory against a '
                'checksum file, without reading hex. That is why a FAILED '
                'line is something a script can act on, and a pair of hex '
                'strings by eye is not.\n\n'
                'Comparing two digests by eye is a job nobody does correctly '
                'twice. Every hash tool has a check mode for exactly this '
                'reason, and using it is the difference between an integrity '
                'process and a ritual.\n\n'
                '`sha256sum * > SHA256SUMS` writes the whole directory down. '
                '`sha256sum -c SHA256SUMS` reads that file back and prints OK '
                'or FAILED per entry, with an exit code you can act on. That '
                'is the entire workflow, and the hard part is remembering to '
                'run the first half early.\n\n'
                '`--quiet` prints only the failures, which is what you want '
                'over a thousand files or inside a script: silence is '
                'success. `--status` prints nothing at all and reports purely '
                'through the exit code, which is what you want inside an if '
                'statement.\n\n'
                '**The filename is part of the line, and that has teeth.** '
                'Rename a file and `-c` reports it missing rather than '
                'mismatched, which are different problems with different '
                'causes. Paths are recorded exactly as you typed them, so a '
                'checksum file written with `sha256sum evidence/*` only '
                'verifies from the directory above.'
            ),
            'examples': [
                {
                    'label': 'Record now, verify later',
                    'code': ('sha256sum * > SHA256SUMS\n'
                             'sha256sum -c SHA256SUMS'),
                    'note': 'Prints OK or FAILED per file. The right way to '
                            'check a directory, and the only way that scales '
                            'past about three files.',
                },
                {
                    'label': 'Only report problems',
                    'code': ('sha256sum -c --quiet SHA256SUMS\n'
                             '  evidence/two.txt: FAILED\n'
                             '\n'
                             'sha256sum -c --status SHA256SUMS\n'
                             '  (nothing; check $? instead)'),
                    'note': '--quiet for a human watching, --status for an if '
                            'statement. Both exit non-zero when anything '
                            'failed.',
                },
                {
                    'label': 'Where the paths bite',
                    'code': ('cd evidence && sha256sum * > ../SUMS\n'
                             '  records: one.txt, two.txt\n'
                             '\n'
                             'sha256sum evidence/* > SUMS\n'
                             '  records: evidence/one.txt, ...'),
                    'note': 'The second only verifies from the parent '
                            'directory. Neither is wrong; they are different '
                            'files and you have to run -c from the matching '
                            'place.',
                },
            ],
            'misconceptions': [
                'A FAILED line does not mean the file is corrupt. It means '
                'the bytes differ from what was recorded, which includes '
                'someone legitimately editing it.',
                '`-c` reporting "No such file or directory" is usually a '
                'working directory problem, not a missing file. The paths in '
                'the checksum file are relative to where you run it.',
                'A checksum file protects nothing on its own. It is a '
                'record, and a record stored next to the thing it describes '
                'can be rewritten by whoever rewrote the thing.',
            ],
            'try_it': [
                'Write a SHA256SUMS file for a directory, modify one file, and '
                'run the check. Note which line says FAILED.',
                'Run the same check with `--quiet`, then `--status`, and print '
                '`$?` after each.',
            ],
        },
        {
            'id': 'tr-limits',
            'title': 'Where hashes stop working',
            'concept': (
                'A hash stops being proof the moment someone can force a '
                'collision, or the moment you needed similarity rather than '
                'identity. That is why MD5 is still a lookup key and no '
                'longer tamper evidence, and why passwords need a different '
                'tool.\n\n'
                '**MD5 and SHA-1 are broken for collision resistance.** An '
                'adversary can construct two different files with the same '
                'digest, and this is not theoretical: it has been '
                'demonstrated with real PDFs and a real certificate. They '
                'remain perfectly fine as lookup keys, because looking '
                'something up in a feed is not an adversarial operation. They '
                'are useless as proof that nobody swapped the file.\n\n'
                'It is worth separating two attacks that get conflated. A '
                '**collision** is finding any two inputs with the same digest, '
                'and MD5 fell to this long ago. A **preimage** is finding an '
                'input matching a digest you were given, which is much harder '
                'and has not fallen even for MD5. That is why an old MD5 in a '
                'threat feed is still a usable identifier.\n\n'
                '**Fuzzy hashing exists because normal hashing avalanches.** '
                'ssdeep and TLSH produce digests that stay similar when the '
                'input stays similar, which is how you find variants of a '
                'sample rather than exact copies. They are not '
                'cryptographic and are not trying to be.\n\n'
                '**An HMAC is a hash plus a key**, and it answers a question a '
                'bare hash cannot: not just "did this change" but "was this '
                'written by someone holding the secret". A published hash '
                'proves nothing about origin; an HMAC does.\n\n'
                '**Password storage is a different problem entirely.** Fast is '
                'the whole point of SHA-256 and exactly the wrong property '
                'for a password, where you want each guess to be expensive. '
                'That is what bcrypt, scrypt and argon2 are for, and the '
                'hashcat module is where that story continues.'
            ),
            'examples': [
                {
                    'label': 'Two attacks, very different difficulty',
                    'code': ('collision   find ANY two inputs that match\n'
                             '            MD5: done in seconds\n'
                             '            SHA-1: done, expensively\n'
                             '\n'
                             'preimage    find an input matching THIS digest\n'
                             '            MD5: still not feasible'),
                    'note': 'This is why an MD5 from a 2011 advisory is still '
                            'a usable lookup key while being worthless as '
                            'tamper evidence.',
                },
                {
                    'label': 'When you want similarity, not identity',
                    'code': ('sha256sum a.exe b.exe\n'
                             '  two unrelated numbers, always\n'
                             '\n'
                             'ssdeep -b a.exe b.exe\n'
                             '  a match score, 0 to 100'),
                    'note': 'Fuzzy hashing is how you spot the repacked '
                            'variant of a sample. Do not reach for it where '
                            'you need proof of anything.',
                },
                {
                    'label': 'The right tool per question',
                    'code': ('did this change?          sha256sum\n'
                             'is this the same sample?  sha256sum, or md5\n'
                             'is this a variant?        ssdeep\n'
                             'did YOU write this?       HMAC, or a signature\n'
                             'store a password          argon2, bcrypt'),
                    'note': 'Only the first two are this module. The last one '
                            'is the mistake with the worst consequences and '
                            'the least obvious symptoms.',
                },
            ],
            'misconceptions': [
                'MD5 matching does not prove a file is unmodified. Collisions '
                'are constructible, and that is the whole reason to use '
                'SHA-256 where an adversary is involved.',
                'SHA-256 is not a password hash. It is fast by design, and '
                'fast is the property an attacker guessing passwords wants '
                'you to have chosen.',
                'A hash is not a signature. It proves the content is '
                'unchanged since the hash was taken and says nothing '
                'whatever about who took it.',
            ],
            'try_it': [
                'Hash a file, change one byte with xxd, and hash it again. '
                'Then decide honestly whether you could have spotted the '
                'difference by eye across a room.',
                'Look up any malware advisory and count how many of the '
                'indicators are MD5. That is why the format outlived its '
                'security.',
            ],
        },
    ],
    'drills': [
        {
            'id': 'trd-sha256',
            'type': 'command',
            'prompt': 'Compute the SHA-256 of sample.bin.',
            'answer': 'sha256sum sample.bin',
            'teach': 'Digest, two spaces, name. That exact format is what -c reads back later.',
        },
        {
            'id': 'trd-sha256-record',
            'type': 'command',
            'prompt': 'Record checksums of every file here into SHA256SUMS.',
            'answer': 'sha256sum * > SHA256SUMS',
            'teach': 'Recording before you touch anything is the cheap half of integrity. Verifying is the other half.',
        },
        {
            'id': 'trd-sha256-check',
            'type': 'command',
            'prompt': 'Verify every entry in SHA256SUMS.',
            'answer': 'sha256sum -c SHA256SUMS',
            'teach': 'Prints OK or FAILED per file, which is better than comparing hex by eye.',
        },
        {
            'id': 'trd-sha256-quiet',
            'type': 'command',
            'prompt': 'Verify SHA256SUMS reporting only the failures.',
            'answer': 'sha256sum -c --quiet SHA256SUMS',
            'teach': 'Silence is success. What you want over a thousand files or inside a script.',
        },
        {
            'id': 'trd-sha256-status',
            'type': 'command',
            'prompt': 'Verify SHA256SUMS silently, reporting only through the exit code.',
            'answer': 'sha256sum -c --status SHA256SUMS',
            'teach': 'No output at all. The form to put inside an if statement, where printing would be noise.',
        },
        {
            'id': 'trd-hash-stream',
            'type': 'command',
            'prompt': 'Hash the contents of the directory dir as a single stream.',
            'answer': 'tar cf - dir/ | sha256sum',
            'teach': 'Anything on stdin can be hashed, which is how a directory or a download in flight gets a fingerprint.',
        },
        {'id': 'hshd-md5', 'type': 'command',
         'answer': 'md5sum sample.bin',
         'prompt': 'Compute the MD5 of a file, to use as a lookup key.',
         'teach': 'Fine for looking something up in a threat-intel set, and not fine for proving nobody tampered with it.'},
    ],
    'challenges': [
        {
            'id': 'trc-hash-record',
            'title': 'Record integrity, then prove it broke',
            'goal': 'Take hashes of a directory, change one byte, and show the check catching exactly that file.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {
                    'evidence/one.txt': 'first file\n',
                    'evidence/two.txt': 'second file\n',
                    'evidence/three.txt': 'third file\n',
                },
            },
            'solution': {
                'shell': 'cd evidence && sha256sum *.txt > ../SHA256SUMS && cd .. && echo tampered >> evidence/two.txt && cd evidence && sha256sum -c ../SHA256SUMS > ../check.txt 2>&1; true',
            },
            'steps': [
                {
                    'instruction': 'Record SHA-256 for every file in evidence/ into SHA256SUMS at the top level.',
                    'hint': 'cd evidence && sha256sum *.txt > ../SHA256SUMS',
                },
                {
                    'instruction': 'Now change one of those files.',
                    'hint': 'echo tampered >> evidence/two.txt',
                },
                {
                    'instruction': 'Run the check and save its output to check.txt. Expect one FAILED and two OK.',
                    'hint': 'sha256sum -c ../SHA256SUMS > ../check.txt 2>&1',
                },
            ],
            'free': 'Produce SHA256SUMS for evidence/, tamper with one file, and capture the verification output in check.txt showing which file failed.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'is_file': [
                        'SHA256SUMS',
                        'check.txt',
                    ],
                    'file_contains': {
                        'check.txt': [
                            'two.txt',
                            'FAILED',
                        ],
                    },
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'trc-avalanche',
            'title': 'Prove the avalanche to yourself',
            'goal': 'Hash two files that differ by one character and record both digests, so the "no such thing as a close hash" claim stops being something you were told.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {
                    'a.txt': 'hello\n',
                    'b.txt': 'hellp\n',
                },
            },
            'solution': {
                'shell': 'sha256sum a.txt b.txt > digests.txt',
            },
            'steps': [
                {
                    'instruction': 'The two files differ by exactly one letter. Confirm that first if you like.',
                    'hint': 'diff a.txt b.txt',
                },
                {
                    'instruction': 'Hash both files in one command and write the result to digests.txt.',
                    'hint': 'sha256sum a.txt b.txt > digests.txt',
                },
                {
                    'instruction': 'Read the two lines and find the longest run of characters they have in common.',
                },
            ],
            'free': 'Produce digests.txt containing the SHA-256 of both files, then look at how little the two digests share.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_contains': {
                        'digests.txt': [
                            'a.txt',
                            'b.txt',
                        ],
                    },
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'trc-identity',
            'title': 'Same bytes, two names, one digest',
            'goal': 'The filename is not part of the hash. Copy a file, hash both, and show the two digests match.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {
                    'original.txt': 'payload\n',
                },
            },
            'solution': {
                'shell': 'cp original.txt copy.txt && sha256sum original.txt copy.txt > pair.txt',
            },
            'steps': [
                {
                    'instruction': 'Copy original.txt to copy.txt so the same bytes have two names.',
                    'hint': 'cp original.txt copy.txt',
                },
                {
                    'instruction': 'Hash both files in one command and write the result to pair.txt.',
                    'hint': 'sha256sum original.txt copy.txt > pair.txt',
                },
                {
                    'instruction': 'Read the two lines. Only the name column should differ.',
                },
            ],
            'free': 'Produce pair.txt containing the SHA-256 of original.txt and of a copy named copy.txt.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'is_file': [
                        'copy.txt',
                        'pair.txt',
                    ],
                    'file_contains': {
                        'pair.txt': [
                            'd4e4877bac978b7952f0d544fc52ebff5411d351d129f1f056fa43f11da9af2b',
                            'original.txt',
                            'copy.txt',
                        ],
                    },
                },
            },
            'fallback': 'self',
        },
    ],
    'quiz': [
        {
            'id': 'trq-md5',
            'type': 'mcq',
            'prompt': 'Two files have the same MD5. What can you conclude?',
            'answer': 'Probably the same content, but MD5 collisions are constructible, so it is not proof.',
            'distractors': [
                'They are definitely identical byte for byte.',
                'They are definitely different, since MD5 is broken.',
                'Nothing at all: MD5 is random with respect to content.',
            ],
            'teach': 'MD5 and SHA-1 remain fine as lookup identifiers and are useless where an adversary is involved. SHA-256 otherwise.',
        },
        {
            'id': 'trq-reverse',
            'type': 'mcq',
            'prompt': 'Someone asks you to "decrypt" a SHA-256 hash back to the original file. What is the honest answer?',
            'answer': 'It cannot be done. The information is gone, and cracking means guessing inputs until one matches.',
            'distractors': [
                'It needs the key the hash was made with.',
                'It is possible but computationally expensive for large files.',
                'Only if you know which algorithm was used.',
            ],
            'teach': 'A hash has no key and no inverse. The output is smaller than the input, so the missing information is genuinely missing.',
        },
        {
            'id': 'trq-similar',
            'type': 'mcq',
            'prompt': 'Two malware samples are the same family, repacked. How do their SHA-256 digests compare?',
            'answer': 'Completely different, as unrelated as two random numbers.',
            'distractors': [
                'Similar, with a shared prefix reflecting the shared code.',
                'Identical, since the behaviour is the same.',
                'Similar in length but not content.',
            ],
            'teach': 'This is what ssdeep and TLSH exist for. A cryptographic hash avalanches on purpose and cannot express similarity.',
        },
        {
            'id': 'trq-password',
            'type': 'mcq',
            'prompt': 'Why is SHA-256 a poor choice for storing passwords?',
            'answer': 'It is fast, which makes guessing cheap for an attacker.',
            'distractors': [
                'It is reversible if you have the salt.',
                'Its collisions are constructible, so two passwords can match.',
                'It produces digests that are too short.',
            ],
            'teach': 'Speed is the right property for checking a file and the wrong one for a password. argon2, bcrypt and scrypt are slow deliberately.',
        },
        {
            'id': 'trq-check-fail',
            'type': 'mcq',
            'prompt': 'sha256sum -c reports "No such file or directory" for every entry. What is the likely cause?',
            'answer': 'You are running it from a different directory than the one the paths were recorded in.',
            'distractors': [
                'The checksum file was written with a different algorithm.',
                'The files were deleted after the checksums were taken.',
                'The checksum file is corrupt and must be regenerated.',
            ],
            'teach': 'Paths are stored exactly as typed. A file written with `sha256sum evidence/*` only verifies from the parent directory.',
        },
    ],
}
