"""org-mode: the last of the priority four, and the D17 finish line.

**Written for someone who already keeps notes in Obsidian**, because that is
the honest situation and pretending otherwise teaches badly. Every lesson names
the Obsidian equivalent where one exists, and the last lesson answers the
question the others keep raising: whether org is supposed to replace the vault
or sit beside it. Learning a second notes system without deciding that first is
how people end up with two half-used ones.

No new adapter. Org files are plain text, so `adapters/emacs.py` already reads
them; the only difference is a `.org` scratch name so the major mode turns on.

Drills are capture type and lean on org's `C-c` bindings rather than Doom's
`SPC m` tree. The `C-c` ones are org's own, they work in any Emacs, and they
are what every piece of org documentation you will ever read is written in.
"""

MODULE = {
    'id': 'org',
    'title': 'org-mode',
    'group': 'Editors',
    'blurb': 'Outlines, TODO states, capture, refile, agenda.',
    'context': 'You are in an org file in Doom, with the cursor on a heading.',
    'needs': ('emacs',),
    'prereqs': ['doom'],
    'adapter': 'emacs',
    'estimate': '4-6 hours',
    'order': 12,

    # ------------------------------------------------------------------
    'lessons': [
        {
            'id': 'org-what',
            'title': 'What org actually is',
            'next': 'org-structure',
            'concept': (
                'org is a plain text file with a strict outline structure, and '
                'a very large amount of Emacs that understands that structure. '
                'The file is readable without Emacs; everything else is Emacs '
                'acting on it.\n\n'
                'If you already use Obsidian, the file itself will feel '
                'familiar: headings, lists, links, tags, plain text on disk. '
                'The difference is what the editor does with them. Obsidian is '
                'a notes application with a graph. org is an outline engine '
                'with a task planner, an agenda, a spreadsheet, and a literate '
                'programming system attached.\n\n'
                'That is why org can feel overwhelming. You are not looking at '
                'a note format, you are looking at about six tools that happen '
                'to share one file format.'
            ),
            'examples': [
                {
                    'label': 'A small org file',
                    'code': ('* Project alpha           :work:\n'
                             '** TODO Write the report\n'
                             '   SCHEDULED: <2026-08-14 Fri>\n'
                             '** DONE Collect the data\n'
                             '** Notes\n'
                             '   Nothing here is magic. It is a text file.'),
                    'note': 'Stars are heading levels, ALL-CAPS words after a '
                            'star are TODO states, and :tags: sit at the end of '
                            'the heading line.',
                },
                {
                    'label': 'The same idea in markdown',
                    'code': ('# Project alpha\n'
                             '## Write the report\n'
                             '- [ ] not started\n'
                             '## Collect the data\n'
                             '- [x] done'),
                    'note': 'Markdown can express the shape. What it cannot do '
                            'is give you an agenda across every file that '
                            'mentions a date.',
                },
            ],
            'misconceptions': [
                'org is not a markdown dialect. The syntax is different on '
                'purpose and the two do not mix cleanly in one file.',
                'org is not only for tasks. Many people use it purely as an '
                'outliner and never open the agenda.',
                'You do not have to adopt all of it. Headings and TODO states '
                'are a complete, useful subset, and most of the rest can wait '
                'or never arrive.',
            ],
            'try_it': [
                'Open `~/org/scratch.org` in Doom, type `* Hello` on the first '
                'line, and press TAB on it.',
            ],
        },
        {
            'id': 'org-structure',
            'title': 'Headings, folding and the outline',
            'next': 'org-todo',
            'concept': (
                'A heading is a line starting with one or more stars. The '
                'number of stars is the depth, and everything under a heading '
                'until the next heading of the same or lower depth belongs to '
                'it. That subtree is the unit org operates on.\n\n'
                'TAB on a heading cycles its folding: collapsed, children, '
                'everything. `S-TAB` does the same for the whole file, which is '
                'how you get a bird\'s-eye view of a long document instantly.\n\n'
                'The moves that matter are structural rather than textual. '
                '`M-RET` makes a new heading at the same level. `M-Right` and '
                '`M-Left` change that one heading\'s depth and leave its '
                'children where they are; add Shift, `M-S-Right`, to carry the '
                'subtree along. `M-Up` and `M-Down` always move the whole '
                'subtree past its siblings. '
                'Once these are in your fingers you stop editing text and start '
                'rearranging an outline.'
            ),
            'examples': [
                {
                    'label': 'Structure editing',
                    'code': ('TAB       fold this heading, cycling\n'
                             'S-TAB     fold the whole file, cycling\n'
                             'M-RET     new heading at this level\n'
                             'M-Right   demote this heading only\n'
                             'M-Left    promote this heading only\n'
                             'M-S-Right demote it and its subtree\n'
                             'M-Up      move this subtree up\n'
                             'M-Down    move it down'),
                    'note': 'Shift is the difference: M-Right moves the heading '
                            'alone and orphans its children, M-S-Right carries '
                            'them. M-Up and M-Down always take the subtree.',
                },
            ],
            'misconceptions': [
                'Obsidian folds headings too, but it does not move them. '
                '`M-Up` on a subtree is the operation with no Obsidian '
                'equivalent, and it is the one that makes org an outliner.',
                'Indentation is cosmetic. Depth comes from the number of stars, '
                'not from leading whitespace.',
                'S-TAB in insert mode does not fold. Structure editing is a '
                'normal-mode activity, like everything else in evil.',
            ],
            'try_it': [
                'Write three headings, put the cursor on the middle one, and '
                'press `M-Down`. Then `M-Right`.',
            ],
        },
        {
            'id': 'org-todo',
            'title': 'TODO states, tags and priorities',
            'next': 'org-lists',
            'concept': (
                'Any heading becomes a task by putting a state keyword straight '
                'after the stars. `C-c C-t` cycles it: nothing, TODO, DONE, and '
                'back. Doom adds more states than stock org, so read what your '
                'own cycle offers.\n\n'
                'This is the first real departure from Obsidian. A checkbox in '
                'Obsidian is a list item; a TODO in org is a heading, which '
                'means it has a subtree, can hold notes and sub-tasks, can be '
                'scheduled, can be refiled somewhere else, and shows up in the '
                'agenda. It is a first-class object rather than a line of text.\n\n'
                'Tags go at the end of the heading line between colons, and '
                'they inherit down the tree, so tagging a project tags '
                'everything in it.'
            ),
            'examples': [
                {
                    'label': 'A task with everything on it',
                    'code': ('** TODO [#A] Write the incident report  :work:ir:\n'
                             '   SCHEDULED: <2026-08-14 Fri>\n'
                             '   DEADLINE: <2026-08-16 Sun>\n'
                             '   Notes about it live here, in the subtree.'),
                    'note': 'Priority in square brackets, tags in colons, dates '
                            'on their own lines underneath.',
                },
                {
                    'label': 'The bindings',
                    'code': ('C-c C-t   cycle the TODO state\n'
                             'C-c C-s   schedule it\n'
                             'C-c C-d   give it a deadline\n'
                             'C-c C-q   set tags\n'
                             'C-c ,     set a priority'),
                    'note': 'SCHEDULED means "start thinking about it then". '
                            'DEADLINE means "it is due then". They are not '
                            'synonyms and the agenda treats them differently.',
                },
            ],
            'misconceptions': [
                'SCHEDULED is not a due date. It is when the task should start '
                'appearing in your agenda, and conflating the two is the most '
                'common org planning mistake.',
                'A DONE heading is not deleted or moved. It stays where it is '
                'and simply stops appearing in most agenda views.',
                'Tags inherit downward. A subtree under a `:work:` heading is '
                'tagged `:work:` whether or not you typed it again.',
            ],
            'try_it': [
                'Make a heading, press `C-c C-t` three times, and watch the '
                'state cycle. Then `C-c C-s` and pick tomorrow.',
            ],
        },
        {
            'id': 'org-lists',
            'title': 'Lists, checkboxes, blocks and tables',
            'next': 'org-links',
            'concept': (
                'Inside a heading you get the things you would expect: lists, '
                'checkboxes, code blocks. Two of them are worth calling out '
                'because they are better than they look.\n\n'
                'CHECKBOXES are for the small stuff that does not deserve a '
                'heading. `C-c C-c` toggles one. A parent list item can show a '
                'progress cookie like `[2/5]` that org updates for you, which '
                'is the right tool for a checklist inside a task.\n\n'
                'TABLES are the surprise. Type a row with pipes, press TAB, and '
                'org aligns the whole table as you type. It also does '
                'arithmetic, sorting and export. Nobody expects a spreadsheet '
                'inside a text file, and it is genuinely useful.'
            ),
            'examples': [
                {
                    'label': 'A checklist inside a task',
                    'code': ('** TODO Ship the release [1/3]\n'
                             '   - [X] tag the commit\n'
                             '   - [ ] write the notes\n'
                             '   - [ ] publish'),
                    'note': 'The [1/3] updates itself as you tick boxes with '
                            '`C-c C-c`.',
                },
                {
                    'label': 'A table, aligning itself',
                    'code': ('| host    | role   | patched |\n'
                             '|---------+--------+---------|\n'
                             '| alpha   | web    | yes     |\n'
                             '| bravo   | db     | no      |'),
                    'note': 'Type the pipes roughly and press TAB. org does the '
                            'alignment.',
                },
            ],
            'misconceptions': [
                'A checkbox is not a TODO. Checkboxes never reach the agenda, '
                'which is exactly why they are right for sub-steps and wrong '
                'for real tasks.',
                '`C-c C-c` is not one command. It is "do the obvious thing '
                'here", and what it does depends entirely on what the cursor is '
                'sitting on.',
            ],
            'try_it': [
                'Type `| a | b |` and press TAB. Then add a second row and '
                'watch the columns line up.',
            ],
        },
        {
            'id': 'org-links',
            'title': 'Links, and how they differ from Obsidian',
            'next': 'org-capture',
            'concept': (
                'org links are `[[target][description]]`, which looks close to '
                'an Obsidian wikilink and behaves differently in one important '
                'way: the target is explicit rather than resolved by filename '
                'search.\n\n'
                'A target can be a file, a heading inside a file, a web URL, a '
                'line in a source file, an email, or a shell command. `C-c C-l` '
                'inserts one with completion, and `C-c C-o` opens whatever is '
                'under the cursor.\n\n'
                'The practical consequence is that org will not silently find a '
                'note you renamed the way Obsidian does. In exchange, a link '
                'can point at things Obsidian has no concept of, like a '
                'specific heading in a specific file or a line of code.'
            ),
            'examples': [
                {
                    'label': 'Link targets',
                    'code': ('[[https://example.com][a web page]]\n'
                             '[[file:~/org/notes.org][another file]]\n'
                             '[[file:~/org/notes.org::*Some heading][a heading]]\n'
                             '[[*A heading in this file]]'),
                    'note': 'The description after the second bracket pair is '
                            'optional, and hidden when displayed.',
                },
            ],
            'misconceptions': [
                'Obsidian `[[wikilinks]]` resolve by name across the vault; org '
                'links resolve by path. Renaming a file breaks org links and '
                'Obsidian mostly fixes them for you.',
                '`C-c C-o` is the only reliable way to follow a link. Clicking '
                'may work and depends on your configuration.',
            ],
            'try_it': [
                'Press `C-c C-l`, paste a URL, give it a description, then put '
                'the cursor on it and press `C-c C-o`.',
            ],
        },
        {
            'id': 'org-capture',
            'title': 'Capture: the feature worth the whole system',
            'next': 'org-refile',
            'concept': (
                'Capture is the answer to "I thought of something and I am in '
                'the middle of something else". One binding, from anywhere in '
                'Emacs, opens a small buffer. You type the thought, press `C-c '
                'C-c`, and you are back where you were. The note has landed '
                'somewhere sensible and you never navigated anywhere.\n\n'
                'In Doom that binding is `SPC X`. Stock org uses `C-c c`.\n\n'
                'This is the thing that makes a notes system survive contact '
                'with a working day. If capturing costs you a context switch, '
                'you stop doing it, and a notes system you stop feeding is '
                'worse than none. Obsidian has quick-capture plugins for '
                'exactly this reason; org has had it built in for twenty '
                'years.'
            ),
            'examples': [
                {
                    'label': 'The loop',
                    'code': ('SPC X       open capture\n'
                             '(pick a template)\n'
                             'type the thing\n'
                             'C-c C-c     file it and return\n'
                             'C-c C-k     abandon it and return'),
                    'note': 'The whole loop is a few seconds and never leaves '
                            'the buffer you were working in.',
                },
                {
                    'label': 'A template, in config.el',
                    'code': ('(setq org-capture-templates\n'
                             "  \\'((\"t\" \"Task\" entry\n"
                             '     (file+headline "~/org/inbox.org" "Inbox")\n'
                             '     "* TODO %?\\n  %U"))) '),
                    'note': '%? is where the cursor lands and %U stamps the '
                            'time. Start with one template, not five.',
                },
            ],
            'misconceptions': [
                'Capture is not for filing things correctly. It is for getting '
                'them out of your head fast; refile sorts them later.',
                'You do not need good templates to start. One inbox template is '
                'enough for months.',
                '`C-c C-c` confirms and `C-c C-k` cancels. Pressing Escape does '
                'not close a capture buffer.',
            ],
            'try_it': [
                'Press `SPC X` from any buffer, capture a thought, and confirm '
                'with `C-c C-c`. Then find where it landed.',
            ],
        },
        {
            'id': 'org-refile',
            'title': 'Refile: where captured things go',
            'next': 'org-agenda',
            'concept': (
                'Capture is deliberately careless, so something has to be '
                'careful later. Refile moves a subtree to another heading, '
                'anywhere in your files, with completion.\n\n'
                '`C-c C-w` on a heading offers a list of targets and moves the '
                'whole subtree there. That is the other half of the loop: '
                'capture into one inbox without thinking, then periodically '
                'empty the inbox by refiling.\n\n'
                'This pairing is the actual workflow, and it is worth more than '
                'any amount of folder structure. An inbox that gets emptied '
                'beats a perfect hierarchy that nothing ever reaches.'
            ),
            'examples': [
                {
                    'label': 'The other half of the loop',
                    'code': ('C-c C-w    refile this subtree\n'
                             'C-u C-c C-w  jump to a refile target instead\n'
                             '\n'
                             'capture  ->  inbox.org\n'
                             'refile   ->  wherever it belongs'),
                    'note': 'Refiling moves the entire subtree, including notes '
                            'and sub-tasks.',
                },
            ],
            'misconceptions': [
                'Refile targets are configured, not automatic. If nothing '
                'sensible is offered, `org-refile-targets` has not been set up '
                'yet.',
                'Refile is not cut and paste. It preserves the subtree, its '
                'tags and its state, and it is undoable.',
            ],
            'try_it': [
                'Capture two thoughts, then refile one of them under a project '
                'heading with `C-c C-w`.',
            ],
        },
        {
            'id': 'org-agenda',
            'title': 'The agenda: why the dates were worth typing',
            'concept': (
                'The agenda is a generated view across every file org knows '
                'about, showing what is scheduled, what is due, and what is '
                'still open. In Doom it is `SPC o A`.\n\n'
                'Nothing about it is stored. It is computed from the SCHEDULED '
                'and DEADLINE lines in your files every time you open it, which '
                'is why those lines are worth typing and why the distinction '
                'between them matters.\n\n'
                'The agenda is also editable in place. You can change a TODO '
                'state, reschedule, or jump to the source heading without '
                'leaving it, which is what makes a daily review take two '
                'minutes rather than twenty.\n\n'
                'This is the piece Obsidian genuinely does not have without '
                'plugins, and it is the strongest argument for keeping org '
                'around even if your notes live elsewhere.'
            ),
            'examples': [
                {
                    'label': 'Opening and driving it',
                    'code': ('SPC o A    open the agenda\n'
                             'a          agenda for the week\n'
                             't          all TODO items\n'
                             '\n'
                             'inside the agenda:\n'
                             'RET        jump to the heading\n'
                             't          change its TODO state\n'
                             'S-Right    reschedule by a day\n'
                             'q          leave'),
                    'note': 'Editing in the agenda edits the real file '
                            'underneath.',
                },
            ],
            'misconceptions': [
                'The agenda only sees files in `org-agenda-files`. A task in a '
                'file org has not been told about will never appear, and this '
                'is the usual reason an agenda looks empty.',
                'An undated TODO does not appear in the weekly agenda. It '
                'appears in the TODO list view, which is a different view.',
            ],
            'try_it': [
                'Schedule something for tomorrow with `C-c C-s`, then open the '
                'agenda with `SPC o A` and find it.',
            ],
            'next': 'org-export',
        },
        {
            'id': 'org-export',
            'title': 'Export: turning the outline into a document',
            'next': 'org-or-obsidian',
            'concept': (
                'An org file is a source format, and the same file can become '
                'an HTML page, a PDF, a markdown file, or plain text. This is '
                'the part that makes org a document tool rather than only a '
                'planner, and it is the honest answer to "how do I hand this to '
                'someone who does not use Emacs".\n\n'
                'Everything goes through one dispatcher: `C-c C-e`. It opens a '
                'menu, and two more keys pick the format and what to do with '
                'it. `h o` writes HTML and opens it, `l o` writes a PDF through '
                'LaTeX and opens it, `m m` writes markdown, `t u` writes UTF-8 '
                'plain text. Inside that menu you can also toggle `C-s`, which '
                'limits the export to the subtree under the cursor rather than '
                'the whole file.\n\n'
                'What gets exported is controlled by keywords at the top of the '
                'file. `#+TITLE:`, `#+AUTHOR:` and `#+DATE:` become the '
                'document header. `#+OPTIONS: toc:nil num:nil` turns off the '
                'table of contents and section numbers. A subtree tagged '
                '`:noexport:` is left out entirely, which is how you keep '
                'private planning notes in the same file as the document you '
                'share.\n\n'
                'The two backends worth knowing: markdown, which is built in '
                'and is how an org document reaches the vault or a git README, '
                'and HTML, which needs nothing installed. PDF is the one with a '
                'dependency: it wants a LaTeX toolchain, and its absence is the '
                'usual reason `l p` fails. Source blocks export as formatted '
                'code, and if you executed them with `C-c C-c` first, their '
                'results are exported too, which is the whole point of the '
                'literate-programming side of org.'
            ),
            'examples': [
                {
                    'label': 'The dispatcher',
                    'code': ('C-c C-e     open the export menu\n'
                             '  h o       HTML, and open it\n'
                             '  l o       PDF via LaTeX, and open it\n'
                             '  m m       markdown\n'
                             '  t u       UTF-8 plain text\n'
                             '  C-s       toggle: this subtree only'),
                    'note': 'Two keys after C-c C-e: the first picks the '
                            'backend, the second what to do with the output.',
                },
                {
                    'label': 'Controlling the output from the file',
                    'code': ('#+TITLE: Incident notes\n'
                             '#+AUTHOR: you\n'
                             '#+OPTIONS: toc:nil num:nil\n'
                             '\n'
                             '* Findings\n'
                             '* Scratch work            :noexport:\n'
                             '  This subtree is left out of every export.'),
                    'note': 'The keywords are the document header; the '
                            ':noexport: tag keeps private sections private.',
                },
            ],
            'misconceptions': [
                'Export does not change your file. It writes a new file beside '
                'it, so the org source is always the thing you keep editing.',
                'PDF export failing is almost always a missing LaTeX '
                'toolchain, not a broken document. HTML and markdown need '
                'nothing extra.',
                'A `:noexport:` tag hides a whole subtree, children included. '
                'That is a feature: planning and document live in one file.',
                'Markdown export is built in but the backend may need enabling '
                'in `init.el` (the `org` module\'s `+dragndrop` is unrelated; '
                'it is `ox-md`, loaded by default in Doom).',
            ],
            'try_it': [
                'Add a `#+TITLE:` to any org file, then press `C-c C-e m m` and '
                'open the markdown it produced. Then try `h o` for HTML.',
            ],
        },
        {
            'id': 'org-or-obsidian',
            'title': 'Should this replace your vault?',
            'concept': (
                'This lesson exists because every lesson before it raised the '
                'question, and learning a second notes system without answering '
                'it is how people end up with two half-used ones.\n\n'
                'The honest answer for someone already invested in Obsidian is: '
                '**probably not, and that is fine.** Obsidian is better at '
                'linked prose notes, at browsing a large corpus, and at being '
                'available on a phone. org is better at tasks with dates, at '
                'capture, and at structural editing of an outline.\n\n'
                'The pragmatic split that actually holds: keep long-lived notes '
                'in the vault, and give org the things it is uniquely good at, '
                'which is planning. One `~/org/inbox.org` for capture and one '
                'agenda is a complete, useful org install, and it does not '
                'compete with anything you already have.\n\n'
                'The failure mode to avoid is migrating the vault. It is weeks '
                'of work, you lose the graph, and you learn nothing about org '
                'that a single inbox file would not have taught you.'
            ),
            'examples': [
                {
                    'label': 'What each is actually better at',
                    'code': ('Obsidian    linked prose, browsing, search,\n'
                             '            phone, graph, a large existing corpus\n'
                             '\n'
                             'org         tasks with dates, the agenda,\n'
                             '            capture, structural outline editing,\n'
                             '            tables, literate code blocks'),
                    'note': 'Almost no overlap in the places either is '
                            'genuinely strong.',
                },
                {
                    'label': 'A complete, small org setup',
                    'code': ('~/org/inbox.org      everything captured\n'
                             '~/org/projects.org   refiled, with dates\n'
                             '\n'
                             'SPC X   capture into the inbox\n'
                             'C-c C-w refile out of it\n'
                             'SPC o A read the agenda'),
                    'note': 'Two files and three bindings. Resist adding more '
                            'until these are a habit.',
                },
            ],
            'misconceptions': [
                'You do not have to choose. Both are plain text on disk and '
                'nothing stops you running both indefinitely.',
                'org-roam exists and is a Zettelkasten system much closer to '
                'Obsidian. It is also a much bigger commitment, and it is the '
                'wrong second step.',
                'Migrating markdown to org is easy and almost always a mistake. '
                'The format was never the reason Obsidian works for you.',
            ],
            'try_it': [
                'Create `~/org/inbox.org`, capture three things into it over a '
                'day, and refile them at the end. Decide after a week, not '
                'before.',
            ],
        },
    ],

    # ------------------------------------------------------------------
    'drills': [
        # structure
        {'id': 'org-fold', 'type': 'keys', 'keys': ['TAB'],
         'prompt': 'Cycle the folding of the heading under the cursor.',
         'teach': 'Collapsed, then children, then everything. S-TAB does the '
                  'same for the whole file.'},
        {'id': 'org-fold-global', 'type': 'keys', 'keys': ['S-TAB'],
         'prompt': 'Cycle the folding of the entire file.',
         'teach': 'The fastest way to get a bird\'s-eye view of a long '
                  'document.'},
        {'id': 'org-new-heading', 'type': 'keys', 'keys': ['M-RET'],
         'prompt': 'Create a new heading at the same level as this one.',
         'teach': 'Same level, after the current one. It also continues list '
                  'items, so the one chord grows both outlines and lists.'},
        {'id': 'org-demote', 'type': 'keys', 'keys': ['M-Right'],
         'prompt': 'Demote this heading one level, leaving its children behind.',
         'teach': 'M-Right moves the heading alone. M-S-Right is the one that '
                  'carries the subtree, which is the distinction that makes '
                  'org an outliner rather than a text file with hashes.'},
        {'id': 'org-promote', 'type': 'keys', 'keys': ['M-Left'],
         'prompt': 'Promote this heading one level.',
         'teach': 'M-Right demotes. With Shift held the whole subtree moves '
                  'instead of just the one heading, which is usually what you '
                  'meant.'},
        {'id': 'org-move-up', 'type': 'keys', 'keys': ['M-Up'],
         'prompt': 'Move this subtree above its previous sibling.',
         'teach': 'The operation with no Obsidian equivalent.'},
        {'id': 'org-move-down', 'type': 'keys', 'keys': ['M-Down'],
         'prompt': 'Move this subtree below its next sibling.',
         'teach': 'M-Up is its opposite. The subtree travels with its '
                  'children, so reordering a plan never orphans the tasks '
                  'under a heading.'},

        # tasks
        {'id': 'org-todo-cycle', 'type': 'keys', 'keys': ['C-c', 'C-t'],
         'prompt': 'Cycle this heading between TODO states.',
         'teach': 'A TODO in org is a heading, so it has a subtree, can be '
                  'scheduled and can be refiled. An Obsidian checkbox is a line.'},
        {'id': 'org-schedule', 'type': 'keys', 'keys': ['C-c', 'C-s'],
         'prompt': 'Schedule this task, meaning when to start thinking about it.',
         'teach': 'SCHEDULED is not a due date. Conflating it with DEADLINE is '
                  'the most common org planning mistake.'},
        {'id': 'org-deadline', 'type': 'keys', 'keys': ['C-c', 'C-d'],
         'prompt': 'Give this task a deadline, meaning when it is actually due.',
         'teach': 'C-c C-s sets SCHEDULED instead, which is when you intend '
                  'to start. The agenda warns as a DEADLINE approaches; '
                  'mixing the two muddies every view.'},
        {'id': 'org-tags', 'type': 'keys', 'keys': ['C-c', 'C-q'],
         'prompt': 'Set the tags on this heading.',
         'teach': 'Tags inherit downward, so tagging a project tags everything '
                  'inside it.'},
        {'id': 'org-priority', 'type': 'keys', 'keys': ['C-c', ','],
         'prompt': 'Set the priority of this heading.',
         'teach': 'Cycles A, B, C, then none. Priorities only matter where '
                  'you will see them: the agenda sorts same-day tasks by '
                  'them.'},

        # the do-what-I-mean key and content
        {'id': 'org-ctrl-c-ctrl-c', 'type': 'keys', 'keys': ['C-c', 'C-c'],
         'prompt': 'Do the obvious thing under the cursor: tick a box, realign a table, run a block.',
         'teach': 'Not one command. It is context sensitive, which is why it is '
                  'worth pressing on anything you are unsure about.'},
        {'id': 'org-link-insert', 'type': 'keys', 'keys': ['C-c', 'C-l'],
         'prompt': 'Insert a link, with completion.',
         'teach': 'It completes from links already in the buffer and recent '
                  'stored ones; C-c l elsewhere stores a target for it first.'},
        {'id': 'org-link-open', 'type': 'keys', 'keys': ['C-c', 'C-o'],
         'prompt': 'Open the link under the cursor.',
         'teach': 'The reliable way. Clicking may or may not be configured.'},

        # capture, refile, agenda
        {'id': 'org-capture', 'type': 'keys', 'keys': ['SPC', 'X'],
         'prompt': 'Capture a thought from anywhere, without navigating.',
         'teach': 'The feature that makes a notes system survive a working '
                  'day. Stock org binds this to C-c c.'},
        {'id': 'org-capture-abort', 'type': 'keys', 'keys': ['C-c', 'C-k'],
         'prompt': 'Abandon a capture without filing it.',
         'teach': 'C-c C-c confirms instead, which is the same do-what-I-mean '
                  'key drilled above. Escape does not close a capture buffer.'},
        {'id': 'org-refile', 'type': 'keys', 'keys': ['C-c', 'C-w'],
         'prompt': 'Move this subtree somewhere it actually belongs.',
         'teach': 'The other half of capture. An inbox that gets emptied beats '
                  'a perfect hierarchy nothing reaches.'},
        {'id': 'org-agenda', 'type': 'keys', 'keys': ['SPC', 'o', 'A'],
         'prompt': 'Open the agenda.',
         'teach': 'Nothing about it is stored. It is computed from your '
                  'SCHEDULED and DEADLINE lines every time.'},
        {'id': 'org-archive', 'type': 'keys', 'keys': ['C-c', 'C-x', 'C-a'],
         'prompt': 'Archive the subtree under the cursor.',
         'teach': 'Archiving retires a DONE tree to a separate file so your '
                  'live files and agenda stay small. It is the counterpart to '
                  'refile: refile moves live items, archive retires finished '
                  'ones.'},

        # export: open the dispatcher (a real chord), then pick a destination
        {'id': 'org-export-dispatch', 'type': 'keys', 'keys': ['C-c', 'C-e'],
         'prompt': 'Open the export dispatcher.',
         'teach': 'One menu for every backend. The next two keys pick the '
                  'format and what to do with the file.'},
        {'id': 'org-export-md', 'type': 'recall', 'keys': ['m', 'm'],
         'prompt': 'In the export menu, write the file as markdown.',
         'teach': 'Markdown is how an org document reaches the vault or a git '
                  'README. It is built in.'},
        {'id': 'org-export-html', 'type': 'recall', 'keys': ['h', 'o'],
         'prompt': 'In the export menu, write HTML and open it.',
         'teach': 'HTML needs nothing installed. The second key, o, opens the '
                  'result; h alone just writes it.'},
        {'id': 'org-export-pdf', 'type': 'recall', 'keys': ['l', 'o'],
         'prompt': 'In the export menu, write a PDF through LaTeX and open it.',
         'teach': 'PDF is the one with a dependency: it wants a LaTeX '
                  'toolchain, and its absence is the usual reason it fails.'},

        # shell / file level
        {'id': 'org-inbox-file', 'type': 'command',
         'answer': 'mkdir -p ~/org',
         'prompt': 'From your shell: create the directory org expects, which is '
                   'org-directory.',
         'teach': 'Doom sets org-directory to ~/org by default. An agenda with '
                  'no files is the usual reason it looks empty.'},
    ],

    # ------------------------------------------------------------------
    'challenges': [
        {
            'id': 'org-build-outline',
            'title': 'Build an outline',
            'goal': 'Use structure editing rather than typing stars by hand.',
            'setup': {'kind': 'emacs', 'scratch_name': 'scratch.org',
                      'start': ['* Project alpha', 'Write two sub-headings '
                                'under this one, then delete this line.']},
            'solution': {'elisp': '(progn (erase-buffer) (insert '
                                  '"* Project alpha\\n** Collect the data\\n'
                                  '** Write the report\\n"))'},
            'steps': [
                {'instruction': 'Put the cursor on the Project alpha heading.',
                 'hint': 'gg'},
                {'instruction': 'Create a new heading below it.',
                 'hint': 'M-RET'},
                {'instruction': 'Demote it so it sits under the project.',
                 'hint': 'M-Right'},
                {'instruction': 'Name it "Collect the data", then add a second '
                                'one called "Write the report".',
                 'hint': 'M-RET makes a sibling at the same level'},
                {'instruction': 'Remove the instruction line and save.',
                 'hint': 'dd then SPC f s'},
            ],
            'free': 'Make the file contain "* Project alpha" with exactly two '
                    'level-two headings under it: "Collect the data" then '
                    '"Write the report".',
            'verify': {'kind': 'emacs',
                       'expect': {'lines': ['* Project alpha',
                                            '** Collect the data',
                                            '** Write the report']}},
            'fallback': 'self',
        },
        {
            'id': 'org-task-states',
            'title': 'Turn headings into tasks',
            'goal': 'Cycle TODO states and add a tag, using the bindings rather '
                    'than typing the keywords.',
            'setup': {'kind': 'emacs', 'scratch_name': 'scratch.org',
                      'start': ['* Weekly review', '** Read the agenda',
                                '** Empty the inbox']},
            'solution': {'elisp': '(progn (erase-buffer) (insert '
                                  '"* Weekly review\\n** DONE Read the agenda\\n'
                                  '** TODO Empty the inbox\\n"))'},
            'steps': [
                {'instruction': 'Put the cursor on "Read the agenda".',
                 'hint': 'it is the second line'},
                {'instruction': 'Cycle it to DONE.',
                 'hint': 'C-c C-t, more than once'},
                {'instruction': 'Cycle "Empty the inbox" to TODO.',
                 'hint': 'C-c C-t once'},
                {'instruction': 'Save.', 'hint': 'SPC f s'},
            ],
            'free': 'Mark "Read the agenda" as DONE and "Empty the inbox" as '
                    'TODO, then save.',
            'verify': {'kind': 'emacs',
                       'expect': {'contains': ['** DONE Read the agenda',
                                               '** TODO Empty the inbox']}},
            'fallback': 'self',
        },
        {
            'id': 'org-checklist',
            'title': 'A checklist inside a task',
            'goal': 'Use checkboxes for sub-steps, which is what they are for, '
                    'and let org count them.',
            'setup': {'kind': 'emacs', 'scratch_name': 'scratch.org',
                      'start': ['* TODO Ship the release [0/3]',
                                'Add three checkbox items under this heading '
                                'and tick the first, then delete this line.']},
            'solution': {'elisp': '(progn (erase-buffer) (insert '
                                  '"* TODO Ship the release [1/3]\\n'
                                  '- [X] tag the commit\\n'
                                  '- [ ] write the notes\\n'
                                  '- [ ] publish\\n"))'},
            'steps': [
                {'instruction': 'Add three list items starting with "- [ ] ".',
                 'hint': 'o to open a line, then type it'},
                {'instruction': 'Tick the first one.',
                 'hint': 'C-c C-c on the item'},
                {'instruction': 'Remove the instruction line and save.',
                 'hint': 'the cookie should read [1/3]'},
            ],
            'free': 'Under the heading, add three checkbox items, tick exactly '
                    'one, and make the cookie read [1/3]. Then save.',
            'verify': {'kind': 'emacs',
                       'expect': {'contains': ['[1/3]', '- [X]'],
                                  'not_contains': 'delete this line',
                                  'line_count': 4}},
            'fallback': 'self',
        },
        {
            'id': 'org-scheduled',
            'title': 'Schedule something and link to it',
            'goal': 'Put a real date on a task and add a link, which is what '
                    'makes the agenda worth opening.',
            'setup': {'kind': 'emacs', 'scratch_name': 'scratch.org',
                      'start': ['* TODO Read the org manual',
                                'Schedule this for any date and add a link to '
                                'https://orgmode.org, then delete this line.']},
            'solution': {'elisp': '(progn (erase-buffer) (insert '
                                  '"* TODO Read the org manual\\n'
                                  '  SCHEDULED: <2026-08-14 Fri>\\n'
                                  '  [[https://orgmode.org][the manual]]\\n"))'},
            'steps': [
                {'instruction': 'Put the cursor on the heading and schedule it.',
                 'hint': 'C-c C-s, then pick a date'},
                {'instruction': 'Add a link to the org website underneath.',
                 'hint': 'C-c C-l, paste the URL, give it a description'},
                {'instruction': 'Remove the instruction line and save.'},
            ],
            'free': 'Schedule the task for any date and add a link to '
                    'https://orgmode.org underneath it, then save.',
            'verify': {'kind': 'emacs',
                       'expect': {'contains': ['SCHEDULED:', 'orgmode.org'],
                                  'not_contains': 'delete this line'}},
            'fallback': 'self',
        },
        {'id': 'org-todo-cycle',
         'title': 'Turn a heading into a task, then finish it',
         'goal': 'A TODO is a keyword on a heading, not a special kind of '
                 'line. Add one, then complete it.',
         'setup': {'kind': 'emacs',
                   'scratch_name': 'scratch.org',
                   'start': ['* Buy milk', '* Call the bank']},
         'solution': {'elisp': '(progn (erase-buffer) (insert "* DONE Buy '
                               'milk\\n* TODO Call the bank\\n"))'},
         'steps': [{'instruction': 'Put the cursor on the first heading '
                                   'and cycle it to TODO.',
                    'hint': 'C-c C-t, or S-Right to step through the '
                            'keywords'},
                   {'instruction': 'Cycle it once more, to DONE.',
                    'hint': 'C-c C-t again. The cycle is TODO, DONE, '
                            'nothing'},
                   {'instruction': 'Make the second heading a TODO and '
                                   'leave it there.',
                    'hint': 'C-c C-t on that line, once'},
                   {'instruction': 'Save and quit.',
                    'hint': 'SPC f s, then SPC q q'}],
         'free': 'Leave the first heading DONE and the second TODO.',
         'verify': {'kind': 'emacs',
                    'expect': {'lines': ['* DONE Buy milk',
                                         '* TODO Call the bank']}},
         'fallback': 'self'},
        {'id': 'org-checkboxes',
         'title': 'A checklist under a heading',
         'goal': 'Checkboxes are list items with a box. Build one and tick '
                 'part of it.',
         'setup': {'kind': 'emacs',
                   'scratch_name': 'scratch.org',
                   'start': ['* Packing']},
         'solution': {'elisp': '(progn (goto-char (point-max)) (insert '
                               '"\\n- [X] passport\\n- [ ] tickets\\n"))'},
         'steps': [{'instruction': 'Under the heading, add a list item '
                                   'with an empty checkbox for passport.',
                    'hint': '- [ ] passport'},
                   {'instruction': 'Add a second one for tickets.',
                    'hint': 'M-RET continues a list, box and all'},
                   {'instruction': 'Tick the passport one.',
                    'hint': 'C-c C-c on the item toggles its box'},
                   {'instruction': 'Save and quit.',
                    'hint': 'SPC f s, then SPC q q'}],
         'free': 'Under Packing, list passport (ticked) and tickets '
                 '(unticked) as checkboxes.',
         'verify': {'kind': 'emacs',
                    'expect': {'contains': ['- [X] passport',
                                            '- [ ] tickets']}},
         'fallback': 'self'},
        {'id': 'org-tags',
         'title': 'Tag a heading so the agenda can find it',
         'goal': 'Tags are how you slice an outline later. Put one on a '
                 'heading.',
         'setup': {'kind': 'emacs',
                   'scratch_name': 'scratch.org',
                   'start': ['* TODO Renew the certificate',
                             '* TODO Water plants']},
         'solution': {'elisp': '(progn (goto-char (point-min)) '
                               '(end-of-line) (insert " :work:"))'},
         'steps': [{'instruction': 'Put the cursor on the certificate '
                                   'heading.',
                    'hint': 'gg'},
                   {'instruction': 'Add the tag work to it.',
                    'hint': 'C-c C-q, type work, Enter. Or type :work: at '
                            'the end of the line yourself'},
                   {'instruction': 'Leave the second heading untagged, and '
                                   'save.',
                    'hint': 'SPC f s, then SPC q q'}],
         'free': 'Tag the certificate heading :work:, leaving the other '
                 'alone.',
         'verify': {'kind': 'emacs',
                    'expect': {'contains': ':work:',
                               'not_contains': 'Water plants :'}},
         'fallback': 'self'},
        {'id': 'org-subtree-move',
         'title': 'Move a subtree, children and all',
         'goal': 'Structure editing moves a heading with everything under '
                 'it. Reorder two sections without touching their '
                 'contents.',
         'setup': {'kind': 'emacs',
                   'scratch_name': 'scratch.org',
                   'start': ['* Second',
                             'body of second',
                             '* First',
                             'body of first']},
         'solution': {'elisp': '(progn (erase-buffer) (insert "* '
                               'First\\nbody of first\\n* Second\\nbody of '
                               'second\\n"))'},
         'steps': [{'instruction': 'Put the cursor on the Second heading.',
                    'hint': 'gg'},
                   {'instruction': 'Move the whole subtree down past the '
                                   'next one.',
                    'hint': 'M-Down on the heading. The body travels with '
                            'it'},
                   {'instruction': 'Save and quit.',
                    'hint': 'SPC f s, then SPC q q. Dragging lines one at '
                            'a time is what this replaces'}],
         'free': 'Put First and its body above Second and its body.',
         'verify': {'kind': 'emacs',
                    'expect': {'lines': ['* First',
                                         'body of first',
                                         '* Second',
                                         'body of second']}},
         'fallback': 'self'},
        {'id': 'org-schedule',
         'title': 'Give a task a date the agenda will notice',
         'goal': 'A date in the body is prose. A SCHEDULED line is data. '
                 'Add the real thing.',
         'setup': {'kind': 'emacs',
                   'scratch_name': 'scratch.org',
                   'start': ['* TODO File the tax return']},
         'solution': {'elisp': '(progn (goto-char (point-max)) (insert '
                               '"\\nDEADLINE: <2026-01-31 Sat>\\n"))'},
         'steps': [{'instruction': 'Put the cursor on the heading.',
                    'hint': 'gg'},
                   {'instruction': 'Add a deadline of 31 January 2026.',
                    'hint': 'C-c C-d opens a date picker. Type 2026-01-31 '
                            'and Enter'},
                   {'instruction': 'Save and quit.',
                    'hint': 'SPC f s. C-c C-s would set SCHEDULED instead, '
                            'which means when you plan to start'}],
         'free': 'Give the task a DEADLINE of 2026-01-31.',
         'verify': {'kind': 'emacs',
                    'expect': {'contains': ['DEADLINE:', '2026-01-31']}},
         'fallback': 'self'},

        {'id': 'org-table',
         'title': 'Build a table and let org align it',
         'goal': 'Org tables are plain text that the editor keeps tidy, and '
                 'they are the feature people are most surprised by.',
         'setup': {'kind': 'emacs',
                   'scratch_name': 'table.org',
                   'start': ['* Costs']},
         'solution': {'elisp': '(progn (goto-char (point-max)) '
                               '(insert "\\n| item | cost |\\n'
                               '|------+------|\\n'
                               '| tea | 3 |\\n| coffee | 4 |\\n") '
                               '(forward-line -1) (org-table-align))'},
         'steps': [{'instruction': 'Under the heading, start a table with a '
                                   'header row of item and cost.',
                    'hint': 'type the pipes yourself, then press Tab'},
                   {'instruction': 'Add a horizontal rule under the header.',
                    'hint': 'a row of dashes, or C-c - on the row below'},
                   {'instruction': 'Add two rows of data. Pressing Tab in the '
                                   'last cell creates the next row.'},
                   {'instruction': 'Align the table and save.',
                    'hint': 'C-c C-c on the table realigns it, then SPC f s'}],
         'free': 'Produce a table under the heading with an item and cost '
                 'header, a rule, and two data rows.',
         'verify': {'kind': 'emacs',
                    'expect': {'contains': ['| item', 'cost', 'tea',
                                            'coffee']}},
         'fallback': 'self'},

        {'id': 'org-properties',
         'title': 'Attach structured data to a heading',
         'goal': 'A property drawer is how a heading carries fields that the '
                 'agenda and column view can read.',
         'setup': {'kind': 'emacs',
                   'scratch_name': 'props.org',
                   'start': ['* TODO Replace the door']},
         'solution': {'elisp': '(progn (goto-char (point-max)) '
                               '(insert "\\n:PROPERTIES:\\n'
                               ':Effort: 2:00\\n'
                               ':Owner: sage\\n'
                               ':END:\\n"))'},
         'steps': [{'instruction': 'Put the cursor on the heading.',
                    'hint': 'gg'},
                   {'instruction': 'Add a property drawer with an Effort of '
                                   'two hours.',
                    'hint': 'C-c C-x p, or type the drawer by hand'},
                   {'instruction': 'Add a second property naming an owner.'},
                   {'instruction': 'Save, and note that the drawer folds away '
                                   'and is still data.',
                    'hint': 'SPC f s'}],
         'free': 'Give the heading a property drawer with an Effort and an '
                 'Owner property.',
         'verify': {'kind': 'emacs',
                    'expect': {'contains': [':PROPERTIES:', ':Effort:',
                                            ':Owner:', ':END:']}},
         'fallback': 'self'},

        {'id': 'org-src-block',
         'title': 'Put code in a document that stays code',
         'goal': 'A source block keeps its language, gets real editing, and '
                 'exports as code rather than as prose.',
         'setup': {'kind': 'emacs',
                   'scratch_name': 'notes.org',
                   'start': ['* How to check the disk']},
         'solution': {'elisp': '(progn (goto-char (point-max)) '
                               '(insert "\\n#+begin_src sh\\n'
                               'df -h /\\n'
                               '#+end_src\\n"))'},
         'steps': [{'instruction': 'Under the heading, open a shell source '
                                   'block.',
                    'hint': 'type <s then Tab, or write the begin_src line'},
                   {'instruction': 'Put a df command inside it.'},
                   {'instruction': 'Close the block and save.',
                    'hint': 'the end_src line, then SPC f s'},
                   {'instruction': 'Note that C-c apostrophe opens the block '
                                   'in a real buffer for that language.'}],
         'free': 'Add a shell source block under the heading containing a df '
                 'command.',
         'verify': {'kind': 'emacs',
                    'expect': {'contains': ['#+begin_src', 'df -h',
                                            '#+end_src']}},
         'fallback': 'self'},

        {'id': 'org-export-setup',
         'title': 'Set a document up to export cleanly',
         'goal': 'Export is controlled from the top of the file and by tags. '
                 'Put the header keywords in, and hide the part you do not '
                 'want shared.',
         'setup': {'kind': 'emacs',
                   'scratch_name': 'report.org',
                   'start': ['* Findings',
                             '  The real content lives here.',
                             '* Scratch work',
                             '  Private notes that must not be shared.']},
         'solution': {'elisp': '(progn (goto-char (point-min)) '
                               '(insert "#+TITLE: Incident report\\n'
                               '#+AUTHOR: analyst\\n'
                               '#+OPTIONS: toc:nil num:nil\\n\\n") '
                               '(goto-char (point-max)) '
                               '(search-backward "* Scratch work") '
                               '(end-of-line) (insert " :noexport:"))'},
         'steps': [{'instruction': 'At the very top of the file, add TITLE, '
                                   'AUTHOR and DATE keywords.',
                    'hint': '#+TITLE:, #+AUTHOR: on their own lines above the '
                            'first heading'},
                   {'instruction': 'Add an OPTIONS line turning off the table '
                                   'of contents and section numbers.',
                    'hint': '#+OPTIONS: toc:nil num:nil'},
                   {'instruction': 'Tag the Scratch work heading so export '
                                   'leaves it out.',
                    'hint': 'add :noexport: at the end of that heading line'},
                   {'instruction': 'Save. Then try C-c C-e m m and confirm '
                                   'the scratch section is absent from the '
                                   'markdown.'}],
         'free': 'Produce report.org with TITLE, AUTHOR and an OPTIONS line at '
                 'the top, and the Scratch work heading tagged :noexport:.',
         'verify': {'kind': 'emacs',
                    'expect': {'contains': ['#+TITLE:', '#+OPTIONS:',
                                            'toc:nil',
                                            '* Scratch work :noexport:']}},
         'fallback': 'self'},

        {'id': 'org-export-run',
         'title': 'Export one document three ways',
         'goal': 'The dispatcher is muscle memory once you have used it a few '
                 'times. Do it for real, and see where the files land.',
         'setup': {'kind': 'self'},
         'steps': [{'instruction': 'Open or write a short org file with a '
                                   'title, a couple of headings and a list.'},
                   {'instruction': 'Export it to markdown and open the '
                                   'result.',
                    'hint': 'C-c C-e m m, then find report.md beside it'},
                   {'instruction': 'Export the same file to HTML and open it '
                                   'in a browser.',
                    'hint': 'C-c C-e h o'},
                   {'instruction': 'Put the cursor on one subtree and export '
                                   'only that, using the C-s toggle in the '
                                   'dispatcher.'},
                   {'instruction': 'If you have a LaTeX toolchain, try a PDF. '
                                   'If it fails, read the error: it is almost '
                                   'always the missing toolchain, not the '
                                   'document.'}],
         'free': 'On your own machine: export one org file to markdown and to '
                 'HTML, and export a single subtree on its own.',
         'verify': {'kind': 'self'},
         'fallback': 'self'},
                  ],

    # ------------------------------------------------------------------
    'quiz': [
        {'id': 'oq-todo-vs-checkbox', 'type': 'mcq',
         'prompt': 'Why is a TODO heading different from a checkbox?',
         'answer': 'A heading has a subtree, can be scheduled and refiled, and '
                   'reaches the agenda.',
         'distractors': ['A checkbox cannot be marked done.',
                         'Only headings can carry tags; both reach the agenda.',
                         'They are the same, one is just shorter to type.'],
         'teach': 'This is the first real departure from Obsidian, where a '
                  'checkbox is the only task primitive. Use checkboxes for '
                  'sub-steps and headings for real tasks.'},

        {'id': 'oq-scheduled-deadline', 'type': 'mcq',
         'prompt': 'What is the difference between SCHEDULED and DEADLINE?',
         'answer': 'SCHEDULED is when to start; DEADLINE is when it is due.',
         'distractors': ['SCHEDULED is a due date; DEADLINE is a hard cutoff.',
                         'They are synonyms with different agenda colours.',
                         'SCHEDULED repeats; DEADLINE happens once.'],
         'teach': 'The agenda treats them differently and conflating them is '
                  'the most common org planning mistake.'},

        {'id': 'oq-agenda-empty', 'type': 'mcq',
         'prompt': 'Your agenda is empty even though you have scheduled tasks. '
                   'What is the usual cause?',
         'answer': 'The file is not in org-agenda-files.',
         'distractors': ['The tasks are DONE.',
                         'You have not run doom sync.',
                         'The dates are in the past.'],
         'teach': 'The agenda is computed only from files org has been told '
                  'about. Nothing else will make a correctly scheduled task '
                  'invisible.'},

        {'id': 'oq-capture-purpose', 'type': 'mcq',
         'prompt': 'What is capture actually for?',
         'answer': 'Getting a thought out of your head without a context switch.',
         'distractors': ['Filing notes into the right place immediately.',
                         'Creating files from templates.',
                         'Importing notes from other applications.'],
         'teach': 'Capture is deliberately careless; refile is the careful half. '
                  'If capturing costs you a context switch you stop doing it.'},

        {'id': 'oq-refile', 'type': 'mcq',
         'prompt': 'What does C-c C-w move?',
         'answer': 'The whole subtree, with its tags, state and notes.',
         'distractors': ['Just the heading line.',
                         'The heading and its direct children only.',
                         'A copy, leaving the original in place.'],
         'teach': 'Refile is not cut and paste. It preserves the subtree and '
                  'it is undoable.'},

        {'id': 'oq-structure-edit', 'type': 'mcq',
         'prompt': 'You press M-Right on a heading that has three children. '
                   'What happens?',
         'answer': 'Only the heading moves, and its children are left behind '
                   'at their old depth.',
         'distractors': ['The heading and all three children are demoted '
                         'together.',
                         'The children are promoted to take its place.',
                         'Nothing; M-Right only works on childless headings.'],
         'teach': 'M-Right demotes the heading alone. Hold Shift, M-S-Right, to '
                  'take the subtree with it. M-Up and M-Down do move the whole '
                  'subtree, which is where the expectation comes from.'},

        {'id': 'oq-links', 'type': 'mcq',
         'prompt': 'You rename a file. What happens to org links pointing at it?',
         'answer': 'They break, because org links resolve by path.',
         'distractors': ['They update automatically, as in Obsidian.',
                         'They resolve by filename search and still work.',
                         'They become plain text but stay readable.'],
         'teach': 'The trade is real: Obsidian resolves by name and fixes '
                  'renames, org resolves by path and can point at things '
                  'Obsidian has no concept of, like a specific heading.'},

        {'id': 'oq-ctrl-c-ctrl-c', 'type': 'mcq',
         'prompt': 'What does C-c C-c do?',
         'answer': 'Whatever is obvious for the thing under the cursor.',
         'distractors': ['Always toggles a checkbox.',
                         'Always saves and exits the buffer.',
                         'Always confirms a capture.'],
         'teach': 'It is context sensitive, which is why it is worth pressing '
                  'on anything you are unsure about.'},

        {'id': 'oq-vs-obsidian', 'type': 'mcq',
         'prompt': 'You already keep notes in Obsidian. What is the sensible '
                   'way to start with org?',
         'answer': 'Keep the vault and give org one inbox file and an agenda.',
         'distractors': ['Migrate the vault to org so everything is in one '
                         'place.',
                         'Use org-roam to replicate the vault in Emacs.',
                         'Run both fully and duplicate notes between them.'],
         'teach': 'The two are strong in almost non-overlapping places. '
                  'Migrating costs weeks, loses the graph, and teaches you '
                  'nothing a single inbox file would not have.'},
    ],
}
