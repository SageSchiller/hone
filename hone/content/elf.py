"""readelf and objdump: the map of a binary, not the dump.

After file, strings and xxd a program is still a bag of bytes with a label.
ELF is the map those bytes actually follow: a header that says what the file
is, sections the linker thinks in, segments the loader thinks in, and symbols
that may or may not still be there. readelf prints that map. objdump prints
the bytes as instructions. They are twins: same file, two questions.

Sandbox-verified by pointing the real tools at a real binary this machine
already has. Scope: how the file is laid out, never how to attack one.
"""

MODULE = {
    'id': 'elf',
    'title': 'readelf and objdump',
    'group': 'Security',
    'blurb': 'Read a binary without running it: the map, then the listing.',
    'context': 'You are at a shell with a binary in front of you, reading it, not running it.',
    'needs': ('readelf', 'objdump'),
    'prereqs': ['linux', 'file'],
    'adapter': 'sandbox',
    'estimate': '3-4 hours',
    'order': 75,

    'lessons': [
        {
            'id': 'ef-what',
            'title': 'A binary is a map, not a bag of bytes',
            'next': 'ef-header',
            'concept': (
                'readelf and objdump read a program without running it. After '
                '`file` says "ELF 64-bit LSB pie executable", the leftover '
                'questions are the ones these two answer: is it for this '
                'machine, what libraries does it need, is it stripped, where '
                'is main, what does this function actually do.\n\n'
                'That is daily work on Linux, not a specialist hobby. A '
                'binary that will not start, a file you did not build, a '
                'library list you do not want `ldd` to obtain by running the '
                'interpreter: those are the reasons to learn the map. '
                '`readelf` prints it (headers, sections, segments, symbols, '
                'the dynamic table). `objdump` prints the same file as '
                'instructions. Reach for readelf when the question is "what '
                'is this file". Reach for objdump when the question is "what '
                'does this function do". Neither one runs the program.\n\n'
                '**ELF is the container those bytes follow.** The first four '
                'bytes are `7f 45 4c 46`, DEL plus the letters E L F. Then a '
                'header (32 or 64 bit, which machine, whether this is an '
                'object, a library, or something the kernel can start) and '
                'two tables: sections for the linker, segments for the '
                'loader. The program sits in both, under different names.\n\n'
                'file, readelf and objdump are three depths of the same '
                'question. file is a guess from a few bytes. readelf names '
                'the fields that guess came from. objdump is what those '
                'fields point at, decoded. Opening objdump first is how a '
                'page of assembly becomes noise rather than an answer.\n\n'
                'The next lesson is the ELF header: the first 64 bytes, and '
                'the one word in it that surprises people on a modern box.'
            ),
            'examples': [
                {
                    'label': 'The first question, two tools',
                    'code': ('file /bin/true\n'
                             '  ELF 64-bit LSB pie executable, x86-64\n'
                             '\n'
                             'readelf -h /bin/true     the header, as fields\n'
                             'objdump -f /bin/true     the same idea, shorter'),
                    'note': 'file is the one-line guess. readelf names the '
                            'fields, which is how you find out Type, Machine '
                            'and whether the file will even run here.',
                },
                {
                    'label': 'Who owns which question',
                    'code': ('readelf -h   header\n'
                             'readelf -S   sections\n'
                             'readelf -l   segments (program headers)\n'
                             'readelf -s   symbols\n'
                             'readelf -d   dynamic section\n'
                             'objdump -d   disassemble\n'
                             'objdump -s   hex dump by section'),
                    'note': 'readelf owns the map. objdump owns the listing. '
                            'Memorise the five letters and objdump -d.',
                },
            ],
            'misconceptions': [
                'readelf and objdump do not run the file. They parse it. That '
                'is why they are safe on something you do not trust yet.',
                'A hex dump is not a map. xxd shows bytes. ELF says which '
                'bytes are the entry point, which are the interpreter, which '
                'are just padding.',
            ],
            'try_it': [
                'Run `file /bin/true`, then `readelf -h /bin/true`, and match '
                'the Class, Type and Machine lines to what file said.',
            ],
        },
        {
            'id': 'ef-header',
            'title': 'The ELF header, and why Type is often DYN',
            'next': 'ef-sections',
            'concept': (
                '`readelf -h` is the first question: what is this file, and '
                'will it even run here. Class, Machine, and Type answer that '
                'in one screen. That is why you read the header before you '
                'disassemble: an ARM binary still prints, and every '
                'instruction is a lie about this box.\n\n'
                '**Class** is ELF32 or ELF64: the pointer size. **Machine** is '
                'the instruction set, x86-64 or ARM or whatever this file was '
                'built for. **Type** is the job: REL is an object file, the '
                '`.o` the compiler just wrote. EXEC is a fixed-address '
                'executable, the old style. DYN is a shared object, and also '
                'almost every modern program you will open, because position '
                'independent executables are DYN files the kernel knows how '
                'to start. file says "pie executable". readelf says DYN. Same '
                'fact.\n\n'
                '**Entry point** is the virtual address the loader jumps to. '
                'It is not "the first byte of the file" and it is not always '
                '`main`. `main` is a symbol. The entry is often `_start` in '
                'the C runtime, which sets up the stack and then calls main.\n\n'
                'A header that says ELF32 and ARM on an x86-64 box is not a '
                'program you can run here. That is the whole reason to read '
                'the header before you try.\n\n'
                'The Type field is the one that catches people. Seeing DYN '
                'and concluding "this is a library, I cannot run it" is the '
                'usual misread. A position-independent executable is a DYN '
                'file the kernel knows how to start, which is why ASLR can '
                'slide the whole program rather than only its libraries. file '
                'already said "pie". readelf is naming the same fact. An '
                'actual shared object is also DYN, and the difference is not '
                'the Type line: it is whether there is an INTERP segment and '
                'whether the file is on a path the kernel will exec.\n\n'
                'The next lesson is sections: the names the linker thinks in.'
            ),
            'examples': [
                {
                    'label': 'The three fields that decide the file',
                    'code': ('readelf -h /bin/true\n'
                             '  Class:    ELF64\n'
                             '  Type:     DYN (Position-Independent '
                             'Executable)\n'
                             '  Machine:  Advanced Micro Devices X86-64\n'
                             '  Entry:    0x2570'),
                    'note': 'DYN plus "file says pie" is the modern default, '
                            'not a shared library you opened by mistake.',
                },
                {
                    'label': 'Object, library, program',
                    'code': ('REL   hello.o      not runnable, needs a link\n'
                             'DYN   libc.so, and most /bin/* today\n'
                             'EXEC  older binaries, fixed load address'),
                    'note': 'Type is the job, not the file name. A .so is DYN. '
                            'A PIE program is also DYN.',
                },
            ],
            'misconceptions': [
                'DYN does not mean "this is a library". On a current Linux it '
                'usually means "this program was built PIE".',
                'The entry point is not main. main is a symbol the runtime '
                'calls after it has a stack.',
            ],
            'try_it': [
                'Run `readelf -h /bin/true` and `readelf -h /lib/x86_64-linux-gnu/libc.so.6` '
                'or whatever libc path `ldd /bin/true` shows. Both say DYN. '
                'Note what else differs.',
            ],
        },
        {
            'id': 'ef-sections',
            'title': 'Sections: how the linker sees the file',
            'next': 'ef-segments',
            'concept': (
                'Sections are the names the linker thinks in. `readelf -S` '
                'is how you find the code (`.text`), the writable data, and '
                'whether symbols are still there. That is the map you search '
                'before you dump bytes.\n\n'
                'A **section** is a named slice of the file with a type and '
                'flags. `.text` is the instructions, executable, not writable. '
                '`.rodata` is constants, readable, not writable. `.data` is '
                'initialised globals, readable and writable. `.bss` is '
                'uninitialised globals: it takes no file bytes, only a size, '
                'because the loader can zero that memory itself. `.symtab` '
                'and `.strtab` are the full symbol table. `.dynsym` is the '
                'smaller one the dynamic linker needs. `.shstrtab` is the '
                'names of the sections themselves.\n\n'
                'Flags are the useful column. A is allocated at run time, W '
                'is writable, X is executable. A `.text` with W is unusual '
                'and worth a second look. A writable and executable section '
                'is the combination loaders and hardening exist to stop.\n\n'
                '`objdump -h` is the same table in a different layout. Use '
                'whichever you can read. The names are the same.\n\n'
                'A first look at `readelf -S` is a wall of names. Most of them '
                'are noise on the first pass: `.comment`, `.note.*`, '
                '`.eh_frame`. The useful question is "which of these is code, '
                'which is writable, which is only a description". That is why '
                'the flags column matters more than the count. A stripped '
                'binary still has `.text`. Stripping removes `.symtab`, not '
                'the instructions, which is why a file that "has no symbols" '
                'is still a program you can disassemble.\n\n'
                'The next lesson is segments: the same bytes, grouped the '
                'way the loader actually maps them.'
            ),
            'examples': [
                {
                    'label': 'The sections you will actually look for',
                    'code': ('readelf -S /bin/true\n'
                             '  .text     PROGBITS  AX    instructions\n'
                             '  .rodata   PROGBITS  A     constants\n'
                             '  .data     PROGBITS  WA    init globals\n'
                             '  .bss      NOBITS    WA    zeroed, not in file\n'
                             '  .symtab   SYMTAB          full names, or gone'),
                    'note': 'NOBITS means "describe this, do not store it". '
                            'That is why .bss does not make the file bigger.',
                },
                {
                    'label': 'objdump says the same thing',
                    'code': ('objdump -h /bin/true\n'
                             '  Idx Name    Size     VMA      File off  Algn\n'
                             '    n .text   0x....   0x....   0x....    2**4'),
                    'note': 'VMA is where it wants to live. File off is where '
                            'the bytes sit in the file. Those two numbers are '
                            'the map.',
                },
            ],
            'misconceptions': [
                '.bss is not missing data. It is data that is defined to be '
                'zero, so storing it would be a waste.',
                'A stripped binary still has sections. It has lost .symtab, '
                'not .text.',
            ],
            'try_it': [
                'Run `readelf -S /bin/true` and find .text, .data and .bss. '
                'Check the flags column against AX, WA, WA.',
            ],
        },
        {
            'id': 'ef-segments',
            'title': 'Segments: how the loader sees the file',
            'next': 'ef-symbols',
            'concept': (
                'Segments are what the kernel actually maps. `readelf -l` '
                'answers which libraries this file needs and how it will sit '
                'in memory, without running it. That is why it replaces '
                '`ldd` on a binary you did not build.\n\n'
                'A **LOAD** segment is a range of the file mapped into memory '
                'with some combination of read, write, execute. There are '
                'usually two: one RX for the code and constants, one RW for '
                'data. Several sections land in one LOAD. That is why a '
                'section table and a segment table can disagree about how '
                'many pieces there are, and both be right.\n\n'
                '**INTERP** names the dynamic linker, usually '
                '`/lib64/ld-linux-x86-64.so.2`. That is the program that '
                'actually starts a dynamically linked binary: the kernel '
                'runs the interpreter, the interpreter maps the rest. '
                '**DYNAMIC** points at the table `readelf -d` prints: NEEDED '
                'libraries, the symbol hash, rpath if any.\n\n'
                'A static binary has no INTERP and almost no DYNAMIC. `ldd` '
                'on one says "not a dynamic executable". That is this table, '
                'empty.\n\n'
                'The usual confusion is counting sections and expecting the '
                'same number of mappings in `/proc/<pid>/maps`. The loader '
                'does not map sections. It maps LOAD segments, and several '
                'sections share one. That is why `.text` and `.rodata` often '
                'live in the same RX range, and why a W+X mapping is the '
                'thing hardening exists to stop: it would be one LOAD with '
                'both write and execute. `readelf -l` is also where '
                '`GNU_STACK` and `GNU_RELRO` show up, which are policy, not '
                'code: whether the stack is executable, whether the GOT is '
                'made read-only after relocate.\n\n'
                'The next lesson is symbols: the names that may still be '
                'attached to addresses.'
            ),
            'examples': [
                {
                    'label': 'Two LOADs and an interpreter',
                    'code': ('readelf -l /bin/true\n'
                             '  INTERP  /lib64/ld-linux-x86-64.so.2\n'
                             '  LOAD    R E    code and rodata\n'
                             '  LOAD    RW     data and bss\n'
                             '  DYNAMIC'),
                    'note': 'R E without W is the execute segment. RW without '
                            'E is the data segment. That split is deliberate.',
                },
                {
                    'label': 'What ldd is actually reading',
                    'code': ('ldd /bin/true\n'
                             '  linux-vdso.so.1\n'
                             '  libc.so.6 => /usr/lib/libc.so.6\n'
                             '  /lib64/ld-linux-x86-64.so.2\n'
                             '\n'
                             'readelf -d /bin/true | grep NEEDED'),
                    'note': 'ldd runs the interpreter in a special mode. '
                            'readelf -d only reads the file. Prefer readelf '
                            'on a binary you do not trust.',
                },
            ],
            'misconceptions': [
                'Sections and segments are not two words for the same table. '
                'The linker uses one, the loader uses the other.',
                'ldd is not a parser. It can run code from the file. readelf '
                '-d does not.',
            ],
            'try_it': [
                'Run `readelf -l /bin/true` and count the LOAD lines. Then '
                '`readelf -d /bin/true` and list every NEEDED library.',
            ],
        },
        {
            'id': 'ef-symbols',
            'title': 'Symbols, and what stripping removes',
            'next': 'ef-disasm',
            'concept': (
                'Symbols are names for addresses. `readelf -s` is how you '
                'find `main`, or learn it is gone. That is why stripping '
                'matters: the program still runs, gdb can no longer break on '
                'a name, and the imports are still there. `objdump -t` is '
                'the same idea.\n\n'
                'There are two tables. `.symtab` is the full one: every '
                'function and global the compiler named, plus a lot of '
                'internal junk. `.dynsym` is the subset the dynamic linker '
                'needs, imports and exports. A binary can lose `.symtab` and '
                'still run, because the loader only needs `.dynsym`. That '
                'loss is **stripping**. `file` then says "stripped". `readelf '
                '-s` still shows the dynamic symbols, just fewer of them.\n\n'
                '`main` lives in `.symtab`. If the file is stripped, `main` '
                'is gone as a name and still present as instructions. You '
                'find it from the entry point, from a string it prints, or '
                'from a disassembly, not from the symbol table.\n\n'
                '`nm` is the short listing people remember. `nm -D` is the '
                'dynamic table. This module uses readelf so the two tables '
                'stay visibly different.\n\n'
                'The failure that wastes an hour is `nm: no symbols` read as '
                '"this file is empty". nm looks at `.symtab` by default. A '
                'stripped system binary has none, and still imports `printf` '
                'through `.dynsym`. `nm -D` or `readelf -s` still has those. '
                '`main` is not one of them, because the dynamic linker never '
                'needed that name: the C runtime calls it after `_start` has '
                'a stack. That is why a stripped binary still runs, and why '
                'gdb will not `break main` on it.\n\n'
                'The next lesson is objdump: the bytes as instructions, '
                'which is what you have left when the names are gone.'
            ),
            'examples': [
                {
                    'label': 'Two tables, two jobs',
                    'code': ('readelf -s  bin     .symtab, or empty if stripped\n'
                             'readelf -s  bin     look for .dynsym in the same '
                             'listing\n'
                             'nm bin              .symtab, errors if stripped\n'
                             'nm -D bin           .dynsym'),
                    'note': 'A stripped system binary still imports printf. '
                            'That import is .dynsym. main is not.',
                },
                {
                    'label': 'What stripping changes',
                    'code': ('gcc -o hello hello.c\n'
                             '  readelf -s hello | grep main     there\n'
                             'strip hello\n'
                             '  readelf -s hello | grep main     gone\n'
                             '  the .text bytes did not move'),
                    'note': 'strip deletes names, not code. The program is '
                            'the same size of instructions and a smaller file.',
                },
            ],
            'misconceptions': [
                'Stripped does not mean empty of symbols. It means the full '
                'table is gone. Imports remain.',
                'main is not special to the loader. It is special to the C '
                'runtime, which is why a stripped binary still starts.',
            ],
            'try_it': [
                'Run `readelf -s /bin/true | head` and see whether main is '
                'there. Then `readelf -s /bin/true | grep printf` and see an '
                'import survive.',
            ],
        },
        {
            'id': 'ef-disasm',
            'title': 'objdump: bytes as instructions',
            'next': 'ef-workflow',
            'concept': (
                '`objdump -d` is the listing: what this function actually '
                'does, in the instructions that will run. That is the tool '
                'you reach for when there is no source, or when the source '
                'and the binary have drifted. Address, hex, instruction.\n\n'
                'The default syntax on Linux is AT&T: `mov %rsi, %rax` means '
                'copy rsi into rax, source then destination, registers with a '
                'percent, immediates with a dollar. Intel syntax flips the '
                'operands and drops the decoration: `objdump -M intel -d`. '
                'Neither is more true. Pick one and stay with it for an hour '
                'or the page will swim.\n\n'
                'You do not need to know every instruction. A first reading '
                'is: `call` goes to a function, `jmp` goes elsewhere, `ret` '
                'comes back, `cmp` and `test` set flags, `jcc` (je, jne, '
                'ja) branches on those flags, `mov` copies, `lea` computes '
                'an address. A call to `puts@plt` is a call through the '
                'procedure linkage table, which is how a dynamically linked '
                'binary reaches libc.\n\n'
                '`objdump -d -j .text` keeps the listing to one section. '
                'Without that, a large binary is a lot of screen.\n\n'
                'The first page of `/bin/true` is not `main`. It is `_start`, '
                'or the C runtime, or a GNU property note, because the entry '
                'point is not the symbol you write. On a PIE binary the '
                'addresses you see are relative to a base the loader has not '
                'chosen yet, which is why they look small and why they will '
                'not match `/proc/<pid>/maps` until the program is running. '
                'Pick a syntax and stay with it for the hour: mixing AT&T '
                'and Intel in the same sitting is how `mov %rsi, %rax` gets '
                'read backwards and the whole listing becomes fiction.\n\n'
                'The next lesson is a short workflow: which flag answers '
                'which question, in the order you actually ask them.'
            ),
            'examples': [
                {
                    'label': 'A few lines of a listing',
                    'code': ('objdump -d -j .text /bin/true | head\n'
                             '  401000:  f3 0f 1e fa     endbr64\n'
                             '  401004:  31 ed           xor    %ebp,%ebp\n'
                             '  401006:  49 89 d1        mov    %rdx,%r9'),
                    'note': 'Address, hex, assembly. The hex is the same '
                            'bytes xxd would show at that offset, decoded.',
                },
                {
                    'label': 'The same bytes, Intel syntax',
                    'code': ('objdump -M intel -d -j .text /bin/true | head\n'
                             '  401006:  49 89 d1        mov    r9, rdx'),
                    'note': 'Same instruction. Destination first in Intel. '
                            'That is the whole syntax war.',
                },
            ],
            'misconceptions': [
                'A listing is not the source. Optimisers move things. What '
                'you see is what will run, not what was written.',
                'plt in a name is not the function. It is the trampoline that '
                'finds the function. The real puts lives in libc.',
            ],
            'try_it': [
                'Disassemble /bin/true with `objdump -d -j .text` and find a '
                'call. Then rerun with `-M intel` and find the same call.',
            ],
        },
        {
            'id': 'ef-workflow',
            'title': 'Which tool answers which question',
            'concept': (
                'This lesson is the habit: which tool answers which question, '
                'in the order you actually ask them. The payoff is not more '
                'flags. It is not opening objdump first and drowning.\n\n'
                '**What is it.** `file`, then `readelf -h`. Architecture, '
                'type, stripped or not. If the Machine line is not this box, '
                'stop. The rest of the tools will still print, and the print '
                'will be about a program you cannot run here.\n\n'
                '**What does it need.** `readelf -d` and the NEEDED lines, or '
                '`readelf -l` and INTERP. Prefer those over `ldd` on a file '
                'you did not build.\n\n'
                '**What is inside.** `readelf -S` for the names, `readelf -s` '
                'for the symbols that remain. If main is there, you have a '
                'place to start a later gdb session. If it is not, you have '
                'the entry point and the strings.\n\n'
                '**What does this function do.** `objdump -d -j .text`, then '
                'search for the name or the address. Hex from xxd and '
                'instructions from objdump are the same bytes. The next '
                'module that consumes this one is gdb, which stops the '
                'process those instructions become.\n\n'
                'Skip the header and the next four commands are harder, not '
                'faster. A listing of an ARM binary on an x86 box still '
                'prints, and every instruction is a lie about this machine. '
                'A `.o` still disassembles, and the calls have no addresses '
                'yet because the linker has not run. The header is a filter: '
                'most files you should not spend an hour on fail it in one '
                'line.\n\n'
                'That is enough to read a binary without running it. Running '
                'it under a debugger is a different tool.'
            ),
            'examples': [
                {
                    'label': 'The five commands, in order',
                    'code': ('file bin\n'
                             'readelf -h bin\n'
                             'readelf -d bin\n'
                             'readelf -s bin\n'
                             'objdump -d -j .text bin'),
                    'note': 'Each line answers one question. Skip one and the '
                            'next one is harder to read, not faster.',
                },
                {
                    'label': 'When to stop',
                    'code': ('Machine: ARM          not this box, stop\n'
                             'Type: REL             it is a .o, link it first\n'
                             'no INTERP, no NEEDED  static, ldd will say so'),
                    'note': 'The header is a filter. Most files you should '
                            'not disassemble fail this filter in one line.',
                },
            ],
            'misconceptions': [
                'objdump first is not faster. Without the header you do not '
                'know whether the listing is even for this machine.',
                'This module does not replace running the program. It is what '
                'you do before you decide to.',
            ],
            'try_it': [
                'Pick any program in /bin, and run the five commands above '
                'on it in order. Write down Type, one NEEDED, and whether '
                'main is in the symbol table.',
            ],
        },
    ],

    'drills': [
        {'id': 'efd-header', 'type': 'command',
         'answer': 'readelf -h bin',
         'prompt': 'Print the ELF header of a file called bin.',
         'teach': '-h is the header: Class, Type, Machine, entry point.'},
        {'id': 'efd-sections', 'type': 'command',
         'answer': 'readelf -S bin',
         'prompt': 'List the sections of a file called bin.',
         'teach': '-S is the section table, the names the linker uses.'},
        {'id': 'efd-segments', 'type': 'command',
         'answer': 'readelf -l bin',
         'prompt': 'List the program headers of a file called bin.',
         'teach': '-l is segments. The loader maps these, not the sections.'},
        {'id': 'efd-symbols', 'type': 'command',
         'answer': 'readelf -s bin',
         'prompt': 'List the symbols of a file called bin.',
         'teach': 'Both .symtab and .dynsym appear here. Stripped files keep '
                  'only the dynamic ones.'},
        {'id': 'efd-dynamic', 'type': 'command',
         'answer': 'readelf -d bin',
         'prompt': 'Print the dynamic section of a file called bin.',
         'teach': 'NEEDED lines are the shared libraries. This reads the file '
                  'and does not run it, unlike ldd.'},
        {'id': 'efd-objdump-h', 'type': 'command',
         'answer': 'objdump -h bin',
         'prompt': 'List sections of bin with objdump.',
         'teach': 'Same table as readelf -S, different layout.'},
        {'id': 'efd-disasm', 'type': 'command',
         'answer': 'objdump -d bin',
         'prompt': 'Disassemble the executable sections of bin.',
         'teach': '-d is the listing. Add -j .text when the file is large.'},
        {'id': 'efd-intel', 'type': 'command',
         'answer': 'objdump -M intel -d bin',
         'prompt': 'Disassemble bin using Intel syntax.',
         'teach': 'Default on Linux is AT&T. -M intel flips the operands.'},
        {'id': 'efd-text', 'type': 'command',
         'answer': 'objdump -d -j .text bin',
         'prompt': 'Disassemble only the .text section of bin.',
         'teach': '-j keeps the listing to one section so the rest is not '
                  'noise.'},
        {'id': 'efd-file', 'type': 'command',
         'answer': 'objdump -f bin',
         'prompt': 'Print objdump\'s short file header for bin.',
         'teach': 'A shorter readelf -h. Architecture and start address.'},
    ],

    'challenges': [
        {
            'id': 'efc-header',
            'title': 'Read the header of a real binary',
            'goal': 'The first question is what the file is. Point readelf at '
                    'a program this machine already has and keep the fields.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {}},
            'solution': {
                'shell': 'readelf -h /bin/true > header.txt',
            },
            'steps': [
                {'instruction': 'Run readelf -h on /bin/true and save the '
                                'output as header.txt.',
                 'hint': 'readelf -h /bin/true > header.txt'},
            ],
            'free': 'Write header.txt containing the ELF header of /bin/true.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_contains': {
                        'header.txt': ['ELF Header', 'Class:', 'Type:',
                                       'Machine:'],
                    },
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'efc-needed',
            'title': 'List the libraries without using ldd',
            'goal': 'ldd runs the interpreter. readelf -d only reads the file. '
                    'On a binary you did not build, that difference matters.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {}},
            'solution': {
                'shell': "readelf -d /bin/true | grep NEEDED > needed.txt",
            },
            'steps': [
                {'instruction': 'Print the dynamic section of /bin/true.',
                 'hint': 'readelf -d /bin/true'},
                {'instruction': 'Keep only the NEEDED lines, in needed.txt.',
                 'hint': 'grep NEEDED'},
            ],
            'free': 'Write needed.txt with the NEEDED lines from /bin/true.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_contains': {
                        'needed.txt': ['NEEDED'],
                    },
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'efc-disasm',
            'title': 'Take a short listing of .text',
            'goal': 'A full objdump of a system binary is long. Restrict it '
                    'to .text and keep the head, so the listing is something '
                    'you can read.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {}},
            'solution': {
                'shell': 'objdump -d -j .text /bin/true | head -n 30 > listing.txt',
            },
            'steps': [
                {'instruction': 'Disassemble only .text of /bin/true.',
                 'hint': 'objdump -d -j .text /bin/true'},
                {'instruction': 'Save the first thirty lines as listing.txt.',
                 'hint': 'head -n 30'},
            ],
            'free': 'Write listing.txt with the start of the .text listing '
                    'of /bin/true.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_contains': {
                        'listing.txt': ['.text'],
                    },
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'efc-own',
            'title': 'Inspect a binary you built',
            'goal': 'The system copies are stripped. A binary you compile '
                    'still has main. Build one and find it.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'Write a tiny C file with a main that returns '
                                '0, and compile it with gcc -o hello hello.c.'},
                {'instruction': 'readelf -h hello and confirm Type and Class.'},
                {'instruction': 'readelf -s hello and find main. Then strip '
                                'hello and look again.'},
                {'instruction': 'objdump -d -j .text hello and find the '
                                'listing, with and without names.'},
            ],
            'free': 'On this machine: compile a tiny program, find main in '
                    'the symbol table, strip it, and look at .text.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
    ],

    'quiz': [
        {
            'id': 'efq-twins',
            'type': 'mcq',
            'prompt': 'What is the split of work between readelf and objdump?',
            'answer': 'readelf prints the ELF map; objdump prints bytes as instructions.',
            'distractors': [
                'readelf runs the program; objdump only reads it.',
                'objdump is for libraries; readelf is for executables.',
                'They are two names for the same command.',
            ],
            'teach': 'Same file, two questions: what is this, and what does this function do.',
        },
        {
            'id': 'efq-dyn',
            'type': 'mcq',
            'prompt': 'readelf -h says Type DYN on /bin/true. What does that usually mean?',
            'answer': 'A position-independent executable, which is how most modern programs are built.',
            'distractors': [
                'The file is a shared library and cannot be started.',
                'The file is an object file that still needs linking.',
                'The file is statically linked.',
            ],
            'teach': 'file says pie executable. readelf says DYN. Same fact.',
        },
        {
            'id': 'efq-bss',
            'type': 'mcq',
            'prompt': 'Why does .bss take no space in the file?',
            'answer': 'It is uninitialised data, defined to be zero, so the loader can create it.',
            'distractors': [
                'The compiler forgot to emit it.',
                'It lives in the ELF header instead.',
                'It is compressed in .note.',
            ],
            'teach': 'NOBITS means describe this, do not store it.',
        },
        {
            'id': 'efq-ldd',
            'type': 'mcq',
            'prompt': 'Why prefer readelf -d over ldd on a binary you did not build?',
            'answer': 'readelf only parses the file; ldd runs the interpreter.',
            'distractors': [
                'ldd cannot see NEEDED lines.',
                'readelf is faster on large files.',
                'ldd only works on stripped binaries.',
            ],
            'teach': 'The map is in the file. You do not need to start the program to read it.',
        },
        {
            'id': 'efq-strip',
            'type': 'mcq',
            'prompt': 'A binary is stripped. What is gone?',
            'answer': 'The full symbol table. Imports in .dynsym and the instructions remain.',
            'distractors': [
                'The .text section.',
                'The ELF header.',
                'Every symbol, including imports.',
            ],
            'teach': 'main vanishes as a name. printf as an import does not.',
        },
        {
            'id': 'efq-intel',
            'type': 'mcq',
            'prompt': 'What does objdump -M intel change?',
            'answer': 'The operand order and decoration of the listing, not the bytes.',
            'distractors': [
                'The machine type in the ELF header.',
                'Whether .text is executable.',
                'Which section is disassembled.',
            ],
            'teach': 'AT&T is source then dest. Intel is dest then source. Same instruction.',
        },
    ],
}
