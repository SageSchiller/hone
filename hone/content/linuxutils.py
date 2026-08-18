"""Linux Utilities: the daily tools, taught as models rather than flags.

This module was once a deliberate drill deck with no lessons, on the argument
that these tools are "I know what I want and cannot remember the flags". That
was reversed at the author's instruction: **every tool gets a full walkthrough,
no drill decks.** The reversal turned out to improve the content rather than
pad it, because each of these tools does have a model worth teaching. `find` is
a small query language, not a search command. `lsof` rests on "everything is an
open file", which is broader than it sounds. Links only make sense once you see
that a name is a pointer to an inode. `df` and `du` disagree for a reason worth
understanding. tar packs a tree; gzip compresses one stream, which is why a
`.gz` log is not an archive. The flags are still the daily friction, and the
drills still carry them, but the lessons now supply the idea the flags hang off.
"""

MODULE = {
    'id': 'linuxutils',
    'title': 'Linux Utilities',
    'group': 'Linux',
    'blurb': 'find, lsof, tar, gzip, links, and inspecting files, bytes and space.',
    'context': 'You are at a shell prompt. The answer is a command you would actually type.',
    'prereqs': ['linux'],
    'adapter': 'sandbox',
    'estimate': '3-4 hours',
    'order': 13,

    'lessons': [
        {
            'id': 'lu-find',
            'title': 'find: a query language for the filesystem',
            'next': 'lu-lsof',
            'concept': (
                'find is not a search command with a pile of flags. It is a '
                'tiny query language, and once you see that, the flags stop '
                'being arbitrary. You give it a starting directory, then a '
                'series of **tests** each file is checked against, and '
                '**actions** to take on the ones that pass. It walks the tree '
                'and evaluates the tests left to right, short-circuiting like '
                '`&&`.\n\n'
                'The common tests are `-name` (by name, with globs), `-type` '
                '(`f` file, `d` directory, `l` symlink), `-mtime` (by age in '
                'days), `-size`, `-maxdepth` (do not walk into subtrees: '
                '`find src -maxdepth 1 -type f` is this directory only), '
                'and `-newer file` (modified more recently than that file). '
                'The signs on `-mtime` and `-size` are the '
                'thing everyone gets wrong: `-mtime -7` is "less than seven '
                'days old", `+7` is "more than", and a bare `7` means the '
                'seventh day exactly, which matches almost nothing. Tests '
                'combine with an implied AND, and you can write `-o` for OR, '
                '`!` for NOT, and escaped parentheses to group.\n\n'
                'The default action is `-print`, but the powerful ones are '
                '`-exec` and `-delete`. `-exec cmd {} \\;` runs the command '
                'once per file, where `{}` is the file and `\\;` ends it. '
                '`-exec cmd {} +` batches many files into one invocation '
                'instead, which is dramatically faster on thousands of files. '
                'When you need to pipe the results into another command '
                'instead, `-print0` writes the names separated by null bytes '
                'so `xargs -0` can survive filenames with spaces and newlines. '
                'That is the entire reason both `-print0` and `-0` exist, and '
                'it is the safety habit worth building.\n\n'
                '`-prune` is the last piece: it tells find to skip a subtree, '
                'which is how you keep it out of `.git` or `node_modules`.\n\n'
                'The next lesson is lsof: the same machine, asked a different '
                'question. find walks names on disk. lsof lists what is '
                'already open, including files that no longer have a name.'
            ),
            'examples': [
                {
                    'label': 'The query shape',
                    'code': ('find . -type f -name "*.log" -mtime -7\n'
                             '     ^         ^            ^\n'
                             '  where     tests, combined with implied AND\n'
                             '\n'
                             'find . \\( -name "*.tmp" -o -name "*.bak" \\) '
                             '-delete'),
                    'note': 'Put -type f before -name and it rejects '
                            'directories before doing the string match, which '
                            'is faster.',
                },
                {
                    'label': 'Acting on what you found',
                    'code': ('find . -name "*.py" -exec grep -l TODO {} \\;\n'
                             '                                one run per file\n'
                             'find . -name "*.py" -exec grep -l TODO {} +\n'
                             '                                one run, many '
                             'files, faster\n'
                             'find . -print0 | xargs -0 rm\n'
                             '                                survives spaces '
                             'in names'),
                    'note': '{} is the file, \\; ends a per-file -exec, and + '
                            'batches instead. -print0 with xargs -0 is the '
                            'safe pipe.',
                },
                {
                    # -n1 and -I{} were drilled and never taught. They are also
                    # the two flags that make xargs do anything interesting.
                    'label': 'xargs, past the safe pipe',
                    'code': ('... | xargs -n1 echo\n'
                             '        one argument per run\n'
                             '\n'
                             '... | xargs -I{} mv {} /tmp/\n'
                             '        put the argument somewhere specific'),
                    'note': 'By default xargs crams as many arguments as it '
                            'can onto one command line, which is fast and '
                            'wrong when the command takes exactly one. -n1 '
                            'forces one at a time.',
                },
                {
                    'label': 'Why -I is the one you reach for',
                    'code': ('xargs mv /tmp/          appends: mv a b c /tmp/\n'
                             'xargs -I{} mv {} /tmp/  substitutes: mv a /tmp/\n'
                             '\n'
                             '-I implies -n1, because a placeholder\n'
                             'can only stand for one thing at a time'),
                    'note': 'Any command where the argument does not go last '
                            'needs -I. The brace pair is conventional, not '
                            'magic: -Ifoo works and reads worse.',
                },
            ],
            'misconceptions': [
                'Quote the `-name` pattern. Unquoted, the shell expands `*.log` '
                'against the current directory before find ever sees it.',
                '`-mtime 7` is not "within seven days". It is the seventh day '
                'exactly. You almost always want `-mtime -7`.',
                '`-exec {} \\;` and `-exec {} +` are different: the first runs '
                'the command once per file, the second batches them. On '
                'thousands of files that is the difference between slow and '
                'instant.',
                'A pipe of `find | xargs` breaks on a filename with a space '
                'unless you use `-print0` and `-0`. This is not paranoia; it is '
                'the first bug you hit on real data.',
            ],
            'try_it': [
                'In a directory tree, run `find . -type f -name "*.py"`, then '
                'add `-mtime -1`, then swap the action for `-exec wc -l {} +`.',
            ],
        },
        {
            'id': 'lu-lsof',
            'title': 'lsof: everything is an open file',
            'next': 'lu-tar',
            'concept': (
                'lsof lists open files, and the reason it is so useful is that '
                'on Linux "open file" means far more than a document. A network '
                'connection is an open file. A running program is an open file. '
                'A shared library mapped into memory is an open file. And a '
                'file that has been deleted while a process still holds it open '
                'is an open file that no longer has a name on disk. Once you '
                'see open files that broadly, lsof answers a whole class of '
                '"what is going on" questions.\n\n'
                'The deleted-but-held case is the one worth remembering, '
                'because it is the answer to a genuinely baffling situation: '
                '`df` says the disk is full, but `du` cannot find the space. '
                'That is almost always a log file that was deleted while a '
                'process kept writing to it. The bytes stay allocated until the '
                'process closes the handle, and `lsof +L1` lists exactly those '
                'files, so you can find the process and restart it.\n\n'
                'The everyday forms are short. `lsof -i :8080` shows who is '
                'listening on a port, which is how you find what to kill before '
                'starting your own server. `lsof -p 1234` shows everything one '
                'process has open. And `lsof /mnt/disk` shows who is using a '
                'path, which is the answer to "target is busy" when you cannot '
                'unmount something.\n\n'
                'The previous lesson walked the tree to find files by name. '
                'This one asks what is already open, which is a different '
                'question and the one `find` cannot answer. The next lesson is '
                'tar: one verb, one file, and why the `f` has to come last.'
            ),
            'examples': [
                {
                    'label': 'The four questions it answers',
                    'code': ('lsof -i :8080     who is on this port\n'
                             'lsof -p 1234      what has this process open\n'
                             'lsof /mnt/disk    who is holding this path busy\n'
                             'lsof +L1          deleted files still held open'),
                    'note': '+L1 means "link count below 1", which is exactly a '
                            'file with no name left on disk.',
                },
                {
                    'label': 'Disk full, du finds nothing',
                    'code': ('df -h /var          100% used\n'
                             'du -sh /var/*       the numbers do not add up\n'
                             'sudo lsof +L1 /var  a deleted log, still open\n'
                             '                    restart that process'),
                    'note': 'df counts the bytes. du only sees names. A deleted '
                            'file with an open handle has no name, so only lsof '
                            'can point at it.',
                },
            ],
            'misconceptions': [
                'The "disk full but du finds nothing" mystery is almost always '
                'a deleted-but-held-open file. `lsof +L1` finds it; restarting '
                'the process frees the space.',
                'lsof needs privileges to see other users\' open files, so a '
                'partial answer usually means you should try it with sudo.',
                'A socket, a running binary and a mapped library all count as '
                'open files here, which is why lsof output is longer than you '
                'expect.',
            ],
            'try_it': [
                'Run `lsof -p $$` to see what your own shell has open, then '
                '`lsof -i` to see every network connection on the machine.',
            ],
        },
        {
            'id': 'lu-tar',
            'title': 'tar: one verb, one file, and options',
            'next': 'lu-gzip',
            'concept': (
                'tar\'s flags look like a random string and are not. Every tar '
                'command picks exactly one **verb**, almost always names a '
                '**file**, and optionally sets **compression**. The verb is '
                '`c` to create, `x` to extract, or `t` to list. The `f` flag is '
                'followed by the archive name, and it must come last among the '
                'clustered flags because the next argument belongs to it. The '
                'compression letter matches the extension: `z` for `.gz`, `j` '
                'for `.bz2`, `J` for `.xz`.\n\n'
                'So `tar -czf backup.tar.gz dir` reads as create, gzip, file, '
                'and `tar -xzf backup.tar.gz` is extract, gzip, file. On '
                'extraction modern tar detects the compression itself, so '
                '`tar -xf` usually works without the letter, but naming it does '
                'no harm.\n\n'
                'Two options matter for staying out of trouble. `-C dir` '
                'extracts into a directory you chose rather than the current '
                'one, which contains a "tar bomb" that would otherwise scatter '
                'files everywhere. And listing with `t` before extracting lets '
                'you read the paths first: an archive with absolute paths or '
                '`../` in it can write outside where you expected, and the '
                'listing is where you catch that.\n\n'
                'The previous lesson asked what is open. This one packs a '
                'tree. The `z` in `-czf` is gzip, but gzip on its own is a '
                'different tool: one stream, not a directory. That is the '
                'next lesson.'
            ),
            'examples': [
                {
                    'label': 'The verb, the file, the compression',
                    'code': ('tar -czf out.tar.gz dir/   create, gzip\n'
                             'tar -xzf out.tar.gz         extract\n'
                             'tar -tzf out.tar.gz         list, do not extract\n'
                             'tar -xzf out.tar.gz -C /tmp/here   extract there\n'
                             'tar -xzf out.tar.gz --strip-components=1'),
                    'note': 'z gzip, j bzip2, J xz. On extract, modern tar '
                            'auto-detects, so -xf alone usually works.',
                },
                {
                    'label': 'Look before you extract',
                    'code': ('tar -tzf mystery.tar.gz | head\n'
                             '  notes.txt\n'
                             '  ../../etc/cron.d/job    walk-out, stop\n'
                             '\n'
                             'tar -xzf safe.tar.gz -C /tmp/out\n'
                             '  extract only after the list looks right'),
                    'note': '`-t` is not optional on an archive you did not '
                            'make. Absolute paths and `../` are the two things '
                            'the listing is for.',
                },
            ],
            'misconceptions': [
                'The `f` must be immediately before the archive name, because '
                'that name is its argument. `tar -cfz` puts z where the name '
                'should be and fails confusingly.',
                'List with `-tf` before you extract an archive you did not '
                'make, and read the paths for a leading slash or a `../`.',
                '`-C` changes directory before extracting, which is the clean '
                'way to avoid an archive that has no top-level folder spraying '
                'files into your current one.',
            ],
            'try_it': [
                'Make a directory, `tar -czf` it, `tar -tzf` to list it, then '
                '`tar -xzf` it into a fresh directory with `-C`.',
            ],
        },
        {
            'id': 'lu-gzip',
            'title': 'gzip: one stream, not a tree',
            'next': 'lu-inspect',
            'concept': (
                'gzip compresses one stream of bytes. That is why a `.gz` '
                'log is not an archive, and why `tar -xzf app.log.gz` is '
                'the wrong tool. tar packs a tree and may then compress '
                'the pack. gzip only shrinks a single file, or whatever '
                'you pipe through it.\n\n'
                '`gzip app.log` writes `app.log.gz` and **deletes** '
                '`app.log`. That default is the first surprise. `gzip -k` '
                'keeps the original. `gzip -d` or `gunzip` inflates it '
                'back, and again eats the `.gz` unless you pass `-k`. '
                '`gzip` on a directory prints "is a directory -- ignored" '
                'and does nothing. A tree wants tar, then gzip, which is '
                'what `-czf` already did.\n\n'
                'Reading without writing a second file is the daily use. '
                '`zcat app.log.gz` prints the decompressed bytes to '
                'stdout. `zgrep error app.log.gz` searches them. A '
                'rotated log that is only on disk as `.gz` is still '
                'grepable; you do not have to unpack it into `/tmp` and '
                'remember to delete the copy.\n\n'
                '`gzip -l app.log.gz` prints compressed size, original '
                'size, and the name. `gzip -t` tests the stream without '
                'writing it out. Both are local and cheap. `file` on the '
                'result says "gzip compressed data" for a lone stream and '
                '"POSIX tar archive (gzip compressed)" for a `.tar.gz`, '
                'which is how you tell them apart before you pick a tool.\n\n'
                '`gzip -c` writes the stream to stdout and leaves the '
                'input alone, which is the pipe form: `cmd | gzip -c > '
                'out.gz`. That is the same default as zcat, in reverse.\n\n'
                'bzip2 and xz are the same model with a different '
                'letter (`bzcat`, `xzcat`). The stream is the thing to '
                'learn once. The next lesson is inspecting a file you '
                'did not write: `stat`, `file`, `strings`, `xxd`.'
            ),
            'examples': [
                {
                    'label': 'Keep the original, then read it',
                    'code': ('gzip -k app.log\n'
                             '  app.log      still here\n'
                             '  app.log.gz   the stream\n'
                             '\n'
                             'zcat app.log.gz\n'
                             'zgrep ERROR app.log.gz\n'
                             'gzip -l app.log.gz'),
                    'note': 'Without -k, app.log is gone. zcat and zgrep '
                            'never write a decompressed file.',
                },
                {
                    'label': 'A tree is tar, a log is gzip',
                    'code': ('gzip src/                 ignored, a directory\n'
                             'tar -czf src.tar.gz src/  the tree\n'
                             '\n'
                             'gzip -k app.log           the log\n'
                             'tar -xzf app.log.gz       not an archive'),
                    'note': '.tar.gz is a tar stream, then gzip. .gz alone '
                            'is just the file. file will tell you which.',
                },
            ],
            'misconceptions': [
                'gzip does not archive a directory. It compresses one '
                'file. tar is the tree; gzip is the stream.',
                'zcat is not "cat a .gz and hope". It decompresses to '
                'stdout. cat app.log.gz prints garbage.',
            ],
            'try_it': [
                'gzip -k a small text file, zcat it, gzip -l it, then '
                'gzip the original without -k and confirm only the .gz '
                'remains.',
            ],
        },
        {
            'id': 'lu-inspect',
            'title': 'What is this file, really',
            'next': 'lu-space',
            'concept': (
                'Three questions come up about a file you did not write, and '
                'each has its own tool. What are its properties? `stat` shows '
                'the size, the permissions, the inode, the link count and the '
                'four timestamps. What kind of file is it? `file` reads the '
                'first bytes and tells you, ignoring the extension entirely, '
                'which is why it disagrees with the name so usefully. What is '
                'inside it? `strings` prints the readable runs of characters, '
                'and `xxd` shows the raw bytes as hex when you need to see '
                'exactly what is there.\n\n'
                'Each of these has its own module, where the forensic angle '
                'is taught in full: what the magic bytes mean, how to carve '
                'data hidden after a file, how much to trust a timestamp. Here '
                'you meet them as everyday utilities: `stat` to check a '
                'timestamp, `file` to identify a download, `strings` to peek '
                'inside a binary for a version or a path.\n\n'
                '`xxd` has one trick worth knowing beyond the dump: `-s` seeks '
                'to an offset and `-l` limits the length, so `xxd -s 512 -l 64` '
                'shows 64 bytes starting half a kilobyte in. That is how you '
                'look at one structure inside a disk image without reading the '
                'whole thing.\n\n'
                'The fourth everyday question is "did this change". `diff '
                '-u old new` prints a unified patch: lines starting with `-` '
                'left, `+` arrived. No output means the files are the same. '
                '`diff -rq a/ b/` walks two trees and only names the files '
                'that differ, which is how you compare a backup to a live '
                'directory without opening either.\n\n'
                'The previous lesson packed files. This one asks what a file '
                'is before you treat it as one. The next lesson is space: why '
                '`df` and `du` disagree, and how to watch a number change.'
            ),
            'examples': [
                {
                    'label': 'Identity, type, and contents',
                    'code': ('stat notes.txt        metadata and timestamps\n'
                             'file mystery.bin      what it actually is\n'
                             'strings -n 8 binary   readable runs, min length 8\n'
                             'xxd file.bin | head   the raw bytes as hex\n'
                             'xxd -s 512 -l 64 img  64 bytes at offset 512'),
                    'note': 'file reads content, never the extension. strings '
                            'defaults to a minimum run of 4, which is noisy; '
                            '-n raises it.',
                },
                {
                    'label': 'When the name lies',
                    'code': ('file photo.jpg\n'
                             '  photo.jpg: Zip archive data\n'
                             'strings -n 8 photo.jpg | head\n'
                             '  PK\\x03\\x04   the zip signature, in ASCII\n'
                             'xxd -l 4 photo.jpg\n'
                             '  00000000: 504b 0304            PK..'),
                    'note': 'The extension said image. The first bytes said '
                            'archive. Trust `file`, then confirm with `xxd`.',
                },
                {
                    'label': 'Did this change',
                    'code': ('diff -u nginx.conf.orig nginx.conf\n'
                             '  --- a  +++ b, then -removed +added\n'
                             'diff -rq /backup/etc /etc\n'
                             '  only the files that differ'),
                    'note': 'Empty output is the success case. That is why a '
                            'quiet `diff` is not a frozen command.',
                },
            ],
            'misconceptions': [
                '`file` does not look at the extension. It reads the magic '
                'bytes, which is why a `.jpg` that is really a zip is caught '
                'here.',
                '`strings` with no `-n` uses a minimum of four characters and '
                'buries the real content in fragments. Raise it to 8 or 10.',
                'xxd offsets are hexadecimal, so a length from `ls` (decimal) '
                'and an offset in xxd need converting before they line up.',
            ],
            'try_it': [
                'Run `file` on a few files in `/bin`, then `stat` one and read '
                'every field, then `strings -n 8` a binary and skim it.',
            ],
        },
        {
            'id': 'lu-space',
            'title': 'Where the space went, and watching it change',
            'next': 'lu-links',
            'concept': (
                'Two tools answer "how full is the disk" and they disagree on '
                'purpose. `df` asks the filesystem itself and reports what it '
                'believes. `du` walks the tree and adds up the files it can '
                'find. When they disagree, the gap is information: usually it '
                'is a deleted file a process still holds open, which `df` counts '
                'and `du` cannot see (back to lsof), or files hidden underneath '
                'a mount point. `du -sh * | sort -h` is the one-liner for "what '
                'is eating this directory", sorted smallest to largest so the '
                'biggest thing is at the bottom of the list.\n\n'
                '`watch` reruns a command every few seconds and shows only the '
                'latest output, which is how you watch a number move without '
                'writing a loop. `watch -n 5 df -h` gives you a live disk meter. '
                '`-d` highlights what changed between runs.\n\n'
                '`tee` is a T-junction in a pipe. It writes its input to a file '
                'and also passes it along, so you can watch output scroll past '
                'and keep a copy at once. Its most-reached-for form is `sudo '
                'tee`: a plain `sudo cmd > /etc/file` does not work, because the '
                'shell opens the redirect as you before sudo runs, so `cmd | '
                'sudo tee /etc/file` is how you write to a root-owned file.\n\n'
                'The previous lesson identified a file. This one asks where '
                'the bytes went. The next lesson is names and inodes: why a '
                'filename is not the file, and why that makes two kinds of '
                'link.'
            ),
            'examples': [
                {
                    'label': 'Finding and watching space',
                    'code': ('df -h                   how full each filesystem '
                             'is\n'
                             'du -sh * | sort -h      what is eating this '
                             'directory\n'
                             'watch -n 5 df -h        a live disk meter\n'
                             'cmd | tee out.txt       see it and save it\n'
                             'echo 1 | sudo tee /proc/sys/...   write as root'),
                    'note': 'df asks the filesystem; du counts files. Their gap '
                            'is usually a deleted-but-held file or a mount.',
                },
                {
                    'label': 'Why sudo redirect fails',
                    'code': ('sudo echo 1 > /proc/sys/vm/drop_caches\n'
                             '  permission denied: the shell opened the file\n'
                             '\n'
                             'echo 1 | sudo tee /proc/sys/vm/drop_caches\n'
                             '  tee runs as root, so the write succeeds'),
                    'note': 'The redirect is done by your shell, not by sudo. '
                            'That is why the pipe-through-tee form exists.',
                },
            ],
            'misconceptions': [
                '`df` and `du` disagreeing is not a bug. The usual cause is a '
                'deleted file still held open, which df counts and du cannot '
                'find.',
                '`sudo cmd > /root/file` fails because the shell opens the '
                'redirect as you, before sudo runs. `cmd | sudo tee /root/file` '
                'is the fix.',
                '`watch` does not return on its own; it reruns until you press '
                'Ctrl-C. `-n` sets the interval and `-d` highlights changes.',
            ],
            'try_it': [
                'Run `du -sh * | sort -h` in your home directory, then '
                '`watch -n 2 ls -l` in a directory while you touch a file in '
                'another terminal.',
            ],
        },
        {
            'id': 'lu-links',
            'title': 'Names, inodes, and the two kinds of link',
            'next': 'lu-less',
            'concept': (
                'The previous lesson asked where the bytes went. This one is '
                'why two names can be the same file, which is the fact `du` '
                'counts once and `ls` shows twice.\n\n'
                'A filename is not the file. The file is an **inode**: the data '
                'plus its metadata, owner, permissions and timestamps. A '
                'directory entry is just a name that points at an inode. Hold '
                'that one fact and both kinds of link become obvious.\n\n'
                'A **hard link**, `ln target link`, is a second name for the '
                'same inode. The two names are completely equal; neither is the '
                '"original", the data survives until the last name is removed, '
                'and because it is a second directory entry for one inode, both '
                'names must live on the same filesystem. A **symbolic link**, '
                '`ln -s target link`, is different in kind: it is a small file '
                'whose contents are a path. It can point across filesystems and '
                'at directories, and it breaks silently if the target moves, '
                'because it only ever held the path, not the data.\n\n'
                '`readlink -f` follows a chain of symlinks to the real path at '
                'the end. And the lookup tools answer a related question: what '
                'will actually run when I type this name? `type -a python3` '
                'shows every meaning the shell has for a name, in priority '
                'order, which matters because an alias or a shell function '
                'beats anything on `PATH`. `which` only sees the PATH '
                'executables, so `type` is the more honest of the two.\n\n'
                'The next lesson is the pager: how to query a file that is '
                'longer than a screen, which is what those names usually '
                'point at once they are logs.'
            ),
            'examples': [
                {
                    'label': 'Two links, one inode idea',
                    'code': ('ln target link      hard link: another name for\n'
                             '                    the same inode, same fs\n'
                             'ln -s target link   symlink: a file holding a '
                             'path\n'
                             'readlink -f link    resolve to the real path\n'
                             'ls -li              show inode numbers and link '
                             'counts'),
                    'note': 'ls -li shows the inode number: two hard links '
                            'share it, a symlink has its own.',
                },
                {
                    'label': 'What will actually run',
                    'code': ('type -a python3    every meaning, in order\n'
                             'which python3      only the PATH executable'),
                    'note': 'type sees aliases and functions; which does not. '
                            'An alias beats PATH, so type is the honest answer.',
                },
            ],
            'misconceptions': [
                'A hard link is not a copy. It is the same inode under a second '
                'name, so an edit through either name changes the one file.',
                'A symlink breaks if the target moves or is deleted, because it '
                'only ever stored the path. A hard link does not, because it '
                'shares the data.',
                '`which` can lie about what runs, because it does not see '
                'aliases or shell functions. `type -a` is the one that tells '
                'the truth.',
            ],
            'try_it': [
                'Make a file, hard-link it, symlink it, and run `ls -li` on all '
                'three. Then delete the original and see which link still '
                'works.',
            ],
        },
        {
            'id': 'lu-less',
            'title': 'The pager, past the basics',
            'concept': (
                'Linux Basics taught `less` as the way to read a long file. It '
                'repays going deeper, because a few more keys turn a log from '
                'something you scroll into something you query.\n\n'
                'Search is the core of it, and it is vim\'s search: `/pattern` '
                'forward, `?pattern` backward, `n` and `N` to repeat. On a '
                'thousand-line log, searching for the error beats scrolling to '
                'it every time. `&pattern` goes further and hides every line '
                'that does not match, so you can filter a noisy log down to '
                'just the lines about one request.\n\n'
                '`F` is the one worth building a habit around. It follows the '
                'file as it grows, like `tail -f`, but with a difference that '
                'matters: press Ctrl-C and you stop following and can scroll '
                'back through everything you have seen, search it, then press '
                '`F` again to resume. That is strictly better than `tail -f` '
                'for a live log you also want to read. `-S` chops long lines '
                'instead of wrapping them, which makes a wide log legible, and '
                '`g` and `G` jump to the top and bottom.\n\n'
                'All of this is worth learning once because `less` is what '
                '`man` uses to display pages, so every one of these keys works '
                'in a man page too.\n\n'
                'The previous lesson treated a name as a pointer. This one is '
                'how you actually read what that pointer leads to, once the '
                'file is longer than a screen.'
            ),
            'examples': [
                {
                    'label': 'Querying a log, not scrolling it',
                    'code': ('/error     search forward     n  N   repeat\n'
                             '&warning   show only lines matching warning\n'
                             'F          follow the file as it grows\n'
                             '           (Ctrl-C to stop and scroll back)\n'
                             '-S         chop long lines instead of wrapping\n'
                             'g   G      jump to the top / the end'),
                    'note': 'The keys are vim\'s keys, and because man uses '
                            'less, they all work in a man page as well.',
                },
                {
                    'label': 'Follow, then read, then follow again',
                    'code': ('less +F /var/log/app.log\n'
                             '  new lines appear as they are written\n'
                             'Ctrl-C\n'
                             '  now you can /search and page\n'
                             'F\n'
                             '  resume following from here'),
                    'note': '`tail -f` cannot pause and search. `F` can, which '
                            'is why it is the better live log once you know '
                            'the key.',
                },
            ],
            'misconceptions': [
                '`F` is not stuck. Ctrl-C stops following and lets you scroll '
                'and search what you have seen; `F` resumes. That is why it '
                'beats `tail -f` when you also want to read.',
                'less loads only what it shows, so it opens a file too big to '
                'fit in memory instantly. That is the whole reason to use it '
                'over `cat`.',
                '`&pattern` filters the view to matching lines, which is '
                'different from `/pattern` that only jumps between them.',
            ],
            'try_it': [
                'Open a long log with `less -S`, filter it with `&` to one '
                'pattern, then open `man less` and use `/` to find the `-S` '
                'flag.',
            ],
        },
    ],

    'drills': [
        {'id': 'lu-diff-u', 'type': 'command',
         'answer': 'diff -u old.conf new.conf',
         'prompt': 'Show a unified diff between old.conf and new.conf.',
         'teach': 'Empty output means they match. -u is the form patch and '
                  'humans both read.'},
        {'id': 'lu-diff-rq', 'type': 'command',
         'answer': 'diff -rq a/ b/',
         'prompt': 'Compare two directory trees and name only the files that differ.',
         'teach': '-r walks, -q stays quiet except for names. That is how you '
                  'compare a backup to a live tree.'},
        # find and xargs
        {'id': 'lu-find-maxdepth', 'type': 'command',
         'answer': 'find src -maxdepth 1 -type f',
         'prompt': 'List files in src only, without walking subdirectories.',
         'teach': '-maxdepth 1 is this directory. Put it before -name.'},
        {'id': 'lu-find-newer', 'type': 'command',
         'answer': 'find . -type f -newer stamp',
         'prompt': 'Find files newer than a file called stamp.',
         'teach': '-newer compares mtime to another file, not a number of days.'},
        {'id': 'lu-find-name', 'type': 'command',
         'answer': 'find . -name "*.log"',
         'prompt': 'Find every .log file under the current directory.',
         'teach': 'Quote the pattern, or the shell expands it before find sees '
                  'it and you search for whatever happens to be in this '
                  'directory.'},
        {'id': 'lu-find-type', 'type': 'command',
         'answer': 'find . -type d -name build',
         'prompt': 'Find directories called build, and not files of that name.',
         'teach': '-type d is directories, f is files. Without it, find '
                  'happily returns a file named build and you act on the '
                  'wrong thing.'},
        {'id': 'lu-find-mtime', 'type': 'command',
         'answer': 'find . -mtime -7',
         'prompt': 'Find everything modified in the last seven days.',
         'teach': '-7 is "less than seven days ago", +7 is "more than". A bare '
                  '7 means exactly the seventh day, which is almost never what '
                  'you wanted.'},
        {'id': 'lu-find-size', 'type': 'command',
         'answer': 'find . -size +100M',
         'prompt': 'Find files larger than 100 megabytes.',
         'teach': 'The plus means larger than; a minus means smaller. Leave '
                  'the sign off and it means exactly that size, which matches '
                  'almost nothing.'},
        {'id': 'lu-find-exec', 'type': 'command',
         'answer': 'find . -name "*.tmp" -exec rm {} +',
         'prompt': 'Delete every .tmp file, running rm as few times as '
                   'possible.',
         'teach': '-exec ... + batches the arguments into one invocation; '
                  '-exec ... \\; runs the command once per file and is much '
                  'slower.'},
        {'id': 'lu-find-delete', 'type': 'command',
         'answer': 'find . -name "*.tmp" -delete',
         'prompt': 'Delete every .tmp file using find\'s own action rather than '
                   'calling rm.',
         'teach': 'Put -delete last. find applies predicates left to right, and '
                  '-delete before -name deletes everything.'},
        {'id': 'lu-find-print0', 'type': 'command',
         'answer': 'find . -print0 | xargs -0 rm',
         'prompt': 'Pipe filenames to xargs safely, so that names containing '
                   'spaces survive.',
         'teach': 'Filenames may contain spaces and newlines. Null separation '
                  'is the only safe way to pass them through a pipe.'},
        {'id': 'lu-find-prune', 'type': 'command',
         'answer': 'find . -name .git -prune -o -name "*.py" -print',
         'prompt': 'Find .py files while skipping the .git directory entirely.',
         'teach': '-prune stops find descending. The -o -print is required '
                  'because -prune is itself an action.'},
        {'id': 'lu-xargs-n', 'type': 'command', 'answer': 'xargs -n1 echo',
         'prompt': 'Run a command once per input item rather than batching them.',
         'teach': 'By default xargs crams as many items as fit onto one '
                  'command line. -n1 forces one call each, which is what you '
                  'want when order or failure per item matters.'},
        {'id': 'lu-xargs-i', 'type': 'command',
         'answer': 'xargs -I{} mv {} /tmp/',
         'prompt': 'Use each input item in the middle of a command rather than '
                   'at the end.',
         'teach': '-I names a placeholder and substitutes it wherever it '
                  'appears, which also switches to one item per command.'},

        # lsof
        {'id': 'lu-lsof-port', 'type': 'command', 'answer': 'lsof -i :8080',
         'prompt': 'Find out what is using port 8080.',
         'teach': 'The colon is required: -i :8080 is a port, -i@host is an '
                  "address. This is the fastest answer to 'address already in "
                  "use'."},
        {'id': 'lu-lsof-deleted', 'type': 'command', 'answer': 'lsof +L1',
         'prompt': 'Find deleted files that are still held open and still using '
                   'disk.',
         'teach': 'DFIR gold, and also the answer to df and du disagreeing.'},
        {'id': 'lu-lsof-path', 'type': 'command', 'answer': 'lsof /mnt',
         'prompt': 'Find out what is keeping a mount busy so it will not '
                   'unmount.',
         'teach': 'Given a path it lists every process holding something open '
                  "under it, which is precisely the list 'target is busy' "
                  'refuses to give you.'},
        {'id': 'lu-lsof-pid', 'type': 'command', 'answer': 'lsof -p 1234',
         'prompt': 'List every file one process has open.',
         'teach': 'Open files include sockets, libraries and the working '
                  'directory, so this doubles as a picture of what a process '
                  'is actually doing.'},

        # tar: pure flag memory, which is exactly what a drill deck is for
        {'id': 'lu-tar-create', 'type': 'command',
         'answer': 'tar -czf archive.tar.gz dir',
         'prompt': 'Create a gzipped archive of a directory.',
         'teach': 'c create, z gzip, f file. The f must come last of the three '
                  'because the filename follows it.'},
        {'id': 'lu-tar-extract', 'type': 'command',
         'answer': 'tar -xzf archive.tar.gz',
         'prompt': 'Extract a gzipped archive.',
         'teach': 'x extract. Modern tar detects the compression, so -xf '
                  'usually works too.'},
        {'id': 'lu-tar-list', 'type': 'command', 'answer': 'tar -tzf archive.tar.gz',
         'prompt': 'List what is inside an archive without extracting it.',
         'teach': 'Do this before extracting anything you did not make. An '
                  'archive can contain absolute paths and ../.'},
        {'id': 'lu-tar-into', 'type': 'command',
         'answer': 'tar -xzf archive.tar.gz -C /tmp/target',
         'prompt': 'Extract an archive into a specific directory rather than '
                   'the current one.',
         'teach': '-C changes directory before extracting. Without it an '
                  'archive built with loose paths sprays files into wherever '
                  'you happened to stand.'},
        {'id': 'lu-tar-strip', 'type': 'command',
         'answer': 'tar -xzf archive.tar.gz --strip-components=1',
         'prompt': 'Extract an archive while discarding its top-level '
                   'directory.',
         'teach': 'The fix for an archive that wraps everything in a version '
                  'directory you do not want.'},
        {'id': 'lu-gzip', 'type': 'command',
         'answer': 'gzip app.log',
         'prompt': 'Compress app.log in place, replacing it with app.log.gz.',
         'teach': 'gzip deletes the original. gzip -k keeps it.'},
        {'id': 'lu-gzip-k', 'type': 'command',
         'answer': 'gzip -k app.log',
         'prompt': 'Compress app.log and keep the original file.',
         'teach': '-k is keep. The default is to replace.'},
        {'id': 'lu-gunzip', 'type': 'command',
         'answer': 'gzip -d app.log.gz',
         'accepts': ['gunzip app.log.gz'],
         'prompt': 'Decompress app.log.gz back to app.log.',
         'teach': 'gzip -d and gunzip are the same command. They eat the .gz '
                  'unless you pass -k.'},
        {'id': 'lu-zcat', 'type': 'command',
         'answer': 'zcat app.log.gz',
         'prompt': 'Print the decompressed contents of app.log.gz to stdout.',
         'teach': 'No second file. cat app.log.gz is the compressed bytes.'},
        {'id': 'lu-zgrep', 'type': 'command',
         'answer': 'zgrep ERROR app.log.gz',
         'prompt': 'Search a compressed log for ERROR without unpacking it.',
         'teach': 'zgrep is grep through the stream. The .gz stays on disk.'},
        {'id': 'lu-gzip-l', 'type': 'command',
         'answer': 'gzip -l app.log.gz',
         'prompt': 'Show compressed size, original size, and name for app.log.gz.',
         'teach': '-l reads the header. -t tests the stream without writing it.'},

        # inspection
        {'id': 'lu-stat', 'type': 'command', 'answer': 'stat file.txt',
         'prompt': 'Show a file\'s size, permissions, inode and timestamps.',
         'teach': 'ls shows one timestamp; stat shows the rest: accessed, '
                  'modified, the inode change time that touch cannot set, '
                  'and birth where the filesystem records it.'},
        {'id': 'lu-file', 'type': 'command', 'answer': 'file mystery.bin',
         'prompt': 'Work out what a file actually is, ignoring its extension.',
         'teach': 'It reads the leading bytes, not the name. Extensions are '
                  'decoration on Linux, and this is what tells you the .jpg '
                  'is actually a script.'},
        {'id': 'lu-strings', 'type': 'command', 'answer': 'strings -n 8 binary',
         'prompt': 'Pull printable text of at least eight characters out of a '
                   'binary.',
         'teach': 'The default minimum is 4, which produces mostly noise. Eight '
                  'is usually the readable setting.'},
        {'id': 'lu-xxd', 'type': 'command', 'answer': 'xxd file.bin | head',
         'prompt': 'Look at the first few lines of a file in hexadecimal.',
         'teach': 'The right side shows printable bytes, the left the '
                  'offsets. The first few bytes are the magic number that '
                  'file used to identify it.'},
        {'id': 'lu-xxd-seek', 'type': 'command', 'answer': 'xxd -s 512 -l 64 disk.img',
         'prompt': 'Dump 64 bytes starting at offset 512.',
         'teach': '-s seek, -l length. This is how you read a specific '
                  'structure out of an image without loading the whole thing.'},

        # space and watching
        {'id': 'lu-du-sort', 'type': 'command', 'answer': 'du -sh * | sort -h',
         'prompt': 'Show what is using space in this directory, smallest first.',
         'teach': 'sort -h understands the K, M and G suffixes that -h '
                  'produces.'},
        {'id': 'lu-df-h', 'type': 'command', 'answer': 'df -h',
         'prompt': 'Show how full each filesystem is, in human units.',
         'teach': 'df is per filesystem, du is per directory. When they '
                  'disagree, a deleted file is still held open somewhere.'},
        {'id': 'lu-watch', 'type': 'command', 'answer': 'watch -n 5 df -h',
         'prompt': 'Re-run a command every five seconds and watch the output '
                   'change in place.',
         'teach': 'It clears and redraws, so change is easy to spot; -d '
                  'highlights what differed. Quote the command if it has its '
                  'own flags.'},
        {'id': 'lu-tee', 'type': 'command', 'answer': 'cmd | tee out.txt',
         'prompt': 'Send output to a file AND to your screen at the same time. '
                   'Use "cmd".',
         'teach': 'tee -a appends. The classic use is `... | sudo tee /etc/...` '
                  'because a plain > redirect happens as your user, not as '
                  'root.'},
        {'id': 'lu-tee-sudo', 'type': 'command',
         'answer': 'echo text | sudo tee /etc/config',
         'prompt': 'Write to a root-owned file from an unprivileged shell.',
         'teach': '`sudo echo x > /etc/f` fails because the redirect is done by '
                  'your shell, not by sudo. This is the fix.'},

        # links and lookups
        {'id': 'lu-ln-s', 'type': 'command', 'answer': 'ln -s target link',
         'prompt': 'Create a symbolic link.',
         'teach': 'Target first, link second, the same order as cp. A symlink '
                  "to a relative target is resolved from the link's own "
                  'directory, which is the classic broken-link cause.'},
        {'id': 'lu-ln-hard', 'type': 'command', 'answer': 'ln target link',
         'prompt': 'Create a hard link, a second name for the same data.',
         'teach': 'A hard link shares the inode, so deleting either name leaves '
                  'the data reachable through the other. It cannot cross '
                  'filesystems.'},
        {'id': 'lu-readlink', 'type': 'command', 'answer': 'readlink -f path',
         'prompt': 'Resolve a path all the way through every symlink to the '
                   'real file.',
         'teach': '-f follows every link and prints an absolute path. It is '
                  'how a script finds its own real location when invoked '
                  'through a symlink.'},
        {'id': 'lu-type-a', 'type': 'command', 'answer': 'type -a python3',
         'prompt': 'Show every python3 that would be found, including aliases '
                   'and builtins.',
         'teach': 'which only searches PATH, so it misses aliases, functions '
                  'and builtins. type asks the shell itself, and -a shows '
                  'every candidate in order.'},

        # less, which reuses vi keys
        {'id': 'lu-less-search', 'type': 'keys', 'keys': ['/'],
         'prompt': 'Search forward inside less.',
         'teach': 'less uses vi keys, which is why this module reinforces the '
                  'vim one for free. n and N move between matches.'},
        {'id': 'lu-less-follow', 'type': 'keys', 'keys': ['S-f'],
         'prompt': 'In less, follow the file as it grows, like tail -f.',
         'teach': 'Ctrl-C stops following and leaves you in the pager, which '
                  'tail -f cannot do.'},
        {'id': 'lu-less-end', 'type': 'keys', 'keys': ['S-g'],
         'prompt': 'Jump to the end of the file in less.',
         'teach': 'Same as vim: G for the end, gg for the start.'},
        {'id': 'lu-less-chop', 'type': 'command', 'answer': 'less -S file.log',
         'prompt': 'Open a file in less without wrapping long lines.',
         'teach': 'Essential for wide log lines and for anything tabular.'},
    ],

    'challenges': [
        {
            'id': 'lu-find-xargs',
            'title': 'Find and act, safely',
            'goal': 'Use find and xargs on filenames containing spaces, which '
                    'is where the naive pipeline breaks.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'logs/': None,
                'logs/one.log': 'a\n',
                'logs/two three.log': 'b\n',
                'logs/keep.txt': 'c\n',
                'archive/': None,
            }},
            'solution': {'shell': 'find logs -name "*.log" -print0 | '
                                  'xargs -0 -I{} mv {} archive/'},
            'steps': [
                {'instruction': 'Find the .log files under logs, quoting the '
                                'pattern.',
                 'hint': 'find logs -name "*.log"'},
                {'instruction': 'Pass them to xargs so a name with a space '
                                'survives.',
                 'hint': '-print0 on find, -0 on xargs'},
                {'instruction': 'Move each one into archive/.',
                 'hint': 'xargs -0 -I{} mv {} archive/'},
            ],
            'free': 'Move both .log files, including the one with a space in '
                    'its name, into archive/. Leave keep.txt alone.',
            'verify': {'kind': 'sandbox', 'expect': {
                'exists': ['archive/one.log', 'archive/two three.log',
                           'logs/keep.txt'],
                'missing': ['logs/one.log', 'logs/two three.log']}},
            'fallback': 'self',
        },
        {
            'id': 'lu-tar-roundtrip',
            'title': 'Archive, inspect, extract elsewhere',
            'goal': 'Do the whole tar loop, including listing before extracting '
                    'and stripping a wrapper directory.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'project/': None,
                'project/a.txt': 'alpha\n',
                'project/b.txt': 'bravo\n',
                'out/': None,
            }},
            'solution': {'shell': 'tar -czf project.tar.gz project && '
                                  'tar -tzf project.tar.gz > listing.txt && '
                                  'tar -xzf project.tar.gz -C out '
                                  '--strip-components=1'},
            'steps': [
                {'instruction': 'Create project.tar.gz from the project '
                                'directory.', 'hint': 'tar -czf project.tar.gz project'},
                {'instruction': 'List its contents into listing.txt without '
                                'extracting.', 'hint': 'tar -tzf ... > listing.txt'},
                {'instruction': 'Extract it into out/, discarding the top-level '
                                'project directory.',
                 'hint': 'tar -xzf ... -C out --strip-components=1'},
            ],
            'free': 'Make project.tar.gz, write its listing to listing.txt, and '
                    'extract it into out/ so that out/a.txt exists rather than '
                    'out/project/a.txt.',
            'verify': {'kind': 'sandbox', 'expect': {
                'exists': ['project.tar.gz', 'listing.txt', 'out/a.txt',
                           'out/b.txt'],
                'missing': ['out/project'],
                'file_contains': {'listing.txt': 'project/a.txt'}}},
            'fallback': 'self',
        },
        {
            'id': 'lu-gzip-log',
            'title': 'Compress a log, then read it without unpacking',
            'goal': 'gzip a single file and prove zcat reads the stream. Keep '
                    'the original so the check can see both.',
            'setup': {'kind': 'sandbox', 'shell': 'bash',
                      'tree': {'app.log': 'ERROR start\nINFO ok\nERROR end\n'}},
            'solution': {'shell': 'gzip -k app.log && zcat app.log.gz > out.txt'},
            'steps': [
                {'instruction': 'Compress app.log and keep the original.',
                 'hint': 'gzip -k app.log'},
                {'instruction': 'Write the decompressed contents to out.txt '
                                'without using gunzip.',
                 'hint': 'zcat app.log.gz > out.txt'},
            ],
            'free': 'Produce app.log.gz and out.txt, leaving app.log in place.',
            'verify': {'kind': 'sandbox', 'expect': {
                'is_file': ['app.log', 'app.log.gz', 'out.txt'],
                'file_contains': {'out.txt': ['ERROR start', 'ERROR end']}}},
            'fallback': 'self',
        },
        {
            'id': 'lu-tee-and-links',
            'title': 'tee, and both kinds of link',
            'goal': 'Capture output while still seeing it, and make the two '
                    'kinds of link so the difference is concrete.',
            'setup': {'kind': 'sandbox', 'shell': 'bash',
                      'tree': {'data.txt': 'original\n'}},
            'solution': {'shell': 'echo "captured" | tee log.txt > /dev/null; '
                                  'ln data.txt hard.txt; ln -s data.txt soft.txt'},
            'steps': [
                {'instruction': 'Write the word captured into log.txt using '
                                'tee.', 'hint': 'echo captured | tee log.txt'},
                {'instruction': 'Make a hard link to data.txt called hard.txt.',
                 'hint': 'ln data.txt hard.txt'},
                {'instruction': 'Make a symbolic link to data.txt called '
                                'soft.txt.', 'hint': 'ln -s data.txt soft.txt'},
            ],
            'free': 'Produce log.txt containing "captured" via tee, a hard link '
                    'hard.txt and a symlink soft.txt, both pointing at '
                    'data.txt.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'log.txt': 'captured'},
                'is_symlink': {'soft.txt': 'data.txt'},
                'is_file': ['hard.txt'],
                'file_equals': {'hard.txt': 'original'}}},
            'fallback': 'self',
        },
        {
            'id': 'lu-find-predicates',
            'title': 'Order the predicates so find does less work',
            'goal': 'find evaluates left to right and stops early. Use that '
                    'deliberately, and use -print0 where it matters.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'src/a.log': 'one\n',
                'src/b.txt': 'two\n',
                'src/deep/c.log': 'three\n',
                'src/deep/d.md': 'four\n',
                'src/odd name.log': 'five\n',
            }},
            'solution': {'shell':
                'find src -type f -name "*.log" > logs.txt && '
                'find src -maxdepth 1 -type f -name "*.log" > shallow.txt && '
                'find src -type f -name "*.log" -print0 | '
                'xargs -0 wc -l > counted.txt && '
                'find src -type f -newer src/a.log > newer.txt'},
            'steps': [
                {'instruction': 'Find every regular file ending in .log '
                                'anywhere under src, into logs.txt.',
                 'hint': 'find src -type f -name "*.log"'},
                {'instruction': 'Do it again limited to the top level, into '
                                'shallow.txt.',
                 'hint': '-maxdepth 1, and it goes before -name'},
                {'instruction': 'Count the lines of every match, using '
                                '-print0 and xargs -0 so the filename with a '
                                'space survives.',
                 'hint': 'find ... -print0 | xargs -0 wc -l > counted.txt'},
                {'instruction': 'Find files newer than src/a.log into '
                                'newer.txt.',
                 'hint': 'find src -type f -newer src/a.log'},
            ],
            'free': 'Produce logs.txt, shallow.txt, counted.txt built with '
                    '-print0 and xargs -0, and newer.txt.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'logs.txt': ['src/a.log', 'src/deep/c.log'],
                                  'shallow.txt': 'src/a.log',
                                  'counted.txt': 'odd name.log'},
                'file_lacks': {'shallow.txt': 'deep/c.log',
                               'logs.txt': 'b.txt'},
                'is_file': ['newer.txt']}},
            'fallback': 'self',
        },
        {
            'id': 'lu-stat-du',
            'title': 'Ask precisely how big and how old',
            'goal': 'stat, du and df answer three different size questions, '
                    'and mixing them up is why numbers disagree.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'data/small.txt': 'x\n',
                'data/notes.md': 'a longer file with rather more content\n',
            }},
            'solution': {'shell':
                'stat -c "%n %s %y" data/*.* > sizes.txt && '
                'du -sh data > dirsize.txt && '
                'du -ab data | sort -rn > bybytes.txt && '
                'df -h . > filesystem.txt'},
            'steps': [
                {'instruction': 'Write the name, byte size and modification '
                                'time of each file in data to sizes.txt.',
                 'hint': 'stat -c "%n %s %y" data/*.*'},
                {'instruction': 'Record the total size of the directory, '
                                'human readable, in dirsize.txt.',
                 'hint': 'du -sh data'},
                {'instruction': 'List every entry by apparent byte size, '
                                'largest first, in bybytes.txt.',
                 'hint': 'du -ab data | sort -rn'},
                {'instruction': 'Record the free space of the filesystem in '
                                'filesystem.txt, and note that du and df '
                                'measure different things.'},
            ],
            'free': 'Produce sizes.txt from stat, dirsize.txt and bybytes.txt '
                    'from du, and filesystem.txt from df.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'sizes.txt': ['small.txt', 'notes.md'],
                                  'dirsize.txt': 'data',
                                  'bybytes.txt': 'notes.md',
                                  'filesystem.txt': '%'}}},
            'fallback': 'self',
        },
        {
            'id': 'lu-which-type',
            'title': 'Find out what will actually run',
            'goal': 'which, type and command -v disagree, and the '
                    'disagreement is the point: an alias or a function beats '
                    'anything on PATH.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {'.keep': ''}},
            'solution': {'shell':
                'type -a ls > type-ls.txt 2>&1; '
                'command -v grep > cv-grep.txt 2>&1; '
                'greet() { echo hi; }; '
                'type greet > type-func.txt 2>&1; '
                'echo "$PATH" | tr ":" "\\n" > pathdirs.txt; true'},
            'steps': [
                {'instruction': 'Record every meaning of ls that the shell '
                                'knows, into type-ls.txt.',
                 'hint': 'type -a ls'},
                {'instruction': 'Record the resolved path of grep into '
                                'cv-grep.txt with the portable command.',
                 'hint': 'command -v grep'},
                {'instruction': 'Define a shell function and ask type about '
                                'it, into type-func.txt. Note that which '
                                'would not have found it at all.',
                 'hint': 'greet() { echo hi; }; type greet'},
                {'instruction': 'Split PATH onto one directory per line in '
                                'pathdirs.txt, and read the order.',
                 'hint': 'echo "$PATH" | tr ":" "\\n"'},
            ],
            'free': 'Produce type-ls.txt, cv-grep.txt, type-func.txt showing '
                    'a function, and pathdirs.txt with one PATH entry per '
                    'line.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'type-ls.txt': 'ls',
                                  'cv-grep.txt': 'grep',
                                  'type-func.txt': 'function',
                                  'pathdirs.txt': '/'}}},
            'fallback': 'self',
        },
        {
            'id': 'lu-inspect-bytes',
            'title': 'file, strings and xxd on the same three files',
            'goal': 'The three inspection tools, applied together, so the '
                    'division of labour between them is obvious.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'plain.txt': 'ordinary text file\n',
                'script.sh': {'content': '#!/bin/bash\necho hello\n',
                              'mode': '755'},
                'weird.dat': '\x00\x01\x02hidden marker string here'
                             '\x00\x03',
            }},
            'solution': {'shell':
                'file plain.txt script.sh weird.dat > types.txt && '
                'strings -n 6 weird.dat > found.txt && '
                'xxd -l 16 weird.dat > head.txt && '
                'head -c 2 script.sh > shebang.txt'},
            'steps': [
                {'instruction': 'Identify all three files by content into '
                                'types.txt.',
                 'hint': 'file plain.txt script.sh weird.dat'},
                {'instruction': 'Pull the readable strings of at least six '
                                'characters out of weird.dat into found.txt.',
                 'hint': 'strings -n 6 weird.dat'},
                {'instruction': 'Dump the first sixteen bytes of weird.dat as '
                                'hex into head.txt.',
                 'hint': 'xxd -l 16 weird.dat'},
                {'instruction': 'Write just the first two bytes of script.sh '
                                'to shebang.txt. Those two bytes are why it '
                                'runs.',
                 'hint': 'head -c 2 script.sh'},
            ],
            'free': 'Produce types.txt, found.txt with the embedded string, '
                    'head.txt with a hex dump, and shebang.txt holding the '
                    'first two bytes of the script.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'types.txt': ['plain.txt', 'script.sh'],
                                  'found.txt': 'hidden marker string',
                                  'head.txt': '00000000'},
                'file_equals': {'shebang.txt': '#!'}}},
            'fallback': 'self',
        },
        {
            'id': 'lu-lsof-watch',
            'title': 'The two tools you reach for when something is stuck',
            'goal': 'lsof answers who is holding this, and watch answers is '
                    'it changing. Both on your own machine, because both are '
                    'about live state.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'Find every process holding a file open under '
                                'your home directory.',
                 'hint': 'lsof +D ~ 2>/dev/null | head'},
                {'instruction': 'Find what is listening on a port you know is '
                                'in use.',
                 'hint': 'lsof -i :22'},
                {'instruction': 'Find deleted files that are still held open, '
                                'which is the classic reason a disk is full '
                                'and du disagrees.',
                 'hint': 'lsof +L1 2>/dev/null'},
                {'instruction': 'Watch a changing command every second and '
                                'have it highlight the differences.',
                 'hint': 'watch -n1 -d "ls -l /tmp | tail"'},
                {'instruction': 'Explain, in a sentence, why lsof +L1 can '
                                'find space that df says is used and du '
                                'cannot account for.'},
            ],
            'free': 'On your own machine: use lsof to find open files by '
                    'directory, by port, and deleted-but-held, and use watch '
                    'with difference highlighting.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
    ],

    'quiz': [
        {'id': 'luq-exec', 'type': 'mcq',
         'prompt': 'What is the difference between `-exec cmd {} \\;` and '
                   '`-exec cmd {} +`?',
         'answer': 'The semicolon runs cmd once per file; the plus batches them.',
         'distractors': ['The plus runs in the background.',
                         'The semicolon is for files, the plus for directories.',
                         'They are the same; the plus is newer syntax.'],
         'teach': 'On ten thousand files that is ten thousand processes versus '
                  'a handful.'},

        {'id': 'luq-print0', 'type': 'mcq',
         'prompt': 'Why does `find . | xargs rm` break?',
         'answer': 'Filenames can contain spaces and newlines, which xargs '
                   'splits on.',
         'distractors': ['xargs cannot read from a pipe.',
                         'rm refuses more than one argument.',
                         'find prints relative paths that rm cannot resolve.'],
         'teach': '-print0 and -0 use a null separator, which cannot appear in '
                  'a filename. It is the only safe way.'},

        {'id': 'luq-delete-order', 'type': 'mcq',
         'prompt': 'What does `find . -delete -name "*.tmp"` do?',
         'answer': 'Deletes everything, because predicates apply left to right.',
         'distractors': ['Deletes only the .tmp files.',
                         'Nothing; the order is invalid.',
                         'Prompts before each deletion.'],
         'teach': 'Put -delete last. This is a genuinely destructive ordering '
                  'mistake.'},

        {'id': 'luq-gzip-stream', 'type': 'mcq',
         'prompt': 'Why is tar -xzf the wrong tool for app.log.gz?',
         'answer': 'gzip compresses one stream. A .gz log is not a tar archive.',
         'distractors': [
             'gzip files cannot be read at all.',
             'tar -xzf only works on directories.',
             'app.log.gz is already extracted.',
         ],
         'teach': 'tar packs a tree. gzip shrinks one file. .tar.gz is both, in that order.'},
        {'id': 'luq-gzip-k', 'type': 'mcq',
         'prompt': 'What does gzip app.log do to app.log?',
         'answer': 'Replaces it with app.log.gz. Pass -k to keep the original.',
         'distractors': [
             'Leaves app.log and writes app.log.gz beside it.',
             'Deletes both files after printing the stream.',
             'Archives the directory that contains app.log.',
         ],
         'teach': 'The default is replace. zcat is how you read without unpacking.'},
        {'id': 'luq-tar-list', 'type': 'mcq',
         'prompt': 'Why list an archive before extracting one you did not make?',
         'answer': 'It can contain absolute paths or .. and write outside the '
                   'directory.',
         'distractors': ['Extraction is slow and listing is fast.',
                         'Listing verifies the checksum.',
                         'Extraction overwrites without asking.'],
         'teach': '`tar -tzf` costs a second. Modern tar strips leading slashes '
                  'but not every tar does.'},

        {'id': 'luq-hardlink', 'type': 'mcq',
         'prompt': 'You hard link a.txt to b.txt, then delete a.txt. What '
                   'happens to the data?',
         'answer': 'Nothing; b.txt still names it.',
         'distractors': ['It is deleted and b.txt breaks.',
                         'b.txt becomes an empty file.',
                         'b.txt is deleted too.'],
         'teach': 'Both names point at one inode. The data goes when the last '
                  'name does, which is also why a symlink behaves completely '
                  'differently here.'},

        {'id': 'luq-tee-sudo', 'type': 'mcq',
         'prompt': 'Why does `sudo echo hello > /etc/file` fail?',
         'answer': 'The shell performs the redirect as you, before sudo runs.',
         'distractors': ['echo cannot write to /etc.',
                         'sudo strips redirections for safety.',
                         '/etc is mounted read-only.'],
         'teach': '`echo hello | sudo tee /etc/file` is the fix, and it is why '
                  'tee earns its place.'},

        {'id': 'luq-lsof-deleted', 'type': 'mcq',
         'prompt': 'What does `lsof +L1` show?',
         'answer': 'Open files with no remaining name, so deleted but still '
                   'using space.',
         'distractors': ['Files opened more than once.',
                         'Files locked by another process.',
                         'Files on network filesystems.'],
         'teach': 'The answer to df and du disagreeing, and forensically '
                  'interesting for the same reason.'},

        {'id': 'luq-mtime', 'type': 'mcq',
         'prompt': 'What does `find . -mtime 7` match?',
         'answer': 'Files modified exactly seven days ago, to the day.',
         'distractors': ['Files modified in the last seven days.',
                         'Files older than seven days.',
                         'Files modified within seven hours.'],
         'teach': 'Almost never what you wanted. -7 is "less than", +7 is '
                  '"more than".'},
    ],
}
