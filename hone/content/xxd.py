"""xxd: reading raw bytes, and finding what hides after the end.

xxd shows a file as hex with offsets, which is how you read a signature, seek into a disk image with -s and -l, and reverse a dump back into bytes with -r. It pairs with the carving story: most formats ignore whatever follows their own end marker, so a ZIP appended to an image is invisible to a viewer and sitting on disk, found by hunting a signature at a non-zero offset. Sandbox-verified.
"""

MODULE = {
    'context': 'You are at a shell prompt with an unknown file in front of you, and you will not run it.',
    'prereqs': [
        'linux',
        'linuxutils',
    ],
    'adapter': 'sandbox',
    'group': 'Security',
    'id': 'xxd',
    'title': 'xxd',
    'needs': [
        'xxd',
    ],
    'estimate': '2 hours',
    'order': 72,
    'blurb': 'Hex dumps, offsets, reversing a dump, and carving data hidden after EOF.',
    'lessons': [
        {
            'id': 'tr-hex',
            'title': 'Reading bytes: xxd, offsets, and where things start',
            'concept': 'A hex dump has three columns: the offset, the bytes, and the printable rendering. All three matter, and the offset is the one people ignore and then need.\n\nOffsets are hex by default, which means a length in the dump and a length from `ls` do not look alike until you convert. That is worth practising, because "the second file starts at 0x1A2B" is how carving and appended data get discussed.\n\n-l limits how much you read, which matters when the file is a gigabyte. -s seeks to an offset, and takes a negative number to seek from the end, which is the fastest way to look at a trailer. -p prints plain hex with no columns, which is what you want when feeding another tool.\n\nxxd is also reversible: -r turns a dump back into bytes. That makes it a byte editor of last resort, and a useful way to build a test file with an exact signature.\n\n`od -A d -t x1z` does the same job with decimal offsets, and `hexdump -C` is the BSD spelling most people learned first. Any of the three is fine; knowing that -s and -l exist is the part that saves time.',
            'examples': [
                {
                    'label': 'The first line is usually enough',
                    'code': 'xxd -l 32 unknown.bin',
                    'note': 'Signature, and often a version or a length field right behind it.',
                },
                {
                    'label': 'Look at the end of the file',
                    'code': 'xxd -s -64 archive.dat',
                    'note': 'Negative seek is from EOF. ZIP keeps its central directory there, which is why appended ZIPs work.',
                },
                {
                    'label': 'Start reading at a known offset',
                    'code': 'xxd -s 0x1000 -l 64 image.raw',
                    'note': 'Offsets take hex directly, which saves converting by hand.',
                },
                {
                    'label': 'Hex out, bytes back in',
                    'code': 'xxd -p file.bin > hex.txt; xxd -r -p hex.txt > copy.bin',
                    'note': 'Round trip. -p is the plain form with no offsets or ASCII column.',
                },
            ],
            'misconceptions': [
                'The offset column is hexadecimal. Comparing it to a decimal byte count without converting is a common and confusing error.',
                'The right hand column is not text. It is every byte that happens to be printable, and a dot for every byte that is not.',
                'xxd -r needs -p if the dump was made with -p. The two forms are not interchangeable.',
            ],
            'try_it': [
                'Dump the last 64 bytes of a ZIP file and find the PK 05 06 end-of-central-directory signature.',
                'Use xxd -r -p to build a file whose first four bytes make file report it as a PNG.',
            ],
            'next': 'tr-embedded',
        },
        {
            'id': 'tr-embedded',
            'title': 'What is hiding after the end of the file',
            'concept': 'Most formats do not care what follows their own data. A JPEG decoder stops at the end-of-image marker. A PNG viewer stops at IEND. Anything after that is ignored by the viewer and is still on disk, which is why appending a ZIP to an image is the oldest trick in the collection and still works.\n\nZIP makes it especially easy, because a ZIP reader locates the archive from the end of the file rather than the start. So one file can be a valid image to one program and a valid archive to another, with no conflict. Those are polyglots, and they are why "file says PNG" is a start rather than a conclusion.\n\nTwo habits catch nearly all of it. First, compare the declared structure to the actual size: if the image ends at byte 40,000 and the file is 900,000 bytes, ask what the rest is. Second, look for signatures at offsets other than zero, which is what `binwalk` automates and what `grep -abo` does by hand for a specific one.\n\nCarving is the extraction step, and `dd` with skip and count is the primitive underneath every tool that does it.',
            'examples': [
                {
                    'label': 'Find a signature anywhere in the file',
                    'code': 'grep -abo "PK" cover.png | head',
                    'note': '-a treats binary as text, -b prints byte offsets, -o prints only the match. Offsets in decimal.',
                },
                {
                    'label': 'Scan for every embedded format',
                    'code': 'binwalk cover.png',
                    'note': 'The automated version. Reports signature and offset for each thing it recognises.',
                },
                {
                    'label': 'Cut a region out by hand',
                    'code': 'dd if=cover.png of=hidden.zip bs=1 skip=40960 status=none',
                    'note': 'skip is where to start, count is how much. This is what carving actually is.',
                },
                {
                    'label': 'Let the archive tool find its own start',
                    'code': 'unzip cover.png',
                    'note': 'Often just works, because ZIP is read from the end and the reader adjusts for the offset.',
                },
            ],
            'misconceptions': [
                'A file that opens correctly is not therefore only what it appears to be. Decoders stop at their own end marker.',
                'grep -b prints decimal byte offsets, while xxd offsets are hex. Mixing them up loses ten minutes reliably.',
                'binwalk reporting a signature is not proof of an embedded file. Short signatures match by chance in large files.',
            ],
            'try_it': [
                'Append a ZIP to a PNG with cat, and check that both a viewer and unzip still handle it.',
                'Find the offset of the appended data with grep -abo, and carve it out with dd.',
            ],
            'next': None,
        },
    ],
    'drills': [
        {
            'id': 'trd-xxd-head',
            'type': 'command',
            'prompt': 'Show the first 16 bytes of unknown.bin as hex.',
            'answer': 'xxd -l 16 unknown.bin',
            'teach': 'The signature lives at the start. One line usually settles the format question.',
        },
        {
            'id': 'trd-xxd-tail',
            'type': 'command',
            'prompt': 'Show the last 64 bytes of archive.dat.',
            'answer': 'xxd -s -64 archive.dat',
            'teach': 'A negative seek is from the end. ZIP keeps its central directory there, which is why appended archives work.',
        },
        {
            'id': 'trd-xxd-offset',
            'type': 'command',
            'prompt': 'Dump 64 bytes of image.raw starting at offset 0x1000.',
            'answer': 'xxd -s 0x1000 -l 64 image.raw',
            'teach': 'Offsets take hex directly, so a finding from grep -b needs converting and one from xxd does not.',
        },
        {
            'id': 'trd-xxd-plain',
            'type': 'command',
            'prompt': 'Print file.bin as plain hex with no offsets or ASCII column.',
            'answer': 'xxd -p file.bin',
            'teach': 'The form other tools can read, and the form xxd -r -p turns back into bytes.',
        },
        {
            'id': 'trd-xxd-revert',
            'type': 'command',
            'prompt': 'Turn the plain hex in hex.txt back into bytes in copy.bin.',
            'answer': 'xxd -r -p hex.txt > copy.bin',
            'teach': 'Reversible, which makes xxd a byte editor of last resort and a way to build an exact test file.',
        },
        {
            'id': 'trd-grep-offset',
            'type': 'command',
            'prompt': 'Find every byte offset where PK appears inside cover.png.',
            'answer': 'grep -abo "PK" cover.png',
            'teach': '-a treats binary as text, -b gives byte offsets in decimal, -o prints only the match.',
        },
        {
            'id': 'trd-binwalk',
            'type': 'command',
            'prompt': 'Scan cover.png for embedded file signatures.',
            'answer': 'binwalk cover.png',
            'teach': 'The automated version of hunting signatures at non-zero offsets. Short signatures do match by chance.',
        },
        {
            'id': 'trd-dd-carve',
            'type': 'command',
            'prompt': 'Carve everything from byte 40960 of cover.png into hidden.zip.',
            'answer': 'dd if=cover.png of=hidden.zip bs=1 skip=40960 status=none',
            'teach': 'skip is where to start, count is how much. This is what every carving tool does underneath.',
        },
    ],
    'challenges': [
        {
            'id': 'trc-appended',
            'title': 'Find what is after the end of the image',
            'goal': 'A file that opens as an image and is bigger than an image should be. Locate the second file inside it and carve it out.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {
                    # A real PNG with a real ZIP appended. It has to be real:
                    # the point of the lesson is that `file` says PNG and a
                    # zip tool still finds the archive, and neither is true of
                    # a hand-typed imitation.
                    'cover.png': {'b64': 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCCUEsDBBQAAAAAACmfDV11V9s5DAAAAAwAAAAKAAAAc2VjcmV0LnR4dHRoZSBwYXlsb2FkClBLAQIUAxQAAAAAACmfDV11V9s5DAAAAAwAAAAKAAAAAAAAAAAAAACAAQAAAABzZWNyZXQudHh0UEsFBgAAAAABAAEAOAAAADQAAAAAAA=='},
                },
            },
            'solution': {
                'shell': 'grep -abo PK cover.png > offsets.txt && off=$(head -1 offsets.txt | cut -d: -f1) && dd if=cover.png of=hidden.zip bs=1 skip=$off status=none',
            },
            'steps': [
                {
                    'instruction': 'Confirm what file thinks cover.png is, then look at its size.',
                    'hint': 'file cover.png; ls -l cover.png',
                },
                {
                    'instruction': 'Find every byte offset where a ZIP signature appears, saving them to offsets.txt.',
                    'hint': 'grep -abo PK cover.png > offsets.txt',
                },
                {
                    'instruction': 'Carve from that offset to the end of the file into hidden.zip.',
                    'hint': 'dd if=cover.png of=hidden.zip bs=1 skip=OFFSET status=none',
                },
            ],
            'free': 'Produce offsets.txt with the ZIP signature offsets in cover.png, and hidden.zip carved from the first of them.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'is_file': [
                        'offsets.txt',
                        'hidden.zip',
                    ],
                    'file_contains': {
                        # Carved correctly, hidden.zip is a working archive
                        # whose member is readable, and carries none of the
                        # PNG that preceded it.
                        'hidden.zip': 'secret.txt',
                    },
                    'file_lacks': {
                        'hidden.zip': 'IHDR',
                    },
                },
            },
            'fallback': 'self',
        },
    ],
    'quiz': [
        {
            'id': 'trq-offsets',
            'type': 'mcq',
            'prompt': 'grep -abo says PK is at 40960 and you want to dump it with xxd. What do you have to watch?',
            'answer': 'grep offsets are decimal and xxd offsets default to hex.',
            'distractors': [
                'grep counts from 1 and xxd counts from 0.',
                'grep offsets are relative to the match, not the file.',
                'xxd cannot seek past 32768 without -s in hex.',
            ],
            'teach': 'xxd -s takes 0x prefixed hex or plain decimal. Mixing the bases silently gives you the wrong region.',
        },
        {
            'id': 'trq-polyglot',
            'type': 'mcq',
            'prompt': 'A PNG opens correctly in a viewer and unzip also extracts files from it. How?',
            'answer': 'The ZIP was appended: the viewer stops at IEND and the ZIP reader works backwards from the end.',
            'distractors': [
                'The file is corrupt and both tools are guessing.',
                'PNG chunks can legally contain a ZIP archive.',
                'unzip is reading a different file with the same inode.',
            ],
            'teach': 'Most decoders stop at their own end marker and ignore what follows, which is why the trick is decades old and still works.',
        },
    ],
}
