"""vim / neovim, and the `modal-grammar` pack Doom consumes in Phase 4.

**This module carries the grammar for two tools.** Doom runs `(evil
+everywhere)`, so its normal mode *is* this normal mode. Per D9 the grammar is
owned here and the Doom module declares a prereq rather than repeating it, which
is why vim precedes Doom in the phase order despite Doom being the more wanted
module. Anything taught here should be true of both; anything true only of vim
belongs in the last lesson.

**These are the first capture-mode drills.** tmux had to use recall because
tmux eats its own prefix. Nothing eats vim's keys, so here you press `ciw` and
the trainer grades the actual keystroke. This is what capture mode was built
for, and it is where motor memory actually comes from.

The lessons are ordered so that lesson 3 makes the rest guessable. Someone who
holds verb-plus-motion can derive `d$`, `c2w` and `yi(` without being told, and
that is the goal: not thirty memorised bindings, but one rule and a vocabulary.
"""

MODULE = {
    'id': 'vim',
    'title': 'vim / neovim',
    'group': 'Editors',
    'blurb': 'Verbs, motions, text objects, and the grammar that joins them.',
    'context': 'You are in nvim, in normal mode, with a file open and the cursor on a line of text.',
    'needs': ('nvim',),
    'prereqs': [],
    'provides': ['modal-grammar'],
    'adapter': 'nvim',
    'estimate': '4-6 hours',
    'order': 41,

    # ------------------------------------------------------------------
    'lessons': [
        {
            'id': 'vim-inout',
            'title': 'Opening a file, and leaving again',
            'next': 'vim-why',
            'concept': (
                '`:help topic` is the manual, and `:h :w` is how you look up '
                'a command you are about to type. `r` plus a character '
                'replaces the one under the cursor, which is the smallest '
                'edit and the one a first day actually needs.\n\n'
                'The oldest joke about vim is that people cannot work out how '
                'to quit it. It is a joke about a real design decision, and '
                'the answer takes one line, so here it is before anything '
                'else.\n\n'
                '**Type `:wq` and press Enter.** The colon opens a command '
                'line at the bottom of the screen, `w` writes the file, `q` '
                'quits. If the colon does nothing, you are in insert mode: '
                'press Esc first, and Esc is the answer to a great many '
                'things in vim.\n\n'
                'The other three worth knowing on day one. `:q` quits and '
                'refuses if you have unsaved changes, which is a feature. '
                '`:q!` quits and throws those changes away, which is what you '
                'want after an experiment went wrong. `:w` saves without '
                'leaving.\n\n'
                'Opening is the ordinary half: `vim notes.txt` or `nvim '
                'notes.txt` from a shell, and the file does not have to exist '
                'yet. vim opens on an empty buffer and writes it when you '
                'save.\n\n'
                '**Why a command line at all.** Normal mode spends every key '
                'on editing, so there is nothing left for "save this" or '
                '"open that". The colon buys a whole line of typed commands '
                'without spending a single normal-mode key on them. Everything '
                'starting with a colon in this module is that same command '
                'line.\n\n'
                'The next lesson is why that command line has to exist at '
                'all: why vim split typing and commanding onto two modes, '
                'and what "composed" actually means on the keys.'
            ),
            'examples': [
                {
                    'label': 'In, and back out',
                    'code': ('vim notes.txt      open it, from a shell\n'
                             '\n'
                             ':w                 save, stay here\n'
                             ':wq                save and quit\n'
                             ':q                 quit, if nothing is unsaved\n'
                             ':q!                quit, discard my changes\n'
                             'ZZ                 same as :wq, no colon'),
                    'note': 'Every one of these is typed in normal mode. If '
                            'they appear in your text instead, press Esc and '
                            'try again.',
                },
                {
                    'label': 'The one that catches people',
                    'code': ('E37: No write since last change\n'
                             '\n'
                             'vim is refusing to quit, not failing.\n'
                             ':wq  to keep the work\n'
                             ':q!  to abandon it'),
                    'note': 'vim never discards your work without being told '
                            'twice, and the exclamation mark is the second '
                            'telling.',
                },
            ],
            'misconceptions': [
                'Closing the terminal is not the way out. It leaves a swap '
                'file behind, and vim will ask awkward questions about it the '
                'next time you open that file.',
                '`:q` refusing to quit is not an error. It is vim declining '
                'to throw away work you never saved.',
                'The colon is not part of the command. It is how you reach '
                'the command line, and it only works from normal mode.',
            ],
            'try_it': [
                'Open a throwaway file with `vim /tmp/scratch.txt`, type a '
                'few characters, press Esc, and leave with `:wq`. Then open '
                'it again and leave with `:q!`.',
                'Press Esc twice before every colon for a while. It costs '
                'nothing and it removes the entire class of "why is it typing '
                'my command into the file".',
            ],
        },
        {
            'id': 'vim-why',
            'title': 'Why modal editing',
            'next': 'vim-modes',
            'concept': (
                'Modal editing is how you spend every key on a command instead '
                'of a letter. That is why vim shortcuts stay short enough to '
                'compose, instead of living on modifier chords nobody '
                'remembers.\n\n'
                'vim splits the problem in two. In insert mode keys type '
                'letters. In normal mode, where you spend most of your time, '
                'every key is a command. Suddenly you have the entire alphabet '
                'as single-keystroke verbs, your hands never leave the home '
                'row, and commands can be composed.\n\n'
                '**Composed** means a command is built from parts, not looked '
                'up as a chord. `d` means delete and then waits for a motion. '
                '`w` means a word. Together they are `dw`, delete a word. '
                '`i(` is the text inside parentheses, so `d` plus `i(` is '
                '`di(`, delete inside the parens, wherever the cursor is '
                'standing inside them. You did not learn `di(` as a shortcut. '
                'You assembled it, which is why the same `d` works on `$` and '
                'on `i"` and on a search.\n\n'
                'The cost is real: you must always know which mode you are in. '
                'Being in the wrong one is the reason people give up. Type '
                '`:wq` while still in insert and the letters `:wq` appear in '
                'the file. Press `dd` in insert and you type two d\'s. The '
                'screen does not shout. It just takes dictation. Escape twice '
                'is the recovery, and the next lesson is the modes themselves, '
                'because "composed" is useless until you can get back to the '
                'mode that speaks it.\n\n'
                'The payoff is that editing becomes a language you speak rather '
                'than a set of shortcuts you memorise.'
            ),
            'examples': [
                {
                    'label': 'The same edit, two ways',
                    'code': ('other editors:  double-click the word,\n'
                             '                then type the replacement\n'
                             '\n'
                             'vim:            ciw  then type the replacement\n'
                             '                (change inner word)'),
                    'note': 'Three keystrokes, no mouse, and the same three '
                            'keystrokes work inside quotes, parens or tags by '
                            'changing one character.',
                },
                {
                    'label': 'Composition, written out',
                    'code': ('d      delete, then wait\n'
                             'w      a word          ->  dw\n'
                             'i(     inside parens   ->  di(\n'
                             '$      to end of line  ->  d$\n'
                             '\n'
                             'same d, three different objects'),
                    'note': 'The verb does not change. The motion does. That '
                            'is the whole language.',
                },
            ],
            'misconceptions': [
                'vim is not hard because it is arcane. It is hard because you '
                'are learning a grammar, and grammars are useless until they '
                'are complete and then suddenly they are not.',
                'The arrow keys work fine. hjkl is faster once your hands stay '
                'home, but nobody is checking, and refusing to use arrows on '
                'day one just makes day one worse.',
            ],
            'try_it': [
                'Open any file in nvim, press Escape, and press `x` a few '
                'times. You just ran a command with one keystroke.',
            ],
        },
        {
            'id': 'vim-modes',
            'title': 'Modes, and how to get home',
            'next': 'vim-grammar',
            'concept': (
                'Modes are how vim splits typing from commanding. That is why '
                'Escape is the first habit: it is how you get back to the '
                'mode that speaks commands. Four modes '
                'matter. NORMAL is home, and it is where every '
                'command lives. INSERT is where keys type letters. VISUAL '
                'selects text so you can act on the selection. COMMAND-LINE is '
                'the `:` prompt for file and editor operations.\n\n'
                'Escape returns to normal from anywhere. When you are confused, '
                'press Escape twice and you are home. That is the single most '
                'useful habit to build in your first week. Twice, because one '
                'Escape from command-line or from a half-typed chord is '
                'sometimes not enough, and a second Escape from normal mode '
                'does nothing. The cost of the extra press is zero. The cost '
                'of thinking you are in normal when you are in insert is the '
                'file filling up with `dd` and `:wq`.\n\n'
                'Insert mode is not a place to rest. If you are not actively '
                'typing letters, you are in the wrong mode, because every '
                'movement and every edit you make with arrows inside insert '
                'is a command you did not learn. It works. It also trains the '
                'habit that makes vim feel like Notepad with extra steps.\n\n'
                'Notice that the ways into insert mode are already commands '
                'with meaning: `i` inserts before the cursor, `a` appends after '
                'it, `A` appends at end of line, `o` opens a line below. '
                'Choosing the right one saves the movement afterwards. They '
                'are doors, and they are also verbs: `o` is "open a line", '
                'not "go to insert and then press Enter".\n\n'
                'The next lesson is what those verbs do once you are home: '
                'one verb, one motion, and why that pair is the whole editor.'
            ),
            'examples': [
                {
                    'label': 'Six doors into insert mode',
                    'code': ('i   before the cursor\n'
                             'a   after the cursor\n'
                             'I   at the first non-blank of the line\n'
                             'A   at the end of the line\n'
                             'o   open a new line below\n'
                             'O   open a new line above'),
                    'note': 'Capitals are the bigger version of the lowercase: '
                            'a appends here, A appends at the end.',
                },
                {
                    'label': 'Getting out',
                    'code': ('Esc     back to normal from anywhere\n'
                             'C-[     the same key, if Esc is far away\n'
                             ':       into command-line mode\n'
                             'v V C-v charwise, linewise, blockwise visual'),
                    'note': 'C-[ and Esc are literally the same byte, which is '
                            'why both work.',
                },
            ],
            'misconceptions': [
                'Insert mode is not where you should be resting. If you are not '
                'actively typing letters, press Escape.',
                'Pressing `i` to move around and arrow-keying in insert mode is '
                'the classic beginner trap. It works, and it prevents you ever '
                'learning the thing that makes vim worth using.',
                'There is no "save mode". `:w` is a command-line command, and '
                '`:` gets you there from normal mode only.',
            ],
            'try_it': [
                'Open a file and practise the loop: `i`, type a word, Escape, '
                '`A`, type another, Escape. Feel where home is.',
            ],
        },
        {
            'id': 'vim-grammar',
            'title': 'Verb plus motion: the whole idea',
            'next': 'vim-motions',
            'concept': (
                'Verb plus motion is how you name an edit without a separate '
                'shortcut for each one. That is why `dw` and `d$` are the '
                'same `d` finished two different ways.\n\n'
                'A vim command is a VERB followed by a MOTION, and it applies '
                'the verb to the text the motion covers. `d` is delete, `w` '
                'moves a word forward, so `dw` deletes a word. `c` is change, '
                '`$` goes to end of line, so `c$` changes to end of line.\n\n'
                'Watch one built. Cursor on the `f` of `foo(bar)`. Press `d`. '
                'Nothing happens yet: vim is waiting. Press `w`. The word is '
                'gone. Press `u` if you want it back. Now the same `d`, then '
                '`$`: everything from the cursor to the end of the line '
                'is gone instead. You did not switch tools. You finished the '
                'sentence differently.\n\n'
                'The power is that verbs and motions are independent. Learn '
                'four verbs and ten motions and you have forty commands, not '
                'fourteen. You never learned `c$`; you derived it. A count '
                'sits on the verb, or on the motion, and multiplies whichever '
                'it sits on: `3dw` is three times "delete a word", which is '
                'the next-but-one lesson.\n\n'
                'A verb typed twice acts on the whole line: `dd` deletes a '
                'line, `yy` yanks one, `cc` changes one. That is the only '
                'irregular verb form in the language.\n\n'
                'The next lesson is the motion half of the pair, because a '
                'verb without a good motion is just `x` with extra steps.'
            ),
            'examples': [
                {
                    'label': 'One-key commands that are not verb plus motion',
                    'code': 'x    delete the character under the cursor\nJ    join this line and the next into one\n~    swap the case of this character\np    put what you last deleted, after the cursor',
                    'note': 'A handful of commands are just verbs with the object built in. J is the one people miss for years and then use every day.',
                },
                {
                    'label': 'Four verbs',
                    'code': ('d   delete\n'
                             'c   change (delete, then enter insert mode)\n'
                             'y   yank (copy)\n'
                             '>   indent'),
                    'note': 'These four cover most editing. `c` is `d` that '
                            'leaves you typing.',
                },
                {
                    'label': 'Multiply them by motions',
                    'code': ('dw   delete to the start of the next word\n'
                             'd$   delete to the end of the line\n'
                             'dgg  delete to the top of the file\n'
                             'cw   change a word\n'
                             'y}   yank to the end of the paragraph\n'
                             '>ap  indent a whole paragraph'),
                    'note': 'None of these need memorising once you have the '
                            'rule. Read them as sentences.',
                },
            ],
            'misconceptions': [
                'The order is verb then motion, never the reverse. `wd` is '
                '"move a word, then wait for a motion for delete".',
                '`x` and `D` and `C` look like exceptions but are just '
                'shorthand: `x` is `dl`, `D` is `d$`, `C` is `c$`.',
                'Not every key is a verb. Pressing `d` and then something that '
                'is not a motion cancels harmlessly; Escape always backs out.',
            ],
            'try_it': [
                'Without looking anything up, work out what `y$`, `c0` and '
                '`dG` do. Then try them.',
            ],
        },
        {
            'id': 'vim-motions',
            'title': 'The motion vocabulary',
            'next': 'vim-textobjects',
            'concept': (
                'The last lesson gave you a verb waiting for a motion. '
                'Motions are where the leverage is, because every motion you '
                'learn multiplies against every verb you already have. They '
                'also work on their own, as movement.\n\n'
                'Learn them in three groups. Within a line: `0` `^` `$` for the '
                'ends, `w` `b` `e` for words, `f` and `t` to jump to a '
                'character. Within a file: `gg` `G` for the ends, `{` `}` for '
                'paragraphs, `/` to search. Structural: `%` jumps between '
                'matching brackets.\n\n'
                'Motions are inclusive or exclusive, and that is the only '
                'subtlety worth having on day one. An exclusive motion stops '
                'before the destination, so `dw` deletes up to the next word '
                'and leaves that word\'s first character. An inclusive motion '
                'takes the destination too, so `d$` deletes through the last '
                'character of the line. That is why `dw` does not eat the next '
                'word and `d$` does not leave the last character sitting there. '
                'You do not need the full table. You need to expect `d$` and '
                '`dw` to feel slightly different, because they are.\n\n'
                '`f` deserves special attention. `fx` jumps to the next `x` on '
                'this line, so `dfx` deletes up to and including it. `t` is the '
                'same but stops just before, which is usually what you want '
                'when deleting up to a comma or a bracket.\n\n'
                'The next lesson is the thing that is better than a motion: '
                'a text object, which names a region wherever you are standing '
                'inside it.'
            ),
            'examples': [
                {
                    'label': 'Within a line',
                    'code': ('0    first column\n'
                             '^    first non-blank character\n'
                             '$    end of line\n'
                             'w    start of next word      b    back a word\n'
                             'e    end of this word\n'
                             'fx   forward to the next x   Fx   backwards\n'
                             'tx   forward to just before x'),
                    'note': '; repeats the last f or t, and , repeats it '
                            'backwards.',
                },
                {
                    'label': 'Across a file',
                    'code': ('gg   first line          G     last line\n'
                             '42G  line 42            {  }   paragraphs\n'
                             '%    matching bracket   /foo   search forward\n'
                             'C-o  jump back          C-i    jump forward'),
                    'note': 'C-o and C-i walk the jump list, which is how you '
                            'get back after a search sends you somewhere.',
                },
            ],
            'misconceptions': [
                '`w` and `e` are not the same. `w` lands on the start of the '
                'next word, `e` on the end of this one, and `dw` versus `de` '
                'differ by exactly the trailing space.',
                '`$` is a motion, not a key that means end. `d$` deletes to the '
                'end, `y$` yanks to it.',
                '`C-i` and `Tab` are the same byte in a terminal, so a terminal '
                'that does not speak the modern keyboard protocol cannot tell '
                'them apart. This is a terminal limitation, not a vim one.',
            ],
            'try_it': [
                'Open a file with brackets in it. Put the cursor on one and '
                'press `%`. Then try `d%`.',
            ],
        },
        {
            'id': 'vim-textobjects',
            'title': 'Text objects: the multiplier',
            'next': 'vim-visual',
            'concept': (
                'The last lesson ran from the cursor to a destination. '
                'Motions run from the cursor to somewhere. Text objects are '
                'different: they name a region regardless of where in it you '
                'are standing. That difference is what makes them so much '
                'better.\n\n'
                'A text object is `i` or `a` followed by the kind of thing. '
                '`iw` is the inner word, `aw` is a word plus its trailing '
                'space. `i(` is what is inside the parentheses, `a(` includes '
                'the parentheses themselves. `i"` `it` `ip` follow the same '
                'pattern for quotes, tags and paragraphs.\n\n'
                'The key insight is that you do not need to position first. '
                'Anywhere inside the parens, `ci(` changes their contents. '
                'Compare `cw`, which only changes from the cursor to the end of '
                'the word and so gives a different result depending on where '
                'you happened to be standing.\n\n'
                'On `foo(bar, baz)` with the cursor on `bar`, `di(` deletes '
                '`bar, baz` and leaves `foo()`. `da(` deletes the parens too '
                'and leaves `foo`. The same pair on quotes: `di"` inside '
                '`"hello"` leaves the quotes, `da"` takes them. The failure '
                'is `di"` when the cursor is not inside a pair: vim beeps, '
                'or in nvim does nothing, because there is no object to '
                'name. People then mash `di"` on the next set of quotes and '
                'wonder why the first string is untouched.\n\n'
                'The next lesson is the number that multiplies any of this: '
                'where a count sits, and why `3dw` and `d3w` are the same '
                'until they are not.'
            ),
            'examples': [
                {
                    'label': 'inner versus around',
                    'code': ('foo(bar, baz)      cursor anywhere inside\n'
                             '\n'
                             'ci(   ->  foo()            just the contents\n'
                             'ca(   ->  foo             the parens too\n'
                             '\n'
                             '"hello there"      cursor anywhere inside\n'
                             'ci"   ->  ""'),
                    'note': 'i is "inner", a is "around" or "a whole".',
                },
                {
                    'label': 'The objects worth knowing',
                    'code': ('iw aw   word\n'
                             'i( a(   parentheses, also i) and ib\n'
                             'i{ a{   braces, also iB\n'
                             'i[ a[   brackets\n'
                             'i" a"   double quotes    i\' a\'   single\n'
                             'it at   an XML or HTML tag\n'
                             'ip ap   paragraph'),
                    'note': 'Every one of these composes with every verb: yi(, '
                            'da{, >ip.',
                },
            ],
            'misconceptions': [
                '`ciw` and `cw` are not interchangeable. With the cursor '
                'mid-word, `cw` changes only the rest of the word while `ciw` '
                'changes all of it. `ciw` is almost always the one you meant.',
                'Text objects only work with a verb in front. `iw` on its own '
                'in normal mode does nothing useful.',
                '`aw` includes the trailing space, which is why `daw` leaves a '
                'clean sentence and `diw` leaves a double space.',
            ],
            'try_it': [
                'Write a line like `print("hello", name)` and try `ci"`, then '
                'undo, then `ci(`, then undo, then `caw` on a word.',
            ],
        },
        {
            'id': 'vim-visual',
            'title': 'Visual mode is a motion you can see',
            'next': 'vim-counts',
            'concept': (
                'Text objects name a region you cannot see until the edit '
                'happens. Visual mode is the same idea with the lights on: '
                'you select first, then apply the operator.\n\n'
                '`v` selects by character. `V` selects by line. `C-v` selects '
                'a block, a rectangle of columns. The selection is a motion. '
                '`d`, `c`, `y`, `>` all apply to it. `o` jumps to the other '
                'end of the selection so you can adjust it without starting '
                'over.\n\n'
                'When the region is irregular, or you need to see it before '
                'you cut, a text object is the wrong tool. Visual is the '
                'right one. It is not a place to stay. Escape when the edit '
                'is done.\n\n'
                'Block visual is the one that pays for itself on code. `C-v` '
                'then `I` or `A` edits a column: comment four lines, or put '
                'the same prefix on each. A visual change repeats poorly '
                'with the dot. Prefer an operator plus a text object when '
                'you will walk the file doing the same edit.\n\n'
                'The next lesson is counts: multiplying a motion you already '
                'know, now that you can also see a region.'
            ),
            'examples': [
                {
                    'label': 'See it, then cut it',
                    'code': ('v      character visual\n'
                             'V      line visual\n'
                             'C-v    block visual\n'
                             'o      other end of the selection\n'
                             'd c y  operators, same as always\n'
                             'gv     reselect the last visual'),
                    'note': '`gv` is how you recover a selection you just '
                            'operated on and wish you had kept.',
                },
                {
                    'label': 'A column of comments',
                    'code': ('C-v j j     three lines, one column\n'
                             'I# Space    insert at the start of the block\n'
                             'Esc         applies to every selected line'),
                    'note': '`I` and `A` in block visual are insert and '
                            'append for the whole column. They fire on Esc.',
                },
            ],
            'misconceptions': [
                'Visual is not a mode you write in. It is a motion you can '
                'see. Escape when the region is right, after the operator.',
                'Dot repeats the last change, not the last selection. A '
                'visual edit of a ragged region will not walk the file the '
                'way `ci"` will.',
            ],
            'try_it': [
                'Select three lines with V, yank them, then gv and delete. '
                'Then try C-v on a column and I to prefix it.',
            ],
        },
        {
            'id': 'vim-counts',
            'title': 'Counts, and where they go',
            'concept': (
                'A count is how you multiply a command you already know. That '
                'is why `3dd` is three lines and `d3w` is three words, '
                'without a new key. `3dd` '
                'deletes three lines, `2w` moves two words, `5x` deletes five '
                'characters.\n\n'
                'The count can go before the verb or between the verb and the '
                'motion, and both mean the same thing: `d2w` and `2dw` both '
                'delete two words. Pick whichever you can type faster. The '
                'count binds to whichever piece it sits on: `3dw` is "three '
                'times, delete a word", `d3w` is "delete, then a 3-word '
                'motion". For `d` and `w` those are the same region. They '
                'stop being the same when the verb itself repeats, or when '
                'the motion is something like `f` that already takes a '
                'character: `d3fx` deletes through the third `x`, because '
                'the `3` belongs to `fx`.\n\n'
                'The failure is counting what you cannot see. `12dd` on a '
                'guess deletes twelve lines whether or not that was the '
                'paragraph. A text object or a search motion is almost '
                'always the better count.\n\n'
                'Counts also work with `.` and with macros, which is where they '
                'earn their keep: record a fix once and apply it twenty times '
                'with `20@a`. Search is the motion that usually replaces the '
                'count, and it is the next lesson.'
            ),
            'examples': [
                {
                    'label': 'Counting',
                    'code': ('3dd    delete three lines\n'
                             'd2w    delete two words\n'
                             '2dw    the same thing\n'
                             '5j     down five lines\n'
                             '3fx    to the third x on this line\n'
                             '42G    go to line 42'),
                    'note': 'A count before G is a line number rather than a '
                            'multiplier, which is the one exception.',
                },
                {
                    'label': 'Where the count sits',
                    'code': ('3dw     three times: delete a word\n'
                             'd3w     delete a 3-word motion\n'
                             '         same region, for this pair\n'
                             '\n'
                             'd3fx    delete through the third x\n'
                             '         3 belongs to fx, not to d'),
                    'note': 'Read the number as attaching to the next piece. '
                            'That is why 42G is a line number.',
                },
            ],
            'misconceptions': [
                'Counting is often slower than a better motion. `d}` beats '
                'counting the lines in a paragraph, and `dap` beats both.',
                'Counting past what you can see is guessing. If you are '
                'squinting to count lines, you want a text object or a search '
                'motion instead.',
            ],
            'try_it': [
                'Delete three lines two ways: `3dd`, undo, then `d3j`. Notice '
                'the second one takes four lines, not three.',
            ],
            'next': 'vim-search',
        },
        {
            'id': 'vim-search',
            'title': 'Search, and substitute',
            'next': 'vim-repeat',
            'concept': (
                'The last lesson multiplied a motion by a number. Searching '
                'is how you move a long way without counting, and it '
                'is also a motion, so it composes with verbs like everything '
                'else.\n\n'
                '`/pattern` searches forward, `?pattern` searches backward, and '
                'Enter jumps to the first match. `n` repeats the search in the '
                'same direction, `N` in the opposite one. The pair you will '
                'reach for constantly is `*` and `#`: they search for the word '
                'under the cursor, forward and backward, with no typing at all. '
                '`*` then `cgn` then `.` is one of the fastest rename loops '
                'there is.\n\n'
                'Because a search is a motion, `d/foo` deletes from the cursor '
                'up to the next `foo`, and `y?bar` yanks back to the previous '
                '`bar`. Highlighting stays on the screen after a search; `:noh` '
                'clears it, and `set incsearch hlsearch` are the two settings '
                'that make search feel alive.\n\n'
                'Substitution is the other half. `:s/old/new/` changes the '
                'first `old` on the current line, `:s/old/new/g` changes every '
                'one on the line, and `:%s/old/new/g` changes every one in the '
                'file. Add the `c` flag, `:%s/old/new/gc`, and vim asks about '
                'each match, which is the safe way to do a big replace. The '
                'left half is a regex, so everything the regex module teaches '
                'applies here, and `\\1` on the right pastes back a group you '
                'captured on the left.'
            ),
            'examples': [
                {
                    'label': 'Typing a search, key by key',
                    'code': '/error<Enter>     jump to the next "error"\n\n/  opens the search prompt\nerror  is typed into it\nRET  (Enter) runs it, n and N repeat',
                    'note': 'The slash is a mode of its own: nothing happens until you press Enter, so Esc backs out of a search you started by accident.',
                },
                {
                    'label': 'Searching and moving',
                    'code': ('/error       forward to the next "error"\n'
                             '?error       backward to the previous one\n'
                             'n   N        repeat, same and opposite direction\n'
                             '*   #        search the word under the cursor\n'
                             'd/;          delete up to the next semicolon\n'
                             ':noh         turn off the leftover highlight'),
                    'note': 'A search is a motion, so it works after d, c and y '
                            'exactly like w or $.',
                },
                {
                    'label': 'Substitution, widening the range',
                    'code': (':s/old/new/      first on this line\n'
                             ':s/old/new/g     all on this line\n'
                             ':%s/old/new/g    all in the file\n'
                             ':%s/old/new/gc   all in the file, asking each\n'
                             ":'<,'>s/old/new/g   only the visual selection\n"
                             ':%s/\\(\\w\\+\\)@/\\1 at /   reuse a captured group'),
                    'note': 'The range is before the s, the flags are after the '
                            'last slash. c asks, g means every match not just '
                            'the first.',
                },
            ],
            'misconceptions': [
                'Without `g`, substitute changes only the FIRST match on each '
                'line, not the whole line. That default surprises everyone once.',
                '`:s` with no range is the current line only, so a `:%s` that '
                'seems to do nothing is often a `:s` you forgot the `%` on.',
                'The left side of a substitution is a regex in vim\'s own '
                'dialect, where `(` is literal and `\\(` groups. `\\v` at the '
                'front switches to the sane spelling, exactly as in the regex '
                'module.',
                'A blind `:%s///g` is not reviewable and not repeatable with '
                '`.`. When you want to see each change, use `gc`, or use the '
                'n-dot loop from the next lesson instead.',
            ],
            'try_it': [
                'Put the cursor on a word that repeats, press `*`, then `n` a '
                'few times. Then run `:%s/that-word/OTHER/gc` and answer the '
                'prompts.',
            ],
        },
        {
            'id': 'vim-repeat',
            'title': 'Dot, undo, and the redo tree',
            'next': 'vim-registers',
            'concept': (
                'The last lesson left you with `n` walking matches. `.` '
                'repeats your last change, and it is the most valuable key '
                'in vim. Make an edit once, move somewhere else, press `.` and '
                'it happens again.\n\n'
                'This changes how you should make edits. `ciwfoo` then Escape '
                'is repeatable with `.` anywhere else in the file. Doing the '
                'same thing with a search-and-replace is not repeatable and not '
                'reviewable. The habit worth building is: make the change '
                'small and repeatable, then walk it with `n` and `.`.\n\n'
                '`.` repeats the last *change*, not the last motion. Moving '
                'with `w` or searching with `n` does not update it. That is '
                'why the n-dot loop works: `n` moves, `.` repeats the edit '
                'you already made. If you insert a small extra delete in the '
                'middle, `.` now repeats that delete, and the rename loop is '
                'gone. The failure looks like "dot is broken". It is doing '
                'exactly the last change.\n\n'
                '`u` undoes and `C-r` redoes. Undo in vim is per change rather '
                'than per keystroke, so one `u` removes the whole of an insert '
                'session. `C-r` walks forward along that same chain. vim\'s '
                'undo is a tree if you undo and then make a new edit, which '
                'is why `:undolist` exists, but `u` and `C-r` are the whole '
                'habit for the first month.\n\n'
                'The next lesson is where the text you deleted actually went, '
                'because `p` does not always paste what you think you yanked.'
            ),
            'examples': [
                {
                    'label': 'The n-dot loop',
                    'code': ('/oldname       search for the thing\n'
                             'ciwnewname Esc change the first one\n'
                             'n              next match\n'
                             '.              same change again\n'
                             'n .  n .       and so on'),
                    'note': 'Reviewable, interruptible, and it skips the ones '
                            'you do not want. A blind :%s cannot do that.',
                },
                {
                    'label': 'What dot repeats',
                    'code': ('ciwfoo Esc     last change is "replace word"\n'
                             'n              motion, dot unchanged\n'
                             '.              replace this word too\n'
                             'x              last change is now "delete char"\n'
                             '.              deletes a character, not a word'),
                    'note': 'Dot is a recording of the last edit. Motions '
                            'are not edits.',
                },
            ],
            'misconceptions': [
                '`.` repeats the last CHANGE, not the last motion or command. '
                'Moving around does not disturb it.',
                'A change made in visual mode repeats poorly. Prefer an '
                'operator plus a text object when you want `.` to work.',
            ],
            'try_it': [
                'Find a word that appears several times in a file. Change the '
                'first with `ciw`, then use `n` and `.` for the rest.',
            ],
        },
        {
            'id': 'vim-registers',
            'title': 'Registers: where deleted text goes',
            'next': 'vim-macros',
            'concept': (
                'The last lesson repeated a change. This one is where the '
                'text from that change went. Nothing you delete is lost. '
                'Deletes and yanks go into '
                'registers, and `p` pastes from the unnamed register, which is '
                'whatever you last cut or copied.\n\n'
                'Named registers let you keep several things at once. `"ayy` '
                'yanks a line into register a, `"ap` pastes it back. The '
                'numbered registers hold your recent deletes automatically, so '
                '`"1p` pastes your last delete and `"2p` the one before it.\n\n'
                'The unnamed register is overwritten by the next delete. That '
                'is the trap. `yy` to copy a line, `dd` to remove a different '
                'one, `p` to paste: you get the deleted line, not the yanked '
                'one. The yank is still in `"0`, the yank register, which '
                'deletes do not touch. `"0p` pastes what you meant. People '
                'swear vim ate their copy. It filed it.\n\n'
                'The one to remember on a desktop is `"+`, the system '
                'clipboard. `"+y` copies out to other applications and `"+p` '
                'pastes in.\n\n'
                'A register can also hold a sequence of keys. That is a '
                'macro, and it is the next lesson.'
            ),
            'examples': [
                {
                    'label': 'Using registers',
                    'code': ('yy    yank a line into the unnamed register\n'
                             'p     paste it after the cursor\n'
                             'P     paste it before\n'
                             '"ayy  yank into register a\n'
                             '"ap   paste from register a\n'
                             '"+y   yank to the system clipboard\n'
                             ':reg  show what is in every register'),
                    'note': ':reg is the way to find the thing you deleted five '
                            'minutes ago and now want back.',
                },
                {
                    'label': 'The yank that seemed to vanish',
                    'code': ('yy      unnamed and "0 now hold the line\n'
                             'dd      unnamed now holds the delete\n'
                             '         "0 is unchanged\n'
                             'p       pastes the delete\n'
                             '"0p     pastes the yank'),
                    'note': 'Deletes clobber the unnamed register. They do '
                            'not clobber "0.',
                },
            ],
            'misconceptions': [
                'Deleting overwrites the unnamed register, so yank-then-delete-'
                'then-paste pastes the deleted text, not the yanked text. Use a '
                'named register when it matters.',
                '`"+` may not exist. It needs clipboard support compiled in; '
                'check with `:echo has("clipboard")`.',
            ],
            'try_it': [
                'Yank a line with `yy`, delete a different one with `dd`, then '
                'press `p`. Work out why you got what you got.',
            ],
        },
        {
            'id': 'vim-macros',
            'title': 'Macros: recorded keystrokes',
            'next': 'vim-buffers',
            'concept': (
                'A macro is how you replay a sequence of keys you already '
                'know. That is why a fix you can do once can run on the next '
                'twenty lines. `qa` starts recording into register a, `q` '
                'stops, and `@a` plays it back. `@@` replays the last macro.\n\n'
                'Because they are just keystrokes, everything you already know '
                'applies. A macro that ends by moving to the next line can be '
                'run with a count: `20@a` applies your fix twenty times.\n\n'
                'The discipline that makes macros reliable is to start from a '
                'known position and end in the equivalent position on the next '
                'target. Begin with `0` or `^`, end with `j`, and it will '
                'replay cleanly.\n\n'
                'Recorded in the wrong mode, a macro is a recording of your '
                'mistake. Start `qa` while still in insert and you capture '
                'letters, not commands. The playback then types `j` into the '
                'file instead of moving down. Escape first, then `qa`. If a '
                'macro is already wrong, `"ap` pastes it as text, you edit '
                'the keys, and `"ay$` yanks the corrected line back into '
                'register a. That is the edit-the-register trick, and it is '
                'faster than re-recording a twelve-keystroke sequence.\n\n'
                'The last lesson is vim-only: buffers, windows and tabs, '
                'which Doom organises differently on purpose.'
            ),
            'examples': [
                {
                    'label': 'Record, then multiply',
                    'code': ('qa        start recording into a\n'
                             '^I- Esc   go home, prepend "- "\n'
                             'j         move to the next line\n'
                             'q         stop recording\n'
                             '20@a      do it to the next twenty lines'),
                    'note': 'This is the fastest way to turn a pasted list into '
                            'a markdown list, and it took one recording.',
                },
                {
                    'label': 'Edit a macro as text',
                    'code': ('"ap      paste register a as a line of keys\n'
                             '          edit the line like any other\n'
                             '"ay$     yank it back into a\n'
                             '@a       play the corrected version'),
                    'note': 'A macro register is just a register. That is why '
                            'this works.',
                },
            ],
            'misconceptions': [
                'A macro recorded from an arbitrary cursor position will drift. '
                'Anchor it with `0`, `^` or a search.',
                'Macros stop at the first error, which is a feature: `20@a` on '
                'a fifteen-line block stops at fifteen rather than mangling '
                'what follows.',
                'A macro register is just a register, so `"ap` pastes your '
                'macro as text and you can edit it and yank it back.',
            ],
            'try_it': [
                'Paste ten lines of anything. Record a macro that adds a comma '
                'to the end of a line and moves down, then run it nine times.',
            ],
        },
        {
            'id': 'vim-buffers',
            'title': 'Buffers, windows and tabs',
            'concept': (
                'A buffer is how vim holds a file in memory. That is why you '
                'switch files without opening a new tab. Doom organises this '
                'layer differently, so everything before this transfers and '
                'this does not.\n\n'
                'A BUFFER is a file in memory. A WINDOW is a viewport onto a '
                'buffer. A TAB is a layout of windows. The confusion people '
                'bring from other editors is expecting tabs to be files, and in '
                'vim they are not: tabs are workspace arrangements, and buffers '
                'are the files. Chrome tabs are files. vim tabs are "the split '
                'layout I want for this task". Using a tab per file is how you '
                'end up with twenty tabs and no idea which buffer is where.\n\n'
                'Most of the time you want buffers, not tabs. `:e file` opens '
                'one, `:ls` lists them, `:b name` switches by partial name. '
                '`C-^` toggles the previous buffer, which is the buffer-level '
                'alt-tab. Closing a window with `C-w q` does not close the '
                'buffer: `:ls` still shows it, and `:b` brings it back. '
                '`:bd` is what forgets the file.\n\n'
                'The Doom module starts where this one stops. Its `SPC b` '
                'tree and its workspaces replace most of this lesson, and '
                'the grammar from the earlier lessons is what you will still '
                'be speaking inside them.'
            ),
            'examples': [
                {
                    'label': 'Buffers',
                    'code': (':e path/to/file   open a file into a buffer\n'
                             ':ls               list buffers\n'
                             ':b partial        switch by partial name\n'
                             ':bd               close the buffer\n'
                             'C-^               toggle to the previous buffer'),
                    'note': 'C-^ is the buffer-level alt-tab and is worth a '
                            'binding in muscle memory.',
                },
                {
                    'label': 'Windows',
                    'code': ('C-w s   split horizontally\n'
                             'C-w v   split vertically\n'
                             'C-w h j k l   move between windows\n'
                             'C-w q   close this window\n'
                             'C-w o   close every other window'),
                    'note': 'Note the shape of this: a prefix, then a command '
                            'key. Exactly like tmux, for exactly the same '
                            'reason.',
                },
            ],
            'misconceptions': [
                'Closing a window does not close the buffer. The file is still '
                'open; `:ls` will show it.',
                'Tabs are not files. A tab holding one window holding one '
                'buffer looks like a file tab and is not one.',
                'This lesson is where Doom diverges. Its workspaces and its '
                '`SPC b` tree replace most of this, so learn it for vim and '
                'expect Doom to differ.',
            ],
            'try_it': [
                'Open two files with `:e`, list them with `:ls`, and toggle '
                'between them with `C-^`.',
            ],
        },
    ],

    # ------------------------------------------------------------------
    # Drill: capture type. Nothing eats vim's keys, so these grade the
    # actual keystroke rather than a typed description of it.
    # ------------------------------------------------------------------
    'drills': [
        # verbs and the line form
        {'id': 'vim-r', 'type': 'keys', 'keys': ['r', 'x'],
         'prompt': 'Replace the character under the cursor with x.',
         'teach': 'r is one character, then you are still in normal mode.'},
        {'id': 'vim-help', 'type': 'command',
         'answer': ':help :w',
         'accepts': [':h :w'],
         'prompt': 'Look up the :w command in vim help.',
         'teach': ':help topic. :h is the short form.'},
        {'id': 'vim-dd', 'type': 'keys', 'keys': ['d', 'd'],
         'prompt': 'Delete the whole line the cursor is on.',
         'teach': 'A verb doubled acts on the line. The same rule gives yy '
                  'and cc.'},
        {'id': 'vim-yy', 'type': 'keys', 'keys': ['y', 'y'],
         'prompt': 'Yank (copy) the current line.',
         'teach': 'Yank is vim for copy. It goes to the unnamed register.'},
        {'id': 'vim-cc', 'type': 'keys', 'keys': ['c', 'c'],
         'prompt': 'Change the whole line, leaving you in insert mode.',
         'teach': 'c is d that leaves you typing. cc clears the line and '
                  'starts insert.'},

        # verb plus motion
        {'id': 'vim-dw', 'type': 'keys', 'keys': ['d', 'w'],
         'prompt': 'Delete from the cursor to the start of the next word.',
         'teach': 'The canonical verb-plus-motion. Read it as a sentence: '
                  'delete word.'},
        {'id': 'vim-cw', 'type': 'keys', 'keys': ['c', 'w'],
         'prompt': 'Change from the cursor to the end of this word.',
         'teach': 'Note this is not the whole word if you are standing in the '
                  'middle of it. That is what ciw is for.'},
        {'id': 'vim-d-dollar', 'type': 'keys', 'keys': ['d', '$'],
         'prompt': 'Delete from the cursor to the end of the line.',
         'teach': 'D is shorthand for exactly this.'},
        {'id': 'vim-y-dollar', 'type': 'keys', 'keys': ['y', '$'],
         'prompt': 'Yank from the cursor to the end of the line.',
         'teach': 'You never learned this one. You derived it from y and $.'},
        {'id': 'vim-dgg', 'type': 'keys', 'keys': ['d', 'g', 'g'],
         'prompt': 'Delete from the cursor to the top of the file.',
         'teach': 'Motions that span the file compose just like the small '
                  'ones.'},

        # text objects
        {'id': 'vim-ciw', 'type': 'keys', 'keys': ['c', 'i', 'w'],
         'prompt': 'Change the whole word the cursor is inside.',
         'teach': 'The most useful three keys in vim. Works from anywhere in '
                  'the word, unlike cw.'},
        {'id': 'vim-daw', 'type': 'keys', 'keys': ['d', 'a', 'w'],
         'prompt': 'Delete the word and its trailing space.',
         'teach': 'a means around. daw leaves a clean sentence where diw '
                  'leaves a double space.'},
        {'id': 'vim-ci-paren', 'type': 'keys', 'keys': ['c', 'i', '('],
         'prompt': 'Change everything inside the parentheses.',
         'teach': 'Works from anywhere inside them. You do not have to '
                  'position on a bracket first.'},
        {'id': 'vim-ca-quote', 'type': 'keys', 'keys': ['c', 'a', '"'],
         'prompt': 'Change the quoted string including the quotes.',
         'teach': 'i for inner keeps the quotes, a for around takes them too.'},
        {'id': 'vim-yi-brace', 'type': 'keys', 'keys': ['y', 'i', '{'],
         'prompt': 'Yank everything inside the braces.',
         'teach': 'Every verb composes with every object. This one you '
                  'derived.'},
        {'id': 'vim-dap', 'type': 'keys', 'keys': ['d', 'a', 'p'],
         'prompt': 'Delete the whole paragraph, including its blank line.',
         'teach': 'Beats counting lines, and it survives the paragraph '
                  'changing length.'},

        # motions on their own
        {'id': 'vim-w', 'type': 'keys', 'keys': ['w'],
         'prompt': 'Move to the start of the next word.',
         'teach': 'w forward, b back, e to the end of this word.'},
        {'id': 'vim-b', 'type': 'keys', 'keys': ['b'],
         'prompt': 'Move back to the start of the previous word.',
         'teach': 'The pair to w. Capital B moves by WORDS, which are split '
                  'only on whitespace, so it treats foo.bar(baz) as one '
                  'thing.'},
        {'id': 'vim-e', 'type': 'keys', 'keys': ['e'],
         'prompt': 'Move to the end of the current word.',
         'teach': 'The difference between w and e is exactly the trailing '
                  'space, which is why dw and de differ.'},
        {'id': 'vim-caret', 'type': 'keys', 'keys': ['^'],
         'prompt': 'Move to the first non-blank character of the line.',
         'teach': '0 goes to column one, ^ skips the indentation. On indented '
                  'code ^ is almost always the one you want.'},
        {'id': 'vim-dollar', 'type': 'keys', 'keys': ['$'],
         'prompt': 'Move to the end of the line.',
         'teach': 'Same character the shell and regex use for end. As a '
                  'motion it composes: d$ deletes to the end of the line, and '
                  'D is that.'},
        {'id': 'vim-gg', 'type': 'keys', 'keys': ['g', 'g'],
         'prompt': 'Jump to the first line of the file.',
         'teach': 'G alone goes to the last line, and a count goes to a line: '
                  '42G or 42gg. Line numbers make this the fastest way around '
                  'a file.'},
        {'id': 'vim-G', 'type': 'keys', 'keys': ['G'],
         'prompt': 'Jump to the last line of the file.',
         'teach': 'With a count in front it goes to that line number instead, '
                  'which is the one place a count is not a multiplier.'},
        {'id': 'vim-f', 'type': 'keys', 'keys': ['f', ','],
         'prompt': 'Jump forward to the next comma on this line.',
         'teach': 'f finds and lands on it, t stops just before. df, deletes '
                  'up to and including the comma.'},
        {'id': 'vim-percent', 'type': 'keys', 'keys': ['%'],
         'prompt': 'Jump to the bracket matching the one under the cursor.',
         'teach': 'd% deletes the whole bracketed region, which is often '
                  'faster than reaching for a text object.'},
        {'id': 'vim-jumpback', 'type': 'keys', 'keys': ['C-o'],
         'prompt': 'Jump back to where you were before the last jump.',
         'teach': 'C-o walks back through the jump list, C-i walks forward. '
                  'C-i and Tab are the same byte in a terminal, which is why '
                  'the forward one sometimes appears not to work.'},

        # entering insert mode
        {'id': 'vim-A', 'type': 'keys', 'keys': ['A'],
         'prompt': 'Start typing at the end of the current line.',
         'teach': 'a appends here, A appends at the end. Capitals are the '
                  'bigger version.'},
        {'id': 'vim-I', 'type': 'keys', 'keys': ['I'],
         'prompt': 'Start typing at the first non-blank of the current line.',
         'teach': 'The tall siblings: I inserts at the first non-blank, A '
                  'appends at the end of the line. Lowercase i and a work '
                  'from the cursor.'},
        {'id': 'vim-o', 'type': 'keys', 'keys': ['o'],
         'prompt': 'Open a new line below and start typing on it.',
         'teach': 'O opens above. Neither needs you to move first.'},

        # editing and repeat
        {'id': 'vim-p', 'type': 'keys', 'keys': ['p'],
         'prompt': 'Paste what you last yanked or deleted, after the cursor.',
         'teach': 'P pastes before. For a whole line, p puts it on the line '
                  'below.'},
        {'id': 'vim-dot', 'type': 'keys', 'keys': ['.'],
         'prompt': 'Repeat your last change.',
         'teach': 'The highest-value key in vim. Pair it with n to walk a '
                  'file making the same edit deliberately.'},
        {'id': 'vim-undo', 'type': 'keys', 'keys': ['u'],
         'prompt': 'Undo the last change.',
         'teach': 'Repeat it to keep undoing; C-r redoes. Each insert-mode '
                  'session counts as one change, however much you typed in '
                  'it.'},
        {'id': 'vim-redo', 'type': 'keys', 'keys': ['C-r'],
         'prompt': 'Redo the change you just undid.',
         'teach': 'Note it is a control chord rather than a letter, unlike '
                  'almost everything else in normal mode.'},
        {'id': 'vim-J', 'type': 'keys', 'keys': ['J'],
         'prompt': 'Join the next line onto this one.',
         'teach': 'It inserts a space and removes the indentation. gJ joins '
                  'without touching whitespace.'},

        # counts, visual, macros
        {'id': 'vim-3dd', 'type': 'keys', 'keys': ['3', 'd', 'd'],
         'prompt': 'Delete three lines.',
         'teach': 'The count can also go inside: d2j is the same three lines, '
                  'but d3j takes four, which is worth trying once.'},
        {'id': 'vim-d2w', 'type': 'keys', 'keys': ['d', '2', 'w'],
         'prompt': 'Delete two words, with the count between verb and motion.',
         'teach': '2dw means the same thing. Type whichever is faster for '
                  'you.'},
        {'id': 'vim-viw', 'type': 'keys', 'keys': ['v', 'i', 'w'],
         'prompt': 'Visually select the word the cursor is inside.',
         'teach': 'Text objects work in visual mode too, which is how you see '
                  'what an object covers before acting on it.'},
        {'id': 'vim-V', 'type': 'keys', 'keys': ['V'],
         'prompt': 'Start a linewise visual selection.',
         'teach': 'Lowercase v selects by character, capital V by line, C-v '
                  'by rectangle. Then operators like d and y act on the '
                  'selection.'},
        {'id': 'vim-record', 'type': 'keys', 'keys': ['q', 'a'],
         'prompt': 'Start recording a macro into register a.',
         'teach': 'q again stops. The register is an ordinary register, so '
                  '"ap pastes the macro out as editable text.'},
        {'id': 'vim-play', 'type': 'keys', 'keys': ['@', 'a'],
         'prompt': 'Play back the macro in register a.',
         'teach': '@@ repeats the last macro, and a count multiplies: 20@a.'},
        {'id': 'vim-clipboard', 'type': 'keys', 'keys': ['"', '+', 'y', 'y'],
         'prompt': 'Yank the current line to the system clipboard.',
         'teach': 'The " prefix picks a register. + is the system clipboard '
                  'on a desktop.'},

        # search: normal-mode keys, captured
        {'id': 'vim-star', 'type': 'keys', 'keys': ['*'],
         'prompt': 'Search for the next occurrence of the word under the '
                   'cursor.',
         'teach': '# searches backward. This needs no typing, which is why '
                  '* then cgn then dot is the fastest rename loop there is.'},
        {'id': 'vim-n', 'type': 'keys', 'keys': ['n'],
         'prompt': 'Jump to the next match of the last search.',
         'teach': 'N goes the other way. n keeps the direction the search '
                  'started in.'},
        {'id': 'vim-search-fwd', 'type': 'keys',
         'keys': ['/', 'e', 'r', 'r', 'o', 'r', 'RET'],
         'prompt': 'Search forward for the word error.',
         'teach': 'A search is a motion, so d/error deletes up to the next '
                  'match. ? searches backward.'},

        # substitution: typed ex-commands, graded as text
        {'id': 'vim-subst-line', 'type': 'command',
         'prompt': 'On the current line, replace the first old with new.',
         'answer': ':s/old/new/',
         'teach': 'No range means this line only, and no g means the first '
                  'match only. Both defaults surprise everyone once.'},
        {'id': 'vim-subst-line-g', 'type': 'command',
         'prompt': 'On the current line, replace every old with new.',
         'answer': ':s/old/new/g',
         'teach': 'The g flag means every match on the line rather than just '
                  'the first.'},
        {'id': 'vim-subst-file', 'type': 'command',
         'prompt': 'In the whole file, replace every old with new.',
         'answer': ':%s/old/new/g',
         'teach': '% is the range meaning every line. This is the blind '
                  'global replace, so reach for it only when you are sure.'},
        {'id': 'vim-subst-confirm', 'type': 'command',
         'prompt': 'In the whole file, replace every old with new, asking '
                   'about each one.',
         'answer': ':%s/old/new/gc',
         'teach': 'The c flag makes vim confirm each match. This is the safe '
                  'way to do a big replace.'},
        {'id': 'vim-noh', 'type': 'command',
         'prompt': 'Clear the search highlight left on the screen.',
         'answer': ':noh',
         'accepts': [':nohlsearch'],
         'teach': 'The matches stay lit after a search until you clear them, '
                  'which is what :noh is for.'},
    ],

    # ------------------------------------------------------------------
    'challenges': [
        {
            'id': 'vim-first-edit',
            'solution': {'keys': 'wciwEARTH\x1b:wq\r'},
            'title': 'Change a word without moving first',
            'goal': 'Use a text object rather than positioning by hand. Change '
                    'the word "world" to "EARTH", then save and quit.',
            'setup': {'kind': 'nvim',
                      'start': ['hello world here', 'leave this line alone']},
            'steps': [
                {'instruction': 'Put the cursor anywhere inside the word world.',
                 'hint': 'w moves you there in one press'},
                {'instruction': 'Change the whole word without selecting it.',
                 'hint': 'ciw, then type EARTH'},
                {'instruction': 'Return to normal mode and save.',
                 'hint': 'Esc then :wq'},
            ],
            'free': 'Change "world" to "EARTH" using a text object, then save '
                    'and quit.',
            'verify': {'kind': 'nvim',
                       'expect': {'lines': ['hello EARTH here',
                                            'leave this line alone']}},
            'fallback': 'self',
        },
        {
            'id': 'vim-swap-lines',
            'solution': {'keys': 'ggddp:wq\r'},
            'title': 'Swap two lines with two keystrokes',
            'goal': 'Put "second" above "first" using only normal-mode '
                    'commands, then save.',
            'setup': {'kind': 'nvim', 'start': ['first', 'second', 'third']},
            'steps': [
                {'instruction': 'Put the cursor on the first line.',
                 'hint': 'gg'},
                {'instruction': 'Delete it. It is not lost, it is in a '
                                'register.',
                 'hint': 'dd'},
                {'instruction': 'Paste it back below the line that is now '
                                'first.',
                 'hint': 'p'},
                {'instruction': 'Save and quit.', 'hint': ':wq'},
            ],
            'free': 'Make the file read second, first, third. Two keystrokes '
                    'is enough.',
            'verify': {'kind': 'nvim',
                       'expect': {'lines': ['second', 'first', 'third']}},
            'fallback': 'self',
        },
        {
            'id': 'vim-text-objects',
            'solution': {'keys': 'ggf\"lci\"new message\x1bjf(lci(x\x1b:wq\r'},
            'title': 'Work inside the brackets',
            'goal': 'Change what is inside the parentheses and what is inside '
                    'the quotes, without touching the delimiters.',
            'setup': {'kind': 'nvim',
                      'start': ['print("old message", verbose)',
                                'result = compute(a, b, c)']},
            'steps': [
                {'instruction': 'Change the quoted string on line 1 to say '
                                'new message.',
                 'hint': 'ci" from anywhere inside the quotes'},
                {'instruction': 'Change the arguments on line 2 to just x.',
                 'hint': 'ci( from anywhere inside the parens'},
                {'instruction': 'Save and quit.', 'hint': ':wq'},
            ],
            'free': 'Make line 1 read print("new message", verbose) and line 2 '
                    'read result = compute(x). Use text objects.',
            'verify': {'kind': 'nvim',
                       'expect': {'lines': ['print("new message", verbose)',
                                            'result = compute(x)']}},
            'fallback': 'self',
        },
        {
            'id': 'vim-macro-list',
            'solution': {'keys': 'ggqaI- \x1bjq5@a:wq\r'},
            'title': 'Turn a list into a markdown list with a macro',
            'goal': 'Prefix every line with "- " by recording the change once '
                    'and replaying it.',
            'setup': {'kind': 'nvim',
                      'start': ['apples', 'bread', 'coffee', 'dates',
                                'eggs', 'flour']},
            'steps': [
                {'instruction': 'Go to the first line.', 'hint': 'gg'},
                {'instruction': 'Start recording into register a.',
                 'hint': 'qa'},
                {'instruction': 'Go to the start of the line and insert "- ".',
                 'hint': 'I- then Esc'},
                {'instruction': 'Move down one line, then stop recording.',
                 'hint': 'j then q'},
                {'instruction': 'Replay it for the remaining five lines.',
                 'hint': '5@a'},
                {'instruction': 'Save and quit.', 'hint': ':wq'},
            ],
            'free': 'Prefix all six lines with "- " by recording a macro once '
                    'and replaying it with a count.',
            'verify': {'kind': 'nvim',
                       'expect': {'lines': ['- apples', '- bread', '- coffee',
                                            '- dates', '- eggs', '- flour']}},
            'fallback': 'self',
        },
        {
            'id': 'vim-dot-repeat',
            'solution': {'keys': 'gg/oldname\rciwnewname\x1bn.nn.:wq\r'},
            'title': 'Walk a file with n and dot',
            'goal': 'Rename every occurrence of oldname to newname, one at a '
                    'time, using search and repeat rather than substitution.',
            # Line 1 deliberately contains no match. With the cursor starting
            # on an occurrence, /oldname jumps past it and the first one never
            # gets changed, which made the steps unable to reach the goal.
            'setup': {'kind': 'nvim',
                      'start': ['def setup():',
                                '    oldname = 1',
                                '    print(oldname)',
                                '    # leave this oldname alone',
                                '    return oldname']},
            'steps': [
                {'instruction': 'Search for oldname.', 'hint': '/oldname then Enter'},
                {'instruction': 'Change this one.', 'hint': 'ciwnewname then Esc'},
                {'instruction': 'Jump to the next match.', 'hint': 'n'},
                {'instruction': 'Repeat the change without retyping it.',
                 'hint': '.'},
                {'instruction': 'Skip the one in the comment, change the last, '
                                'then save.',
                 'hint': 'n to skip past, then . on the last one'},
            ],
            'free': 'Rename oldname to newname everywhere except inside the '
                    'comment, using n and the dot command.',
            'verify': {'kind': 'nvim',
                       'expect': {'lines': ['def setup():',
                                            '    newname = 1',
                                            '    print(newname)',
                                            '    # leave this oldname alone',
                                            '    return newname']}},
            'fallback': 'self',
        },
        {'id': 'vim-paragraph',
         'title': 'Delete a paragraph without counting lines',
         'goal': 'A paragraph is a text object. Delete the whole first '
                 'paragraph, including the blank line after it, in one '
                 'command.',
         'setup': {'kind': 'nvim',
                   'start': ['first para line one',
                             'first para line two',
                             '',
                             'second para']},
         'solution': {'keys': 'dap:wq\r'},
         'steps': [{'instruction': 'Leave the cursor anywhere in the first '
                                   'paragraph.',
                    'hint': 'it starts there already'},
                   {'instruction': 'Delete around the paragraph, which '
                                   'takes the blank line with it.',
                    'hint': 'dap: delete a paragraph. dip would leave the '
                            'blank line'},
                   {'instruction': 'Save and quit.', 'hint': ':wq'}],
         'free': 'Leave only the second paragraph, using one text-object '
                 'command.',
         'verify': {'kind': 'nvim', 'expect': {'lines': ['second para']}},
         'fallback': 'self'},
        {'id': 'vim-join',
         'title': 'Join two lines',
         'goal': 'Put the second line onto the end of the first, with one '
                 'space between them, in one keystroke.',
         'setup': {'kind': 'nvim', 'start': ['one', 'two', 'three']},
         'solution': {'keys': 'J:wq\r'},
         'steps': [{'instruction': 'With the cursor on the first line, '
                                   'join the next one onto it.',
                    'hint': 'capital J. It inserts the space for you'},
                   {'instruction': 'Save and quit.',
                    'hint': ':wq. gJ joins without the space, if you ever '
                            'need that'}],
         'free': 'Leave the file as "one two" then "three".',
         'verify': {'kind': 'nvim',
                    'expect': {'lines': ['one two', 'three']}},
         'fallback': 'self'},
        {'id': 'vim-inside-quotes',
         'title': 'Change what is inside the quotes',
         'goal': 'Replace the quoted string without touching the quotes, '
                 'from wherever the cursor happens to be on the line.',
         'setup': {'kind': 'nvim',
                   'start': ['name = "old value"', 'other = "leave me"']},
         'solution': {'keys': 'ci"new\x1b:wq\r'},
         'steps': [{'instruction': 'The cursor is at the start of the '
                                   'line, before the quotes. That is fine.',
                    'hint': 'quote text objects search forward on the '
                            'line'},
                   {'instruction': 'Change what is inside the quotes to '
                                   'new.',
                    'hint': 'ci" then type new. ca" would eat the quotes '
                            'too'},
                   {'instruction': 'Escape and save.',
                    'hint': 'Esc then :wq'}],
         'free': 'Make the first line read name = "new", leaving the '
                 'second line alone.',
         'verify': {'kind': 'nvim',
                    'expect': {'lines': ['name = "new"',
                                         'other = "leave me"']}},
         'fallback': 'self'},
        {'id': 'vim-substitute',
         'title': 'Replace every occurrence in the file',
         'goal': 'Use the substitute command over the whole file, '
                 'replacing every match on every line, not just the first '
                 'on each.',
         'setup': {'kind': 'nvim',
                   'start': ['foo one foo', 'bar two', 'three foo']},
         'solution': {'keys': ':%s/foo/BAR/g\r:wq\r'},
         'steps': [{'instruction': 'Open the command line and address '
                                   'every line.',
                    'hint': ':%s means every line. :s alone means this '
                            'one'},
                   {'instruction': 'Replace foo with BAR, every time it '
                                   'appears.',
                    'hint': ':%s/foo/BAR/g. Without the g you get the '
                            'first per line'},
                   {'instruction': 'Save and quit.', 'hint': ':wq'}],
         'free': 'Replace every foo with BAR everywhere in the file.',
         'verify': {'kind': 'nvim',
                    'expect': {'lines': ['BAR one BAR',
                                         'bar two',
                                         'three BAR']}},
         'fallback': 'self'},
        {'id': 'vim-append-end',
         'title': 'Append to the end of a line',
         'goal': 'Get into insert mode at the end of the line without '
                 'pressing a motion first.',
         'setup': {'kind': 'nvim',
                   'start': ['todo: write it', 'todo: leave this one']},
         'solution': {'keys': 'A DONE\x1b:wq\r'},
         'steps': [{'instruction': 'Jump to the end of the line and start '
                                   'inserting, in one key.',
                    'hint': 'capital A. It is $ and a in one'},
                   {'instruction': 'Type a space and DONE.',
                    'hint': 'the space matters: " DONE"'},
                   {'instruction': 'Escape and save.',
                    'hint': 'Esc then :wq'}],
         'free': 'Make the first line read "todo: write it DONE", leaving '
                 'the second alone.',
         'verify': {'kind': 'nvim',
                    'expect': {'lines': ['todo: write it DONE',
                                         'todo: leave this one']}},
         'fallback': 'self'},
        {'id': 'vim-search-change',
         'title': 'Find it, then change it',
         'goal': 'Search for a word rather than navigating to it, then '
                 'change that word in place.',
         'setup': {'kind': 'nvim',
                   'start': ['the quick brown fox',
                             'jumps over the lazy dog']},
         'solution': {'keys': '/lazy\rcwtired\x1b:wq\r'},
         'steps': [{'instruction': 'Search forward for the word lazy.',
                    'hint': '/lazy then Enter. The cursor lands on the '
                            'match'},
                   {'instruction': 'Change that word to tired.',
                    'hint': 'cw then type tired'},
                   {'instruction': 'Escape and save.',
                    'hint': 'Esc then :wq. n would take you to the next '
                            'match'}],
         'free': 'Change lazy to tired, finding it by searching rather '
                 'than by moving there.',
         'verify': {'kind': 'nvim',
                    'expect': {'lines': ['the quick brown fox',
                                         'jumps over the tired dog']}},
         'fallback': 'self'},

        {'id': 'vim-registers',
         'title': 'Yank into a named register and use it',
         'goal': 'The unnamed register is overwritten constantly. Put text '
                 'somewhere it will survive, then paste it.',
         'setup': {'kind': 'nvim',
                   'start': ['keep this line',
                             'delete me',
                             'delete me too',
                             'paste target']},
         'solution': {'keys': 'gg"ayyjddddG"ap:wq\r'},
         'steps': [{'instruction': 'Yank the first line into register a.',
                    'hint': '"ayy, where "a selects the register'},
                   {'instruction': 'Delete a couple of lines, which would '
                                   'normally clobber what you yanked.',
                    'hint': 'dd'},
                   {'instruction': 'Paste register a at the end of the file.',
                    'hint': 'G then "ap'},
                   {'instruction': 'Save. Note that "0 always holds the last '
                                   'yank, which is the other way out of this '
                                   'problem.',
                    'hint': ':wq'}],
         'free': 'Using a named register, copy the first line and paste it at '
                 'the end, with deletions in between.',
         'verify': {'kind': 'nvim',
                    'expect': {'contains': ['keep this line', 'paste target']}},
         'fallback': 'self'},

        {'id': 'vim-counts-motions',
         'title': 'Put a count on a verb and a motion',
         'goal': 'A count multiplies, and it can go on either half of the '
                 'grammar. Use both places.',
         'setup': {'kind': 'nvim',
                   'start': ['alpha bravo charlie delta echo',
                             'one', 'two', 'three', 'four', 'five', 'keep']},
         'solution': {'keys': 'gg3dwj4dd:wq\r'},
         'steps': [{'instruction': 'On the first line, delete the first three '
                                   'words with one command.',
                    'hint': '3dw, or d3w. Both mean the same thing'},
                   {'instruction': 'Go to the second line and delete four '
                                   'lines from there.',
                    'hint': 'j then 4dd'},
                   {'instruction': 'Save.',
                    'hint': ':wq'}],
         'free': 'Delete the first three words of line one, then four whole '
                 'lines starting at line two.',
         'verify': {'kind': 'nvim',
                    'expect': {'lines': ['delta echo', 'five', 'keep']}},
         'fallback': 'self'},

        {'id': 'vim-visual-block',
         'title': 'Edit a column with visual block',
         'goal': 'Visual block is the mode that has no equivalent anywhere '
                 'else. Use it to prefix several lines at once.',
         'setup': {'kind': 'nvim',
                   'start': ['alpha', 'bravo', 'charlie', 'delta']},
         'solution': {'keys': 'gg\x16jjjI# \x1b:wq\r'},
         'steps': [{'instruction': 'Enter visual block mode at the start of '
                                   'the first line.',
                    'hint': 'Ctrl-v'},
                   {'instruction': 'Extend the block down over all four '
                                   'lines.',
                    'hint': 'jjj'},
                   {'instruction': 'Insert a comment marker at the start of '
                                   'the block, then escape. The edit applies '
                                   'to every line when you leave insert '
                                   'mode.',
                    'hint': 'I then a hash and a space, then Esc'},
                   {'instruction': 'Save.',
                    'hint': ':wq'}],
         'free': 'Prefix all four lines with a hash and a space, in one '
                 'visual block edit.',
         'verify': {'kind': 'nvim',
                    'expect': {'lines': ['# alpha', '# bravo', '# charlie',
                                         '# delta']}},
         'fallback': 'self'},
                  ],

    # ------------------------------------------------------------------
    'quiz': [
        {'id': 'vq-grammar', 'type': 'mcq',
         'prompt': 'You have never seen the command y} before. What does it do?',
         'answer': 'Yanks from the cursor to the end of the paragraph.',
         'distractors': ['Yanks the current line and the next.',
                         'Nothing; } is not a motion.',
                         'Yanks to the matching brace.'],
         'teach': 'This is the point of the grammar. y is a verb, } is a '
                  'motion, and you can read commands you were never taught.'},

        {'id': 'vq-cw-vs-ciw', 'type': 'mcq',
         'prompt': 'The cursor is on the "r" in "worlds". What is the '
                   'difference between cw and ciw?',
         'answer': 'cw changes "rlds", ciw changes the whole word.',
         'distractors': ['They do the same thing.',
                         'cw changes the whole word, ciw only to the end.',
                         'ciw also removes the trailing space.'],
         'teach': 'Motions run from the cursor; text objects name a region '
                  'regardless of where you are standing. That is why ciw is '
                  'nearly always the one you meant.'},

        {'id': 'vq-count-position', 'type': 'mcq',
         'prompt': 'Which pair does the same thing?',
         'answer': 'd2w and 2dw',
         'distractors': ['3dd and d3j', 'diw and daw', 'x and X'],
         'teach': 'A count can sit before the verb or between verb and motion. '
                  '3dd and d3j differ because d3j takes four lines.'},

        {'id': 'vq-iw-vs-aw', 'type': 'mcq',
         'prompt': 'Why does daw usually read better than diw?',
         'answer': 'aw takes the trailing space, so you are not left with a '
                   'double space.',
         'distractors': ['daw is faster to type.',
                         'diw does not work mid-word.',
                         'aw also removes punctuation.'],
         'teach': 'i is inner, a is around. The difference is exactly the '
                  'whitespace or the delimiters.'},

        {'id': 'vq-registers', 'type': 'mcq',
         'prompt': 'You press yy on line 1, then dd on line 5, then p. What '
                   'gets pasted?',
         'answer': 'Line 5, because the delete overwrote the unnamed register.',
         'distractors': ['Line 1, because yanks take priority.',
                         'Both, in the order they were captured.',
                         'Nothing; dd clears the register.'],
         'teach': 'Deletes and yanks share the unnamed register. Use a named '
                  'register like "ayy when you need to hold on to something.'},

        {'id': 'vq-dot', 'type': 'mcq',
         'prompt': 'You do ciwfoo then Esc, then press j four times, then '
                   'press dot. What happens?',
         'answer': 'The word under the cursor is changed to foo.',
         'distractors': ['The cursor moves down four more lines.',
                         'Nothing; moving cleared the repeat.',
                         'The last four presses of j repeat.'],
         'teach': 'Dot repeats the last change, not the last command. Movement '
                  'does not disturb it, which is what makes the n-dot loop '
                  'work.'},

        {'id': 'vq-macro-anchor', 'type': 'mcq',
         'prompt': 'Why should a macro usually start with ^ or 0?',
         'answer': 'So it replays from a known position instead of drifting.',
         'distractors': ['Because recording requires a motion first.',
                         'To stop it overwriting the register.',
                         'Because @ replays from column one anyway.'],
         'teach': 'Anchor at the start, end on the next target, and a macro '
                  'replays cleanly however many times you ask for.'},

        {'id': 'vq-buffers-tabs', 'type': 'mcq',
         'prompt': 'In vim, what is a tab?',
         'answer': 'A layout of windows, not a file.',
         'distractors': ['An open file, as in other editors.',
                         'A viewport onto a buffer.',
                         'Another name for a buffer.'],
         'teach': 'Buffers are files, windows are viewports, tabs are '
                  'arrangements. Expecting tabs to be files is the confusion '
                  'people import from other editors.'},

        {'id': 'vq-ctrl-i', 'type': 'mcq',
         'prompt': 'Why does C-i sometimes appear not to work in a terminal?',
         'answer': 'C-i and Tab are the same byte, so most terminals cannot '
                   'tell them apart.',
         'distractors': ['C-i is not bound by default in vim.',
                         'It only works in neovim, not vim.',
                         'It requires the jump list to be non-empty.'],
         'teach': 'This is a terminal limitation rather than a vim one. '
                  'Terminals speaking the modern keyboard protocol can '
                  'distinguish them; older ones cannot.'},
    ],
}
