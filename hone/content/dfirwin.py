"""Windows and Sysmon DFIR triage: the events that matter, and how to filter.

The PowerShell module teaches the object pipeline and introduces `Get-WinEvent`.
This one is about the other half of that skill, which is a body of knowledge
rather than a syntax: **which events are worth looking at, what each one
actually proves, and how to filter a log with millions of records without
waiting an hour.**

Three things make this hard, and each gets a lesson. Event IDs are numerous,
badly named and mean different things in different channels. The filtering
interface has three layers with a large performance cliff between them, and
the slow one is the obvious one. And Sysmon, which is where most of the useful
detail lives, is not installed by default and is only as good as its
configuration.

**Verification.** Live `Get-WinEvent` needs Windows, and the trainer says so
rather than pretending. What it can do honestly is give you real event XML in
the sandbox and have you filter it with real PowerShell, because `pwsh` runs on
Linux and XPath over event XML is the same XPath either way. So the filter
expressions are verified for real, on this machine, and only the live cmdlet is
self-marked.

**Both directions.** The event map is as useful for building detections as for
reading them, and the lessons are written for someone who may be doing either.
"""

MODULE = {
    'id': 'dfirwin',
    'title': 'Windows and Sysmon DFIR',
    'group': 'Security',
    'blurb': 'Event IDs worth knowing, XPath filtering, Sysmon, and the artifact map.',
    'context': 'You are triaging Windows event data, at a PowerShell prompt.',
    'needs': ['pwsh'],
    'prereqs': ['powershell'],
    'adapter': 'pwshbox',
    'estimate': '4-5 hours',
    'order': 89,

    'lessons': [
        {
            'id': 'dw-channels',
            'title': 'Channels, providers, and where the log actually is',
            'concept':
                '`Get-WinEvent` is how you read Windows event records from a '
                'channel or a saved evtx. That is why the first skill is '
                'knowing which of the hundreds of channels holds the answer, '
                'and that an event ID only means something with its channel.\n\n'
                'Windows logging is not one log. It is hundreds of channels, '
                'each written by a provider, each with its own numbering, and '
                'the first skill is knowing which one holds the answer.\n\n'
                'The classic three are Security, System and Application. '
                'Security is the interesting one for most investigations and '
                'is also the one that needs auditing enabled before it '
                'records anything: a great deal of what people expect to find '
                'there is simply not being logged by default.\n\n'
                'Beyond those are the operational channels, named like '
                'Microsoft-Windows-Sysmon/Operational or '
                'Microsoft-Windows-PowerShell/Operational. These carry most '
                'of the detail that modern detection depends on, and they are '
                'where you look when the classic three are thin.\n\n'
                'The critical consequence of many channels is that **an event '
                'ID only means something together with its channel.** Event '
                'ID 1 in Sysmon is process creation. Event ID 1 in the System '
                'channel is something else entirely. Quoting an ID without '
                'its provider is the single most common source of confusion '
                'in write-ups.\n\n'
                'Logs are files, at C:\\Windows\\System32\\winevt\\Logs, and '
                'they can be copied off a machine and read elsewhere, which '
                'is what makes offline triage possible at all.',
            'examples': [
                {'label': 'What channels exist here',
                 'code': 'Get-WinEvent -ListLog * | Where-Object '
                         'RecordCount -gt 0',
                 'note': 'Hundreds of them. Filtering to non-empty ones makes '
                         'the list readable.'},
                {'label': 'Which providers write to Security',
                 'code': 'Get-WinEvent -ListProvider * | Where-Object '
                         '{ $_.LogLinks.LogName -contains "Security" }',
                 'note': 'Provider and channel are different things, and both '
                         'appear in filters.'},
                {'label': 'Read a saved log rather than a live one',
                 'code': 'Get-WinEvent -Path .\\Security.evtx -MaxEvents 10',
                 'note': '-Path takes an evtx file, which is how you triage a '
                         'copy on your own machine.'},
                {'label': 'Is anything even being recorded',
                 'code': 'Get-WinEvent -ListLog Security | Select-Object '
                         'RecordCount, MaximumSizeInBytes, IsEnabled',
                 'note': 'A small maximum size means old events are already '
                         'gone, which is a finding of its own.'},
            ],
            'misconceptions': [
                'An event ID is not unique across Windows. It only means '
                'something alongside its channel or provider.',
                'The Security log is not comprehensive by default. Most of '
                'the interesting auditing is off until someone turns it on.',
                'A log with a small maximum size silently discards the oldest '
                'events, so absence of evidence is often just rotation.',
            ],
            'try_it': [
                'List the channels on a Windows machine with more than zero '
                'records and count them.',
                'Check the maximum size of the Security log and work out how '
                'many hours it holds.',
            ],
            'next': 'dw-ids',
        },
        {
            'id': 'dw-ids',
            'title': 'The event IDs actually worth knowing',
            'concept':
                'A short list of event IDs is how you turn a huge log into '
                'evidence. That is why 4624, 4625, 4688, 7045, 1102 and 4104 '
                'are worth learning with what they prove, not as a numbered '
                'list.\n\n'
                '**Authentication.** 4624 is a successful logon and its Logon '
                'Type field is the important part: 2 is interactive at the '
                'console, 3 is network such as a file share, 10 is RemoteDesktop, '
                '5 is a service, 4 is batch. 4625 is a failed logon and its '
                'status codes distinguish a bad password from a disabled '
                'account. 4634 and 4647 are logoff. 4648 is a logon with '
                'explicit credentials, which is what runas and lateral '
                'movement look like.\n\n'
                '**Accounts and privilege.** 4720 account created, 4726 '
                'deleted, 4732 added to a security-enabled local group, 4728 '
                'to a global group. 4672 is special privileges assigned at '
                'logon, which in practice means an administrative logon '
                'happened.\n\n'
                '**Process and persistence.** 4688 is process creation, and '
                'it is worth far more once command line auditing is enabled, '
                'which is a separate policy setting. 7045 in System is a new '
                'service installed, which is a classic persistence signal. '
                '4698 is a scheduled task created.\n\n'
                '**Log integrity.** 1102 is the Security log being cleared, '
                'and 104 is another log being cleared. These are short lists '
                'and they matter enormously.\n\n'
                '**PowerShell.** 4104 in the PowerShell Operational channel '
                'is script block logging, and it records the actual code, '
                'deobfuscated. It is the single highest value modern source '
                'and it is off by default.\n\n'
                'Twenty IDs carry the weight. The next lesson is how to '
                'find them in a log of two million events without '
                'waiting twenty minutes.',
            'examples': [
                {'label': 'Failed logons, most recent first',
                 'code': 'Get-WinEvent -FilterHashtable @{LogName="Security"; '
                         'ID=4625} -MaxEvents 50',
                 'note': 'Read the Logon Type and the status code, not just '
                         'the count.'},
                {'label': 'Interactive logons only',
                 'code': 'Get-WinEvent -FilterHashtable @{LogName="Security"; '
                         'ID=4624} | Where-Object { $_.Properties[8].Value '
                         '-eq 2 }',
                 'note': 'Logon type lives in a numbered property, which is '
                         'why XPath filtering is usually nicer.'},
                {'label': 'Was the log cleared',
                 'code': 'Get-WinEvent -FilterHashtable @{LogName="Security"; '
                         'ID=1102}',
                 'note': 'One of the shortest and most significant queries '
                         'there is.'},
                {'label': 'What did PowerShell actually run',
                 'code': 'Get-WinEvent -FilterHashtable '
                         '@{LogName="Microsoft-Windows-PowerShell/Operational"; '
                         'ID=4104}',
                 'note': 'Script block logging records the code after '
                         'deobfuscation, which is why attackers dislike it.'},
            ],
            'misconceptions': [
                '4625 alone does not mean an attack. Read the count, the '
                'accounts, the source and the time distribution together.',
                '4688 without command line auditing tells you a process ran '
                'and not what it was told to do, which is most of the value.',
                'A missing 1102 does not prove the log was not tampered with. '
                'It proves it was not cleared through the normal interface.',
            ],
            'try_it': [
                'Find every 4624 on a machine you own and tabulate them by '
                'logon type.',
                'Check whether command line auditing and script block logging '
                'are enabled on a machine you administer.',
            ],
            'next': 'dw-filter',
        },
        {
            'id': 'dw-filter',
            'title': 'Three ways to filter, and the performance cliff',
            'concept':
                '`-FilterHashtable` and `-FilterXPath` are how you let the '
                'event log service discard events before PowerShell builds '
                'objects. That is why `Where-Object` on a two-million-event '
                'log is the slow way, and why XPath is the one that can ask '
                'for logon type 3.\n\n'
                '**Where-Object is the slow one.** It reads every event into '
                'PowerShell objects and then discards most of them. On a log '
                'with two million records that is two million objects '
                'constructed to keep fifty. It is also the one everybody '
                'reaches for first, because it reads naturally.\n\n'
                '**-FilterHashtable is fast**, because the filter is passed '
                'to the event log service and applied before anything is '
                'materialised. It takes LogName, ProviderName, ID, Level, '
                'StartTime, EndTime and Data, and covers most everyday '
                'questions.\n\n'
                '**-FilterXPath and -FilterXml are fast and precise.** They '
                'reach inside the event data, which the hashtable cannot do '
                'properly: filtering on "logon type equals 3" or "target user '
                'name equals admin" needs XPath. The syntax is where people '
                'give up, and it is worth pushing through because it is the '
                'only way to ask most real questions.\n\n'
                'The XPath shape is regular once you see it. System fields '
                'live under System, event specific fields under EventData/Data '
                'with a Name attribute, and the two are combined with and.',
            'examples': [
                {
                    'label': 'When the pretty output is hiding the field you want',
                    'code': '$event = Get-WinEvent -MaxEvents 1\n$event.ToXml()\n\nthe full event, every EventData field,\nwith the names the schema actually uses',
                    'note': 'The console view shows a rendered summary. ToXml gives you everything, which is how you find the field name to filter on next time.',
                },
                {'label': 'The slow way, which reads naturally',
                 'code': 'Get-WinEvent -LogName Security | Where-Object '
                         '{ $_.Id -eq 4625 }',
                 'note': 'Correct and glacial. It materialises the whole log '
                         'first.'},
                {'label': 'The fast everyday way',
                 'code': 'Get-WinEvent -FilterHashtable @{LogName="Security"; '
                         'ID=4625; StartTime=(Get-Date).AddDays(-1)}',
                 'note': 'Filtered by the service before anything reaches '
                         'PowerShell.'},
                {'label': 'Reaching into the event data',
                 'code': 'Get-WinEvent -LogName Security -FilterXPath '
                         '"*[System[EventID=4624] and '
                         'EventData[Data[@Name=\'LogonType\']=\'3\']]"',
                 'note': 'Network logons only. The hashtable cannot express '
                         'this properly.'},
                {'label': 'The same shape against a file',
                 'code': 'Get-WinEvent -Path .\\Security.evtx -FilterXPath '
                         '"*[System[EventID=1102]]"',
                 'note': 'XPath works on saved logs too, which is most of '
                         'offline triage.'},
            ],
            'misconceptions': [
                'Where-Object is not merely slower. On a large log it is the '
                'difference between seconds and half an hour.',
                '-FilterHashtable\'s Data key matches any data field, not a '
                'named one. Named fields need XPath.',
                'XPath here is not the full XPath standard. The event log '
                'service supports a documented subset.',
            ],
            'try_it': [
                'Time the same query with Where-Object and with '
                '-FilterHashtable on a busy log.',
                'Write an XPath that selects only logon type 10, and check it '
                'against a saved log.',
            ],
            'next': 'dw-sysmon',
        },
        {
            'id': 'dw-sysmon',
            'title': 'Sysmon: the detail Windows does not log by default',
            'concept':
                'Sysmon is a free Sysinternals driver that logs what the '
                'built-in auditing does not: full process creation with '
                'command lines and hashes, network connections with the '
                'process that made them, file creation times being changed, '
                'driver and image loads, registry changes, WMI subscriptions '
                'and named pipes.\n\n'
                'The event IDs worth knowing are short. **1** process create, '
                'with command line, parent, hashes. **3** network connection, '
                'with the process. **7** image loaded, which catches DLL side '
                'loading. **8** CreateRemoteThread, which is classic '
                'injection. **10** process access, which is how credential '
                'dumping against lsass shows up. **11** file create. **12**, '
                '**13** and **14** registry. **15** file stream created, '
                'which carries the download mark. **22** DNS query. **23** '
                'file delete.\n\n'
                'The thing to internalise is that **Sysmon is only as good as '
                'its configuration.** A default install logs almost '
                'everything and is useless from volume alone. The published '
                'configurations, SwiftOnSecurity\'s and Olaf Hartong\'s '
                'modular one, are what make it usable, and they work by '
                'excluding the known-normal rather than including the '
                'known-bad.\n\n'
                'Event 1 alone changes an investigation, because it gives you '
                'the parent process. A chain of winword.exe spawning '
                'cmd.exe spawning powershell.exe is a sentence, and nothing '
                'in the default logging tells it.',
            'examples': [
                {'label': 'Process creation with the full command line',
                 'code': 'Get-WinEvent -FilterHashtable '
                         '@{LogName="Microsoft-Windows-Sysmon/Operational"; '
                         'ID=1} -MaxEvents 20',
                 'note': 'Command line, parent, and hashes. This is the '
                         'single most useful event on Windows.'},
                {'label': 'Which process made that connection',
                 'code': 'Get-WinEvent -FilterHashtable '
                         '@{LogName="Microsoft-Windows-Sysmon/Operational"; '
                         'ID=3}',
                 'note': 'Sysmon 3 ties a network connection to the process, '
                         'which the firewall log does not.'},
                {'label': 'Install with a real configuration',
                 'code': 'sysmon64.exe -accepteula -i sysmonconfig.xml',
                 'note': 'The configuration is the product. A default install '
                         'is noise.'},
                {'label': 'Update the configuration later',
                 'code': 'sysmon64.exe -c sysmonconfig.xml',
                 'note': 'No reinstall needed, and worth doing as detections '
                         'change.'},
            ],
            'misconceptions': [
                'Sysmon is not an EDR. It logs, it does not block, and it '
                'has no console of its own.',
                'A default Sysmon install is not a good baseline. Volume '
                'alone makes it unusable without a curated configuration.',
                'Sysmon event 1 and Security event 4688 are not duplicates. '
                'Sysmon adds hashes, the parent chain and a GUID that ties '
                'events together.',
            ],
            'try_it': [
                'Read a published Sysmon configuration and find the section '
                'that excludes known-normal traffic.',
                'On a machine with Sysmon, find a process chain three levels '
                'deep using ParentProcessGuid.',
            ],
            'next': 'dw-artifacts',
        },
        {
            'id': 'dw-artifacts',
            'title': 'The artifact map beyond the event log',
            'concept':
                'Event logs are one source and they rotate. A great deal of '
                'what an investigation needs lives elsewhere on disk, and '
                'knowing the map is most of the speed.\n\n'
                '**Execution.** Prefetch in C:\\Windows\\Prefetch records that '
                'a program ran, when, and how many times, and survives the '
                'program being deleted. Shimcache and Amcache record '
                'execution or presence with different reliability and '
                'different well documented caveats. UserAssist in the '
                'registry records GUI program launches per user.\n\n'
                '**Persistence.** Run and RunOnce keys, scheduled tasks in '
                'C:\\Windows\\System32\\Tasks as XML, services in the '
                'registry, WMI event subscriptions, and startup folders. '
                'Autoruns from Sysinternals enumerates nearly all of it in '
                'one pass.\n\n'
                '**Files and downloads.** The Zone.Identifier alternate data '
                'stream marks a file as downloaded and often records where '
                'from. The MFT and the USN journal record file activity long '
                'after the files themselves are gone.\n\n'
                '**Accounts and network.** SAM and SYSTEM hives hold local '
                'accounts; SRUM records per-process network usage; the '
                'registry holds every network the machine has joined.\n\n'
                'The habit worth building is order. Volatile first if the '
                'machine is live, then the event logs, then the on-disk '
                'artifacts, and hash and record everything you copy as you '
                'go.\n\n'
                'The map is not an order. The next lesson is a triage '
                'order that finds things, which is where the map pays '
                'off.',
            'examples': [
                {'label': 'What ran, even if it is gone now',
                 'code': 'Get-ChildItem C:\\Windows\\Prefetch\\*.pf | '
                         'Sort-Object LastWriteTime -Descending | '
                         'Select-Object -First 20',
                 'note': 'Prefetch survives deletion of the executable, which '
                         'is exactly when you need it.'},
                {'label': 'Where did this file come from',
                 'code': 'Get-Content .\\installer.exe -Stream Zone.Identifier',
                 'note': 'The mark of the web, often with the referrer URL in '
                         'it.'},
                {'label': 'Persistence in the obvious place',
                 'code': 'Get-ItemProperty '
                         '"HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"',
                 'note': 'First place to look, and far from the only one.'},
                {'label': 'Scheduled tasks as files',
                 'code': 'Get-ChildItem C:\\Windows\\System32\\Tasks -Recurse '
                         '-File',
                 'note': 'They are XML on disk, so they can be read from a '
                         'copied image without the scheduler.'},
            ],
            'misconceptions': [
                'Prefetch does not prove what a program did, only that it '
                'ran, when, and how often.',
                'Shimcache is not a reliable execution artifact on its own. '
                'It can record presence without execution.',
                'Deleting a file does not remove the record of it. The MFT '
                'and the USN journal outlive the data.',
            ],
            'try_it': [
                'List the twenty most recent prefetch files on a Windows '
                'machine and match them against what you remember running.',
                'Find a downloaded file and read its Zone.Identifier stream.',
            ],
            'next': 'dw-triage',
        },
        {
            'id': 'dw-triage',
            'title': 'A triage order that finds things',
            'concept':
                'A fixed order of questions is how you triage a Windows host '
                'in an hour rather than a day. That is why the window, the '
                'logons, what ran, what persisted, what left, and what was '
                'hidden come before any deep dive.\n\n'
                '**Establish the window.** When did the thing happen, and how '
                'much log do you actually have either side of it. Check the '
                'log sizes before assuming coverage.\n\n'
                '**Who logged in.** 4624 with logon types, 4625 for failures, '
                '4648 for explicit credentials. Build a table of account, '
                'type, source and time. Most investigations turn on this '
                'table.\n\n'
                '**What ran.** Sysmon 1 if you have it, 4688 if not, and read '
                'the parent chains rather than the process names alone. An '
                'ordinary binary with an extraordinary parent is the signal.\n\n'
                '**What persisted.** New services 7045, scheduled tasks 4698, '
                'Run keys, and anything created in the window you '
                'established.\n\n'
                '**What left.** Sysmon 3 for connections with process names, '
                'Sysmon 22 for DNS, and firewall logs if they exist.\n\n'
                '**What was hidden.** 1102 and 104 for cleared logs, and any '
                'gap in the timeline that nobody can explain.\n\n'
                'Throughout, the discipline is the same as file triage: work '
                'on copies, hash what you collect, and write down what you '
                'ran and when. An investigation you cannot reproduce is a '
                'story.',
            'examples': [
                {'label': 'Bound the question first',
                 'code': 'Get-WinEvent -ListLog Security,System,Application | '
                         'Select-Object LogName, RecordCount, '
                         'MaximumSizeInBytes',
                 'note': 'Find out what coverage you have before you go '
                         'looking for absence of evidence.'},
                {'label': 'The logon table',
                 'code': 'Get-WinEvent -FilterHashtable @{LogName="Security"; '
                         'ID=4624; StartTime=$start; EndTime=$end} | '
                         'Select-Object TimeCreated, '
                         '@{n="Type";e={$_.Properties[8].Value}}, '
                         '@{n="User";e={$_.Properties[5].Value}}',
                 'note': 'Calculated properties turn positional data into a '
                         'readable table.'},
                {'label': 'Everything in the window, one channel at a time',
                 'code': 'Get-WinEvent -FilterHashtable @{LogName="Security"; '
                         'StartTime=$start; EndTime=$end} | '
                         'Group-Object Id | Sort-Object Count -Descending',
                 'note': 'Grouping by ID first shows the shape of the window '
                         'before you read anything in detail.'},
                {'label': 'Export for someone else to read',
                 'code': 'Get-WinEvent -FilterHashtable @{LogName="Security"; '
                         'ID=4625} | Export-Csv -NoTypeInformation '
                         'failed-logons.csv',
                 'note': 'CSV for humans, Export-Clixml when you need the '
                         'objects back intact.'},
            ],
            'misconceptions': [
                'Absence of an event is not absence of the activity. Check '
                'whether the auditing was on and whether the log rotated.',
                'A suspicious process name is weaker evidence than an '
                'ordinary process with an unusual parent.',
                'Working on the live machine is convenient and destroys '
                'volatile evidence in the order you touch it.',
            ],
            'try_it': [
                'Pick any hour on a machine you own and group every Security '
                'event in it by ID.',
                'Build a logon table for a day and see how many types appear.',
            ],
            'next': 'dw-limits',
        },
        {
            'id': 'dw-limits',
            'title': 'Reading Linux-side, and what does not transfer',
            'concept':
                '`evtx_dump` and `python-evtx` are how you read a Windows '
                'evtx from Linux. That is why `Get-WinEvent` is a Windows-only '
                'cmdlet, and why the XPath and the event IDs are the half of '
                'this skill that transfers.\n\n'
                'PowerShell itself runs on Linux and macOS, so the pipeline, '
                'the object model, Select-Object, Where-Object, Group-Object '
                'and Export-Csv all work anywhere. What does not is anything '
                'that reads the Windows event log service: `Get-WinEvent` and '
                '`Get-EventLog` are Windows only, because the thing they talk '
                'to is a Windows service.\n\n'
                'What transfers is the data. An evtx file is a file, and '
                'there are cross platform readers: `evtx_dump` from the '
                'Rust evtx crate turns it into XML or JSON, and '
                '`python-evtx` does the same. Once it is XML or JSON, every '
                'tool in this roster applies: XPath in PowerShell, jq if you '
                'converted to JSON, grep and awk for a quick count.\n\n'
                'That is why the XPath skill is the durable half of this '
                'module. The cmdlet is a Windows detail; the filter '
                'expression is a fact about the event schema and works '
                'wherever the XML goes.\n\n'
                'The other half that transfers is the knowledge: which IDs '
                'matter and what they prove is the same on any platform you '
                'read them from.',
            'examples': [
                {'label': 'Turn an evtx into something portable',
                 'code': 'evtx_dump -o jsonl Security.evtx > security.jsonl',
                 'note': 'JSON lines, which jq reads happily and which every '
                         'other tool in this roster can handle.'},
                {'label': 'Then use the tools you already have',
                 'code': 'jq -r \'select(.Event.System.EventID == 4625) | '
                         '.Event.EventData.TargetUserName\' security.jsonl | '
                         'sort | uniq -c | sort -rn',
                 'note': 'Failed logons per account, on Linux, with no '
                         'Windows involved at all.'},
                {'label': 'XPath against XML, in pwsh anywhere',
                 'code': 'Select-Xml -Path events.xml -XPath '
                         '"//Event[System/EventID=4625]"',
                 'note': 'The same filter shape as Get-WinEvent, running on '
                         'any platform.'},
            ],
            'misconceptions': [
                'PowerShell on Linux does not give you Get-WinEvent. The '
                'shell is portable, the Windows service it talks to is not.',
                'Converting an evtx to JSON does not lose the structure. It '
                'changes the encoding, and the fields survive.',
                'Knowing the cmdlet is the smaller half of this skill. '
                'Knowing which IDs matter is what transfers.',
            ],
            'try_it': [
                'Convert an evtx file to JSON lines and count events by ID '
                'with jq.',
                'Write the same filter twice, once as Get-WinEvent XPath and '
                'once as a jq select.',
            ],
            'next': None,
        },
    ],

    'drills': [
        {'id': 'dwd-listlog', 'type': 'command',
         'prompt': 'List every event channel that has at least one record.',
         'answer': 'Get-WinEvent -ListLog * | Where-Object RecordCount -gt 0',
         'teach': 'Hundreds of channels exist. The non-empty ones are the '
                  'only readable list.'},
        {'id': 'dwd-logsize', 'type': 'command',
         'prompt': 'Show the record count and maximum size of the Security log.',
         'answer': 'Get-WinEvent -ListLog Security | Select-Object '
                   'RecordCount, MaximumSizeInBytes',
         'teach': 'Check coverage before concluding anything from absence of '
                  'evidence.'},
        {'id': 'dwd-path', 'type': 'command',
         'prompt': 'Read the first ten events from the saved file Security.evtx.',
         'answer': 'Get-WinEvent -Path .\\Security.evtx -MaxEvents 10',
         'teach': '-Path reads a copied log, which is how offline triage '
                  'works at all.'},
        {'id': 'dwd-4625', 'type': 'command',
         'prompt': 'Get the 50 most recent failed logons from the Security log.',
         'answer': 'Get-WinEvent -FilterHashtable @{LogName="Security"; '
                   'ID=4625} -MaxEvents 50',
         'teach': '4625 is a failed logon. Read the type and status, not just '
                  'the count.'},
        {'id': 'dwd-4624', 'type': 'command',
         'prompt': 'Get successful logons from the Security log with a hashtable filter.',
         'answer': 'Get-WinEvent -FilterHashtable @{LogName="Security"; '
                   'ID=4624}',
         'teach': '4624, and its Logon Type field is where the meaning '
                  'actually is.'},
        {'id': 'dwd-1102', 'type': 'command',
         'prompt': 'Find any record of the Security log being cleared.',
         'answer': 'Get-WinEvent -FilterHashtable @{LogName="Security"; '
                   'ID=1102}',
         'teach': 'One of the shortest and most significant queries there '
                  'is.'},
        {'id': 'dwd-7045', 'type': 'command',
         'prompt': 'Find newly installed services in the System log.',
         'answer': 'Get-WinEvent -FilterHashtable @{LogName="System"; '
                   'ID=7045}',
         'teach': 'A classic persistence signal, and a short list on most '
                  'machines.'},
        {'id': 'dwd-4104', 'type': 'command',
         'prompt': 'Get PowerShell script block logging events.',
         'answer': 'Get-WinEvent -FilterHashtable '
                   '@{LogName="Microsoft-Windows-PowerShell/Operational"; '
                   'ID=4104}',
         'teach': 'Records the code after deobfuscation. The highest value '
                  'modern source, and off by default.'},
        {'id': 'dwd-sysmon1', 'type': 'command',
         'prompt': 'Get the 20 most recent Sysmon process creation events.',
         'answer': 'Get-WinEvent -FilterHashtable '
                   '@{LogName="Microsoft-Windows-Sysmon/Operational"; ID=1} '
                   '-MaxEvents 20',
         'teach': 'Command line, parent and hashes. The single most useful '
                  'event on Windows.'},
        {'id': 'dwd-sysmon3', 'type': 'command',
         'prompt': 'Get Sysmon network connection events.',
         'answer': 'Get-WinEvent -FilterHashtable '
                   '@{LogName="Microsoft-Windows-Sysmon/Operational"; ID=3}',
         'teach': 'Ties a connection to the process that made it, which the '
                  'firewall log cannot.'},
        {'id': 'dwd-timewindow', 'type': 'command',
         'prompt': 'Get Security events from the last 24 hours only.',
         'answer': 'Get-WinEvent -FilterHashtable @{LogName="Security"; '
                   'StartTime=(Get-Date).AddDays(-1)}',
         'teach': 'StartTime and EndTime in the hashtable are applied by the '
                  'service, so they are cheap.'},
        {'id': 'dwd-xpath-id', 'type': 'command',
         'prompt': 'Select event ID 4625 from the Security log using XPath.',
         'answer': 'Get-WinEvent -LogName Security -FilterXPath '
                   '"*[System[EventID=4625]]"',
         'teach': 'System fields live under System. This is the shape every '
                  'event log XPath starts from.'},
        {'id': 'dwd-xpath-data', 'type': 'command',
         'prompt': 'Select 4624 events whose LogonType is 3, using XPath.',
         'answer': 'Get-WinEvent -LogName Security -FilterXPath '
                   '"*[System[EventID=4624] and '
                   'EventData[Data[@Name=\'LogonType\']=\'3\']]"',
         'teach': 'Named event data needs XPath. The hashtable cannot reach '
                  'a specific field.'},
        {'id': 'dwd-xpath-user', 'type': 'command',
         'prompt': 'Select events where TargetUserName is admin, using XPath.',
         'answer': 'Get-WinEvent -LogName Security -FilterXPath '
                   '"*[EventData[Data[@Name=\'TargetUserName\']=\'admin\']]"',
         'teach': 'The EventData half can stand alone when you do not care '
                  'which event ID it was.'},
        {'id': 'dwd-selectxml', 'type': 'command',
         'prompt': 'Select 4625 events from events.xml with Select-Xml.',
         'answer': 'Select-Xml -Path events.xml -XPath '
                   '"//Event[System/EventID=4625]"',
         'teach': 'The portable form: works on any platform, on XML exported '
                  'from anywhere.'},
        {'id': 'dwd-group', 'type': 'command',
         'prompt': 'Group Security events by event ID, most frequent first.',
         'answer': 'Get-WinEvent -LogName Security | Group-Object Id | '
                   'Sort-Object Count -Descending',
         'teach': 'Grouping first shows the shape of a window before you read '
                  'anything in detail.'},
        {'id': 'dwd-message', 'type': 'command',
         'prompt': 'Show the time and full message of the last five Security events.',
         'answer': 'Get-WinEvent -LogName Security -MaxEvents 5 | '
                   'Select-Object TimeCreated, Message',
         'teach': 'Message is the rendered text. The structured fields are in '
                  'Properties and in the XML.'},
        {'id': 'dwd-toxml', 'type': 'command',
         'prompt': 'Convert an event object to its raw XML.',
         'answer': '$event.ToXml()',
         'teach': 'Every event is XML underneath, and reading it is how you '
                  'find the field names XPath needs.'},
        {'id': 'dwd-csv', 'type': 'command',
         'prompt': 'Export failed logon events to failed.csv without type '
                   'information.',
         'answer': 'Get-WinEvent -FilterHashtable @{LogName="Security"; '
                   'ID=4625} | Export-Csv -NoTypeInformation failed.csv',
         'teach': 'CSV for humans. Export-Clixml when you need the objects '
                  'back with their types.'},
        {'id': 'dwd-prefetch', 'type': 'command',
         'prompt': 'List the 20 most recently written prefetch files.',
         'answer': 'Get-ChildItem C:\\Windows\\Prefetch\\*.pf | Sort-Object '
                   'LastWriteTime -Descending | Select-Object -First 20',
         'teach': 'Prefetch survives the executable being deleted, which is '
                  'exactly when you want it.'},
        {'id': 'dwd-zoneid', 'type': 'command',
         'prompt': 'Read the download marker stream on installer.exe.',
         'answer': 'Get-Content .\\installer.exe -Stream Zone.Identifier',
         'teach': 'The mark of the web, and often the referring URL with it.'},
        {'id': 'dwd-runkey', 'type': 'command',
         'prompt': 'Read the machine-wide Run key from the registry.',
         'answer': 'Get-ItemProperty '
                   '"HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"',
         'teach': 'The first place to look for persistence, and far from the '
                  'only one.'},
        {'id': 'dwd-tasks', 'type': 'command',
         'prompt': 'List every scheduled task file on disk.',
         'answer': 'Get-ChildItem C:\\Windows\\System32\\Tasks -Recurse -File',
         'teach': 'They are XML on disk, readable from a copied image with no '
                  'scheduler involved.'},
        {'id': 'dwd-sysmon-install', 'type': 'command',
         'prompt': 'Install Sysmon with the configuration file sysmonconfig.xml.',
         'answer': 'sysmon64.exe -accepteula -i sysmonconfig.xml',
         'teach': 'The configuration is the product. A default install is '
                  'volume without signal.'},
        {'id': 'dwd-sysmon-config', 'type': 'command',
         'prompt': 'Update a running Sysmon with a new configuration.',
         'answer': 'sysmon64.exe -c sysmonconfig.xml',
         'teach': 'No reinstall needed, and worth doing whenever detections '
                  'change.'},
        {'id': 'dwd-evtxdump', 'type': 'command',
         'prompt': 'Convert Security.evtx to JSON lines in security.jsonl.',
         'answer': 'evtx_dump -o jsonl Security.evtx > security.jsonl',
         'teach': 'Once it is JSON, jq and every other tool in this roster '
                  'applies, with no Windows involved.'},
        {'id': 'dwd-jq-4625', 'type': 'command',
         'prompt': 'Count failed logons per account in security.jsonl with jq.',
         'answer': 'jq -r \'select(.Event.System.EventID == 4625) | '
                   '.Event.EventData.TargetUserName\' security.jsonl | sort | '
                   'uniq -c | sort -rn',
         'teach': 'The knowledge transfers even when the cmdlet does not. '
                  'This is the same question on Linux.'},
    ],

    'challenges': [
        {
            'id': 'dwc-xpath-id',
            'title': 'Filter event XML by ID, for real',
            'goal': 'Write and run an XPath that selects one event ID out of '
                    'a log, using PowerShell on this machine.',
            'setup': {'kind': 'pwshbox', 'tree': {
                'events.xml':
                    '<Events>\n'
                    '<Event><System><EventID>4624</EventID>'
                    '<Computer>WS01</Computer></System>'
                    '<EventData><Data Name="TargetUserName">sage</Data>'
                    '<Data Name="LogonType">2</Data></EventData></Event>\n'
                    '<Event><System><EventID>4625</EventID>'
                    '<Computer>WS01</Computer></System>'
                    '<EventData><Data Name="TargetUserName">admin</Data>'
                    '<Data Name="LogonType">3</Data></EventData></Event>\n'
                    '<Event><System><EventID>4625</EventID>'
                    '<Computer>WS02</Computer></System>'
                    '<EventData><Data Name="TargetUserName">admin</Data>'
                    '<Data Name="LogonType">3</Data></EventData></Event>\n'
                    '<Event><System><EventID>1102</EventID>'
                    '<Computer>WS01</Computer></System>'
                    '<EventData><Data Name="SubjectUserName">sage</Data>'
                    '</EventData></Event>\n'
                    '</Events>\n',
            }},
            'solution': {'shell':
                'pwsh -NoProfile -Command \'(Select-Xml -Path events.xml '
                '-XPath "//Event[System/EventID=4625]").Count | '
                'Set-Content failed-count.txt; '
                'Select-Xml -Path events.xml -XPath '
                '"//Event[System/EventID=1102]" | ForEach-Object '
                '{ $_.Node.System.Computer } | Set-Content cleared-on.txt\''},
            'steps': [
                {'instruction': 'Read events.xml. It holds four events across '
                                'two computers.',
                 'hint': 'cat events.xml'},
                {'instruction': 'Count the failed logons, 4625, and write the '
                                'number to failed-count.txt.',
                 'hint': '(Select-Xml -Path events.xml -XPath '
                         '"//Event[System/EventID=4625]").Count'},
                {'instruction': 'Find which computer had its log cleared, '
                                'event 1102, and write its name to '
                                'cleared-on.txt.',
                 'hint': 'Select-Xml ... | ForEach-Object '
                         '{ $_.Node.System.Computer }'},
            ],
            'free': 'Produce failed-count.txt holding the number of 4625 '
                    'events, and cleared-on.txt naming the computer with an '
                    '1102.',
            'verify': {'kind': 'pwshbox', 'expect': {
                'file_contains': {'failed-count.txt': '2',
                                  'cleared-on.txt': 'WS01'}}},
            'fallback': 'self',
        },
        {
            'id': 'dwc-xpath-data',
            'title': 'Reach inside the event data',
            'goal': 'Filter on a named field rather than an event ID, which '
                    'is the thing the hashtable filter cannot do.',
            'setup': {'kind': 'pwshbox', 'tree': {
                'events.xml':
                    '<Events>\n'
                    '<Event><System><EventID>4624</EventID></System>'
                    '<EventData><Data Name="TargetUserName">sage</Data>'
                    '<Data Name="LogonType">2</Data></EventData></Event>\n'
                    '<Event><System><EventID>4624</EventID></System>'
                    '<EventData><Data Name="TargetUserName">svc_backup</Data>'
                    '<Data Name="LogonType">3</Data></EventData></Event>\n'
                    '<Event><System><EventID>4624</EventID></System>'
                    '<EventData><Data Name="TargetUserName">attacker</Data>'
                    '<Data Name="LogonType">10</Data></EventData></Event>\n'
                    '<Event><System><EventID>4624</EventID></System>'
                    '<EventData><Data Name="TargetUserName">sage</Data>'
                    '<Data Name="LogonType">10</Data></EventData></Event>\n'
                    '</Events>\n',
            }},
            'solution': {'shell':
                'pwsh -NoProfile -Command \'Select-Xml -Path events.xml '
                '-XPath "//Event[EventData/Data[@Name=\'"\'"\'LogonType\'"\'"\']=10]" '
                '| ForEach-Object { ($_.Node.EventData.Data | '
                'Where-Object { $_.Name -eq "TargetUserName" })."#text" } | '
                'Set-Content rdp-users.txt\''},
            'steps': [
                {'instruction': 'Every event here is a 4624, so the ID tells '
                                'you nothing. The LogonType field does.'},
                {'instruction': 'Select only the events whose LogonType is '
                                '10, which is RemoteDesktop.',
                 'hint': '-XPath "//Event[EventData/Data[@Name=\'LogonType\']=10]"'},
                {'instruction': 'Write the TargetUserName of each into '
                                'rdp-users.txt, one per line.'},
            ],
            'free': 'Produce rdp-users.txt listing the usernames of every '
                    'logon whose type was 10.',
            'verify': {'kind': 'pwshbox', 'expect': {
                'file_contains': {'rdp-users.txt': ['attacker', 'sage']},
                'file_lacks': {'rdp-users.txt': 'svc_backup'}}},
            'fallback': 'self',
        },
        {
            'id': 'dwc-count-by-id',
            'title': 'Shape the window before reading it',
            'goal': 'Group a set of events by ID and count them, which is the '
                    'first thing to do with any unfamiliar log.',
            'setup': {'kind': 'pwshbox', 'tree': {
                'events.xml':
                    '<Events>\n'
                    '<Event><System><EventID>4624</EventID></System></Event>\n'
                    '<Event><System><EventID>4625</EventID></System></Event>\n'
                    '<Event><System><EventID>4625</EventID></System></Event>\n'
                    '<Event><System><EventID>4625</EventID></System></Event>\n'
                    '<Event><System><EventID>4688</EventID></System></Event>\n'
                    '<Event><System><EventID>7045</EventID></System></Event>\n'
                    '</Events>\n',
            }},
            'solution': {'shell':
                'pwsh -NoProfile -Command \'Select-Xml -Path events.xml '
                '-XPath "//Event" | ForEach-Object '
                '{ $_.Node.System.EventID } | Group-Object | '
                'Sort-Object Count -Descending | ForEach-Object '
                '{ "$($_.Count) $($_.Name)" } | Set-Content by-id.txt\''},
            'steps': [
                {'instruction': 'Select every Event node and pull out its '
                                'EventID.',
                 'hint': 'Select-Xml -Path events.xml -XPath "//Event" | '
                         'ForEach-Object { $_.Node.System.EventID }'},
                {'instruction': 'Group them and sort by count, most frequent '
                                'first.',
                 'hint': 'Group-Object | Sort-Object Count -Descending'},
                {'instruction': 'Write lines of "count id" to by-id.txt.',
                 'hint': 'ForEach-Object { "$($_.Count) $($_.Name)" }'},
            ],
            'free': 'Produce by-id.txt with one line per event ID, counted '
                    'and sorted with the most frequent first.',
            'verify': {'kind': 'pwshbox', 'expect': {
                'file_contains': {'by-id.txt': ['3 4625', '1 7045']}}},
            'fallback': 'self',
        },
        {
            'id': 'dwc-jq-crossover',
            'title': 'Answer the same question on the Linux side',
            'goal': 'Take event data as JSON and answer a Windows question '
                    'with jq, proving the knowledge is the portable part.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'events.jsonl':
                    '{"Event":{"System":{"EventID":4625},'
                    '"EventData":{"TargetUserName":"admin"}}}\n'
                    '{"Event":{"System":{"EventID":4625},'
                    '"EventData":{"TargetUserName":"admin"}}}\n'
                    '{"Event":{"System":{"EventID":4625},'
                    '"EventData":{"TargetUserName":"root"}}}\n'
                    '{"Event":{"System":{"EventID":4624},'
                    '"EventData":{"TargetUserName":"sage"}}}\n',
            }},
            'solution': {'shell':
                "jq -r 'select(.Event.System.EventID == 4625) | "
                ".Event.EventData.TargetUserName' events.jsonl | sort | "
                "uniq -c | sort -rn > failed-by-user.txt"},
            'steps': [
                {'instruction': 'Select only the 4625 records and pull out '
                                'the target username.',
                 'hint': "jq -r 'select(.Event.System.EventID == 4625) | "
                         ".Event.EventData.TargetUserName' events.jsonl"},
                {'instruction': 'Count them per account, most frequent first, '
                                'into failed-by-user.txt.',
                 'hint': 'sort | uniq -c | sort -rn'},
                {'instruction': 'Note that this is the same investigation '
                                'question, on a machine with no Windows on '
                                'it at all.'},
            ],
            'free': 'Produce failed-by-user.txt counting failed logons per '
                    'account from the JSON event data, most frequent first.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'failed-by-user.txt': ['2 admin', '1 root']},
                'file_lacks': {'failed-by-user.txt': 'sage'}}},
            'fallback': 'self',
        },
        {
            'id': 'dwc-logon-table',
            'title': 'Build the logon table',
            'goal': 'Turn raw logon events into the table that most '
                    'investigations actually turn on: who, what type, and '
                    'from where.',
            'setup': {'kind': 'pwshbox', 'tree': {
                'logons.xml':
                    '<Events>\n'
                    '<Event><System><EventID>4624</EventID></System>'
                    '<EventData><Data Name="TargetUserName">sage</Data>'
                    '<Data Name="LogonType">2</Data>'
                    '<Data Name="IpAddress">-</Data></EventData></Event>\n'
                    '<Event><System><EventID>4624</EventID></System>'
                    '<EventData><Data Name="TargetUserName">svc_sql</Data>'
                    '<Data Name="LogonType">5</Data>'
                    '<Data Name="IpAddress">-</Data></EventData></Event>\n'
                    '<Event><System><EventID>4624</EventID></System>'
                    '<EventData><Data Name="TargetUserName">helpdesk</Data>'
                    '<Data Name="LogonType">10</Data>'
                    '<Data Name="IpAddress">10.0.0.44</Data></EventData></Event>\n'
                    '</Events>\n',
            }},
            'solution': {'shell':
                'pwsh -NoProfile -Command \'Select-Xml -Path logons.xml '
                '-XPath "//Event" | ForEach-Object { $d = $_.Node.EventData.Data; '
                '$u = ($d | Where-Object Name -eq "TargetUserName")."#text"; '
                '$t = ($d | Where-Object Name -eq "LogonType")."#text"; '
                '$i = ($d | Where-Object Name -eq "IpAddress")."#text"; '
                '"$u,$t,$i" } | Set-Content logon-table.csv\''},
            'steps': [
                {'instruction': 'For each event, pull out TargetUserName, '
                                'LogonType and IpAddress.',
                 'hint': '$d = $_.Node.EventData.Data; ($d | Where-Object '
                         'Name -eq "TargetUserName")."#text"'},
                {'instruction': 'Write one comma separated line per logon to '
                                'logon-table.csv.'},
                {'instruction': 'Read the result. Type 10 with a real IP '
                                'address is the row worth asking about.'},
            ],
            'free': 'Produce logon-table.csv with one line per logon giving '
                    'the username, the logon type and the source address.',
            'verify': {'kind': 'pwshbox', 'expect': {
                'file_contains': {'logon-table.csv': ['sage,2', 'svc_sql,5',
                                                      'helpdesk,10,10.0.0.44']}}},
            'fallback': 'self',
        },
        {
            'id': 'dwc-real-windows',
            'title': 'Do it on a real Windows machine',
            'goal': 'Everything above ran on canned XML. Live event logs need '
                    'Windows, so this one is on your honour.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'On a Windows machine you administer, check '
                                'the size and record count of the Security '
                                'log and work out how many hours it holds.'},
                {'instruction': 'Build a logon table for the last day with a '
                                'hashtable filter and calculated properties.',
                 'hint': 'Get-WinEvent -FilterHashtable @{LogName="Security"; '
                         'ID=4624; StartTime=(Get-Date).AddDays(-1)}'},
                {'instruction': 'Check whether command line auditing and '
                                'script block logging are enabled. If not, '
                                'note what you are missing.'},
                {'instruction': 'Time the same query with Where-Object and '
                                'with -FilterHashtable, and write down the '
                                'ratio.'},
                {'instruction': 'If Sysmon is installed, find a process chain '
                                'three levels deep. If not, read a published '
                                'configuration and note what it excludes.'},
            ],
            'free': 'On a real Windows machine: measure your log coverage, '
                    'build a logon table, check whether the high value '
                    'auditing is on, and compare filter performance.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
    ],

    'quiz': [
        {'id': 'dwq-id-context', 'type': 'mcq',
         'prompt': 'A write-up says "look for event ID 1". What is missing?',
         'answer': 'The channel or provider, since IDs are only unique within '
                   'one.',
         'distractors': ['The severity level to filter on.',
                         'The time window to search.',
                         'Whether to use Get-WinEvent or Get-EventLog.'],
         'teach': 'Sysmon 1 is process creation. System 1 is something else '
                  'entirely. The ID alone is not an identifier.'},
        {'id': 'dwq-where-object', 'type': 'mcq',
         'prompt': 'Why is Get-WinEvent -LogName Security | Where-Object '
                   '{$_.Id -eq 4625} so slow?',
         'answer': 'Every event is read and turned into an object before any '
                   'are discarded.',
         'distractors': ['Where-Object cannot use the log index.',
                         'The pipeline serialises objects to disk between '
                         'stages.',
                         'The Security log is encrypted and must be '
                         'decrypted per event.'],
         'teach': '-FilterHashtable pushes the filter down to the event log '
                  'service, so nothing unwanted is ever materialised.'},
        {'id': 'dwq-xpath-need', 'type': 'mcq',
         'prompt': 'You need only logon type 3 events. Why will '
                   '-FilterHashtable not do?',
         'answer': 'It cannot filter on a named field inside the event data.',
         'distractors': ['It cannot filter on event ID and a field at the '
                         'same time.',
                         'It only accepts one key per query.',
                         'Logon type is not recorded in the event data.'],
         'teach': 'The Data key matches any field, not a named one. Named '
                  'fields are what XPath is for.'},
        {'id': 'dwq-4624-type', 'type': 'mcq',
         'prompt': 'A 4624 event has Logon Type 10. What does that mean?',
         'answer': 'A RemoteDesktop logon.',
         'distractors': ['A service starting under that account.',
                         'A network logon such as a file share.',
                         'An interactive logon at the physical console.'],
         'teach': '2 interactive, 3 network, 4 batch, 5 service, 10 '
                  'RemoteDesktop. The type carries most of the meaning.'},
        {'id': 'dwq-1102', 'type': 'mcq',
         'prompt': 'What is event 1102 in the Security log?',
         'answer': 'The Security log was cleared.',
         'distractors': ['An account was locked out.',
                         'The audit policy was changed.',
                         'A privileged logon occurred.'],
         'teach': 'A very short list on a healthy machine, and one of the '
                  'highest signal queries you can run.'},
        {'id': 'dwq-4688', 'type': 'mcq',
         'prompt': 'Why is 4688 often less useful than people expect?',
         'answer': 'Command line auditing is a separate setting, and without '
                   'it you get the binary but not its arguments.',
         'distractors': ['It only records processes started by '
                         'administrators.',
                         'It is written to the System log, which rotates '
                         'faster.',
                         'It is superseded by 4624 on modern Windows.'],
         'teach': 'The arguments are usually the interesting part. Sysmon 1 '
                  'gives them plus the parent and hashes.'},
        {'id': 'dwq-sysmon-config', 'type': 'mcq',
         'prompt': 'What is the main problem with a default Sysmon install?',
         'answer': 'It logs so much that the volume makes it unusable.',
         'distractors': ['It logs too little to be worth having.',
                         'It conflicts with the built-in audit policy.',
                         'It cannot record command lines without extra '
                         'configuration.'],
         'teach': 'The configuration is the product. Published ones work by '
                  'excluding known-normal rather than listing known-bad.'},
        {'id': 'dwq-getwinevent-linux', 'type': 'mcq',
         'prompt': 'You have PowerShell on Linux and an evtx file. Can you use '
                   'Get-WinEvent?',
         'answer': 'No. Convert the evtx to XML or JSON and filter that '
                   'instead.',
         'distractors': ['Yes, with -Path, since the file is self '
                         'contained.',
                         'Yes, after installing the Windows compatibility '
                         'module.',
                         'Only for the Security channel, which is portable.'],
         'teach': 'The cmdlet talks to a Windows service. evtx_dump plus jq, '
                  'or Select-Xml over the XML, does the same job anywhere.'},
        {'id': 'dwq-prefetch', 'type': 'mcq',
         'prompt': 'What does a prefetch file prove?',
         'answer': 'That the program ran, when, and roughly how often.',
         'distractors': ['What the program did while it ran.',
                         'That the program is still installed.',
                         'Which user account launched it.'],
         'teach': 'It survives the executable being deleted, which is exactly '
                  'the case where you need it.'},
        {'id': 'dwq-absence', 'type': 'mcq',
         'prompt': 'You find no 4625 events at all for the day in question. '
                   'What should you check first?',
         'answer': 'Whether the auditing was enabled and whether the log '
                   'rotated.',
         'distractors': ['Whether the account was disabled.',
                         'Whether the attacker used a network logon '
                         'instead.',
                         'Whether the events went to the System log.'],
         'teach': 'Absence of evidence is the most misread result in this '
                  'work. Establish coverage before drawing conclusions.'},
    ],
}
