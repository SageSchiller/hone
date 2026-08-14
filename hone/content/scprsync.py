"""scp and rsync: moving files over ssh, and the trailing slash.

Two tools that ride on the ssh connection you already set up, so they inherit your keys, your config and your aliases. scp is the simple one-file copy; rsync is the one you actually want for a tree, because it copies only differences, resumes, preserves metadata and can make a destination match a source exactly. The single most useful and most dangerous idea in the pair is the trailing slash on the source, which decides whether you copy a directory or its contents, so this module is built around getting that into muscle memory.

All verified offline: every rsync challenge runs between two directories the trainer owns, with no packet leaving the machine.
"""

MODULE = {
    'id': 'scprsync',
    'title': 'scp and rsync',
    'group': 'Network',
    'blurb': 'One-file copies with scp, syncing trees with rsync, and the trailing slash that changes everything.',
    'context': 'You are at a shell moving files between your machine and another over ssh.',
    'needs': [
        'rsync',
    ],
    'prereqs': [
        'ssh',
    ],
    'adapter': 'sandbox',
    'estimate': '2-3 hours',
    'order': 51,
    'lessons': [
        {
            'id': 'scp-basics',
            'title': 'scp: copying over the same connection as ssh',
            'concept': 'scp copies files over ssh, using the same keys, the same config and the same aliases, so once ssh works, scp works. The shape is `scp SOURCE DEST`, where a remote side is written `host:path` with a colon. Leave the colon off and you have quietly made a local copy instead.\n\nA bare colon means the remote home directory, so `scp report.txt web:` drops the file in your home on web. Copying the other way just swaps the arguments: `scp web:/etc/hostname .` brings it here. `-r` copies a directory, and `-P` sets the port, capital P because lowercase -p preserves timestamps, which is the opposite of what you reach for.\n\nscp is fine for one file or a small handful. The moment you are copying a tree, or copying it more than once, the next lesson is the tool you actually want.',
            'examples': [
                {
                    'label': 'Both directions',
                    'code': 'scp report.txt web:                 into your home on web\nscp report.txt web:/tmp/            to a named path\nscp web:/etc/hostname .             fetch it here\nscp -r site/ web:/var/www/          a whole directory',
                    'note': 'The alias `web` comes straight from ~/.ssh/config, so scp inherits every setting you put there.',
                },
                {
                    'label': 'The two flags that bite',
                    'code': 'scp -P 2222 file web:      capital P is the PORT\nscp -p file web:           lowercase p preserves times\nscp -C file web:           compress in transit',
                    'note': 'ssh uses -p for the port and scp uses -P. Mixing them up is the classic five-minute confusion.',
                },
            ],
            'misconceptions': [
                'Forgetting the colon does not error. `scp a web` makes a local copy named web, and the file never leaves your machine.',
                'scp does not sync. It copies the bytes every time, with no idea what is already at the far end, which is exactly what rsync fixes.',
                'The uppercase and lowercase p are different flags. -P is the port, -p preserves modification times.',
            ],
            'try_it': [
                'Copy a file to yourself with `scp file.txt localhost:/tmp/` and back again, and watch it use the same auth as ssh.',
            ],
            'next': 'rm-transfer',
        },
        {
            'id': 'rm-transfer',
            'title': 'Moving data, and the trailing slash',
            'next': None,
            'concept': '`scp` copies a file and is fine for one file. `rsync` copies only differences, resumes, preserves permissions, and can delete things on the destination that no longer exist on the source. For anything more than one file, rsync.\n\nThe trailing slash on the SOURCE is the thing that catches everyone, and it is worth learning deliberately rather than by accident. `rsync -a src dest/` copies the directory **into** dest, giving `dest/src/`. `rsync -a src/ dest/` copies the **contents** of src into dest. One character, completely different result.\n\n`--delete` makes the destination match the source exactly, including removing files. Combined with a wrong trailing slash it will happily delete a great deal. `--dry-run` first, every time: it is a habit rather than a flag.',
            'examples': [
                {
                    'label': 'The trailing slash',
                    'code': 'src/  contains  a.txt  b.txt\n\nrsync -a src  dest/   ->  dest/src/a.txt\nrsync -a src/ dest/   ->  dest/a.txt\n\nthe slash means "the contents of"',
                    'note': 'Say it out loud once: slash means contents. It is the single most useful sentence in this module.',
                },
                {
                    'label': 'Using it safely',
                    'code': 'rsync -av --dry-run src/ host:dest/   look first\nrsync -av src/ host:dest/            then do it\n\n-a  archive: recursive, keeps permissions,\n    times, symlinks\n-v  verbose      -z  compress in transit\n--delete  make dest match src exactly\n-P  progress and resume partial files',
                    'note': '`-avP --dry-run` is the combination to type by reflex before anything with --delete.',
                },
            ],
            'misconceptions': [
                'The trailing slash on the DESTINATION does almost nothing. It is the source slash that changes the result.',
                '`--delete` deletes on the destination, not the source, and with the wrong source slash that can be everything.',
                'rsync over ssh reads your `~/.ssh/config`, so an alias works here exactly as it does for ssh.',
            ],
            'try_it': [
                'Make two directories and run rsync both ways, with and without the source slash. Look at the result each time.',
            ],
        },
    ],
    'drills': [
        {
            'id': 'rm-cmd-scp',
            'type': 'command',
            'answer': 'scp file.txt host:',
            'prompt': 'Copy one file to your home directory on a remote host.',
            'teach': 'The bare colon means the remote home directory. Leave the colon off and you have quietly made a local copy instead.',
        },
        {
            'id': 'rm-cmd-rsync-contents',
            'type': 'command',
            'answer': 'rsync -av src/ dest/',
            'prompt': 'Copy the CONTENTS of src into dest, so dest/a.txt rather than dest/src/a.txt.',
            'teach': 'The trailing slash on the source means "the contents of". One character, completely different result.',
        },
        {
            'id': 'rm-cmd-rsync-into',
            'type': 'command',
            'answer': 'rsync -av src dest/',
            'prompt': 'Copy the directory src INTO dest, so you end up with dest/src/.',
            'teach': 'A trailing slash on the SOURCE copies its contents instead. That one character is the difference between dest/src/ and dest/.',
        },
        {
            'id': 'rm-cmd-rsync-dry',
            'type': 'command',
            'answer': 'rsync -av --dry-run src/ host:dest/',
            'prompt': 'Show what an rsync would do, without doing it.',
            'teach': 'Type this by reflex before anything with --delete.',
        },
    ],
    'challenges': [
        {
            'id': 'rm-trailing-slash',
            'title': 'The trailing slash, for real',
            'goal': 'Run rsync both ways between two local directories and see the difference the slash makes. This is the misconception the whole module is built around.',
            'setup': {
                'kind': 'sandbox',
                'tree': {
                    'src/': None,
                    'src/a.txt': 'alpha\n',
                    'src/b.txt': 'bravo\n',
                    'into/': None,
                    'contents/': None,
                },
            },
            'solution': {
                'shell': 'rsync -a src into/ && rsync -a src/ contents/',
            },
            'steps': [
                {
                    'instruction': 'Copy the src DIRECTORY into into/, so you end up with into/src/a.txt.',
                    'hint': 'rsync -a src into/    with no slash on src',
                },
                {
                    'instruction': 'Copy the CONTENTS of src into contents/, so you end up with contents/a.txt.',
                    'hint': 'rsync -a src/ contents/    with the slash',
                },
            ],
            'free': 'Using rsync twice, produce into/src/a.txt and also contents/a.txt, from the same source directory.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'exists': [
                        'into/src/a.txt',
                        'into/src/b.txt',
                        'contents/a.txt',
                        'contents/b.txt',
                    ],
                    'missing': [
                        'contents/src',
                        'into/a.txt',
                    ],
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'rm-rsync-dryrun',
            'title': 'Make --dry-run and --delete a habit',
            'goal': 'Sync two directories the safe way round, and see exactly what --delete would have removed before it removes it.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {
                    'src/keep.txt': 'keep me\n',
                    'src/also.txt': 'me too\n',
                    'src/nested/deep.txt': 'deeper\n',
                    'dest/keep.txt': 'keep me\n',
                    'dest/stale.txt': 'should not survive\n',
                },
            },
            'solution': {
                'shell': 'rsync -av --delete --dry-run src/ dest/ > planned.txt && rsync -a --delete src/ dest/ && find dest -type f | sort > after.txt',
            },
            'steps': [
                {
                    'instruction': 'Run the sync with --dry-run first, saving what it says it would do to planned.txt. Add -v, or a dry run prints nothing at all.',
                    'hint': 'rsync -av --delete --dry-run src/ dest/ > planned.txt',
                },
                {
                    'instruction': 'Read planned.txt and find the line about deleting stale.txt. That line is why the habit exists.',
                },
                {
                    'instruction': 'Now run it for real, then list what is in dest afterwards into after.txt.',
                    'hint': 'rsync -a --delete src/ dest/',
                },
                {
                    'instruction': 'Note the trailing slash on src/. Without it you would have got dest/src/ instead.',
                },
            ],
            'free': 'Produce planned.txt from a dry run showing the deletion, and after.txt listing dest once the real sync has mirrored src and removed the stale file.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_contains': {
                        'planned.txt': 'stale.txt',
                        'after.txt': [
                            'dest/keep.txt',
                            'dest/nested/deep.txt',
                        ],
                    },
                    'missing': [
                        'dest/stale.txt',
                        'dest/src',
                    ],
                    'file_lacks': {
                        'after.txt': 'stale',
                    },
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'rm-scp-rsync',
            'title': 'Move a tree twice, and compare the two tools',
            'goal': 'scp and rsync do overlapping jobs with different semantics, and the second run is where they differ most.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {
                    'source/one.txt': 'first\n',
                    'source/two.txt': 'second\n',
                    'source/sub/three.txt': 'third\n',
                },
            },
            'solution': {
                'shell': 'mkdir -p viascp viarsync && cp -r source/. viascp/ && rsync -a source/ viarsync/ && echo "changed" >> source/one.txt && rsync -a --itemize-changes source/ viarsync/ > second-run.txt && diff -r viascp viarsync > differences.txt; true',
            },
            'steps': [
                {
                    'instruction': 'Copy the tree into viascp using an ordinary recursive copy, standing in for scp -r.',
                    'hint': 'cp -r source/. viascp/',
                },
                {
                    'instruction': 'Copy it into viarsync with rsync -a, minding the trailing slash.',
                    'hint': 'rsync -a source/ viarsync/',
                },
                {
                    'instruction': 'Change one source file, then run rsync again with --itemize-changes into second-run.txt.',
                    'hint': 'rsync -a --itemize-changes source/ viarsync/',
                },
                {
                    'instruction': 'Read second-run.txt. Only the changed file is listed, which is what rsync is for and what scp cannot do.',
                },
                {
                    'instruction': 'Diff the two destinations into differences.txt.',
                },
            ],
            'free': 'Produce viascp and viarsync holding the same tree, and second-run.txt showing that a second rsync transfers only what changed.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'is_file': [
                        'viascp/one.txt',
                        'viarsync/sub/three.txt',
                        'differences.txt',
                    ],
                    'file_contains': {
                        'second-run.txt': 'one.txt',
                    },
                    'file_lacks': {
                        'second-run.txt': 'three.txt',
                    },
                },
            },
            'fallback': 'self',
        },
    ],
    'quiz': [
        {
            'id': 'srq-slash',
            'type': 'mcq',
            'prompt': 'What does the trailing slash on an rsync SOURCE change?',
            'answer': 'src/ copies the contents of src, while src copies the directory itself into the destination.',
            'distractors': [
                'It forces rsync to delete extra files at the destination.',
                'It is required or rsync refuses to run.',
                'It makes the transfer recursive.',
            ],
            'teach': 'Slash means "the contents of". `rsync -a src/ dest/` gives dest/a.txt; `rsync -a src dest/` gives dest/src/a.txt.',
        },
        {
            'id': 'srq-delete',
            'type': 'mcq',
            'prompt': 'What does rsync --delete remove, and where?',
            'answer': 'Files on the destination that no longer exist on the source.',
            'distractors': [
                'Files on the source once they are safely copied.',
                'Files on both sides that differ.',
                'Nothing until you also pass --force.',
            ],
            'teach': 'It makes the destination match the source exactly. Combined with a wrong source slash it can delete a great deal, so --dry-run first.',
        },
        {
            'id': 'srq-second',
            'type': 'mcq',
            'prompt': 'You copy a tree, change one file, and copy again. Why rsync over scp?',
            'answer': 'rsync transfers only the changed file the second time; scp copies everything again.',
            'distractors': [
                'scp cannot copy directories at all.',
                'rsync encrypts and scp does not.',
                'scp corrupts files larger than a few megabytes.',
            ],
            'teach': 'rsync copies differences, resumes and preserves metadata. That second run is where the two tools diverge most.',
        },
        {
            'id': 'srq-config',
            'type': 'mcq',
            'prompt': 'You have a Host alias in ~/.ssh/config. Does rsync see it?',
            'answer': 'Yes, rsync runs over ssh and reads the same config, so the alias works unchanged.',
            'distractors': [
                'No, rsync has its own separate hosts file.',
                'Only if you pass -e ssh explicitly.',
                'Only for pulls, not for pushes.',
            ],
            'teach': 'scp, sftp and git over ssh read it too. One alias fixes all of them at once.',
        },
    ],
}
