"""Doom Emacs: only the layer that is Doom's.

**This module deliberately does not teach modal editing.** Doom runs `(evil
+everywhere)`, so `ciw`, `daw`, `%` and the whole verb-plus-motion grammar are
identical to the vim module, which owns the `modal-grammar` pack per D9. Doom
declares vim as a prereq and starts where vim stops. Repeating the grammar here
would double the authoring and, worse, let the two copies drift.

What is genuinely Doom's, and therefore what is here: the `SPC` leader tree and
why discoverability is the whole design, workspaces, the way buffers and
windows are reached, popup rules, and the specific places where evil inside
Emacs is *not* vim. The vanilla `C-x` and `C-c` bindings arrive as the last
lesson, framed as the layer underneath, never as a parallel track. Learning
both at once is a reliable way to learn neither.

**The survival keys are the exception, and they go first.** That rule above put
`C-x C-c`, what a chord is, and the fact that `SPC f s` is three presses into
lesson nine of nine. All true, all arriving after the eight lessons and every
challenge that assume them. A student testing this module read the whole
opening, pressed Enter on a challenge, and could not get out of the editor,
which is not a pacing problem but a stranding one. So lesson one is now how to
quit and how to cancel, and the distinction between a chord and a sequence,
because the notation is unreadable without it. That is not the same thing as
teaching the vanilla binding system as a parallel track: it is four keys and a
piece of syntax, and the rest still waits for lesson nine.

Drills are **capture type**. `SPC` is an ordinary space in normal mode and
nothing intercepts it, so `SPC f s` is graded as the actual keystroke.
"""

