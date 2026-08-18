"""file: what a thing actually is, not what it is called.

A file's type is its contents, not its extension: file reads the magic bytes and tells you what something really is, which is why it disagrees with the name so usefully. This module also covers opening an unknown archive safely, listing before extracting, because identifying a file and handling it without harm are the same skill. Sandbox-verified. Never run the sample.
"""

MODULE = {
    'context': 'You are at a shell prompt with an unknown file in front of you, and you will not run it.',
    'prereqs': [
        'linux',
        'linuxutils',
    ],
    'adapter': 'sandbox',
    'group': 'Security',
    'id': 'file',
    'title': 'file',
    'needs': [
        'file',
    ],
    'estimate': '2 hours',
    'order': 72,
    'blurb': 'Magic bytes versus the extension, MIME types, and opening archives safely.',
    'lessons': [
        {
            'id': 'tr-what',
            'title': 'The first question about any unknown file',
            'next': 'tr-magic',
            'concept': (
                '`file` is how you identify a file from its contents, without '
                'running it and without trusting its name. That is why it is '
                'the first command on something that just arrived.\n\n'
                '`file thing` prints a one-line description of what something '
                'actually is. It does this **without running it and without '
                'trusting its name**, which are the two properties that make '
                'it safe to point at anything.\n\n'
                'How it works is worth knowing because it explains both its '
                'power and its limits. `file` opens the thing, reads the '
                'first few hundred bytes, and compares them against a large '
                'database of known signatures shipped with the system. If a '
                'signature matches, it says so, often with detail: image '
                'dimensions, the architecture of a binary, the compression '
                'method of an archive.\n\n'
                'If nothing matches, it falls back to guessing from '
                'structure, and you get vaguer answers like "ASCII text" or '
                '"data". **"data" means "I have no idea"**, and on a file that '
                'is supposed to be something specific, that is itself a '
                'finding: encrypted, compressed and packed content all look '
                'like noise, because that is what they are.\n\n'
                'The habit worth forming is `file` then `strings` then `xxd`, '
                'in that order, getting slower and more detailed as the '
                'question narrows. This module is the first of the three. '
                'How file knows, and why the name can lie, is the next lesson.'
            ),
            'examples': [
                {
                    'label': 'The command, and what it tells you',
                    'code': ('file report.pdf\n'
                             '  PDF document, version 1.7\n'
                             '\n'
                             'file photo.jpg\n'
                             '  JPEG image data, 4032x3024\n'
                             '\n'
                             'file mystery.bin\n'
                             '  data'),
                    'note': '"data" is not an error. It means nothing in the '
                            'signature database matched, which on something '
                            'claiming to be a document is the interesting '
                            'answer.',
                },
                {
                    'label': 'Why it is safe to run first',
                    'code': ('file suspicious.exe      reads bytes\n'
                             './suspicious.exe         runs the program\n'
                             '\n'
                             'one of these is a diagnostic\n'
                             'and one is a decision'),
                    'note': 'file never executes anything and never follows '
                            'anything anywhere. It is the same class of safe '
                            'as `ls`.',
                },
                {
                    'label': 'The triage order',
                    'code': ('file thing        what kind of thing is it?\n'
                             'strings thing     what is written in it?\n'
                             'xxd thing | head  what do the bytes look like?\n'
                             '\n'
                             'each one narrows the next'),
                    'note': 'Skipping to the hex dump first is a common '
                            'beginner move and it wastes an hour. Let `file` '
                            'tell you what you are looking at.',
                },
            ],
            'misconceptions': [
                'file does not read the extension. Rename a PNG to .txt and '
                'file still says PNG, which is the entire reason to use it.',
                '"data" is not a failure. It means unrecognised, and '
                'encrypted, compressed and packed content all land there.',
                'file does not run anything. It reads the beginning of the '
                'file and consults a table, which is why it is safe on '
                'something you do not trust.',
            ],
            'try_it': [
                'Run `file` on five random things in /usr/bin and /etc and '
                'see how much detail it gives for each.',
                'Copy a PNG to a file called notes.txt and run `file` on it. '
                'Then decide how much you trust any extension.',
            ],
        },
        {
            'id': 'tr-magic',
            'title': 'The extension is a label, the magic is the file',
            'concept': 'The name can lie because nothing in a Unix filesystem enforces that invoice.pdf is a PDF. The extension is part of the name, and the name is metadata that anyone can write. What actually decides is the content, and specifically the first few bytes, because most formats begin with a fixed signature.\n\nPDF files start with %PDF. ZIP archives, and therefore also every .docx, .xlsx, .jar and .apk, start with PK followed by 03 04. ELF binaries start with 0x7F then ELF. PNG starts with 89 50 4E 47. Windows executables start with MZ, the initials of Mark Zbikowski, a Microsoft engineer, which is the kind of fact that makes signatures memorable.\n\n`file` is the tool that reads these, and it is doing something more careful than a table lookup: it works through a compiled database of magic patterns, at various offsets, with fallbacks, and it will tell you a great deal more than the type. For an ELF it names the architecture, whether it is dynamically linked, and whether it was stripped, all of which are triage facts.\n\nThe start is also the limit. `file` only reads the beginning, so a JPEG header glued onto a ZIP still reports as JPEG, and a polyglot PDF that is also a ZIP will usually be called a PDF. When the answer and the size or the later bytes disagree, `xxd` past the header is the next look, not a second run of `file`.\n\nWhen `file` says "data", that is a real answer: no signature matched. Encrypted blobs, compressed streams and carved fragments all look like that.\n\n`file -z` looks inside compressed members. A file named `notes.txt.gz` reports as gzip without `-z`, and as gzip wrapping ASCII text with it. The wrapper is still true; `-z` adds what the payload is. That is the look to take before deciding whether to decompress, because the name of the archive is no more trustworthy than the name of the file.',
            'examples': [
                {
                    'label': 'When the metadata is the answer',
                    'code': 'file photo.jpg        JPEG image data, 4032x3024\nexiftool photo.jpg    camera, lens, timestamps, GPS',
                    'note': 'file reads the first few bytes and stops. exiftool reads the metadata blocks properly, which on a photograph is often the interesting part.',
                },
                {
                    'label': 'What is it, really',
                    'code': 'file suspicious.jpg',
                    'note': 'If the answer is not JPEG, the name was a claim rather than a fact.',
                },
                {
                    'label': 'Look at the signature yourself',
                    'code': 'xxd -l 16 suspicious.jpg',
                    'note': 'The first sixteen bytes settle it. PK.. means ZIP, whatever the name says.',
                },
                {
                    'label': 'Type only, for scripting',
                    'code': 'file -b --mime-type *',
                    'note': '-b drops the filename, --mime-type gives a stable string a script can compare.',
                },
                {
                    'label': 'Follow a symlink to its target',
                    'code': 'file -L link-to-thing',
                    'note': 'Without -L you learn where it points, not what the target is.',
                },
                {
                    'label': 'Look through the compression',
                    'code': 'file notes.txt.gz         gzip compressed data\nfile -z notes.txt.gz      gzip compressed data: ASCII text',
                    'note': '-z does not extract anything. It identifies the payload so you know whether decompressing is worth it.',
                },
            ],
            'misconceptions': [
                'file does not read the extension at all. It reads content, which is why it disagrees with the name so usefully.',
                'A .docx is a ZIP archive. So is a .jar, an .apk and an .odt. That is not a trick, it is the format.',
                '"data" is not a failure. It means nothing matched, which is itself informative about encryption or compression.',
            ],
            'try_it': [
                'Copy a PNG to a file named notes.txt and run file on it.',
                'Run xxd -l 16 on five different file types and learn to recognise three signatures by eye.',
            ],
            'next': 'tr-archives',
        },
        {
            'id': 'tr-archives',
            'title': 'Opening things safely, and in what order',
            'concept': 'The discipline that separates triage from an incident of your own making is simple: look before you extract, and never execute.\n\nEvery archive tool can list without extracting. `tar -tvf` and `unzip -l` show the paths, sizes and modes of what is inside. That listing is where you find the two problems worth catching in advance: absolute paths beginning with a slash, and traversal paths containing dot dot, either of which writes outside the directory you thought you were in. Modern GNU tar strips leading slashes and refuses obvious traversal, and plenty of other extractors do not.\n\nWhen that goes wrong it is quiet. `tar -xf` prints nothing, exits 0, and a path like `../../.ssh/authorized_keys` is now on disk where you did not look. The listing would have shown it; the extract does not ask. GNU tar may strip a leading slash and still write `etc/cron.d/x` into the current directory, which is better and still not what you thought you were unpacking.\n\nA tar bomb is the other case: an archive with no common top level directory that scatters two thousand files into your current one. The listing shows that too, and the fix is to extract into a directory you made for it.\n\nThe order that works is always the same. Identify with `file`, hash it and write the hash down, look with `strings` and `xxd`, list the contents, extract into a fresh directory if you must, and read the extracted files without running anything. Every step is reversible except the last one, and the last one is the one to be slow about.',
            'examples': [
                {
                    'label': 'Look before extracting, tar',
                    'code': 'tar -tvf bundle.tar.gz',
                    'note': 'Paths, modes, sizes. Read the paths for a leading slash or a dot dot.',
                },
                {
                    'label': 'Look before extracting, zip',
                    'code': 'unzip -l bundle.zip',
                    'note': 'Same job. unzip also has -t to test integrity without writing anything.',
                },
                {
                    'label': 'Extract somewhere you chose',
                    'code': 'mkdir -p out && tar -xf bundle.tar.gz -C out',
                    'note': '-C keeps a tar bomb contained. Habit, not caution.',
                },
                {
                    'label': 'Read one file out of an archive without unpacking',
                    'code': 'tar -xOf bundle.tar.gz manifest.json | head',
                    'note': '-O writes to stdout. Nothing lands on disk at all.',
                },
            ],
            'misconceptions': [
                'Extracting an archive does not run anything, but it can overwrite files outside the directory if the paths are absolute or traversing.',
                'A .tar.gz listing is cheap: tar reads only the headers, so -tvf on a huge archive is fast.',
                'unzip -t tests integrity, not safety. A perfectly intact archive can still contain traversal paths.',
            ],
            'try_it': [
                'List a tarball you did not make, and check every path for a leading slash or dot dot.',
                'Extract something with -C into a fresh directory, and confirm nothing landed outside it.',
            ],
            'next': None,
        },
    ],
    'drills': [
        {
            'id': 'trd-file',
            'type': 'command',
            'prompt': 'Identify what suspicious.jpg really is.',
            'answer': 'file suspicious.jpg',
            'teach': 'Reads content, never the extension, which is exactly why its disagreement with the name is useful.',
        },
        {
            'id': 'trd-file-mime',
            'type': 'command',
            'prompt': 'Print only the MIME type of sample.bin, with no filename.',
            'answer': 'file -b --mime-type sample.bin',
            'teach': '-b drops the name, --mime-type gives a stable string a script can compare.',
        },
        {
            'id': 'trd-file-link',
            'type': 'command',
            'prompt': 'Identify what a symlink points at rather than the link itself.',
            'answer': 'file -L link',
            'teach': 'Without -L you learn only that it is a symlink, which you could see from ls.',
        },
        {
            'id': 'trd-exiftool',
            'type': 'command',
            'prompt': 'Read the embedded metadata of photo.jpg.',
            'answer': 'exiftool photo.jpg',
            'teach': 'Camera, software, and often GPS and the original timestamps, all of which survive a rename.',
        },
        {
            'id': 'trd-tar-list',
            'type': 'command',
            'prompt': 'List what is inside bundle.tar.gz without extracting it.',
            'answer': 'tar -tvf bundle.tar.gz',
            'teach': 'Read the paths for a leading slash or a dot dot before you let anything write to disk.',
        },
        {
            'id': 'trd-tar-safe',
            'type': 'command',
            'prompt': 'Extract bundle.tar.gz into the directory out.',
            'answer': 'tar -xf bundle.tar.gz -C out',
            'teach': '-C contains a tar bomb. It should be habit rather than a precaution you remember when worried.',
        },
        {
            'id': 'trd-tar-stdout',
            'type': 'command',
            'prompt': 'Read manifest.json out of bundle.tar.gz without writing to disk.',
            'answer': 'tar -xOf bundle.tar.gz manifest.json',
            'teach': '-O sends the member to stdout, so nothing lands on disk at all.',
        },
        {
            'id': 'trd-zip-list',
            'type': 'command',
            'prompt': 'List the contents of bundle.zip without extracting.',
            'answer': 'unzip -l bundle.zip',
            'teach': 'unzip -t is the integrity test. Neither of them tells you the paths are safe: you read those yourself.',
        },
    ],
    'challenges': [
        {
            'id': 'trc-identify',
            'title': 'Trust the bytes, not the name',
            'goal': 'Three files with confident extensions. Work out what each actually is and write the answers down.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {
                    # Real bytes, not an imitation: `file` reads structure, not
                    # just the first four characters, so a fake header would be
                    # reported as data and teach the opposite of the lesson.
                    'holiday.jpg': {'b64': 'UEsDBBQAAAAAACmfDV11V9s5DAAAAAwAAAAKAAAAc2VjcmV0LnR4dHRoZSBwYXlsb2FkClBLAQIUAxQAAAAAACmfDV11V9s5DAAAAAwAAAAKAAAAAAAAAAAAAACAAQAAAABzZWNyZXQudHh0UEsFBgAAAAABAAEAOAAAADQAAAAAAA=='},
                    'notes.txt': {'b64': 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCC'},
                    'readme.pdf': '#!/bin/sh\necho this is a shell script\n',
                },
            },
            'solution': {
                'shell': 'file holiday.jpg notes.txt readme.pdf > types.txt',
            },
            'steps': [
                {
                    'instruction': 'Run file on all three at once and read what it says rather than what they are called.',
                    'hint': 'file holiday.jpg notes.txt readme.pdf',
                },
                {
                    'instruction': 'Save that output to types.txt.',
                    'hint': 'file holiday.jpg notes.txt readme.pdf > types.txt',
                },
                {
                    'instruction': 'Confirm one of them by eye with a hex dump of its first bytes.',
                    'hint': 'xxd -l 8 notes.txt',
                },
            ],
            'free': 'Produce types.txt containing what file reports for all three of these misleadingly named files.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_contains': {
                        # The types, not just the names: checking only the
                        # filenames passed even when the fixtures were mangled
                        # and file reported all three as text.
                        'types.txt': [
                            'holiday.jpg',
                            'Zip archive',
                            'notes.txt',
                            'PNG image data',
                            'readme.pdf',
                            'shell script',
                        ],
                    },
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'trc-archive-safe',
            'title': 'Read an archive before you let it write anything',
            'goal': 'List first, spot the path that would escape, and extract into a directory of your own.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {
                    'payload/notes.txt': 'ordinary content\n',
                    'payload/data.csv': 'a,b,c\n1,2,3\n',
                },
            },
            'solution': {
                'shell': 'tar -cf bundle.tar payload && tar -tvf bundle.tar > listing.txt && mkdir -p out && tar -xf bundle.tar -C out',
            },
            'steps': [
                {
                    'instruction': 'Make an archive of payload/ to work with.',
                    'hint': 'tar -cf bundle.tar payload',
                },
                {
                    'instruction': 'List it without extracting, saving the listing to listing.txt.',
                    'hint': 'tar -tvf bundle.tar > listing.txt',
                },
                {
                    'instruction': 'Read the paths. Then extract into a fresh directory called out.',
                    'hint': 'mkdir -p out && tar -xf bundle.tar -C out',
                },
            ],
            'free': 'Produce listing.txt from tar -tvf, and extract the archive into out/ rather than into the current directory.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_contains': {
                        'listing.txt': [
                            'payload/notes.txt',
                            'payload/data.csv',
                        ],
                    },
                    'is_file': [
                        'out/payload/notes.txt',
                    ],
                    'missing': [
                        'notes.txt',
                    ],
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'trc-own-downloads',
            'title': 'Triage something you actually downloaded',
            'goal': 'Run the whole routine on a real file on your own machine, in the order that keeps you out of trouble.',
            'setup': {
                'kind': 'self',
            },
            'steps': [
                {
                    'instruction': 'Pick a file you downloaded and did not write. Identify it and hash it first.',
                    'hint': 'file thing; sha256sum thing',
                },
                {
                    'instruction': 'Look inside without running it: strings with a sensible minimum, and the first bytes.',
                    'hint': 'strings -n 10 thing | less; xxd -l 32 thing',
                },
                {
                    'instruction': 'Check whether the size matches what the format should be, and look for signatures past the start.',
                },
                {
                    'instruction': 'If it is an archive, list it before you extract, and extract into a fresh directory.',
                },
            ],
            'free': 'On your own machine: identify, hash, inspect and safely open a file you downloaded, without running it.',
            'verify': {
                'kind': 'self',
            },
            'fallback': 'self',
        },
    ],
    'quiz': [
        {
            'id': 'trq-docx',
            'type': 'mcq',
            'prompt': 'xxd shows a .docx beginning with 50 4B 03 04. What is it?',
            'answer': 'A ZIP archive, which is what the docx format is.',
            'distractors': [
                'A corrupted Word file with a damaged header.',
                'A renamed executable pretending to be a document.',
                'An encrypted document using the Office container.',
            ],
            'teach': 'PK are the initials of Phil Katz. docx, xlsx, jar, apk and odt are all ZIP containers.',
        },
        {
            'id': 'trq-file-data',
            'type': 'mcq',
            'prompt': 'file reports simply "data". What does that tell you?',
            'answer': 'No known signature matched, which suggests encryption, compression or a fragment.',
            'distractors': [
                'The file is empty.',
                'file lacks the magic database for this type.',
                'The file is plain text with unusual line endings.',
            ],
            'teach': 'It is a real answer rather than a failure, and it narrows things down more than it looks.',
        },
        {
            'id': 'trq-tar-safe',
            'type': 'mcq',
            'prompt': 'What is the point of running tar -tvf before tar -xf?',
            'answer': 'To read the paths for absolute or traversing entries before anything is written.',
            'distractors': [
                'To decompress the archive once so extraction is faster.',
                'To verify the checksum of every member.',
                'To make tar refuse unsafe paths on the next run.',
            ],
            'teach': 'Listing is cheap because tar reads only headers. Combine it with -C into a fresh directory and both problems go away.',
        },
        {
            'id': 'trq-file-ext',
            'type': 'mcq',
            'prompt': 'A PNG renamed to notes.txt: what does file report?',
            'answer': 'PNG image data. file reads content, never the extension.',
            'distractors': [
                'ASCII text, because the name ends in .txt.',
                'data, because the name and the bytes disagree.',
                'PNG image data, but only if you pass --mime-type.',
            ],
            'teach': 'The extension is part of the name, and nothing in a Unix filesystem enforces it. That disagreement is the whole reason to run the command.',
        },
    ],
}
