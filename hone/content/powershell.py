"""PowerShell: the object pipeline, and the Windows evidence it reaches.

**The last module in the roster**, and the one whose checking splits cleanly
in two. PowerShell runs on Linux, so the object pipeline, which is the half
worth learning, is graded by really running what you type: `Sort-Object`,
`Where-Object`, `Group-Object`, `Measure-Object`, `Select-Object`, calculated
properties and `-match` against `-like` all behave identically here and on
Windows.

The Windows half is not faked. `Get-WinEvent`, `Get-Service`, WMI and the
registry do not exist on this platform and no stand-in is shipped for them,
because the lesson of that content is that filtering belongs at the source
where the source has millions of records, and a fifty-row imitation teaches
the opposite by making both approaches feel instant. That content stays
readable and its challenge stays self-marked and says why.

**The whole module is one reframe.** Every shell you have learned so far pipes
**text**, so every tool has to parse the previous tool's output and every
pipeline is a small exercise in `cut` and `awk`. PowerShell pipes **objects**
with typed properties, so filtering and sorting and selecting happen on named
fields and nothing is ever parsed. Once that lands, the cmdlets are
predictable; before it lands, they look like a verbose way to do `grep`.

The DFIR payoff is `Get-WinEvent`. Windows event logs are the evidence in most
Windows investigations, and reaching them properly means XPath or a filter
hashtable rather than pulling everything and filtering afterwards, which on a
real machine is the difference between seconds and half an hour.
"""

