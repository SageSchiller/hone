"""Volatility: reading a machine's memory after the fact.

The plan deferred memory forensics as too heavy for v1 and said to revisit it
if it became a focus. Under the boundary rule it earns a module easily, because
the mental model is genuinely unlike anything else in the roster: **a memory
image is a snapshot of kernel and process structures, and every plugin is a
different way of walking them.** Disk forensics reads files somebody wrote.
Memory forensics reads the data structures the operating system was using at
one instant, which is why it can recover things that were never written down
anywhere: unpacked code, network connections, injected regions, clipboard
contents, and processes deliberately hidden from the process list.

The single most instructive idea here is **list walking versus scanning**, and
`pslist` against `psscan` is the canonical demonstration. One follows the
kernel's own linked list of processes; the other sweeps memory for anything
that looks like a process structure. When they disagree, the disagreement is
the finding. That is a genuinely new way of thinking for most people, and it
generalises to nearly every plugin family.

**Verification: none, and this module says so plainly.** Volatility 3 is a
Python project rather than a package, it needs symbol tables for the kernel of
the machine the image came from, and a memory image is gigabytes. There is no
honest offline lab a trainer can build here, so every challenge is self-marked
per D8, and each one is written around a public sample image you download once.

**Scope.** How the tool works and how to read what it says. Not incident
response procedure, and not malware analysis, both of which are different
subjects.
"""

