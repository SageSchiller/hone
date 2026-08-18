"""strings: the cheapest look inside a binary.

strings prints the runs of printable characters in a file, which is where URLs,
paths, error messages and version strings hide. Two flags carry it: -n to cut
the noise, and -e l to find the UTF-16 text that Windows binaries are full of
and the default ASCII pass misses entirely. Sandbox-verified.

**Expanded from one lesson to three.** It arrived from the D31 triage split as
a single lesson that opened on "strings walks a file and prints every run of
printable characters longer than a threshold", which assumes the reader already
knows what a binary is and why text would be sitting loose inside one. The ramp
now starts at why a compiled program contains readable words at all, which is
the thing that makes the tool make sense, and ends on triage workflow: what an
empty result means, and how to go from a hit to a location and then to the
bytes around it.
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
            'id': 'tr-why',
            'title': 'Why a program has words inside it',
            'next': 'tr-strings',
            'concept': (
                '`strings` is how you dump the readable text sitting in a '
                'binary, without running it. That is why error messages, URLs '
                'and paths are the first useful facts you get from a file '
                'you do not trust.\n\n'
                'The answer is that **a program has to carry its data with '
                'it**. Every error message it might print, every URL it might '
                'contact, every registry key it reads, every file path it '
                'opens, every window title, every format string: all of that '
                'is text, and text does not compile down into anything. It '
                'sits in a data section of the file, in plain view, exactly '
                'as the programmer typed it.\n\n'
                'So a binary is machine code with a filing cabinet attached, '
                'and `strings` is the tool that dumps the filing cabinet '
                'without opening the code at all. It never executes anything, '
                'which is the other reason it is the first thing you reach '
                'for on something you do not trust.\n\n'
                '**What counts as a string** is deliberately simple: a run of '
                'printable characters, at least some minimum length, ending '
                'at anything that is not. There is no parsing, no format '
                'awareness and no cleverness. That crudeness is why it works '
                'on absolutely any file, including ones nothing else can '
                'read.\n\n'
                'It is almost always the second command after `file`, and the '
                'pair answers most of "what is this" before you have '
                'committed to anything. Two flags decide what you actually '
                'see, and they are the next lesson.'
            ),
            'examples': [
                {
                    'label': 'What the compiler kept',
                    'code': ('printf("connecting to %s\\n", host);\n'
                             '\n'
                             'the code becomes machine instructions.\n'
                             '"connecting to %s\\n" stays exactly as it is,\n'
                             'in the data section, readable forever.'),
                    'note': 'This is why error messages are such good '
                            'material: you can search a binary for the text '
                            'it printed at you and find the code path.',
                },
                {
                    'label': 'The two-command opening move',
                    'code': ('file sample.bin        what kind of thing?\n'
                             'strings -n 10 sample.bin | less\n'
                             '                       what is written in it?'),
                    'note': 'Neither one runs the file. That is the whole '
                            'point of doing them first.',
                },
                {
                    'label': 'What it will find, roughly in order of use',
                    'code': ('URLs and domain names\n'
                             'file paths and registry keys\n'
                             'error and status messages\n'
                             'the compiler and its version\n'
                             'library and function names'),
                    'note': 'The compiler string is the one people overlook. '
                            'It tells you what built the thing, which '
                            'narrows what it is faster than anything else '
                            'here.',
                },
            ],
            'misconceptions': [
                'strings does not decompile anything. It finds text that was '
                'always text, and it never turns machine code back into '
                'source.',
                'strings does not run the file. It reads bytes, which is why '
                'it is safe to point at something you are suspicious of.',
                'A binary containing readable text is not badly built. Every '
                'compiled program on your machine is full of it.',
            ],
            'try_it': [
                'Run `strings -n 10 /bin/ls | head -40` and look for the '
                'error messages you have seen ls print at you.',
                'Find the compiler version string in any binary on your '
                'system. It is usually near the end.',
            ],
        },
        {
            'id': 'tr-strings',
            'title': 'strings: the cheapest look inside',
            'next': 'tr-triage',
            'concept': 'Those two flags are -n and -e, and they are why a default run so often looks empty. strings walks a file and prints every run of printable characters longer than a threshold. It is crude, it is fast, and it is almost always the second command after `file`, because a surprising amount of what a binary is for is written in plain text inside it: URLs, registry paths, error messages, file names, and the name of the compiler.\n\nTwo flags change everything. -n sets the minimum run length, and the default of 4 produces a lot of noise; raising it to 8 or 10 leaves the strings that are actually words. -e chooses the encoding, and this is the one people miss: Windows binaries are full of UTF-16 text, which the default ASCII pass renders as nothing at all. `strings -e l` finds the little-endian 16-bit strings, and on a Windows sample that is usually where the interesting content is.\n\n-t adds the offset each string was found at, in decimal, hex or octal, which is what turns a finding into a location you can go back to.\n\nThe limits are as important as the tool. Packed, compressed or encrypted content has no readable strings, so an empty result is itself a finding. And a string proves the bytes are present, never that the program uses them.',
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
                    'label': 'The 8-bit pass, then filter',
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
        },
        {
            'id': 'tr-triage',
            'title': 'From a hit to a location to the bytes',
            'concept': (
                'Running strings is easy. Getting an answer out of forty '
                'thousand lines of it is the actual skill, and it is three '
                'habits rather than any further flags.\n\n'
                '**Filter towards a question, not away from noise.** Piping '
                'to `grep -i http` asks "does this contact anything". '
                '`grep -iE "\\.(exe|dll|bat|ps1)"` asks "what does it drop". '
                '`sort -u` collapses the same string appearing two hundred '
                'times. Reading the whole dump top to bottom is the one '
                'approach that reliably finds nothing.\n\n'
                '**An empty result is a finding, not a failure.** A two '
                'megabyte binary with no readable strings is packed, '
                'compressed or encrypted, and that is worth knowing '
                'immediately: it tells you the next step is unpacking rather '
                'than more reading. Before concluding that, run the UTF-16 '
                'pass, because half a Windows binary is invisible without '
                'it.\n\n'
                '**Presence is not use.** A URL in a binary means those bytes '
                'are in the file. It does not mean the program ever contacts '
                'it, and it may be a leftover, a decoy, or a string in a '
                'library nobody calls. strings tells you what is there and '
                'never what runs.\n\n'
                'The bridge to everything else is `-t`, which prints the '
                'offset. A string plus an offset is a place you can return to '
                'with `xxd -s`, and the bytes around a string are frequently '
                'more interesting than the string.'
            ),
            'examples': [
                {
                    'label': 'Asking a question rather than scrolling',
                    'code': ('strings -n 8 s.bin | grep -i http\n'
                             'strings -n 8 s.bin | grep -iE "\\\\.(exe|dll)"\n'
                             'strings -n 8 s.bin | sort -u | wc -l'),
                    'note': 'The last one is a habit worth having: it tells '
                            'you in one line whether this file is going to '
                            'be talkative or silent.',
                },
                {
                    'label': 'The full triage sweep',
                    'code': ('file s.bin\n'
                             'strings -n 10 s.bin      | sort -u > ascii.txt\n'
                             'strings -e l -n 10 s.bin | sort -u > utf16.txt\n'
                             'wc -l ascii.txt utf16.txt'),
                    'note': 'Both passes, every time, on anything from '
                            'Windows. The line counts alone tell you which '
                            'file to read first.',
                },
                {
                    'label': 'Going back to the bytes',
                    'code': ('strings -t x -n 8 s.bin | grep -i http\n'
                             '   7f2a http://updates.example.invalid/x\n'
                             '\n'
                             'xxd -s 0x7f2a -l 96 s.bin'),
                    'note': 'The offset is the handoff to the xxd module. '
                            'What sits immediately before and after a string '
                            'is often the rest of the answer.',
                },
            ],
            'misconceptions': [
                'An empty strings output is not a broken command. It is '
                'evidence, and the usual conclusion is that the content is '
                'packed.',
                'Finding a suspicious domain is not proof of behaviour. You '
                'have found bytes, which is a lead rather than a conclusion.',
                'Running both encodings is not belt and braces. On a Windows '
                'sample the two passes routinely return completely different '
                'content.',
            ],
            'try_it': [
                'Run the full sweep above on any Windows executable you have '
                'and compare the line counts of the two files.',
                'Take one hit with an offset and dump the surrounding bytes '
                'with `xxd -s`. Look at what is stored next to it.',
            ],
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
            'id': 'trc-two-passes',
            'title': 'The half of the file the default pass cannot see',
            'goal': 'Run both encodings against one sample and produce two files. They will have nothing in common, which is the entire argument for always doing both.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {
                    'sample.bin': {
                        'b64': 'AAFNWpAAVGhpcyBwcm9ncmFtIGNhbm5vdCBiZSBydW4gaW4gRE9TIG1vZGUAAABDADoAXABVAHMAZQByAHMAXABQAHUAYgBsAGkAYwBcAHMAdABhAGcAZQAuAHAAcwAxAAAAAABodHRwOi8vY2RuLmV4YW1wbGUuaW52YWxpZC9iZWFjb24AAABIAEsAQwBVAFwAUwBvAGYAdAB3AGEAcgBlAFwATQBpAGMAcgBvAHMAbwBmAHQAXABXAGkAbgBkAG8AdwBzAFwAQwB1AHIAcgBlAG4AdABWAGUAcgBzAGkAbwBuAFwAUgB1AG4AAAAAAP////////////////////////////////////////////////////8=',
                    },
                },
            },
            'solution': {
                'shell': 'strings -n 8 sample.bin > ascii.txt && strings -e l -n 8 sample.bin > utf16.txt',
            },
            'steps': [
                {
                    'instruction': 'Run the default pass with a minimum length of 8 and save it to ascii.txt.',
                    'hint': 'strings -n 8 sample.bin > ascii.txt',
                },
                {
                    'instruction': 'Now run the UTF-16 little-endian pass and save that to utf16.txt.',
                    'hint': 'strings -e l -n 8 sample.bin > utf16.txt',
                },
                {
                    'instruction': 'Compare the two files. Nothing in one appears in the other, and the second holds the registry key and the dropped path.',
                    'hint': 'cat ascii.txt utf16.txt',
                },
            ],
            'free': 'Produce ascii.txt and utf16.txt: the same sample read at minimum length 8, once with the default encoding and once with UTF-16 little-endian.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_contains': {
                        'ascii.txt': ['cdn.example.invalid', 'DOS mode'],
                        'utf16.txt': ['CurrentVersion', 'stage.ps1'],
                    },
                    'file_lacks': {
                        'ascii.txt': 'CurrentVersion',
                    },
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'trc-strings-triage',
            'title': 'Ask a question instead of scrolling',
            'goal': 'Take the same sample and answer one specific question: what does it try to contact, and where does it write. Filtering towards a question is the skill; reading the whole dump is not.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {
                    'sample.bin': {
                        'b64': 'AAFNWpAAVGhpcyBwcm9ncmFtIGNhbm5vdCBiZSBydW4gaW4gRE9TIG1vZGUAAABDADoAXABVAHMAZQByAHMAXABQAHUAYgBsAGkAYwBcAHMAdABhAGcAZQAuAHAAcwAxAAAAAABodHRwOi8vY2RuLmV4YW1wbGUuaW52YWxpZC9iZWFjb24AAABIAEsAQwBVAFwAUwBvAGYAdAB3AGEAcgBlAFwATQBpAGMAcgBvAHMAbwBmAHQAXABXAGkAbgBkAG8AdwBzAFwAQwB1AHIAcgBlAG4AdABWAGUAcgBzAGkAbwBuAFwAUgB1AG4AAAAAAP////////////////////////////////////////////////////8=',
                    },
                },
            },
            'solution': {
                'shell': 'strings -n 8 sample.bin | grep -i http > urls.txt && strings -e l -n 8 sample.bin | grep -iE "\\.(ps1|exe|bat|dll)" > drops.txt && strings -t x -e l -n 8 sample.bin | grep -i currentversion > persist.txt',
            },
            'steps': [
                {
                    'instruction': 'From the default pass, pull just the lines mentioning http into urls.txt.',
                    'hint': 'strings -n 8 sample.bin | grep -i http > urls.txt',
                },
                {
                    'instruction': 'From the UTF-16 pass, pull the lines naming a script or executable into drops.txt.',
                    'hint': 'strings -e l -n 8 sample.bin | grep -iE "\\.(ps1|exe|bat|dll)"',
                },
                {
                    'instruction': 'Find the Run key with its offset this time, into persist.txt. The offset is what lets you go back with xxd -s.',
                    'hint': 'strings -t x -e l -n 8 sample.bin | grep -i currentversion',
                },
            ],
            'free': 'Produce urls.txt (anything it contacts), drops.txt (anything it writes), and persist.txt (the Run key, with its offset).',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_contains': {
                        'urls.txt': 'cdn.example.invalid',
                        'drops.txt': 'stage.ps1',
                        'persist.txt': 'CurrentVersion',
                    },
                },
            },
            'fallback': 'self',
        },
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
        {
            'id': 'trq-strings-n',
            'type': 'mcq',
            'prompt': 'Why raise strings -n from the default of 4 to 8 or 10?',
            'answer': 'The default buries real words in four-character fragments.',
            'distractors': [
                'Shorter runs are encrypted and not worth printing.',
                'Windows binaries crash the default pass below 8.',
                'Offsets are only recorded for strings of length 8 or more.',
            ],
            'teach': 'A run of four printable bytes happens constantly in machine code. Raising the floor is a filter, not a precision setting.',
        },
        {
            'id': 'trq-presence',
            'type': 'mcq',
            'prompt': 'strings finds a URL in a binary. What does that prove?',
            'answer': 'Those bytes are in the file. It does not prove the program contacts it.',
            'distractors': [
                'The program contacts that URL every time it runs.',
                'The URL is in the code path that will execute next.',
                'The binary was packed, and the URL is the unpacker.',
            ],
            'teach': 'Leftovers, decoys and unused library strings all print the same way. A hit is a lead to take back with xxd -s, not a conclusion.',
        },
    ],
}
