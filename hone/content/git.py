"""git: the model first, because the CLI only makes sense afterwards.

The roster calls git the hardest tool in common daily use, and the reason is
specific: the underlying model is small and clean, and the command line that
sits on it is inconsistent enough to hide it. People memorise incantations,
the incantations fail in a slightly different situation, and there is nothing
underneath to reason from.

So lessons one and two are the model, and everything after is commands read as
operations on it. Someone who holds "commits are snapshots, refs are pointers,
branches are labels that move" can work out what `reset --hard` does. Someone
who has memorised `reset --hard` cannot work out anything.

Challenges use the git adapter, which makes this one of the best-verified
modules in the roster: every question a challenge wants to ask has a plumbing
command that answers it exactly.
"""

MODULE = {
    'id': 'git',
    'title': 'git',
    'group': 'Version control',
    'blurb': 'The commit graph, and the commands that move pointers around it.',
    'context': 'You are at a shell inside a git repository with some history and a clean-ish working tree.',
    'needs': ('git',),
    'prereqs': ['linux'],
    'adapter': 'git',
    'estimate': '6-8 hours',
    'order': 50,

    'lessons': [
        {
            'id': 'git-why',
            'title': 'The problem git is solving',
            'next': 'git-model',
            'concept': (
                'Before any commands, the problem. Everyone who has written '
                'anything has invented a worse version of git by accident:\n\n'
                '```\n'
                'report.doc\n'
                'report-v2.doc\n'
                'report-final.doc\n'
                'report-final-ACTUAL.doc\n'
                'report-final-ACTUAL-jos-edits.doc\n'
                '```\n\n'
                'That directory is a version control system. It is just a bad '
                'one. It cannot tell you what changed between two of those '
                'files, it cannot merge Jo\'s edits with yours, it cannot say '
                'who wrote which sentence or why, and it grows forever.\n\n'
                '**git is a program that keeps the history of a directory.** '
                'You tell it, at moments you choose, "save the state of '
                'everything right now, and here is why". It stores that, '
                'cheaply, forever. Later you can see any past state, compare '
                'any two, find when a particular line appeared, and combine '
                'work done by several people who were all editing at '
                'once.\n\n'
                'Two things make it feel harder than that description '
                'sounds.\n\n'
                '**It is distributed.** There is no central server that owns '
                'the truth. Every copy is complete, with the full history, '
                'and services like GitHub are just another copy that everyone '
                'agrees to meet at. This is why you can commit on a plane.\n\n'
                '**Its command names are historical rather than logical.** '
                'The model underneath is small and clean; the interface grew '
                'over twenty years and it shows. Someone who understands the '
                'model can work out what a command probably does. Someone who '
                'has memorised commands is lost the first time something goes '
                'sideways. So the next lesson is the model, and it is the '
                'most valuable one here.'
            ),
            'examples': [
                {
                    'label': 'The same directory, both ways',
                    'code': ('without git        with git\n'
                             '-----------        --------\n'
                             'report.doc         report.doc\n'
                             'report-v2.doc      + a history of every\n'
                             'report-final.doc     version, each with\n'
                             'report-FINAL2.doc    a message and an author'),
                    'note': 'One file on disk, always the current one. The '
                            'history lives in a hidden .git directory beside '
                            'it and never clutters your view.',
                },
                {
                    'label': 'What it lets you ask',
                    'code': ('what changed since yesterday?\n'
                             'who wrote this line, and why?\n'
                             'what did this look like last Tuesday?\n'
                             'combine my work with theirs\n'
                             'undo that, but keep the rest'),
                    'note': 'Every one of these is a command you will meet. '
                            'They are all reading the same history from a '
                            'different angle.',
                },
                {
                    'label': 'The three places a file can be',
                    'code': ('working tree   the files you are editing\n'
                             '     |  git add\n'
                             'index          what will go in next commit\n'
                             '     |  git commit\n'
                             'history        saved, permanently'),
                    'note': 'The middle one is the bit no other tool has, and '
                            'it is the source of most early confusion. It has '
                            'a lesson of its own shortly.',
                },
            ],
            'misconceptions': [
                'git is not GitHub. git is the program on your machine; '
                'GitHub is a company hosting copies of git repositories. You '
                'can use git for years without an account anywhere.',
                'A commit is not a backup of changed files. It is a snapshot '
                'of the whole project at a moment, which is why checking out '
                'an old commit gives you the entire project as it was.',
                'git does not need a network. Committing, branching, viewing '
                'history and searching are all local, and only push and pull '
                'talk to anyone.',
            ],
            'try_it': [
                'Run `git init` in a throwaway directory and look at what '
                'appeared: `ls -a` shows one hidden directory, and that is '
                'the entire system.',
                'Think of the last time you kept a file named "-final". That '
                'instinct is correct and git is the version of it that '
                'works.',
            ],
        },
        {
            'id': 'git-model',
            'title': 'Commits, refs, and why branches are cheap',
            'next': 'git-three-trees',
            'concept': (
                'Commits, refs and branches are how git stores history as a '
                'graph of snapshots. That is why a branch is a 41-byte file, '
                'and why checking out an old commit restores the whole '
                'project. A commit is not a diff. It also records its parent, '
                'which is what turns a pile of snapshots into a graph. Diffs '
                'are computed between two commits when you ask for them; they '
                'are not what is stored.\n\n'
                'A branch is a **pointer to one commit**, stored as a file '
                'containing a hash. That is the entire implementation. Making a '
                'branch writes forty-one bytes, which is why branching in git '
                'is instant and why the advice to branch freely is not '
                'bravado.\n\n'
                '`HEAD` is a pointer to where you are, and usually points at a '
                'branch rather than directly at a commit. Committing moves the '
                'branch forward and HEAD follows. Almost every git command you '
                'will learn is moving one of these pointers or building a new '
                'commit for one to point at.\n\n'
                'That is why branches are cheap: you are writing a 41-byte '
                'file, not copying a project. Deleting a branch deletes that '
                'file. The commits stay if any other name still reaches them, '
                'and vanish later if nothing does. People treat "delete the '
                'branch" as "delete the work" because other systems stored '
                'the work *in* the branch. git stores the work in the graph '
                'and hangs labels on it.\n\n'
                'The next lesson is the three places a file exists at once, '
                'because that is what `git status` is actually reporting.'
            ),
            'examples': [
                {
                    'label': 'The graph',
                    'code': ('A <- B <- C  <- main   <- HEAD\n'
                             '      \\\n'
                             '       D <- E  <- feature\n'
                             '\n'
                             'each letter is a full snapshot\n'
                             'each arrow points at a PARENT\n'
                             'main and feature are just labels'),
                    'note': 'Every history diagram in every git tutorial is '
                            'this. Once it is in your head the commands stop '
                            'being arbitrary.',
                },
                {
                    'label': 'A branch really is a file',
                    'code': ('$ cat .git/refs/heads/main\n'
                             '3f2a91c8e0b4d5a7f6c3e2b1a0d9c8b7a6f5e4d3\n'
                             '\n'
                             '$ cat .git/HEAD\n'
                             'ref: refs/heads/main'),
                    'note': 'Nothing is hidden. You can read the whole model '
                            'with cat.',
                },
            ],
            'misconceptions': [
                'A commit does not store a diff. It stores a complete tree, '
                'which is why checking out an old commit is fast and why git '
                'does not slow down as history grows.',
                'Branches do not contain commits. Several branches can point '
                'into the same chain, and deleting a branch deletes a label, '
                'not the work.',
                'The commit hash is of the content, the parent, the author and '
                'the message together. Change any of them and it is a different '
                'commit, which is why rewriting history creates new commits '
                'rather than editing old ones.',
            ],
            'try_it': [
                'In any repository, run `cat .git/HEAD` and then `git log '
                "--oneline --graph --all` and match the picture to the file.",
            ],
        },
        {
            'id': 'git-three-trees',
            'title': 'Three trees, and what the index is for',
            'next': 'git-basics',
            'concept': (
                'git has three places your files exist at once, and every '
                'confusing message is about the difference between them.\n\n'
                'The **working tree** is what is on disk. The **index**, also '
                'called the staging area, is what your next commit will '
                'contain. **HEAD** is what your last commit contained.\n\n'
                'The index is the part other version control systems do not '
                'have, and it exists so a commit can be smaller than your '
                'changes. You fixed a bug and also renamed a variable; `git add '
                '-p` lets you commit those separately. That is the whole '
                'justification, and once you use it once it stops feeling like '
                'bureaucracy.\n\n'
                '`git status` is a report on the two gaps: between HEAD and the '
                'index, and between the index and the working tree.\n\n'
                '`git restore file` copies from the index onto disk, so you '
                'lose unstaged edits. `git restore --source=HEAD file` copies '
                'from the last commit, skipping the index. `git restore '
                '--staged file` copies from HEAD into the index and leaves '
                'the working tree alone, which is how you unstage without '
                'undoing the edit. Mixing those up is why "I unstaged it and '
                'my file went back" is sometimes true and sometimes not: it '
                'depends which restore you ran.\n\n'
                'The next lesson is the daily loop that moves files across '
                'those three places: status, add, commit, log.'
            ),
            'examples': [
                {
                    'label': 'The three, and what moves between them',
                    'code': ('HEAD  <--commit--  index  <--add--  working tree\n'
                             '  |                  |                 |\n'
                             '  |                  |--- restore --->  |\n'
                             '  |--- reset ------->  |                |\n'
                             '  |--- restore --source=HEAD -------->  |\n'
                             '\n'
                             'git diff           index vs working tree\n'
                             'git diff --staged  HEAD vs index'),
                    'note': 'Two diffs because there are two gaps. Plain `git '
                            'diff` not showing your staged work is not a bug.',
                },
                {
                    'label': 'Committing part of your work',
                    'code': ('git add -p file      choose hunk by hunk\n'
                             'git commit -m "fix"  only what you staged\n'
                             'git status           the rest is still there'),
                    'note': 'This is the reason the index exists.',
                },
            ],
            'misconceptions': [
                '`git diff` shows unstaged changes only. Once you stage '
                'something it disappears from that output, which reads like '
                'the change was lost.',
                '`git commit -a` skips the index for tracked files, and skips '
                'untracked ones entirely. It is a shortcut, not a "commit '
                'everything".',
                'Staging is not saving. Nothing in the index is safe from a '
                '`reset --hard` and it is not in your history until you '
                'commit.',
            ],
            'try_it': [
                'Edit two things in one file, `git add -p`, stage one hunk, and '
                'compare `git diff` with `git diff --staged`.',
            ],
        },
        {
            'id': 'git-basics',
            'title': 'The daily loop',
            'next': 'git-branches',
            'concept': (
                'Status, add, commit, log. Most days are only these. A '
                'machine that has never committed needs `git config '
                '--global user.name` and `user.email` first, or commit '
                'refuses. `git clone url` copies a remote; `git init` '
                'starts an empty one.\n\n'
                '`git status` first, always. It tells you which branch you are '
                'on, what is staged, what is not, and what is untracked, and it '
                'suggests the command for whatever you probably want next. '
                'Reading it properly removes most of the need to memorise '
                'anything.\n\n'
                'A commit message is worth more thought than it usually gets. '
                'The first line is a summary in the imperative, under about '
                'fifty characters, and if there is more to say a blank line '
                'then prose. The reason is that git tooling everywhere shows '
                'you only the first line, so "fix stuff" is a message you will '
                'meet again when you least want it.\n\n'
                '`git add file` does not mean "this is a new file". It means '
                '"put the current bytes of this path into the index". You do '
                'it every time the file changes, including the twentieth '
                'edit. Forgetting that is why people commit an old version: '
                'they edited after `add` and never added again. `git status` '
                'says `modified` under "Changes not staged" when that has '
                'happened.\n\n'
                '`git show HEAD` is one commit as a message and a patch. '
                '`git log -p` is the same idea walking history: each commit, '
                'then its diff. `--oneline` is the summary; `-p` is the '
                'change. Read `show` when you know which commit. Read '
                '`log -p` when you do not.\n\n'
                'A commit is local. Nothing has left the machine.\n\n'
                '`git stash` puts the working-tree mess aside without making '
                'a commit. `git stash pop` brings it back. The stash is a '
                'scratch pile, not history: it is not on a branch, it does '
                'not show in `git log`, and a drop loses it. Stash when the '
                'tree is dirty and a switch is needed. Commit when the '
                'change is meant to stay.\n\n'
                '`git commit --amend` folds the current index into the last '
                'commit and rewrites that commit. That is safe only if the '
                'commit has not been pushed, because anyone who already '
                'pulled the old hash now has a different history. After a '
                'push, a new commit is the honest fix.\n\n'
                '`.gitignore` stops untracked files from appearing in `git '
                'status`. It does not untrack a file that is already in the '
                'index. A secret committed and then added to `.gitignore` is '
                'still in history. `git rm --cached file` drops it from the '
                'index and leaves the working copy.\n\n'
                'The next lesson is branches: how those local commits grow a '
                'second line of history, and what merge does when the lines '
                'meet.'
            ),
            'examples': [
                {
                    'label': 'The loop',
                    'code': ('git status                 what is going on\n'
                             'git add file               stage one file\n'
                             'git add -p                 stage part of one\n'
                             'git commit -m "message"    commit the index\n'
                             'git log --oneline --graph  read the history\n'
                             'git show HEAD              what was in that one\n'
                             'git log -p                 history as patches'),
                    'note': '`git log --oneline --graph --all --decorate` is '
                            'worth an alias. It draws the picture from lesson '
                            'one.',
                },
                {
                    'label': 'A message that ages well',
                    'code': ('Fix crash when config file is missing\n'
                             '\n'
                             'The loader assumed the file existed and threw a\n'
                             'raw IOError. Fall back to defaults instead.\n'
                             '\n'
                             'not:  fixes\n'
                             'not:  WIP\n'
                             'not:  addressed review comments'),
                    'note': 'Imperative mood, because it completes the sentence '
                            '"applying this commit will...".',
                },
                {
                    'label': 'Stash, amend, and ignore',
                    'code': (
                        'git stash                 put the mess aside\n'
                        'git stash pop             bring it back\n'
                        'git commit --amend        rewrite the last commit\n'
                        '                           only if it was not pushed\n'
                        '\n'
                        'echo "*.o" >> .gitignore  stop tracking new objects\n'
                        'git rm --cached secret    untrack, leave the file'
                    ),
                    'note': 'stash is not a commit. amend rewrites history. '
                            '.gitignore does not untrack what is already in '
                            'the index.',
                },
            ],
            'misconceptions': [
                '`git add` does not mean "add a new file". It means "put this '
                'version into the index", and you do it every time you change a '
                'file, not once.',
                '`git commit` with no `-m` opens your editor and an empty '
                'message aborts the commit, which is the escape hatch when you '
                'did not mean to commit.',
                'Committing is local. Nothing has gone anywhere until you push.',
                '`git stash` is not a commit. It is a scratch pile, and a '
                'drop loses the work because it was never in history.',
                '`.gitignore` does not untrack a file already in the index. '
                '`git rm --cached` is the extra step.',
                '`git commit --amend` is only safe before a push. After a '
                'push it rewrites a hash other people already have.',
            ],
            'try_it': [
                'Run `git log --oneline --graph --all --decorate` in a repo '
                'with branches and compare it to lesson one\'s diagram.',
            ],
        },
        {
            'id': 'git-branches',
            'title': 'Branching and merging',
            'next': 'git-remotes',
            'concept': (
                'Branching is how you grow a second line of history without '
                'copying the project. That is why a feature can be committed '
                'on its own and merged later.\n\n'
                '`git switch -c name` creates and moves to a branch. `git '
                'switch name` moves to an existing one. These are newer and '
                'clearer than `checkout`, which did both of those jobs plus '
                'several unrelated ones and is why `checkout` confused everyone '
                'for a decade.\n\n'
                'Merging has two shapes. If the target branch has not moved '
                'since you branched, git just slides the pointer forward: a '
                '**fast-forward**, with no merge commit. If both have moved, '
                'git builds a **merge commit** with two parents. Neither is '
                'better; knowing which you are getting is what stops merges '
                'being surprising.\n\n'
                'When both branches changed the same lines, git stops and hands '
                'you a **conflict**, and this is the part worth practising '
                'because the markers look alarming and are not. git writes both '
                'versions into the file between markers: everything from '
                '`<<<<<<<` to `=======` is your side, everything from there to '
                '`>>>>>>>` is theirs. You edit the file to what it should '
                'actually be, delete all three marker lines, `git add` it to '
                'say "resolved", and `git commit` to finish the merge. There is '
                'no magic: you are choosing the final text by hand. If it goes '
                'wrong, `git merge --abort` puts everything back as if you never '
                'started, which is the escape hatch worth knowing before you '
                'need it.'
            ),
            'examples': [
                {
                    'label': 'Branching',
                    'code': ('git switch -c feature     create and move\n'
                             'git switch main           move back\n'
                             'git switch -               the previous branch\n'
                             'git branch                 list local\n'
                             'git branch -d feature      delete (safely)\n'
                             'git merge feature          merge into current'),
                    'note': '`-d` refuses if the branch is unmerged; `-D` does '
                            'not. Prefer `-d` and let it protect you.',
                },
                {
                    'label': 'Reading and resolving a conflict',
                    'code': ('<<<<<<< HEAD\n'
                             'the line as it is on your branch\n'
                             '=======\n'
                             'the line as it is on theirs\n'
                             '>>>>>>> feature\n'
                             '\n'
                             'edit to the final text, delete the 3 markers,\n'
                             'then:  git add file  &&  git commit\n'
                             'or give up:  git merge --abort'),
                    'note': 'The markers are just text git inserted. Nothing is '
                            'broken; you are choosing the result.',
                },
                {
                    'label': 'The two shapes',
                    'code': ('fast-forward:   A-B-C          A-B-C\n'
                             '                    ^main   ->     ^main ^feature\n'
                             '\n'
                             'merge commit:   A-B-C-M   M has two parents\n'
                             '                   \\ /\n'
                             '                    D-E'),
                    'note': '`git merge --no-ff` forces a merge commit even when '
                            'a fast-forward was possible, which some teams want '
                            'so the branch is visible in history.',
                },
            ],
            'misconceptions': [
                'A conflict is not an error. It is git saying two people '
                'changed the same lines and it will not guess. Edit the file, '
                '`git add` it, and `git commit`.',
                'Deleting a merged branch loses nothing. The commits are '
                'reachable from wherever you merged them.',
                '`git checkout` still works and still does five unrelated '
                'things. `switch` and `restore` split those jobs up, and are '
                'the ones to learn.',
            ],
            'try_it': [
                'Make a branch, commit on it, switch back, and run `git merge`. '
                'Note whether it says "Fast-forward".',
            ],
        },
        {
            'id': 'git-remotes',
            'title': 'Remotes, fetch and push',
            'next': 'git-undo',
            'concept': (
                'A remote is how this repository talks to a copy on another '
                'machine, usually called `origin`. That is why your `main` '
                'and `origin/main` are different branches that share a name, '
                'and why you cannot commit to `origin/main`.\n\n'
                '`git fetch` downloads their commits and updates your '
                '`origin/main` pointer. It changes nothing you are working on. '
                '`git pull` is fetch **plus** a merge into your current branch, '
                'which is where surprises come from: it changes your files.\n\n'
                'The habit worth building is `git fetch` then `git log '
                '..origin/main` to see what arrived, then merge or rebase '
                'deliberately. `pull` is fine when you know your branch is '
                'clean and behind; it is where accidental merge commits come '
                'from otherwise.\n\n'
                '`origin/main` is a local file under `.git/refs/remotes/`. '
                'It moves when you fetch, not when they push. That is why '
                '`git log main..origin/main` can look stale: you have not '
                'fetched. A rejected push (`failed to push some refs`) almost '
                'always means their `main` has commits your `main` does not. '
                'Fetch, integrate, push again. `--force` overwrites their '
                'copy with yours, which is how shared branches lose work.\n\n'
                'The next lesson is undoing: restore, reset, revert, and the '
                'reflog that makes most of those reversible.'
            ),
            'examples': [
                {
                    'label': 'Two branches that share a name',
                    'code': ('main           your pointer, you commit here\n'
                             'origin/main    last fetched copy of theirs\n'
                             '\n'
                             'git fetch      origin/main moves\n'
                             'git push       their main moves, if allowed'),
                    'note': 'Same name, two pointers, two machines. Mixing '
                            'them up is most of "I pushed and it vanished".',
                },
                {
                    'label': 'Talking to a remote',
                    'code': ('git clone URL              copy it locally\n'
                             'git remote -v              what remotes exist\n'
                             'git fetch                  download, change nothing\n'
                             'git log ..origin/main      what arrived\n'
                             'git pull                   fetch plus merge\n'
                             'git pull --rebase          fetch plus rebase\n'
                             'git push                   send your commits\n'
                             'git push -u origin feature set upstream, first time'),
                    'note': '`-u` records the tracking branch so later `git push` '
                            'needs no arguments.',
                },
            ],
            'misconceptions': [
                '`origin/main` is not a branch you can commit to. It is your '
                'local record of where their main was at the last fetch.',
                'A rejected push usually means the remote has commits you do '
                'not. Fetch and integrate; `--force` overwrites their work.',
                '`git pull` on a branch with local commits creates a merge '
                'commit. `--rebase` is what most people actually wanted.',
            ],
            'try_it': [
                'Run `git fetch` then `git log --oneline ..origin/main` in a '
                'repo with a remote. That is what pull would have merged.',
            ],
        },
        {
            'id': 'git-undo',
            'title': 'Undoing things, and the reflog',
            'next': 'git-rewrite',
            'concept': (
                'Restore, reset and revert are how you undo, and each touches '
                'a different place. That is why the same instinct, go back, is '
                'three commands rather than one.\n\n'
                '`git restore file` throws away working-tree changes to that '
                'file. `git restore --staged file` unstages without touching '
                'the file. `git reset --soft C` moves the branch to C and keeps '
                'everything staged. `git reset --mixed C`, the default, moves '
                'the branch and unstages. `git reset --hard C` moves the branch '
                'and **destroys** your working tree.\n\n'
                '`git revert C` is different in kind: it makes a **new commit** '
                'that undoes C, which is what you want on anything already '
                'pushed, because it changes nothing that exists.\n\n'
                'And the safety net: **`git reflog`** records every position '
                'HEAD has held, including ones no branch points at any more. '
                'Almost anything you think you destroyed is in there for weeks. '
                'It is the single most reassuring command in git.\n\n'
                '`reset --hard` and `restore` without `--staged` are the two '
                'that destroy uncommitted work, and the reflog cannot help: '
                'it only records commits and HEAD moves. Work that was never '
                'committed is not in there. That is why `status` first is not '
                'politeness. On anything already pushed, `revert` is the '
                'undo, because it adds a commit instead of moving a pointer '
                'other people already have.\n\n'
                'The next lesson is rebase, which also moves history, and '
                'the rule that keeps it from becoming other people\'s problem.'
            ),
            'examples': [
                {
                    'label': 'Sorted by what they touch',
                    'code': ('restore file          working tree only\n'
                             'restore --staged f    index only\n'
                             'reset --soft C        branch only\n'
                             'reset --mixed C       branch + index (default)\n'
                             'reset --hard C        branch + index + files\n'
                             'revert C              new commit undoing C'),
                    'note': '`restore file` and `reset --hard` are the two that can lose work you have not committed. '
                            'Everything else is recoverable.',
                },
                {
                    'label': 'The safety net',
                    'code': ('git reflog                     everywhere HEAD went\n'
                             'git reset --hard HEAD@{3}      go back to one\n'
                             'git switch -c rescue HEAD@{3}  or branch from it'),
                    'note': 'Try this before believing anything is gone. '
                            'Commits stay reachable for weeks.',
                },
            ],
            'misconceptions': [
                '`reset` and `revert` are not variations on one idea. reset '
                'moves a pointer; revert creates a commit. Use revert for '
                'anything already pushed.',
                '`reset --hard` and `restore file` are the two that destroy uncommitted work, '
                'and there is no reflog for work that was never committed.',
                '`git checkout -- file` was the old spelling of `restore`, '
                'which is why old answers look nothing like current advice.',
            ],
            'try_it': [
                'Commit something, `git reset --hard HEAD~1`, then `git reflog` '
                'and bring it back. Do it once so you trust it.',
            ],
        },
        {
            'id': 'git-rewrite',
            'title': 'Rebase, and when not to',
            'next': 'git-detached',
            'concept': (
                'Rebase replays your commits on top of a different base, '
                'producing new commits with new hashes and a linear history. '
                'Merge preserves what happened; rebase makes it read as though '
                'it happened in order.\n\n'
                'Interactive rebase, `git rebase -i`, is the same machinery '
                'aimed at your own recent work: reorder, squash, reword, drop. '
                'This is how six commits of "wip", "fix", "actually fix" become '
                'one that a reviewer can read.\n\n'
                'The rule that matters is simple: **do not rebase anything you '
                'have pushed and others may have.** Rewriting makes new '
                'commits, so anyone holding the old ones now has a divergent '
                'history and their next pull is a mess. Rebase your own '
                'unpushed work freely, and merge everything else.\n\n'
                'A rebase conflict stops on each replayed commit, so one '
                'rebase can ask you to fix the same file three times. That '
                'is not a loop. It is commit A, then B, then C, each applied '
                'onto the new base. `git rebase --abort` puts the branch '
                'back where it started. After a rebase you have already '
                'pushed, `git push --force-with-lease` updates the remote '
                'only if nobody else pushed in the meantime; `--force` does '
                'not check.\n\n'
                '`git cherry-pick HASH` copies one commit onto this branch. '
                '`git tag -a v1.0` names a commit; `git push --tags` sends '
                'the names. `git bisect start` then `good`/`bad` walks '
                'history to the first bad commit. `git blame file` names '
                'who last touched each line. Those four are how you move, '
                'name, hunt, and attribute a commit after the daily loop.\n\n'
                'The last lesson is detached HEAD, which is the same pointer '
                'model with the branch label taken off.'
            ),
            'examples': [
                {
                    'label': 'Cleaning up before review',
                    'code': ('git rebase -i HEAD~4\n'
                             '\n'
                             'pick  a1b2  Add parser\n'
                             'squash c3d4  wip\n'
                             'squash e5f6  fix typo\n'
                             'reword 7g8h  Add tests\n'
                             '\n'
                             '-> two clean commits instead of four'),
                    'note': 'Editing the list top to bottom is chronological, '
                            'oldest first, which is the opposite of `git log`.',
                },
                {
                    'label': 'The rule',
                    'code': ('unpushed, yours       rebase freely\n'
                             'pushed, shared        merge, never rebase\n'
                             'pushed, only yours    rebase, then force-with-lease\n'
                             '\n'
                             'git push --force-with-lease   not --force'),
                    'note': '`--force-with-lease` refuses if someone else pushed '
                            'meanwhile. Plain `--force` does not, and that is '
                            'the difference between careful and destructive.',
                },
            ],
            'misconceptions': [
                'Rebase does not move commits. It copies them, so the originals '
                'are still in the reflog if it goes wrong.',
                'A rebase conflict is resolved per commit, which is why one '
                'rebase can stop several times. `git rebase --abort` puts '
                'everything back.',
                'Squashing is not required to be tidy. A series of small honest '
                'commits is often better than one large squashed one.',
            ],
            'try_it': [
                'Make three throwaway commits on a branch and squash them into '
                'one with `git rebase -i HEAD~3`.',
            ],
        },
        {
            'id': 'git-detached',
            'title': 'Detached HEAD, and why it is not a problem',
            'concept': (
                'Detached HEAD is how you look at an old commit without moving '
                'a branch. That is why git warns: commits you make there '
                'vanish unless you hang a label on them.\n\n'
                'It matters for one reason: commits you make there have no '
                'branch pointing at them, so when you switch away nothing '
                'refers to them and they eventually get cleaned up. That is the '
                'entire danger, and `git switch -c name` at any point fixes it '
                'by giving them a label.\n\n'
                'Once lesson one is solid this is obvious rather than '
                'frightening: HEAD is a pointer, it usually points at a branch, '
                'and sometimes it does not.\n\n'
                'You get here by checking out a commit hash, a tag, or '
                '`HEAD~2`. git prints a long warning because the next '
                '`commit` has no branch to advance, so `switch main` later '
                'leaves those commits reachable only from the reflog. That '
                'is the entire danger. It is not a corrupt repository. '
                '`git switch -c rescue` at any moment hangs a label on '
                'where you are, and the warning goes away because HEAD '
                'points at a branch again.\n\n'
                'If you already switched away, `git reflog` still has the '
                'hash. This module ends here because once the pointers are '
                'solid, the rest of git is names for moving them.'
            ),
            'examples': [
                {
                    'label': 'What detached means in the files',
                    'code': ('on a branch:    .git/HEAD -> ref: refs/heads/main\n'
                             'detached:       .git/HEAD -> a1b2c3d4...\n'
                             '\n'
                             'commit now:     new hash, no branch file updated\n'
                             'switch -c fix:  new branch file, HEAD points at it'),
                    'note': 'Read .git/HEAD. The warning is that file no '
                            'longer saying ref:.',
                },
                {
                    'label': 'Getting there and back',
                    'code': ('git switch --detach HEAD~2   deliberately\n'
                             'git checkout a1b2c3d         also detaches\n'
                             '\n'
                             'git switch -c rescue         keep what you did\n'
                             'git switch -                 or just leave'),
                    'note': 'If you already left and lost commits, the reflog '
                            'still has them.',
                },
            ],
            'misconceptions': [
                'Detached HEAD is not a broken repository. It is a normal state '
                'that git is warning you about because it is easy to lose work '
                'from.',
                'You can commit while detached. The commits are real; they are '
                'just unreferenced.',
            ],
            'try_it': [
                'Run `git switch --detach HEAD~1`, read the message properly, '
                'then `git switch -`.',
            ],
        },
    ],

    'drills': [
        {'id': 'g-status', 'type': 'command', 'answer': 'git status',
         'prompt': 'Find out what is staged, what is not, and which branch you '
                   'are on.',
         'teach': 'Run it first, always. It also suggests the command for '
                  'whatever you probably want next.'},
        {'id': 'g-clone', 'type': 'command',
         'answer': 'git clone url',
         'prompt': 'Copy a remote repository to this machine.',
         'teach': 'clone is how you start from someone else\'s history. init is an empty one.'},
        {'id': 'g-cherry', 'type': 'command',
         'answer': 'git cherry-pick HASH',
         'prompt': 'Copy one existing commit onto this branch.',
         'teach': 'cherry-pick copies a commit. merge brings a whole line of history.'},
        {'id': 'g-add', 'type': 'command', 'answer': 'git add file',
         'prompt': 'Stage the current bytes of a path called file.',
         'teach': 'add means put these bytes in the index, not "this is a new file". Do it again after every edit.'},
        {'id': 'g-show', 'type': 'command', 'answer': 'git show HEAD',
         'prompt': 'Print the latest commit, message and patch.',
         'teach': 'show is one commit. log -p is the same idea, walking history.'},
        {'id': 'g-log-p', 'type': 'command', 'answer': 'git log -p',
         'prompt': 'Walk history and show each commit as a patch.',
         'teach': '-p is the diff. --oneline is the summary. Use both.'},
        {'id': 'g-merge-abort', 'type': 'command', 'answer': 'git merge --abort',
         'prompt': 'Give up on a merge that stopped with conflicts.',
         'teach': 'Puts the branch back as if you never merged. rebase --abort is the sibling.'},
        {'id': 'g-add-p', 'type': 'command', 'answer': 'git add -p',
         'prompt': 'Stage some of your changes but not all of them, choosing '
                   'hunk by hunk.',
         'teach': 'This is the reason the index exists.'},
        {'id': 'g-commit', 'type': 'command', 'answer': 'git commit -m "message"',
         'prompt': 'Commit what is staged, with a message, without opening an '
                   'editor.',
         'teach': 'Without a message git opens your editor. The message is '
                  'not optional, so leaving it empty aborts the commit.'},
        {'id': 'g-log-graph', 'type': 'command',
         'answer': 'git log --oneline --graph --all',
         'prompt': 'Draw the commit graph for every branch, one line per commit.',
         'teach': 'This is the picture from the first lesson, generated from '
                  'your own repository.'},
        {'id': 'g-diff', 'type': 'command', 'answer': 'git diff',
         'prompt': 'Show changes you have made but not yet staged.',
         'teach': 'With no arguments it shows unstaged changes only. Add '
                  '--staged to see what you are actually about to commit, '
                  'which is the more useful review.'},
        {'id': 'g-diff-staged', 'type': 'command', 'answer': 'git diff --staged',
         'accepts': ['git diff --cached'],
         'prompt': 'Show changes you have staged but not yet committed.',
         'teach': 'Two diffs because there are two gaps: HEAD to index, and '
                  'index to working tree.'},
        {'id': 'g-switch-c', 'type': 'command', 'answer': 'git switch -c feature',
         'prompt': 'Create a branch called feature and move to it.',
         'teach': 'switch and restore split up the several unrelated jobs '
                  'checkout used to do.'},
        {'id': 'g-switch', 'type': 'command', 'answer': 'git switch main',
         'prompt': 'Move to the existing branch called main.',
         'teach': 'switch is for branches and restore is for files. checkout '
                  'did both, which is exactly why it was confusing enough to '
                  'split in two.'},
        {'id': 'g-switch-back', 'type': 'command', 'answer': 'git switch -',
         'prompt': 'Return to the branch you were on before this one.',
         'teach': 'The dash means the previous branch, the same way it does '
                  'in cd.'},
        {'id': 'g-merge', 'type': 'command', 'answer': 'git merge feature',
         'prompt': 'Merge the feature branch into the branch you are on.',
         'teach': 'A merge brings the named branch INTO the one you are '
                  'standing on, so which branch you are on matters more than '
                  'the one you type.'},
        {'id': 'g-branch-d', 'type': 'command', 'answer': 'git branch -d feature',
         'prompt': 'Delete the feature branch, but only if it has been merged.',
         'teach': 'Prefer -d over -D and let it protect you.'},
        {'id': 'g-fetch', 'type': 'command', 'answer': 'git fetch',
         'prompt': 'Download what the remote has, without changing any of your '
                   'files.',
         'teach': 'Fetch updates your view of the remote and touches nothing '
                  'in your working tree, so it is always safe to run.'},
        {'id': 'g-incoming', 'type': 'command', 'answer': 'git log ..origin/main',
         'prompt': 'See which commits the remote has that you do not, after '
                   'fetching.',
         'teach': 'This is what pull would have merged. Looking first is the '
                  'habit worth building.'},
        {'id': 'g-pull-rebase', 'type': 'command', 'answer': 'git pull --rebase',
         'prompt': 'Bring in remote commits and replay yours on top, rather '
                   'than creating a merge commit.',
         'teach': 'Rebasing rewrites your local commits, which is fine '
                  'because nobody else has seen them. Set pull.rebase true to '
                  'make it the default.'},
        {'id': 'g-push-u', 'type': 'command',
         'answer': 'git push -u origin feature',
         'prompt': 'Push a new branch and record it as the upstream so later '
                   'pushes need no arguments.',
         'teach': '-u records the tracking branch. Without it, every later '
                  'push needs the remote and branch spelled out again.'},
        {'id': 'g-restore', 'type': 'command', 'answer': 'git restore file.txt',
         'prompt': 'Throw away your uncommitted changes to file.txt.',
         'teach': 'There is no reflog for work that was never committed, so '
                  'this one is genuinely irreversible.'},
        {'id': 'g-unstage', 'type': 'command',
         'answer': 'git restore --staged file.txt',
         'prompt': 'Unstage file.txt without changing the file itself.',
         'teach': '--staged moves it out of the index and leaves the file '
                  'alone. Drop that flag and it discards your edits instead.'},
        {'id': 'g-reset-soft', 'type': 'command', 'answer': 'git reset --soft HEAD~1',
         'prompt': 'Undo the last commit but keep all of its changes staged.',
         'teach': 'Move the branch pointer back, leave everything else alone. '
                  'This is how you redo a commit message or split a commit.'},
        {'id': 'g-reset-hard', 'type': 'command', 'answer': 'git reset --hard HEAD~1',
         'prompt': 'Undo the last commit and discard its changes entirely.',
         'teach': 'The only reset that destroys uncommitted work. Committed '
                  'work is still in the reflog.'},
        {'id': 'g-revert', 'type': 'command', 'answer': 'git revert HEAD',
         'prompt': 'Undo the last commit by making a new commit, safe to do on '
                   'something already pushed.',
         'teach': 'Revert adds a commit that undoes another; reset removes '
                  'commits. That is why revert is the one that is safe on '
                  'history others have pulled.'},
        {'id': 'g-reflog', 'type': 'command', 'answer': 'git reflog',
         'prompt': 'List everywhere HEAD has been, including commits no branch '
                   'points at any more.',
         'teach': 'The single most reassuring command in git. Try this before '
                  'believing anything is gone.'},
        {'id': 'g-rebase-i', 'type': 'command', 'answer': 'git rebase -i HEAD~3',
         'prompt': 'Reorder, squash or reword your last three commits.',
         'teach': 'HEAD~3 means the last three commits and you edit the list '
                  'of them. Never do this to commits someone else has already '
                  'pulled.'},
        {'id': 'g-force-lease', 'type': 'command',
         'answer': 'git push --force-with-lease',
         'prompt': 'Push rewritten history, but refuse if someone else has '
                   'pushed since you last fetched.',
         'teach': 'Plain --force does not check, which is the difference '
                  'between careful and destructive.'},
        {'id': 'g-stash', 'type': 'command', 'answer': 'git stash',
         'prompt': 'Put your uncommitted changes aside so you can switch '
                   'branches cleanly.',
         'teach': 'A stash is a stack, so pop takes the most recent one back. '
                  'It is easy to leave one there for a month and forget it '
                  'exists.'},
        {'id': 'g-bisect', 'type': 'command', 'answer': 'git bisect start',
         'prompt': 'Begin a binary search through history for the commit that '
                   'introduced a bug.',
         'teach': 'You mark one bad commit and one good one and git checks '
                  'out the midpoint until it finds the change. Ten steps '
                  'covers a thousand commits.'},
        {'id': 'g-blame', 'type': 'command', 'answer': 'git blame file.txt',
         'prompt': 'Find out which commit last changed each line of file.txt.',
         'teach': 'It shows the last commit to touch each line, which is not '
                  'always the one that introduced the bug. -w ignores '
                  'whitespace-only changes.'},
    ],

    'challenges': [
        {
            'id': 'g-first-commit',
            'title': 'Stage and commit',
            'goal': 'Take a change from the working tree, through the index, '
                    'into history.',
            'setup': {'kind': 'git', 'branch': 'main',
                      'tree': {'README.md': '# project\n'},
                      'commits': [{'message': 'initial commit',
                                   'tree': {'README.md': '# project\n'}}]},
            'solution': {'shell': 'echo "hello" > notes.txt && git add notes.txt '
                                  '&& git -c user.email=t@t -c user.name=t '
                                  'commit -q -m "Add notes"'},
            'steps': [
                {'instruction': 'Create a file called notes.txt with something '
                                'in it.', 'hint': 'echo hello > notes.txt'},
                {'instruction': 'Stage it.', 'hint': 'git add notes.txt'},
                {'instruction': 'Commit it with a message mentioning notes.',
                 'hint': 'git commit -m "Add notes"'},
            ],
            'free': 'Create notes.txt, commit it with a message mentioning '
                    'notes, and leave the working tree clean.',
            'verify': {'kind': 'git', 'expect': {
                'branch': 'main', 'commit_count': 2,
                'subjects_contain': 'notes', 'clean': True,
                'exists': ['notes.txt']}},
            'fallback': 'self',
        },
        {
            'id': 'g-branch-merge',
            'title': 'Branch, commit, merge',
            'goal': 'Do the whole branching loop and end up back on main with '
                    'the work included.',
            'setup': {'kind': 'git', 'branch': 'main',
                      'tree': {'app.py': 'print(1)\n'},
                      'commits': [{'message': 'initial commit',
                                   'tree': {'app.py': 'print(1)\n'}}]},
            'solution': {'shell': 'git switch -q -c feature && echo "print(2)" '
                                  '>> app.py && git add -A && git -c '
                                  'user.email=t@t -c user.name=t commit -q '
                                  '-m "Extend app" && git switch -q main '
                                  '&& git -c user.email=t@t -c user.name=t '
                                  'merge -q feature'},
            'steps': [
                {'instruction': 'Create and switch to a branch called feature.',
                 'hint': 'git switch -c feature'},
                {'instruction': 'Change app.py and commit it.',
                 'hint': 'git add -A then git commit -m "Extend app"'},
                {'instruction': 'Switch back to main.', 'hint': 'git switch main'},
                {'instruction': 'Merge feature into it.',
                 'hint': 'git merge feature. Watch for "Fast-forward"'},
            ],
            'free': 'Make a feature branch, commit a change to app.py on it, '
                    'and merge it back into main.',
            'verify': {'kind': 'git', 'expect': {
                'branch': 'main', 'branches': ['feature', 'main'],
                'min_commits': 2, 'subjects_contain': 'Extend', 'clean': True}},
            'fallback': 'self',
        },
        {
            'id': 'g-undo-soft',
            'title': 'Undo a commit without losing it',
            'goal': 'Move the branch pointer back and keep the work staged, '
                    'which is how you redo a commit properly.',
            'setup': {'kind': 'git', 'branch': 'main',
                      'commits': [
                          {'message': 'initial commit',
                           'tree': {'a.txt': 'one\n'}},
                          {'message': 'oops wrong message',
                           'tree': {'b.txt': 'two\n'}}]},
            'solution': {'shell': 'git reset -q --soft HEAD~1 && git -c '
                                  'user.email=t@t -c user.name=t commit -q '
                                  '-m "Add b with a proper message"'},
            'steps': [
                {'instruction': 'Undo the last commit, keeping its changes '
                                'staged.', 'hint': 'git reset --soft HEAD~1'},
                {'instruction': 'Commit again with a message you are not '
                                'embarrassed by.',
                 'hint': 'git commit -m "Add b with a proper message"'},
            ],
            'free': 'Replace the last commit with one that has a better '
                    'message, without losing the file it added.',
            'verify': {'kind': 'git', 'expect': {
                'commit_count': 2, 'subjects_lack': 'oops',
                'exists': ['b.txt'], 'clean': True}},
            'fallback': 'self',
        },
        {
            'id': 'g-reflog-rescue',
            'title': 'Rescue a commit you destroyed',
            'goal': 'Throw away a commit with reset --hard, then get it back, '
                    'so you trust the reflog.',
            'setup': {'kind': 'git', 'branch': 'main',
                      'commits': [
                          {'message': 'initial commit', 'tree': {'a.txt': 'one\n'}},
                          {'message': 'important work', 'tree': {'gold.txt': 'gold\n'}}]},
            'solution': {'shell': 'git reset -q --hard HEAD~1 && '
                                  'git reset -q --hard HEAD@{1}'},
            'steps': [
                {'instruction': 'Destroy the last commit with reset --hard.',
                 'hint': 'git reset --hard HEAD~1, and note gold.txt vanishes'},
                {'instruction': 'Confirm it is gone.',
                 'hint': 'ls, and git log --oneline'},
                {'instruction': 'Find it in the reflog and bring it back.',
                 'hint': 'git reflog, then git reset --hard HEAD@{1}'},
            ],
            'free': 'Reset --hard away the "important work" commit, then '
                    'recover it using the reflog.',
            'verify': {'kind': 'git', 'expect': {
                'commit_count': 2, 'subjects_contain': 'important',
                'exists': ['gold.txt']}},
            'fallback': 'self',
        },
        {
            'id': 'g-detached',
            'title': 'Escape a detached HEAD',
            'goal': 'Get into the state git warns you about, do work there, and '
                    'keep it.',
            'setup': {'kind': 'git', 'branch': 'main',
                      'commits': [
                          {'message': 'first', 'tree': {'a.txt': 'one\n'}},
                          {'message': 'second', 'tree': {'b.txt': 'two\n'}},
                          {'message': 'third', 'tree': {'c.txt': 'three\n'}}]},
            'solution': {'shell': 'git switch -q --detach HEAD~1 && '
                                  'echo x > rescued.txt && git add -A && '
                                  'git -c user.email=t@t -c user.name=t commit '
                                  '-q -m "Work done while detached" && '
                                  'git switch -q -c rescue'},
            'steps': [
                {'instruction': 'Detach HEAD onto the second commit.',
                 'hint': 'git switch --detach HEAD~1, and read the message'},
                {'instruction': 'Create and commit a file there.',
                 'hint': 'these commits have no branch pointing at them'},
                {'instruction': 'Give them a branch called rescue before you '
                                'lose them.', 'hint': 'git switch -c rescue'},
            ],
            'free': 'Detach onto an older commit, commit a file called '
                    'rescued.txt there, and give that work a branch named '
                    'rescue.',
            'verify': {'kind': 'git', 'expect': {
                'branch': 'rescue', 'detached': False,
                'exists': ['rescued.txt'],
                'subjects_contain': 'detached'}},
            'fallback': 'self',
        },

        {'id': 'g-resolve-conflict',
         'title': 'Resolve a merge conflict by hand',
         'goal': 'Two branches changed the same line. Merge them, read the '
                 'markers, and choose the final text yourself.',
         'setup': {'kind': 'git',
                   'branch': 'main',
                   'tree': {'config.txt': 'timeout = 10\n'},
                   'commits': [{'message': 'initial commit',
                                'tree': {'config.txt': 'timeout = 10\n'}}]},
         'solution': {'shell':
             'git switch -c feature -q && '
             'echo "timeout = 30" > config.txt && git add -A && '
             'git -c user.email=t@t -c user.name=t commit -q -m '
             '"feature: timeout 30" && '
             'git switch main -q && '
             'echo "timeout = 20" > config.txt && git add -A && '
             'git -c user.email=t@t -c user.name=t commit -q -m '
             '"main: timeout 20" && '
             # the merge conflicts on the single line; resolve to a chosen
             # value, then add and commit to complete the merge.
             'git -c user.email=t@t -c user.name=t merge feature -q '
             '--no-edit; '
             'echo "timeout = 25" > config.txt && git add config.txt && '
             'git -c user.email=t@t -c user.name=t commit -q --no-edit'},
         'steps': [{'instruction': 'Make a feature branch that sets the '
                                   'timeout to 30 and commit it.',
                    'hint': 'git switch -c feature; edit; git commit'},
                   {'instruction': 'Back on main, set the same line to 20 and '
                                   'commit. Now the two disagree.',
                    'hint': 'git switch main; edit config.txt; git commit'},
                   {'instruction': 'Merge feature. git stops with a conflict '
                                   'and writes both versions into the file '
                                   'between markers.',
                    'hint': 'git merge feature'},
                   {'instruction': 'Edit config.txt to the value you actually '
                                   'want, delete all three marker lines, then '
                                   'add and commit to finish the merge.',
                    'hint': 'set it to timeout = 25, then git add config.txt '
                            '&& git commit'}],
         'free': 'Create a conflict on config.txt between main and feature, '
                 'then resolve it to timeout = 25 and complete the merge so '
                 'the tree is clean.',
         'verify': {'kind': 'git',
                    'expect': {'branch': 'main',
                               'clean': True,
                               'file_contains': {'config.txt': 'timeout = 25'},
                               'file_lacks': {'config.txt': '<<<<<<<'}}},
         'fallback': 'self'},
        {'id': 'g-undo-safely',
         'title': 'Undo a commit that has already been shared',
         'goal': 'Reset rewrites history. Revert adds to it. Use the one '
                 'that is safe when someone else has your commits.',
         'setup': {'kind': 'git',
                   'branch': 'main',
                   'tree': {'config.txt': 'good\n'},
                   'commits': [{'message': 'initial commit',
                                'tree': {'config.txt': 'good\n'}},
                               {'message': 'Break the config',
                                'tree': {'config.txt': 'BROKEN\n'}}]},
         'solution': {'shell': 'git -c user.email=t@t -c user.name=t '
                               'revert --no-edit HEAD'},
         'steps': [{'instruction': 'Look at what the last commit did.',
                    'hint': 'git show HEAD, or git log -1 -p'},
                   {'instruction': 'Undo it by adding a new commit rather '
                                   'than removing the old one.',
                    'hint': 'git revert HEAD'},
                   {'instruction': 'The file should say good again, and '
                                   'the history should be longer, not '
                                   'shorter.',
                    'hint': 'git log --oneline to see both commits still '
                            'there'}],
         'free': 'Undo the breaking commit with a new commit, leaving '
                 'config.txt reading good.',
         'verify': {'kind': 'git',
                    'expect': {'min_commits': 3,
                               'clean': True,
                               'file_contains': {'config.txt': 'good'},
                               'subjects_contain': 'Revert'}},
         'fallback': 'self'},
        {'id': 'g-stash-switch',
         'title': 'Put work aside to deal with something else',
         'goal': 'You are mid-change and something urgent arrives. Park '
                 'the work, switch, and come back to it.',
         'setup': {'kind': 'git',
                   'branch': 'main',
                   'tree': {'notes.txt': 'original\n'},
                   'commits': [{'message': 'initial commit',
                                'tree': {'notes.txt': 'original\n'}}]},
         'solution': {'shell': 'echo "half done" > notes.txt && git stash '
                               '-q && git switch -c urgent -q && git '
                               'switch main -q && git stash pop -q'},
         'steps': [{'instruction': 'Change notes.txt to say "half done", '
                                   'but do not commit it.',
                    'hint': 'echo "half done" > notes.txt'},
                   {'instruction': 'Park that change so the tree is clean.',
                    'hint': 'git stash. git status should be clean '
                            'afterwards'},
                   {'instruction': 'Make a branch called urgent, then come '
                                   'back to main.',
                    'hint': 'git switch -c urgent, then git switch main'},
                   {'instruction': 'Bring your parked change back.',
                    'hint': 'git stash pop. A stash is a stack'}],
         'free': 'Stash a half-finished change, create a branch called '
                 'urgent, return to main and restore the change.',
         'verify': {'kind': 'git',
                    'expect': {'branch': 'main',
                               'branches': ['urgent'],
                               'clean': False,
                               'file_contains': {'notes.txt': 'half '
                                                              'done'}}},
         'fallback': 'self'},
        {'id': 'g-amend',
         'title': 'Fix the commit you just made',
         'goal': 'You forgot a file, or the message was wrong. Fix the '
                 'last commit rather than adding a "fix typo" one.',
         'setup': {'kind': 'git',
                   'branch': 'main',
                   'tree': {'a.txt': 'one\n'},
                   'commits': [{'message': 'initial commit',
                                'tree': {'a.txt': 'one\n'}},
                               {'message': 'Add teh feature',
                                'tree': {'b.txt': 'two\n'}}]},
         'solution': {'shell': 'git -c user.email=t@t -c user.name=t '
                               'commit -q --amend -m "Add the feature"'},
         'steps': [{'instruction': 'Look at the message on the last '
                                   'commit. It has a typo.',
                    'hint': 'git log -1'},
                   {'instruction': 'Rewrite that commit with a corrected '
                                   'message.',
                    'hint': 'git commit --amend -m "Add the feature"'},
                   {'instruction': 'The history should still be two '
                                   'commits long.',
                    'hint': 'amend replaces the commit; it does not add '
                            'one. Never amend something already pushed'}],
         'free': 'Correct the typo in the last commit message without '
                 'adding a new commit.',
         'verify': {'kind': 'git',
                    'expect': {'commit_count': 2,
                               'head_subject': 'Add the feature',
                               'subjects_lack': 'teh'}},
         'fallback': 'self'},
        {'id': 'g-ignore',
         'title': 'Stop tracking what should never have been tracked',
         'goal': 'A secret or a build artefact got committed. Ignore it '
                 'going forward and take it out of the index.',
         'setup': {'kind': 'git',
                   'branch': 'main',
                   'tree': {'app.py': 'print(1)\n',
                            'secrets.env': 'TOKEN=abc123\n'},
                   'commits': [{'message': 'initial commit',
                                'tree': {'app.py': 'print(1)\n',
                                         'secrets.env': 'TOKEN=abc123\n'}}]},
         'solution': {'shell': 'echo "secrets.env" > .gitignore && git rm '
                               '--cached -q secrets.env && git add -A && '
                               'git -c user.email=t@t -c user.name=t '
                               'commit -q -m "Ignore secrets.env"'},
         'steps': [{'instruction': 'Add secrets.env to a .gitignore file.',
                    'hint': 'echo secrets.env > .gitignore'},
                   {'instruction': 'Take it out of the index without '
                                   'deleting it from disk.',
                    'hint': 'git rm --cached secrets.env. Without --cached '
                            'the file goes too'},
                   {'instruction': 'Commit both the .gitignore and the '
                                   'removal.',
                    'hint': 'git add -A && git commit -m "Ignore '
                            'secrets.env". The secret is still in history: '
                            'rotating it is the real fix'}],
         'free': 'Ignore secrets.env, untrack it without deleting it, and '
                 'commit that.',
         'verify': {'kind': 'git',
                    'expect': {'min_commits': 2,
                               'clean': True,
                               'exists': ['secrets.env', '.gitignore'],
                               'file_contains': {'.gitignore': 'secrets.env'}}},
         'fallback': 'self'},
        {'id': 'g-tag-release',
         'title': 'Mark a commit as a release',
         'goal': 'A tag is a name for a commit that does not move. Put one '
                 'on the current state.',
         'setup': {'kind': 'git',
                   'branch': 'main',
                   'tree': {'VERSION': '1.0.0\n'},
                   'commits': [{'message': 'initial commit',
                                'tree': {'VERSION': '1.0.0\n'}}]},
         'solution': {'shell': 'git -c user.email=t@t -c user.name=t tag '
                               '-a v1.0.0 -m "Release 1.0.0"'},
         'steps': [{'instruction': 'Create an annotated tag called v1.0.0 '
                                   'on the current commit.',
                    'hint': 'git tag -a v1.0.0 -m "Release 1.0.0"'},
                   {'instruction': 'Check it is there.',
                    'hint': 'git tag, or git show v1.0.0'},
                   {'instruction': 'Note that a plain "git push" does not '
                                   'send tags.',
                    'hint': 'git push --tags, or git push origin v1.0.0'}],
         'free': 'Put an annotated tag v1.0.0 on the current commit.',
         'verify': {'kind': 'git', 'expect': {'tags': ['v1.0.0']}},
         'fallback': 'self'},

        {'id': 'g-rebase',
         'title': 'Replay your work on top of theirs',
         'goal': 'Rebase a feature branch onto an updated main, so the '
                 'history reads as though you started from the current '
                 'state.',
         'setup': {'kind': 'git',
                   'branch': 'main',
                   'tree': {'app.txt': 'base\n'},
                   'commits': [{'message': 'initial commit',
                                'tree': {'app.txt': 'base\n'}},
                               {'message': 'main moves on',
                                'tree': {'main.txt': 'from main\n'}}]},
         'solution': {'shell':
             'git -c user.email=t@t -c user.name=t checkout -q -b feature '
             'HEAD~1 && '
             'echo "feature work" > feature.txt && git add feature.txt && '
             'git -c user.email=t@t -c user.name=t commit -q -m '
             '"add the feature" && '
             'git -c user.email=t@t -c user.name=t rebase main'},
         'steps': [{'instruction': 'Branch off the commit before the tip, so '
                                   'you are deliberately behind main.',
                    'hint': 'git checkout -b feature HEAD~1'},
                   {'instruction': 'Make a commit on the feature branch.',
                    'hint': 'echo "feature work" > feature.txt; git add -A; '
                            'git commit -m "add the feature"'},
                   {'instruction': 'Rebase it onto main, so your commit sits '
                                   'on top of the newer work.',
                    'hint': 'git rebase main'},
                   {'instruction': 'Look at the log. Your commit has a new '
                                   'hash: rebasing rewrites, it does not '
                                   'move.'}],
         'free': 'From a feature branch that started behind main, rebase onto '
                 'main so your commit sits on top of the newer one.',
         'verify': {'kind': 'git', 'expect': {
             'branch': 'feature',
             'subjects_contain': ['add the feature', 'main moves on'],
             'min_commits': 3}},
         'fallback': 'self'},

        {'id': 'g-cherry-pick',
         'title': 'Take one commit and leave the rest',
         'goal': 'Cherry-pick a single fix from another branch without '
                 'merging everything else that is on it.',
         'setup': {'kind': 'git',
                   'branch': 'main',
                   'tree': {'app.txt': 'base\n'},
                   'commits': [{'message': 'initial commit',
                                'tree': {'app.txt': 'base\n'}}]},
         'solution': {'shell':
             'git -c user.email=t@t -c user.name=t checkout -q -b sidework && '
             'echo "unrelated" > unrelated.txt && git add -A && '
             'git -c user.email=t@t -c user.name=t commit -q -m '
             '"unrelated change" && '
             'echo "the fix" > fix.txt && git add -A && '
             'git -c user.email=t@t -c user.name=t commit -q -m '
             '"the important fix" && '
             'git -c user.email=t@t -c user.name=t checkout -q main && '
             'git -c user.email=t@t -c user.name=t cherry-pick sidework'},
         'steps': [{'instruction': 'Make a branch with two commits on it: one '
                                   'unrelated, then the fix you want.',
                    'hint': 'git checkout -b sidework, then two commits'},
                   {'instruction': 'Go back to main.',
                    'hint': 'git checkout main'},
                   {'instruction': 'Bring across only the fix commit, by '
                                   'name.',
                    'hint': 'git cherry-pick sidework, or the commit hash'},
                   {'instruction': 'Check that the unrelated change did not '
                                   'come with it.',
                    'hint': 'git log --oneline; ls'}],
         'free': 'With two commits on a side branch, bring only the second '
                 'one onto main and leave the first behind.',
         'verify': {'kind': 'git', 'expect': {
             'branch': 'main',
             'subjects_contain': ['the important fix'],
             'subjects_lack': ['unrelated change'],
             'exists': ['fix.txt'],
             'missing': ['unrelated.txt']}},
         'fallback': 'self'},

        {'id': 'g-bisect',
         'title': 'Let git find the commit that broke it',
         'goal': 'Bisect a short history to the exact commit that introduced '
                 'a bad value, using the run form so it is not guesswork.',
         'setup': {'kind': 'git',
                   'branch': 'main',
                   'tree': {'value.txt': 'good\n'},
                   'commits': [{'message': 'first good',
                                'tree': {'value.txt': 'good\n'}},
                               {'message': 'second good',
                                'tree': {'value.txt': 'good\n',
                                         'other.txt': 'x\n'}},
                               {'message': 'the bad one',
                                'tree': {'value.txt': 'bad\n'}},
                               {'message': 'later work',
                                'tree': {'value.txt': 'bad\n',
                                         'more.txt': 'y\n'}}]},
         'solution': {'shell':
             'git bisect start HEAD HEAD~3 > /dev/null 2>&1; '
             'git bisect run grep -q "^good$" value.txt > bisect.log 2>&1; '
             # git says "is the first 'bad' commit", with the quotes, so a
             # grep for the unquoted phrase matches nothing.
             'grep -m1 "is the first" bisect.log > culprit.txt 2>/dev/null; '
             'git bisect reset > /dev/null 2>&1; '
             'git log --oneline > history.txt 2>&1; true'},
         'steps': [{'instruction': 'Start a bisect with the current commit '
                                   'as bad and the oldest as good.',
                    'hint': 'git bisect start HEAD HEAD~3'},
                   {'instruction': 'Let git drive it with a test command that '
                                   'exits zero while things are still good.',
                    'hint': 'git bisect run grep -q "^good$" value.txt'},
                   {'instruction': 'Capture the line naming the first bad '
                                   'commit into culprit.txt. Note that git '
                                   'quotes the word bad in that message.',
                    'hint': 'grep -m1 "is the first" bisect.log'},
                   {'instruction': 'Reset the bisect so HEAD goes back where '
                                   'it belongs. Forgetting this leaves you '
                                   'detached.',
                    'hint': 'git bisect reset'}],
         'free': 'Bisect the history with a run command, capture the first '
                 'bad commit into culprit.txt, and reset afterwards.',
         'verify': {'kind': 'git', 'expect': {
             'branch': 'main',
             'detached': False,
             'file_contains': {'culprit.txt': 'is the first',
                               'history.txt': 'the bad one'}}},
         'fallback': 'self'},

        {'id': 'g-remote-track',
         'title': 'Wire up a remote and see what tracking means',
         'goal': 'Add a remote, push a branch, and read the ahead and behind '
                 'counts that every later status line depends on.',
         'setup': {'kind': 'git',
                   'branch': 'main',
                   'tree': {'app.txt': 'base\n'},
                   'commits': [{'message': 'initial commit',
                                'tree': {'app.txt': 'base\n'}}]},
         'solution': {'shell':
             # Inside the sandbox, deliberately. A bare repo one level up
             # would be outside the directory the trainer created, which D1
             # forbids and which the sandbox would never clean up.
             'git init -q --bare origin.git && '
             'git remote add origin ./origin.git && '
             'git push -q -u origin main 2>/dev/null && '
             'echo "local work" > local.txt && git add -A && '
             'git -c user.email=t@t -c user.name=t commit -q -m '
             '"work not yet pushed" && '
             'git remote -v > remotes.txt && '
             'git status -sb > status.txt && '
             'git rev-list --count origin/main..main > ahead.txt'},
         'steps': [{'instruction': 'Create a bare repository beside this one '
                                   'to act as the remote.',
                    'hint': 'git init --bare origin.git'},
                   {'instruction': 'Add it as origin and push main with -u so '
                                   'the branch tracks it.',
                    'hint': 'git remote add origin ./origin.git; git push -u '
                            'origin main'},
                   {'instruction': 'Make one more local commit that you do '
                                   'not push.'},
                   {'instruction': 'Save the remote list, the short status '
                                   'with branch info, and the count of '
                                   'commits you are ahead by.',
                    'hint': 'git status -sb; git rev-list --count '
                            'origin/main..main'}],
         'free': 'Set up a local bare remote, push main with tracking, make '
                 'one unpushed commit, and record remotes.txt, status.txt and '
                 'ahead.txt.',
         'verify': {'kind': 'git', 'expect': {
             'branch': 'main',
             'file_contains': {'remotes.txt': 'origin',
                               'status.txt': 'main',
                               'ahead.txt': '1'}}},
         'fallback': 'self'},
                  ],

    'quiz': [
        {'id': 'gq-snapshot', 'type': 'mcq',
         'prompt': 'What does a commit actually store?',
         'answer': 'A complete snapshot of the project, plus its parent.',
         'distractors': ['A diff against the previous commit.',
                         'Only the files you changed.',
                         'A patch file and a message.'],
         'teach': 'Diffs are computed on demand. This is why checking out an '
                  'old commit is fast and why history does not slow git down.'},

        {'id': 'gq-branch', 'type': 'mcq',
         'prompt': 'What is a branch?',
         'answer': 'A file containing one commit hash.',
         'distractors': ['A copy of the repository at a point in time.',
                         'A list of the commits that belong to it.',
                         'A directory under .git holding those commits.'],
         'teach': 'Forty-one bytes. That is why branching is instant and why '
                  'deleting a branch does not delete work.'},

        {'id': 'gq-diff', 'type': 'mcq',
         'prompt': 'You edit a file and `git add` it. Why does `git diff` now '
                   'show nothing?',
         'answer': 'It compares the index to the working tree, and they match.',
         'distractors': ['The change was lost by adding it.',
                         'diff only works on committed files.',
                         'You need to commit before diff works.'],
         'teach': 'Two gaps, two diffs. `git diff --staged` compares HEAD to '
                  'the index and will show it.'},

        {'id': 'gq-reset-revert', 'type': 'mcq',
         'prompt': 'You pushed a bad commit and others have pulled it. What do '
                   'you use?',
         'answer': 'revert, because it adds a new commit and changes nothing '
                   'that exists.',
         'distractors': ['reset --hard, then force push.',
                         'reset --soft and recommit.',
                         'rebase -i and drop the commit.'],
         'teach': 'Rewriting anything others hold gives them a divergent '
                  'history. revert is the only one that is safe there.'},

        {'id': 'gq-hard', 'type': 'mcq',
         'prompt': 'Which of these can actually lose work permanently?',
         'answer': 'reset --hard, on changes that were never committed.',
         'distractors': ['reset --soft on a pushed commit.',
                         'rebase -i squashing four commits.',
                         'Deleting a merged branch.'],
         'teach': 'Committed work stays in the reflog for weeks. There is no '
                  'reflog for work that was never committed.'},

        {'id': 'gq-fetch-pull', 'type': 'mcq',
         'prompt': 'What is the difference between fetch and pull?',
         'answer': 'pull is fetch plus a merge into your current branch.',
         'distractors': ['fetch is for branches, pull is for tags.',
                         'They are the same; pull is the newer spelling.',
                         'fetch downloads one branch, pull downloads all.'],
         'teach': 'fetch changes nothing you are working on, which is why '
                  'fetch-then-look is the safer habit.'},

        {'id': 'gq-origin-main', 'type': 'mcq',
         'prompt': 'What is `origin/main`?',
         'answer': 'Your local record of where the remote main was at your last '
                   'fetch.',
         'distractors': ['A live view of the remote branch.',
                         'A branch on the remote server.',
                         'An alias for your own main branch.'],
         'teach': 'It only updates when you fetch, which is why it can be '
                  'stale and why a push can be rejected unexpectedly.'},

        {'id': 'gq-rebase-rule', 'type': 'mcq',
         'prompt': 'When is rebasing a bad idea?',
         'answer': 'On commits you have pushed that others may already have.',
         'distractors': ['On any branch with more than ten commits.',
                         'Whenever there might be a conflict.',
                         'On a branch that has been merged once already.'],
         'teach': 'Rebase creates new commits with new hashes. Anyone holding '
                  'the old ones now has a divergent history.'},

        {'id': 'gq-detached', 'type': 'mcq',
         'prompt': 'What is actually risky about a detached HEAD?',
         'answer': 'Commits made there have no branch, so nothing refers to '
                   'them once you leave.',
         'distractors': ['You cannot commit at all while detached.',
                         'It corrupts the index until you switch back.',
                         'It silently rewrites the branch you came from.'],
         'teach': 'It is a normal state, not an error. `git switch -c name` '
                  'fixes it by giving the work a label.'},

        {'id': 'gq-force-lease', 'type': 'mcq',
         'prompt': 'Why prefer --force-with-lease over --force?',
         'answer': 'It refuses if someone else pushed since your last fetch.',
         'distractors': ['It is faster on large repositories.',
                         'It keeps a backup branch automatically.',
                         'It only rewrites commits you authored.'],
         'teach': 'Plain --force does not check, which is the difference '
                  'between careful and destructive.'},

        {'id': 'gq-merge-abort', 'type': 'mcq',
         'prompt': 'A merge stopped with conflicts. You want the branch as if '
                   'the merge never started. What do you run?',
         'answer': 'git merge --abort',
         'distractors': ['git reset --hard HEAD',
                         'git revert HEAD',
                         'git checkout -- .'],
         'teach': 'abort puts the branch back as if you never merged. reset '
                  '--hard throws away unrelated work sitting in the tree.'},
    ],
}