MODULE = {
    'id': 'powershell',
    'title': 'PowerShell',
    'group': 'Scripting',
    'blurb': 'An object pipeline, not a text one, and the Windows logs it reads.',
    'context': 'You are at a PowerShell prompt on Windows. Everything in the pipeline is an object, not text.',
    'needs': ('pwsh',),
    'prereqs': ['bash'],
    # The object pipeline is graded by running it in a real pwsh. The
    # Windows-only cmdlets are not, and are not imitated either.
    'adapter': 'pwsh',
    'estimate': '4-6 hours',
    'order': 61,

    'lessons': [
        {
            'id': 'ps-what',
            'title': 'PowerShell on Linux, and why you would',
            'next': 'ps-objects',
            'concept': (
                'PowerShell is how you run a shell that pipes objects rather '
                'than text, and on Linux the command is `pwsh`. That is why '
                'Windows administration and the event-log work later in this '
                'module are readable from the machine you already have.\n\n'
                'That surprises people, and it is worth being clear about why '
                'you might care even if you never touch Windows.\n\n'
                '**The reason is the pipeline.** Every Unix shell pipes text '
                'between programs, so every program has to format its output '
                'for a human and every other program has to unpick that '
                'formatting. `cut`, `awk` and `sed` exist in large part to '
                'undo layout that was applied one step earlier. PowerShell '
                'pipes **objects**: structured things with named properties '
                'and types. Nothing is formatted until the very end, so '
                'nothing has to be parsed.\n\n'
                'Whether that is better is a genuine argument. What is not in '
                'doubt is that it is a **different idea worth having**, and '
                'that meeting it changes how you look at the shell you '
                'already use.\n\n'
                'The other reason is practical: **Windows administration '
                'happens in PowerShell**, and every DFIR and security module '
                'in this trainer that touches Windows expects you to read it. '
                'The event log module is written in it. Being able to read a '
                'PowerShell one-liner is a prerequisite for a lot of writing '
                'about Windows, whatever you run at home.\n\n'
                '**The naming is the friendly part.** Commands are '
                '`Verb-Noun`: `Get-Process`, `Stop-Service`, '
                '`Get-ChildItem`. The verbs come from a fixed approved list, '
                'so a command you have never seen is usually guessable, which '
                'is the exact opposite of `awk`, `dd` and `tar`.'
            ),
            'examples': [
                {
                    'label': 'Starting it, and leaving',
                    'code': ('pwsh              PS > is PowerShell\n'
                             'exit              back to bash\n'
                             '\n'
                             'pwsh -c "Get-Process | Select -First 3"\n'
                             '                  one command, no prompt'),
                    'note': 'It is an ordinary program you start and leave. '
                            'The prompt changing to PS > is the only sign you '
                            'are in it.',
                },
                {
                    'label': 'Guessable names, for once',
                    'code': ('Get-Process       list processes\n'
                             'Get-ChildItem     list a directory (ls)\n'
                             'Get-Content       print a file (cat)\n'
                             'Stop-Process      kill\n'
                             '\n'
                             'Get-Command -Verb Get   list them all'),
                    'note': 'Verbose, and deliberately so. The aliases ls, '
                            'cat and cd all exist for interactive use, so '
                            'muscle memory mostly survives.',
                },
                {
                    'label': 'The difference in one line',
                    'code': ('bash   ls -l | awk \'{print $5}\'\n'
                             '       (which column was size again?)\n'
                             '\n'
                             'pwsh   Get-ChildItem | Select Length\n'
                             '       (the property is called Length)'),
                    'note': 'The bash version breaks if the format changes or '
                            'a filename has a space. The PowerShell one asks '
                            'for a named property and cannot.',
                },
            ],
            'misconceptions': [
                'PowerShell is not Windows-only. It is open source, runs on '
                'Linux and macOS, and everything in this module works from a '
                'Linux terminal.',
                'PowerShell is not a replacement for bash on Linux. It is a '
                'different model worth knowing, and most people use it '
                'alongside rather than instead.',
                'The long command names are not the whole story. Aliases like '
                'ls, cat and cd exist for typing, and the long forms are what '
                'you write in scripts and read in other people\'s.',
            ],
            'try_it': [
                'Run `pwsh`, then `Get-Process | Select -First 3`, then '
                '`exit`. That is the whole round trip.',
                'Run `Get-Command -Verb Get | Measure-Object` and see how '
                'many things you can now guess the name of.',
            ],
        },
        {
            'id': 'ps-objects',
            'title': 'The pipeline carries objects',
            'next': 'ps-verbnoun',
            'concept': (
                'The PowerShell pipeline is how you pass objects with named '
                'properties, not formatted text. That is why `Sort-Object '
                'Length` sorts on a number, and a space in a filename cannot '
                'break the line.\n\n'
                'In bash, `ls -l | awk \'{print $5}\'` works by counting '
                'columns in text somebody formatted for a human. If the format '
                'changes, or a filename has a space, it breaks. Every Unix '
                'pipeline is doing that, and `cut`, `awk` and `sed` exist '
                'largely to undo formatting that was applied a moment '
                'earlier.\n\n'
                'PowerShell passes **objects**. `Get-ChildItem` does not emit '
                'text, it emits file objects with a `Length` property, a '
                '`Name`, a `LastWriteTime`. `Get-ChildItem | Sort-Object '
                'Length` sorts on a number because it is a number. Nothing was '
                'formatted, so nothing has to be parsed back.\n\n'
                'The text you see is produced at the very end, by a formatter, '
                'purely for your benefit. That is why the display can lie about '
                'what is there, and why the next lesson\'s `Get-Member` matters '
                'so much.\n\n'
                'Formatting at the end is not the object. `Format-Table` '
                'destroys the objects for anything downstream, which is why '
                'a pretty table piped into `Where-Object` then fails. The '
                'TypeName becomes FormatStartData, `CPU` is gone, and '
                '`Where-Object CPU -gt 10` matches nothing. It looks like '
                'the filter is wrong. It is not; there is no CPU property '
                'left to test. `Select-Object Name` still prints a table, '
                'so people reach for `cut`. `-ExpandProperty Name` is the '
                'actual value. Filter and select first; format last. The '
                'next lesson is how commands are named, so you can find '
                'the next one.'
            ),
            'examples': [
                {
                    'label': 'The same job, two models',
                    'code': ('bash:\n'
                             "  ls -l | awk '$5 > 1000000 {print $9}'\n"
                             '  count columns in formatted text\n'
                             '\n'
                             'PowerShell:\n'
                             '  Get-ChildItem | Where-Object Length -gt 1MB |\n'
                             '    Select-Object Name\n'
                             '  filter on a property that is already a number'),
                    'note': '`1MB` is a literal PowerShell understands, which is '
                            'the kind of thing you get once values have types.',
                },
                {
                    'label': 'What you see is not what is there',
                    'code': ('Get-Process | Select-Object -First 1\n'
                             '  shows about eight columns\n'
                             '\n'
                             'Get-Process | Get-Member\n'
                             '  shows sixty-odd properties and methods'),
                    'note': 'The display picked eight. The object has all of '
                            'them, and you can filter on any of them.',
                },
                {
                    # The module never said how to start or leave pwsh, which
                    # matters more here than for most tools: on Linux it is a
                    # prompt inside your own shell, so leaving it and leaving
                    # the terminal look identical and are not.
                    'label': 'Starting it, and leaving it',
                    'code': ('pwsh               PS > is PowerShell, inside '
                             'your shell\n'
                             'exit               back to bash\n'
                             'Ctrl-D             the same thing\n'
                             'Ctrl-C             stop what is running, stay '
                             'here'),
                    'note': 'On Linux pwsh is a program you start and leave '
                            'like any other. The prompt changing to PS > is '
                            'the only sign you are in it.',
                },
            ],
            'misconceptions': [
                'PowerShell is not "bash with longer names". The pipeline '
                'carries a different kind of thing, and treating output as text '
                'is what makes it feel clumsy.',
                'You almost never need to parse PowerShell output. If you are '
                'reaching for string splitting, there is usually a property.',
                'It runs on Linux and macOS as `pwsh`, and most of this module '
                'applies there. The event-log parts do not, because those are '
                'Windows.',
            ],
            'try_it': [
                'If you have pwsh anywhere, run `Get-Process | Sort-Object CPU '
                '-Descending | Select-Object -First 5` and notice that nothing '
                'was parsed.',
            ],
        },
        {
            'id': 'ps-verbnoun',
            'title': 'Verb-Noun, and finding things',
            'next': 'ps-getmember',
            'concept': (
                'Every cmdlet is `Verb-Noun`, and the verbs come from an '
                'approved list. That sounds bureaucratic and is the reason the '
                'system is discoverable: if you know the noun, you can guess '
                'the command, and if you know the verb you can find every noun '
                'it applies to.\n\n'
                '`Get-` reads, `Set-` writes, `New-` creates, `Remove-` '
                'deletes, `Start-` and `Stop-` do what they say. So having '
                'never seen it, you can correctly guess that `Get-Service` '
                'exists and that `Stop-Service` stops one.\n\n'
                '`Get-Command` searches the whole set with wildcards, and '
                '`Get-Help` explains one, with `-Examples` being the part worth '
                'reading first. Between them you can work almost anything out '
                'without leaving the shell, which is the closest analogue to '
                '`apropos` and rather better than it.\n\n'
                'What that looks like on a fresh machine: `Get-Help '
                'Get-WinEvent` prints a one-paragraph stub and no examples. '
                'The cmdlet exists; the help files were never downloaded. '
                '`Update-Help` is the fetch, and until it runs, `-Examples` '
                'is empty and people assume the cmdlet is undocumented.\n\n'
                '`Get-Command *event*` is the search; `Get-Help Get-WinEvent '
                '-Examples` is the read. Guessing a Unix name (`ls` works as '
                'an alias) and then looking for `grep` is how people miss '
                '`Where-Object`. The next lesson is `Get-Member`, which is '
                'how you stop guessing at property names.'
            ),
            'examples': [
                {
                    'label': 'Finding your way',
                    'code': ('Get-Command *service*        what exists\n'
                             'Get-Command -Verb Get -Noun *Event*\n'
                             'Get-Help Get-WinEvent -Examples\n'
                             'Get-Help Get-WinEvent -Full\n'
                             'Update-Help                  fetch the full text'),
                    'note': '`-Examples` first, always. Most cmdlets have '
                            'several and they are usually the answer.',
                },
                {
                    'label': 'Aliases, and why not to use them in scripts',
                    'code': ('ls  gci  dir   ->  Get-ChildItem\n'
                             'cat  gc  type  ->  Get-Content\n'
                             'ps             ->  Get-Process\n'
                             '?              ->  Where-Object\n'
                             '%              ->  ForEach-Object'),
                    'note': 'Fine interactively, bad in a script: aliases can '
                            'differ between machines and read as noise to '
                            'anyone else.',
                },
            ],
            'misconceptions': [
                'Cmdlet names are case-insensitive, as is most of PowerShell. '
                '`get-process` works, and the capitalisation is convention.',
                'The Unix-looking aliases are not the Unix commands. `ls` here '
                'is `Get-ChildItem` and does not take `-la`.',
                '`Get-Help` may be a stub until you run `Update-Help`, which is '
                'why the help sometimes seems useless on a fresh machine.',
            ],
            'try_it': [
                'Guess the cmdlet that lists scheduled tasks, then check '
                'yourself with `Get-Command *ScheduledTask*`.',
            ],
        },
        {
            'id': 'ps-getmember',
            'title': 'Get-Member is the way in',
            'next': 'ps-filtering',
            'concept': (
                '`Get-Member` is how you list every property and method an '
                'object has, not the handful the display shows. That is why '
                'you find the field you actually want to filter on, instead '
                'of guessing at names.\n\n'
                'Since the default display shows only a handful '
                'of properties, `Get-Member` is how you discover the other '
                'fifty, and it is how you find the one you actually want to '
                'filter on.\n\n'
                'The companion is `Select-Object *`, which shows the values of '
                'every property for one object rather than just their names. '
                '`Get-Member` for the shape, `Select-Object *` for the '
                'contents. Between them you never have to guess what is '
                'available.\n\n'
                '`gm` is the alias. Run it on one object, not a thousand: '
                '`Get-Process | Select-Object -First 1 | Get-Member`. The '
                'failure is piping a formatted table into it and seeing '
                'format objects instead of processes. The TypeName starts '
                'with Format, `Kill()` is gone, and it looks as if '
                'processes have no methods. They do; the format cmdlet '
                'replaced them. The other miss is piping a thousand '
                'processes in and reading the same type description a '
                'thousand times. One unformatted object is the habit. The '
                'next lesson is Where, Select, ForEach and Sort, which is '
                'the pipeline vocabulary. Those cmdlets take property '
                'names; Get-Member is how those names stop being a guess.'
            ),
            'examples': [
                {
                    'label': 'Looking inside',
                    'code': ('Get-Process | Get-Member\n'
                             '  TypeName: System.Diagnostics.Process\n'
                             '  Name  MemberType  Definition\n'
                             '  CPU        Property   double\n'
                             '  Id         Property   int\n'
                             '  Kill       Method     void Kill()\n'
                             '\n'
                             'Get-Process | Select-Object -First 1 *'),
                    'note': 'The TypeName line is worth reading: it tells you '
                            'what to search for when you need the '
                            'documentation.',
                },
                {
                    'label': 'After Format-Table, Get-Member shows the wrapper',
                    'code': ('Get-Process | Format-Table | Get-Member\n'
                             '  TypeName: ...Format.FormatStartData\n'
                             '\n'
                             'Kill() is gone. CPU is gone.\n'
                             'these are display objects, not processes'),
                    'note': 'If the TypeName is not the type expected, '
                            'something upstream already destroyed the objects. '
                            'That is almost always a Format-* cmdlet.',
                },
            ],
            'misconceptions': [
                'The columns you see are chosen by a formatter, not by the '
                'object. Absence from the display says nothing about absence '
                'from the object.',
                '`Get-Member` on a collection describes the elements, not the '
                'collection. That is almost always what you wanted.',
                'Methods are there too. `Kill()` on a process object is '
                'sometimes more direct than finding a cmdlet for it.',
            ],
            'try_it': [
                'Pipe three different cmdlets into `Get-Member` and notice how '
                'much more is there than the display suggested.',
            ],
        },
        {
            'id': 'ps-filtering',
            'title': 'Where, Select, ForEach and Sort',
            'next': 'ps-output',
            'concept': (
                'Where-Object, Select-Object, Sort-Object and ForEach-Object '
                'are how you filter, pick, sort and act on objects. That is '
                'why they do most of the work.\n\n'
                '`Where-Object` filters, so it is grep and awk\'s pattern. '
                '`Select-Object` picks properties or a number of items, so it '
                'is cut and head. `Sort-Object` sorts on a named property, so '
                'it is sort with no `-k`. `ForEach-Object` runs a block per '
                'item, so it is xargs and awk\'s action.\n\n'
                'Inside `Where-Object` and `ForEach-Object`, `$_` is the current '
                'object. The modern comparison syntax lets you skip the block '
                'entirely for simple cases: `Where-Object Length -gt 1MB` reads '
                'better than the older `Where-Object { $_.Length -gt 1MB }` and '
                'means the same.\n\n'
                'The comparison operators are worth memorising because they are '
                'not symbols: `-eq`, `-ne`, `-gt`, `-lt`, `-like` for wildcards, '
                '`-match` for regex.\n\n'
                '`-eq` is case-insensitive. `-ceq` is not. Using `>` in a '
                'filter is a redirect, not a comparison, and it will write a '
                'file you did not want. What that looks like: `Where-Object '
                'CPU > 10` opens a file named `10` and writes the incoming '
                'objects into it, then the filter sees no comparison. The '
                'file appearing in the directory is the clue. The silent '
                'one is `-like` given a regex: `Name -like "^app"` matches '
                'nothing, because `^` is not a wildcard, and the pipeline '
                'just looks empty.\n\n'
                'A script is the same language as the prompt. `$n = 3` '
                'stores a value for the rest of the session. Names start '
                'with `$`. `$_` is the current pipeline object, which is '
                'why it appears inside `Where-Object` and `ForEach-Object` '
                'blocks and nowhere else.\n\n'
                '`if ($n -gt 1) { ... } else { ... }` is a language branch, '
                'not a cmdlet. The condition is in parentheses, the body in '
                'braces, and `-gt` is still the comparison because `>` '
                'would redirect.\n\n'
                '`foreach ($f in Get-ChildItem) { $f.Name }` is a statement: '
                'it collects the whole list, then loops. `ForEach-Object { '
                '$_.Name }` is a cmdlet: it streams one object at a time. '
                'The statement is clearer for a short script. The cmdlet is '
                'what belongs in a pipeline.\n\n'
                '`Group-Object Name` groups a stream and hands you `Name` '
                'and `Count`. That is the histogram. `Select-Object '
                '@{n="KB";e={$_.Length/1KB}}` is a calculated property: a '
                'new field from an expression.\n\n'
                'A pipeline function is `function Get-Root { param([Parameter('
                'ValueFromPipeline=$true)]$Path) process { Split-Path $Path '
                '-Leaf } }`. `[pscustomobject]@{Name=$n}` builds an object '
                'you can pipe onward.\n\n'
                '`pwsh ./script.ps1` runs a file. The `./` is required for '
                'the same reason a Unix shell refuses a name in the current '
                'directory: a script in `.` is not on `$env:PATH`. On '
                'Windows, ExecutionPolicy can refuse an unsigned file. '
                '`Get-ExecutionPolicy` shows the rule. A script is how a '
                'one-liner you trust becomes something you can run again.'
            ),
            'examples': [
                {
                    'label': 'Doing arithmetic on a property',
                    'code': 'Get-Process | Measure-Object CPU -Sum\nGet-Process | Measure-Object CPU -Average -Maximum\n\nCount, Sum, Average, Minimum, Maximum',
                    'note': 'Measure-Object counts by default and computes nothing else unless asked, which is why -Sum exists rather than being implied.',
                },
                {
                    'label': 'The four',
                    'code': ('Get-Process |\n'
                             '  Where-Object CPU -gt 10 |\n'
                             '  Sort-Object CPU -Descending |\n'
                             '  Select-Object -First 5 Name, Id, CPU\n'
                             '\n'
                             'Get-ChildItem *.log |\n'
                             '  ForEach-Object { $_.Name.ToUpper() }'),
                    'note': 'Read it top to bottom as a sentence. That is the '
                            'shape almost every useful PowerShell line has.',
                },
                {
                    'label': 'Operators',
                    'code': ('-eq  -ne          equal, not equal\n'
                             '-gt  -ge  -lt  -le\n'
                             '-like  "*.log"    wildcards\n'
                             '-match "^ERROR"   regex\n'
                             '-contains         is this item in that list\n'
                             '-in               is this in that list\n'
                             '\n'
                             '-ceq  -clike      the case-sensitive versions'),
                    'note': 'Comparisons are case-insensitive by default, which '
                            'is the opposite of every other shell you know.',
                },
                {
                    'label': 'Variables, if, foreach, and a file',
                    'code': (
                        '$n = 3\n'
                        'if ($n -gt 1) { "many" } else { "one" }\n'
                        'foreach ($f in Get-ChildItem) { $f.Name }\n'
                        'Get-ChildItem | ForEach-Object { $_.Name }\n'
                        '\n'
                        'pwsh ./script.ps1'
                    ),
                    'note': 'foreach the statement collects first. '
                            'ForEach-Object streams. $_ is only the '
                            'pipeline object. pwsh ./script.ps1 is how a '
                            'file runs.',
                },
            ],
            'misconceptions': [
                '`==` is not a comparison operator; it is a syntax error. '
                'PowerShell uses `-eq` because `>` was already redirection.',
                '`-match` takes a regex and `-like` takes wildcards. Using the '
                'wrong one silently matches nothing.',
                'String comparison is case-insensitive by default. Prefix with '
                '`c` when case matters, which is a real trap coming from Unix.',
                '`foreach` the statement is not `ForEach-Object`. The '
                'statement collects the whole list first. The cmdlet streams.',
            ],
            'try_it': [
                'Write one pipeline that finds the five largest files in a '
                'directory, using all four cmdlets.',
            ],
        },
        {
            'id': 'ps-output',
            'title': 'Getting output out',
            'next': 'ps-eventlog',
            'concept': (
                'Because objects survive all the way down the pipeline, '
                'exporting is a single cmdlet rather than an exercise in '
                'formatting.\n\n'
                'Import is the same idea backwards, and it is worth '
                'knowing first because the drills here lean on it. '
                '`Import-Csv` turns each row of a CSV into an object '
                'with one property per column, so a spreadsheet becomes '
                'something `Where-Object` and `Select-Object` can filter '
                'exactly like process objects. `Get-Content` gives you '
                'plain lines instead, and `Set-Content` writes them '
                'back.\n\n'
                '`Export-Csv -NoTypeInformation` writes real CSV with the '
                'properties as columns. `ConvertTo-Json` produces JSON you can '
                'hand to jq. `Out-File` writes text. `Export-Clixml` preserves '
                'the objects themselves, so `Import-Clixml` on another machine '
                'gets them back with types intact, which is genuinely useful '
                'when collecting evidence.\n\n'
                'The rule that catches everyone: **`Format-*` must be last.** '
                '`Format-Table` and `Format-List` destroy the objects and emit '
                'formatting instructions, so anything after them receives '
                'nonsense. If your export is full of empty columns, a '
                '`Format-Table` is upstream of it.\n\n'
                'The other quiet loss is encoding. `>` is `Out-File` with '
                'the default encoding, which on Windows PowerShell 5 was '
                'UTF-16 with a BOM. Open that file on Linux and `grep` sees '
                'garbage at the start of every line, or a binary-looking '
                'file. `-Encoding utf8` is the fix. `ConvertTo-Json` has a '
                'different trap: `-Depth` defaults to 2, so a nested event '
                'object becomes `{...}` and the fields are gone.'
            ),
            'examples': [
                {
                    'label': 'Exporting',
                    'code': ('... | Export-Csv -NoTypeInformation out.csv\n'
                             '... | ConvertTo-Json -Depth 5 > out.json\n'
                             '... | Export-Clixml evidence.xml\n'
                             '... | Out-File -Encoding utf8 out.txt\n'
                             '\n'
                             'Import-Clixml evidence.xml   objects, restored'),
                    'note': '`-Depth` on ConvertTo-Json defaults to 2 and '
                            'silently truncates nested structures, which is a '
                            'quiet way to lose data.',
                },
                {
                    'label': 'The Format-* trap',
                    'code': ('wrong:\n'
                             '  ... | Format-Table | Export-Csv out.csv\n'
                             '  out.csv is full of formatting objects\n'
                             '\n'
                             'right:\n'
                             '  ... | Select-Object A, B | Export-Csv out.csv\n'
                             '  ... | Format-Table          for reading only'),
                    'note': 'Select-Object shapes data. Format-Table shapes '
                            'display. They look similar and are not.',
                },
            ],
            'misconceptions': [
                '`Format-Table` is not `Select-Object`. One is for your eyes at '
                'the end of a pipeline, the other is a real projection you can '
                'keep piping.',
                '`Export-Csv` without `-NoTypeInformation` writes a junk header '
                'line on older versions. Newer PowerShell dropped it.',
                '`>` is `Out-File` with the default encoding, which historically '
                'was UTF-16 and surprised everyone who then read the file on '
                'Linux.',
            ],
            'try_it': [
                'Export a process list to CSV, then deliberately put '
                '`Format-Table` in the middle and look at what you get.',
            ],
        },
        {
            'id': 'ps-eventlog',
            'title': 'Get-WinEvent, and filtering at the source',
            'concept': (
                'Windows event logs are the evidence in most Windows '
                'investigations, and `Get-WinEvent` is how you reach them. The '
                'part that matters is **where** the filtering happens.\n\n'
                'Piping into `Where-Object` pulls every event across into '
                'PowerShell and filters afterwards. On a Security log with '
                'millions of records that is minutes to hours. Passing '
                '`-FilterHashtable` or `-FilterXPath` pushes the filter into the '
                'log subsystem, which does it at the source and returns only '
                'what matched. Same answer, wildly different time.\n\n'
                'The hashtable form is the readable one and covers most needs: '
                'log name, event id, and a time range. XPath is more expressive '
                'and is what you need to filter on a field inside the event '
                'data rather than on its metadata. Against an XML *file*, '
                '`Select-Xml -Path events.xml -XPath //Event` is the same '
                'language without the event log.\n\n'
                'Worth knowing by number: 4624 is a successful logon, 4625 a '
                'failed one, 4688 a process creation, and 1102 is the security '
                'log being cleared, which is rarely innocent.\n\n'
                'This module is useful on Linux for the object pipeline. '
                'Get-WinEvent needs Windows. Filtering at the source is the '
                'habit that transfers: push the predicate into the tool, do '
                'not pull a million rows and then grep.\n\n'
                'What the slow path looks like: `Get-WinEvent -LogName '
                'Security | Where-Object Id -eq 4625` starts printing '
                'eventually, then the prompt never comes back, because it '
                'is still walking millions of events you already decided '
                'you do not want. `-MaxEvents` on the unfiltered query '
                'does not save you if `Where-Object` is downstream: the '
                'source still emits everything.'
            ),
            'examples': [
                {
                    'label': 'Filter at the source',
                    'code': ('slow:\n'
                             '  Get-WinEvent -LogName Security |\n'
                             '    Where-Object Id -eq 4625\n'
                             '\n'
                             'fast:\n'
                             '  Get-WinEvent -FilterHashtable @{\n'
                             '    LogName   = "Security"\n'
                             '    Id        = 4625\n'
                             '    StartTime = (Get-Date).AddDays(-1)\n'
                             '  }'),
                    'note': 'The difference on a real Security log is minutes '
                            'versus seconds, and it is the single most useful '
                            'thing in this lesson.',
                },
                {
                    'label': 'Reaching inside the event',
                    'code': ('Get-WinEvent -LogName Security -FilterXPath "\n'
                             '  *[System[EventID=4625]] and\n'
                             '   *[EventData[Data[@Name=\'TargetUserName\']\n'
                             '     =\'administrator\']]"\n'
                             '\n'
                             '$e = Get-WinEvent -MaxEvents 1 ...\n'
                             '$e | Select-Object -ExpandProperty Properties'),
                    'note': 'The hashtable cannot see inside EventData. That is '
                            'the line where you have to switch to XPath.',
                },
            ],
            'misconceptions': [
                'Filtering with `Where-Object` gives the right answer and the '
                'wrong runtime. On a large log it is the difference between a '
                'useful tool and an abandoned one.',
                'The event Message is rendered text and is slow to produce. '
                'Filter and select on the structured properties, and read the '
                'message only for the events you kept.',
                '`Get-EventLog` is the old cmdlet and cannot see most modern '
                'logs. `Get-WinEvent` is the one to learn.',
                'These cmdlets are Windows-only. `pwsh` on Linux runs the '
                'language but there are no Windows event logs to read.',
            ],
            'try_it': [
                'On any Windows machine you have access to, count failed logons '
                'in the last day with a FilterHashtable, then time the '
                'Where-Object version and compare.',
            ],
        },
    ],

    'drills': [
        {'id': 'ps-cmd-getcommand', 'type': 'command', 'answer': 'Get-Command *service*',
         'prompt': 'Find every cmdlet whose name mentions service.',
         'teach': 'Every cmdlet is Verb-Noun, so guessing the noun and '
                  'wildcarding it finds the command faster than a search '
                  'engine will.'},
        {'id': 'ps-cmd-help', 'type': 'command', 'answer': 'Get-Help Get-WinEvent -Examples',
         'prompt': 'Read the examples for a cmdlet, which is the part worth '
                   'reading first.',
         'teach': '-Examples is the section worth reading first. -Online '
                  'opens the full page, and local help may need Update-Help '
                  'before it exists at all.'},
        {'id': 'ps-cmd-getmember', 'type': 'command', 'answer': 'Get-Process | Get-Member',
         'prompt': 'Discover every property and method an object has, not the few the display shows.',
         'teach': 'The one habit to take from this module: pipe anything you do '
                  'not understand into Get-Member.'},
        {'id': 'ps-cmd-selectstar', 'type': 'command',
         'answer': 'Get-Process | Select-Object -First 1 *',
         'prompt': 'Show every property VALUE for one object, rather than just '
                   'the property names.',
         'teach': 'The default display shows a handful of properties chosen '
                  'by a format file, not everything the object actually '
                  'carries.'},
        {'id': 'ps-cmd-where', 'type': 'command',
         'answer': 'Get-Process | Where-Object CPU -gt 10',
         'prompt': 'Keep only the processes using more than ten seconds of CPU, '
                   'using the modern comparison form.',
         'teach': 'The comparison operators are written -gt, -eq, -lt and so '
                  'on because the angle brackets mean redirection. This short '
                  'form handles one comparison only.'},
        {'id': 'ps-cmd-where-block', 'type': 'command',
         'answer': 'Get-Process | Where-Object { $_.CPU -gt 10 }',
         'prompt': 'Write the same filter with a script block and the current object.',
         'teach': '$_ is the current object. The block form is needed as soon '
                  'as the condition is more than one comparison.'},
        {'id': 'ps-cmd-sort', 'type': 'command',
         'answer': 'Get-Process | Sort-Object CPU -Descending',
         'prompt': 'Sort processes by CPU, highest first.',
         'teach': 'No -k and no -n, because CPU is already a number.'},
        {'id': 'ps-cmd-select', 'type': 'command',
         'answer': 'Get-Process | Select-Object -First 5 Name, Id, CPU',
         'prompt': 'Take the first five and keep only three properties.',
         'teach': 'Select-Object picks properties and counts; Where-Object '
                  'picks objects. Confusing the two is the usual beginner '
                  'error.'},
        {'id': 'ps-cmd-foreach', 'type': 'command',
         'answer': 'Get-ChildItem | ForEach-Object { $_.Name }',
         'prompt': 'Run a block once per item in the pipeline.',
         'teach': '$_ is the current object. ForEach-Object streams down the '
                  'pipeline, while a foreach statement collects everything '
                  'first.'},
        {'id': 'ps-cmd-measure', 'type': 'command',
         'answer': 'Get-Process | Measure-Object CPU -Sum',
         'prompt': 'Total a numeric property across the pipeline.',
         'teach': 'It does count, sum, average, minimum and maximum, and it '
                  'counts by default when you name no property.'},
        {'id': 'ps-cmd-group', 'type': 'command',
         'answer': 'Get-Process | Group-Object Name',
         'prompt': 'Group pipeline items by a property, which is the '
                   'sort | uniq -c of PowerShell.',
         'teach': 'You get objects back carrying Count and Name, so you can '
                  'sort on the count instead of parsing text to find it.'},
        {'id': 'ps-cmd-match', 'type': 'command',
         'answer': 'Get-ChildItem | Where-Object Name -match "^app"',
         'prompt': 'Filter on a property using a regular expression.',
         'teach': '-match is regex, -like is wildcards. Using the wrong one '
                  'silently matches nothing.'},
        {'id': 'ps-cmd-like', 'type': 'command',
         'answer': 'Get-ChildItem | Where-Object Name -like "*.log"',
         'prompt': 'Filter on a property using a wildcard rather than a regex.',
         'teach': '-like takes wildcards, -match takes a regex, and -eq on a '
                  'string is exact. Picking the wrong one is why a filter '
                  'silently matches nothing.'},
        {'id': 'ps-cmd-csv', 'type': 'command',
         'answer': 'Export-Csv -NoTypeInformation out.csv',
         'prompt': 'Write pipeline objects out as real CSV, with the properties '
                   'as columns.',
         'teach': '-NoTypeInformation drops the type comment older versions '
                  'put on the first line, which breaks every other CSV reader '
                  'that meets it.'},
        {'id': 'ps-cmd-json', 'type': 'command', 'answer': 'ConvertTo-Json -Depth 5',
         'prompt': 'Convert pipeline objects to JSON without silently '
                   'truncating nested structures.',
         'teach': '-Depth defaults to 2, which is a quiet way to lose data.'},
        {'id': 'ps-cmd-clixml', 'type': 'command', 'answer': 'Export-Clixml evidence.xml',
         'prompt': 'Save objects with their types intact, so another machine '
                   'can load them back as objects.',
         'teach': 'CSV flattens everything to strings. This keeps the object '
                  'structure, which is what you want when handing evidence to '
                  'another analyst.'},
        {'id': 'ps-cmd-service', 'type': 'command', 'answer': 'Get-Service',
         'prompt': 'List services, using the cmdlet name you can guess from the '
                   'verb-noun rule.',
         'teach': 'The verb-noun rule means you can often guess a cmdlet you '
                  'have never used, which is the single biggest thing '
                  'PowerShell gets right.'},
        {'id': 'ps-cmd-winevent-hash', 'type': 'command',
         'answer': 'Get-WinEvent -FilterHashtable @{LogName="Security"; Id=4625}',
         'prompt': 'Get failed logon events, filtering at the source rather '
                   'than afterwards.',
         'teach': 'On a real Security log this is the difference between '
                  'seconds and many minutes.'},
        {'id': 'ps-cmd-winevent-time', 'type': 'command',
         'answer': 'Get-WinEvent -FilterHashtable @{LogName="Security"; Id=4624; '
                   'StartTime=(Get-Date).AddDays(-1)}',
         'prompt': 'Get successful logons from the last day, filtered at the '
                   'source.',
         'teach': 'A filter hashtable is applied inside the event log '
                  'service. Piping to Where-Object instead pulls every event '
                  'across first, which on a Security log can take hours.'},
        {'id': 'ps-cmd-winevent-xpath', 'type': 'command',
         'answer': 'Get-WinEvent -LogName Security -FilterXPath "*[System[EventID=4688]]"',
         'prompt': 'Use XPath to filter events, which is what you need to reach '
                   'inside the event data.',
         'teach': "The hashtable filter cannot reach inside the event's own "
                  'data fields and XPath can. That is the only reason to '
                  'accept the syntax.'},
        {'id': 'ps-cmd-expand', 'type': 'command',
         'answer': 'Select-Object -ExpandProperty Properties',
         'prompt': 'Unwrap a property so you get its contents rather than an '
                   'object containing it.',
         'teach': 'Without it you get an object whose single property holds '
                  'what you wanted, and the display shows the wrapper rather '
                  'than the contents.'},
        # ------------------------------------------------------------------
        # Graded by running them in a real PowerShell, in a throwaway
        # directory holding six sample files and `logons.csv`, a table of
        # synthetic logon records. It is a CSV and not an event log, on
        # purpose: see the adapter. Answers are compared on what they print,
        # so any pipeline printing the same thing passes.
        #
        # Full cmdlet names throughout. PowerShell drops the aliases that
        # would shadow real binaries on Linux and macOS, so `sort` here runs
        # /usr/bin/sort. The adapter detects that and explains it, but the
        # references must not depend on it.
        # ------------------------------------------------------------------
        {'id': 'ps-run-largest', 'type': 'pwsh',
         'answer': 'Get-ChildItem | Sort-Object Length -Descending | '
                   'Select-Object -First 3 -ExpandProperty Name',
         'prompt': 'Print the names of the three largest files, largest '
                   'first, one name per line.',
         'teach': 'No parsing anywhere. `ls -lS | head -3 | awk ...` gets the '
                  'same answer by cutting up a string that was formatted for '
                  'a human, and breaks on the filename with a space in it.'},
        {'id': 'ps-run-expand', 'type': 'pwsh',
         'answer': 'Get-ChildItem -Filter *.txt | Sort-Object Name | '
                   'Select-Object -ExpandProperty Name',
         'prompt': 'Print just the names of the .txt files, sorted, one per '
                   'line, with no table header.',
         'teach': '-ExpandProperty is the difference between an object with '
                  'one property and the value itself. Without it you get a '
                  'table with a header, which is the single most common '
                  'surprise when piping into something else.'},
        {'id': 'ps-run-sum', 'type': 'pwsh',
         'answer': 'Get-ChildItem | Measure-Object Length -Sum | '
                   'Select-Object -ExpandProperty Sum',
         'prompt': 'Print the total number of bytes in the directory, as a '
                   'bare number.',
         'teach': 'Measure-Object returns an object with Count, Sum, Average '
                  'and friends, so the sum has to be asked for by name.'},
        {'id': 'ps-run-count', 'type': 'pwsh',
         'answer': '(Get-ChildItem -Filter *.txt).Count',
         'prompt': 'Print how many .txt files there are, as a bare number.',
         'teach': 'Wrapping in parentheses and taking .Count is the terse '
                  'form. It has one trap worth knowing: a single result is '
                  'not an array, so older PowerShell returned nothing here.'},
        {'id': 'ps-run-match', 'type': 'pwsh',
         'answer': "Get-ChildItem | Where-Object Name -match 'report' | "
                   'Sort-Object Name | Select-Object -ExpandProperty Name',
         'prompt': 'Print the names of files whose name contains "report", '
                   'sorted, one per line.',
         'teach': '-match is a regular expression and -like is wildcards. '
                  'Reaching for -like out of habit and then writing regex '
                  'inside it is the usual way this goes wrong.'},
        {'id': 'ps-run-like', 'type': 'pwsh',
         'answer': "Get-ChildItem | Where-Object Name -like '*.txt' | "
                   'Sort-Object Name | Select-Object -ExpandProperty Name',
         'prompt': 'Now the same shape with wildcards: print the names ending '
                   'in .txt, sorted, one per line.',
         'teach': 'Same question, other operator. `-like "*.txt"` and '
                  '`-match "\\.txt$"` both work; mixing the syntaxes does not.'},
        {'id': 'ps-run-failed', 'type': 'pwsh',
         'answer': '(Import-Csv logons.csv | Where-Object Id -eq 4625).Count',
         'prompt': 'logons.csv holds logon records. Print how many are failures '
                   '(Id 4625), as a bare number.',
         'teach': 'Import-Csv hands you objects with named properties, so the '
                  'filter is on a field rather than on a column position that '
                  'moves the moment the format changes.'},
        {'id': 'ps-run-top-account', 'type': 'pwsh',
         'answer': 'Import-Csv logons.csv | Where-Object Id -eq 4625 | '
                   'Group-Object Account | Sort-Object Count -Descending | '
                   'Select-Object -First 1 -ExpandProperty Name',
         'prompt': 'Print the name of the account with the most failed logons.',
         'teach': 'Group-Object then sort by Count is the shape of nearly '
                  'every "which one is worst" question in an investigation.'},
        {'id': 'ps-run-group-table', 'type': 'pwsh',
         'answer': 'Import-Csv logons.csv | Where-Object Id -eq 4625 | '
                   'Group-Object Account | Sort-Object Count -Descending | '
                   'Select-Object Count, Name',
         'prompt': 'Print failure counts by account, worst first, as columns '
                   'Count then Name.',
         'teach': 'Select-Object at the end, never Format-Table: this output '
                  'is still objects, so it can go on to Export-Csv. A '
                  'Format-* cmdlet turns it into formatting instructions and '
                  'everything downstream gets nonsense.'},
        {'id': 'ps-run-unique', 'type': 'pwsh',
         'answer': 'Import-Csv logons.csv | Select-Object -ExpandProperty '
                   'Workstation -Unique | Sort-Object',
         'prompt': 'Print each distinct workstation name once, sorted, one '
                   'per line.',
         'teach': '-Unique on Select-Object, not a separate uniq, and note it '
                  'does not require sorting first the way `sort | uniq` does.'},
        {'id': 'ps-run-calc', 'type': 'pwsh',
         'answer': 'Get-ChildItem -Filter *.txt | Sort-Object Name | '
                   'Select-Object Name, @{n="KB";e={[math]::Round($_.Length/1KB,1)}}',
         'prompt': 'Print the .txt files by name, as Name plus a calculated '
                   'column KB rounded to one decimal.',
         'teach': 'The calculated property hashtable, @{n=...;e={...}}, is '
                  'the thing to memorise: it is how you add a column that '
                  'does not exist on the object. 1KB is a real literal.'},
        {'id': 'ps-run-foreach', 'type': 'pwsh',
         'answer': 'Get-ChildItem | ForEach-Object { $_.Name.ToUpper() } | '
                   'Sort-Object',
         'prompt': 'Print every filename in upper case, sorted, one per line.',
         'teach': '$_ is the current object and it has methods, not just '
                  'properties. Calling .ToUpper() on it is a reminder that '
                  'these are real .NET objects.'},

        {'id': 'ps-cmd-max', 'type': 'command',
         'answer': 'Get-WinEvent -LogName Security -MaxEvents 10',
         'prompt': 'Take only the ten most recent events, so an exploratory '
                   'query cannot run away.',
         'teach': '-MaxEvents stops at the source. Piping to Select-Object '
                  '-First also stops early, but only after the query has '
                  'begun returning.'},
    ],

    'challenges': [
        {
            'id': 'ps-object-pipeline',
            'title': 'Feel the difference',
            'goal': 'Do the same job in bash and in PowerShell and notice that '
                    'one of them parses text and the other does not. Needs a '
                    'machine with pwsh, so the trainer cannot check it.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'In bash, list the five largest files in a '
                                'directory.',
                 'hint': 'ls -lS | head -6, or find with -printf and sort'},
                {'instruction': 'In PowerShell, do the same.',
                 'hint': 'Get-ChildItem | Sort-Object Length -Descending | '
                         'Select-Object -First 5 Name, Length'},
                {'instruction': 'Now make both handle a filename containing a '
                                'space. Note which one needed changing.'},
                {'instruction': 'Pipe the PowerShell version into Get-Member '
                                'and find three properties the display never '
                                'showed you.'},
            ],
            'free': 'Solve "five largest files" in both shells, then break both '
                    'with a filename containing a space and see which survives.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
        {
            'id': 'ps-eventlog-hunt',
            'title': 'Filter at the source',
            'goal': 'Answer a real question from a Windows event log, and prove '
                    'to yourself where the filtering belongs. Needs Windows.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'Count failed logons in the last day using '
                                '-FilterHashtable.',
                 'hint': '@{LogName="Security"; Id=4625; '
                         'StartTime=(Get-Date).AddDays(-1)}'},
                {'instruction': 'Do the same with Get-WinEvent piped into '
                                'Where-Object, and time both.',
                 'hint': 'Measure-Command { ... }'},
                {'instruction': 'Group the failures by account name and find '
                                'the most targeted one.',
                 'hint': 'Group-Object, after expanding the properties'},
                {'instruction': 'Export the result to CSV without a Format-* '
                                'cmdlet anywhere in the pipeline.'},
            ],
            'free': 'Using filtering at the source, count and group failed '
                    'logons from the last day and export the result to CSV.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
        {
            'id': 'ps-getmember',
            'title': 'Ask an object what it is',
            'goal': 'Use Get-Member the way it is meant to be used: as the '
                    'first thing you do with an unfamiliar object, not the '
                    'last.',
            'setup': {'kind': 'pwshbox', 'tree': {
                'staff.csv': 'name,dept,salary\nalice,eng,100\n'
                             'bob,sales,80\ncarol,eng,120\n',
            }},
            'solution': {'shell':
                'pwsh -NoProfile -Command \'Import-Csv staff.csv | '
                'Get-Member | Out-String | Set-Content members.txt; '
                'Import-Csv staff.csv | Get-Member -MemberType NoteProperty | '
                'ForEach-Object { $_.Name } | Set-Content props.txt\''},
            'steps': [
                {'instruction': 'Import staff.csv and pipe it into Get-Member. '
                                'Add Out-String, or Set-Content records only '
                                'each member and loses the type header.',
                 'hint': 'Import-Csv staff.csv | Get-Member | Out-String | '
                         'Set-Content members.txt'},
                {'instruction': 'Now list just the property names, one per '
                                'line, into props.txt.',
                 'hint': '-MemberType NoteProperty, then ForEach-Object '
                         '{ $_.Name }'},
                {'instruction': 'Note that the type name at the top of '
                                'members.txt is what tells you which cmdlets '
                                'will accept this object.'},
            ],
            'free': 'Produce members.txt with the full Get-Member output for '
                    'the imported CSV, and props.txt listing just its '
                    'property names.',
            'verify': {'kind': 'pwshbox', 'expect': {
                'file_contains': {'members.txt': ['TypeName', 'NoteProperty'],
                                  'props.txt': ['name', 'dept', 'salary']}}},
            'fallback': 'self',
        },
        {
            'id': 'ps-filter-sort',
            'title': 'Filter, sort and select, in that order',
            'goal': 'Build the pipeline everybody actually writes, and get '
                    'the numeric sort right, which is where it usually goes '
                    'wrong.',
            'setup': {'kind': 'pwshbox', 'tree': {
                'staff.csv': 'name,dept,salary\nalice,eng,100\n'
                             'bob,sales,80\ncarol,eng,120\ndave,eng,90\n',
            }},
            'solution': {'shell':
                'pwsh -NoProfile -Command \'Import-Csv staff.csv | '
                'Where-Object { $_.dept -eq "eng" } | '
                'Sort-Object { [int]$_.salary } -Descending | '
                'Select-Object name,salary | '
                'Export-Csv -NoTypeInformation eng.csv\''},
            'steps': [
                {'instruction': 'Import staff.csv and keep only the rows '
                                'where dept is eng.',
                 'hint': 'Where-Object { $_.dept -eq "eng" }'},
                {'instruction': 'Sort them by salary, highest first. CSV '
                                'gives you strings, so cast to int or you '
                                'will sort alphabetically.',
                 'hint': 'Sort-Object { [int]$_.salary } -Descending'},
                {'instruction': 'Keep only name and salary, and export to '
                                'eng.csv without the type header.',
                 'hint': 'Export-Csv -NoTypeInformation eng.csv'},
            ],
            'free': 'Produce eng.csv containing only the engineering staff, '
                    'sorted by salary descending, with just the name and '
                    'salary columns.',
            'verify': {'kind': 'pwshbox', 'expect': {
                'file_contains': {'eng.csv': ['"carol","120"', '"alice","100"',
                                              '"dave","90"']},
                'file_lacks': {'eng.csv': 'bob'}}},
            'fallback': 'self',
        },
        {
            'id': 'ps-calculated',
            'title': 'Add a column that was not there',
            'goal': 'Use a calculated property, which is the piece of syntax '
                    'that turns Select-Object from a column picker into a '
                    'transformer.',
            'setup': {'kind': 'pwshbox', 'tree': {
                'staff.csv': 'name,dept,salary\nalice,eng,100\n'
                             'bob,sales,80\ncarol,eng,120\n',
            }},
            'solution': {'shell':
                'pwsh -NoProfile -Command \'Import-Csv staff.csv | '
                'Select-Object name,@{n="Annual";e={[int]$_.salary * 12}} | '
                'Export-Csv -NoTypeInformation annual.csv\''},
            'steps': [
                {'instruction': 'Import the CSV and select the name column '
                                'plus a new column called Annual.',
                 'hint': '@{n="Annual";e={[int]$_.salary * 12}}'},
                {'instruction': 'The expression runs per object, with $_ '
                                'bound to that object. Multiply the salary by '
                                'twelve.'},
                {'instruction': 'Export to annual.csv without the type '
                                'header.'},
            ],
            'free': 'Produce annual.csv with a name column and a computed '
                    'Annual column holding twelve times the salary.',
            'verify': {'kind': 'pwshbox', 'expect': {
                'file_contains': {'annual.csv': ['"Annual"', '"alice","1200"',
                                                 '"carol","1440"']}}},
            'fallback': 'self',
        },
        {
            'id': 'ps-group',
            'title': 'Count by key, the object way',
            'goal': 'Group-Object, which is the cmdlet that replaces sort '
                    'and uniq -c, and produces objects rather than a table '
                    'you have to parse back.',
            'setup': {'kind': 'pwshbox', 'tree': {
                'events.csv': 'user,action\nalice,login\nbob,login\n'
                              'alice,logout\nalice,login\ncarol,login\n'
                              'bob,logout\n',
            }},
            'solution': {'shell':
                'pwsh -NoProfile -Command \'Import-Csv events.csv | '
                'Group-Object user | Sort-Object Count -Descending | '
                'ForEach-Object { "$($_.Count) $($_.Name)" } | '
                'Set-Content byuser.txt; '
                'Import-Csv events.csv | Group-Object action | '
                'Select-Object Name,Count | '
                'Export-Csv -NoTypeInformation byaction.csv\''},
            'steps': [
                {'instruction': 'Group the events by user, sort by count '
                                'descending, and write "count name" lines to '
                                'byuser.txt.',
                 'hint': 'Group-Object user | Sort-Object Count -Descending'},
                {'instruction': 'Separately group by action and export Name '
                                'and Count to byaction.csv.'},
                {'instruction': 'Note that Group-Object hands you objects '
                                'with a Count and a Group, not text you have '
                                'to parse.'},
            ],
            'free': 'Produce byuser.txt with counts per user, most frequent '
                    'first, and byaction.csv with the count per action.',
            'verify': {'kind': 'pwshbox', 'expect': {
                'file_contains': {'byuser.txt': ['3 alice', '2 bob'],
                                  'byaction.csv': ['"login","4"',
                                                   '"logout","2"']}}},
            'fallback': 'self',
        },
        {
            'id': 'ps-formats',
            'title': 'Export properly, and never through Format-Table',
            'goal': 'Write the same data three ways, and see why a Format-* '
                    'cmdlet must be the last thing in a pipeline.',
            'setup': {'kind': 'pwshbox', 'tree': {
                'staff.csv': 'name,dept,salary\nalice,eng,100\n'
                             'bob,sales,80\n',
            }},
            'solution': {'shell':
                'pwsh -NoProfile -Command \'$s = Import-Csv staff.csv; '
                '$s | Export-Csv -NoTypeInformation out.csv; '
                '$s | ConvertTo-Json | Set-Content out.json; '
                '$s | Export-Clixml out.xml; '
                '$s | Format-Table | Out-String | Set-Content formatted.txt; '
                '$s | Format-Table | Get-Member | '
                'Select-Object -First 1 -ExpandProperty TypeName | '
                'Set-Content whatformatgives.txt\''},
            'steps': [
                {'instruction': 'Import the CSV once into a variable, then '
                                'export it to out.csv, out.json and out.xml.',
                 'hint': 'Export-Csv, ConvertTo-Json, Export-Clixml'},
                {'instruction': 'Now pipe it through Format-Table into '
                                'formatted.txt, and note that this is text '
                                'for a human.'},
                {'instruction': 'Pipe Format-Table into Get-Member and write '
                                'the type name you get to '
                                'whatformatgives.txt. That type is why '
                                'nothing downstream of Format-* works.',
                 'hint': 'Format-Table | Get-Member'},
            ],
            'free': 'Produce out.csv, out.json, out.xml, formatted.txt, and '
                    'whatformatgives.txt showing the format object type that '
                    'Format-Table emits.',
            'verify': {'kind': 'pwshbox', 'expect': {
                'is_file': ['out.csv', 'out.json', 'out.xml',
                            'formatted.txt'],
                'file_contains': {'out.json': 'alice',
                                  'whatformatgives.txt': 'Format'}}},
            'fallback': 'self',
        },
        {
            'id': 'ps-xpath-xml',
            'title': 'Filter event XML with XPath, on this machine',
            'goal': 'Get-WinEvent needs Windows, but the XPath does not. '
                    'Practise the filter language against real event XML '
                    'here.',
            'setup': {'kind': 'pwshbox', 'tree': {
                'events.xml':
                    '<Events>\n'
                    '<Event><System><EventID>4625</EventID></System>'
                    '<EventData><Data Name="TargetUserName">admin</Data>'
                    '</EventData></Event>\n'
                    '<Event><System><EventID>4625</EventID></System>'
                    '<EventData><Data Name="TargetUserName">root</Data>'
                    '</EventData></Event>\n'
                    '<Event><System><EventID>4624</EventID></System>'
                    '<EventData><Data Name="TargetUserName">sage</Data>'
                    '</EventData></Event>\n'
                    '</Events>\n',
            }},
            'solution': {'shell':
                'pwsh -NoProfile -Command \'(Select-Xml -Path events.xml '
                '-XPath "//Event[System/EventID=4625]").Count | '
                'Set-Content failed.txt; '
                'Select-Xml -Path events.xml -XPath '
                '"//Event[System/EventID=4625]" | ForEach-Object '
                '{ ($_.Node.EventData.Data)."#text" } | '
                'Set-Content who.txt\''},
            'steps': [
                {'instruction': 'Count the 4625 events in events.xml and '
                                'write the number to failed.txt.',
                 'hint': '(Select-Xml -Path events.xml -XPath '
                         '"//Event[System/EventID=4625]").Count'},
                {'instruction': 'Write the target username from each of those '
                                'events to who.txt, one per line.'},
                {'instruction': 'This is the same filter shape Get-WinEvent '
                                'takes, which is why the skill transfers even '
                                'though the cmdlet does not.'},
            ],
            'free': 'Produce failed.txt holding the count of 4625 events, and '
                    'who.txt listing the target usernames from them.',
            'verify': {'kind': 'pwshbox', 'expect': {
                'file_contains': {'failed.txt': '2',
                                  'who.txt': ['admin', 'root']},
                'file_lacks': {'who.txt': 'sage'}}},
            'fallback': 'self',
        },
        {
            'id': 'ps-function',
            'title': 'Write a function that behaves like a cmdlet',
            'goal': 'Parameters, a pipeline input block, and returning '
                    'objects rather than printing text.',
            'setup': {'kind': 'pwshbox', 'tree': {
                'nums.txt': '4\n9\n16\n25\n',
            }},
            'solution': {'shell':
                "cat > roots.ps1 <<'PS1'\n"
                'function Get-Root {\n'
                '    param(\n'
                '        [Parameter(ValueFromPipeline=$true)]\n'
                '        [int]$Number\n'
                '    )\n'
                '    process {\n'
                '        [pscustomobject]@{ Number = $Number; Root = '
                '[math]::Sqrt($Number) }\n'
                '    }\n'
                '}\n'
                'PS1\n'
                'pwsh -NoProfile -Command \'. ./roots.ps1; '
                'Get-Content nums.txt | Get-Root | '
                'Export-Csv -NoTypeInformation roots.csv\''},
            'steps': [
                {'instruction': 'Write roots.ps1 defining a function Get-Root '
                                'with an int parameter that accepts pipeline '
                                'input.',
                 'hint': '[Parameter(ValueFromPipeline=$true)]'},
                {'instruction': 'Inside a process block, emit a custom object '
                                'with Number and Root properties. Emit, do '
                                'not Write-Host.',
                 'hint': '[pscustomobject]@{ Number = $Number; Root = '
                         '[math]::Sqrt($Number) }'},
                {'instruction': 'Dot source it, pipe nums.txt through it, and '
                                'export to roots.csv.',
                 'hint': '. ./roots.ps1; Get-Content nums.txt | Get-Root'},
            ],
            'free': 'Produce roots.ps1 defining a pipeline-capable Get-Root '
                    'function, and roots.csv holding each number with its '
                    'square root.',
            'verify': {'kind': 'pwshbox', 'expect': {
                'file_contains': {'roots.ps1': ['function Get-Root',
                                                'ValueFromPipeline'],
                                  'roots.csv': ['"4","2"', '"25","5"']}}},
            'fallback': 'self',
        },
    ],

    'quiz': [
        {'id': 'psq-objects', 'type': 'mcq',
         'prompt': 'What travels down a PowerShell pipeline?',
         'answer': 'Objects with typed properties.',
         'distractors': ['Lines of text, like bash.',
                         'JSON documents.',
                         'File handles.'],
         'teach': 'The whole module follows from this. It is why nothing has to '
                  'be parsed back out of formatted output.'},

        {'id': 'psq-eq', 'type': 'mcq',
         'prompt': 'How do you test equality in PowerShell?',
         'answer': '-eq',
         'distractors': ['==', '.eq()', '='],
         'teach': 'Symbols were taken: > is redirection. Hence the dashed '
                  'operators.'},

        {'id': 'psq-case', 'type': 'mcq',
         'prompt': 'Is `"ERROR" -eq "error"` true?',
         'answer': 'Yes; string comparison is case-insensitive by default.',
         'distractors': ['No, string comparison is exact.',
                         'Only inside Where-Object.',
                         'It raises a type error.'],
         'teach': 'The opposite of every other shell you know. Use -ceq when '
                  'case matters.'},

        {'id': 'psq-getmember', 'type': 'mcq',
         'prompt': 'The output shows eight columns. How many properties does '
                   'the object have?',
         'answer': 'Possibly many more; the display is chosen by a formatter.',
         'distractors': ['Exactly eight.',
                         'Eight, plus any you add with Select-Object.',
                         'It depends on the terminal width.'],
         'teach': 'Which is why Get-Member is the habit to build. Absence from '
                  'the display says nothing about absence from the object.'},

        {'id': 'psq-format-last', 'type': 'mcq',
         'prompt': 'Why must Format-Table be the last thing in a pipeline?',
         'answer': 'It destroys the objects and emits formatting instructions.',
         'distractors': ['It is slower than the alternatives.',
                         'It only reads the first ten items.',
                         'It buffers the whole pipeline.'],
         'teach': 'If your CSV export is full of empty columns, a Format-* is '
                  'upstream of it.'},

        {'id': 'psq-select-vs-format', 'type': 'mcq',
         'prompt': 'What is the difference between Select-Object and '
                   'Format-Table?',
         'answer': 'Select-Object shapes data you can keep piping; Format-Table '
                   'shapes display.',
         'distractors': ['They are equivalent; one is shorter.',
                         'Select-Object is for properties, Format-Table for '
                         'rows.',
                         'Format-Table is the newer name.'],
         'teach': 'They look similar and are not, which is the source of the '
                  'previous question\'s bug.'},

        {'id': 'psq-match-like', 'type': 'mcq',
         'prompt': 'Which operator takes a wildcard like `*.log`?',
         'answer': '-like',
         'distractors': ['-match', '-contains', '-in'],
         'teach': '-match takes a regex. Using the wrong one silently matches '
                  'nothing, which is the worst kind of wrong.'},

        {'id': 'psq-winevent-where', 'type': 'mcq',
         'prompt': 'Why is `Get-WinEvent -LogName Security | Where-Object Id -eq '
                   '4625` a bad idea on a busy server?',
         'answer': 'It transfers every event before filtering, which can take '
                   'many minutes.',
         'distractors': ['Where-Object cannot see the Id property.',
                         'It needs administrator rights and the other form does '
                         'not.',
                         'It only returns the most recent 1000 events.'],
         'teach': '-FilterHashtable pushes the filter into the log subsystem. '
                  'Same answer, wildly different runtime.'},

        {'id': 'psq-xpath-when', 'type': 'mcq',
         'prompt': 'When do you have to use -FilterXPath rather than '
                   '-FilterHashtable?',
         'answer': 'When filtering on a field inside the event data rather than '
                   'its metadata.',
         'distractors': ['Whenever there is more than one condition.',
                         'On remote machines only.',
                         'When the log is larger than a gigabyte.'],
         'teach': 'The hashtable covers log, id and time. It cannot see inside '
                  'EventData, and that is the line where you switch.'},

        {'id': 'psq-4625', 'type': 'mcq',
         'prompt': 'Which event ID is a failed logon?',
         'answer': '4625',
         'distractors': ['4624', '4688', '1102'],
         'teach': '4624 is a successful logon, 4688 a process creation, and '
                  '1102 is the security log being cleared, which is rarely '
                  'innocent.'},
    ],
}
