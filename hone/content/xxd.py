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
    'order': 74,
    'blurb': 'Hex dumps, offsets, reversing a dump, and carving data hidden after EOF.',
    'lessons': [
        {
            'id': 'tr-bytes',
            'title': 'Bytes, hex, and why anyone counts in sixteens',
            'next': 'tr-hex',
            'concept': (
                'Everything on a disk is bytes, and a byte is a number from 0 '
                'to 255. A text file is bytes that happen to be letters. A '
                'PNG is bytes that happen to describe pixels. There is no '
                'other kind of file, and a hex dump is simply those numbers '
                'written down where you can see them.\n\n'
                '**Hexadecimal is base 16**, using 0 to 9 and then a to f for '
                'ten to fifteen. It exists here for one reason: a byte is '
                'exactly two hex digits, every time. In decimal a byte is one, '
                'two or three digits and the columns never line up; in hex a '
                'thousand bytes is a thousand tidy pairs. That is the whole '
                'argument, and it is enough.\n\n'
                'So `41` is one byte, decimal 65, which in ASCII is the '
                'letter A. `00` is a zero byte. `ff` is 255, the largest a '
                'byte goes. If you learn three landmarks, `20` is a space, '
                '`0a` is a newline, and `41` is A, you can read a surprising '
                'amount of a dump without a table.\n\n'
                '**ASCII is the map from bytes to characters** for the first '
                '128 values, and the useful pattern is that the letters are '
                'contiguous: A to Z is 41 to 5a, a to z is 61 to 7a. Upper '
                'and lower case differ by exactly one bit, which is why '
                'flipping case is cheap and why `20` keeps turning up.\n\n'
                'A hex dump is not a decoding of anything. It is the file, '
                'written in a base that fits the page. Reading that dump, and '
                'seeking to a place in it, is the next lesson.'
            ),
            'examples': [
                {
                    'label': 'One line of a dump, taken apart',
                    'code': ('00000000: 4865 6c6c 6f0a                 Hello.\n'
                             '\\______/  \\__________/                 \\____/\n'
                             ' offset      the bytes              printable\n'
                             '\n'
                             '48=H 65=e 6c=l 6c=l 6f=o 0a=newline'),
                    'note': 'The dot on the right is not a full stop in the '
                            'file. It is how the printable column draws a '
                            'byte that has no printable character.',
                },
                {
                    'label': 'Why hex and not decimal',
                    'code': ('decimal   72 101 108 108 111 10\n'
                             'hex       48  65  6c  6c  6f 0a\n'
                             '\n'
                             'the same bytes. one of these\n'
                             'lines up in columns forever.'),
                    'note': 'Two hex digits is exactly one byte, always. That '
                            'single property is why every dump, every debugger '
                            'and every protocol spec uses it.',
                },
                {
                    'label': 'Landmarks worth memorising',
                    'code': ('00   a zero byte, padding, terminator\n'
                             '20   a space\n'
                             '0a   newline (0d 0a on Windows)\n'
                             '41   A        61   a\n'
                             '30   0        ff   255, the maximum'),
                    'note': 'Five values and you can navigate most dumps. '
                            'Long runs of 00 are padding or empty space, and '
                            'they are how you spot where a structure ends.',
                },
            ],
            'misconceptions': [
                'Hex is not a format the file is stored in. The file is '
                'bytes; hex is a way of writing numbers, chosen because two '
                'digits is exactly one byte.',
                'The right-hand column of a dump is not the file\'s text. It '
                'is the same bytes rendered as characters where that is '
                'possible, and dots where it is not.',
                'A byte is not a character. It is a character in ASCII text, '
                'and one of several bytes making a character in UTF-8, and '
                'neither in a JPEG.',
            ],
            'try_it': [
                'Run `printf "Hi" | xxd` and confirm you get 4869, then work '
                'out why from the table above.',
                'Dump a text file you wrote and find the 0a at the end of '
                'each line. That byte is the entire concept of a line.',
            ],
        },
        {
            'id': 'tr-hex',
            'title': 'Reading bytes: xxd, offsets, and where things start',
            'concept': (
                'A hex dump has three columns: the offset, the bytes, and '
                'the printable rendering. All three matter, and the offset is '
                'the one people ignore and then need.\n\n'
                '**The offset is a position, counted from zero.** It is the '
                'answer to "how far into this file am I", and xxd prints it '
                'in hex, which trips people up because `ls` reports sizes in '
                'decimal. A file that `ls` says is 4096 bytes ends at offset '
                '0x1000, and until those two look like the same number to '
                'you, carving is harder than it needs to be. `printf "%d\\n" '
                '0x1000` converts, and doing it a few times is enough.\n\n'
                '**Each line is sixteen bytes by default**, which is why '
                'offsets go up by 0x10 per line and why the printable column '
                'is sixteen characters wide. `-c` changes that: `-c 8` for '
                'something with an eight-byte structure, `-c 4` when you are '
                'reading 32-bit values, and suddenly a structure that looked '
                'like noise lines up in columns.\n\n'
                '**Four flags do the navigating.** `-l` limits how much you '
                'read, which matters when the file is a gigabyte and you '
                'wanted the header. `-s` seeks to an offset, and takes a '
                'negative number to seek from the *end*, which is the fastest '
                'way to look at a trailer. `-g` sets how many bytes are '
                'grouped between spaces. `-p` prints plain hex with no '
                'columns at all, which is the form you feed to another '
                'tool.\n\n'
                '**A common early confusion is byte order.** Look at four '
                'bytes `01 00 00 00` and the number they represent is 1, not '
                '16777216, on any machine you are likely to be using. x86 '
                'stores the least significant byte first, which is called '
                'little-endian and reads backwards to a human. If a length '
                'field looks absurdly large, you are probably reading it in '
                'the wrong direction.\n\n'
                '`od -A d -t x1z` does the same job with decimal offsets, and '
                '`hexdump -C` is the BSD spelling most people learned first. '
                'Any of the three is fine; knowing that `-s` and `-l` exist '
                'is the part that saves time. Everything so far only reads. '
                'Going the other way, dump back into bytes, is the next lesson.'
            ),
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
            'next': 'tr-revert',
        },
        {
            'id': 'tr-revert',
            'title': 'The round trip, and editing a byte on purpose',
            'next': 'tr-embedded',
            'concept': (
                '`xxd -r` is how you turn a hex dump back into bytes. That '
                'is why a dump can be edited with any text tool and written '
                'back as a file. With `-p` on both ends you have a complete '
                'round trip through text, and therefore through every text '
                'tool you already know.\n\n'
                'That gives you a byte editor made of `sed`. Dump to plain '
                'hex, change the characters you want, revert. It is clumsy '
                'compared to a real hex editor and it is always available, '
                'scriptable, and reviewable, which a GUI is not.\n\n'
                '**The round trip is exact.** `xxd -p file | xxd -r -p` '
                'reproduces the file byte for byte, and that is worth '
                'proving to yourself once with `sha256sum` because it is what '
                'makes every edit below trustworthy.\n\n'
                'Two modes, and mixing them is the usual mistake. **Plain '
                'mode** (`-p` both ways) is a raw stream of hex digits with '
                'no offsets: simple, and what you want for scripting. '
                '**Full mode** keeps the offset column, and `xxd -r` uses '
                'those offsets to place bytes, which means you can patch one '
                'line of a dump and revert only that. Feed a full dump to '
                '`-r -p` and you get garbage, because it reads the offsets as '
                'data.\n\n'
                '**Why you would do this deliberately.** Fixing a corrupted '
                'magic number so a tool will open a file. Building a test '
                'fixture with an exact signature to check what something '
                'detects. Flipping one byte to see what a parser does. '
                'Neutering a sample by breaking its header so nothing can '
                'run it by accident, which is a genuine and widespread '
                'handling practice.\n\n'
                'Work on a copy. This edits bytes with no undo and no '
                'confirmation, which is exactly what you wanted and also '
                'exactly how you lose an original.'
            ),
            'examples': [
                {
                    'label': 'The round trip, and proving it is exact',
                    'code': ('xxd -p file.bin | xxd -r -p > copy.bin\n'
                             'sha256sum file.bin copy.bin\n'
                             '\n'
                             'two identical digests, or something\n'
                             'is wrong with your assumptions'),
                    'note': 'Do this once. Every edit you make afterwards '
                            'rests on the round trip being lossless, so it '
                            'is worth ten seconds of proof.',
                },
                {
                    'label': 'Changing one byte with text tools',
                    'code': ('xxd -p broken.png \\\n'
                             "  | sed '1s/^88/89/' \\\n"
                             '  | xxd -r -p > fixed.png\n'
                             '\n'
                             'first two hex digits of the file,\n'
                             '88 becomes 89'),
                    'note': 'sed is operating on hex characters as text. The '
                            '`1s/^88/` anchors it to the very start, which '
                            'matters because 88 appears all over a real file.',
                },
                {
                    'label': 'Patching by offset, in full mode',
                    'code': ('xxd file.bin > dump.txt\n'
                             '(edit the line at the offset you want)\n'
                             'xxd -r dump.txt > patched.bin\n'
                             '\n'
                             'full mode keeps offsets, so -r\n'
                             'puts bytes back where they came from'),
                    'note': 'This is the mode to use when you know the offset '
                            'from a previous `-s` and want to change what is '
                            'there without touching anything else.',
                },
                {
                    'label': 'Building a file with an exact signature',
                    'code': ("printf '%s' '474946383961' | xxd -r -p > "
                             'fake.gif\n'
                             'file fake.gif\n'
                             '  GIF image data, version 89a\n'
                             '\n'
                             'six bytes. no image, no pixels,\n'
                             'no data of any kind.'),
                    'note': 'A useful way to test what a detector actually '
                            'looks at, and a blunt demonstration that `file` '
                            'reads the front of a file and infers the rest.',
                },
                {
                    'label': 'And where that stops working',
                    'code': ("printf '%s' '504b0304' | xxd -r -p > fake.zip\n"
                             'file fake.zip\n'
                             '  data\n'
                             '\n'
                             'the ZIP signature alone is not enough:\n'
                             "file's rule wants more structure than that"),
                    'note': 'Worth knowing before you conclude a detector is '
                            'broken. Some signatures are four bytes and some '
                            'are a pattern spread through the file, and ZIP '
                            'is the second kind.',
                },
            ],
            'misconceptions': [
                '`-r` and `-r -p` are not interchangeable. Plain mode has no '
                'offsets; full mode uses them to place bytes, and feeding one '
                'to the other produces nonsense rather than an error.',
                'Editing the printable column of a dump does nothing. `xxd '
                '-r` reads the hex, and the right-hand column is a rendering '
                'it regenerates.',
                'The round trip is not lossy or approximate. `xxd -p | xxd -r '
                '-p` returns the identical file, which is what makes this '
                'usable at all.',
            ],
            'try_it': [
                'Round-trip a file and compare hashes. Then do it again with '
                '`-p` on one side only, and see what breaks.',
                'Make a four-byte file with a PNG signature and run `file` on '
                'it. Consider what that tells you about signature detection.',
            ],
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
            'id': 'trc-repair-magic',
            'title': 'Repair a file nothing will open',
            'goal': 'A PNG with one wrong byte at the very start. `file` calls it "data" and no viewer will touch it. Put the byte back with the xxd round trip and prove it worked.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {
                    'broken.png': {
                        'b64': 'iFBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCC',
                    },
                },
            },
            'solution': {
                'shell': "xxd -p broken.png | sed '1s/^88/89/' | xxd -r -p > fixed.png && file fixed.png > verdict.txt",
            },
            'steps': [
                {
                    'instruction': 'Look at the first sixteen bytes and compare them with what a PNG should start with.',
                    'hint': 'xxd -l 16 broken.png',
                },
                {
                    'instruction': 'A PNG begins 89 50 4E 47. Find which byte is wrong here.',
                    'hint': 'The very first one. It reads 88.',
                },
                {
                    'instruction': 'Dump to plain hex, correct that byte, and revert it into fixed.png.',
                    'hint': "xxd -p broken.png | sed '1s/^88/89/' | xxd -r -p > fixed.png",
                },
                {
                    'instruction': 'Run file on the result and save what it says to verdict.txt.',
                    'hint': 'file fixed.png > verdict.txt',
                },
            ],
            'free': 'Produce fixed.png, a valid PNG, by correcting the single wrong byte in broken.png. Capture the output of file in verdict.txt.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'is_file': ['fixed.png', 'verdict.txt'],
                    'file_contains': {'verdict.txt': 'PNG image'},
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'trc-roundtrip',
            'title': 'Prove the round trip, then build a signature',
            'goal': 'Two short exercises in the same idea: that xxd goes both ways exactly. Round-trip a file and check the hashes match, then construct a file from nothing but hex.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {
                    'sample.bin': 'the quick brown fox\njumps over the lazy dog\n',
                },
            },
            'solution': {
                'shell': "xxd -p sample.bin | xxd -r -p > copy.bin && sha256sum sample.bin copy.bin > hashes.txt && printf '%s' '474946383961' | xxd -r -p > fake.gif && file fake.gif > kind.txt",
            },
            'steps': [
                {
                    'instruction': 'Dump sample.bin to plain hex and turn it straight back into a file called copy.bin.',
                    'hint': 'xxd -p sample.bin | xxd -r -p > copy.bin',
                },
                {
                    'instruction': 'Hash both files into hashes.txt. The two digests should be identical.',
                    'hint': 'sha256sum sample.bin copy.bin > hashes.txt',
                },
                {
                    'instruction': 'Now build a file out of six bytes of hex: 474946383961, which spells GIF89a. Call it fake.gif.',
                    'hint': "printf '%s' '474946383961' | xxd -r -p > fake.gif",
                },
                {
                    'instruction': 'Ask file what it thinks fake.gif is, into kind.txt. It contains no image at all.',
                    'hint': 'file fake.gif > kind.txt',
                },
            ],
            'free': 'Produce copy.bin (a round trip of sample.bin), hashes.txt showing both digests, and a six-byte fake.gif whose type file reports in kind.txt.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_equals': {'copy.bin': 'the quick brown fox\njumps over the lazy dog\n'},
                    'is_file': ['hashes.txt', 'fake.gif', 'kind.txt'],
                    'file_contains': {'kind.txt': 'GIF image data'},
                },
            },
            'fallback': 'self',
        },
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
        {
            'id': 'trq-xxd-modes',
            'type': 'mcq',
            'prompt': 'You dump with xxd (full form) and revert with xxd -r -p. What happens?',
            'answer': 'Garbage: -r -p treats the offset column as hex data.',
            'distractors': [
                'The original file, because -r detects the form.',
                'An error naming the missing -p on the dump side.',
                'A file containing only the printable column.',
            ],
            'teach': 'Plain mode is a raw stream of digits. Full mode keeps offsets so -r can patch one line. Mixing them is the usual silent failure.',
        },
        {
            'id': 'trq-xxd-seek',
            'type': 'mcq',
            'prompt': 'What does xxd -s -64 archive.dat show?',
            'answer': 'The last 64 bytes, because a negative seek is from the end.',
            'distractors': [
                'Bytes 0 to 63, ignoring the minus as a typo.',
                'An error: -s only accepts a hex offset.',
                '64 bytes starting at offset 64 from the start.',
            ],
            'teach': 'ZIP keeps its central directory at the end, which is why this is the first look at an archive and why appended ZIPs still open.',
        },
    ],
}
