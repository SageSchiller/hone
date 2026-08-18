"""pacman and apt: a database of files, not a downloader.

Two dialects of the same job. pacman is Arch, CachyOS, Manjaro. apt (and
dpkg under it) is Debian, Ubuntu, Mint, Kali. A package manager is a
database of installed files plus a solver that decides what else has to
come along. Search, info and query are three questions people collapse
into one. What owns this file is the daily one.

Sandbox-verified by querying the local database this machine already has,
or by writing the command line. Search and install hit a network or mutate
the box, so those stay honestly self-marked. D1: the trainer never runs
-S, install, -Syu or upgrade.

linux is the prerequisite: a path, a file, and a command that prints.
"""

MODULE = {
    'id': 'pkg',
    'title': 'pacman and apt',
    'group': 'Linux',
    'blurb': 'A database of files: search, query, what owns this, and the upgrade traps.',
    'context': 'You are at a shell on a Linux box, asking the local package database.',
    'needs': (),
    'prereqs': ['linux'],
    'adapter': 'sandbox',
    'estimate': '3-4 hours',
    'order': 11,

    'lessons': [
        {
            'id': 'pk-what',
            'title': 'A database of files, not a downloader',
            'next': 'pk-search',
            'concept': (
                'A package manager is a database of files plus a solver. That '
                'is why `pacman -Qo /usr/bin/true` and `dpkg -S /usr/bin/true` '
                'are more useful than `install` on most days: they answer '
                'what put this file here, and what else came with it.\n\n'
                'This module is two dialects of that job. **pacman** is Arch, '
                'CachyOS, Manjaro. **apt**, with **dpkg** underneath, is '
                'Debian, Ubuntu, Mint, Kali. Learn the one on this box and '
                'keep the other as a translation. dnf, apk and brew are the '
                'same model with different flags, and they are not a third '
                'module.\n\n'
                'Three questions get collapsed into one. **Search** asks the '
                'repo index what exists. **Info** describes one package. '
                '**Query** asks the local database what is already installed, '
                'which files it owns, and which package owns a path. Install '
                'is the easy half. Query is the half that earns the lesson.\n\n'
                'The solver is why a one-word install pulls twelve other '
                'packages. Those are dependencies. Removing the one word '
                'does not always remove the twelve, which is how a disk '
                'fills with leftovers. The next lessons name the commands. '
                'This one is the picture they all sit on.\n\n'
                'A first session treats the tool as curl with extra flags. '
                'Then a file in `/usr/bin` has no owner, or a remove leaves '
                'two hundred megabytes behind, and there is no model for '
                'either. The database is the thing to learn. The download '
                'is the thing it already does well.\n\n'
                'The next lesson is search and info: what exists, and what '
                'one package actually is, before anyone installs it.'
            ),
            'examples': [
                {
                    'label': 'The same job, two dialects',
                    'code': ('# what owns this file\n'
                             'pacman -Qo /usr/bin/true\n'
                             'dpkg -S  /usr/bin/true\n'
                             '\n'
                             '# what is installed\n'
                             'pacman -Q bash\n'
                             'dpkg -l  bash'),
                    'note': 'Query is local. It does not phone out. That is '
                            'the half this module can check.',
                },
                {
                    'label': 'What it is not',
                    'code': ('a downloader     curl a tarball into /usr\n'
                             'a package manager  a database, then a solver\n'
                             '\n'
                             'pip, npm, cargo   language ecosystems\n'
                             '                   a different course'),
                    'note': 'OS packages own system files. Language tools '
                            'own a project. Mixing them is how /usr fills '
                            'with things apt cannot see.',
                },
            ],
            'misconceptions': [
                'install is not the skill. Query is. A box you did not build '
                'is almost always a query problem first.',
                'pacman and apt are not two products that happen to install '
                'software. They are two CLIs on the same model. Translate, '
                'do not relearn.',
            ],
            'try_it': [
                'On this box, run whichever of pacman -Q bash or dpkg -l bash '
                'exists, and read the line. That is the local database.',
            ],
        },
        {
            'id': 'pk-search',
            'title': 'Search and info: what exists',
            'next': 'pk-query',
            'concept': (
                'Search is how you ask the repo index whether a name exists, '
                'and info is how you read one package before you touch it. '
                'That is why they come before install: the wrong name is a '
                'wasted download, and the right name is often not the '
                'command you type.\n\n'
                '`pacman -Ss bash` searches descriptions. `pacman -Si bash` '
                'prints one package: version, repo, depends, size. `apt '
                'search bash` and `apt show bash` are the same pair. `apt '
                'search` wants a short query; a long sentence is how you get '
                'a thousand hits and miss the one you wanted.\n\n'
                'The name in the database is not always the binary. On this '
                'roster, `dig` is `bind` or `dnsutils`, `nvim` is `neovim`, '
                '`nc` is `openbsd-netcat`. Search, then info, then install. '
                'Guessing the package from the command is the usual miss.\n\n'
                'Search reads an index that has to be current. On Arch that '
                'index is what `-Sy` refreshes, and refreshing it without '
                'upgrading is the trap in a later lesson. On Debian, `apt '
                'update` fetches the lists; `apt search` against a stale '
                'list is a confident lie. Neither search nor info installs '
                'anything.\n\n'
                'The failure is installing the first hit. `apt search python` '
                'is a novel. The package that provides the `python3` you '
                'meant is one line in that novel, and info is how you '
                'confirm depends and size before the solver starts. A short '
                'query, then one info, then a decision.\n\n'
                'The next lesson is query: the local database, which does '
                'not need the network at all.'
            ),
            'examples': [
                {
                    'label': 'Search, then describe',
                    'code': ('pacman -Ss nvim\n'
                             'pacman -Si neovim\n'
                             '\n'
                             'apt search nvim\n'
                             'apt show neovim'),
                    'note': 'The hit is neovim, not nvim. Info is where you '
                            'confirm that before you type install.',
                },
                {
                    'label': 'What info is for',
                    'code': ('Name / Package\n'
                             'Version\n'
                             'Depends / Depends On\n'
                             'Installed Size\n'
                             'Description'),
                    'note': 'Depends is the solver preview. A tiny tool that '
                            'pulls a desktop stack is a fact you want before '
                            'the download starts.',
                },
            ],
            'misconceptions': [
                'search is not query. Search asks the index what could be '
                'installed. Query asks what already is.',
                'The first search hit is not always the package. Read the '
                'name column. The command and the package often disagree.',
            ],
            'try_it': [
                'Search for nvim in this box\'s dialect, then show the '
                'package that actually provides it. Do not install it.',
            ],
        },
        {
            'id': 'pk-query',
            'title': 'Query: what is installed, and what owns this file',
            'next': 'pk-install',
            'concept': (
                'Query is how you ask the local database. That is why it is '
                'the daily skill: a file appeared, a command is missing, a '
                'disk is full of packages you do not remember installing. '
                'None of those needs the network.\n\n'
                '`pacman -Q` lists installed packages. `pacman -Q bash` is '
                'one. `pacman -Qi bash` is the info view of an installed '
                'copy. `pacman -Ql bash` lists the files it owns. `pacman '
                '-Qo /usr/bin/true` is the inverse: which package owns this '
                'path. `dpkg -l`, `dpkg -s`, `dpkg -L` and `dpkg -S` are '
                'the same four questions.\n\n'
                'What owns this file is the DFIR and admin question. A '
                'binary in `/usr/bin` you did not put there is almost always '
                'a package. A binary in `/usr/local` or a home directory is '
                'often not, and `-Qo` / `-S` saying "no package" is the '
                'finding, not a failure.\n\n'
                '`pacman -Qe` is what you asked for, as opposed to what the '
                'solver pulled in. `pacman -Qdt` is orphans: installed as '
                'deps, no longer required. `apt list --installed` and `apt '
                'autoremove --dry-run` are the Debian pair. That is how a '
                'disk fills, and how you read it back.\n\n'
                'A missing command is often a missing package, and query is '
                'how you tell those apart from a PATH mistake. `which nvim` '
                'says not found. `pacman -Q neovim` or `dpkg -l neovim` says '
                'whether the package was ever installed. Two different '
                'fixes. Mixing them up is an afternoon.\n\n'
                'A path that is *not* installed is a different database. '
                '`pacman -F /usr/bin/nvim` (after `pacman -Fy` once) and '
                '`apt-file search nvim` ask the repo index which package '
                '*would* own that file. `dpkg -S` and `pacman -Qo` cannot '
                'see it until it is on the disk.\n\n'
                'The next lesson is install, remove and upgrade: the half '
                'that changes the box, which this trainer will not run.'
            ),
            'examples': [
                {
                    'label': 'Four questions, two dialects',
                    'code': ('# installed?\n'
                             'pacman -Q bash          dpkg -l bash\n'
                             '# describe installed\n'
                             'pacman -Qi bash         dpkg -s bash\n'
                             '# files in the package\n'
                             'pacman -Ql bash         dpkg -L bash\n'
                             '# who owns this path\n'
                             'pacman -Qo /usr/bin/true\n'
                             'dpkg -S  /usr/bin/true'),
                    'note': 'Memorise the four. Search was the index. These '
                            'four are the machine in front of you.',
                },
                {
                    'label': 'No package is an answer',
                    'code': ('pacman -Qo ~/.local/bin/foo\n'
                             '  error: No package owns ...\n'
                             '\n'
                             'dpkg -S /usr/local/bin/foo\n'
                             '  dpkg-query: no path found'),
                    'note': 'A path the database does not know is how you '
                            'spot a hand-dropped binary, a pip install, or '
                            'a cargo install into home.',
                },
            ],
            'misconceptions': [
                'dpkg -S is not apt-file. dpkg only knows installed files. '
                'A file that is in the repos but not installed is invisible '
                'to it.',
                'pacman -Q with no name is the whole list, not an error. '
                'Pipe it. Do not scroll it.',
            ],
            'try_it': [
                'Ask this box what owns /usr/bin/true, then list a few files '
                'from that package. Confirm true is among them.',
            ],
        },
        {
            'id': 'pk-install',
            'title': 'Install, remove, upgrade: you run these',
            'next': 'pk-repos',
            'concept': (
                'Install is how a name on the index becomes files on the '
                'disk. That is why it is the command everyone knows, and why '
                'it is the one this trainer will not run: it needs the '
                'network and it mutates the real box. Learn the line, then '
                'run it yourself.\n\n'
                '`sudo pacman -S neovim` installs. `sudo pacman -R neovim` '
                'removes the package and leaves its deps. `sudo pacman -Rns '
                'neovim` removes the package, unneeded deps, and config '
                'files the package marked as such. `sudo apt install '
                'neovim`, `sudo apt remove neovim`, `sudo apt autoremove` '
                'are the Debian shape. `apt purge` drops config too.\n\n'
                'Upgrade is a different verb. `sudo pacman -Syu` syncs the '
                'index and upgrades everything in one action. That pairing '
                'is load-bearing; the next lesson but one says why. On '
                'Debian the pair is `sudo apt update` then `sudo apt '
                'upgrade`. `full-upgrade` may remove packages the solver '
                'now considers in the way. Read the list before you say '
                'yes.\n\n'
                '`apt` is the interactive command. `apt-get` is the one '
                'scripts should call, because its output is stable. This '
                'module teaches `apt` for a human at a prompt.\n\n'
                'The last screen before yes is the transaction. Both tools '
                'print what they will add, remove and upgrade. A one-word '
                'install that also removes a kernel or pulls a desktop is '
                'still waiting for you to type yes. Read that list. The '
                'solver is not a mind reader.\n\n'
                'A file already on disk is `sudo pacman -U pkg.pkg.tar.zst` '
                'or `sudo apt install ./pkg.deb`. The cache of old downloads '
                'is `sudo pacman -Sc` or `sudo apt clean`, which is how a '
                'full `/var` often gets its space back.\n\n'
                'The next lesson is where the bits come from: official '
                'repos, and the extras people bolt on.'
            ),
            'examples': [
                {
                    'label': 'The three verbs',
                    'code': ('# install\n'
                             'sudo pacman -S neovim\n'
                             'sudo apt install neovim\n'
                             '\n'
                             '# remove, and leftovers\n'
                             'sudo pacman -Rns neovim\n'
                             'sudo apt remove neovim && sudo apt autoremove\n'
                             '\n'
                             '# upgrade the world\n'
                             'sudo pacman -Syu\n'
                             'sudo apt update && sudo apt upgrade'),
                    'note': 'Read the transaction. A one-word install that '
                            'pulls a desktop is a fact you want before yes.',
                },
                {
                    'label': 'What this trainer will not do',
                    'code': ('hone will query the local database\n'
                             'hone will not install, remove, or upgrade\n'
                             '\n'
                             'that is your box, and D1'),
                    'note': 'A challenge that asks you to install something '
                            'is self-marked on purpose. The check is you, '
                            'not the trainer.',
                },
            ],
            'misconceptions': [
                'remove is not uninstall-the-deps. On both dialects you have '
                'to ask, or leftovers stay until the disk complains.',
                'upgrade is not install of one package. It is the whole '
                'world against a new index. Treat it as one decision.',
            ],
            'try_it': [
                'Type the upgrade line for this box, then Ctrl-C out of the '
                'confirmation if it offers one. Read what it would do. Do '
                'not confirm it for this lesson.',
            ],
        },
        {
            'id': 'pk-repos',
            'title': 'Where the bits come from',
            'next': 'pk-traps',
            'concept': (
                'A repo is a signed list of packages plus the files they '
                'point at. That is why an official install is a different '
                'act from curling a script: the index has a name, a version, '
                'and a signature you can check. Learn where your box looks, '
                'and you stop treating every install as the same risk.\n\n'
                'On Arch the official repos are named in `/etc/pacman.conf`: '
                'core, extra, and whatever the flavour adds (CachyOS has '
                'its own). Anything else is **AUR**, a community build '
                'recipe, not a binary repo. yay and paru are AUR helpers. '
                'They are not pacman. A PKGBUILD is a shell script you can '
                'read; skip that step and you are running a stranger\'s '
                'script as root.\n\n'
                'On Debian the official lists live under '
                '`/etc/apt/sources.list` and `sources.list.d/`. A **PPA** '
                'is an extra Ubuntu list someone published. `apt` will '
                'install from it as if it were official. It is not. Third '
                'party repos are how a box picks up a newer Firefox and, '
                'sometimes, a key that now signs whatever they like.\n\n'
                'hone\'s own install line already knows this: some tools '
                'print an AUR or pipx route instead of `pacman -S`, because '
                'a command that fails is worse than a command that says '
                'so. That honesty is the same skill as reading the repo '
                'name in `pacman -Si` or `apt show`.\n\n'
                'A third-party repo that also ships `libc` or `bash` is how '
                'a box stops being upgradeable. Prefer a repo that only '
                'adds the one thing you came for. The official lists are '
                'boring on purpose.\n\n'
                'The next lesson is the traps: partial upgrades, holds, '
                'and why -Syu is one action.'
            ),
            'examples': [
                {
                    'label': 'Read the source before the install',
                    'code': ('pacman -Si neovim | grep -E "Repository|Name"\n'
                             'apt policy neovim\n'
                             '\n'
                             'Repository    : extra\n'
                             '  vs\n'
                             'Repository    : a third-party list'),
                    'note': 'policy and -Si name the source. A surprise '
                            'repo is the finding.',
                },
                {
                    'label': 'Official against bolted on',
                    'code': ('Arch     core extra, then AUR as a recipe\n'
                             'Debian   sources.list, then a PPA\n'
                             '\n'
                             'AUR is a build. A PPA is a repo.\n'
                             'Neither is the official index.'),
                    'note': 'AUR compiles on your box. A PPA ships binaries. '
                            'Different risk, same rule: know which one you '
                            'just enabled.',
                },
            ],
            'misconceptions': [
                'AUR is not an official Arch repo. It is a collection of '
                'build scripts. Reading the PKGBUILD is the review.',
                'A PPA is not "Ubuntu, so it is safe". It is an extra '
                'signer. apt will not warn you twice.',
            ],
            'try_it': [
                'Open pacman.conf or sources.list and list the repos this '
                'box trusts. Then info one installed package and name the '
                'repo it came from.',
            ],
        },
        {
            'id': 'pk-traps',
            'title': 'Partial upgrades, holds, and leftovers',
            'next': 'pk-workflow',
            'concept': (
                'These traps are why the model is worth an afternoon. A '
                'package manager that only installed things would be a '
                'cheat sheet. One that can leave the box half-upgraded, or '
                'refuse to touch a package you forgot you held, is a tool.\n\n'
                '**Partial upgrades on Arch.** `pacman -Sy` refreshes the '
                'index. `pacman -S pkg` then installs against that new '
                'index while the rest of the system is still old. Libraries '
                'move, the one new package links against them, and the next '
                'boot is a surprise. `-Syu` is one action on purpose: sync '
                'and upgrade together. Do not split them. `pacman -Sy pkg` '
                'is the same trap written shorter.\n\n'
                '**Holds on Debian.** `apt-mark hold pkg` pins a version. '
                'The next `upgrade` will skip it and not always shout. '
                '`apt-mark showhold` is the inventory. On Arch the equivalent '
                'is `IgnorePkg` in `pacman.conf`, which is easier to forget '
                'because it is a file, not a command you just ran.\n\n'
                '**Leftovers.** The solver installs deps. Remove the thing '
                'you asked for and the deps can stay. `pacman -Qdt` lists '
                'orphans. `pacman -Rns` on the original package, or a later '
                'pass over the orphan list, is the cleanup. `apt autoremove` '
                'is the Debian one. A full disk is often this, not a file '
                'you wrote.\n\n'
                'The other silent skip is a hold you set six months ago. An '
                'upgrade that "worked" and left one library old is how a '
                'tool starts crashing after a neighbour moved. `showhold` '
                'and `IgnorePkg` are the first things to read when an '
                'upgrade did not upgrade the thing you came for.\n\n'
                'After `-Syu`, a `.pacnew` next to a config you had edited '
                'is the new default, left beside your version on purpose. '
                'Debian asks through `ucf` or writes `.dpkg-dist`. The '
                'upgrade did not overwrite you. Merge the file, or the next '
                'release\'s default never arrives.\n\n'
                'The next lesson is the habit: which command answers which '
                'question, in the order you actually ask them.'
            ),
            'examples': [
                {
                    'label': 'The Arch line that is safe',
                    'code': ('sudo pacman -Syu           one action\n'
                             'sudo pacman -Syu neovim    upgrade world,\n'
                             '                           then this package\n'
                             '\n'
                             'sudo pacman -Sy neovim     the trap'),
                    'note': '-Syu can take a name at the end. That still '
                            'upgrades the world first. That is the point.',
                },
                {
                    'label': 'Holds and leftovers',
                    'code': ('apt-mark showhold\n'
                             'apt-mark hold linux-image-amd64\n'
                             '\n'
                             'pacman -Qdt                orphans\n'
                             'sudo apt autoremove --dry-run'),
                    'note': 'dry-run first. An autoremove list that includes '
                            'something you still want is a dep you should '
                            'have marked explicit.',
                },
            ],
            'misconceptions': [
                '-Sy then -S is not "faster than -Syu". It is a partial '
                'upgrade. The speed is the risk.',
                'A hold is not a backup. It is a pin. The package stays '
                'old while everything around it moves.',
            ],
            'try_it': [
                'On Arch, read the -Syu man sentence and confirm -Sy is '
                'called out. On Debian, run apt-mark showhold. On either, '
                'list orphans or dry-run autoremove.',
            ],
        },
        {
            'id': 'pk-workflow',
            'title': 'Which command answers which question',
            'concept': (
                'This lesson is the habit: which command answers which '
                'question, in the order you actually ask them. The payoff '
                'is not more flags. It is not typing install first and '
                'debugging the wreckage.\n\n'
                '**What is it called.** Search, then info. Confirm the '
                'package name is not the command name. Confirm the repo is '
                'one you meant to trust.\n\n'
                '**Is it already here.** Query. `-Q` / `dpkg -l`. If it is '
                'installed, info on the installed copy tells you the '
                'version and why it is here (explicit or as a dep).\n\n'
                '**What owns this file.** `-Qo` / `dpkg -S`. No package is '
                'an answer. That is how you tell a system binary from a '
                'hand-dropped one.\n\n'
                '**Then act.** Install, remove, or upgrade, yourself, after '
                'you have the name. On Arch, `-Syu` as one action. On '
                'Debian, update then upgrade, and check holds first.\n\n'
                'Translate, do not relearn. A Debian day after a year of '
                'Arch is the four query questions and the one upgrade '
                'line, not a new career. dnf, apk and brew wait until a '
                'box that only has those is the box in front of you.\n\n'
                'A foreign box is the test. Sit down, find which dialect '
                'answers `command -v pacman` or `command -v apt`, and start '
                'at query, not at install. The files are already there. The '
                'database knows their names. Ask it.\n\n'
                'That is enough to live on a Linux box without treating '
                'the package manager as a downloader with extra flags.'
            ),
            'examples': [
                {
                    'label': 'The five questions, in order',
                    'code': ('search / info     what is it called, which repo\n'
                             'query installed   is it already here\n'
                             'query owner       what put this file here\n'
                             'then install      only after the name is right\n'
                             'upgrade           the whole world, as one act'),
                    'note': 'Skip a step and the next one is harder, not '
                            'faster. The wrong name is an install you then '
                            'have to undo.',
                },
                {
                    'label': 'A pocket card',
                    'code': ('              pacman           apt / dpkg\n'
                             'search        -Ss              apt search\n'
                             'info          -Si              apt show\n'
                             'installed     -Q               dpkg -l\n'
                             'files         -Ql              dpkg -L\n'
                             'owns path     -Qo              dpkg -S\n'
                             'install       -S               apt install\n'
                             'upgrade       -Syu             update && upgrade'),
                    'note': 'The left column is the question. The other two '
                            'are translations. That is the whole module.',
                },
            ],
            'misconceptions': [
                'install first is not faster. Without a name and a repo you '
                'are guessing, and the solver will help you guess wrong.',
                'This module does not replace reading the transaction. The '
                'list of what will be installed is still the last check.',
            ],
            'try_it': [
                'Pick any binary in /usr/bin, run the owner query, then '
                'info that package. Write down repo, version, and whether '
                'you asked for it or the solver did.',
            ],
        },
    ],

    'drills': [
        {'id': 'pkd-ss', 'type': 'command',
         'answer': 'pacman -Ss nvim',
         'prompt': 'Search the Arch repos for nvim.',
         'teach': '-Ss is search. The package you want may not be called nvim.'},
        {'id': 'pkd-si', 'type': 'command',
         'answer': 'pacman -Si neovim',
         'prompt': 'Describe the neovim package from the Arch index.',
         'teach': '-Si is info against the index, not the installed copy.'},
        {'id': 'pkd-q', 'type': 'command',
         'answer': 'pacman -Q bash',
         'prompt': 'Ask pacman whether bash is installed, and its version.',
         'teach': '-Q is the local database. No network.'},
        {'id': 'pkd-qo', 'type': 'command',
         'answer': 'pacman -Qo /usr/bin/true',
         'prompt': 'Ask pacman which package owns /usr/bin/true.',
         'teach': 'The inverse of -Ql. No package is a finding.'},
        {'id': 'pkd-ql', 'type': 'command',
         'answer': 'pacman -Ql bash',
         'prompt': 'List the files the bash package owns.',
         'teach': '-Ql is the file list. -Qi is the description.'},
        {'id': 'pkd-qdt', 'type': 'command',
         'answer': 'pacman -Qdt',
         'prompt': 'List orphaned packages: deps nothing still needs.',
         'teach': 'Leftovers from a remove that did not take the deps.'},
        {'id': 'pkd-syu', 'type': 'command',
         'answer': 'sudo pacman -Syu',
         'prompt': 'Sync the Arch index and upgrade everything, as one action.',
         'teach': 'Split this into -Sy then -S and you have a partial upgrade.'},
        {'id': 'pkd-rns', 'type': 'command',
         'answer': 'sudo pacman -Rns neovim',
         'prompt': 'Remove neovim, its unneeded deps, and its config files.',
         'teach': '-R is the package only. -Rns is the cleanup most people mean.'},
        {'id': 'pkd-apt-search', 'type': 'command',
         'answer': 'apt search nvim',
         'prompt': 'Search Debian packages for nvim.',
         'teach': 'apt search is -Ss. Then apt show, not install, to confirm.'},
        {'id': 'pkd-apt-show', 'type': 'command',
         'answer': 'apt show neovim',
         'prompt': 'Describe the neovim package on Debian.',
         'teach': 'apt show is info. dpkg -s is the same for an installed copy.'},
        {'id': 'pkd-dpkg-s', 'type': 'command',
         'answer': 'dpkg -S /usr/bin/true',
         'prompt': 'Ask dpkg which installed package owns /usr/bin/true.',
         'teach': 'dpkg -S only sees installed files. apt-file sees the index.'},
        {'id': 'pkd-dpkg-l', 'type': 'command',
         'answer': 'dpkg -L bash',
         'prompt': 'List the files the installed bash package owns on Debian.',
         'teach': 'dpkg -L is pacman -Ql. dpkg -l is the installed list.'},
        {'id': 'pkd-apt-up', 'type': 'command',
         'answer': 'sudo apt update && sudo apt upgrade',
         'prompt': 'Refresh Debian lists, then upgrade installed packages.',
         'teach': 'update is the index. upgrade is the packages. Two steps, '
                  'one decision.'},
        {'id': 'pkd-qe', 'type': 'command',
         'answer': 'pacman -Qe',
         'prompt': 'List packages you asked for, not the solver leftovers.',
         'teach': '-Qe is explicit. -Qdt is the orphans the solver left.'},
        {'id': 'pkd-f', 'type': 'command',
         'answer': 'pacman -F /usr/bin/nvim',
         'prompt': 'Ask the Arch files db which package would own /usr/bin/nvim.',
         'teach': '-F searches the index. -Qo only sees installed files. -Fy first.'},
        {'id': 'pkd-sc', 'type': 'command',
         'answer': 'sudo pacman -Sc',
         'prompt': 'Clear uninstalled package files from the Arch cache.',
         'teach': '-Sc is the cache. A full /var is often this, not a file you wrote.'},
        {'id': 'pkd-hold', 'type': 'command',
         'answer': 'apt-mark showhold',
         'prompt': 'List packages Debian will refuse to upgrade.',
         'teach': 'A hold is silent during upgrade. Show it before you wonder '
                  'why a package never moves.'},
    ],

    'challenges': [
        {
            'id': 'pkc-owner',
            'title': 'What owns /usr/bin/true',
            'goal': 'The daily query: a path in, a package name out. Run it '
                    'on this machine, in whichever dialect the box has.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {}},
            'solution': {
                'shell': (
                    'if command -v pacman >/dev/null; then '
                    'pacman -Qo /usr/bin/true > owner.txt; '
                    'elif command -v dpkg >/dev/null; then '
                    'dpkg -S /usr/bin/true > owner.txt; '
                    'else echo "no package manager" > owner.txt; fi'
                ),
            },
            'steps': [
                {'instruction': 'Ask the local database which package owns '
                                '/usr/bin/true. Save the line as owner.txt.',
                 'hint': 'pacman -Qo /usr/bin/true  or  dpkg -S /usr/bin/true'},
            ],
            'free': 'Write owner.txt naming the package that owns '
                    '/usr/bin/true.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_contains': {'owner.txt': ['coreutils']},
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'pkc-info',
            'title': 'Describe an installed package',
            'goal': 'Info on something already here. Version is the field '
                    'both dialects print under a stable word.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {}},
            'solution': {
                'shell': (
                    'if command -v pacman >/dev/null; then '
                    'pacman -Qi bash > info.txt; '
                    'elif command -v dpkg >/dev/null; then '
                    'dpkg -s bash > info.txt; '
                    'else echo "Version: unknown" > info.txt; fi'
                ),
            },
            'steps': [
                {'instruction': 'Describe the installed bash package and save '
                                'the output as info.txt.',
                 'hint': 'pacman -Qi bash  or  dpkg -s bash'},
            ],
            'free': 'Write info.txt containing the installed bash description.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_contains': {'info.txt': ['Version']},
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'pkc-card',
            'title': 'A pocket card for both dialects',
            'goal': 'The translation is the skill. Write the owner query in '
                    'both dialects, so a Debian day after an Arch year is '
                    'one line, not a search.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {}},
            'solution': {
                'shell': (
                    "printf '%s\\n' "
                    "'pacman -Qo /usr/bin/true' "
                    "'dpkg -S /usr/bin/true' "
                    '> both.txt'
                ),
            },
            'steps': [
                {'instruction': 'Write both.txt with two lines: the pacman '
                                'owner query and the dpkg owner query for '
                                '/usr/bin/true.',
                 'hint': 'pacman -Qo ... and dpkg -S ...'},
            ],
            'free': 'Write both.txt with the owner query in both dialects.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_contains': {
                        'both.txt': ['pacman -Qo', 'dpkg -S'],
                    },
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'pkc-live',
            'title': 'Install something you actually want',
            'goal': 'Query is checked. Install is yours. The trainer will '
                    'not mutate this box.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'Search for a tool you actually want, then '
                                'info it, and confirm the package name and '
                                'the repo.'},
                {'instruction': 'Install it yourself. Read the transaction '
                                'before you say yes.'},
                {'instruction': 'Query the owner of one file it dropped, and '
                                'confirm the package name matches.'},
                {'instruction': 'If you do not want it after all, remove it '
                                'the way this module taught, deps included.'},
            ],
            'free': 'On this machine: search, info, install, then query a '
                    'file it owns. Remove it if you do not want it.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
    ],

    'quiz': [
        {
            'id': 'pkq-model',
            'type': 'mcq',
            'prompt': 'What is a package manager, besides a way to download software?',
            'answer': 'A database of installed files plus a solver for dependencies.',
            'distractors': [
                'A wrapper around curl that puts files in /usr.',
                'A compiler that turns source into a system binary.',
                'A language-specific installer like pip or npm.',
            ],
            'teach': 'Query the database. The download is the easy half.',
        },
        {
            'id': 'pkq-owner',
            'type': 'mcq',
            'prompt': 'Which pair answers "what package owns this file"?',
            'answer': 'pacman -Qo and dpkg -S',
            'distractors': [
                'pacman -Ss and apt search',
                'pacman -S and apt install',
                'pacman -Qdt and apt autoremove',
            ],
            'teach': 'Owner is the inverse of the file list. Search will not see an installed path.',
        },
        {
            'id': 'pkq-partial',
            'type': 'mcq',
            'prompt': 'Why is pacman -Sy pkg a trap?',
            'answer': 'It refreshes the index then installs one package against it, leaving the rest of the system old.',
            'distractors': [
                'It deletes orphans without asking.',
                'It skips the signature check on that one package.',
                'It holds the package so later upgrades ignore it.',
            ],
            'teach': '-Syu is one action on purpose. Split it and you have a partial upgrade.',
        },
        {
            'id': 'pkq-search',
            'type': 'mcq',
            'prompt': 'Search and query ask different databases. Which is which?',
            'answer': 'Search asks the repo index; query asks what is already installed.',
            'distractors': [
                'They are two names for the same local list.',
                'Search asks installed packages; query asks the index.',
                'Search is Debian; query is Arch.',
            ],
            'teach': 'A package can be searchable and not installed. Query will not see it.',
        },
        {
            'id': 'pkq-aur',
            'type': 'mcq',
            'prompt': 'What is the AUR, relative to pacman?',
            'answer': 'A collection of community build scripts, not an official binary repo.',
            'distractors': [
                'The fourth official Arch repo, after core and extra.',
                'A Debian PPA that Arch machines can add.',
                'The cache directory pacman uses for downloaded packages.',
            ],
            'teach': 'A PKGBUILD is a script. Reading it is the review. yay is not pacman.',
        },
        {
            'id': 'pkq-dpkg',
            'type': 'mcq',
            'prompt': 'dpkg -S cannot find a file that apt search shows. Why?',
            'answer': 'dpkg only knows installed files. The package is in the index but not on the disk.',
            'distractors': [
                'apt search is always wrong about paths.',
                'dpkg -S needs root and failed silently.',
                'The file is owned by pacman on Debian too.',
            ],
            'teach': 'apt-file searches the index for paths. dpkg -S searches the installed set.',
        },
    ],
}
