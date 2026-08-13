"""tmux: the first content module.

Drills here are **recall type, not capture type**, and that is a deliberate
constraint rather than a shortcut. tmux binds `C-b`, so a trainer running
inside tmux never sees the prefix, and one running outside tmux would drill the
chord stripped of the context that gives it meaning. Production practice
arrives in Phase 2 as verified challenges: you drive a real session and the
adapter reads `tmux list-panes` back.

Ordering is not alphabetical. The lessons build one model (session, window,
pane) and then spend the rest of the module showing that every binding is a
verb applied to one of those three nouns. Someone who holds that model can
guess bindings they were never taught, which is the actual goal.

All example output is ASCII so it survives the bottom rung of D20.
"""

MODULE = {
    'id': 'tmux',
    'title': 'tmux',
    'group': 'Terminal',
    'blurb': 'Sessions, windows, panes, and the prefix key.',
    'context': 'You are at a shell inside a tmux session. C-b is the prefix, so a chord means: press the prefix, release it, then press the key.',
    'needs': ('tmux',),
    'prereqs': [],
    'adapter': 'tmux',
    'estimate': '2-3 hours',
    'order': 20,

    # ------------------------------------------------------------------
    # Walkthrough
    # ------------------------------------------------------------------
    'lessons': [
        {
            'id': 'tmux-why',
            'title': 'Why tmux exists',
            'next': 'tmux-model',
            'concept': (
                'Everything you run in a terminal is a child of that terminal. '
                'Close the window, drop the SSH connection, or lose the wifi, '
                'and the shell gets a hangup signal and takes your work with '
                'it. A compile halfway through, a download at 90 percent, a '
                'database migration: all gone.\n\n'
                'tmux breaks that link. It runs a server in the background and '
                'your shells are children of the server, not of your terminal. '
                'Your terminal becomes a viewer that can be closed and reopened '
                'without the work noticing.\n\n'
                'That is the whole idea. Every binding you are about to learn '
                'is bookkeeping on top of it. If you learn only one thing from '
                'this module, learn detach and attach.'
            ),
            'examples': [
                {
                    'label': 'The problem',
                    'code': ('$ ssh server\n'
                             '$ ./long-import.sh      # 40 minutes in...\n'
                             'Connection to server closed by remote host.\n'
                             '# the import died with the connection'),
                    'note': 'Nothing you did was wrong. The process was simply '
                            'a child of a connection that ended.',
                },
                {
                    'label': 'The fix',
                    'code': ('$ ssh server\n'
                             '$ tmux new -s import\n'
                             '$ ./long-import.sh\n'
                             '# connection drops, or you press C-b d\n'
                             '$ ssh server\n'
                             '$ tmux attach -t import  # still running'),
                    'note': 'Same command, same machine, and the work survived '
                            'because it belonged to the tmux server.',
                },
            ],
            'misconceptions': [
                'tmux is not a terminal emulator and does not replace ghostty, '
                'Alacritty or iTerm. It runs inside one.',
                'It is not primarily a window manager. Splitting panes is the '
                'feature people notice first and the least important reason to '
                'use it.',
            ],
            'try_it': [
                'Run `tmux new -s scratch`, then `sleep 300`, then close the '
                'entire terminal window. Open a new one and run `tmux attach '
                '-t scratch`. The sleep is still going.',
            ],
        },
        {
            'id': 'tmux-model',
            'title': 'Sessions, windows, panes',
            'next': 'tmux-prefix',
            'concept': (
                'tmux has exactly three levels of container, and almost every '
                'confusion people have with tmux comes from collapsing them '
                'into fewer.\n\n'
                'A SESSION is a workspace. It is the thing that survives when '
                'you detach, and the thing you name. One per project is a good '
                'habit.\n\n'
                'A WINDOW is a full screen inside a session, like a tab. Only '
                'one window is visible at a time.\n\n'
                'A PANE is a rectangle inside a window. A window can be split '
                'into many panes and you see all of them at once.\n\n'
                'Every binding you learn is a verb attached to one of these '
                'three nouns. Once you know which noun a command acts on, you '
                'can usually guess what it does.'
            ),
            'examples': [
                {
                    'label': 'The shape of it',
                    'code': ('session "work"\n'
                             '  +- window 0: editor\n'
                             '  |    +- pane 0 -+- pane 1\n'
                             '  +- window 1: server      <- visible\n'
                             '  +- window 2: logs\n'
                             '\n'
                             'session "notes"\n'
                             '  +- window 0: obsidian'),
                    'note': 'Two independent sessions. Detaching from "work" '
                            'leaves all three of its windows running.',
                },
                {
                    'label': 'What the status bar tells you',
                    'code': ('[work] 0:editor  1:server*  2:logs   "host" 14:32\n'
                             '  ^         ^        ^\n'
                             '  session   window   the * marks the current one'),
                    'note': 'The leftmost bracket is the session name. Read it '
                            'when you are lost.',
                },
            ],
            'misconceptions': [
                'A tmux window is not a window of your terminal emulator. They '
                'are unrelated ideas that share a word, and this is the single '
                'most common source of confusion.',
                'Panes do not survive on their own. Closing the last pane in a '
                'window closes the window; closing the last window ends the '
                'session.',
                'You do not need multiple sessions to use tmux well. Many '
                'people use one session with several windows for years.',
            ],
            'try_it': [
                'In a tmux session run `C-b c` twice, then `C-b w`. The chooser '
                'shows the tree: session at the top, windows underneath.',
            ],
        },
        {
            'id': 'tmux-prefix',
            'title': 'The prefix key',
            'next': 'tmux-panes',
            'concept': (
                'tmux sits between your keyboard and your shell, so it needs a '
                'way to tell "this keystroke is for me" from "this keystroke is '
                'for the program you are running". It does that with a prefix.\n\n'
                'Press `C-b`, release it, then press the command key. `C-b c` '
                'is three physical actions: hold Ctrl and press b, let go, then '
                'press c. It is not a chord, and it is not held down.\n\n'
                'Everything tmux does goes through the prefix. That is why the '
                'bindings are short and unmemorable-looking: they only have to '
                'be unique after the prefix, not unique in your whole shell.'
            ),
            'examples': [
                {
                    'label': 'Three actions, not one',
                    'code': ('C-b        press and release\n'
                             'c          then press this\n'
                             '\n'
                             'wrong:  holding Ctrl the whole time\n'
                             'wrong:  C-b and c at the same moment'),
                    'note': 'A short pause between the two is fine. tmux waits.',
                },
                {
                    'label': 'When you are lost',
                    'code': 'C-b ?      list every binding, q to leave',
                    'note': 'This is the single most useful binding in tmux and '
                            'almost nobody knows it.',
                },
            ],
            'misconceptions': [
                'The prefix is not a modifier. You release it before pressing '
                'the command key.',
                '`C-b` on its own does nothing visible. If you press it and '
                'then think better of it, press Escape or any unbound key.',
                'Many people rebind the prefix to `C-a`, which collides with '
                'the readline binding for start-of-line. Learn the default '
                'first: it is what you will meet on other people\'s machines.',
            ],
            'try_it': [
                'Press `C-b` and wait three seconds before pressing `?`. It '
                'still works, which proves the prefix is not held.',
            ],
        },
        {
            'id': 'tmux-panes',
            'title': 'Panes: splitting and moving',
            'next': 'tmux-windows',
            'concept': (
                'Panes split the current window. The two splitting bindings are '
                'the ones people look up forever, because the mnemonic is '
                'visual rather than verbal.\n\n'
                'Look at the character, not the word. `%` has a vertical bar in '
                'the middle, so it splits into left and right. `"` is two marks '
                'stacked at the top, so it splits into top and bottom.\n\n'
                'The other pane binding worth knowing early is `z`, which zooms '
                'the current pane to fill the window and back again. It is how '
                'you read a stack trace without destroying your layout.'
            ),
            'examples': [
                {
                    'label': 'Split and navigate',
                    'code': ('C-b %      split left | right\n'
                             'C-b "      split top / bottom\n'
                             'C-b o      cycle to the next pane\n'
                             'C-b Left   move to the pane on the left\n'
                             'C-b z      zoom this pane, and again to restore\n'
                             'C-b x      kill this pane, asks first'),
                    'note': 'Directional movement takes arrow keys and is far '
                            'easier to think about than cycling with o.',
                },
                {
                    'label': 'Reading the mnemonic',
                    'code': ('%   has a vertical bar   ->  |  side by side\n'
                             '"   has stacked marks    ->  =  top over bottom'),
                    'note': 'This is worth ten seconds of staring. It is the '
                            'difference between knowing and guessing forever.',
                },
            ],
            'misconceptions': [
                'Zoom is not maximise-and-lose-the-others. The other panes are '
                'still there and still running; press `C-b z` again.',
                '`C-b x` closes a pane, not a window. Closing the last pane in '
                'a window does close the window, which is where people get '
                'surprised.',
                'Panes cannot be moved between sessions directly by splitting. '
                'You want `C-b !` to break a pane out into its own window.',
            ],
            'try_it': [
                'Build this: split side by side, then split the right-hand pane '
                'top and bottom. That is the classic editor-plus-two-terminals '
                'layout and it is `C-b %` then `C-b "`.',
                'Zoom into one pane with `C-b z`, run `htop`, then unzoom.',
            ],
        },
        {
            'id': 'tmux-windows',
            'title': 'Windows: tabs inside a session',
            'next': 'tmux-sessions',
            'concept': (
                'A window is a whole screen inside your session. If panes are '
                'for things you want to watch at once, windows are for things '
                'you want to switch between.\n\n'
                'The bindings mirror what you already know from browser tabs: '
                '`c` creates, `n` and `p` move next and previous, and a digit '
                'jumps straight to that number.\n\n'
                'Name your windows. `C-b ,` renames the current one, and a '
                'status bar reading `0:editor 1:server 2:logs` is worth far '
                'more than `0:zsh 1:zsh 2:zsh`.'
            ),
            'examples': [
                {
                    'label': 'The tab bindings',
                    'code': ('C-b c      create a window\n'
                             'C-b n      next window\n'
                             'C-b p      previous window\n'
                             'C-b 2      jump to window 2\n'
                             'C-b l      last window, the one you came from\n'
                             'C-b ,      rename this window\n'
                             'C-b w      choose from a list\n'
                             'C-b &      kill this window, asks first'),
                    'note': '`C-b l` is the one that pays off daily: it toggles '
                            'between two windows the way alt-tab does.',
                },
            ],
            'misconceptions': [
                'Window numbers are not stable. Kill window 1 and the others '
                'keep their numbers, leaving a gap, so `C-b 2` may not be the '
                'third window.',
                '`C-b w` shows windows across every session, not just this one, '
                'which makes it a fast way to jump between projects.',
            ],
            'try_it': [
                'Create three windows, name them with `C-b ,`, and watch the '
                'status bar fill in. Then jump between them by number.',
            ],
        },
        {
            'id': 'tmux-sessions',
            'title': 'Sessions: detach and attach',
            'next': 'tmux-copy',
            'concept': (
                'This is the lesson that pays for the whole module. Detaching '
                'leaves everything running and hands your terminal back. '
                'Attaching picks it up exactly where you left it, from any '
                'terminal, on any connection.\n\n'
                'Detach with `C-b d`. Nothing stops. The status bar disappears '
                'and you are back at your shell, and the session is still there '
                'in the background.\n\n'
                'Most session work happens from the shell rather than through '
                'the prefix, because you usually want it before you are inside '
                'tmux at all.'
            ),
            'examples': [
                {
                    'label': 'From the shell',
                    'code': ('$ tmux new -s work      create and attach\n'
                             '$ tmux ls               list sessions\n'
                             '$ tmux attach -t work   attach to one\n'
                             '$ tmux new -d -s bg     create without attaching\n'
                             '$ tmux kill-session -t work'),
                    'note': '`tmux a` is a valid abbreviation of attach, and '
                            '`tmux new` of new-session.',
                },
                {
                    'label': 'From inside',
                    'code': ('C-b d      detach, leave it running\n'
                             'C-b s      choose another session\n'
                             'C-b $      rename this session'),
                    'note': '`C-b s` switches sessions without detaching, which '
                            'is how you keep several projects open at once.',
                },
                {
                    'label': 'What ls looks like',
                    'code': ('$ tmux ls\n'
                             'notes: 1 windows (created Tue Aug 12 09:02:11)\n'
                             'work: 3 windows (created Tue Aug 12 08:40:55) '
                             '(attached)'),
                    'note': 'The `(attached)` marker tells you which one some '
                            'terminal is currently viewing.',
                },
            ],
            'misconceptions': [
                'Detaching is not closing. This is the single most important '
                'sentence in this module.',
                'A session with no name gets a number, and `tmux ls` showing '
                '`0:` and `1:` is a sign you should have used `-s`.',
                '`tmux kill-session` kills the processes inside it. There is no '
                'undo and no confirmation.',
                'Rebooting the machine does end every session. tmux survives '
                'disconnection, not restarts.',
            ],
            'try_it': [
                'Start `tmux new -s test`, run `top`, detach with `C-b d`, and '
                'confirm with `tmux ls` that it is still there. Then attach '
                'again and quit properly.',
            ],
        },
        {
            'id': 'tmux-copy',
            'title': 'Copy mode: scrolling and copying',
            'next': 'tmux-config',
            'concept': (
                'Your terminal\'s scrollback does not work the way you expect '
                'inside tmux, because tmux is drawing the screen and keeps its '
                'own history per pane. To look at it you enter copy mode.\n\n'
                '`C-b [` enters copy mode. Now the pane is frozen and your keys '
                'move a cursor instead of going to the shell. Arrow keys and '
                'PageUp scroll. `q` leaves.\n\n'
                'Copying is a three-step ritual: start a selection, extend it, '
                'confirm it. With the default key table that is Space, then '
                'movement, then Enter. Paste back with `C-b ]`.\n\n'
                'This is the part of tmux people bounce off, and the reason is '
                'almost always that they did not realise they had changed mode.'
            ),
            'examples': [
                {
                    'label': 'The ritual',
                    'code': ('C-b [      enter copy mode\n'
                             'PageUp     scroll back\n'
                             'Space      start selecting\n'
                             '(move)     extend the selection\n'
                             'Enter      copy it and leave copy mode\n'
                             'C-b ]      paste into any pane\n'
                             'q          leave without copying'),
                    'note': 'With `setw -g mode-keys vi` the movement keys '
                            'become hjkl and selection becomes v and y.',
                },
            ],
            'misconceptions': [
                'In copy mode you are not at a shell prompt any more. Typing a '
                'command does nothing useful, and this is why it feels broken.',
                'The tmux buffer is not your system clipboard. Pasting into a '
                'browser needs `C-b ]` into something else, or a clipboard '
                'integration you set up on purpose.',
                'Your mouse scroll wheel may appear to work and may be '
                'scrolling your terminal emulator instead of the pane, showing '
                'you the wrong history.',
            ],
            'try_it': [
                'Run `ls -la /usr/bin` in a pane, enter copy mode, page back to '
                'the top, select a filename, and paste it into another pane.',
            ],
        },
        {
            'id': 'tmux-config',
            'title': 'A config worth having',
            'concept': (
                'Default tmux is usable and you should learn it first, because '
                'it is what exists on every server you will ever log into. But '
                'four settings are worth adding once the defaults are in your '
                'fingers.\n\n'
                'Start window numbering at 1, because the 0 key is at the wrong '
                'end of the keyboard. Turn the mouse on for resizing panes. Use '
                'vi keys in copy mode if you use vi keys anywhere else. Raise '
                'the history limit, because the default runs out.\n\n'
                'Resist the urge to rebind the prefix until you have used the '
                'default for a month.'
            ),
            'examples': [
                {
                    'label': '~/.tmux.conf',
                    'code': ('set -g base-index 1\n'
                             'setw -g pane-base-index 1\n'
                             'set -g mouse on\n'
                             'setw -g mode-keys vi\n'
                             'set -g history-limit 50000'),
                    'note': 'Reload without restarting: `C-b :` then '
                            '`source-file ~/.tmux.conf`.',
                },
            ],
            'misconceptions': [
                'A config change does not apply to running sessions until you '
                'reload it, and some settings only apply to new windows.',
                'Turning the mouse on breaks terminal-native text selection. '
                'Hold Shift while dragging to get it back.',
            ],
            'try_it': [
                'Write the five lines above, reload with `C-b :` and '
                '`source-file ~/.tmux.conf`, and check that a new window is '
                'numbered 1.',
            ],
        },
    ],

    # ------------------------------------------------------------------
    # Drill: recall type, per the module docstring
    # ------------------------------------------------------------------
    'drills': [
        # panes
        {'id': 'tmux-split-h', 'type': 'recall', 'keys': ['C-b', '%'],
         'prompt': 'Split the current pane into left and right.',
         'teach': 'The % character has a vertical bar through the middle. '
                  'That bar is the split you get.'},
        {'id': 'tmux-split-v', 'type': 'recall', 'keys': ['C-b', '"'],
         'prompt': 'Split the current pane into top and bottom.',
         'teach': 'The " character is two marks stacked at the top, and you '
                  'get a stacked split.'},
        {'id': 'tmux-pane-next', 'type': 'recall', 'keys': ['C-b', 'o'],
         'prompt': 'Cycle to the next pane.',
         'teach': 'o for "other". Fine with two panes, awkward with five, '
                  'which is why the arrow bindings exist.'},
        {'id': 'tmux-pane-left', 'type': 'recall', 'keys': ['C-b', 'Left'],
         'prompt': 'Move to the pane to the left of this one.',
         'teach': 'Directional movement beats cycling as soon as you have '
                  'more than two panes.'},
        {'id': 'tmux-pane-zoom', 'type': 'recall', 'keys': ['C-b', 'z'],
         'prompt': 'Zoom this pane to fill the window, and back again.',
         'teach': 'Nothing is lost while zoomed. The other panes keep running '
                  'and press it again to restore the layout.'},
        {'id': 'tmux-pane-kill', 'type': 'recall', 'keys': ['C-b', 'x'],
         'prompt': 'Close the current pane.',
         'teach': 'It asks first. Closing the last pane in a window also '
                  'closes the window.'},
        {'id': 'tmux-pane-numbers', 'type': 'recall', 'keys': ['C-b', 'q'],
         'prompt': 'Show the pane numbers so you can jump to one.',
         'teach': 'The numbers flash up briefly; press one while it is showing '
                  'to jump straight there.'},
        {'id': 'tmux-pane-last', 'type': 'recall', 'keys': ['C-b', ';'],
         'prompt': 'Jump to the last pane you were in.',
         'teach': 'The pane-level equivalent of alt-tab.'},
        {'id': 'tmux-pane-break', 'type': 'recall', 'keys': ['C-b', '!'],
         'prompt': 'Break this pane out into a window of its own.',
         'teach': 'Useful when a pane you meant to glance at turns into the '
                  'thing you are actually working on.'},
        {'id': 'tmux-pane-rotate', 'type': 'recall', 'keys': ['C-b', 'C-o'],
         'prompt': 'Rotate the panes within the window.',
         'teach': 'Note this one keeps Ctrl held for the second key, which is '
                  'unusual and worth remembering.'},

        # windows
        {'id': 'tmux-win-new', 'type': 'recall', 'keys': ['C-b', 'c'],
         'prompt': 'Create a new window.',
         'teach': 'c for create. The new window becomes the current one.'},
        {'id': 'tmux-win-next', 'type': 'recall', 'keys': ['C-b', 'n'],
         'prompt': 'Go to the next window.',
         'teach': 'n for next, p for previous. They wrap around.'},
        {'id': 'tmux-win-prev', 'type': 'recall', 'keys': ['C-b', 'p'],
         'prompt': 'Go to the previous window.',
         'teach': 'p for previous, not paste. Paste is C-b ].'},
        {'id': 'tmux-win-last', 'type': 'recall', 'keys': ['C-b', 'l'],
         'prompt': 'Toggle back to the window you were just in.',
         'teach': 'l for last. This is the highest-value window binding and '
                  'the least known.'},
        {'id': 'tmux-win-number', 'type': 'recall', 'keys': ['C-b', '2'],
         'prompt': 'Jump straight to window number 2.',
         'teach': 'Numbers are positions, not identities: killing a window '
                  'leaves a gap rather than renumbering.'},
        {'id': 'tmux-win-rename', 'type': 'recall', 'keys': ['C-b', ','],
         'prompt': 'Rename the current window.',
         'teach': 'A status bar reading 0:editor 1:server beats 0:zsh 1:zsh.'},
        {'id': 'tmux-win-choose', 'type': 'recall', 'keys': ['C-b', 'w'],
         'prompt': 'Show an interactive list of windows to choose from.',
         'teach': 'It lists windows in every session, so it doubles as a way '
                  'to jump between projects.'},
        {'id': 'tmux-win-kill', 'type': 'recall', 'keys': ['C-b', '&'],
         'prompt': 'Close the current window.',
         'teach': 'It asks first. Closing the last window ends the session.'},

        # sessions and modes
        {'id': 'tmux-detach', 'type': 'recall', 'keys': ['C-b', 'd'],
         'prompt': 'Detach from this session, leaving everything running.',
         'teach': 'd for detach. This is the binding the whole tool exists '
                  'for. Nothing stops.'},
        {'id': 'tmux-sess-choose', 'type': 'recall', 'keys': ['C-b', 's'],
         'prompt': 'Switch to a different session without detaching.',
         'teach': 'How you keep several projects open and move between them.'},
        {'id': 'tmux-sess-rename', 'type': 'recall', 'keys': ['C-b', '$'],
         'prompt': 'Rename the current session.',
         'teach': 'Worth doing the moment tmux ls starts showing bare numbers.'},
        {'id': 'tmux-cmd-prompt', 'type': 'recall', 'keys': ['C-b', ':'],
         'prompt': 'Open the tmux command prompt.',
         'teach': 'Everything a binding does is a command underneath, and this '
                  'is where you type them: source-file, new-window, set -g.'},
        {'id': 'tmux-copy-mode', 'type': 'recall', 'keys': ['C-b', '['],
         'prompt': 'Enter copy mode so you can scroll back through the pane.',
         'teach': 'The bracket points backwards, into history. C-b ] pastes '
                  'forwards out of it.'},
        {'id': 'tmux-paste', 'type': 'recall', 'keys': ['C-b', ']'],
         'prompt': 'Paste the most recent tmux buffer.',
         'teach': 'This is the tmux buffer, not your system clipboard.'},
        {'id': 'tmux-help', 'type': 'recall', 'keys': ['C-b', '?'],
         'prompt': 'List every key binding tmux currently has.',
         'teach': 'The most useful binding in tmux and the least used. Press q '
                  'to leave the list.'},

        # shell-level commands
        {'id': 'tmux-cmd-new', 'type': 'command',
         'answer': 'tmux new -s work',
         'accepts': ['tmux new-session -s work'],
         'prompt': 'From your shell: create and attach to a session named work.',
         'teach': 'Always name sessions with -s. Unnamed ones get numbers and '
                  'become impossible to tell apart.'},
        {'id': 'tmux-cmd-ls', 'type': 'command',
         'answer': 'tmux ls',
         'accepts': ['tmux list-sessions'],
         'prompt': 'From your shell: list the sessions that exist.',
         'teach': 'Shows window counts and marks which session is attached.'},
        {'id': 'tmux-cmd-attach', 'type': 'command',
         'answer': 'tmux attach -t work',
         'accepts': ['tmux a -t work', 'tmux attach-session -t work'],
         'prompt': 'From your shell: attach to the existing session named work.',
         'teach': '-t means target. tmux a is a valid abbreviation.'},
        {'id': 'tmux-cmd-newd', 'type': 'command',
         'answer': 'tmux new -d -s build',
         'accepts': ['tmux new-session -d -s build'],
         'prompt': 'From your shell: create a session named build in the '
                   'background without attaching to it.',
         'teach': '-d is how scripts start tmux sessions, and how you queue up '
                  'a workspace before you need it.'},
        {'id': 'tmux-cmd-kill', 'type': 'command',
         'answer': 'tmux kill-session -t work',
         'prompt': 'From your shell: destroy the session named work.',
         'teach': 'No confirmation and no undo. It kills the processes inside.'},
    ],

    # ------------------------------------------------------------------
    # Practice
    # ------------------------------------------------------------------
    'challenges': [
        {
            'id': 'tmux-first-session',
            'solution': {'commands': [['new-session', '-d', '-s',
                                       'hone-drill']]},
            'title': 'Create, detach, reattach',
            'goal': 'Prove to yourself that a session survives your terminal.',
            # create: False because creating the session IS the task here.
            # Doing it for the student would verify our own work.
            'setup': {'kind': 'tmux', 'session': 'hone-drill',
                      'create': False, 'handoff': 'shell'},
            'steps': [
                {'instruction': 'From your shell, create a session named '
                                'hone-drill and attach to it.',
                 'hint': 'tmux new -s hone-drill'},
                {'instruction': 'Inside it, start something long-running.',
                 'hint': 'sleep 600'},
                {'instruction': 'Detach from the session.',
                 'hint': 'C-b d'},
                {'instruction': 'Confirm from the shell that it still exists.',
                 'hint': 'tmux ls'},
                {'instruction': 'Attach again and confirm the sleep is running.',
                 'hint': 'tmux attach -t hone-drill'},
            ],
            'free': 'Create a named session, leave something running in it, '
                    'detach, confirm from the shell that it survived, and '
                    'attach again.',
            'verify': {'kind': 'tmux', 'expect': {'session_exists': True}},
            'fallback': 'self',
        },
        {
            'id': 'tmux-three-pane',
            'solution': {'commands': [['split-window', '-t', 'hone-drill'],
                                      ['split-window', '-t', 'hone-drill']]},
            'title': 'Build a three-pane layout',
            'goal': 'One tall pane on the left, two stacked on the right. This '
                    'is the classic editor-plus-two-terminals working layout.',
            'setup': {'kind': 'tmux', 'session': 'hone-drill',
                      'create': True, 'handoff': 'attach'},
            'steps': [
                {'instruction': 'Split the window into left and right.',
                 'hint': 'C-b %'},
                {'instruction': 'Move into the right-hand pane.',
                 'hint': 'C-b Right, or C-b o'},
                {'instruction': 'Split that pane into top and bottom.',
                 'hint': 'C-b "'},
                {'instruction': 'Zoom the left pane, then restore it.',
                 'hint': 'C-b Left then C-b z, and C-b z again'},
            ],
            'free': 'Build a window with one tall pane on the left and two '
                    'stacked panes on the right, then zoom one and restore it.',
            'verify': {'kind': 'tmux',
                       'expect': {'session_exists': True, 'min_panes': 3}},
            'fallback': 'self',
        },
        {
            'id': 'tmux-window-workflow',
            # No window index in the target: base-index varies by config, and
            # this module's own lesson says window numbers are positions rather
            # than identities. Targeting the session renames its current window.
            'solution': {'commands': [
                ['rename-window', '-t', 'hone-drill', 'editor'],
                ['new-window', '-t', 'hone-drill', '-n', 'server'],
                ['new-window', '-t', 'hone-drill', '-n', 'logs']]},
            'title': 'Name and navigate windows',
            'goal': 'Get a status bar that tells you something, then move '
                    'around it without looking.',
            'setup': {'kind': 'tmux', 'session': 'hone-drill',
                      'create': True, 'handoff': 'attach'},
            'steps': [
                {'instruction': 'Create two more windows.',
                 'hint': 'C-b c, twice'},
                {'instruction': 'Name each one after what it is for.',
                 'hint': 'C-b , then type the name'},
                {'instruction': 'Jump to the first window by its number.',
                 'hint': 'C-b 0, or C-b 1 with base-index set'},
                {'instruction': 'Toggle between the last two windows twice.',
                 'hint': 'C-b l'},
            ],
            'free': 'Create three named windows and move between them by '
                    'number and with the last-window toggle.',
            'verify': {'kind': 'tmux',
                       'expect': {'min_windows': 3, 'named_windows': True}},
            'fallback': 'self',
        },
        {
            'id': 'tmux-copy-paste',
            'title': 'Copy from scrollback into another pane',
            'goal': 'Get through the copy-mode ritual once, deliberately.',
            'setup': {'kind': 'tmux', 'session': 'hone-drill',
                      'create': True, 'handoff': 'attach'},
            'steps': [
                {'instruction': 'Produce more output than fits on screen.',
                 'hint': 'ls -la /usr/bin'},
                {'instruction': 'Enter copy mode and scroll back to the top.',
                 'hint': 'C-b [ then PageUp'},
                {'instruction': 'Select a filename.',
                 'hint': 'Space to start, movement keys to extend'},
                {'instruction': 'Confirm the selection, which also leaves copy '
                                'mode.',
                 'hint': 'Enter'},
                {'instruction': 'Paste it into a different pane.',
                 'hint': 'move panes, then C-b ]'},
            ],
            'free': 'Fill a pane with output, copy one line out of the '
                    'scrollback, and paste it into a different pane.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
    ],

    # ------------------------------------------------------------------
    # Quiz: model checks, not binding recall. The drills cover bindings.
    # ------------------------------------------------------------------
    'quiz': [
        {'id': 'q-detach-survives', 'type': 'mcq',
         'prompt': 'You are attached to a tmux session running a 40-minute '
                   'import. You close the whole terminal window. What happens '
                   'to the import?',
         'answer': 'It keeps running; you can attach again from a new terminal.',
         'distractors': [
             'It receives a hangup signal and dies.',
             'It pauses and resumes when you next attach.',
             'It keeps running but its output is lost.'],
         'teach': 'Your shells are children of the tmux server, not of your '
                  'terminal. Closing the viewer is the same as detaching.'},

        {'id': 'q-containers', 'type': 'mcq',
         'prompt': 'Order these from largest to smallest.',
         'answer': 'session, window, pane',
         'distractors': ['window, session, pane', 'session, pane, window',
                         'pane, window, session'],
         'teach': 'A session holds windows, a window holds panes. Almost every '
                  'tmux confusion is these three collapsed into fewer.'},

        {'id': 'q-last-pane', 'type': 'mcq',
         'prompt': 'A window has one pane left and you press C-b x and confirm. '
                   'What happens?',
         'answer': 'The window closes too, since it has no panes left.',
         'distractors': ['The pane clears but the window stays.',
                         'tmux refuses, because a window needs one pane.',
                         'The whole session ends.'],
         'teach': 'Containers do not outlive their contents. The same applies '
                  'one level up: closing the last window ends the session.'},

        {'id': 'q-prefix-timing', 'type': 'mcq',
         'prompt': 'You press C-b, then get distracted for five seconds, then '
                   'press c. What happens?',
         'answer': 'A new window is created; tmux waits for the second key.',
         'distractors': ['Nothing, the prefix timed out.',
                         'A literal c is typed into the shell.',
                         'tmux beeps and cancels.'],
         'teach': 'The prefix is not a modifier you hold. It is a mode you '
                  'enter, and it waits.'},

        {'id': 'q-copy-mode-keys', 'type': 'mcq',
         'prompt': 'You are in copy mode and you type "ls" and press Enter. '
                   'What happens?',
         'answer': 'Nothing useful; those keys are copy-mode commands, not shell '
                   'input.',
         'distractors': ['ls runs in the pane.',
                         'ls is copied to the tmux buffer.',
                         'The pane exits copy mode and runs ls.'],
         'teach': 'Copy mode is a different keymap. Realising you have changed '
                  'mode is most of what makes copy mode click.'},

        {'id': 'q-window-numbers', 'type': 'mcq',
         'prompt': 'You have windows 0, 1 and 2, and you kill window 1. What is '
                   'the third window now numbered?',
         'answer': '2, unchanged; there is now a gap at 1.',
         'distractors': ['1, the windows renumber.',
                         '3, numbers only ever increase.',
                         'It depends on renumber-windows, which defaults on.'],
         'teach': 'Numbers are positions rather than identities and tmux does '
                  'not renumber by default. Set renumber-windows on if the gaps '
                  'bother you.'},

        {'id': 'q-buffer-vs-clipboard', 'type': 'mcq',
         'prompt': 'You copy a line in tmux copy mode, then try to paste it into '
                   'a browser with Ctrl-V. Why is nothing there?',
         'answer': 'The tmux buffer is separate from the system clipboard.',
         'distractors': ['The selection was never confirmed with Enter.',
                         'Browsers cannot accept terminal selections.',
                         'The buffer expired when you left copy mode.'],
         'teach': 'C-b ] pastes from the tmux buffer into a tmux pane. Getting '
                  'it to the system clipboard needs deliberate setup.'},

        {'id': 'q-reboot', 'type': 'mcq',
         'prompt': 'Which of these ends a detached tmux session?',
         'answer': 'Rebooting the machine.',
         'distractors': ['Closing your terminal emulator.',
                         'Losing your SSH connection.',
                         'Logging out of your shell.'],
         'teach': 'tmux survives disconnection, not restarts. The server is a '
                  'process on that machine like any other.'},
    ],
}
