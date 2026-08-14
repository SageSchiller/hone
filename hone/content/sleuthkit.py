"""The Sleuth Kit: reading a disk image below the filesystem.

Volatility covers memory and nothing covered disk, which is an odd shape for a
DFIR roster. This is the other half: `mmls`, `fsstat`, `fls`, `istat`, `icat`,
`blkls` and `mactime`, the command-line tools that read an image without
mounting it and without asking the operating system's opinion.

**The idea that makes the tool set learnable** is that it is not a pile of
commands, it is four layers with a naming convention. An image contains a
volume system, which contains a filesystem, which contains metadata, which
points at data units. Every tool's prefix says which layer it works at: `mm`
for media management, `fs` for the filesystem, `i` for inode metadata, `blk`
for data units. Once you see that, `blkcat` and `icat` stop being two arbitrary
names and start being the same verb at two different layers.

**Why not just mount it.** Mounting asks the kernel to interpret the
filesystem, which means you see what the filesystem wants you to see: live
files, current names, nothing that was deleted. These tools read the
structures directly, so a deleted directory entry is still an entry, and the
data it pointed at is still on the disk until something overwrites it. That
difference is the entire subject.

**Genuinely verified, which is rare for forensics content.** A FAT12 image is
small enough to build with a script in the sandbox, so the challenges run the
real tools against a real filesystem the trainer made: `fls` really does list
the deleted entry with a `*`, and `icat` really does recover its contents.
Nothing is mounted, nothing needs root, and no disk of yours is touched.
"""

#: Builds the lab image. Shipped as a script the challenge runs rather than as
#: a base64 blob, because a 256 KB image is 350 KB of base64 and because
#: watching the structures get written is itself part of the lesson.
MAKE_IMAGE = r'''#!/usr/bin/env python3
"""Write a small FAT12 image with two live files and one deleted one."""
import struct

SEC, TOT, RESV, FATSEC, ROOTENT = 512, 512, 1, 2, 64
ROOTSEC = (ROOTENT * 32) // SEC

boot = bytearray(SEC)
boot[0:3] = b'\xeb\x3c\x90'
boot[3:11] = b'HONELAB '
struct.pack_into('<H', boot, 11, SEC)      # bytes per sector
boot[13] = 1                                # sectors per cluster
struct.pack_into('<H', boot, 14, RESV)     # reserved sectors
boot[16] = 1                                # number of FATs
struct.pack_into('<H', boot, 17, ROOTENT)  # root directory entries
struct.pack_into('<H', boot, 19, TOT)      # total sectors
boot[21] = 0xF8                             # media descriptor
struct.pack_into('<H', boot, 22, FATSEC)   # sectors per FAT
struct.pack_into('<H', boot, 24, 1)
struct.pack_into('<H', boot, 26, 1)
boot[510:512] = b'\x55\xaa'                 # boot signature


def entry(name, ext, cluster, size, deleted=False):
    e = bytearray(32)
    e[0:8] = name.ljust(8).encode()
    e[8:11] = ext.ljust(3).encode()
    if deleted:
        # Deleting a FAT file replaces the first byte of its name with 0xE5
        # and frees its clusters. The name and the data are both still here.
        e[0] = 0xE5
    e[11] = 0x20
    struct.pack_into('<H', e, 26, cluster)
    struct.pack_into('<I', e, 28, size)
    return e


FILES = [
    ('NOTES', 'TXT', b'quarterly figures, nothing unusual\n', False),
    ('README', 'TXT', b'lab image built by hone\n', False),
    ('SECRET', 'TXT', b'the exfiltration plan lives here\n', True),
]

fat = bytearray(SEC * FATSEC)
fat[0], fat[1], fat[2] = 0xF8, 0xFF, 0xFF
root = bytearray(SEC * ROOTSEC)
data = bytearray()
cluster = 2
for i, (name, ext, content, deleted) in enumerate(FILES):
    root[i * 32:(i + 1) * 32] = entry(name, ext, cluster, len(content), deleted)
    if not deleted:
        off = (cluster * 3) // 2
        if cluster % 2 == 0:
            fat[off] = 0xFF
            fat[off + 1] = (fat[off + 1] & 0xF0) | 0x0F
        else:
            fat[off] = (fat[off] & 0x0F) | 0xF0
            fat[off + 1] = 0xFF
    data += content.ljust(SEC, b'\x00')
    cluster += 1

img = bytes(boot) + bytes(fat) + bytes(root) + bytes(data)
img += bytes(SEC * TOT - len(img))
with open('disk.img', 'wb') as fh:
    fh.write(img)
print('wrote disk.img')
'''