MODULE = {
    'id': 'doom',
    'title': 'Doom Emacs',
    'group': 'Editors',
    'blurb': 'The SPC tree, workspaces, and where evil stops being vim.',
    'context': 'You are in Doom Emacs, in evil normal mode, with a file open. SPC is the leader.',
    'needs': ('emacs',),
    'prereqs': ['vim'],
    'adapter': 'emacs',
    'estimate': '3-5 hours',
    'order': 42,

    # ------------------------------------------------------------------
    'lessons': [
        {
            'id': 'doom-survive',
            'title': 'Getting in, and getting back out',
            'next': 'doom-what',
            'concept': (
                'Two things stop a first session dead, and neither of them is '
                'interesting enough to be anyone\'s favourite lesson. They go '
                'first anyway, because everything after this assumes you can '
                'get out of the editor you are about to be dropped into.\n\n'
                'This module assumes the vim module. Doom runs evil, so `ciw`, '
                '`daw` and the rest of the verb-plus-motion grammar are '
                'already yours. If `ciw` is not in your fingers, do vim '
                'first. The rest of these lessons will not reteach it.\n\n'
                '**C-x C-c quits Emacs.** Doom\'s own quit is `SPC q q`, '
                'three presses on the leader tree. Either one leaves. Closing '
                'the terminal window works too, in the sense that a fire '
                'solves a kitchen, and it takes anything you had not saved '
                'with it.\n\n'
                '**C-g cancels whatever Emacs is in the middle of.** A '
                'half-typed key sequence, a prompt you did not mean to open, '
                'a minibuffer asking a question you do not understand: C-g '
                'puts you back in a normal buffer. Press it twice if once did '
                'nothing. It is the most useful key in Emacs and the one '
                'nobody is told about.\n\n'
                '**Now the notation, because the rest of this module is '
                'written in it.** C-x means hold Control and press x. M-x '
                'means hold Meta, which is Alt on most keyboards, and press '
                'x. Written together, C-x C-c is one then the other: Control '
                'and x, then Control and c.\n\n'
                'SPC f s is a different animal. Those are three separate '
                'presses, space then f then s, with nothing held down at all. '
                'A chord is keys at the same time; a sequence is keys one '
                'after another. Doom\'s leader tree is sequences, Emacs\'s own '
                'bindings are chords, and telling them apart on sight is most '
                'of what makes the notation readable.\n\n'
                'The next lesson is which of the three layers you just used: '
                'Emacs, evil, or Doom, because the same key can belong to any '
                'of them and the fix depends on which.'
            ),
            'examples': [
                {
                    'label': 'The keys that get you unstuck',
                    'code': ('C-g        cancel whatever is happening\n'
                             'ESC        back to normal mode, if you are in '
                             'insert\n'
                             'C-x C-s    save this file\n'
                             'C-x C-c    quit Emacs\n'
                             'SPC h k    what does this key do?'),
                    'note': 'C-g and C-x C-c are worth having in your fingers '
                            'before you need either of them.',
                },
                {
                    'label': 'Chord or sequence',
                    'code': ('C-x C-c    two chords, one after the other\n'
                             '           hold Ctrl, x. hold Ctrl, c.\n'
                             '\n'
                             'SPC f s    three presses, nothing held\n'
                             '           space. f. s.'),
                    'note': 'If SPC types a space instead of opening the '
                            'menu, you are in insert mode. Press ESC first.',
                },
            ],
            'misconceptions': [
                'C-x C-c is not "close this file". It quits Emacs entirely, '
                'though it will ask about unsaved buffers before it goes.',
                'C-g is not undo. It abandons the command in progress and '
                'changes nothing you have already typed.',
                'SPC is only the leader in normal mode. In insert mode it is '
                'a space, which is why the leader appears to stop working '
                'right after you type something.',
            ],
            'try_it': [
                'Run `emacs` with no arguments. Press C-g a few times, then '
                'quit with C-x C-c. Doing it once on purpose is worth more '
                'than reading it twice.',
                'Press SPC and wait a second without pressing anything else. '
                'The menu that appears is the subject of the next lesson.',
                'If `ciw` is not automatic, stop and do the vim module '
                'before continuing.',
            ],
        },
        {
            'id': 'doom-what',
            'title': 'What Doom actually is',
            'next': 'doom-leader',
            'concept': (
                'The last lesson used keys from all three layers without '
                'naming them. Doom is not an editor. It is a configuration '
                'framework for '
                'Emacs, which means three separate things are in play and '
                'confusing them is the main source of frustration.\n\n'
                'EMACS is the program: a Lisp interpreter that happens to edit '
                'text. EVIL is a package that reimplements vim inside it, which '
                'is why your normal-mode grammar transfers unchanged. DOOM is a '
                'curated set of packages and bindings on top of both, organised '
                'around a leader key.\n\n'
                'So when something does not work, the useful question is which '
                'layer owns it. A motion that misbehaves is evil. A missing '
                'command is a Doom module you have not enabled. An error '
                'mentioning a function name is Emacs, and it is telling you '
                'more than you think.\n\n'
                '`doom sync` is the command that makes a change to `init.el` '
                'or `packages.el` real. Those files are a shopping list: they '
                'do not take effect until Doom installs and compiles what they '
                'name. Edit `init.el`, skip `doom sync`, restart, and nothing '
                'changed. That is the failure that looks like "Doom ignored '
                'me". It did not. You updated a list and never asked it to '
                'go shopping. `config.el` is different: it is evaluated at '
                'startup, so a restart (or `SPC h r r`) is enough.\n\n'
                'The next lesson is the tree those leader keys hang from, and '
                'why waiting after `SPC` is the documentation, not a lag.'
            ),
            'examples': [
                {
                    'label': 'Three layers, three places to look',
                    'code': ('Doom     ~/.config/doom/init.el      modules\n'
                             '         ~/.config/doom/config.el    your settings\n'
                             '         ~/.config/doom/packages.el  extra packages\n'
                             '\n'
                             'evil     vim bindings inside Emacs\n'
                             'Emacs    everything underneath'),
                    'note': 'After editing init.el or packages.el you must run '
                            '`doom sync`. After editing config.el you usually '
                            'need only a restart.',
                },
                {
                    'label': 'Which file, which command',
                    'code': ('init.el / packages.el   doom sync, then restart\n'
                             'config.el               SPC h r r, or restart\n'
                             '\n'
                             '~/.config/emacs/bin/doom   the binary, not PATH'),
                    'note': 'doom is rarely on PATH until you put it there. '
                            'The full path is the one that always works.',
                },
            ],
            'misconceptions': [
                'Doom is not a fork of Emacs. You are running stock Emacs with '
                'a large configuration, and every piece of Emacs documentation '
                'still applies.',
                'The `doom` command is not usually on your PATH. It lives in '
                '`~/.config/emacs/bin/doom`, and forgetting this is why people '
                'think `doom sync` is broken.',
                'Your normal-mode keys are evil, not Doom. Anything you learned '
                'in the vim module works here unchanged.',
            ],
            'try_it': [
                'Run `~/.config/emacs/bin/doom doctor`. It checks your install '
                'and tells you what is missing.',
            ],
        },
        {
            'id': 'doom-leader',
            'title': 'The SPC tree, and why it is a tree',
            'next': 'doom-files',
            'concept': (
                'The leader tree is how you reach every Doom command without '
                'memorising a chord. That is why you press `SPC` and wait: '
                'the menu is the map. In normal mode, `SPC` is '
                'the leader. Everything Doom adds '
                'hangs off it in a tree grouped by noun: `SPC f` for files, '
                '`SPC b` for buffers, `SPC w` for windows, `SPC p` for '
                'projects, `SPC g` for git, `SPC s` for search.\n\n'
                'The important part is what happens when you press `SPC` and '
                'wait. A menu appears showing every next key and what it does. '
                'This is the design: you are not expected to memorise the tree, '
                'you are expected to walk it and let the menu teach you.\n\n'
                'A chord you must remember (`C-x C-s`) is gone if you forget '
                'it. A tree you can pause on is still there: you press `SPC`, '
                'read `f` for files, press `f`, read `s` for save. The delay '
                'before the menu is which-key doing its job, not Emacs being '
                'slow. Turn the delay to zero and you lose the only map.\n\n'
                'That changes how to learn Doom. Do not look bindings up. Press '
                '`SPC`, read, and pick. The ones you use daily will become '
                'muscle memory on their own, and the rest stay discoverable '
                'forever. If `SPC` types a space, you are in insert mode: '
                'Escape first. That is the same wrong-mode failure the vim '
                'module named, and it is the most common "leader is broken" '
                'report.\n\n'
                'The next lesson is the first three branches you will live '
                'in: files, buffers, and projects, which are three different '
                'questions and not three names for open.'
            ),
            'examples': [
                {
                    'label': 'The tree by first key',
                    'code': ('SPC f   files        SPC b   buffers\n'
                             'SPC w   windows      SPC p   projects\n'
                             'SPC s   search       SPC g   git\n'
                             'SPC h   help         SPC c   code\n'
                             'SPC o   open         SPC q   quit and session\n'
                             'SPC TAB workspaces   SPC :   run a command'),
                    'note': 'Nouns, not verbs. Decide what kind of thing you '
                            'want first, then what to do with it.',
                },
                {
                    'label': 'When you are lost',
                    'code': ('SPC        wait, and read the menu\n'
                             'SPC h b b  search every binding\n'
                             'SPC h f    what does this function do\n'
                             'SPC h k    what does this key do'),
                    'note': '`SPC h` is the most valuable branch of the tree '
                            'and the one people never open.',
                },
            ],
            'misconceptions': [
                '`SPC` is only the leader in normal mode. In insert mode it '
                'inserts a space, which is the answer to "why did my leader '
                'stop working".',
                'The popup menu is not a delay to be tuned away. It is the '
                'documentation, and it appears exactly when you have paused '
                'because you were unsure.',
                'You do not need to memorise the tree before using Doom. Almost '
                'nobody knows all of it, including people who have used it for '
                'years.',
            ],
            'try_it': [
                'Press `SPC` and just read the menu for thirty seconds. Then '
                'press `h` and read that one too.',
            ],
        },
        {
            'id': 'doom-files',
            'title': 'Files, buffers and projects',
            'next': 'doom-windows',
            'concept': (
                'The last lesson was the tree. Three different questions, '
                'three different branches, and '
                'picking the wrong one is the most common beginner stumble.\n\n'
                '`SPC f f` finds a file by path, starting where you are. `SPC '
                'b b` switches to a buffer you already have open. `SPC SPC` '
                'finds a file inside the current project, which is usually what '
                'you actually wanted.\n\n'
                'A buffer is a file in memory, the same idea as the last vim '
                'lesson. `SPC f f` on a path you have not opened yet creates '
                'a buffer with no file on disk until you save. `SPC f s` then '
                'asks where to write it, because there is no path yet. That '
                'is not a broken save. It is Emacs refusing to invent a name. '
                'People hit `SPC f s` on the `*scratch*` buffer and think '
                'Doom ate the binding.\n\n'
                'Saving is `SPC f s`. It is worth typing that a hundred times '
                'until it is reflex, because it is the one binding you will use '
                'more than any other.\n\n'
                'The next lesson is what happens when one file is not enough: '
                'windows that split the frame, and workspaces that keep a '
                'layout per task.'
            ),
            'examples': [
                {
                    'label': 'Reaching things',
                    'code': ('SPC SPC    find file in project    <- the usual one\n'
                             'SPC f f    find file by path\n'
                             'SPC f s    save\n'
                             'SPC f r    recently opened files\n'
                             'SPC b b    switch buffer\n'
                             'SPC b k    kill this buffer\n'
                             'SPC ,      switch buffer, short form\n'
                             'SPC p p    switch project'),
                    'note': 'A project is usually a git repository. Doom works '
                            'that out on its own.',
                },
                {
                    'label': 'Three questions',
                    'code': ('already open?     SPC b b\n'
                             'in this repo?     SPC SPC\n'
                             'somewhere else?   SPC f f\n'
                             '\n'
                             'no path yet?      SPC f s will ask for one'),
                    'note': 'Scratch and new unsaved buffers have no file. '
                            'Save then has to invent one.',
                },
            ],
            'misconceptions': [
                'Killing a buffer does not close the file on disk, and finding '
                'a file that is already open does not open it twice.',
                '`SPC f f` starting in the wrong directory is not a bug. It '
                'starts from the current buffer\'s directory, which is why '
                '`SPC SPC` is usually the better question.',
                'A file outside any project still works. Doom just cannot offer '
                'you project-wide search for it.',
            ],
            'try_it': [
                'Open a git repository, press `SPC SPC`, and type three letters '
                'of a filename. Then do the same with `SPC f f` and notice the '
                'difference.',
            ],
        },
        {
            'id': 'doom-windows',
            'title': 'Windows and workspaces',
            'next': 'doom-evil-gaps',
            'concept': (
                'A window is how you show two buffers at once. A workspace '
                'is how you keep a layout per task. That is why a split is '
                'for now, and a workspace is for switching context. Windows '
                'split the frame, exactly as they do in vim, and the '
                'bindings live under `SPC w`. Because evil is running, `C-w v` '
                'and `C-w s` work too, and most people end up using those.\n\n'
                'WORKSPACES are Doom\'s addition and they have no vim '
                'equivalent. A workspace is a named set of windows and buffers, '
                'so you can keep one per task and switch without losing your '
                'layout. They live under `SPC TAB`.\n\n'
                'If tmux is already in your fingers, the mental model is the '
                'same shape: workspace is to Doom roughly what session is to '
                'tmux, and window is to Doom what pane is to tmux.\n\n'
                '`C-x C-c` from a split still quits Emacs. It does not close '
                'the split. That is the first-lesson exit key, and it does '
                'the same thing in a one-window frame and a four-window one. '
                '`SPC w c` or `C-w c` closes this window. `C-x C-c` is how '
                'people lose an unsaved buffer in the other split because they '
                'wanted "close this pane" and got "quit the program".\n\n'
                'The next lesson is where evil stops being the vim you already '
                'know: the seams, not the grammar. The vim module still owns '
                '`ciw`.'
            ),
            'examples': [
                {
                    'label': 'Windows',
                    'code': ('SPC w v   split vertically     C-w v  same thing\n'
                             'SPC w s   split horizontally   C-w s  same thing\n'
                             'SPC w c   close this window    C-w c\n'
                             'SPC w o   close every other    C-w o\n'
                             'C-w h j k l   move between windows'),
                    'note': 'The C-w forms come from evil and are usually '
                            'faster. Learn those.',
                },
                {
                    'label': 'Workspaces',
                    'code': ('SPC TAB n   new workspace\n'
                             'SPC TAB d   delete this workspace\n'
                             'SPC TAB r   rename it\n'
                             'SPC TAB .   switch to one\n'
                             'SPC TAB 1   go to workspace 1'),
                    'note': 'One workspace per task, not per file. They are for '
                            'context switching, not organisation.',
                },
            ],
            'misconceptions': [
                'A workspace is not a tab bar. The bar at the top showing them '
                'is a display of workspaces, not a list of files.',
                'Closing every other window with `C-w o` does not kill those '
                'buffers. They are still open and `SPC b b` will find them.',
                'Deleting a workspace does not kill its buffers either. Doom '
                'keeps buffers globally and workspaces are views onto them.',
            ],
            'try_it': [
                'Create a workspace with `SPC TAB n`, open two files in it, '
                'switch away with `SPC TAB .`, and come back.',
            ],
        },
        {
            'id': 'doom-evil-gaps',
            'title': 'Where evil is not vim',
            'next': 'doom-search',
            'concept': (
                'The seams are how you tell when evil is still vim and when '
                'Emacs is answering instead. That is why a missing `:command` '
                'is usually `M-x` or `SPC :`, not a broken install. Evil is '
                'a faithful reimplementation, and the grammar you '
                'learned transfers essentially unchanged. Do not relearn '
                '`ciw` here; the vim module already owns it. But it is running '
                'inside Emacs, and there are seams. Knowing where they are '
                'saves an afternoon.\n\n'
                'The `:` commands are the biggest one. Some ex commands exist, '
                'many do not, and the real interface underneath is `SPC :` or '
                '`M-x`, which runs Emacs commands by name. When a `:something` '
                'does not exist, the answer is almost always an Emacs command '
                'with a longer name.\n\n'
                'The other seam is undo. Doom uses Emacs undo underneath, so '
                'the granularity can differ from vim, and `SPC` bindings that '
                'run Emacs commands may group differently than you expect. '
                '`C-g` is the Emacs-shaped Escape: it aborts a minibuffer, a '
                'half-typed `SPC` sequence, or a prompt you did not mean to '
                'open. Escape still returns to normal mode. They are not '
                'interchangeable, which is why a stuck minibuffer ignores '
                'Escape and yields to `C-g`.\n\n'
                'Window keys are the third seam. `C-w` is evil\'s, and it '
                'works. `C-x 2` is Emacs\'s, and it also works. Mixing them '
                'is fine. Looking for vim\'s `:sp` and finding nothing is '
                'how you discover `SPC w s`.\n\n'
                '`gc` is a Doom operator, not a vim one: `gc` plus a motion '
                'comments that region, `gcc` comments the line, `gc2j` is '
                'this line and the two below. It uses the same grammar as '
                '`d` and `c`. That is why it feels like vim and is not in '
                'the vim module.\n\n'
                'The next lesson is search, which in a large project replaces '
                'most of the navigation you just learned.'
            ),
            'examples': [
                {
                    'label': 'The seams',
                    'code': (':w :q :wq :e     work as you expect\n'
                             ':%s/a/b/g        works\n'
                             ':set             mostly does not; use Emacs vars\n'
                             '\n'
                             'SPC :  or  M-x   run any Emacs command by name\n'
                             'SPC h k          ask what a key really does'),
                    'note': '`SPC h k` then pressing the key is the fastest way '
                            'to find out which layer owns a binding.',
                },
                {
                    'label': 'Escape versus C-g',
                    'code': ('Esc    back to normal mode\n'
                             'C-g    abort whatever Emacs is doing\n'
                             '\n'
                             'stuck in a prompt?     C-g\n'
                             'typed i by accident?   Esc'),
                    'note': 'The first lesson named both. This is why they '
                            'are not the same key with two labels.',
                },
            ],
            'misconceptions': [
                'Your `.vimrc` does not apply and never will. Doom configuration '
                'is elisp in `~/.config/doom/config.el`.',
                'Plugins do not carry over. The Doom equivalent is a module in '
                '`init.el` or a package in `packages.el`, followed by `doom '
                'sync`.',
                '`:set number` may appear to do nothing. Line numbers are a '
                'Doom setting (`display-line-numbers-type`) rather than a vim '
                'option.',
            ],
            'try_it': [
                'Press `SPC h k` then `SPC f s`. Read which function it runs. '
                'That is the layer underneath showing itself.',
            ],
        },
        {
            'id': 'doom-search',
            'title': 'Search, and why it replaces navigation',
            'concept': (
                'The last lesson was the seams. In a large project, searching '
                'beats browsing, and Doom leans '
                'hard on that. `SPC s p` searches every file in the project and '
                'gives you a live-filtered list of results.\n\n'
                'This changes how you move around. Rather than remembering where '
                'a function lives, search for its name and jump. Rather than '
                'opening a file tree, `SPC SPC` and type three letters.\n\n'
                '`/` still searches this buffer and still composes with '
                'operators, exactly as the vim module taught. `SPC s p` is a '
                'different question: every file in the project. Searching the '
                'buffer you are not in is the usual miss: you typed `/TODO` '
                'and the other file is full of them. `SPC s p` then `TODO` is '
                'the one that finds them.\n\n'
                'The search results buffer is itself editable in Doom, which is '
                'the feature nobody discovers: you can filter to the matches you '
                'want and apply an edit across all of them at once.\n\n'
                'The next lesson is magit, which is the same idea applied to '
                'git: a menu instead of a memory test, still sitting on the '
                'model the git module taught.'
            ),
            'examples': [
                {
                    'label': 'Finding things',
                    'code': ('SPC s p   search the whole project\n'
                             'SPC s b   search this buffer\n'
                             'SPC s d   search this directory\n'
                             'SPC *     search the project for the word\n'
                             '          under the cursor\n'
                             'SPC s i   jump to a heading or symbol'),
                    'note': '`SPC *` is the fastest way to answer "where else '
                            'is this used".',
                },
                {
                    'label': 'This buffer versus the project',
                    'code': ('/TODO          this buffer, a vim motion\n'
                             'SPC s b TODO   this buffer, a live list\n'
                             'SPC s p TODO   every file in the project\n'
                             'SPC *          the word under the cursor,\n'
                             '               across the project'),
                    'note': '/ still composes: d/foo works. SPC s p does not, '
                            'because it is a different tool.',
                },
            ],
            'misconceptions': [
                'Search does not replace the vim `/` motion. `/` still searches '
                'the current buffer and still composes with operators, so `d/foo` '
                'works.',
                'Project search needs ripgrep. If `SPC s p` is slow or missing, '
                '`doom doctor` will tell you.',
            ],
            'try_it': [
                'Put the cursor on any identifier in a project and press '
                '`SPC *`.',
            ],
            'next': 'doom-magit',
        },
        {
            'id': 'doom-magit',
            'title': 'magit: git as a menu, not a memory test',
            'next': 'doom-config',
            'concept': (
                'magit is the reason a lot of people use Emacs at all, and Doom '
                'ships it. It is a front end to the git model, so it assumes you '
                'hold what the git module teaches: commits, the index, refs, '
                'branches. What it removes is the memorising. `SPC g g` opens '
                'the status buffer, and from there every action is a single key '
                'with a menu one keystroke away.\n\n'
                'The status buffer is the whole interface. It shows unstaged and '
                'staged changes as foldable sections. `Tab` expands a section to '
                'show which files changed, and again to show the diff. On any '
                'change, `s` stages it and `u` unstages it, and crucially you '
                'can stage a single hunk, or even a single line in visual mode, '
                'rather than the whole file. That is the feature that changes '
                'how you commit: small, reviewed commits become easy.\n\n'
                'Committing is `c c`, which opens a message buffer; write it and '
                'finish with `C-c C-c`. Pushing is `P p`, pulling is `F p`, '
                'fetching is `f`. Branches live under `b`, and `l l` shows the '
                'log. Every one of those top keys opens a transient menu of '
                'options, so you are never guessing at flags: press `P` and the '
                'push menu shows you `-f`, upstream, and the rest.\n\n'
                'The thing to internalise is that magit is not a different git. '
                'It runs the same commands you would type, shows you what it is '
                'about to do, and lets you stage at a finer grain than the '
                'command line makes comfortable. When it does something you did '
                'not expect, `$` shows the actual git commands it ran.\n\n'
                'The next lesson is how to change Doom itself without the '
                'change vanishing on restart.'
            ),
            'examples': [
                {
                    'label': 'The status buffer, and staging',
                    'code': ('SPC g g   open the magit status buffer\n'
                             'Tab       fold or unfold a section into its diff\n'
                             's         stage the change at point\n'
                             'u         unstage it\n'
                             'S         stage everything\n'
                             'x         discard a change (careful)'),
                    'note': 'On a single hunk, s stages just that hunk. In '
                            'visual mode, s stages just the selected lines.',
                },
                {
                    'label': 'Committing, and moving commits around',
                    'code': ('c c   start a commit, then C-c C-c to finish\n'
                             'c a   amend the last commit\n'
                             'P p   push        F p   pull        f u   fetch\n'
                             'b b   switch branch   b c   create one\n'
                             'l l   show the log     $     show the git it ran'),
                    'note': 'Each capital opens a transient menu of flags, so '
                            'the options are shown rather than memorised.',
                },
            ],
            'misconceptions': [
                'magit is not a simplified git. It exposes more of git than the '
                'CLI does comfortably, especially hunk-level and line-level '
                'staging.',
                'The commit message buffer is a normal buffer. You finish with '
                '`C-c C-c`, not by saving, and `C-c C-k` cancels.',
                'If you do not hold the git model, magit will not teach it. Do '
                'the git module first; magit is the interface, not the course.',
            ],
            'try_it': [
                'In a scratch git repo, change a file, press `SPC g g`, stage '
                'it with `s`, and commit with `c c` then `C-c C-c`.',
            ],
        },
        {
            'id': 'doom-config',
            'title': 'Changing Doom without breaking it',
            'next': 'doom-vanilla',
            'concept': (
                'The last lesson was magit. This one is the files that make '
                'Doom yours. Three files, and knowing which one takes which '
                'kind of change is most of the skill.\n\n'
                '`init.el` is a list of MODULES to enable, mostly by '
                'uncommenting. `packages.el` declares extra packages Doom does '
                'not ship. `config.el` is your own settings and bindings.\n\n'
                'The rule that catches everyone: after changing `init.el` or '
                '`packages.el` you must run `doom sync`, because those files '
                'decide what gets installed. Changing `config.el` needs only a '
                'restart, or `SPC h r r` to reload.\n\n'
                '`doom sync` rebuilds the autoloads and installs what '
                '`packages.el` named. It does not evaluate `config.el`. That '
                'is why a new package you listed is still missing until sync, '
                'and a `setq` you just wrote is missing until reload. A '
                'package uncommented in `init.el` and never synced is the '
                'same vanishing act as the second lesson: the list changed, '
                'the install did not. `doom doctor` is the next thing to run '
                'when a module you enabled still has no keys: it will name '
                'the missing binary or the module that did not load.\n\n'
                '`SPC f p` opens those three files. The last lesson is the '
                'layer they sit on, and why this module kept it until now.'
            ),
            'examples': [
                {
                    'label': 'The loop',
                    'code': ('SPC f p            open a Doom config file\n'
                             '# edit init.el, uncomment a module\n'
                             '~/.config/emacs/bin/doom sync\n'
                             '# restart Emacs\n'
                             '\n'
                             'SPC h r r          reload config.el without a\n'
                             '                   restart'),
                    'note': 'Put `~/.config/emacs/bin` on your PATH once and '
                            '`doom sync` stops being annoying.',
                },
                {
                    'label': 'A setting in config.el',
                    'code': ("(setq display-line-numbers-type 'relative)\n"
                             '(setq doom-theme (quote doom-one))'),
                    'note': 'This is elisp, not a config format. Anything Emacs '
                            'can do, this file can do.',
                },
            ],
            'misconceptions': [
                'Editing `init.el` without running `doom sync` does nothing, '
                'and this is the single most common Doom frustration.',
                '`doom doctor` is not just for installation problems. Run it '
                'whenever something is mysteriously missing.',
                'You do not need to understand elisp to configure Doom. You do '
                'need to keep the parentheses balanced.',
            ],
            'try_it': [
                'Open `init.el` with `SPC f p`, read the module list, and find '
                'three you have never enabled.',
            ],
        },
        {
            'id': 'doom-vanilla',
            'title': 'The layer underneath',
            'concept': (
                'Vanilla chords are how you read Emacs documentation and '
                'survive a minibuffer that is not running evil. That is why '
                'this lesson is last: learn them as a reading skill, not as '
                'a second editor.\n\n'
                'You need them anyway, for two reasons. Some places do not run '
                'evil, particularly minibuffer prompts. And every piece of Emacs '
                'documentation, every StackOverflow answer, and every package '
                'README is written in `C-x` and `C-c`.\n\n'
                'Learn the handful that appear constantly and let the rest stay '
                'foreign. You are not switching; you are gaining the ability to '
                'read.\n\n'
                '`M-x` is the way out when the tree has no leaf for what you '
                'want. Type a few letters of the command name and Emacs '
                'completes it. That is also how you survive a broken binding: '
                'the function still exists, the key does not. `SPC :` is the '
                'same prompt with a Doom-shaped entrance. `C-g` cancels it, '
                'which is why that key was lesson one and this is lesson ten.\n\n'
                'The vanilla Emacs module exists if you want the other half as '
                'its own course. This module stops here, because the job was '
                'the Doom layer on top of the vim grammar you already have.'
            ),
            'examples': [
                {
                    'label': 'The ones that repay learning',
                    'code': ('C-g       cancel, the Emacs Escape\n'
                             'M-x       run a command by name\n'
                             'C-x C-s   save        (SPC f s in Doom)\n'
                             'C-x C-f   find file   (SPC f f)\n'
                             'C-x b     switch buffer\n'
                             'C-x C-c   quit Emacs\n'
                             'C-/       undo'),
                    'note': '`C-g` is the important one. It cancels a half-typed '
                            'command anywhere, including where Escape does not.',
                },
                {
                    'label': 'Reading the notation',
                    'code': ('C-x       hold Control, press x\n'
                             'M-x       hold Alt (Meta), press x\n'
                             'C-x C-s   two chords in sequence\n'
                             'C-c p f   a chord then two plain keys'),
                    'note': 'Same idea as the tmux prefix and the Doom leader: a '
                            'prefix, then a command key.',
                },
            ],
            'misconceptions': [
                'These are not an alternative to the `SPC` tree. They are what '
                'the `SPC` tree calls underneath, which is why `SPC h k` shows '
                'you a function name.',
                '`C-g` and Escape are not the same. Escape returns to normal '
                'mode, `C-g` aborts whatever Emacs is in the middle of.',
            ],
            'try_it': [
                'Start typing `C-x` and then press `C-g`. Nothing happens, '
                'which is the point.',
            ],
        },
    ],

    # ------------------------------------------------------------------
    # Drill: capture type. SPC is an ordinary key in normal mode.
    # ------------------------------------------------------------------
    'drills': [
        {'id': 'doom-quit', 'type': 'keys', 'keys': ['SPC', 'q', 'q'],
         'prompt': 'Quit Doom using the leader tree.',
         'teach': 'SPC q q is Doom\'s quit. C-x C-c is Emacs\'s. Either leaves.'},
        {'id': 'doom-gc', 'type': 'keys', 'keys': ['g', 'c', 'c'],
         'prompt': 'Comment the current line with the Doom operator.',
         'teach': 'gc is an operator: gcc the line, gc2j this line and two down.'},
        {'id': 'doom-save', 'type': 'keys', 'keys': ['SPC', 'f', 's'],
         'prompt': 'Save the current file.',
         'teach': 'The binding you will use more than any other. Worth typing '
                  'a hundred times until it is reflex.'},
        {'id': 'doom-find-project', 'type': 'keys', 'keys': ['SPC', 'SPC'],
         'prompt': 'Find a file inside the current project.',
         'teach': 'Usually the question you actually meant, rather than SPC f f '
                  'which starts from a path.'},
        {'id': 'doom-find-file', 'type': 'keys', 'keys': ['SPC', 'f', 'f'],
         'prompt': 'Find a file by path, starting from this buffer\'s directory.',
         'teach': "It starts at this buffer's directory rather than the "
                  'project root: that is what makes it the right pick for a '
                  'neighbouring file, and SPC SPC the right pick inside a '
                  'project.'},
        {'id': 'doom-recent', 'type': 'keys', 'keys': ['SPC', 'f', 'r'],
         'prompt': 'Reopen something from your recent files.',
         'teach': 'The mnemonic is file-recent. It searches everything you '
                  'have opened across sessions, which usually beats '
                  'remembering the path.'},
        {'id': 'doom-config-file', 'type': 'keys', 'keys': ['SPC', 'f', 'p'],
         'prompt': 'Open one of your Doom configuration files.',
         'teach': 'Saves remembering where ~/.config/doom actually is.'},
        {'id': 'doom-buffer', 'type': 'keys', 'keys': ['SPC', 'b', 'b'],
         'prompt': 'Switch to another open buffer.',
         'teach': 'SPC , is the short form and worth learning second.'},
        {'id': 'doom-kill-buffer', 'type': 'keys', 'keys': ['SPC', 'b', 'k'],
         'prompt': 'Close the current buffer without closing the window.',
         'teach': 'Buffers and windows are separate things: killing the '
                  'buffer frees the file, and the window stays and shows '
                  'something else.'},
        {'id': 'doom-project', 'type': 'keys', 'keys': ['SPC', 'p', 'p'],
         'prompt': 'Switch to a different project.',
         'teach': 'A project is anything with a .git (or a .project marker). '
                  'After switching, SPC SPC finds files inside it only.'},
        {'id': 'doom-search-project', 'type': 'keys', 'keys': ['SPC', 's', 'p'],
         'prompt': 'Search every file in the current project.',
         'teach': 'In a large project, searching beats browsing. This is how '
                  'you navigate.'},
        {'id': 'doom-search-buffer', 'type': 'keys', 'keys': ['SPC', 's', 'b'],
         'prompt': 'Search within the current buffer.',
         'teach': 'The mnemonic is search-buffer. Its sibling SPC s p '
                  'searches the whole project, and both preview matches as '
                  'you type.'},
        {'id': 'doom-search-word', 'type': 'keys', 'keys': ['SPC', '*'],
         'prompt': 'Search the project for the word under the cursor.',
         'teach': 'The fastest answer to "where else is this used".'},
        {'id': 'doom-window-vsplit', 'type': 'keys', 'keys': ['SPC', 'w', 'v'],
         'prompt': 'Split the window vertically, using the leader.',
         'teach': 'C-w v does the same and comes from evil. Most people end up '
                  'using that one.'},
        {'id': 'doom-window-evil', 'type': 'keys', 'keys': ['C-w', 'v'],
         'prompt': 'Split the window vertically, the evil way.',
         'teach': 'Identical to SPC w v. Your vim fingers already know it.'},
        {'id': 'doom-window-close', 'type': 'keys', 'keys': ['SPC', 'w', 'c'],
         'prompt': 'Close the current window, leaving the buffer open.',
         'teach': 'The buffer survives: closing a window just stops '
                  'displaying it. SPC b k is the one that actually kills the '
                  'buffer.'},
        {'id': 'doom-workspace-new', 'type': 'keys', 'keys': ['SPC', 'TAB', 'n'],
         'prompt': 'Create a new workspace.',
         'teach': 'One workspace per task, not per file. They exist for context '
                  'switching.'},
        {'id': 'doom-workspace-switch', 'type': 'keys',
         'keys': ['SPC', 'TAB', '.'],
         'prompt': 'Switch to a different workspace.',
         'teach': 'Workspaces are whole window layouts. SPC TAB alone shows '
                  'the list, and the dot means pick one by name.'},
        {'id': 'doom-git', 'type': 'keys', 'keys': ['SPC', 'g', 'g'],
         'prompt': 'Open magit, the git interface.',
         'teach': 'Magit assumes you already hold git\'s model: commits, refs, '
                  'the index. It is a front end, not a tutorial.'},

        # magit-internal keys: recall, because they are pressed inside the
        # magit buffer rather than in evil normal mode, so capturing them in
        # the trainer's context would grade the wrong thing.
        {'id': 'doom-magit-stage', 'type': 'recall', 'keys': ['s'],
         'prompt': 'In the magit status buffer, stage the change at point.',
         'teach': 'u unstages. On a single hunk, s stages just that hunk, '
                  'which is the finer grain the command line makes awkward.'},
        {'id': 'doom-magit-commit', 'type': 'recall', 'keys': ['c', 'c'],
         'prompt': 'In magit, start a commit.',
         'teach': 'It opens a message buffer. You finish with C-c C-c, not by '
                  'saving, and C-c C-k cancels.'},
        {'id': 'doom-magit-push', 'type': 'recall', 'keys': ['P', 'p'],
         'prompt': 'In magit, push to the upstream.',
         'teach': 'Capital P opens a transient menu showing every push option, '
                  'so -f and the rest are displayed rather than remembered.'},
        {'id': 'doom-magit-log', 'type': 'recall', 'keys': ['l', 'l'],
         'prompt': 'In magit, show the commit log.',
         'teach': 'F p pulls, f u fetches from upstream, b b switches branch. The status '
                  'buffer is the hub they all return to.'},
        {'id': 'doom-help-key', 'type': 'keys', 'keys': ['SPC', 'h', 'k'],
         'prompt': 'Ask what a key is actually bound to.',
         'teach': 'The fastest way to find out which of the three layers owns a '
                  'binding.'},
        {'id': 'doom-help-binding', 'type': 'keys', 'keys': ['SPC', 'h', 'b', 'b'],
         'prompt': 'Search every keybinding Doom currently has.',
         'teach': 'The answer machine for this entire module: type any '
                  'fragment of a description and it shows the chord bound to '
                  'it.'},
        {'id': 'doom-reload', 'type': 'keys', 'keys': ['SPC', 'h', 'r', 'r'],
         'prompt': 'Reload your config.el without restarting Emacs.',
         'teach': 'The mnemonic is help-reload. It re-evaluates your config '
                  'in place; only package changes need the slower doom sync '
                  'and restart.'},
        {'id': 'doom-command', 'type': 'keys', 'keys': ['SPC', ':'],
         'prompt': 'Run any Emacs command by name.',
         'teach': 'The same thing as M-x. When a :ex command does not exist, '
                  'this is where the real one lives.'},
        {'id': 'doom-cancel', 'type': 'keys', 'keys': ['C-g'],
         'prompt': 'Abort whatever Emacs is in the middle of.',
         'teach': 'Not the same as Escape. Escape returns to normal mode; C-g '
                  'cancels a half-typed command, including where Escape will '
                  'not help you.'},
        {'id': 'doom-vanilla-save', 'type': 'keys', 'keys': ['C-x', 'C-s'],
         'prompt': 'Save, using the binding every Emacs document assumes.',
         'teach': 'You are not switching to these. You are gaining the ability '
                  'to read documentation written in them.'},
        {'id': 'doom-vanilla-mx', 'type': 'keys', 'keys': ['M-x'],
         'prompt': 'Run a command by name, the vanilla way.',
         'teach': 'Every binding is just a name bound to a chord, and M-x '
                  'calls the name directly. If you know the command, you '
                  'never need the binding.'},

        # shell-level, because doom sync is the thing people forget
        {'id': 'doom-sync', 'type': 'command',
         'answer': '~/.config/emacs/bin/doom sync',
         'accepts': ['doom sync'],
         'prompt': 'From your shell: apply a change you made to init.el.',
         'teach': 'Editing init.el without this does nothing at all, and it is '
                  'the single most common Doom frustration.'},
        {'id': 'doom-doctor', 'type': 'command',
         'answer': '~/.config/emacs/bin/doom doctor',
         'accepts': ['doom doctor'],
         'prompt': 'From your shell: check your Doom install for problems.',
         'teach': 'Not only for installation. Run it whenever something is '
                  'mysteriously missing.'},
    ],

    # ------------------------------------------------------------------
    'challenges': [
        {
            'id': 'doom-edit-save',
            'title': 'Edit and save the Doom way',
            'goal': 'Prove your vim grammar works unchanged inside Doom, and '
                    'save with the leader rather than :w.',
            'setup': {'kind': 'emacs',
                      'start': ['hello world here', 'leave this line alone']},
            'solution': {'elisp': '(progn (goto-char (point-min)) '
                                  '(forward-word 2) (backward-kill-word 1) '
                                  '(insert "EARTH"))'},
            'steps': [
                {'instruction': 'Put the cursor inside the word world.',
                 'hint': 'w, exactly as in vim'},
                {'instruction': 'Change the whole word to EARTH.',
                 'hint': 'ciw, exactly as in vim. evil is doing this'},
                {'instruction': 'Return to normal mode and save with the leader.',
                 'hint': 'Esc then SPC f s'},
                {'instruction': 'Quit.', 'hint': 'SPC q q, or C-x C-c'},
            ],
            'free': 'Change "world" to "EARTH" using a text object, save with '
                    'SPC f s, and quit.',
            'verify': {'kind': 'emacs',
                       'expect': {'lines': ['hello EARTH here',
                                            'leave this line alone']}},
            'fallback': 'self',
        },
        {
            'id': 'doom-multi-line',
            'title': 'A macro, inside Doom',
            'goal': 'Confirm that recorded keystrokes work the same here as in '
                    'vim, because evil is doing the recording.',
            'setup': {'kind': 'emacs',
                      'start': ['apples', 'bread', 'coffee', 'dates']},
            'solution': {'elisp': '(progn (goto-char (point-min)) '
                                  '(while (not (eobp)) (beginning-of-line) '
                                  '(insert "- ") (forward-line 1)))'},
            'steps': [
                {'instruction': 'Go to the first line.', 'hint': 'gg'},
                {'instruction': 'Record a macro that prefixes a line with "- " '
                                'and moves down.',
                 'hint': 'qa then I- Esc then j then q'},
                {'instruction': 'Replay it for the remaining lines.',
                 'hint': '3@a'},
                {'instruction': 'Save.', 'hint': 'SPC f s'},
            ],
            'free': 'Prefix all four lines with "- " using a recorded macro, '
                    'then save.',
            'verify': {'kind': 'emacs',
                       'expect': {'lines': ['- apples', '- bread', '- coffee',
                                            '- dates']}},
            'fallback': 'self',
        },
        {
            'id': 'doom-know-your-config',
            'title': 'Read your own configuration',
            'goal': 'Find out what is actually enabled in your Doom install, '
                    'rather than guessing.',
            'setup': {'kind': 'emacs',
                      'start': ['Write the name of one module you found',
                                'enabled in your own init.el, then save.']},
            'solution': {'elisp': '(progn (erase-buffer) (insert "evil\\n"))'},
            'steps': [
                {'instruction': 'Open your Doom config.', 'hint': 'SPC f p'},
                {'instruction': 'Look at the module list in init.el.',
                 'hint': 'the uncommented lines are the enabled ones'},
                {'instruction': 'Come back here and write one module name you '
                                'found, on its own line.',
                 'hint': 'evil is a safe answer, and it is why ciw works'},
                {'instruction': 'Save.', 'hint': 'SPC f s'},
            ],
            'free': 'Look at your own init.el and write the name of one enabled '
                    'module into this buffer, then save.',
            # Two things at once: your config really mentions it, and you really
            # wrote it down. Reading the config is read-only, per D1.
            'verify': {'kind': 'emacs',
                       'expect': {'config_contains': 'evil',
                                  'contains': 'evil'}},
            'fallback': 'self',
        },
        {'id': 'doom-jump-to-line',
         'title': 'Delete a line you found by searching',
         'goal': "Find a line with Doom's search rather than scrolling to "
                 'it, then delete it with the vim command you already '
                 'know.',
         'setup': {'kind': 'emacs',
                   'start': ['keep this one',
                             'DELETE THIS LINE',
                             'and keep this']},
         'solution': {'elisp': '(progn (goto-char (point-min)) '
                               '(search-forward "DELETE THIS LINE") '
                               '(beginning-of-line) (kill-whole-line))'},
         'steps': [{'instruction': 'Search the buffer for the word DELETE.',
                    'hint': 'SPC s b, then type DELETE. Or / like vim'},
                   {'instruction': 'With the cursor on that line, delete '
                                   'the whole line.',
                    'hint': 'dd. evil is providing this, exactly as in '
                            'vim'},
                   {'instruction': 'Save and quit.',
                    'hint': 'SPC f s to save, SPC q q to quit'}],
         'free': 'Delete the line that shouts, keeping the other two.',
         'verify': {'kind': 'emacs',
                    'expect': {'lines': ['keep this one',
                                         'and keep this']}},
         'fallback': 'self'},
        {'id': 'doom-sort-lines',
         'title': 'Use a command you cannot bind',
         'goal': 'Not everything has a key. Run a command by name and '
                 'watch it do more than a keystroke would.',
         'setup': {'kind': 'emacs',
                   'start': ['pear', 'apple', 'cherry', 'banana']},
         'solution': {'elisp': '(sort-lines nil (point-min) (point-max))'},
         'steps': [{'instruction': 'Select the whole buffer.',
                    'hint': 'ggVG in evil, or C-x h'},
                   {'instruction': 'Run the sort-lines command by name.',
                    'hint': 'SPC : opens the command prompt, then type '
                            'sort-lines. M-x does the same'},
                   {'instruction': 'Save and quit.',
                    'hint': 'SPC f s, then SPC q q'}],
         'free': 'Sort the four lines alphabetically.',
         'verify': {'kind': 'emacs',
                    'expect': {'lines': ['apple',
                                         'banana',
                                         'cherry',
                                         'pear']}},
         'fallback': 'self'},
        {'id': 'doom-open-above',
         'title': 'Add a line above the first one',
         'goal': 'Insert a new line above the current one without moving '
                 'to the end of the line above it first.',
         'setup': {'kind': 'emacs', 'start': ['second line', 'third line']},
         'solution': {'elisp': '(progn (goto-char (point-min)) (insert '
                               '"first line\\n"))'},
         'steps': [{'instruction': 'Put the cursor on the first line.',
                    'hint': 'gg'},
                   {'instruction': 'Open a new line above it and start '
                                   'typing.',
                    'hint': 'capital O. Lowercase o opens below'},
                   {'instruction': 'Type "first line", escape, save and '
                                   'quit.',
                    'hint': 'Esc, then SPC f s, then SPC q q'}],
         'free': 'Add "first line" above the two that are there.',
         'verify': {'kind': 'emacs',
                    'expect': {'lines': ['first line',
                                         'second line',
                                         'third line']}},
         'fallback': 'self'},
        {'id': 'doom-replace-all',
         'title': 'Replace every occurrence, the Emacs way',
         'goal': 'Emacs has its own substitute and it is interactive. Use '
                 'it across the whole buffer.',
         'setup': {'kind': 'emacs',
                   'start': ['alpha needs work',
                             'beta needs work',
                             'gamma is fine']},
         'solution': {'elisp': '(progn (goto-char (point-min)) (while '
                               '(search-forward "needs work" nil t)  '
                               '(replace-match "is done")))'},
         'steps': [{'instruction': 'Go to the top of the buffer, because '
                                   'this replaces forward from point.',
                    'hint': 'gg. This is the part people forget'},
                   {'instruction': 'Start a replace across the buffer.',
                    'hint': 'M-x replace-string, or :%s/// which also '
                            'works, because evil'},
                   {'instruction': 'Replace "needs work" with "is done", '
                                   'then save and quit.',
                    'hint': 'SPC f s, then SPC q q'}],
         'free': 'Change every "needs work" to "is done".',
         'verify': {'kind': 'emacs',
                    'expect': {'lines': ['alpha is done',
                                         'beta is done',
                                         'gamma is fine']}},
         'fallback': 'self'},
        {'id': 'doom-config-look',
         'title': 'Find out what a key is actually bound to',
         'goal': 'The single most useful thing in Emacs: ask it what a key '
                 'does, in your configuration, right now.',
         'setup': {'kind': 'emacs', 'start': ['answer here']},
         'solution': {'elisp': '(progn (erase-buffer) (insert '
                               '"evil-window-split\\n"))'},
         'steps': [{'instruction': 'Ask Doom what SPC w s is bound to.',
                    'hint': 'SPC h k, then press the keys. It names the '
                            'command'},
                   {'instruction': 'Replace the line in this buffer with '
                                   'that command name.',
                    'hint': 'the answer starts with evil-window-'},
                   {'instruction': 'Save and quit.',
                    'hint': 'SPC f s, then SPC q q'}],
         'free': 'Write the command name that SPC w s runs into this '
                 'buffer, on its own.',
         'verify': {'kind': 'emacs',
                    'expect': {'contains': 'evil-window-split'}},
         'fallback': 'self'},

        {'id': 'doom-window-split',
         'title': 'Split the frame and put something in it',
         'goal': 'Doom windows are SPC w, and the split you make has to be '
                 'useful rather than decorative.',
         'setup': {'kind': 'emacs',
                   'scratch_name': 'split.txt',
                   'start': ['first line', 'second line', 'third line']},
         'solution': {'elisp': '(progn (split-window-right) '
                               '(goto-char (point-max)) '
                               '(insert "\\nedited in the other window"))'},
         'steps': [{'instruction': 'Split the frame vertically, so there are '
                                   'two windows side by side.',
                    'hint': 'SPC w v, or SPC w /'},
                   {'instruction': 'Move to the other window.',
                    'hint': 'SPC w w cycles, SPC w l goes right'},
                   {'instruction': 'Add a line at the end of the buffer, then '
                                   'save.',
                    'hint': 'G then o, type it, Esc, SPC f s'},
                   {'instruction': 'Note that both windows show the same '
                                   'buffer, so the edit appears in both. That '
                                   'is the buffer and window distinction '
                                   'made visible.'}],
         'free': 'Split the frame, add a line at the end of the buffer from '
                 'the other window, and save.',
         'verify': {'kind': 'emacs',
                    'expect': {'contains': ['first line',
                                            'edited in the other window']}},
         'fallback': 'self'},

        {'id': 'doom-comment-region',
         'title': 'Comment a region with the operator',
         'goal': 'Doom binds commenting as an evil operator, so it composes '
                 'with motions exactly like d and y do.',
         'setup': {'kind': 'emacs',
                   'scratch_name': 'code.py',
                   'start': ['first = 1', 'second = 2', 'third = 3',
                             'keep = 4']},
         'solution': {'elisp': '(progn (goto-char (point-min)) '
                               '(comment-region (point-min) '
                               '(line-end-position 3)))'},
         'steps': [{'instruction': 'Put the cursor on the first line.',
                    'hint': 'gg'},
                   {'instruction': 'Comment the first three lines with the '
                                   'comment operator and a motion.',
                    'hint': 'gc2j, which is gc plus a two-line-down motion'},
                   {'instruction': 'Save. The fourth line should be '
                                   'untouched.',
                    'hint': 'SPC f s'}],
         'free': 'Comment out the first three lines, leaving the fourth '
                 'alone, then save.',
         'verify': {'kind': 'emacs',
                    'expect': {'contains': ['# first = 1', '# third = 3',
                                            'keep = 4']}},
         'fallback': 'self'},


        {'id': 'doom-magit-commit',
         'title': 'Make a real commit through magit',
         'goal': 'The trainer cannot drive magit for you, so this one is on '
                 'your own machine. Do a whole change-stage-commit loop '
                 'without typing a git command.',
         'setup': {'kind': 'self'},
         'steps': [{'instruction': 'Open a scratch git repository in Doom, or '
                                   'make one with SPC : and a shell.'},
                   {'instruction': 'Change a file, then open the magit status '
                                   'buffer.',
                    'hint': 'SPC g g'},
                   {'instruction': 'Expand a change with Tab to see its diff, '
                                   'then stage just one hunk rather than the '
                                   'whole file.',
                    'hint': 'move onto a hunk, press s'},
                   {'instruction': 'Commit it with a message, and finish the '
                                   'message buffer properly.',
                    'hint': 'c c, write the message, C-c C-c'},
                   {'instruction': 'Press $ and read the actual git commands '
                                   'magit ran. They are the ones you already '
                                   'know from the git module.'}],
         'free': 'On your own machine: change a file, stage one hunk in '
                 'magit, commit it with a message, and read back the git '
                 'commands magit ran.',
         'verify': {'kind': 'self'},
         'fallback': 'self'},
                  ],

    # ------------------------------------------------------------------
    'quiz': [
        {'id': 'dq-layers', 'type': 'mcq',
         'prompt': 'Your `ciw` works but `SPC f s` does nothing. Which layer is '
                   'the problem in?',
         'answer': 'Doom, since evil is clearly working.',
         'distractors': ['evil, since a key is not responding.',
                         'Emacs, since the file will not save.',
                         'The terminal, since SPC is being eaten.'],
         'teach': 'Splitting problems by layer is most of debugging Doom. A '
                  'working motion proves evil is fine, so a broken leader '
                  'binding is Doom\'s.'},

        {'id': 'dq-spc-insert', 'type': 'mcq',
         'prompt': 'Why does pressing SPC sometimes just insert a space?',
         'answer': 'You are in insert mode; SPC is only the leader in normal '
                   'mode.',
         'distractors': ['The leader key timed out.',
                         'A popup stole the binding.',
                         'The workspace has no leader configured.'],
         'teach': 'Press Escape and try again. This is the single most common '
                  'moment of "my leader stopped working".'},

        {'id': 'dq-init-sync', 'type': 'mcq',
         'prompt': 'You uncomment a module in init.el and restart Emacs. '
                   'Nothing changed. Why?',
         'answer': 'init.el changes need `doom sync` before they take effect.',
         'distractors': ['You must edit config.el instead.',
                         'Modules only load in a new workspace.',
                         'A restart is not enough; you need to log out.'],
         'teach': 'init.el decides what gets installed, so something has to '
                  'install it. This is the most common Doom frustration and it '
                  'has one answer.'},

        {'id': 'dq-workspace-buffers', 'type': 'mcq',
         'prompt': 'You delete a workspace with SPC TAB d. What happens to the '
                   'files that were open in it?',
         'answer': 'Nothing; the buffers are still open and SPC b b finds them.',
         'distractors': ['They are closed and unsaved changes are lost.',
                         'They move to the default workspace.',
                         'They are saved and then closed.'],
         'teach': 'Doom keeps buffers globally. A workspace is a view onto '
                  'them, not a container that owns them.'},

        {'id': 'dq-find-file', 'type': 'mcq',
         'prompt': 'What is the difference between SPC SPC and SPC f f?',
         'answer': 'SPC SPC searches the project; SPC f f browses from a path.',
         'distractors': ['SPC SPC opens recent files; SPC f f opens any file.',
                         'They are the same, one is just shorter.',
                         'SPC SPC is for buffers; SPC f f is for files.'],
         'teach': 'Choosing the wrong one is the most common early stumble. In '
                  'a project, SPC SPC is nearly always the question you meant.'},

        {'id': 'dq-vimrc', 'type': 'mcq',
         'prompt': 'Where do your vim settings go in Doom?',
         'answer': 'Nowhere; you rewrite them as elisp in config.el.',
         'distractors': ['~/.vimrc is read by evil automatically.',
                         'In init.el, under the evil module.',
                         'In a .vim directory next to your Doom config.'],
         'teach': 'evil reimplements vim\'s editing, not vim\'s configuration '
                  'format. `:set number` does nothing; the Emacs variable does.'},

        {'id': 'dq-cg', 'type': 'mcq',
         'prompt': 'What does C-g do that Escape does not?',
         'answer': 'Aborts whatever Emacs is in the middle of, including where '
                   'Escape will not help.',
         'distractors': ['Nothing; they are bound to the same command.',
                         'Returns to normal mode from insert mode.',
                         'Closes the current popup only.'],
         'teach': 'Escape is an evil idea, C-g is an Emacs one. In a minibuffer '
                  'prompt, C-g is the one that works.'},

        {'id': 'dq-discoverability', 'type': 'mcq',
         'prompt': 'What is the intended way to learn the SPC tree?',
         'answer': 'Press SPC, pause, and read the menu that appears.',
         'distractors': ['Memorise the reference card before starting.',
                         'Rebind the ones you use to something shorter.',
                         'Read init.el to see which are enabled.'],
         'teach': 'The popup is the documentation and it appears exactly when '
                  'you paused because you were unsure. Almost nobody knows the '
                  'whole tree, including long-time users.'},

        {'id': 'dq-prereq', 'type': 'mcq',
         'prompt': 'Why does this module not teach ciw, daw or text objects?',
         'answer': 'They are evil, which is vim, so the vim module already '
                   'taught them.',
         'distractors': ['Doom rebinds them to something else.',
                         'They only work in the vim module\'s challenges.',
                         'Text objects are not available in Emacs.'],
         'teach': 'Doom runs evil, so the grammar is identical. Teaching it '
                  'twice would let the two copies drift apart.'},
    ],
}
