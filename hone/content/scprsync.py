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
            'id': 'xfer-what',
            'title': 'Getting a file from here to there',
            'next': 'scp-basics',
            'concept': (
                'scp and rsync are how you put a file on another machine, or '
                'pull one back. That is why they are the pair to reach for '
                'once ssh works and the file is still only here. There are '
                'two tools worth knowing, they look almost identical, and '
                'choosing between them is the whole of this module.\n\n'
                '**Both of them ride on ssh.** That is the piece to '
                'internalise first: neither scp nor rsync is a network '
                'protocol. They run ssh underneath, so if `ssh server` works, '
                'they work, with the same keys, the same `~/.ssh/config` '
                'aliases and the same jump hosts. If ssh does not work, '
                'nothing here will, and fixing ssh is the whole fix.\n\n'
                '**The syntax borrows from cp**, with a colon marking the '
                'remote side. `scp file server:/tmp/` means "this local file, '
                'to that path over there". The colon is doing all the work, '
                'and leaving it out quietly performs a local copy to a file '
                'named `server` instead, which is the classic first '
                'mistake.\n\n'
                '**scp copies. rsync synchronises.** scp sends everything you '
                'named, every time, no questions. rsync compares the two '
                'sides first and sends only what differs, which on the second '
                'run of a large directory is the difference between minutes '
                'and seconds. rsync can also resume, preserve permissions and '
                'timestamps properly, and delete things on the far side that '
                'you deleted here.\n\n'
                'The rule of thumb: **one file once, scp. A directory, or '
                'more than once, rsync.** rsync is not harder, it just has '
                'one piece of syntax that catches everybody, and the next '
                'lessons are largely about that.'
            ),
            'examples': [
                {
                    'label': 'The shape, both directions',
                    'code': ('scp report.pdf server:/tmp/     to there\n'
                             'scp server:/tmp/report.pdf .    from there\n'
                             '\n'
                             'the colon marks which side is remote'),
                    'note': 'No colon anywhere means both sides are local, '
                            'and scp will happily do that without comment.',
                },
                {
                    'label': 'Why it needs no configuration',
                    'code': ('ssh prod           works?\n'
                             'scp file prod:     then this works too\n'
                             'rsync -a dir/ prod:/srv/   and this\n'
                             '\n'
                             'same keys, same config, same aliases'),
                    'note': 'A host alias you defined in ~/.ssh/config is '
                            'usable here immediately. Nothing needs telling '
                            'twice.',
                },
                {
                    'label': 'The same job, twice',
                    'code': ('scp -r site/ server:/var/www/\n'
                             '  second run: sends all of it again\n'
                             '\n'
                             'rsync -a site/ server:/var/www/\n'
                             '  second run: sends what changed'),
                    'note': 'On a directory you will transfer more than once, '
                            'this is not a small difference, and it is the '
                            'reason rsync exists.',
                },
            ],
            'misconceptions': [
                'scp and rsync are not network protocols. They are programs '
                'that drive ssh, which is why they inherit every part of your '
                'ssh setup for free.',
                'rsync is not only for backups. It is the better choice for '
                'any repeated transfer, and most transfers turn out to be '
                'repeated.',
                'A missing colon is not an error. `scp file server` copies '
                'the file to a local file named server, silently and '
                'successfully.',
            ],
            'try_it': [
                'Copy one file to a machine you can ssh to, then copy it '
                'back. Note that you configured nothing.',
                'Copy a directory with rsync twice in a row and watch how '
                'much less the second run transfers.',
            ],
        },
        {
            'id': 'scp-basics',
            'title': 'scp: copying over the same connection as ssh',
            'concept': (
                'The previous lesson said both tools ride on ssh. This one is '
                'the smaller of the two, the one you reach for when the job '
                'is one file and you want it over there now.\n\n'
                'scp copies files over ssh, using the same keys, the same '
                'config and the same aliases, so once ssh works, scp works. '
                'The shape is `scp SOURCE DEST`, where a remote side is '
                'written `host:path` with a colon. Leave the colon off and '
                'you have quietly made a local copy instead. There is no '
                'error. The file sits in the current directory with the '
                'hostname as its name, and nothing left the machine.\n\n'
                'A bare colon means the remote home directory, so `scp '
                'report.txt web:` drops the file in your home on web. '
                'Copying the other way just swaps the arguments: `scp '
                'web:/etc/hostname .` brings it here. `-r` copies a '
                'directory. `-P` sets the port, capital P, because lowercase '
                '`-p` preserves timestamps, which is the opposite of what '
                'you reach for when ssh taught you `-p`.\n\n'
                'There is no progress bar by default and no resume. A dropped '
                'link starts the whole file over. That is why scp is fine '
                'for one file or a small handful, and why the next lesson is '
                'the tool you actually want the moment the tree is large or '
                'the transfer will happen twice.\n\n'
                'A trailing slash on the source is just a path to scp. It is '
                'not the rsync rule. Mixing the two is how people copy a '
                'directory into itself and wonder where the extra folder '
                'came from.'
            ),
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
            'concept': (
                '`scp` copies a file and is fine for one file. `rsync` copies '
                'only differences, resumes, preserves permissions, and can '
                'delete things on the destination that no longer exist on '
                'the source. For anything more than one file, rsync.\n\n'
                '**How it knows what differs**, because this is the part that '
                'makes it feel like magic. For each file, rsync compares size '
                'and modification time; if they match it skips the file '
                'entirely. If they differ, it does not resend the file, it '
                'splits both copies into blocks, compares checksums, and '
                'sends only the blocks that changed. Appending a line to a '
                'one-gigabyte log transfers a few kilobytes.\n\n'
                '**`-a` is the flag you will use every time.** It is not one '
                'option but a bundle: recurse into directories, preserve '
                'permissions, timestamps, symlinks, owner and group. Without '
                'it you get a copy whose metadata is subtly wrong in ways you '
                'discover much later. Add `-v` to see what moved and `-h` to '
                'make the sizes readable, and `-avh` becomes muscle '
                'memory.\n\n'
                '**The trailing slash on the SOURCE catches everyone**, and it '
                'is worth learning deliberately rather than by accident. '
                '`rsync -a src dest/` copies the directory **into** dest, '
                'giving `dest/src/`. `rsync -a src/ dest/` copies the '
                '**contents** of src into dest. One character, completely '
                'different result. The way to remember it: a trailing slash '
                'means "the things inside", not "the thing".\n\n'
                'The slash on the destination changes nothing at all, which '
                'is why people conclude the rule is inconsistent. It is not, '
                'it just only applies to one side.\n\n'
                '**`--delete` makes the destination match the source exactly**, '
                'including removing files that are no longer in the source. '
                'That is what you want for a mirror and it is a loaded gun '
                'pointed at the destination: combined with a wrong trailing '
                'slash, or a source that failed to mount and is therefore '
                'empty, it will remove a great deal very efficiently.\n\n'
                '**`--dry-run` first, every time.** It is a habit rather than '
                'a flag: `-n` shows exactly what would happen and changes '
                'nothing. On any command with `--delete` in it, running '
                'without `-n` first is how the story starts.\n\n'
                '`-P` is `--progress` plus `--partial`. Progress prints each '
                'file as it moves; `--partial` keeps an unfinished copy so a '
                'dropped link resumes rather than starting over. That is why '
                '`-avP` is the everyday form for a large tree. `-P` does not '
                'print a single total for the whole run: each file gets its '
                'own bar, and a tree of thousands looks like noise. '
                '`--info=progress2` is the tree total, one running count for '
                'the whole transfer.'
            ),
            'examples': [
                {
                    'label': 'The trailing slash',
                    'code': 'src/  contains  a.txt  b.txt\n\nrsync -a src  dest/   ->  dest/src/a.txt\nrsync -a src/ dest/   ->  dest/a.txt\n\nthe slash means "the contents of"',
                    'note': 'Say it out loud once: slash means contents. It is the single most useful sentence in this module.',
                },
                {
                    'label': 'Using it safely',
                    'code': 'rsync -av --dry-run src/ host:dest/   look first\nrsync -av src/ host:dest/            then do it\n\n-a  archive: recursive, keeps permissions,\n    times, symlinks\n-v  verbose      -z  compress in transit\n--delete  make dest match src exactly\n-P  --progress plus --partial (resume)\n--info=progress2   one total for the tree\n--exclude .git --exclude node_modules',
                    'note': '`-avP --dry-run` is the combination to type by reflex before anything with --delete. Use --info=progress2 when the per-file bar is too noisy to read.',
                },
            ],
            'misconceptions': [
                'The trailing slash on the DESTINATION does almost nothing. It is the source slash that changes the result.',
                '`--delete` deletes on the destination, not the source, and with the wrong source slash that can be everything.',
                'rsync over ssh reads your `~/.ssh/config`, so an alias works here exactly as it does for ssh.',
                '`-P` means the port to scp and progress to rsync. rsync takes a port through ssh instead: `-e \'ssh -p 2222\'`.',
                'The trailing slash rule belongs to rsync alone. `scp -r` copies the directory itself whether or not you write a slash.',
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
            'id': 'srd-exclude',
            'type': 'command',
            'answer': 'rsync -av --exclude .git src/ host:dest/',
            'prompt': 'Sync a project without copying its git directory.',
            'teach': 'The first real tree you sync has a .git or a node_modules in it, and --exclude repeats for each pattern you want left behind.',
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
