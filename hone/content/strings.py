"""strings: the cheapest look inside a binary.

strings prints the runs of printable characters in a file, which is where URLs, paths, error messages and version strings hide. Two flags carry it: -n to cut the noise, and -e l to find the UTF-16 text that Windows binaries are full of and the default ASCII pass misses entirely. Sandbox-verified.
"""

MODULE = {
    'context': 'You are at a shell prompt with an unknown file in front of you, and you will not run it.',
    'prereqs': [
        'linux',
        'linuxutils',
    ],
    'adapter': 'sandbox',
    'group': 'Security',
    'id': 'strings',
    'title': 'strings',
    'needs': [
        'strings',
    ],
    'estimate': '1-2 hours',
    'order': 73,
    'blurb': 'Readable runs, the minimum length, and the UTF-16 pass Windows needs.',
    'lessons': [
        {
            'id': 'tr-strings',
            'title': 'strings: the cheapest look inside',
            'concept': 'strings walks a file and prints every run of printable characters longer than a threshold. It is crude, it is fast, and it is almost always the second command after `file`, because a surprising amount of what a binary is for is written in plain text inside it: URLs, registry paths, error messages, file names, and the name of the compiler.\n\nTwo flags change everything. -n sets the minimum run length, and the default of 4 produces a lot of noise; raising it to 8 or 10 leaves the strings that are actually words. -e chooses the encoding, and this is the one people miss: Windows binaries are full of UTF-16 text, which the default ASCII pass renders as nothing at all. `strings -e l` finds the little-endian 16-bit strings, and on a Windows sample that is usually where the interesting content is.\n\n-t adds the offset each string was found at, in decimal, hex or octal, which is what turns a finding into a location you can go back to.\n\nThe limits are as important as the tool. Packed, compressed or encrypted content has no readable strings, so an empty result is itself a finding. And a string proves the bytes are present, never that the program uses them.',
            'examples': [
                {
                    'label': 'Cut the noise',
                    'code': 'strings -n 10 sample.bin | less',
                    'note': 'The default minimum of 4 buries the real content in fragments.',
                },
                {
                    'label': 'The flag that finds Windows text',
                    'code': 'strings -e l -n 8 sample.exe',
                    'note': 'UTF-16 little endian. Without it, half a Windows binary looks empty.',
                },
                {
                    'label': 'Where was it found',
                    'code': 'strings -t x -n 8 sample.bin | grep -i http',
                    'note': 'Offsets in hex, so you can go straight back with xxd -s.',
                },
                {
                    'label': 'Every encoding, then filter',
                    'code': 'strings -a -e S sample.bin | sort -u | head -50',
                    'note': '-a scans the whole file rather than only the loaded sections.',
                },
            ],
            'misconceptions': [
                'An empty strings output does not mean an empty file. It usually means packed, compressed or encrypted content.',
                'Finding a URL in a binary does not mean the program contacts it. Presence is not use.',
                'The default encoding is 7-bit ASCII only. Anything UTF-16 is invisible until you pass -e.',
            ],
            'try_it': [
                'Run strings with -n 4 and -n 12 on the same binary and compare how much is left.',
                'Take any file with UTF-16 content and find text that the default pass misses entirely.',
            ],
            'next': None,
        },
    ],
    'drills': [
        {
            'id': 'trd-strings-n',
            'type': 'command',
            'prompt': 'List strings of at least 10 characters in sample.bin.',
            'answer': 'strings -n 10 sample.bin',
            'teach': 'The default minimum of 4 buries real content in fragments. Raising it is the first thing to do.',
        },
        {
            'id': 'trd-strings-utf16',
            'type': 'command',
            'prompt': 'Find the UTF-16 little-endian strings in sample.exe.',
            'answer': 'strings -e l sample.exe',
            'teach': 'Half a Windows binary is invisible to the default ASCII pass. This is the flag people miss.',
        },
        {
            'id': 'trd-strings-offset',
            'type': 'command',
            'prompt': 'List strings in sample.bin with their offsets in hex.',
            'answer': 'strings -t x sample.bin',
            'teach': 'Turns a finding into a location, so you can go straight back with xxd -s.',
        },
        {
            'id': 'trd-strings-all',
            'type': 'command',
            'prompt': 'Scan the whole of sample.bin for strings, not just its loaded sections.',
            'answer': 'strings -a sample.bin',
            'teach': 'Scanning the whole file is the default on modern binutils, and -d restores the old sections-only behaviour.',
        },
    ],
    'challenges': [
        {
            'id': 'trc-strings',
            'title': 'Pull the readable part out of a binary blob',
            'goal': 'Use the two flags that matter, a sensible minimum length and offsets, to find what is written inside a file.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {
                    'blob.bin': '\x00\x01\x02xy\x00\x00http://updates.example.invalid/payload\x00\x03\x04ab\x00C:\\\\Users\\\\Public\\\\run.bat\x00\x05\x06',
                },
            },
            'solution': {
                'shell': 'strings -n 8 -t x blob.bin > found.txt',
            },
            'steps': [
                {
                    'instruction': 'Run strings on blob.bin with the default settings and note the fragments.',
                    'hint': 'strings blob.bin',
                },
                {
                    'instruction': 'Raise the minimum length to 8 and add hex offsets, saving to found.txt.',
                    'hint': 'strings -n 8 -t x blob.bin > found.txt',
                },
                {
                    'instruction': 'Take one offset from found.txt and go back to it with a hex dump.',
                    'hint': 'xxd -s 0x7 -l 48 blob.bin',
                },
            ],
            'free': 'Produce found.txt: strings of at least 8 characters from blob.bin, each with its hex offset.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_contains': {
                        'found.txt': [
                            'updates.example.invalid',
                            'run.bat',
                        ],
                    },
                },
            },
            'fallback': 'self',
        },
    ],
    'quiz': [
        {
            'id': 'trq-strings-empty',
            'type': 'mcq',
            'prompt': 'strings on a 2 MB binary returns almost nothing. What is the most likely reason?',
            'answer': 'The content is packed, compressed or encrypted.',
            'distractors': [
                'The binary is statically linked.',
                'The file is a 64-bit ELF and strings only reads 32-bit.',
                'strings needs root to read program headers.',
            ],
            'teach': 'An empty result is a finding. Also try -e l, because UTF-16 text is invisible to the default pass.',
        },
        {
            'id': 'trq-utf16',
            'type': 'mcq',
            'prompt': 'A Windows binary shows no interesting strings by default. Which flag most often fixes that?',
            'answer': '-e l, for 16-bit little-endian strings.',
            'distractors': [
                '-a, to scan the whole file.',
                '-t x, to show offsets.',
                '-n 4, to lower the minimum length.',
            ],
            'teach': 'Windows text is largely UTF-16, and the default ASCII pass renders it as nothing at all.',
        },
    ],
}