MODULE = {
    'id': 'vol',
    'title': 'Volatility',
    'group': 'Security',
    'blurb': 'Memory images, symbol tables, plugin families, and pslist versus psscan.',
    'context': 'You are analysing a memory image on your own machine, with volatility3 installed.',
    'needs': ['vol'],
    'prereqs': ['file', 'python'],
    'adapter': None,
    'estimate': '4-5 hours',
    'order': 93,

    'lessons': [
        {
            'id': 'vo-model',
            'title': 'What a memory image actually is',
            'concept':
                'Volatility is how you parse a memory image for kernel '
                'structures, processes, and data that never hit disk. That '
                'is why malware that only ran in RAM, an unpacked payload, '
                'and a closed connection are recoverable here and nowhere '
                'else.\n\n'
                'A memory image contains the raw contents of memory: '
                'kernel structures, process address spaces, cached file '
                'contents, network state, and a great deal of data that was '
                'never written to disk and never would be.\n\n'
                'That last part is the whole reason for the discipline. '
                'Malware that only ever ran in memory leaves nothing on disk '
                'to find. A packed executable is unreadable on disk and '
                'unpacked in memory, because it had to be. Encryption keys, '
                'decrypted configuration, the command line of a process that '
                'exited, and a network connection that closed all exist here '
                'and nowhere else.\n\n'
                'To read any of it, the tool has to know the layout of the '
                'kernel structures for the exact operating system build the '
                'image came from. Volatility 2 called this a **profile** and '
                'shipped a fixed list. Volatility 3 uses **symbol tables**, '
                'downloads or generates them, and identifies the image '
                'automatically most of the time. This is the single biggest '
                'difference between the two versions and the reason most old '
                'write-ups do not apply verbatim.\n\n'
                'Everything after that is plugins. A plugin knows the shape of '
                'one kind of structure and how to walk it, and the plugin '
                'names are consistent: `windows.pslist`, `linux.pslist`, '
                '`windows.netscan`. The operating system is the first path '
                'element and it is not optional.\n\n'
                'A plugin walks a structure. The next lesson is symbol '
                'tables, without which nothing knows where a field '
                'lives.',
            'examples': [
                {'label': 'The shape of every command',
                 'code': 'vol -f memory.raw windows.info',
                 'note': '-f the image, then the plugin. windows.info first, '
                         'always: it tells you what the image is.'},
                {'label': 'What plugins exist',
                 'code': 'vol -h | grep windows',
                 'note': 'The list is long and the naming is regular, so '
                         'grepping it is how you find things.'},
                {'label': 'Volatility 2 syntax, for reading old write-ups',
                 'code': 'vol.py -f memory.raw --profile=Win7SP1x64 pslist',
                 'note': 'The --profile flag is version 2. Version 3 works it '
                         'out and the plugin names gained a prefix.'},
            ],
            'misconceptions': [
                'A memory image is not a disk image. There are no files in '
                'it, only the structures and buffers that were in RAM.',
                'Volatility 3 does not use profiles. Old commands with '
                '--profile are version 2 and will not run.',
                'The operating system prefix on a plugin name is required. '
                'pslist alone is not a valid volatility 3 plugin.',
            ],
            'try_it': [
                'Run windows.info on a sample image and read every field it '
                'prints.',
                'Grep the plugin list for a keyword and count how many '
                'plugins mention it.',
            ],
            'next': 'vo-symbols',
        },
        {
            'id': 'vo-symbols',
            'title': 'Symbol tables, and why nothing works without them',
            'concept':
                'A symbol table is how Volatility finds a field inside a '
                'kernel structure. That is why Windows usually downloads the '
                'matching table, and why a Linux image without debug symbols '
                'may be unanalysable.\n\n'
                'Those offsets differ between operating '
                'system versions, service packs, and in the Linux case '
                'between individual kernel builds. Symbol tables carry that '
                'information.\n\n'
                '**For Windows**, this is mostly automatic. Volatility 3 '
                'reads the kernel debug information from the image, works out '
                'the exact build, and downloads the matching symbols from '
                'Microsoft\'s symbol server, caching them locally. When it '
                'fails it is usually a network problem or an unusual build, '
                'and the error names the GUID it wanted.\n\n'
                '**For Linux and macOS it is the hard part**, and this is '
                'what stops most people. There is no public symbol server, '
                'because a kernel build is specific to a distribution and '
                'often to a machine. You generate the symbol table yourself, '
                'from the debug symbols of the exact kernel the image came '
                'from, using `dwarf2json`. If you do not have those debug '
                'symbols, you may simply be unable to analyse the image, and '
                'that is a real outcome rather than a mistake you made.\n\n'
                'The practical consequence is a habit: **when you capture a '
                'Linux memory image, capture the kernel debug information at '
                'the same time.** After the fact is far harder, and after the '
                'machine is rebuilt it may be impossible.\n\n'
                'Symbol tables live in the volatility symbols directory as '
                'JSON, often compressed, and `isfinfo` lists what is '
                'available.',
            'examples': [
                {'label': 'Confirm it identified the image',
                 'code': 'vol -f memory.raw windows.info',
                 'note': 'Kernel base, build, and the symbol table it chose. '
                         'If this fails, nothing else will work.'},
                {'label': 'What symbol tables do I have',
                 'code': 'vol isfinfo',
                 'note': 'Lists the tables volatility knows about locally.'},
                {'label': 'Point it at your own symbols',
                 'code': 'vol -s ./symbols -f memory.raw linux.pslist',
                 'note': '-s names a symbol directory, which is how a '
                         'generated Linux table gets used.'},
                {'label': 'Generate a Linux table from debug symbols',
                 'code': 'dwarf2json linux --elf /usr/lib/debug/vmlinux '
                         '> symbols/mykernel.json',
                 'note': 'The exact kernel the image came from. A close '
                         'version is not close enough.'},
            ],
            'misconceptions': [
                'A symbol table from a similar kernel version does not work. '
                'The offsets are build specific.',
                'Windows symbol download failing is usually network or '
                'proxy, not a corrupt image.',
                'Capturing a Linux image without the kernel debug symbols may '
                'make it unanalysable, and that is not recoverable later.',
            ],
            'try_it': [
                'Run windows.info on a sample image and note which symbol '
                'table it selected.',
                'Look at your local symbols directory and see what is cached '
                'there.',
            ],
            'next': 'vo-processes',
        },
        {
            'id': 'vo-processes',
            'title': 'pslist against psscan: the idea worth the module',
            'concept':
                'Two plugins answer "what processes were running" and they '
                'answer it by completely different means. Understanding why '
                'they disagree is the central skill here.\n\n'
                '**pslist walks the list.** The kernel keeps a doubly linked '
                'list of process structures, and pslist follows it from the '
                'head, exactly as the operating system does. It is fast, it '
                'is accurate about what the kernel believes, and it can be '
                'lied to: unlinking a process structure from that list hides '
                'it from pslist and from Task Manager alike, while the '
                'process keeps running because the scheduler uses a different '
                'structure.\n\n'
                '**psscan scans.** It sweeps the whole image looking for '
                'anything with the byte signature of a process structure, '
                'ignoring the list entirely. So it finds unlinked processes, '
                'and it also finds **exited** processes whose structures have '
                'not yet been overwritten, which is a bonus rather than a '
                'false positive.\n\n'
                'Therefore: **run both and diff them.** A process in psscan '
                'and not in pslist is either exited or deliberately hidden, '
                'and telling those apart is the next question. This is the '
                'general pattern for the whole tool, and other plugin pairs '
                'work the same way.\n\n'
                '`pstree` shows the parent and child relationships, which is '
                'where anomalies are most visible: the wrong parent for a '
                'well known process is a stronger signal than any process '
                'name. And `psinfo` style detail, plus `cmdline`, gives you '
                'the arguments, which are usually the interesting part.\n\n'
                'List versus scan is the pattern, not just the process '
                'question. The next lesson is the plugin families, each '
                'of which has that pair.',
            'examples': [
                {'label': 'The kernel\'s own answer',
                 'code': 'vol -f mem.raw windows.pslist',
                 'note': 'Follows the linked list. Fast, and exactly as '
                         'lie-able as the list itself.'},
                {'label': 'The independent answer',
                 'code': 'vol -f mem.raw windows.psscan',
                 'note': 'Sweeps for structures. Finds unlinked and exited '
                         'processes that pslist cannot see.'},
                {'label': 'The comparison, which is the actual technique',
                 'code': 'vol -f mem.raw windows.pslist > list.txt\n'
                         'vol -f mem.raw windows.psscan > scan.txt\n'
                         'diff <(awk "{print \\$2}" list.txt | sort) '
                         '<(awk "{print \\$2}" scan.txt | sort)',
                 'note': 'The difference is the finding. Everything else here '
                         'is reading it.'},
                {'label': 'Relationships, where anomalies show',
                 'code': 'vol -f mem.raw windows.pstree',
                 'note': 'A wrong parent for a well known process is a much '
                         'stronger signal than a suspicious name.'},
                {'label': 'What was it told to do',
                 'code': 'vol -f mem.raw windows.cmdline',
                 'note': 'Arguments are usually the interesting part, and '
                         'they survive in memory after the process exits.'},
            ],
            'misconceptions': [
                'psscan finding more processes than pslist is normal. Exited '
                'processes linger, and that is useful rather than an error.',
                'A hidden process is not hidden from the scheduler. It is '
                'unlinked from a list the reporting tools read.',
                'A suspicious process name is weak evidence. An ordinary name '
                'with an impossible parent is strong evidence.',
            ],
            'try_it': [
                'Run pslist and psscan on the same image and diff the process '
                'ID columns.',
                'Look at a pstree and find any process whose parent does not '
                'make sense.',
            ],
            'next': 'vo-families',
        },
        {
            'id': 'vo-families',
            'title': 'The plugin families, and what each answers',
            'concept':
                'The plugin families are how you guess the right name '
                'without searching hundreds of plugins. That is why '
                'processes, memory, files, network, registry and kernel are '
                'the groups, and why malfind is the highest-yield one.\n\n'
                '**Processes.** pslist, psscan, pstree, cmdline, '
                'privileges, getsids. Who was running, related how, with what '
                'arguments and what rights.\n\n'
                '**Memory of a process.** memmap and memdump write out a '
                'process address space; vadinfo lists its memory regions and '
                'their permissions; malfind finds regions that are executable '
                'and private and have no backing file, which is the classic '
                'shape of injected code. malfind is the single highest yield '
                'plugin in the tool.\n\n'
                '**Files.** filescan finds file objects in memory, dumpfiles '
                'extracts their cached contents. This recovers files that '
                'were deleted from disk but still cached.\n\n'
                '**Network.** netscan and netstat recover sockets and '
                'connections, including ones that had already closed.\n\n'
                '**Registry, on Windows.** hivelist, printkey, hashdump. The '
                'registry is largely in memory and readable, including hives '
                'that are locked on disk.\n\n'
                '**Kernel.** modules and modscan for drivers, with the same '
                'list-versus-scan distinction, ssdt and callbacks for hooks.\n\n'
                '**Everything else.** windows.dlllist, handles, consoles, '
                'and the timeline plugins that put events in order.\n\n'
                'The Linux equivalents follow the same names with a linux '
                'prefix, and the coverage is thinner because the structures '
                'vary more.',
            'examples': [
                {'label': 'The highest yield single plugin',
                 'code': 'vol -f mem.raw windows.malfind',
                 'note': 'Executable, private, no backing file. That is what '
                         'injected code looks like from the kernel side.'},
                {'label': 'Connections, including closed ones',
                 'code': 'vol -f mem.raw windows.netscan',
                 'note': 'Sockets recovered from structures, so it sees what '
                         'netstat on the live box would have missed.'},
                {'label': 'Get a process out for other tools',
                 'code': 'vol -f mem.raw -o ./out windows.memmap --pid 1234 '
                         '--dump',
                 'note': '-o is the output directory. The dump then goes to '
                         'strings, yara, or a disassembler.'},
                {'label': 'Read the registry from memory',
                 'code': 'vol -f mem.raw windows.printkey --key '
                         '"Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Run"',
                 'note': 'Persistence, read from RAM, including hives that '
                         'are locked on disk.'},
                {'label': 'Files that were cached in memory',
                 'code': 'vol -f mem.raw windows.filescan | grep -i '
                         'suspicious',
                 'note': 'Then dumpfiles by offset. This recovers files '
                         'deleted from disk but still cached.'},
            ],
            'misconceptions': [
                'malfind results are not automatically malicious. Legitimate '
                'JIT compilers produce the same shape.',
                'dumpfiles recovers what was in the cache, which may be a '
                'partial file rather than the whole thing.',
                'netscan showing a closed connection is not stale data. It is '
                'evidence of a connection that existed.',
            ],
            'try_it': [
                'Run malfind on a sample image and read the disassembly it '
                'prints for each hit.',
                'Use netscan on an image and list every remote address, then '
                'ask which process owned each.',
            ],
            'next': 'vo-workflow',
        },
        {
            'id': 'vo-workflow',
            'title': 'An order of questions that works',
            'concept':
                'A memory image is large and the plugin list is long, so '
                'having a default order matters more here than in most '
                'tools.\n\n'
                '**Confirm the image.** windows.info or banners.Banners. If '
                'volatility cannot identify it, stop and fix that first: '
                'everything downstream will be wrong or absent.\n\n'
                '**Establish the process picture.** pslist, psscan, pstree, '
                'and diff the first two. Read the tree for impossible '
                'parents. This is where most investigations turn.\n\n'
                '**Get the command lines.** cmdline for everything. '
                'Arguments say more than names, and they are frequently the '
                'entire finding.\n\n'
                '**Look for injection.** malfind, and read what it prints '
                'rather than counting it.\n\n'
                '**Establish the network picture.** netscan, and tie each '
                'connection to a process from the earlier list.\n\n'
                '**Then go specific.** Registry keys, files, handles, '
                'drivers, according to what the first five raised.\n\n'
                'Two habits throughout. **Save every plugin\'s output to a '
                'file** named after the plugin, because you will want to '
                'compare and because rerunning a plugin on a large image is '
                'slow. And **write down the question each command was '
                'answering**, because a directory of forty output files with '
                'no notes is not an investigation.\n\n'
                'Volatility is also slow on large images. Running plugins in '
                'a loop and going away is a better use of time than watching '
                'one at a time.',
            'examples': [
                {'label': 'Save everything, named by plugin',
                 'code': 'for p in windows.info windows.pslist windows.psscan '
                         'windows.pstree windows.cmdline windows.netscan; do\n'
                         '  vol -f mem.raw $p > "out/${p}.txt" 2>&1\n'
                         'done',
                 'note': 'Start this and go and do something else. Rerunning '
                         'on a large image is slow.'},
                {'label': 'The diff that starts the investigation',
                 'code': 'comm -13 <(awk \'NR>2{print $1}\' out/windows.pslist.txt '
                         '| sort -u) <(awk \'NR>2{print $1}\' '
                         'out/windows.psscan.txt | sort -u)',
                 'note': 'Processes psscan saw and pslist did not. Exited, or '
                         'hidden.'},
                {'label': 'Machine readable output',
                 'code': 'vol -r json -f mem.raw windows.pslist > pslist.json',
                 'note': '-r json, and then jq. The same argument as keeping '
                         'nmap XML.'},
                {'label': 'Keep the notes with the output',
                 'code': 'echo "psscan vs pslist: pid 3120 only in psscan" '
                         '>> out/NOTES.md',
                 'note': 'Forty output files with no notes is not an '
                         'investigation.'},
            ],
            'misconceptions': [
                'Running every plugin is not a strategy. Six in order answer '
                'most of the question.',
                'Volatility being slow is not a misconfiguration on a large '
                'image. Plan around it.',
                'JSON output is not only for scripts. It is much easier to '
                'filter than the table format.',
            ],
            'try_it': [
                'Write a loop that runs six plugins into named files and time '
                'the whole thing.',
                'Produce JSON output for one plugin and query it with jq.',
            ],
            'next': 'vo-capture',
        },
        {
            'id': 'vo-capture',
            'title': 'Getting an image in the first place',
            'concept':
                'Analysis presumes an image, and capture has its own rules '
                'that are easy to get wrong once and impossible to fix '
                'afterwards.\n\n'
                'The central constraint is that **capturing memory changes '
                'memory.** Your capture tool loads, allocates, and runs, and '
                'that is unavoidable. It is accepted, it is documented, and '
                'it is the reason you use the smallest reasonable tool and '
                'write the image to external storage rather than to the '
                'machine\'s own disk.\n\n'
                '**Order of volatility** is the general principle: capture '
                'the most perishable evidence first. Memory before disk, '
                'because memory is gone at power off and the disk is not.\n\n'
                'The tools: on Windows, WinPmem and DumpIt are the common '
                'ones and both produce a raw or AFF4 image. On Linux, AVML '
                'from Microsoft works without building a kernel module, which '
                'is a considerable advantage over LiME, though LiME remains '
                'standard and can produce a compatible format. On a virtual '
                'machine, **the best capture is a hypervisor snapshot**: '
                'pausing the VM and taking the memory file perturbs nothing '
                'at all, and a VMware .vmem or a virsh dump is directly '
                'analysable.\n\n'
                'Hash the image as soon as it is written, record the time, '
                'the tool and its version, and keep those notes with it. And '
                'for Linux, capture the kernel debug symbols at the same '
                'time, for the reason the symbols lesson gives.\n\n'
                'Image formats: raw is a flat copy and is what everything '
                'reads. Crash dumps, hibernation files and AFF4 all carry '
                'memory too, and volatility handles the common ones.',
            'examples': [
                {'label': 'The perturbation-free capture, on a VM',
                 'code': 'virsh dump --memory-only --live vmname mem.raw',
                 'note': 'Nothing runs inside the guest, so nothing is '
                         'disturbed. Always prefer this where it is '
                         'available.'},
                {'label': 'Linux, without building a module',
                 'code': 'sudo ./avml /media/external/mem.lime',
                 'note': 'To external storage, never to the machine\'s own '
                         'disk.'},
                {'label': 'Windows',
                 'code': 'winpmem.exe -o E:\\mem.raw',
                 'note': 'Small, well understood, and writes to the drive you '
                         'name.'},
                {'label': 'Hash it immediately and write it down',
                 'code': 'sha256sum mem.raw | tee mem.raw.sha256',
                 'note': 'With the time, the tool and its version, kept '
                         'alongside the image.'},
                {'label': 'Do not forget the symbols, on Linux',
                 'code': 'cp /usr/lib/debug/boot/vmlinux-$(uname -r) '
                         '/media/external/',
                 'note': 'Without this the image may be unanalysable, and '
                         'after a rebuild it is gone.'},
            ],
            'misconceptions': [
                'Capturing memory does not leave memory untouched. It cannot, '
                'and that is accepted rather than hidden.',
                'Writing the image to the machine\'s own disk overwrites '
                'unallocated space that may itself be evidence.',
                'A hibernation file or crash dump is not useless. Both '
                'contain memory and volatility can read the common formats.',
            ],
            'try_it': [
                'Snapshot a virtual machine you own and analyse its memory '
                'file directly.',
                'Capture memory from a Linux VM with AVML and note how long '
                'it takes and how large the file is.',
            ],
            'next': 'vo-limits',
        },
        {
            'id': 'vo-limits',
            'title': 'What memory forensics cannot tell you',
            'concept':
                'The limits are as worth knowing as the capabilities, and '
                'they are less often taught.\n\n'
                '**It is one instant.** A memory image is a photograph. It '
                'shows what was in RAM at capture time and says nothing '
                'reliable about what happened an hour earlier. Anything '
                'overwritten since is simply gone.\n\n'
                '**It is not consistent.** The capture takes time, during '
                'which the machine keeps running, so different parts of the '
                'image are from different moments. Structures can be caught '
                'mid-update, and a plugin failing on one structure while '
                'succeeding on others is normal rather than a sign of '
                'tampering.\n\n'
                '**Absence proves very little.** Memory is reused constantly, '
                'so a process that exited an hour ago is probably gone from '
                'the image entirely. Not finding something is nearly always '
                'weaker evidence than finding it.\n\n'
                '**Anti-forensics exists.** Direct kernel object manipulation '
                'is exactly what psscan exists to counter, and there are '
                'techniques aimed at the analysis tools themselves.\n\n'
                '**Symbols may not be obtainable**, particularly on Linux, '
                'and then the image may be unreadable regardless of skill.\n\n'
                'None of that makes it less valuable. It makes it one source '
                'among several: memory says what was running, disk says what '
                'was stored, logs say what was recorded, and network capture '
                'says what was sent. The investigations that go wrong are the '
                'ones that treat any single source as complete.',
            'examples': [
                {'label': 'The evidence is a photograph',
                 'code': 'vol -f mem.raw windows.info | grep -i time',
                 'note': 'Record the capture time and reason about everything '
                         'relative to it.'},
                {'label': 'Corroborate rather than conclude',
                 'code': 'vol -f mem.raw windows.cmdline > cmdline.txt\n'
                         '# then check the same window in the event log',
                 'note': 'Memory plus logs plus disk. One source alone is how '
                         'investigations go wrong.'},
                {'label': 'A plugin failing is often normal',
                 'code': 'vol -f mem.raw windows.malfind 2>&1 | grep -i '
                         'error',
                 'note': 'Structures caught mid-update produce errors on a '
                         'perfectly good image.'},
            ],
            'misconceptions': [
                'Not finding a process in memory does not mean it never ran. '
                'Memory is reused constantly.',
                'A memory image is not internally consistent, because the '
                'machine kept running during capture.',
                'Memory analysis does not replace disk or log analysis. It '
                'answers a different question.',
            ],
            'try_it': [
                'Take two images of the same VM a minute apart and diff the '
                'process lists.',
                'Find something in memory and then look for corroboration in '
                'that machine\'s logs.',
            ],
            'next': None,
        },
    ],

    'drills': [
        {'id': 'vod-info', 'type': 'command',
         'prompt': 'Identify what operating system mem.raw came from.',
         'answer': 'vol -f mem.raw windows.info',
         'teach': 'Always first. If this fails, nothing downstream will be '
                  'right.'},
        {'id': 'vod-banner', 'type': 'command',
         'prompt': 'Read the kernel banner from a Linux memory image.',
         'answer': 'vol -f mem.raw banners.Banners',
         'teach': 'The banner names the exact kernel build, which is what you '
                  'need to find or build symbols.'},
        {'id': 'vod-pslist', 'type': 'command',
         'prompt': 'List processes from mem.raw by walking the kernel list.',
         'answer': 'vol -f mem.raw windows.pslist',
         'teach': 'Follows the linked list, exactly as the kernel does, and '
                  'can be lied to by unlinking.'},
        {'id': 'vod-psscan', 'type': 'command',
         'prompt': 'Find processes in mem.raw by scanning for their structures.',
         'answer': 'vol -f mem.raw windows.psscan',
         'teach': 'Ignores the list, so it finds unlinked and exited '
                  'processes. The disagreement is the finding.'},
        {'id': 'vod-pstree', 'type': 'command',
         'prompt': 'Show the process parent and child relationships in mem.raw.',
         'answer': 'vol -f mem.raw windows.pstree',
         'teach': 'A wrong parent for a well known process is stronger '
                  'evidence than any suspicious name.'},
        {'id': 'vod-cmdline', 'type': 'command',
         'prompt': 'Show the command line arguments of every process in mem.raw.',
         'answer': 'vol -f mem.raw windows.cmdline',
         'teach': 'Arguments say more than names, and they survive in memory '
                  'after the process exits.'},
        {'id': 'vod-malfind', 'type': 'command',
         'prompt': 'Find memory regions in mem.raw that look like injected code.',
         'answer': 'vol -f mem.raw windows.malfind',
         'teach': 'Executable, private, no backing file. The highest yield '
                  'single plugin, and JIT compilers look the same.'},
        {'id': 'vod-netscan', 'type': 'command',
         'prompt': 'Recover network connections from mem.raw.',
         'answer': 'vol -f mem.raw windows.netscan',
         'teach': 'Includes connections that had already closed, which live '
                  'netstat would have missed entirely.'},
        {'id': 'vod-dlllist', 'type': 'command',
         'prompt': 'List the loaded modules of process 1234 in mem.raw.',
         'answer': 'vol -f mem.raw windows.dlllist --pid 1234',
         'teach': '--pid narrows nearly every process plugin to one process.'},
        {'id': 'vod-handles', 'type': 'command',
         'prompt': 'List the open handles of process 1234 in mem.raw.',
         'answer': 'vol -f mem.raw windows.handles --pid 1234',
         'teach': 'Files, keys, mutexes and events. A named mutex is often '
                  'the most specific indicator a family has.'},
        {'id': 'vod-filescan', 'type': 'command',
         'prompt': 'Find file objects present in mem.raw.',
         'answer': 'vol -f mem.raw windows.filescan',
         'teach': 'File objects with offsets, which dumpfiles then extracts '
                  'by offset.'},
        {'id': 'vod-dumpfiles', 'type': 'command',
         'prompt': 'Extract cached files for process 1234 into ./out.',
         'answer': 'vol -f mem.raw -o ./out windows.dumpfiles --pid 1234',
         'teach': '-o is the output directory, and it must exist. What comes '
                  'out is what was cached, possibly partial.'},
        {'id': 'vod-memmap', 'type': 'command',
         'prompt': 'Dump the full address space of process 1234 into ./out.',
         'answer': 'vol -f mem.raw -o ./out windows.memmap --pid 1234 --dump',
         'teach': 'Then run strings, yara or a disassembler over it. This is '
                  'how unpacked code gets recovered.'},
        {'id': 'vod-vadinfo', 'type': 'command',
         'prompt': 'List the memory regions and permissions of process 1234.',
         'answer': 'vol -f mem.raw windows.vadinfo --pid 1234',
         'teach': 'The underlying data malfind reasons over. Reading it '
                  'yourself is how malfind stops being magic.'},
        {'id': 'vod-hivelist', 'type': 'command',
         'prompt': 'List the registry hives present in mem.raw.',
         'answer': 'vol -f mem.raw windows.registry.hivelist',
         'teach': 'The registry is largely in memory, including hives that '
                  'are locked on disk.'},
        {'id': 'vod-printkey', 'type': 'command',
         'prompt': 'Print the Run key from the registry in mem.raw.',
         'answer': 'vol -f mem.raw windows.registry.printkey --key '
                   '"Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Run"',
         'teach': 'Persistence, read from RAM. Backslashes need escaping in a '
                  'shell.'},
        {'id': 'vod-hashdump', 'type': 'command',
         'prompt': 'Recover local account hashes from mem.raw.',
         'answer': 'vol -f mem.raw windows.hashdump',
         'teach': 'The SAM is in memory. This is why an image is treated as '
                  'sensitive as the machine it came from.'},
        {'id': 'vod-modules', 'type': 'command',
         'prompt': 'List loaded kernel drivers from the module list in mem.raw.',
         'answer': 'vol -f mem.raw windows.modules',
         'teach': 'The list-walking version. modscan is the scanning '
                  'counterpart, and the same diff applies.'},
        {'id': 'vod-modscan', 'type': 'command',
         'prompt': 'Find kernel drivers in mem.raw by scanning rather than listing.',
         'answer': 'vol -f mem.raw windows.modscan',
         'teach': 'Same pslist versus psscan idea, one layer down in the '
                  'kernel.'},
        {'id': 'vod-linux-pslist', 'type': 'command',
         'prompt': 'List processes from a Linux memory image.',
         'answer': 'vol -f mem.raw linux.pslist.PsList',
         'teach': 'The operating system prefix is required, and the Linux '
                  'plugin names are more deeply nested.'},
        {'id': 'vod-symbols-dir', 'type': 'command',
         'prompt': 'Run a Linux plugin using symbol tables from ./symbols.',
         'answer': 'vol -s ./symbols -f mem.raw linux.pslist.PsList',
         'teach': '-s names a symbol directory, which is how a table you '
                  'generated yourself gets used.'},
        {'id': 'vod-dwarf2json', 'type': 'command',
         'prompt': 'Generate a symbol table from the debug kernel at /usr/lib/debug/vmlinux.',
         'answer': 'dwarf2json linux --elf /usr/lib/debug/vmlinux > '
                   'symbols/kernel.json',
         'teach': 'It must be the exact kernel the image came from. A close '
                  'version is not close enough.'},
        {'id': 'vod-isfinfo', 'type': 'command',
         'prompt': 'List the symbol tables volatility knows about locally.',
         'answer': 'vol isfinfo',
         'teach': 'Worth checking before concluding that an image cannot be '
                  'read.'},
        {'id': 'vod-json', 'type': 'command',
         'prompt': 'Produce JSON output for the process list of mem.raw.',
         'answer': 'vol -r json -f mem.raw windows.pslist',
         'teach': '-r json, and then jq. Far easier to filter than the table '
                  'format.'},
        {'id': 'vod-pid-filter', 'type': 'command',
         'prompt': 'Show only process 1234 in the process list of mem.raw.',
         'answer': 'vol -f mem.raw windows.pslist --pid 1234',
         'teach': 'Most process plugins take --pid, which saves grepping and '
                  'is much faster on a large image.'},
        {'id': 'vod-plugins', 'type': 'command',
         'prompt': 'List every plugin whose name mentions windows.',
         'answer': 'vol -h | grep windows',
         'teach': 'The naming is regular, so grepping the help is how you '
                  'find a plugin you half remember.'},
        {'id': 'vod-virsh-dump', 'type': 'command',
         'prompt': 'Capture memory from the running virtual machine vmname.',
         'answer': 'virsh dump --memory-only --live vmname mem.raw',
         'teach': 'Nothing runs inside the guest, so nothing is perturbed. '
                  'The best capture available when it is available.'},
        {'id': 'vod-avml', 'type': 'command',
         'prompt': 'Capture Linux memory to external storage with AVML.',
         'answer': 'sudo ./avml /media/external/mem.lime',
         'teach': 'No kernel module to build, and never write the image to '
                  'the machine\'s own disk.'},
        {'id': 'vod-winpmem', 'type': 'command',
         'prompt': 'Capture Windows memory to E drive with WinPmem.',
         'answer': 'winpmem.exe -o E:\\mem.raw',
         'teach': 'Small and well understood. Capture changes memory, which '
                  'is accepted and documented rather than hidden.'},
        {'id': 'vod-hash-image', 'type': 'command',
         'prompt': 'Hash the captured image and save the hash beside it.',
         'answer': 'sha256sum mem.raw | tee mem.raw.sha256',
         'teach': 'Immediately, with the time, the tool and its version '
                  'recorded alongside.'},
    ],

    'challenges': [
        {
            'id': 'voc-setup',
            'title': 'Get volatility working on a real image',
            'goal': 'Install the tool, fetch a public sample image, and get '
                    'as far as it correctly identifying what the image is.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'Install volatility 3, ideally with pipx so '
                                'it does not disturb your system Python.',
                 'hint': 'pipx install volatility3'},
                {'instruction': 'Download a public sample memory image. The '
                                'volatility project and several university '
                                'forensics courses publish them.'},
                {'instruction': 'Hash the image you downloaded and record it '
                                'alongside, as you would for evidence.',
                 'hint': 'sha256sum image.raw | tee image.raw.sha256'},
                {'instruction': 'Run windows.info and read every field. '
                                'Confirm it found a symbol table.'},
                {'instruction': 'If it failed, work out whether the cause was '
                                'the image, the symbols or the network, '
                                'before going further.'},
            ],
            'free': 'Install volatility 3, obtain a public sample image, hash '
                    'it, and get windows.info to identify it correctly.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
        {
            'id': 'voc-pslist-psscan',
            'title': 'Find what the process list is not showing',
            'goal': 'Run both process plugins, diff them mechanically, and '
                    'account for every difference.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'Run windows.pslist and windows.psscan on '
                                'your sample image, saving each to its own '
                                'file.'},
                {'instruction': 'Extract just the process IDs from each and '
                                'sort them.',
                 'hint': "awk 'NR>2{print $1}' pslist.txt | sort -u"},
                {'instruction': 'Use comm to find the IDs psscan saw and '
                                'pslist did not.',
                 'hint': 'comm -13 pslist-pids.txt psscan-pids.txt'},
                {'instruction': 'For each difference, decide whether it is an '
                                'exited process or something else, and write '
                                'down your reasoning.'},
                {'instruction': 'Do the same for windows.modules against '
                                'windows.modscan, which is the same idea one '
                                'layer down.'},
            ],
            'free': 'On a sample image: diff pslist against psscan '
                    'mechanically, account for every difference, and repeat '
                    'the exercise for modules against modscan.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
        {
            'id': 'voc-triage-run',
            'title': 'Run the whole triage sequence and keep it',
            'goal': 'Six plugins in order, into named files, with notes. The '
                    'habit matters as much as the output.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'Write a loop that runs info, pslist, psscan, '
                                'pstree, cmdline and netscan into an output '
                                'directory named per plugin.',
                 'hint': 'for p in windows.info windows.pslist ...; do vol -f '
                         'mem.raw $p > out/$p.txt 2>&1; done'},
                {'instruction': 'Time the whole thing, and note which plugin '
                                'dominated.'},
                {'instruction': 'Read pstree and find any process whose '
                                'parent does not make sense for it.'},
                {'instruction': 'Read cmdline and note any argument that '
                                'would be interesting on its own.'},
                {'instruction': 'Write a NOTES file recording, for each '
                                'plugin, the question it was answering and '
                                'what you concluded.'},
            ],
            'free': 'On a sample image: run the six plugin triage sequence '
                    'into named files, time it, and write notes recording the '
                    'question and conclusion for each.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
        {
            'id': 'voc-malfind',
            'title': 'Read malfind rather than counting it',
            'goal': 'Find injected regions, dump one, and take it apart with '
                    'tools from the rest of this roster.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'Run windows.malfind and read what it prints, '
                                'including the disassembly, for each hit.'},
                {'instruction': 'For one hit, run vadinfo on the same process '
                                'and find the corresponding region. Note its '
                                'permissions.'},
                {'instruction': 'Dump that process address space to a '
                                'directory.',
                 'hint': 'vol -f mem.raw -o ./out windows.memmap --pid PID '
                         '--dump'},
                {'instruction': 'Run strings with a sensible minimum and the '
                                'UTF-16 pass over the dump, as the strings '
                                'module taught.'},
                {'instruction': 'If you have yara installed, write a rule '
                                'from something you found and run it against '
                                'the dump.'},
                {'instruction': 'Consider what a legitimate JIT compiler '
                                'would look like here, and how you would tell '
                                'it apart.'},
            ],
            'free': 'On a sample image: read every malfind hit, correlate one '
                    'with vadinfo, dump the process, and analyse the dump '
                    'with strings and yara.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
        {
            'id': 'voc-network',
            'title': 'Tie connections back to processes',
            'goal': 'Recover the network picture and join it to the process '
                    'picture, which is where the finding usually is.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'Run windows.netscan and save the output.'},
                {'instruction': 'Extract every unique remote address and '
                                'port.',
                 'hint': "awk 'NR>2{print $4, $5}' netscan.txt | sort -u"},
                {'instruction': 'For each connection, find the owning process '
                                'in your pslist output, and its command line '
                                'in cmdline.'},
                {'instruction': 'Note any connection whose owning process is '
                                'not in pslist at all, and say what that '
                                'means.'},
                {'instruction': 'Note any closed connection, and say why it '
                                'is still evidence.'},
            ],
            'free': 'On a sample image: recover every connection, join each '
                    'to its owning process and command line, and account for '
                    'any that has no live process.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
        {
            'id': 'voc-capture',
            'title': 'Capture your own image, correctly',
            'goal': 'Do the capture side on a machine you own, including the '
                    'parts that are impossible to fix afterwards.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'On a virtual machine you own, take a '
                                'hypervisor memory dump while it runs.',
                 'hint': 'virsh dump --memory-only --live vmname mem.raw'},
                {'instruction': 'Hash it immediately and record the time, the '
                                'tool and its version alongside.'},
                {'instruction': 'If the VM is Linux, capture the kernel debug '
                                'symbols at the same time, and generate a '
                                'symbol table from them.',
                 'hint': 'dwarf2json linux --elf vmlinux > symbols/k.json'},
                {'instruction': 'Analyse your own image with pslist and '
                                'confirm you can see processes you know were '
                                'running.'},
                {'instruction': 'Take a second image a minute later and diff '
                                'the process lists, to see how much changes.'},
            ],
            'free': 'On a VM you own: capture memory without perturbing the '
                    'guest, hash and document it, obtain the symbols you '
                    'would need, analyse it, and compare two captures a '
                    'minute apart.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
    ],

    'quiz': [
        {'id': 'voq-pslist-psscan', 'type': 'mcq',
         'prompt': 'psscan shows a process that pslist does not. What are the '
                   'two likely explanations?',
         'answer': 'It exited and its structure survives, or it was unlinked '
                   'from the list.',
         'distractors': ['The image is corrupt in that region.',
                         'psscan is less accurate and produces false '
                         'positives.',
                         'The process belongs to a different session.'],
         'teach': 'pslist walks the kernel list and psscan sweeps for '
                  'structures. The disagreement is where the technique lives.'},
        {'id': 'voq-hiding', 'type': 'mcq',
         'prompt': 'How can a process run without appearing in pslist?',
         'answer': 'Its structure is unlinked from the list the reporting '
                   'tools read, while the scheduler uses another.',
         'distractors': ['It runs entirely in kernel space with no process '
                         'structure.',
                         'It renames itself to match a system process.',
                         'It suspends itself between captures.'],
         'teach': 'Direct kernel object manipulation. psscan exists precisely '
                  'because the list can be lied to.'},
        {'id': 'voq-symbols', 'type': 'mcq',
         'prompt': 'Why is analysing a Linux image usually harder than a '
                   'Windows one?',
         'answer': 'There is no public symbol server, so the symbol table '
                   'must be built from the exact kernel.',
         'distractors': ['Linux memory is compressed by default.',
                         'Volatility has no Linux plugins.',
                         'Linux images cannot be captured without a kernel '
                         'module.'],
         'teach': 'Capture the kernel debug symbols at the same time as the '
                  'image, because afterwards may be too late.'},
        {'id': 'voq-profile', 'type': 'mcq',
         'prompt': 'A write-up uses --profile=Win7SP1x64. What does that tell '
                   'you?',
         'answer': 'It is volatility 2, and the command will not work '
                   'unchanged in volatility 3.',
         'distractors': ['The image is from Windows 7 and needs no symbols.',
                         'The profile flag is optional in both versions.',
                         'The write-up is using a custom symbol table.'],
         'teach': 'Version 3 replaced profiles with symbol tables and gave '
                  'plugins an operating system prefix.'},
        {'id': 'voq-malfind', 'type': 'mcq',
         'prompt': 'What shape does malfind look for?',
         'answer': 'Memory that is executable and private with no backing '
                   'file.',
         'distractors': ['Byte signatures of known malware families.',
                         'Processes whose parent is unexpected.',
                         'Regions with unusually high entropy.'],
         'teach': 'Legitimate JIT compilers produce the same shape, so a hit '
                  'is a lead rather than a verdict.'},
        {'id': 'voq-netscan', 'type': 'mcq',
         'prompt': 'netscan shows a closed connection. Is that useful?',
         'answer': 'Yes. The structure survives, and it is evidence a '
                   'connection existed.',
         'distractors': ['No, it is stale data from a previous boot.',
                         'No, closed connections are always false '
                         'positives.',
                         'Only if the owning process is still running.'],
         'teach': 'This is one of the things memory gives you that a live '
                  'netstat would already have lost.'},
        {'id': 'voq-capture-vm', 'type': 'mcq',
         'prompt': 'What is the least disruptive way to capture memory from a '
                   'virtual machine?',
         'answer': 'A hypervisor snapshot or dump, which runs nothing inside '
                   'the guest.',
         'distractors': ['A capture tool run inside the guest as '
                         'administrator.',
                         'Suspending the guest and copying its disk image.',
                         'Reading /proc/kcore from inside the guest.'],
         'teach': 'Every in-guest tool perturbs the thing it measures. The '
                  'hypervisor does not have to.'},
        {'id': 'voq-writetarget', 'type': 'mcq',
         'prompt': 'Why write a memory image to external storage rather than '
                   'the local disk?',
         'answer': 'Writing locally overwrites unallocated space that may '
                   'itself be evidence.',
         'distractors': ['Local disks are too slow for the volume of data.',
                         'The capture tool cannot write to the system '
                         'volume.',
                         'It would corrupt the image with filesystem '
                         'metadata.'],
         'teach': 'Order of volatility, and not destroying one source while '
                  'collecting another.'},
        {'id': 'voq-absence', 'type': 'mcq',
         'prompt': 'You do not find a suspicious process in the image. What '
                   'does that establish?',
         'answer': 'Very little, because memory is reused and it may be long '
                   'gone.',
         'distractors': ['That it never ran on this machine.',
                         'That it ran only in kernel space.',
                         'That the image was captured incorrectly.'],
         'teach': 'A memory image is one instant. Absence is much weaker '
                  'evidence than presence.'},
        {'id': 'voq-consistency', 'type': 'mcq',
         'prompt': 'A plugin errors on one structure but works on others. '
                   'What is the most likely reason?',
         'answer': 'The machine kept running during capture, so parts of the '
                   'image are from different moments.',
         'distractors': ['The symbol table is wrong for this image.',
                         'Anti-forensics is targeting the analysis tool.',
                         'The image was truncated during transfer.'],
         'teach': 'A memory image is not internally consistent, and occasional '
                  'errors are normal rather than a sign of tampering.'},
    ],
}
