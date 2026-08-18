"""Emacs, plain: the editor underneath Doom, taught as its own thing.

**Why this exists next to the Doom module.** Doom is a configuration framework,
and its whole design is a leader tree that replaces the bindings underneath.
That is a good way to use Emacs and a bad way to learn what Emacs *is*: someone
who only knows `SPC f s` cannot read any Emacs documentation written since
1985, cannot use the Emacs on a server, and cannot tell whether a problem is
theirs or Doom's. This module is for the other route, and for the people who
never wanted Doom in the first place.

**It declares no prereqs and is nobody's prereq.** Overlap with the Doom module
is deliberate and small: both have to teach `C-x C-c`, `C-g` and what a chord
is, because a module that assumes the other one was read is a module that
strands half its students. Everything past that diverges, because the two are
genuinely different editors to sit in front of.

**Order 9 puts it first in the Editors group.** That is curriculum order, not a
gate. It goes first because it is the only module in the group that assumes
nothing at all, and hone never forces a sequence.

**Survival material is lesson one, on purpose.** An audit of all fifty modules
found this group was the worst in the roster for it: Doom taught the way out of
Emacs in lesson nine of nine, vim never taught `:wq` in any of its eleven, and
a student testing Doom got handed an editor they could not leave. Lesson one
here is how to get in, how to cancel, and how to get out, and only then what
any of it means.

Drills are `keys` type: Emacs bindings are chords, they are what the
documentation is written in, and they are exactly the thing that has to become
reflex before the editor stops being hostile.
"""

