"""stat: a file's metadata, and how far to trust a timestamp.

stat shows the size, permissions, inode, link count and the four timestamps. The forensic point is the asymmetry: touch sets mtime and atime to anything with no privileges, while ctime moves as a side effect and cannot be set directly, so a file whose mtime is far older than its ctime is worth asking about. Sandbox-verified.
"""

MODULE = {
    'context': 'You are at a shell prompt with an unknown file in front of you, and you will not run it.',
    'prereqs': [
        'linux',
        'linuxutils',
    ],
    'adapter': 'sandbox',
    'group': 'Security',
    'id': 'stat',
    'title': 'stat',
    'needs': [],
    'estimate': '1-2 hours',
    'order': 76,
    'blurb': 'The four timestamps, mtime versus ctime, and why touch does not fool ctime.',
    'lessons': [
        {
            'id': 'tr-inode',
            'title': 'The file, and the thing that describes it',
            'next': 'tr-times',
            'concept': (
                '`stat` is how you read the inode: size, permissions, owner, '
                'link count and timestamps, without opening the contents. '
                'That is why it works on a file you would rather not open '
                'and on one far too large to.\n\n'
                'The contents live in blocks on the disk. Everything else '
                'about the file lives in an **inode**: the size, the '
                'permissions, the owner, the link count, and the timestamps. '
                'The name is not in the inode at all. A name is an entry in a '
                'directory that points at an inode, which is why one file can '
                'have several names and why renaming a file changes nothing '
                'about the file itself.\n\n'
                '`stat` is the command that prints the inode. `ls -l` shows a '
                'chosen handful of the same information, formatted for '
                'scanning; `stat` shows all of it, formatted for reading. '
                'When the two seem to disagree they do not: `ls` is showing a '
                'different field than you assumed.\n\n'
                '**This is why there are several timestamps rather than one.** '
                'Changing the contents and changing the permissions are edits '
                'to two different places, so they are recorded separately. '
                'That separation is invisible until you need it, and then it '
                'is the entire subject.\n\n'
                'Everything here is read-only and instant. `stat` never opens '
                'the contents, so it works on a file you would rather not '
                'open and on one far too large to.\n\n'
                'The next lesson is those timestamps, and how far to '
                'trust each one.'
            ),
            'examples': [
                {
                    'label': 'Name, inode, contents',
                    'code': ('notes.txt  ---\\\n'
                             '                >-- inode 8214 --> the bytes\n'
                             'backup.txt ---/    size, mode, owner,\n'
                             '                   timestamps, link count'),
                    'note': 'Two names, one inode, one file. `ln` makes this, '
                            'and the link count in stat is how you notice it '
                            'has happened.',
                },
                {
                    'label': 'The same file, two views',
                    'code': ('ls -l notes.txt\n'
                             '  -rw-r--r-- 1 sage sage 42 Aug 14 09:12\n'
                             '\n'
                             'stat notes.txt\n'
                             '  Size, Blocks, inode, Links,\n'
                             '  Access, Modify, Change, Birth'),
                    'note': 'ls shows one timestamp and does not say which. '
                            'It is mtime, and that unlabelled default has '
                            'misled a lot of people.',
                },
            ],
            'misconceptions': [
                'The filename is not part of the file. It lives in the '
                'directory, and the inode does not know it.',
                '`ls -l` does not show you "the" timestamp. It shows one of '
                'four, chosen for you, with no label on it.',
                'stat does not read the contents. It reads the inode, which '
                'is why it returns instantly on a file of any size.',
            ],
            'try_it': [
                'Run `stat` on any file and find the inode number and the '
                'link count in the output.',
                'Make a hard link with `ln a b`, run stat on both, and '
                'confirm you are looking at one inode under two names.',
            ],
        },
        {
            'id': 'tr-times',
            'title': 'Timestamps, and how much to trust them',
            'concept': 'The previous lesson left open why there are several timestamps rather than one. A Linux file has three timestamps in the classic model and four on most modern filesystems, and confusing them is the usual mistake.\n\nmtime is when the contents last changed. atime is when it was last read, and is often disabled or lazily updated for performance, so its absence means nothing. ctime is when the inode last changed, which covers permissions, ownership and link count as well as content, and it is the one that is hardest to set. btime is the creation time, exposed by `stat` where the filesystem records it.\n\nThe forensic point is the asymmetry. `touch` sets mtime and atime to anything you like, in one command, with no privileges. ctime updates as a side effect and cannot be set directly through the normal interface. So a file whose mtime is older than its ctime by a long way is a file worth asking about, and a directory where every file has the same convenient timestamp is worth asking about too.\n\nNone of this is proof. Timestamps are evidence with a known and easy tampering path, which is exactly why they are read alongside hashes rather than instead of them.',
            'examples': [
                {
                    'label': 'All of them at once',
                    'code': 'stat sample.bin',
                    'note': 'Access, Modify, Change and Birth, plus size, inode, links and mode.',
                },
                {
                    'label': 'Just the one you want, formatted',
                    'code': 'stat -c "%y %n" *',
                    'note': '%y is mtime, %z is ctime, %w is birth. Scriptable and stable.',
                },
                {
                    'label': 'Sort a directory by modification time',
                    'code': 'ls -lt --time-style=full-iso',
                    'note': 'The full ISO stamp includes seconds, which the default drops.',
                },
                {
                    'label': 'Find what changed in the last day',
                    'code': 'find . -newermt "-1 day" -type f',
                    'note': 'By mtime. -newerct compares ctime, which is the harder one to fake.',
                },
            ],
            'misconceptions': [
                'ctime is not creation time. It is inode change time, and the creation time is btime where it exists at all.',
                'An atime that never updates is normal. relatime and noatime are the common mount defaults.',
                'touch can set mtime and atime to any value at all, so a plausible mtime is not evidence of anything on its own.',
            ],
            'try_it': [
                'Use touch -d to backdate a file, then compare its mtime and ctime with stat.',
                'chmod a file and watch which of the four timestamps moves.',
            ],
            'next': 'tr-timeline',
        },
        {
            'id': 'tr-timeline',
            'title': 'Building a timeline, and reading it sceptically',
            'concept': (
                'One file\'s timestamps are trivia. **A directory\'s '
                'timestamps, sorted, are a narrative**, and producing that '
                'narrative quickly is the skill this module exists for.\n\n'
                'The trick is `stat -c`, which prints exactly the fields you '
                'name in the order you name them. Put the timestamp first and '
                'pipe to `sort`, and a directory becomes a sequence of '
                'events. `%y` is mtime, `%z` is ctime, `%x` is atime, `%w` is '
                'birth, `%n` is the name, and `%a` is the permission bits in '
                'octal.\n\n'
                '`find` does the filtering half. `-newermt "-1 day"` selects '
                'by modification time against a date you describe in words. '
                'The `-newerXY` family generalises it: `-newerct` compares '
                'ctime to a time, and `-newercm` compares one file\'s ctime '
                'to another\'s mtime, which sounds baroque and is exactly how '
                'you ask "what was touched after this thing happened".\n\n'
                '**Now the sceptical half, which is the point.** A timeline '
                'is a story assembled from a record anyone with access could '
                'edit, so read it for **internal contradictions** rather than '
                'for truth:\n\n'
                'An mtime far older than its ctime says the content was '
                'backdated after the inode last changed. Every file in a '
                'directory sharing one convenient timestamp says a loop set '
                'them. A file whose btime is later than its mtime is claiming '
                'to have been modified before it existed. None of these is '
                'proof, and all of them are questions.\n\n'
                'Which is why timestamps travel with hashes. A hash says the '
                'content is what it was; a timestamp says when someone would '
                'like you to think it got there.'
            ),
            'examples': [
                {
                    'label': 'A directory as a sequence of events',
                    'code': ('stat -c "%y %n" * | sort\n'
                             '\n'
                             '2026-08-01 09:14 notes.txt\n'
                             '2026-08-13 22:07 .bashrc\n'
                             '2026-08-13 22:07 .profile\n'
                             '2026-08-13 22:08 authorized_keys'),
                    'note': 'Three files in one minute, late at night, one of '
                            'them an ssh key. The sort did all of that work.',
                },
                {
                    'label': 'Filtering to a window',
                    'code': ('find . -newermt "-1 day" -type f\n'
                             '   changed in the last 24 hours\n'
                             '\n'
                             'find . -newerct "2026-08-13 22:00" -type f\n'
                             '   inode changed after that moment'),
                    'note': 'The date is parsed in plain language, so "-2 '
                            'hours", "yesterday" and a full timestamp all '
                            'work.',
                },
                {
                    'label': 'The three contradictions worth looking for',
                    'code': ('mtime << ctime    content backdated\n'
                             'many identical     set by a loop\n'
                             'btime > mtime      modified before it existed\n'
                             '\n'
                             'stat -c "%w|%x|%y|%z|%n" suspicious.sh'),
                    'note': 'ctime is the awkward one to forge because there '
                            'is no normal interface for setting it, which is '
                            'precisely why it is the one to compare against.',
                },
            ],
            'misconceptions': [
                'A timeline is not a record of what happened. It is a record '
                'of what the filesystem noticed, which anyone with write '
                'access could have arranged.',
                'ctime is not the creation time, despite the c. It is the '
                'inode change time, and btime is the creation time where the '
                'filesystem records one at all.',
                'Matching timestamps across a directory are not necessarily '
                'suspicious. Package installs and checkouts do it constantly, '
                'which is why the question is whether this directory should '
                'look like that.',
            ],
            'try_it': [
                'Run `stat -c "%y %n" *` in your home directory, pipe it to '
                'sort, and read the last ten lines as a story.',
                'Backdate a file with `touch -d`, then print mtime and ctime '
                'side by side and see the contradiction you just created.',
            ],
        },
    ],
    'drills': [
        {
            'id': 'trd-stat',
            'type': 'command',
            'prompt': 'Show every timestamp and inode detail of sample.bin.',
            'answer': 'stat sample.bin',
            'teach': 'Access, Modify, Change and Birth. Four different questions that get confused constantly.',
        },
        {
            'id': 'trd-stat-format',
            'type': 'command',
            'prompt': 'Print the modification time and name of every file here.',
            'answer': 'stat -c "%y %n" *',
            'teach': '%y is mtime, %z is ctime, %w is birth. Scriptable and unambiguous, unlike ls output.',
        },
        {
            'id': 'trd-touch-backdate',
            'type': 'command',
            'prompt': 'Set the modification time of note.txt to 1 January 2020.',
            'answer': 'touch -d "2020-01-01" note.txt',
            'teach': 'No privileges needed, which is exactly why mtime alone proves nothing.',
        },
        {
            'id': 'trd-find-newer',
            'type': 'command',
            'prompt': 'Find files here modified in the last day.',
            'answer': 'find . -newermt "-1 day" -type f',
            'teach': '-newermt compares mtime, -newerct compares ctime, and the second is the harder one to forge.',
        },
        {'id': 'std-octal', 'type': 'command',
         'answer': 'stat -c "%a %n" *',
         'prompt': 'Print the octal permissions and name of every file here.',
         'teach': 'The most common scripting use of stat: 644 is far easier to test in a script than the rw-r--r-- that ls prints.'},
    ],
    'challenges': [
        {
            'id': 'trc-timeline',
            'title': 'Turn a directory into a timeline',
            'goal': 'Backdate two files, then produce the sorted list of what happened when. This is the move that turns a pile of files into a sequence of events.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {
                    'a.txt': 'first\n',
                    'b.txt': 'second\n',
                    'c.txt': 'third\n',
                },
            },
            'solution': {
                'shell': 'touch -d "2020-01-01" a.txt && touch -d "2022-06-15" b.txt && stat -c "%y %n" a.txt b.txt c.txt | sort > timeline.txt',
            },
            'steps': [
                {
                    'instruction': 'Set a.txt to have been modified on 2020-01-01.',
                    'hint': 'touch -d "2020-01-01" a.txt',
                },
                {
                    'instruction': 'Set b.txt to 2022-06-15. Leave c.txt alone, so it keeps today.',
                    'hint': 'touch -d "2022-06-15" b.txt',
                },
                {
                    'instruction': 'Print the modification time and name of all three, sorted, into timeline.txt.',
                    'hint': 'stat -c "%y %n" a.txt b.txt c.txt | sort > timeline.txt',
                },
                {
                    'instruction': 'Read it. Because the timestamp leads the line, sorting the text sorted the events.',
                },
            ],
            'free': 'Backdate a.txt to 2020-01-01 and b.txt to 2022-06-15, then write timeline.txt: one line per file, modification time first, sorted oldest to newest.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_contains': {
                        'timeline.txt': ['2020-01-01', '2022-06-15', 'a.txt', 'b.txt', 'c.txt'],
                    },
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'trc-window',
            'title': 'Ask what changed after a date',
            'goal': 'Use find to select by time rather than by name, which is how you answer "what was touched since the incident" without reading anything.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {
                    'a.txt': 'old\n',
                    'b.txt': 'newer\n',
                    'c.txt': 'newest\n',
                },
            },
            'solution': {
                'shell': 'touch -d "2020-01-01" a.txt && touch -d "2022-06-15" b.txt && find . -newermt "2021-01-01" -name "[abc].txt" | sort > recent.txt',
            },
            'steps': [
                {
                    'instruction': 'Backdate a.txt to 2020-01-01 and b.txt to 2022-06-15, as before.',
                    'hint': 'touch -d "2020-01-01" a.txt',
                },
                {
                    'instruction': 'Find the files modified after 2021-01-01 and write them, sorted, to recent.txt.',
                    'hint': 'find . -newermt "2021-01-01" -name "[abc].txt" | sort > recent.txt',
                },
                {
                    'instruction': 'Check that a.txt is absent. It is older than the cutoff, which is the whole point.',
                },
            ],
            'free': 'Backdate a.txt to 2020 and b.txt to 2022, then produce recent.txt listing only the files modified after 2021-01-01.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_contains': {'recent.txt': ['b.txt', 'c.txt']},
                    'file_lacks': {'recent.txt': 'a.txt'},
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'trc-timestamps',
            'title': 'Catch a backdated file',
            'goal': 'Backdate a file yourself, then show the timestamp that did not go along with it.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {
                    'report.txt': 'quarterly figures\n',
                },
            },
            'solution': {
                'shell': 'touch -d "2019-03-04 10:00:00" report.txt && stat -c "%n mtime=%y ctime=%z" report.txt > times.txt',
            },
            'steps': [
                {
                    'instruction': 'Set the modification time of report.txt to some date in 2019.',
                    'hint': 'touch -d "2019-03-04 10:00:00" report.txt',
                },
                {
                    'instruction': 'Record its mtime and ctime together into times.txt.',
                    'hint': 'stat -c "%n mtime=%y ctime=%z" report.txt > times.txt',
                },
                {
                    'instruction': 'Read them. The mtime is 2019 and the ctime is today, because touch could not move it.',
                },
            ],
            'free': 'Produce times.txt showing report.txt with an mtime in 2019 and a ctime of today.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_contains': {
                        'times.txt': [
                            'mtime=2019',
                            'ctime=20',
                        ],
                    },
                },
            },
            'fallback': 'self',
        },
    ],
    'quiz': [
        {
            'id': 'trq-ctime',
            'type': 'mcq',
            'prompt': 'A file has an mtime from 2019 and a ctime from this morning. What does that suggest?',
            'answer': 'Its metadata changed today, and the mtime may have been set deliberately.',
            'distractors': [
                'The file was created this morning and last edited in 2019.',
                'The filesystem lost the original ctime.',
                'Nothing: ctime always tracks the current time.',
            ],
            'teach': 'touch sets mtime and atime freely. ctime moves as a side effect and cannot be set through the normal interface, which is what makes the mismatch interesting.',
        },
        {
            'id': 'trq-atime',
            'type': 'mcq',
            'prompt': 'A file you know was read yesterday shows an old atime. Why?',
            'answer': 'Most filesystems mount with relatime or noatime, so atime rarely updates.',
            'distractors': [
                'Reading a file does not update atime on Linux.',
                'The read came from cache, so no timestamp changed.',
                'atime only updates for writes.',
            ],
            'teach': 'Its absence means nothing at all, which is why atime is the weakest of the four timestamps.',
        },
        {
            'id': 'trq-btime',
            'type': 'mcq',
            'prompt': 'What is the difference between ctime and btime?',
            'answer': 'ctime is inode change; btime is creation, where the filesystem records it.',
            'distractors': [
                'ctime is creation; btime is the last backup time.',
                'They are aliases for the same field on Linux.',
                'ctime is content change; btime is inode change.',
            ],
            'teach': 'The c in ctime is change, not create. ls -l shows mtime and labels none of them, which is how the mix-up starts.',
        },
        {
            'id': 'trq-ls-time',
            'type': 'mcq',
            'prompt': 'Which timestamp does ls -l print, and how is it labelled?',
            'answer': 'mtime, with no label, which is why people treat it as the time.',
            'distractors': [
                'ctime, labelled Change.',
                'btime, labelled Birth.',
                'atime, labelled with the word Access.',
            ],
            'teach': 'stat names all four. The unlabelled ls default is the one that has misled people into thinking a file has a single time.',
        },
    ],
}
