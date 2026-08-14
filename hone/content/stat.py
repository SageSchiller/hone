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
    'order': 72,
    'blurb': 'The four timestamps, mtime versus ctime, and why touch does not fool ctime.',
    'lessons': [
        {
            'id': 'tr-times',
            'title': 'Timestamps, and how much to trust them',
            'concept': 'A Linux file has three timestamps in the classic model and four on most modern filesystems, and confusing them is the usual mistake.\n\nmtime is when the contents last changed. atime is when it was last read, and is often disabled or lazily updated for performance, so its absence means nothing. ctime is when the inode last changed, which covers permissions, ownership and link count as well as content, and it is the one that is hardest to set. btime is the creation time, exposed by `stat` where the filesystem records it.\n\nThe forensic point is the asymmetry. `touch` sets mtime and atime to anything you like, in one command, with no privileges. ctime updates as a side effect and cannot be set directly through the normal interface. So a file whose mtime is older than its ctime by a long way is a file worth asking about, and a directory where every file has the same convenient timestamp is worth asking about too.\n\nNone of this is proof. Timestamps are evidence with a known and easy tampering path, which is exactly why they are read alongside hashes rather than instead of them.',
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
            'next': None,
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
    ],
    'challenges': [
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
    ],
}