MODULE = {
    'id': 'emacs',
    'title': 'Emacs',
    'group': 'Editors',
    'blurb': 'Chords, buffers and windows, the mark, and M-x as the whole map.',
    'context': 'You are in a plain Emacs, in a buffer with a file open, no evil mode and no leader key.',
    'needs': ('emacs',),
    'prereqs': [],
    'adapter': 'emacs',
    'estimate': '3-5 hours',
    'order': 40,

    # ------------------------------------------------------------------
    'lessons': [
        {
            'id': 'em-inout',
            'title': 'Getting in, cancelling, getting out',
            'next': 'em-notation',
            'concept': (
                'Emacs is an editor that runs commands by name, and binds '
                'some of those names to chords. It is not vim. It is not '
                'Doom. It is the program both of those sit on, and the one '
                'that is on a server when nothing else is installed.\n\n'
                'Three keys make the first hour survivable, and none of '
                'them is worth saving for later.\n\n'
                '**C-x C-c quits.** Emacs asks about anything unsaved before '
                'it goes, so this is safe to press when you are lost. Closing '
                'the terminal instead leaves auto-save files behind and '
                'answers no questions.\n\n'
                '**C-g cancels whatever is in progress.** A key sequence you '
                'started by accident, a prompt you cannot read, a search that '
                'ran away: C-g puts you back in the buffer. Press it twice if '
                'once did not do it. This is the single most useful key in '
                'the editor and the one nobody mentions.\n\n'
                '**C-x C-s saves.** Not Ctrl-S, which in a terminal freezes '
                'the display and convinces people the editor has crashed. If '
                'that happens, C-q unfreezes it.\n\n'
                'Starting is ordinary. `emacs notes.txt` opens a file, and '
                '`emacs -nw notes.txt` keeps it inside the terminal instead '
                'of opening a window. The file does not have to exist yet.\n\n'
                'C-x C-c still quits, the same key the Doom module led with. '
                'This module is vanilla Emacs with no evil, so SPC is a space '
                'and there is no leader tree.\n\n'
                'C-g prints `Quit` in the echo area and drops the prefix. If '
                'a minibuffer prompt is still sitting there, press it again: '
                'some commands nest a prompt inside a prefix, and one cancel '
                'only peels one layer. Killing the terminal instead of C-x '
                'C-c leaves `#notes.txt#` auto-save files in the directory, '
                'and the next Emacs to open that file will offer to recover '
                'them. That offer is not a crash report. It is Emacs finding '
                'work it was not allowed to finish. The next lesson is how '
                'the documentation writes the keys you just used.'
            ),
            'examples': [
                {
                    'label': 'The whole survival kit',
                    'code': ('emacs -nw notes.txt   open, in this terminal\n'
                             '\n'
                             'C-g                   cancel what is happening\n'
                             'C-x C-s               save\n'
                             'C-x C-c               quit\n'
                             'C-q                   unfreeze a stuck '
                             'terminal'),
                    'note': 'C-g first. Everything else in Emacs is '
                            'recoverable if you can always get back to a '
                            'known state.',
                },
                {
                    'label': 'What a stuck Emacs usually is',
                    'code': ('you pressed Ctrl-S out of habit\n'
                             '\n'
                             'the terminal has stopped drawing, not Emacs.\n'
                             'C-q resumes it, and your keystrokes were all\n'
                             'received while it looked frozen.'),
                    'note': 'This is a terminal behaviour older than Emacs '
                            'and nothing to do with the editor, which is why '
                            'no amount of reading the Emacs manual explains '
                            'it.',
                },
            ],
            'misconceptions': [
                'C-x C-c does not discard your work. It asks about every '
                'modified buffer first, one at a time.',
                'C-g is not undo. It abandons the command you are part way '
                'through and changes nothing already in the buffer.',
                'Emacs is not frozen when Ctrl-S stops the display. The '
                'terminal is holding output back, and C-q releases it.',
            ],
            'try_it': [
                'Run `emacs -nw /tmp/scratch.txt`, type a word, save with C-x '
                'C-s, and quit with C-x C-c. Do it twice so it is boring.',
                'Start a sequence you do not intend to finish, like C-x, then '
                'press C-g. Watching the prefix disappear is the whole point.',
            ],
        },
        {
            'id': 'em-notation',
            'title': 'Reading the notation',
            'next': 'em-buffers',
            'concept': (
                'Every piece of Emacs documentation ever written uses the '
                'same shorthand, and it is unreadable until someone spends a '
                'paragraph on it.\n\n'
                '**C- means hold Control.** `C-f` is Control and f together. '
                '**M- means hold Meta**, which is Alt on essentially every '
                'keyboard made since Meta keys stopped existing. `M-f` is Alt '
                'and f. If Alt does not work, Esc pressed and released '
                'beforehand does the same job, which is why terminals that '
                'eat Alt are survivable.\n\n'
                '**Two of them side by side means one after the other.** `C-x '
                'C-s` is Control-x, then Control-s. You can keep Control held '
                'down through both, and most people do.\n\n'
                '**A prefix is a real thing, not a formality.** `C-x` on its '
                'own does nothing except wait: the echo area at the bottom '
                'shows `C-x-` and Emacs holds until you finish the sequence. '
                'That waiting state is where beginners get stuck, and C-g is '
                'the way out of it.\n\n'
                'Named keys are spelled out: `RET` is Enter, `SPC` is space, '
                '`TAB` is Tab, `DEL` is Backspace. `C-M-f` means all three at '
                'once, which is rarer and reads exactly as it looks.\n\n'
                'While a prefix is pending the echo area shows `C-x-` and '
                'every key is part of the sequence, including keys you did '
                'not mean. Type `C-x` then `s` and you have started '
                '`save-some-buffers`, which will walk every modified buffer '
                'asking. That is not a hang. It is a command you entered by '
                'finishing a prefix you had forgotten about. C-g abandons '
                'it; answering the prompts also works and is slower. The '
                'echo area is how you know you are in that state before the '
                'next key commits you.'
            ),
            'examples': [
                {
                    'label': 'Chords and sequences',
                    'code': ('C-f       one chord: Ctrl and f\n'
                             'M-f       one chord: Alt and f\n'
                             'C-x C-s   two chords, in order\n'
                             'C-x 2     a chord, then a plain digit\n'
                             'C-M-f     Ctrl and Alt and f, together'),
                    'note': 'Note C-x 2: the second key has no modifier at '
                            'all. Prefixes do not make the rest of the '
                            'sequence into chords.',
                },
                {
                    'label': 'When Alt is eaten by the terminal',
                    'code': ('M-f          Alt and f\n'
                             'ESC f        the same command, always\n'
                             '\n'
                             'ESC is pressed and released, not held.'),
                    'note': 'Worth knowing before you need it: some '
                            'terminals, multiplexers and remote sessions '
                            'swallow Alt, and this is the escape hatch.',
                },
            ],
            'misconceptions': [
                'C-x is not a command. It is a prefix, and Emacs waits for '
                'the rest of the sequence rather than doing anything.',
                'M- and ESC are not different bindings. ESC pressed and '
                'released is the same as holding Meta, which is why every '
                'Meta binding has a fallback.',
                'Capitalisation in the notation is not shift. `C-x C-s` and '
                '`C-X C-S` mean the same keys; a real shift is written out, '
                'as in `C-x C-S-f`.',
            ],
            'try_it': [
                'Press C-x and stop. Read the echo area at the bottom of the '
                'screen, then press C-g.',
                'Press C-h k and then any key. Emacs tells you exactly what '
                'that key is bound to, which turns the notation into '
                'something you can look up rather than memorise.',
            ],
        },
        {
            'id': 'em-buffers',
            'title': 'Buffers, windows and frames',
            'next': 'em-move',
            'concept': (
                'Emacs uses three words that every other program uses '
                'differently, and getting them straight makes the rest of the '
                'editor readable.\n\n'
                '**A buffer is content.** Usually a file you opened, '
                'sometimes output, sometimes a list. Buffers exist whether or '
                'not anything is showing them.\n\n'
                '**A window is a viewport onto a buffer.** Splitting the '
                'screen makes two windows, and both can show the same buffer '
                'at different places, which is genuinely useful when editing '
                'one long file.\n\n'
                '**A frame is what your operating system calls a window.** '
                'This is the one that catches people, and it is why Emacs '
                'documentation seems to be talking nonsense until you know.\n\n'
                'So `C-x k` kills a buffer, which is closing the file, while '
                '`C-x 0` closes a window, which just stops showing it. The '
                'buffer is still there and `C-x b` will bring it straight '
                'back. Nothing is lost by closing a window, and that is worth '
                'internalising early because it makes the split commands safe '
                'to experiment with.\n\n'
                'Killing the buffer you are looking at does not close Emacs. '
                'The window stays and shows another buffer, often `*scratch*` '
                'or whatever you visited last. That is why C-x k feels like '
                'it did nothing if you were not watching the mode line: the '
                'file is gone, the window is not. `C-x C-b` lists everything '
                'still living, including `*Help*` and `*Messages*`, which is '
                'how a session accumulates a dozen buffers you never opened '
                'on purpose. None of them are files. C-x k on those just '
                'dismisses them.\n\n'
                'The split is safe. The question left open is how you '
                'move inside the buffer you are looking at, and the '
                'next lesson is that grid.'
            ),
            'examples': [
                {
                    'label': 'Windows: four commands and you are fluent',
                    'code': ('C-x 2     split, one above the other\n'
                             'C-x 3     split, side by side\n'
                             'C-x o     go to the other window\n'
                             'C-x 0     close this window\n'
                             'C-x 1     close every window but this one'),
                    'note': 'C-x 1 is the panic button when Emacs has filled '
                            'the screen with help buffers and compilation '
                            'output.',
                },
                {
                    'label': 'Buffers: moving between open things',
                    'code': ('C-x b     switch buffer, by name, with TAB\n'
                             'C-x C-b   list every buffer\n'
                             'C-x k     kill this buffer\n'
                             '\n'
                             'C-x b RET returns to the previous buffer'),
                    'note': 'C-x b defaults to the buffer you were in last, '
                            'so pressing Enter at the prompt is a fast toggle '
                            'between two files.',
                },
            ],
            'misconceptions': [
                'Closing a window does not close the file. The buffer '
                'survives, and C-x b brings it back exactly where you left '
                'the cursor.',
                'A frame is not a window. Emacs called them frames first, and '
                'the manual has never given the word up.',
                'Two windows showing one buffer are not copies. Type in '
                'either and both update, because there is only ever one '
                'buffer.',
            ],
            'try_it': [
                'Split with C-x 2, move between the halves with C-x o, then '
                'collapse it with C-x 1.',
                'Open a second file with C-x C-f, then flip between the two '
                'with C-x b and Enter a few times.',
            ],
        },
        {
            'id': 'em-move',
            'title': 'Moving, and the mark',
            'next': 'em-search',
            'concept': (
                'Movement keys are how you place the point. The mark is how '
                'you name the other end of a region. That is why a selection '
                'in Emacs is two places, not a highlight you have to keep.\n\n'
                'The movement keys look arbitrary and are not. They are a '
                'grid: C- for characters and lines, M- for words and '
                'sentences, and the same letter means the same direction at '
                'both scales.\n\n'
                '`C-f` and `C-b` go forward and back one character; `M-f` and '
                '`M-b` do it a word at a time. `C-n` and `C-p` are next and '
                'previous line. `C-a` and `C-e` are the start and end of the '
                'line. Once you notice that f is forward, b is back, n is '
                'next and p is previous, most of it stops needing memorising.\n\n'
                '**The mark is the idea worth the lesson.** `C-SPC` sets a '
                'mark where the cursor is. Move somewhere else, and the text '
                'between the mark and the cursor is the region, which is what '
                'other editors call a selection. `C-w` kills the region, '
                '`M-w` copies it, and `C-y` yanks the last thing killed back '
                'in. `C-x h` marks the whole buffer, which is the region '
                '`sort-lines` wants when you mean every line.\n\n'
                'Kill and yank rather than cut and paste, and the difference '
                'is real: killed text stacks up in a ring, and `M-y` straight '
                'after a `C-y` cycles back through earlier kills. It is a '
                'clipboard with history, and it has been there since before '
                'clipboards.\n\n'
                'The mark stays where you left it, including from three files '
                'ago if you never set a new one. C-w then kills from that '
                'old place to here, which can be most of the buffer. The '
                'highlight is not required: transient-mark-mode shows the '
                'region only after a fresh C-SPC, so a stale mark is '
                'invisible until you kill. C-g deactivates it. C-y puts the '
                'text back, so the recovery is yank rather than undo, and '
                'the kill is now on the ring either way.'
            ),
            'examples': [
                {
                    'label': 'The movement grid',
                    'code': ('        character   word        line/buffer\n'
                             'back    C-b         M-b         C-a  M-<\n'
                             'forward C-f         M-f         C-e  M->\n'
                             '\n'
                             'C-n next line      C-p previous line'),
                    'note': 'M-< and M-> are the start and end of the whole '
                            'buffer, and they are the same angle brackets you '
                            'would draw pointing that way.',
                },
                {
                    'label': 'Select, kill, yank',
                    'code': ('C-SPC     set the mark here\n'
                             '...move...\n'
                             'C-w       kill the region\n'
                             'M-w       copy the region instead\n'
                             'C-y       yank it back\n'
                             'M-y       and again, further back the ring'),
                    'note': 'C-y then M-y M-y walks back through everything '
                            'you have killed this session. No other editor '
                            'gives you this for free.',
                },
                {
                    # Both of these were drilled and set as a challenge hint
                    # before anything taught them. ramp.py caught it in the
                    # module written to fix exactly that class of problem,
                    # which is the argument for the script existing.
                    'label': 'Deleting backwards, and taking it back',
                    'code': ('M-DEL     kill the word behind the cursor\n'
                             'C-k       kill to the end of the line\n'
                             '\n'
                             'C-/       undo\n'
                             'C-x u     undo, the other spelling'),
                    'note': 'Emacs undo is a ring rather than a stack, so '
                            'undoing your undos is how you redo. C-g then C-/ '
                            'changes direction.',
                },
            ],
            'misconceptions': [
                'The region is not a selection you have to keep highlighted. '
                'The mark stays set, and the region is simply whatever lies '
                'between it and the cursor right now.',
                'C-w is not a word delete. It kills the region, which is why '
                'pressing it with a stale mark somewhere far away removes '
                'more than you expected. C-g clears the mark.',
                'Yank does not mean pull from the system clipboard. It means '
                'the Emacs kill ring, which is a separate thing and usually '
                'the one you want.',
            ],
            'try_it': [
                'Set a mark with C-SPC, move down three lines, and copy with '
                'M-w. Then yank it somewhere with C-y.',
                'Kill three different lines with C-k, then press C-y and M-y '
                'M-y and watch the yanked text change.',
            ],
        },
        {
            'id': 'em-search',
            'title': 'Search, without freezing the terminal',
            'next': 'em-mx',
            'concept': (
                'The previous lesson moved the point on purpose. This one is '
                'how you find the place to move to, without leaving the '
                'keyboard.\n\n'
                '`C-s` starts incremental search. Each character you type '
                'narrows the match, and the point jumps to it as you type. '
                '`C-r` goes backward. `C-s` again jumps to the next hit. RET '
                'drops you on the match. `C-g` cancels and returns to where '
                'you started. That last one is the same cancel as lesson 1, '
                'and it is how you abandon a search that went the wrong way.\n\n'
                'This is not the same `Ctrl-S` that freezes a terminal. At a '
                'shell, Ctrl-S is XOFF and the screen stops drawing until '
                'Ctrl-Q. Inside Emacs, after a command, `C-s` is I-search, '
                'and the echo area says so. If the screen freezes and the '
                'echo area is empty, you hit the terminal, not Emacs: press '
                'Ctrl-Q.\n\n'
                'Replace is a named command. `M-%` is query-replace: it asks '
                'on each hit, `y` or `n`. `M-x replace-string` does not ask. '
                'Use the one that asks until the pattern is boring.\n\n'
                'The next lesson is how every one of these keys is just a '
                'name you can type if you forget the chord.'
            ),
            'examples': [
                {
                    'label': 'Find, then find the next',
                    'code': ('C-s error      start, type the word\n'
                             'C-s            next hit\n'
                             'C-r            previous hit\n'
                             'RET            stay here\n'
                             'C-g            back where you started'),
                    'note': 'The echo area says I-search. That is how you '
                            'know you are in search and not frozen.',
                },
                {
                    'label': 'Change it with review',
                    'code': ('M-% old RET new RET\n'
                             '  y   replace this one\n'
                             '  n   skip\n'
                             '  !   replace the rest\n'
                             '  q   stop'),
                    'note': 'Query-replace is slower than replace-string and '
                            'is the one that does not wreck a file.',
                },
            ],
            'misconceptions': [
                'A frozen screen after Ctrl-S is the terminal, not Emacs. '
                'Ctrl-Q starts drawing again. If the echo area says '
                'I-search, you are in Emacs and C-g leaves.',
                'C-s C-s with nothing typed repeats the last search. That is '
                'a feature, and it looks like a stuck key the first time.',
            ],
            'try_it': [
                'Open any file, press C-s, type a word you can see, jump '
                'with C-s a few times, then C-g back. Then try M-% on a '
                'short word and answer n on the first hit.',
            ],
        },
        {
            'id': 'em-mx',
            'title': 'M-x, and why nothing is hidden',
            'next': 'em-files',
            'concept': (
                'Every key in Emacs runs a named command, and every named '
                'command can be run without its key. `M-x` opens a prompt, '
                'you type the name, and TAB completes it. That is the whole '
                'mechanism, and it is why Emacs has no menus worth using.\n\n'
                'It also means the editor can describe itself, which is the '
                'part worth building a habit around. `C-h k` followed by any '
                'key says what that key does and names the command behind it. '
                '`C-h f` describes a command by name. `C-h b` lists every '
                'binding active right now.\n\n'
                'Those three turn Emacs from something you memorise into '
                'something you interrogate. A key did something surprising: '
                'C-h k it and find out what it was. You half remember a '
                'command name: M-x and TAB through the completions.\n\n'
                '**The minibuffer is where all of this happens**, at the very '
                'bottom of the screen. It is an ordinary buffer that takes '
                'over the last line, the usual editing keys work in it, and '
                'C-g always abandons whatever it is asking.\n\n'
                'TAB at the M-x prompt is not decoration. Type `white` and '
                'TAB and you get `whitespace-mode` and a handful of cousins, '
                'including commands you have never bound and would never have '
                'searched for by exact name. A typo that matches nothing just '
                'sits there; another TAB says `[No match]`. C-g leaves the '
                'prompt. The same completion works after C-h f, so the loop '
                'is: wonder what it is called, type a fragment, read the '
                'list, then C-h f the one that looks right before you run it. '
                'C-a, C-e, C-k and yank all work inside the minibuffer, which '
                'is how you edit a long M-x name rather than deleting it and '
                'starting again.'
            ),
            'examples': [
                {
                    'label': 'The self-documenting part',
                    'code': ('C-h k <key>   what does this key do?\n'
                             'C-h f <name>  what does this command do?\n'
                             'C-h b         every binding, right now\n'
                             'C-h t         the built-in tutorial'),
                    'note': 'C-h k is the one to build a reflex around. It '
                            'answers "what did I just press" faster than any '
                            'search engine.',
                },
                {
                    'label': 'Running a command by name',
                    'code': ('M-x replace-string RET\n'
                             'M-x whitespace-mode RET\n'
                             '\n'
                             'TAB completes, and completing a\n'
                             'half-remembered name is how you find things'),
                    'note': 'Anything bound to a key can be run this way, and '
                            'the great majority of commands are bound to no '
                            'key at all.',
                },
            ],
            'misconceptions': [
                'M-x is not a shell. It runs Emacs commands, not programs; '
                'M-x shell is the command that gets you a shell.',
                'C-h is not help-about-Emacs. It is a prefix, and the key '
                'after it chooses what kind of description you want.',
                'A command with no key binding is not a lesser command. Most '
                'of Emacs has no binding, because there are not enough keys.',
            ],
            'try_it': [
                'Press C-h k and then C-x C-s. Read what it says the command '
                'is called.',
                'Run M-x and type "buffer", then press TAB to see how many '
                'commands you have never heard of.',
            ],
        },
        {
            'id': 'em-files',
            'title': 'Files, and where your settings live',
            'concept': (
                'Find-file is how you open a path, including one that does '
                'not exist yet. That is why a new file is just a name you '
                'save later. `C-x C-f` opens it, and the prompt is the same '
                'minibuffer with TAB completion.\n\n'
                '`C-x C-s` saves this buffer. `C-x C-w` saves it somewhere '
                'else, which is Save As. `C-x s` offers to save every '
                'modified buffer one at a time.\n\n'
                '**Emacs writes two kinds of file next to yours and both are '
                'deliberate.** `notes.txt~` is the backup of the previous '
                'version. `#notes.txt#` is an auto-save, written every few '
                'hundred keystrokes, and it is what survives a crash. Seeing '
                'them is not a fault, and deleting them is safe once you have '
                'saved.\n\n'
                '**Your configuration is `~/.emacs.d/init.el`**, and it is '
                'Emacs Lisp, evaluated top to bottom at startup. You do not '
                'need to write any to use the editor. When you do, `M-x '
                'eval-buffer` applies it without restarting, and that is the '
                'loop: edit init.el, evaluate, keep going.\n\n'
                'If Emacs offers to recover a file on visit, it found a '
                '`#name#` newer than the file on disk. That is the crash path '
                'working. `M-x recover-this-file` is the deliberate version, '
                'and declining the offer leaves the auto-save in place so '
                'you can try again. Two Emacs editing the same file is a '
                'different warning: a symlink lock in the same directory, '
                '`.#notes.txt`, pointing at the first session. That is not a '
                'backup. It is how the second session knows to ask before it '
                'overwrites the first.'
            ),
            'examples': [
                {
                    'label': 'Opening and saving',
                    'code': ('C-x C-f   open a file, or make one\n'
                             'C-x C-s   save this buffer\n'
                             'C-x C-w   save it under another name\n'
                             'C-x s     save all, asking about each'),
                    'note': 'find-file on a name that does not exist is the '
                            'normal way to start a new file. Nothing is '
                            'written until you save.',
                },
                {
                    'label': 'The files Emacs leaves lying about',
                    'code': ('notes.txt     yours\n'
                             'notes.txt~    the previous version\n'
                             '#notes.txt#   auto-save, for a crash\n'
                             '\n'
                             'both are configurable, neither is a bug'),
                    'note': 'If Emacs offers to recover a file on opening, it '
                            'found one of these newer than the file. M-x '
                            'recover-this-file is the deliberate version.',
                },
            ],
            'misconceptions': [
                'find-file does not fail on a name that does not exist. It '
                'opens an empty buffer pointed at that name, which is how new '
                'files are made.',
                'The tilde and hash files are not temporary junk from a '
                'crash. They are written during normal use and are how a '
                'crash becomes survivable.',
                'init.el is not required. Emacs runs perfectly with no '
                'configuration at all, and starting with none is a reasonable '
                'way to learn what is actually yours.',
            ],
            'try_it': [
                'Open a file that does not exist with C-x C-f, type a line, '
                'and save it. Then look at the directory and find the backup.',
                'Run M-x describe-variable on user-init-file to see exactly '
                'which configuration file this Emacs is using.',
            ],
        },
    ],

    # ------------------------------------------------------------------
    'drills': [
        {'id': 'em-d-quit', 'type': 'keys', 'keys': ['C-x', 'C-c'],
         'prompt': 'Quit Emacs.',
         'teach': 'The one to know before anything else. Emacs asks about '
                  'unsaved buffers on the way out, so it is safe when lost.'},
        {'id': 'em-d-save', 'type': 'keys', 'keys': ['C-x', 'C-s'],
         'prompt': 'Save the current buffer.',
         'teach': 'Not Ctrl-S, which freezes a terminal. If that happens, C-q '
                  'unfreezes it and your keystrokes were all received.'},
        {'id': 'em-d-cancel', 'type': 'keys', 'keys': ['C-g'],
         'prompt': 'Cancel the sequence you are half way through.',
         'teach': 'The most useful key in the editor. It returns you to a '
                  'known state from a prefix, a prompt or a runaway command.'},
        {'id': 'em-d-search', 'type': 'keys', 'keys': ['C-s'],
         'prompt': 'Start incremental search.',
         'teach': 'Each character narrows the match. C-s again is the next '
                  'hit. C-g returns to where you started. If the screen '
                  'freezes and the echo area is empty, that was the terminal: '
                  'Ctrl-Q.'},
        {'id': 'em-d-query-replace', 'type': 'keys', 'keys': ['M-%'],
         'prompt': 'Start query-replace.',
         'teach': 'It asks on each hit. replace-string does not. Use the one '
                  'that asks until the pattern is boring.'},
        {'id': 'em-d-open', 'type': 'keys', 'keys': ['C-x', 'C-f'],
         'prompt': 'Open a file.',
         'teach': 'find-file, and it makes the buffer whether or not the file '
                  'exists, which is also how you start a new one.'},
        {'id': 'em-d-buffer', 'type': 'keys', 'keys': ['C-x', 'b'],
         'prompt': 'Switch to another buffer by name.',
         'teach': 'Note the plain b with no Control. A prefix does not make '
                  'the rest of the sequence into chords.'},
        {'id': 'em-d-list', 'type': 'keys', 'keys': ['C-x', 'C-b'],
         'prompt': 'List every open buffer.',
         'teach': 'The one with Control on both keys lists them; the one '
                  'without switches. They are one keystroke apart on purpose.'},
        {'id': 'em-d-kill-buf', 'type': 'keys', 'keys': ['C-x', 'k'],
         'prompt': 'Close the current buffer.',
         'teach': 'Kills the buffer, which is closing the file. Closing the '
                  'window with C-x 0 leaves the buffer open behind it.'},
        {'id': 'em-d-split-below', 'type': 'keys', 'keys': ['C-x', '2'],
         'prompt': 'Split the screen into two windows, one above the other.',
         'teach': 'The digit is a plain digit. C-x 3 splits side by side, and '
                  'C-x 1 collapses back to one.'},
        {'id': 'em-d-only', 'type': 'keys', 'keys': ['C-x', '1'],
         'prompt': 'Close every window except this one.',
         'teach': 'The panic button when help buffers and compilation output '
                  'have filled the screen. Nothing is lost: buffers survive.'},
        {'id': 'em-d-other', 'type': 'keys', 'keys': ['C-x', 'o'],
         'prompt': 'Move the cursor to the other window.',
         'teach': 'o for other. It cycles when there are more than two.'},
        {'id': 'em-d-mark-all', 'type': 'keys', 'keys': ['C-x', 'h'],
         'prompt': 'Mark the whole buffer as the region.',
         'teach': 'C-x h is the region sort-lines wants when you mean every line.'},
        {'id': 'em-d-mark', 'type': 'keys', 'keys': ['C-SPC'],
         'prompt': 'Set the mark, to start selecting.',
         'teach': 'Everything between the mark and the cursor is the region. '
                  'There is no highlight to maintain.'},
        {'id': 'em-d-copy', 'type': 'keys', 'keys': ['M-w'],
         'prompt': 'Copy the region.',
         'teach': 'M-w copies, C-w kills. The pair to keep straight, because '
                  'one of them removes the text.'},
        {'id': 'em-d-yank', 'type': 'keys', 'keys': ['C-y'],
         'prompt': 'Yank back the last thing you killed.',
         'teach': 'And M-y straight afterwards cycles further back through '
                  'the kill ring, which is a clipboard with history.'},
        {'id': 'em-d-word-fwd', 'type': 'keys', 'keys': ['M-f'],
         'prompt': 'Move forward one word.',
         'teach': 'C- is characters, M- is words, and the letter means the '
                  'same direction at both scales.'},
        {'id': 'em-d-eol', 'type': 'keys', 'keys': ['C-e'],
         'prompt': 'Move to the end of the line.',
         'teach': 'C-a is the start. These two are worth having before any '
                  'of the fancier motions.'},
        {'id': 'em-d-buf-end', 'type': 'keys', 'keys': ['M->'],
         'prompt': 'Move to the end of the buffer.',
         'teach': 'M-< is the start. The angle brackets point the way they '
                  'go, which is the only mnemonic you need.'},
        {'id': 'em-d-mx', 'type': 'keys', 'keys': ['M-x'],
         'prompt': 'Run a command by name.',
         'teach': 'Every key runs a named command, and most commands have no '
                  'key at all. TAB completes at the prompt.'},
        # Typed rather than captured: C-h and Backspace are the same byte
        # without the Kitty protocol, so a capture drill here would grade a
        # keystroke it cannot actually tell apart. validate.py catches this.
        {'id': 'em-d-describe', 'type': 'recall', 'keys': ['C-h', 'k'],
         'prompt': 'Ask what a key does.',
         'teach': 'Then press the key. This is how Emacs is meant to be '
                  'learned: interrogated rather than memorised.'},
        {'id': 'em-d-undo', 'type': 'keys', 'keys': ['C-/'],
         'prompt': 'Undo the last change.',
         'teach': 'C-x u does the same thing. Emacs undo is a ring rather '
                  'than a stack, so undoing an undo is redo.'},
        {'id': 'em-d-kill-line', 'type': 'keys', 'keys': ['C-k'],
         'prompt': 'Kill from the cursor to the end of the line.',
         'teach': 'Killed text goes on the ring, so C-k C-k C-k then C-y '
                  'moves three lines rather than losing them.'},
    ],

    # ------------------------------------------------------------------
    'challenges': [
        {
            'id': 'em-ch-sort-mx',
            'title': 'Run a command you have never heard of',
            'goal': 'Sort the lines of a buffer without knowing the binding, because there is not one. This is the M-x habit: the command exists, it has a sensible name, and you can find it by typing part of it.',
            'setup': {'kind': 'emacs',
                      'start': ['pear', 'apple', 'cherry', 'banana']},
            'solution': {
                'elisp': '(progn (sort-lines nil (point-min) (point-max)))'},
            'steps': [
                {'instruction': 'Select the whole buffer. C-x h marks everything.',
                 'hint': 'C-x h'},
                {'instruction': 'Run the sort command by name. Start typing "sort-" and let TAB show you what exists.',
                 'hint': 'M-x sort-lines'},
                {'instruction': 'Save and quit.',
                 'hint': 'C-x C-s then C-x C-c'},
            ],
            'free': 'Sort the four lines alphabetically using a named command rather than retyping them, then save.',
            'verify': {'kind': 'emacs',
                       'expect': {'lines': ['apple', 'banana', 'cherry', 'pear']}},
            'fallback': 'self',
        },
        {
            'id': 'em-ch-replace',
            'title': 'Replace every occurrence, and notice what that costs',
            'goal': 'A blunt replace-string across a buffer, including the one place you probably did not want it. Reading the result is the lesson.',
            'setup': {'kind': 'emacs',
                      'start': ['host = localhost',
                                'backup = localhost',
                                '# localhost is the default']},
            'solution': {
                'elisp': '(progn (goto-char (point-min)) (while (search-forward "localhost" nil t) (replace-match "db01")))'},
            'steps': [
                {'instruction': 'Go to the top of the buffer. replace-string only works forward from point.',
                 'hint': 'M-<'},
                {'instruction': 'Replace every localhost with db01.',
                 'hint': 'M-x replace-string RET localhost RET db01 RET'},
                {'instruction': 'Look at the comment line. It changed too, because a blunt replace has no idea what a comment is.'},
                {'instruction': 'Save and quit.', 'hint': 'C-x C-s then C-x C-c'},
            ],
            'free': 'Replace every occurrence of localhost with db01, then read all three lines and consider which one you would not have wanted changed.',
            'verify': {'kind': 'emacs',
                       'expect': {'lines': ['host = db01', 'backup = db01',
                                            '# db01 is the default']}},
            'fallback': 'self',
        },

        {
            'id': 'em-ch-edit-save',
            'title': 'Edit a line and save it, with no evil mode',
            'goal': 'Change one word using plain Emacs editing, save the '
                    'buffer, and leave. No modal editing and no leader key: '
                    'this is the editor underneath.',
            'setup': {'kind': 'emacs',
                      'start': ['hello world here', 'leave this line alone']},
            'solution': {
                'elisp': '(progn (goto-char (point-min)) (forward-word 2) '
                         '(backward-kill-word 1) (insert "EARTH"))'},
            'steps': [
                {'instruction': 'Move to the start of the buffer.',
                 'hint': 'M-<'},
                {'instruction': 'Move forward to the word "world".',
                 'hint': 'M-f moves a word at a time'},
                {'instruction': 'Remove the word and type EARTH in its place.',
                 'hint': 'M-DEL kills the word behind the cursor'},
                {'instruction': 'Save the buffer.', 'hint': 'C-x C-s'},
                {'instruction': 'Quit Emacs.', 'hint': 'C-x C-c'},
            ],
            'free': 'Change "world" to "EARTH", save, and quit. Plain Emacs '
                    'keys only.',
            'verify': {'kind': 'emacs',
                       'expect': {'lines': ['hello EARTH here',
                                            'leave this line alone']}},
            'fallback': 'self',
        },
        {
            'id': 'em-ch-kill-yank',
            'title': 'Move a line with the kill ring',
            'goal': 'Use the mark, a kill and a yank to move a line, which is '
                    'the Emacs answer to cut and paste and behaves better '
                    'than one.',
            'setup': {'kind': 'emacs',
                      'start': ['second', 'first', 'third']},
            'solution': {
                'elisp': '(progn (goto-char (point-min)) '
                         '(kill-whole-line) (forward-line 1) (yank))'},
            'steps': [
                {'instruction': 'Put the cursor on the line reading "second".',
                 'hint': 'M-< is the top of the buffer'},
                {'instruction': 'Kill the whole line, newline included.',
                 'hint': 'C-a then C-k C-k, or M-x kill-whole-line'},
                {'instruction': 'Move down one line, past "first".',
                 'hint': 'C-n'},
                {'instruction': 'Yank the killed line back in.',
                 'hint': 'C-y'},
                {'instruction': 'Save and quit.', 'hint': 'C-x C-s then C-x C-c'},
            ],
            'free': 'Reorder the lines to first, second, third by killing and '
                    'yanking rather than retyping.',
            'verify': {'kind': 'emacs',
                       'expect': {'lines': ['first', 'second', 'third']}},
            'fallback': 'self',
        },
    ],

    # ------------------------------------------------------------------
    'quiz': [
        {'id': 'em-q-prefix', 'type': 'mcq',
         'prompt': 'You press C-x and nothing happens. What is going on?',
         'answer': 'It is a prefix, and Emacs is waiting for the rest of the '
                   'sequence.',
         'distractors': ['The binding is unset in this buffer.',
                         'The terminal swallowed the Control key.',
                         'Emacs has hung and needs to be killed.'],
         'teach': 'The echo area shows C-x- while it waits. C-g abandons the '
                  'sequence, which is why it is the first key worth knowing.'},
        {'id': 'em-q-window', 'type': 'mcq',
         'prompt': 'You close a window with C-x 0. What happened to the file?',
         'answer': 'Nothing. The buffer is still open and C-x b returns to it.',
         'distractors': ['It was closed, and unsaved changes were lost.',
                         'It was saved and then closed.',
                         'It was closed but the backup file remains.'],
         'teach': 'Windows show buffers, they do not own them. C-x k is the '
                  'one that closes the file, and it asks if it is modified.'},
        {'id': 'em-q-frozen', 'type': 'mcq',
         'prompt': 'The display stopped updating after you pressed Ctrl-S. '
                   'What fixes it?',
         'answer': 'C-q, which resumes the terminal output.',
         'distractors': ['C-g, which cancels the stuck command.',
                         'C-x C-c, since Emacs has to be restarted.',
                         'Nothing. The session is lost.'],
         'teach': 'This is terminal flow control, older than Emacs and '
                  'nothing to do with it. Every keystroke was received while '
                  'the screen looked frozen.'},
        {'id': 'em-q-region', 'type': 'mcq',
         'prompt': 'You set a mark, moved a long way, and pressed C-w. Why '
                   'did so much disappear?',
         'answer': 'C-w kills the region, which is everything between the '
                   'mark and the cursor.',
         'distractors': ['C-w kills the current word and repeated it.',
                         'The mark moved with the cursor as you travelled.',
                         'C-w kills to the end of the buffer by default.'],
         'teach': 'The mark stays where you set it. C-y brings it all back, '
                  'and C-g clears a stale mark before it catches you again.'},
        {'id': 'em-q-mx', 'type': 'mcq',
         'prompt': 'A key did something you did not expect. What finds out '
                   'what it was?',
         'answer': 'C-h k, then press the key again.',
         'distractors': ['M-x, then type the key.',
                         'C-h b, which is the only way to see a binding.',
                         'Reading init.el, since bindings live there.'],
         'teach': 'C-h k names the command and shows its documentation. It is '
                  'the habit that turns Emacs from memorisation into lookup.'},
    ],
}
