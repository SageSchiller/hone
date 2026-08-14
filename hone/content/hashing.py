"""hashing: identity, integrity, and their limits.

A cryptographic hash is a fixed-length name for exact content: the same bytes always give the same value, different bytes almost never do. That gives identity (a name independent of filename and path) and integrity (compare now against before). sha256sum -c checks a whole directory at once. Which algorithm matters: MD5 and SHA-1 are broken for proving nobody tampered, fine as lookups. Sandbox-verified.
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
    'estimate': '1-2 hours',
    'order': 75,
    'blurb': 'sha256sum for identity and integrity, -c to verify, and why MD5 is not enough.',
    'lessons': [
        {
            'id': 'tr-hash',
            'title': 'Hashes: identity, integrity, and their limits',
            'concept': 'A cryptographic hash turns any amount of data into a fixed length value, such that the same bytes always give the same value and different bytes almost never do. That gives two distinct uses, and they are worth separating.\n\n**Identity.** The hash is a name for the exact content, independent of the filename, the path and the timestamps. It is how a sample is looked up, how two people confirm they have the same artefact, and what an indicator list contains.\n\n**Integrity.** Compare the hash now with the hash from before, and any difference means the bytes changed. `sha256sum -c` reads a checksum file and reports each entry as OK or FAILED, which is the right way to do this in bulk rather than comparing strings by eye.\n\nWhich algorithm matters. MD5 and SHA-1 are broken for collision resistance: an adversary can construct two different files with the same digest. They remain fine as identifiers for looking things up, and they are useless as proof that nobody swapped the file. SHA-256 is the default answer for anything where an adversary is involved.\n\nWhat a hash cannot do is tell you that two similar files are similar: one flipped bit changes everything. That is what fuzzy hashing, ssdeep and TLSH, exists for.',
            'examples': [
                {
                    'label': 'Identify a file by content',
                    'code': 'sha256sum sample.bin',
                    'note': 'The digest, then two spaces, then the name. That exact format is what -c reads back.',
                },
                {
                    'label': 'Record now, verify later',
                    'code': 'sha256sum * > SHA256SUMS\nsha256sum -c SHA256SUMS',
                    'note': 'Prints OK or FAILED per file. The right way to check a directory.',
                },
                {
                    'label': 'Only report problems',
                    'code': 'sha256sum -c --quiet SHA256SUMS',
                    'note': 'Silence is success. Useful in a script or over a thousand files.',
                },
                {
                    'label': 'Hash a stream, not a file',
                    'code': 'tar cf - dir/ | sha256sum',
                    'note': 'Anything on stdin can be hashed, which is how you fingerprint a directory or a download in flight.',
                },
            ],
            'misconceptions': [
                'MD5 matching does not prove a file is unmodified. Collisions are constructible, and that is the whole reason to use SHA-256.',
                'A hash says nothing about similarity. One changed byte gives a completely different digest, by design.',
                'The filename is part of the line: rename the file and -c reports it missing rather than mismatched, and a trailing space becomes part of the name rather than to match.',
            ],
            'try_it': [
                'Hash a file, change one byte with xxd, and hash it again.',
                'Write a SHA256SUMS file for a directory, modify one file, and run the check.',
            ],
            'next': None,
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
    ],
}