MODULE = {
    'id': 'sleuthkit',
    'title': 'The Sleuth Kit',
    'group': 'Security',
    'blurb': 'Reading a disk image by layer: partitions, filesystem, inodes, and deleted files.',
    'context': 'You are at a shell with a disk image file, which you will read and never mount.',
    'needs': ['fls', 'icat'],
    'prereqs': ['file', 'xxd'],
    'adapter': 'sandbox',
    'estimate': '3-4 hours',
    'order': 83,

    'lessons': [
        {
            'id': 'tsk-layers',
            'title': 'Four layers, and the prefix that names them',
            'next': 'tsk-volumes',
            'concept': (
                'The Sleuth Kit looks like thirty unrelated commands and is '
                'really four layers with a naming convention. Learn the '
                'convention and the tool names stop needing to be '
                'memorised.\n\n'
                'An **image** is the raw bytes of a disk. Inside it a '
                '**volume system** divides those bytes into partitions. '
                'Inside a partition a **filesystem** organises space. The '
                'filesystem holds **metadata** structures, one per file, and '
                'each of those points at the **data units** that hold the '
                'contents.\n\n'
                'Every tool is named for the layer it works at. `mm` is media '
                'management, so `mmls` lists partitions. `fs` is the '
                'filesystem, so `fsstat` describes one. `i` is inode metadata, '
                'so `istat` describes one file\'s metadata and `ils` lists '
                'them. `blk` is data units, so `blkcat` prints one block. And '
                '`fls` lists filenames, because the file name layer is what '
                'connects a name to its metadata.\n\n'
                'The suffixes repeat too. `ls` lists, `stat` describes one '
                'thing, `cat` prints contents. So `icat` prints the contents '
                'of the file at an inode, and `blkcat` prints the contents of '
                'a block. Same verb, different layer, and knowing that is most '
                'of the tool set.\n\n'
                'The point of working this way rather than mounting the image '
                'is that mounting asks the kernel for its interpretation, and '
                'the kernel shows you the filesystem as it currently claims to '
                'be. These tools read the structures themselves, which is how '
                'a deleted entry is still visible.'
            ),
            'examples': [
                {
                    'label': 'The layers, and who works at each',
                    'code': ('image        img_stat    the raw bytes\n'
                             '  volume     mmls        partitions\n'
                             '    filesystem fsstat    layout, type\n'
                             '      name     fls       names -> inodes\n'
                             '      metadata istat     one file, described\n'
                             '        data   icat      the contents'),
                    'note': 'Prefix is the layer, suffix is the verb. `ls` '
                            'lists, `stat` describes, `cat` prints.',
                },
                {
                    'label': 'Reading, never mounting',
                    'code': ('fls disk.img              no mount, no root\n'
                             'mount -o loop disk.img    a different question\n'
                             '\n'
                             'mount shows what the filesystem claims\n'
                             'fls shows what is written in it'),
                    'note': 'A mounted filesystem hides deleted entries by '
                            'definition. Reading the structures does not.',
                },
            ],
            'misconceptions': [
                'These tools do not mount anything and do not need root. They '
                'read a file, which is also why they cannot damage the '
                'evidence.',
                'A deleted file is not gone. In most filesystems deletion '
                'marks the entry and frees the space; the bytes stay until '
                'something reuses them, which is the entire basis of '
                'recovery.',
                '`fls` is not `ls`. It lists what the filesystem structures '
                'say, including entries the kernel would never show you.',
            ],
            'try_it': [
                'Run `img_stat` on any image file you have and see the tool '
                'answer at the outermost layer before anything else.',
            ],
        },
        {
            'id': 'tsk-volumes',
            'title': 'Partitions, and the offset everybody forgets',
            'next': 'tsk-files',
            'concept': (
                'A whole-disk image starts with a volume system, not a '
                'filesystem, and this is where most first attempts fail.\n\n'
                '`mmls disk.img` prints the partition table: a row per slot, '
                'with a start sector, a length and a description. The number '
                'that matters is the **start sector**, because every '
                'filesystem tool then needs to be told where its filesystem '
                'begins.\n\n'
                'That is what `-o` is for. `fsstat -o 2048 disk.img` says "the '
                'filesystem starts 2048 sectors in". Forget `-o` on a '
                'partitioned image and the tool reads the partition table as '
                'though it were a filesystem, fails to recognise it, and tells '
                'you it cannot determine the filesystem type. That error '
                'almost always means a missing offset rather than a corrupt '
                'image.\n\n'
                'An image of a single partition, which is what you get from '
                'imaging a filesystem rather than a disk, has no volume system '
                'at all. Then `mmls` is the thing that fails and you use the '
                'tools with no `-o`. Working out which kind of image you have '
                'is the first move, and `mmls` failing is a useful answer '
                'rather than a problem.\n\n'
                'Once inside, `fsstat` tells you the filesystem type, the '
                'sector and cluster size, and which sectors hold which '
                'structures. It is the orientation command.'
            ),
            'examples': [
                {
                    'label': 'Find the partition, then work inside it',
                    'code': ('mmls disk.img\n'
                             '  Slot  Start   Length   Description\n'
                             '  002   2048    204800   NTFS / exFAT\n'
                             '\n'
                             'fsstat -o 2048 disk.img\n'
                             'fls   -o 2048 disk.img'),
                    'note': 'The Start column is the number that goes after '
                            '-o, and it is in sectors, not bytes.',
                },
                {
                    'label': 'Which kind of image is this',
                    'code': ('mmls disk.img     works  -> whole disk, use -o\n'
                             'mmls disk.img     fails  -> single filesystem\n'
                             '\n'
                             '"Cannot determine file system type"\n'
                             '   usually means you forgot -o'),
                    'note': 'Both kinds are normal. The failure is information, '
                            'not a fault.',
                },
            ],
            'misconceptions': [
                'The `-o` offset is in sectors, not bytes. Passing a byte '
                'offset produces a confident, wrong answer or no answer at '
                'all.',
                '"Cannot determine file system type" on a whole-disk image is '
                'almost never corruption. It is a missing `-o`.',
                '`mmls` failing does not mean the image is broken. An image of '
                'one filesystem has no partition table to read.',
            ],
            'try_it': [
                'Run `mmls` on an image and then `fsstat` with and without the '
                'offset, so you see both the answer and the error.',
            ],
        },
        {
            'id': 'tsk-files',
            'title': 'Names, inodes, and getting a deleted file back',
            'next': 'tsk-timeline',
            'concept': (
                'Three commands do the actual work, and they chain: `fls` '
                'gives you an inode number, `istat` describes it, `icat` '
                'prints its contents.\n\n'
                '`fls` lists the name layer. Each row is a type, an inode '
                'number and a name: `r/r 3: NOTES.TXT` is a regular file at '
                'inode 3. `-r` recurses into directories, and `-d` shows '
                'deleted entries only.\n\n'
                '**A deleted entry is marked with a `*`.** In FAT you will '
                'also see its first character replaced, because deletion '
                'literally overwrites the first byte of the name with `0xE5`, '
                'so `SECRET.TXT` becomes `_ECRET.TXT`. The name is damaged and '
                'the rest of the entry, including the pointer to the data, is '
                'usually intact.\n\n'
                'That is why recovery works. `icat disk.img 5` reads whatever '
                'the metadata at inode 5 still points at and prints it. If '
                'nothing has been written to the disk since, the contents come '
                'back whole. If something has, you get whatever is there now, '
                'which is why the first rule of handling a suspect disk is to '
                'stop writing to it.\n\n'
                '`istat` is the middle step people skip and should not: it '
                'shows the size, the timestamps and the exact data units the '
                'file occupies, which is how you confirm that a recovery is '
                'plausible before trusting its contents.'
            ),
            'examples': [
                {
                    'label': 'The chain',
                    'code': ('fls disk.img\n'
                             '  r/r 3:   NOTES.TXT\n'
                             '  r/r 4:   README.TXT\n'
                             '  r/r * 5: _ECRET.TXT     <- deleted\n'
                             '\n'
                             'istat disk.img 5      size, times, blocks\n'
                             'icat  disk.img 5      the contents back'),
                    'note': 'The `*` is the deletion marker. The `_` is FAT '
                            'having overwritten the first letter with 0xE5.',
                },
                {
                    'label': 'Useful flags',
                    'code': ('fls -r disk.img       recurse into directories\n'
                             'fls -d -r disk.img    deleted entries only\n'
                             'fls -m / -r disk.img  bodyfile, for a timeline\n'
                             '\n'
                             'icat disk.img 5 > recovered.txt\n'
                             'tsk_recover -e disk.img out/   everything at once'),
                    'note': '`icat` prints to stdout, so redirect it. '
                            '`tsk_recover -e` bulk-extracts including deleted.',
                },
            ],
            'misconceptions': [
                'The `*` in `fls` output means the entry is deleted, not that '
                'the file is special or corrupt.',
                'Recovery is not guaranteed. It works because the data has not '
                'been overwritten yet, which is a race you are not running: '
                'stop writing to the disk.',
                '`icat` takes an inode number, not a filename. The number is '
                'the middle column of `fls`, which is why the two are always '
                'used together.',
            ],
            'try_it': [
                'On an image you own, run `fls -d -r` and see whether anything '
                'deleted is still listed.',
            ],
        },
        {
            'id': 'tsk-timeline',
            'title': 'A filesystem timeline in two commands',
            'concept': (
                'The question in an investigation is rarely "what is on this '
                'disk". It is "what happened, in what order", and the '
                'filesystem answers that if you ask it correctly.\n\n'
                'Every file carries timestamps, and the classic four are '
                'called **MACB**: Modified, Accessed, Changed (metadata '
                'changed), and Born (created). Different filesystems support '
                'different subsets, which is itself worth knowing.\n\n'
                'The workflow is two commands. `fls -m / -r image` writes a '
                '**bodyfile**, a pipe-separated intermediate format with one '
                'line per file carrying every timestamp. Then `mactime -b '
                'bodyfile` turns that into a chronological listing, one entry '
                'per timestamp per file, sorted by time. Add a date to limit '
                'it: `mactime -b body.txt 2026-08-13`.\n\n'
                'What you get is a narrative. A cluster of files created '
                'within the same second is an extraction. A binary whose '
                'accessed time is minutes after its created time is something '
                'that was written and then run. A file modified long after '
                'everything around it stopped changing is worth a look.\n\n'
                'The bodyfile format is deliberately dull and stable, which is '
                'why other tools emit it too. A timeline that combines '
                'filesystem times with log events is built by concatenating '
                'bodyfiles before running `mactime`, and that is the standard '
                'way to put disk activity and application activity on one '
                'clock.'
            ),
            'examples': [
                {
                    'label': 'Bodyfile, then timeline',
                    'code': ('fls -m / -r disk.img > body.txt\n'
                             'mactime -b body.txt > timeline.txt\n'
                             '\n'
                             'mactime -b body.txt 2026-08-13\n'
                             'mactime -d -b body.txt > timeline.csv'),
                    'note': '`-m /` sets the path prefix written into the '
                            'bodyfile. `-d` makes mactime emit CSV.',
                },
                {
                    'label': 'What a bodyfile line holds',
                    'code': ('0|/NOTES.TXT|3|r/rrwxrwxrwx|0|0|35|0|0|0|0\n'
                             '  ^         ^ ^            ^  ^  ^\n'
                             '  name      | mode         u  g  size\n'
                             '            inode          then a,m,c,b times'),
                    'note': 'Dull and stable on purpose, which is why other '
                            'tools emit it and timelines can be merged.',
                },
            ],
            'misconceptions': [
                'A timeline is not a list of files. It is one row per '
                'timestamp, so a single file appears several times, once for '
                'each of its MACB times.',
                'Timestamps are evidence, not truth. They can be set by any '
                'program with permission, so a suspiciously round or '
                'out-of-order time is a finding rather than a fact.',
                'Not every filesystem records all four MACB times, and the '
                'letters mean subtly different things between them. Check with '
                '`fsstat` which one you are reading.',
            ],
            'try_it': [
                'Build a bodyfile from an image and run `mactime` on it, then '
                'find the busiest single second in the output.',
            ],
        },
    ],

    'drills': [
        {'id': 'tskd-imgstat', 'type': 'command', 'answer': 'img_stat disk.img',
         'prompt': 'Describe a disk image at the outermost layer.',
         'teach': 'The image layer: format and size, before any question '
                  'about partitions or filesystems.'},
        {'id': 'tskd-mmls', 'type': 'command', 'answer': 'mmls disk.img',
         'prompt': 'List the partitions in a whole-disk image.',
         'teach': 'The Start column is what you pass to -o. It is in sectors, '
                  'and forgetting it is the commonest first mistake.'},
        {'id': 'tskd-fsstat', 'type': 'command', 'answer': 'fsstat -o 2048 disk.img',
         'prompt': 'Describe the filesystem in the partition at sector 2048.',
         'teach': 'The orientation command: type, sector and cluster size, and '
                  'which sectors hold which structures.'},
        {'id': 'tskd-fls', 'type': 'command', 'answer': 'fls disk.img',
         'prompt': 'List the files at the root of an image, by name and inode.',
         'teach': 'Type, inode, name. The inode in the middle column is what '
                  'every later command wants.'},
        {'id': 'tskd-fls-r', 'type': 'command', 'answer': 'fls -r disk.img',
         'prompt': 'List every file in an image, recursing into directories.',
         'teach': 'Without -r you see only the root directory, which on a real '
                  'image is almost never what you wanted.'},
        {'id': 'tskd-fls-deleted', 'type': 'command', 'answer': 'fls -d -r disk.img',
         'prompt': 'List only the deleted entries in an image.',
         'teach': 'Deleted entries are marked with a * in normal output; -d '
                  'shows nothing else, which is the fast first look.'},
        {'id': 'tskd-istat', 'type': 'command', 'answer': 'istat disk.img 5',
         'prompt': 'Describe the metadata of one file, given its inode.',
         'teach': 'Size, timestamps and the data units it occupies. The step '
                  'that tells you whether a recovery is plausible.'},
        {'id': 'tskd-icat', 'type': 'command', 'answer': 'icat disk.img 5',
         'prompt': 'Print the contents of the file at inode 5.',
         'teach': 'Takes an inode, never a filename, and writes to stdout, so '
                  'redirect it to keep what you recovered.'},
        {'id': 'tskd-blkcat', 'type': 'command', 'answer': 'blkcat disk.img 100',
         'prompt': 'Print the contents of one data unit by its number.',
         'teach': 'Same verb as icat, one layer down: blocks rather than '
                  'files, for when no metadata points at the data.'},
        {'id': 'tskd-blkls', 'type': 'command', 'answer': 'blkls disk.img > unalloc.raw',
         'prompt': 'Extract only the unallocated space from an image.',
         'teach': 'What is left when every live file is removed, which is '
                  'where carving with a tool like binwalk starts.'},
        {'id': 'tskd-bodyfile', 'type': 'command', 'answer': 'fls -m / -r disk.img > body.txt',
         'prompt': 'Write a bodyfile of every file, for timelining.',
         'teach': '-m sets the path prefix and switches the output to the '
                  'pipe-separated bodyfile format mactime expects.'},
        {'id': 'tskd-mactime', 'type': 'command', 'answer': 'mactime -b body.txt',
         'prompt': 'Turn a bodyfile into a chronological timeline.',
         'teach': 'One row per timestamp per file, sorted by time. Add a date '
                  'argument to limit it to one day.'},
        {'id': 'tskd-recover', 'type': 'command', 'answer': 'tsk_recover -e disk.img out/',
         'prompt': 'Bulk-extract every file from an image, deleted included.',
         'teach': '-e means everything, allocated and not. Without it you get '
                  'only the live files.'},
    ],

    'challenges': [
        {
            'id': 'tskc-orient',
            'title': 'Orient yourself in an image',
            'goal': 'Build the lab image, then answer the first two questions '
                    'about any image: what filesystem is this, and what is in '
                    'it.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'make-image.py': {'content': MAKE_IMAGE, 'mode': '755'},
            }},
            'solution': {'shell':
                'python3 make-image.py && '
                'fsstat disk.img > fs.txt 2>&1 && '
                'fls disk.img > files.txt 2>&1'},
            'steps': [
                {'instruction': 'Run make-image.py to write disk.img. Read it '
                                'first if you like: it writes a FAT12 '
                                'filesystem by hand.',
                 'hint': 'python3 make-image.py'},
                {'instruction': 'Describe the filesystem into fs.txt. Note that '
                                'no -o offset is needed, because this image is '
                                'one filesystem rather than a whole disk.',
                 'hint': 'fsstat disk.img > fs.txt'},
                {'instruction': 'List the files into files.txt, and read the '
                                'middle column: those inode numbers are what '
                                'every other command wants.',
                 'hint': 'fls disk.img > files.txt'},
            ],
            'free': 'Produce disk.img, fs.txt describing the filesystem, and '
                    'files.txt listing its entries.',
            'verify': {'kind': 'sandbox', 'expect': {
                'is_file': ['disk.img'],
                'file_contains': {'fs.txt': 'FAT12',
                                  'files.txt': ['NOTES.TXT', 'README.TXT']}}},
            'fallback': 'self',
        },
        {
            'id': 'tskc-deleted',
            'title': 'Recover a file that was deleted',
            'goal': 'The point of the whole tool set: find the entry the '
                    'kernel would never show you, and get its contents back.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'make-image.py': {'content': MAKE_IMAGE, 'mode': '755'},
            }},
            'solution': {'shell':
                'python3 make-image.py && '
                'fls -d -r disk.img > deleted.txt 2>&1 && '
                'inode=$(fls -r disk.img | awk \'/\\*/ {print $(NF-1)}\' '
                '| tr -d ":" | head -1) && '
                'istat disk.img "$inode" > meta.txt 2>&1; '
                'icat disk.img "$inode" > recovered.txt 2>&1; true'},
            'steps': [
                {'instruction': 'Build the image, then list only the deleted '
                                'entries into deleted.txt.',
                 'hint': 'python3 make-image.py && fls -d -r disk.img > '
                         'deleted.txt'},
                {'instruction': 'Look at the name. FAT overwrote its first '
                                'character with 0xE5 when it was deleted, '
                                'which is why it reads _ECRET.TXT.'},
                {'instruction': 'Take its inode number and describe the '
                                'metadata into meta.txt, to check the size and '
                                'blocks still look sane.',
                 'hint': 'istat disk.img INODE > meta.txt'},
                {'instruction': 'Recover the contents into recovered.txt. The '
                                'data was never erased, only unlinked.',
                 'hint': 'icat disk.img INODE > recovered.txt'},
            ],
            'free': 'Produce deleted.txt listing the deleted entry, meta.txt '
                    'describing its metadata, and recovered.txt holding the '
                    'contents of the deleted file.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'deleted.txt': 'ECRET.TXT',
                                  'recovered.txt': 'exfiltration plan'},
                'is_file': ['meta.txt']}},
            'fallback': 'self',
        },
        {
            'id': 'tskc-timeline',
            'title': 'Build a filesystem timeline',
            'goal': 'Turn the image into a chronology, which is the form an '
                    'investigation actually needs.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'make-image.py': {'content': MAKE_IMAGE, 'mode': '755'},
            }},
            'solution': {'shell':
                'python3 make-image.py && '
                'fls -m / -r disk.img > body.txt 2>&1 && '
                'mactime -b body.txt > timeline.txt 2>&1; '
                'wc -l < body.txt > count.txt; true'},
            'steps': [
                {'instruction': 'Build the image and write a bodyfile of every '
                                'file, with / as the path prefix.',
                 'hint': 'fls -m / -r disk.img > body.txt'},
                {'instruction': 'Look at one line of body.txt and find the '
                                'inode and the size among the pipe-separated '
                                'fields.'},
                {'instruction': 'Turn the bodyfile into a timeline.',
                 'hint': 'mactime -b body.txt > timeline.txt'},
                {'instruction': 'Record how many entries the bodyfile held in '
                                'count.txt.',
                 'hint': 'wc -l < body.txt > count.txt'},
            ],
            'free': 'Produce body.txt in bodyfile format, timeline.txt from '
                    'mactime, and count.txt holding the number of bodyfile '
                    'lines.',
            'verify': {'kind': 'sandbox', 'expect': {
                'is_file': ['body.txt', 'timeline.txt', 'count.txt'],
                'file_contains': {'body.txt': ['NOTES.TXT', '|']}}},
            'fallback': 'self',
        },
        {
            'id': 'tskc-real-image',
            'title': 'Read an image you made yourself',
            'goal': 'The lab image is one filesystem with no partition table. '
                    'A real disk has both, so the trainer cannot stand in for '
                    'it.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'Image something small you own and do not mind '
                                'reading, such as a USB stick, with dd or '
                                'ddrescue. Never work on the original.',
                 'hint': 'sudo dd if=/dev/sdX of=usb.img bs=4M status=progress'},
                {'instruction': 'Run mmls on it and find the start sector of '
                                'the partition you care about.'},
                {'instruction': 'Use that number with -o for fsstat and fls, '
                                'and notice the error you get if you leave it '
                                'off.',
                 'hint': 'fls -o START usb.img'},
                {'instruction': 'Build a bodyfile and a timeline of the whole '
                                'thing, then find the busiest single second.'},
            ],
            'free': 'On an image of your own: find the partition offset with '
                    'mmls, list files with fls -o, and build a mactime '
                    'timeline of it.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
    ],

    'quiz': [
        {'id': 'tskq-prefix', 'type': 'mcq',
         'prompt': 'What does the prefix of a Sleuth Kit tool name tell you?',
         'answer': 'Which layer it works at: mm volume, fs filesystem, i '
                   'metadata, blk data units.',
         'distractors': ['Which filesystem type it supports.',
                         'Whether it needs root.',
                         'Whether it writes to the image or only reads.'],
         'teach': 'Prefix is the layer and suffix is the verb, so icat and '
                  'blkcat are the same action one layer apart.'},
        {'id': 'tskq-offset', 'type': 'mcq',
         'prompt': 'fsstat on a whole-disk image says it cannot determine the '
                   'filesystem type. Most likely cause?',
         'answer': 'You did not pass -o with the partition start sector, so it '
                   'read the partition table as a filesystem.',
         'distractors': ['The image is corrupt.',
                         'The filesystem is encrypted.',
                         'fsstat needs root for whole-disk images.'],
         'teach': 'Run mmls first, take the Start column, pass it to -o. The '
                  'offset is in sectors, not bytes.'},
        {'id': 'tskq-star', 'type': 'mcq',
         'prompt': 'In fls output, what does a * before the inode number mean?',
         'answer': 'The entry is deleted.',
         'distractors': ['The file is a symbolic link.',
                         'The metadata is corrupt.',
                         'The file is larger than one data unit.'],
         'teach': 'Deleted entries are still in the structures, which is why '
                  'fls can show them and a mounted filesystem cannot.'},
        {'id': 'tskq-icat', 'type': 'mcq',
         'prompt': 'What does icat take as its argument?',
         'answer': 'An inode number, which you read from the middle column of '
                   'fls.',
         'distractors': ['A filename.',
                         'A byte offset into the image.',
                         'A partition number.'],
         'teach': 'That is why fls and icat are always used together: one '
                  'produces the number the other consumes.'},
        {'id': 'tskq-why-recover', 'type': 'mcq',
         'prompt': 'Why is recovering a deleted file possible at all?',
         'answer': 'Deletion marks the entry and frees the space; the data '
                   'stays until something overwrites it.',
         'distractors': ['The filesystem keeps a hidden backup copy.',
                         'The data is moved to a recycle area.',
                         'The tools reconstruct the contents from the '
                         'journal.'],
         'teach': 'Which is why the first rule with a suspect disk is to stop '
                  'writing to it: you are racing whatever reuses the space.'},
        {'id': 'tskq-mount', 'type': 'mcq',
         'prompt': 'Why read an image with these tools instead of mounting it?',
         'answer': 'Mounting shows the filesystem as it currently claims to '
                   'be, so deleted entries are invisible.',
         'distractors': ['Mounting is slower on large images.',
                         'These tools support more filesystems than the '
                         'kernel.',
                         'Mounting requires converting the image first.'],
         'teach': 'Reading the structures directly is also non-destructive and '
                  'needs no root, which matters when the image is evidence.'},
        {'id': 'tskq-bodyfile', 'type': 'mcq',
         'prompt': 'What is a bodyfile?',
         'answer': 'A stable intermediate format, one line per file with its '
                   'timestamps, that mactime turns into a timeline.',
         'distractors': ['A copy of every deleted file in the image.',
                         'The raw contents of the unallocated space.',
                         'A list of the data units each file occupies.'],
         'teach': 'Deliberately dull so other tools emit it too, which is how '
                  'disk and application activity end up on one clock.'},
        {'id': 'tskq-macb', 'type': 'mcq',
         'prompt': 'A single file appears four times in a mactime timeline. '
                   'Why?',
         'answer': 'A timeline has one row per timestamp, and the file has '
                   'several MACB times.',
         'distractors': ['It was modified four times.',
                         'The timeline lists each data unit separately.',
                         'It exists in four directories as hard links.'],
         'teach': 'Modified, Accessed, Changed and Born. Which of the four a '
                  'filesystem records varies, so check with fsstat.'},
    ],
}
