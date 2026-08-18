"""tcpdump: filter syntax, and the contrast nobody teaches explicitly.

**Scope is drawn tightly at filters.** Protocol analysis is Wireshark's course,
not this one, and trying to cover both would produce a module that teaches
neither. What is here is the thing that actually blocks people: writing a
filter that captures what you meant.

**The central contrast is capture filters versus display filters.** They are
two different languages that look similar enough to be confused constantly:

    tcp port 443        BPF, used by tcpdump and by -f in Wireshark
    tcp.port == 443     Wireshark display filter syntax

Nobody teaches this difference on purpose, so everybody learns it by writing
the wrong one into the wrong box. This module says it in lesson one and repeats
it in the quiz.

**Filters are now graded by running them.** This module shipped content-only
on the reasoning that D1 forbids capturing traffic, which is still true and
still observed: nothing here opens an interface. What that reasoning missed is
that a capture file can be *written* rather than captured, so `pcapgen` builds
one and the `pcap` adapter runs your filter against it. Both languages are
graded, in the tool that owns each: `tcpdump -r` for capture filters,
`tshark -r -Y` for display filters.

That turns the module's central claim into something the tools demonstrate
rather than something this file asserts. Type `tcp.port == 443` into a capture
drill and tcpdump refuses it in its own words; type the same string into the
next drill and it passes. Nobody argues with that.

**What is still not checkable, and still says so.** Capturing needs privileges
and an interface, so the live-capture challenge remains self-marked: no
fixture makes `-i any` honest. Grading is by which packets a filter selects,
never by its text, so every correct spelling passes.
"""

MODULE = {
    'id': 'tcpdump',
    'title': 'tcpdump',
    'group': 'Network',
    'blurb': 'BPF filters, and why display filters are a different language.',
    'context': 'You are at a root shell on a machine whose traffic you are allowed to capture.',
    'needs': ('tcpdump', 'tshark'),
    'prereqs': ['ssh'],
    # Filters are run against a generated capture file. Capturing traffic is
    # still outside D1 and still not done: the fixture is written, not caught.
    'adapter': 'pcap',
    'estimate': '3-5 hours',
    'order': 57,

    'lessons': [
        {
            'id': 'td-what',
            'title': 'What a packet is, and what capturing means',
            'next': 'td-two-languages',
            'concept': (
                'tcpdump is how you print the packets that actually crossed '
                'the wire. That is why a capture settles what logs cannot: '
                'whether a request left, whether it was answered, and whether '
                'the thing that answered was the one you asked. Everything a '
                'machine sends or receives travels as **packets**: small, '
                'self-contained chunks of bytes, each carrying enough '
                'addressing to find its way. A one-megabyte download is not '
                'one thing arriving. It is a few hundred packets arriving '
                'and being reassembled.\n\n'
                'Each packet is built in **layers**, wrapped like envelopes '
                'inside envelopes. The outermost says which machine on this '
                'cable; inside that, which machine on the internet; inside '
                'that, which program on that machine; and inside that, '
                'whatever the program actually meant to say.\n\n'
                '**Capturing means asking the network card for copies** of '
                'packets as they pass. Not intercepting, not delaying, not '
                'modifying: copies. The traffic carries on exactly as it '
                'would have. That is why capture is a diagnostic rather than '
                'an intervention, and why it needs privileges: the card '
                'ordinarily hands your process only its own traffic, and you '
                'are asking for all of it.\n\n'
                '**Why it is worth the trouble.** Logs tell you what a '
                'program decided to write down. A capture tells you what '
                'actually crossed the wire, which settles arguments nothing '
                'else can: whether the request left at all, whether it was '
                'answered, whether it was answered slowly, and whether the '
                'thing that answered was the thing you meant to ask.\n\n'
                '`tcpdump` prints packets. That is the whole of what it does. '
                'Everything else in this module is about choosing which '
                'packets and how much of each to show, because the default of '
                '"all of them" becomes unreadable in about two seconds.'
            ),
            'examples': [
                {
                    'label': 'Stopping it, which you will need immediately',
                    'code': 'Ctrl-C     stop capturing, print the counts\n\n1274 packets captured\n1281 packets received by filter\n7 packets dropped by kernel\n\n-c 20      stop on its own after 20 packets',
                    'note': 'tcpdump runs until interrupted, so Ctrl-C is part of the command. The dropped count is worth reading: if it is high, the filter is too wide and you are losing packets you never saw.',
                },
                {
                    'label': 'One packet, unwrapped',
                    'code': ('Ethernet   which card, on this cable\n'
                             ' IP        which machine, on the internet\n'
                             '  TCP      which program, and in what order\n'
                             '   HTTP    "GET /index.html"\n'
                             '\n'
                             'each layer wraps the one below it'),
                    'note': 'tcpdump can filter at any of these layers, which '
                            'is why its filter language has words like '
                            '`ether`, `ip`, `tcp` and `port` sitting side by '
                            'side.',
                },
                {
                    'label': 'What a line of output says',
                    'code': ('09:15:02.123 IP 10.0.0.5.54321 > '
                             '93.184.216.34.443: Flags [S]\n'
                             '\\__________/    \\___________/   '
                             '\\______________/       \\___/\n'
                             '    when          from            to           '
                             ' kind'),
                    'note': 'Flags [S] is a connection starting. Reading these '
                            'lines fluently is most of the module and it '
                            'arrives faster than you expect.',
                },
                {
                    'label': 'Why you almost always need a filter',
                    'code': ('tcpdump -i any\n'
                             '  everything: thousands of lines a second,\n'
                             '  including the ssh session you are typing\n'
                             '  this into.\n'
                             '\n'
                             'tcpdump -i any port 53\n'
                             '  just the DNS'),
                    'note': 'Capturing your own remote session is the classic '
                            'first move: every line printed generates '
                            'traffic, which prints a line. Filter it out or '
                            'watch it feed itself.',
                },
            ],
            'misconceptions': [
                'Capturing does not intercept traffic. It copies packets as '
                'they pass, and nothing is delayed, blocked or altered by '
                'being watched.',
                'A packet is not a message. One request can be split across '
                'several, and several small messages can share one, which is '
                'why reassembly is something tools do for you.',
                'Reading a capture does not need root, though taking one '
                'does. A saved file is an ordinary file that anyone who can '
                'read it can analyse.',
            ],
            'try_it': [
                'Run `sudo tcpdump -i any -c 5` and read the five lines. '
                'Ignore the detail; just find the two addresses in each.',
                'Run it again while loading a web page, and see how many '
                'packets one page turns out to be.',
            ],
        },
        {
            'id': 'td-two-languages',
            'title': 'Two filter languages, and which is which',
            'next': 'td-bpf',
            'concept': (
                'Capture filters and display filters are how you choose which '
                'packets you record, and which of those you later show. That '
                'is why mixing the two languages is the mistake that looks '
                'like an empty capture.\n\n'
                'A **capture filter** decides which packets are recorded at '
                'all. It is written in BPF, it is what tcpdump takes on the '
                'command line, and because it runs in the kernel it is fast and '
                'deliberately limited. `tcp port 443`.\n\n'
                'A **display filter** decides which of the packets you already '
                'have are shown. It is Wireshark\'s own language, far more '
                'expressive, and it cannot be used for capture. `tcp.port == '
                '443`.\n\n'
                'They look similar enough that people paste one into the other '
                'and get either a syntax error or, worse, a filter that '
                'silently matches nothing. The rule: **spaces and words are '
                'BPF, dots and double equals are display.**\n\n'
                'The reason they cannot be the same language is where they '
                'run. A capture filter is compiled into a tiny program the '
                'kernel runs on every packet, before anything is copied up. '
                'That is why it is fast, why it cannot see a reassembled '
                'stream, and why it has no word for HTTP. A display filter '
                'runs later, after a dissector has named every field, so '
                '`http.request` is cheap there and impossible at capture '
                'time.\n\n'
                'Pasting a Wireshark filter into tcpdump is the usual first '
                'failure: a syntax error, or a filter that matches nothing '
                'and looks like an empty capture. The next lesson is BPF: '
                'hosts, ports, and the parentheses the shell will eat.'
            ),
            'examples': [
                {
                    'label': 'The same intent, two languages',
                    'code': ('capture (BPF)          display (Wireshark)\n'
                             '---------------------  ---------------------\n'
                             'tcp port 443           tcp.port == 443\n'
                             'host 10.0.0.1          ip.addr == 10.0.0.1\n'
                             'src net 10.0.0.0/8     ip.src == 10.0.0.0/8\n'
                             'tcp and not port 22    tcp and !(tcp.port == 22)\n'
                             'icmp                   icmp'),
                    'note': 'Only the last one is the same in both, which is '
                            'exactly the sort of coincidence that keeps the '
                            'confusion alive.',
                },
                {
                    'label': 'Which tool takes which',
                    'code': ('tcpdump  "tcp port 443"          capture only\n'
                             'tshark -f "tcp port 443"         capture\n'
                             'tshark -Y "tcp.port == 443"      display\n'
                             'wireshark: the top bar is display,\n'
                             '           capture options is BPF'),
                    'note': 'tshark takes both, with different flags, which is '
                            'the clearest place to see that they are separate '
                            'things.',
                },
            ],
            'misconceptions': [
                'A display filter in tcpdump is a syntax error, but a subtly '
                'wrong BPF filter often just matches nothing, which looks like '
                '"there was no traffic".',
                'Capture filters cannot see application data reliably, because '
                'they run per packet in the kernel with no reassembly. '
                '"tcp.payload contains" has no BPF equivalent.',
                'Capture broadly and filter on display. Disk is cheap and you '
                'cannot go back and capture the packet you discarded.',
            ],
            'try_it': [
                'Write the filter for "HTTP traffic to one host" in both '
                'languages, and notice you have to think differently for each.',
            ],
        },
        {
            'id': 'td-bpf',
            'title': 'BPF: types, directions and protocols',
            'next': 'td-reading',
            'concept': (
                'BPF is how you write a capture filter for a host, a port or '
                'a protocol. That is why the grid of type, direction and '
                'protocol is the language tcpdump actually takes.\n\n'
                'A primitive has a **type** (`host`, `net`, `port`, '
                '`portrange`), optionally a **direction** (`src`, `dst`), and '
                'optionally a **protocol** (`tcp`, `udp`, `icmp`, `ip`, '
                '`arp`). `src host 10.0.0.1`, `dst port 443`, `tcp portrange '
                '8000-8100`.\n\n'
                'Combine them with `and`, `or` and `not`. A qualified '
                'primitive is one unit, so `not tcp port 22` negates the whole '
                'of it and means exactly what you hoped: everything except TCP '
                'port 22. The trap is precedence between the operators, because '
                '`not` outranks `and`: `not port 22 and tcp` reads as `(not '
                'port 22) and tcp`, not as "not (port 22 and tcp)". '
                'Parenthesise anything with more than two terms, and remember '
                'the shell wants the parentheses quoted.\n\n'
                '`tcpdump not port 22 and tcp` is `(not port 22) and tcp`. '
                'That is why a filter you thought excluded SSH-over-TCP still '
                'shows UDP. Quote the whole expression.\n\n'
                'Leave the quotes off and the shell treats `(` as a subshell '
                'start, so the filter never reaches tcpdump, or only part of '
                'it does. The capture then looks empty. And `host 10.0.0.1` '
                'with no direction matches both ways: usually right, but a '
                'filter you meant as traffic to the server also catches '
                'everything it sent, which can hide the handshake you were '
                'looking for. The next lesson is reading the one-line output '
                'so you know whether the filter did what you meant.'
            ),
            'examples': [
                {
                    'label': 'The grid',
                    'code': ('host 10.0.0.1          either direction\n'
                             'src host 10.0.0.1      from it\n'
                             'dst host 10.0.0.1      to it\n'
                             'net 10.0.0.0/8         a whole range\n'
                             'port 443               either direction\n'
                             'dst port 443           to that port\n'
                             'portrange 8000-8100\n'
                             'tcp / udp / icmp / arp'),
                    'note': 'Omitting the direction means either, which is '
                            'almost always what you want and occasionally not.',
                },
                {
                    'label': 'Combining, and the precedence trap',
                    'code': ("tcpdump 'host 10.0.0.1 and port 443'\n"
                             "tcpdump 'tcp and not port 22'\n"
                             "tcpdump 'src net 10.0.0.0/8 and dst port 53'\n"
                             '\n'
                             "not tcp port 22        all of it negated\n"
                             "not port 22 and tcp    reads as (not port 22) and tcp"),
                    'note': 'A qualified primitive is one unit, so the first '
                            'line means what you hoped. The second is the trap: '
                            'not outranks and. Quote the whole filter, because '
                            'parentheses are shell metacharacters.',
                },
            ],
            'misconceptions': [
'`not tcp port 22` does mean "everything except SSH": the qualified '
                'primitive is negated as a whole. What bites is operator '
                'precedence, because `not` outranks `and`.',
                '`port 53` matches both TCP and UDP unless you say which, which '
                'is usually helpful and occasionally surprising.',
                'BPF has no concept of a connection. It matches packets, so '
                '"show me failed logins" is not expressible here.',
            ],
            'try_it': [
                'Write a filter for "DNS queries leaving this network but not '
                'to our own resolver" and count how many parentheses you '
                'needed.',
            ],
        },
        {
            'id': 'td-reading',
            'title': 'Reading the output',
            'next': 'td-flags',
            'concept': (
                'tcpdump\'s default output is dense and consistent, and once '
                'you can read one line the rest follow.\n\n'
                'Timestamp, protocol, source address and port, a greater-than '
                'sign, destination address and port, then flags and details. '
                'The `.` in `10.0.0.1.443` separates address from port, which '
                'trips people who expect a colon.\n\n'
                'Always use `-nn`. A single `-n` stops address resolution and '
                'the second `n` stops port-name resolution, so you see `443` '
                'rather than `https`. It is faster, it does not leak reverse '
                'lookups onto the network, and it means the output matches the '
                'filter you typed.'
                '\n\n'
                'Without `-nn` two things go wrong at once. tcpdump fires a '
                'reverse DNS lookup for every new address, and that lookup '
                'is itself traffic on the network you are trying to watch. A '
                'slow or broken resolver then stalls the next line for '
                'seconds, so a busy capture looks like it froze. The port '
                'names compound it: you filtered on `443` and the output '
                'says `https`, which is the same thing written two ways and '
                'is how people miss the match.\n\n'
                'The default line is the header. `-A` prints the payload as '
                'ASCII, `-X` prints hex with ASCII beside it. Cleartext HTTP, '
                'DNS and banners become readable; TLS is ciphertext and looks '
                'like junk under both flags. That junk is not a broken '
                'capture, it is the encryption working. Reach for `-A` when '
                'you expect text, `-X` when you need to see the bytes.\n\n'
                'The next lesson is matching on TCP flags and packet size, '
                'which is how you find SYNs and refusals in a noisy capture. '
                'A SYN is `[S]` with length 0; a refuse is `[R]`. Once you '
                'can see those, the capture is no longer a wall of text.'
            ),
            'examples': [
                {
                    'label': 'One line, taken apart',
                    'code': ('09:41:22.104512 IP 10.0.0.1.51234 > 10.0.0.2.443:\n'
                             '  Flags [S], seq 1829301, win 64240, length 0\n'
                             '\n'
                             'time  proto  src.port  >  dst.port\n'
                             'Flags [S] SYN  [S.] SYN-ACK  [.] ACK\n'
                             '      [P] PUSH  [F] FIN  [R] RESET'),
                    'note': 'A dot inside the flags means ACK, so `[S.]` is '
                            'SYN-ACK. This is the notation people find most '
                            'opaque.',
                },
                {
                    'label': 'Flags you will actually look for',
                    'code': ('[S]    connection attempt\n'
                             '[S.]   accepted\n'
                             '[R]    refused, or torn down\n'
                             '[F.]   graceful close\n'
                             '\n'
                             'many [S] with no [S.]  ->  filtered or dead\n'
                             '[S] then [R]           ->  actively refused'),
                    'note': 'That last pair is the difference between a '
                            'firewall dropping you and nothing listening, and '
                            'you can read it straight off the capture.',
                },
                {
                    'label': 'The payload, when you need to read it',
                    'code': ('tcpdump -nn -A -r cap.pcap \'port 80\'\n'
                             'tcpdump -nn -X -r cap.pcap icmp\n'
                             '\n'
                             '-A   ASCII payload\n'
                             '-X   hex, with ASCII beside it\n'
                             'TLS on 443 looks like junk either way'),
                    'note': 'Junk on a TLS port is the encryption working, not '
                            'a truncated capture.',
                },
            ],
            'misconceptions': [
                'Without `-nn`, tcpdump does reverse DNS lookups, which is slow '
                'and generates traffic of its own on the network you are trying '
                'to observe.',
                'The dot before the port is a separator, not part of the '
                'address.',
                'A capture showing nothing may mean your filter is wrong rather '
                'than the traffic being absent. Try without the filter first.',
            ],
            'try_it': [
                'Read the example line above and say out loud who is connecting '
                'to whom, on what port, and what stage the handshake is at.',
            ],
        },
        {
            'id': 'td-flags',
            'title': 'Matching on bits',
            'next': 'td-capture',
            'concept': (
                'Indexing into a packet is how you match TCP flags and sizes '
                'that have no named primitive. That is why this is the syntax '
                'for finding SYNs, refusals and scans in a noisy capture. The '
                'form is `proto[offset:size]`, and two idioms are worth having '
                'by heart.\n\n'
                '`tcp[tcpflags] & tcp-syn != 0` matches any packet with the SYN '
                'bit set. Adding `and tcp[tcpflags] & tcp-ack == 0` narrows it '
                'to connection attempts only, which is how you find scans and '
                'how you count who is knocking.\n\n'
                'The other common one is length: `greater 1000` matches packets '
                'over a size, and `ip[2:2] > 1000` does it by reading the IP '
                'total-length field directly. The first is easier; the second '
                'shows you the mechanism.\n\n'
                '`tcp[tcpflags] & tcp-syn != 0` is the SYN hunt. Forgetting '
                'the mask and writing `tcp[tcpflags] == tcp-syn` misses '
                'SYN-ACK, because that packet has two bits set. TCP flags '
                'live in one byte as individual bits, so several can be set '
                'at once. A SYN-ACK has both SYN and ACK. Equality against a '
                'single named constant therefore misses every packet that is '
                'doing two things, which is most of the handshake. The mask '
                '(`&`) asks whether this bit is on, regardless of its '
                'neighbours. Forgetting it is the usual miss: the filter '
                'looks right, the SYN-ACKs vanish, and the capture looks '
                'like nothing answered.\n\n'
                'The next lesson is capturing to a file without wrecking the '
                'machine or the evidence. Write first, filter second: a live '
                'typo is gone, a pcap is not.'
            ),
            'examples': [
                {
                    'label': 'The two you will reuse',
                    'code': ("tcpdump 'tcp[tcpflags] & tcp-syn != 0'\n"
                             '  any SYN, including SYN-ACK\n'
                             '\n'
                             "tcpdump 'tcp[tcpflags] & (tcp-syn|tcp-ack)"
                             " == tcp-syn'\n"
                             '  connection attempts only\n'
                             '\n'
                             "tcpdump 'tcp[tcpflags] & tcp-rst != 0'\n"
                             '  refusals and resets'),
                    'note': 'Named constants exist: tcp-syn, tcp-ack, tcp-fin, '
                            'tcp-rst, tcp-push, tcp-urg.',
                },
                {
                    'label': 'Reading fields directly',
                    'code': ("tcpdump 'greater 1000'         packet size\n"
                             "tcpdump 'ip[2:2] > 1000'       IP total length\n"
                             "tcpdump 'ip[8] < 5'            low TTL\n"
                             '\n'
                             'proto[offset:size], size is 1, 2 or 4'),
                    'note': 'A low TTL on inbound traffic is worth noticing, '
                            'and this is how you filter for it.',
                },
            ],
            'misconceptions': [
                '`tcp[tcpflags] & tcp-syn != 0` includes SYN-ACK, so it is not '
                'the same as "connection attempts". You need the ACK bit clear '
                'as well.',
                'Byte offsets are into the protocol header, not the whole '
                'packet, which is why the protocol name in front matters.',
                'This does not work on IPv6 the same way, because the header is '
                'a fixed size with extension headers after it.',
            ],
            'try_it': [
                'Write a filter that matches only connection attempts to port '
                '22, then extend it to exclude one trusted source.',
            ],
        },
        {
            'id': 'td-capture',
            'title': 'Capturing to a file, and doing it safely',
            'next': 'td-workflow',
            'concept': (
                'Almost all real work is capture to a file first, analysis '
                'afterwards. Capturing straight to your terminal loses '
                'everything the moment you scroll, and you cannot re-run a '
                'different filter over traffic you never saved.\n\n'
                '`-w file.pcap` writes raw packets. `-r file.pcap` reads them '
                'back, and reading back needs no privileges at all, which is '
                'the part people do not realise: you can hand a colleague a '
                'pcap and they can analyse it as an ordinary user.\n\n'
                'Three more flags matter. `-c N` stops after N packets, which '
                'stops a capture eating a disk. `-s0` captures whole packets '
                'rather than truncating, and is the default on modern versions '
                'but worth stating. `-i any` captures on every interface, which '
                'is the fastest way to stop guessing which one matters. `-D` '
                'lists the interfaces tcpdump can capture on, with a number '
                'for each, which is how you see what `any` is collecting '
                'before you start.\n\n'
                '`-s 0` (or no snaplen cap) keeps full packets; a short '
                'snaplen silently truncates payloads and looks like missing '
                'data. Older tcpdump defaulted to 68 or 96 bytes, enough for '
                'headers and not for payloads. Reading that file later, HTTP '
                'looks empty and TLS looks cut, and it is easy to conclude '
                'the traffic never carried data. `-C` and `-W` rotate files '
                'so a forgotten capture cannot fill the disk. An unbounded '
                '`-w` on a busy interface will, and the capture you needed '
                'is the one that ran out of space. The next lesson is a '
                'workflow that uses a file first, filters later.'
            ),
            'examples': [
                {
                    'label': 'The standard invocation',
                    'code': ('tcpdump -D                       what can be captured\n'
                             "sudo tcpdump -i any -nn -s0 -w cap.pcap "
                             "'port 443'\n"
                             '\n'
                             'tcpdump -nn -r cap.pcap                no root\n'
                             "tcpdump -nn -r cap.pcap 'host 10.0.0.5'\n"
                             '  a different filter over the same capture'),
                    'note': 'That second filter is the whole argument for '
                            'writing to a file: you can ask a new question '
                            'without needing the traffic to happen again.',
                },
                {
                    'label': 'Not filling the disk',
                    'code': ('-c 1000              stop after 1000 packets\n'
                             '-G 3600 -w cap-%H.pcap   rotate hourly\n'
                             '-W 24                stop after 24 files\n'
                             '-Z user              drop privileges after '
                             'opening'),
                    'note': 'With `-G`, `-W` limits the count and then exits: '
                            'it is a ceiling, not a ring. A rolling day comes '
                            'free from the filename instead, because `%H` wraps '
                            'after 24 hours and overwrites.',
                },
            ],
            'misconceptions': [
                'Capture needs root or CAP_NET_RAW. Reading a pcap does not, '
                'which is why analysis is usually done unprivileged.',
                'The output of `-w` is not text. Piping it to grep does nothing '
                'useful; read it back with `-r`.',
                'A capture without `-c` or `-G` will fill the disk given time, '
                'and it is always the disk you needed.',
            ],
            'try_it': [
                'If you have tcpdump elsewhere: capture 20 packets to a file, '
                'then read it back twice with two different filters.',
            ],
        },
        {
            'id': 'td-workflow',
            'title': 'A workflow that works under pressure',
            'concept': (
                'When something is wrong and you are reaching for a capture, '
                'the order matters more than the cleverness of the filter.\n\n'
                'Capture **broadly** and to a file. Narrow later. The most '
                'common mistake is writing a precise filter first, capturing '
                'nothing, and concluding there was no traffic, when the filter '
                'was simply wrong.\n\n'
                'Then work from the outside in. Is there any traffic at all? '
                'Between the right two hosts? On the right port? Reaching the '
                'right stage of the handshake? Each answer rules out a layer, '
                'and the layer it stops at is usually the answer.\n\n'
                'And know where this tool stops. tcpdump shows packets. If the '
                'question is about application behaviour, reassembled streams, '
                'or TLS contents, the answer is Wireshark or tshark reading the '
                'same pcap, and that is a handoff rather than a failure.\n\n'
                'Capture wide, save the file, filter in a second command. '
                'A live filter you typed wrong is gone; a pcap you can '
                're-read. The layer it stops at is readable in the flags. '
                'SYNs with no SYN-ACK means the packet left and nothing '
                'answered: host down, port filtered, or the wrong address. '
                'SYN then RST is a host that is up and a port that is '
                'closed. A completed handshake and then no data is an '
                'application problem, not a network one. Each of those is a '
                'different ticket, and the capture is what tells them apart. '
                'This module stays on the packet. Reassembled streams belong '
                'to Wireshark.'
            ),
            'examples': [
                {
                    'label': 'Outside in',
                    'code': ("1  tcpdump -nn -i any -c 50\n"
                             '     is anything happening at all\n'
                             "2  tcpdump -nn -r cap.pcap 'host 10.0.0.5'\n"
                             '     between the right machines\n'
                             "3  ... 'host 10.0.0.5 and port 443'\n"
                             '     on the right port\n'
                             '4  read the flags: [S] with no [S.]'),
                    'note': 'Steps 2 and 3 are re-filters of one capture, which '
                            'is why step 1 wrote to a file.',
                },
                {
                    'label': 'An empty capture is not a finding yet',
                    'code': ("tcpdump -nn -i any -c 20 "
                             "'host 10.0.0.5 and port 443'\n"
                             '  0 packets captured\n'
                             '\n'
                             'write first, then ask:\n'
                             'tcpdump -nn -i any -c 50 -w cap.pcap\n'
                             "tcpdump -nn -r cap.pcap 'host 10.0.0.5'\n"
                             '  traffic was there; the live filter was not'),
                    'note': 'The first command proved nothing. A file you can '
                            're-filter is how a dead host is told from a typo.',
                },
            ],
            'misconceptions': [
                'An empty capture is more often a wrong filter than an absent '
                'packet. Remove the filter before concluding anything.',
                'tcpdump is not the tool for reassembled application data. Hand '
                'the pcap to tshark or Wireshark; it is the same file.',
            ],
            'try_it': [
                'Next time something will not connect, capture first without a '
                'filter and narrow afterwards. Notice how often the first '
                'filter you would have written was wrong.',
            ],
        },
    ],

    'drills': [
        {'id': 'td-cmd-host', 'type': 'command', 'answer': "tcpdump -nn 'host 10.0.0.1'",
         'prompt': 'Capture traffic to or from one address, without resolving '
                   'names or ports.',
         'teach': 'Always -nn. It is faster and it does not put reverse lookups '
                  'on the network you are observing.'},
        {'id': 'td-cmd-srchost', 'type': 'command',
         'answer': "tcpdump -nn 'src host 10.0.0.1'",
         'prompt': 'Capture only traffic coming FROM one address.',
         'teach': 'The direction qualifier is src, dst, or neither, and '
                  'neither means both. Leaving it out is why a filter matches '
                  'twice the traffic you expected.'},
        {'id': 'td-cmd-dstport', 'type': 'command',
         'answer': "tcpdump -nn 'dst port 443'",
         'prompt': 'Capture only traffic going TO port 443.',
         'teach': 'port matches TCP and UDP unless you say which, so naming '
                  'the protocol as well gives you the narrower filter.'},
        {'id': 'td-cmd-net', 'type': 'command',
         'answer': "tcpdump -nn 'net 10.0.0.0/8'",
         'prompt': 'Capture traffic involving a whole network range.',
         'teach': 'net takes a prefix. Without the mask it means the old '
                  'classful network, which is almost never what you meant.'},
        {'id': 'td-cmd-portrange', 'type': 'command',
         'answer': "tcpdump -nn 'portrange 8000-8100'",
         'prompt': 'Capture traffic on any port in a range.',
         'teach': 'Useful for ephemeral ports, and for a service that spreads '
                  'itself across a block rather than sitting on one number.'},
        {'id': 'td-cmd-and', 'type': 'command',
         'answer': "tcpdump -nn 'host 10.0.0.1 and port 443'",
         'prompt': 'Capture traffic involving one host on one port.',
         'teach': 'and, or and not compose the primitives, and the quotes are '
                  'what keep the shell from eating them first.'},
        {'id': 'td-cmd-not', 'type': 'command',
         'answer': "tcpdump -nn 'not (tcp port 22)'",
         'prompt': 'Capture everything except SSH, with the parentheses that '
                   'make it mean what you want.',
         'teach': '`not tcp port 22` works without them, but parenthesising '
                  'is the habit worth having: `not` outranks `and`, so the '
                  'moment a second operator appears the grouping stops being '
                  'obvious.'},
        {'id': 'td-cmd-icmp', 'type': 'command', 'answer': "tcpdump -nn 'icmp'",
         'prompt': 'Capture only ICMP.',
         'teach': 'Blocking ICMP outright breaks path MTU discovery, so a '
                  'capture with no ICMP in it at all is itself a finding.'},
        {'id': 'td-cmd-arp', 'type': 'command', 'answer': "tcpdump -nn 'arp'",
         'prompt': 'Capture only ARP.',
         'teach': 'ARP is layer two, so it never crosses a router. If you can '
                  'see it, the sender is on your own segment.'},
        {'id': 'td-cmd-syn', 'type': 'command',
         'answer': "tcpdump -nn 'tcp[tcpflags] & tcp-syn != 0'",
         'prompt': 'Capture any packet with the SYN bit set.',
         'teach': 'This includes SYN-ACK, so it is not the same as connection '
                  'attempts.'},
        {'id': 'td-cmd-synonly', 'type': 'command',
         'answer': "tcpdump -nn 'tcp[tcpflags] & (tcp-syn|tcp-ack) == tcp-syn'",
         'prompt': 'Capture connection attempts only, with SYN set and ACK '
                   'clear.',
         'teach': 'How you find scans, and how you count who is knocking.'},
        {'id': 'td-cmd-rst', 'type': 'command',
         'answer': "tcpdump -nn 'tcp[tcpflags] & tcp-rst != 0'",
         'prompt': 'Capture resets and refusals.',
         'teach': 'A reset usually means a closed port or a firewall '
                  'rejecting rather than dropping. Silence is what dropping '
                  'looks like.'},
        {'id': 'td-cmd-greater', 'type': 'command', 'answer': "tcpdump -nn 'greater 1000'",
         'prompt': 'Capture packets of at least 1000 bytes.',
         'teach': 'It matches the whole frame length, so the comparison '
                  'counts headers as well as payload.'},
        {'id': 'td-cmd-ttl', 'type': 'command', 'answer': "tcpdump -nn 'ip[8] < 5'",
         'prompt': 'Capture IP packets with a low TTL, by reading the field '
                   'directly.',
         'teach': 'ip[8] is the TTL byte by offset. Indexing into the header '
                  'is how you filter on anything the filter language has no '
                  'keyword for.'},
        {'id': 'td-cmd-write', 'type': 'command',
         'answer': "tcpdump -i any -nn -s0 -w cap.pcap 'port 443'",
         'prompt': 'Capture on every interface to a file, whole packets, '
                   'filtered to one port.',
         'teach': '-s0 takes whole packets. The default snap length truncates '
                  'them and loses the payload you were capturing to read.'},
        {'id': 'td-cmd-read', 'type': 'command', 'answer': 'tcpdump -nn -r cap.pcap',
         'prompt': 'Read a saved capture back. This needs no privileges.',
         'teach': 'Reading a file needs no privileges at all, which is the '
                  'argument for capturing on the server and analysing it '
                  'somewhere else.'},
        {'id': 'td-cmd-refilter', 'type': 'command',
         'answer': "tcpdump -nn -r cap.pcap 'host 10.0.0.5'",
         'prompt': 'Apply a different filter to a capture you already have.',
         'teach': 'The whole argument for writing to a file: you can ask a new '
                  'question without the traffic happening again.'},
        {'id': 'td-cmd-count', 'type': 'command', 'answer': 'tcpdump -nn -c 1000',
         'prompt': 'Stop capturing after 1000 packets, so it cannot fill the '
                   'disk.',
         'teach': 'An unbounded capture is a way to fill a disk during an '
                  'incident, which is the worst possible moment for it.'},
        {'id': 'td-cmd-rotate', 'type': 'command',
         'answer': 'tcpdump -nn -G 3600 -W 24 -w cap-%H.pcap',
         'prompt': 'Capture into hourly files, stopping after a day of them.',
         'teach': '-G is the seconds per file and -W the number of files, after '
                  'which tcpdump exits. Drop -W and %H wraps after 24 hours, '
                  'which is the rolling window people actually mean.'},
        {'id': 'td-cmd-tshark-capture', 'type': 'command',
         'answer': 'tshark -f "tcp port 443"',
         'prompt': 'Give tshark a CAPTURE filter, in BPF.',
         'teach': '-f is BPF and -Y is a display filter. tshark taking both is '
                  'the clearest place to see they are different languages.'},
        {'id': 'td-cmd-tshark-display', 'type': 'command',
         'answer': 'tshark -Y "tcp.port == 443"',
         'prompt': 'Give tshark a DISPLAY filter, in Wireshark syntax.',
         'teach': 'Display filters and capture filters are different '
                  'languages. -f takes the capture syntax, -Y takes the '
                  'Wireshark one, and neither accepts the other.'},
        {'id': 'td-cmd-tshark-read', 'type': 'command',
         'answer': 'tshark -r cap.pcap -Y "http.request"',
         'prompt': 'Read a pcap in tshark and show only HTTP requests, which is '
                   'not expressible as a capture filter.',
         'teach': 'Capture filters run per packet in the kernel with no '
                  'reassembly, so anything about a stream needs a display '
                  'filter.'},

        # ------------------------------------------------------------------
        # Graded against a real capture file. Everything below is run rather
        # than compared: write any filter that selects the right packets and
        # it passes. The fixture holds an HTTPS session, a DNS exchange, a
        # refused SSH connection, a cleartext HTTP request from a second
        # host, a ping, and one packet from another subnet. See `pcapgen`.
        # ------------------------------------------------------------------
        {'id': 'td-bpf-https', 'type': 'bpf', 'answer': 'tcp port 443',
         'prompt': 'Select only the HTTPS traffic.',
         'teach': 'Both directions, because `port` matches source or '
                  'destination. `dst port 443` would have caught half a '
                  'conversation, which is the usual first mistake.'},
        {'id': 'td-bpf-dns', 'type': 'bpf', 'answer': 'udp port 53',
         'prompt': 'Select the DNS traffic, and nothing else.',
         'teach': 'Saying `udp` as well as the port is the habit worth '
                  'keeping: port 53 over TCP is a zone transfer, which is a '
                  'different thing you probably did not mean.'},
        {'id': 'td-bpf-icmp', 'type': 'bpf', 'answer': 'icmp',
         'prompt': 'Select the ping traffic.',
         'teach': 'ICMP has no ports at all, so a filter written in terms of '
                  'ports can never see it.'},
        {'id': 'td-bpf-nottcp', 'type': 'bpf', 'answer': 'not tcp',
         'prompt': 'Select everything that is not TCP.',
         'teach': 'Worth running once on a real network: the answer is '
                  'usually noisier than people expect.'},
        {'id': 'td-bpf-host', 'type': 'bpf', 'answer': 'host 10.0.0.7',
         'prompt': 'Select only traffic to or from 10.0.0.7.',
         'teach': '`host` is both directions. `src host` and `dst host` split '
                  'it when you care which way it went.'},
        {'id': 'td-bpf-ssh', 'type': 'bpf', 'answer': 'port 22',
         'prompt': 'Select the SSH attempt and whatever answered it.',
         'teach': 'The answer here is a RST: the connection was refused. A '
                  'filter for `port 22` finds the refusal as well as the try.'},
        {'id': 'td-bpf-syn', 'type': 'bpf',
         'answer': 'tcp[tcpflags] & (tcp-syn|tcp-ack) == tcp-syn',
         'prompt': 'Select connection attempts only: SYN set, ACK clear.',
         'teach': 'The mask-and-compare form is the one to memorise. '
                  '`tcp[tcpflags] & tcp-syn != 0` also matches the SYN-ACK, '
                  'so it answers a different question than you asked.'},
        {'id': 'td-bpf-rst', 'type': 'bpf',
         'answer': 'tcp[tcpflags] & tcp-rst != 0',
         'prompt': 'Select the refused connection.',
         'teach': 'RST is how a closed port answers, and scanning for it is '
                  'how you tell a filtered port from a closed one.'},
        {'id': 'td-bpf-net', 'type': 'bpf', 'answer': 'src net 192.168.50.0/24',
         'prompt': 'Select traffic arriving from the 192.168.50.0/24 network.',
         'teach': '`net` takes CIDR, and `src net` is the form that answers '
                  '"who is talking to us from over there".'},
        {'id': 'td-bpf-highport', 'type': 'bpf', 'answer': 'tcp port 8080',
         'prompt': 'Select the traffic on port 8080.',
         'teach': 'Nothing about 8080 is special to BPF. Ports are numbers, '
                  'and the well-known ones have no privileged status here.'},

        # Display filters, graded in tshark. Same questions, other language.
        {'id': 'td-dis-https', 'type': 'display', 'answer': 'tcp.port == 443',
         'prompt': 'Now in DISPLAY syntax: select the HTTPS traffic. Same '
                   'packets as `tcp port 443`.',
         'teach': 'Dotted field name, double equals. If you typed the capture '
                  'filter here, tshark told you so, which is the entire point '
                  'of the pairing.'},
        {'id': 'td-dis-dns', 'type': 'display', 'answer': 'dns',
         'prompt': 'Select the DNS traffic, as a display filter.',
         'teach': 'A display filter can name a protocol the dissector '
                  'understands, rather than the port it usually runs on. That '
                  'is a thing BPF cannot do: it would find DNS on port 5353 '
                  'and would not be fooled by something else on port 53.'},
        {'id': 'td-dis-icmp', 'type': 'display', 'answer': 'icmp',
         'prompt': 'Select the ping traffic, as a display filter.',
         'teach': 'One of the few strings that is valid in both languages and '
                  'means the same thing. That coincidence is exactly why '
                  'people believe the two languages are one language.'},
        {'id': 'td-dis-syn', 'type': 'display',
         'answer': 'tcp.flags.syn == 1 && tcp.flags.ack == 0',
         'prompt': 'Connection attempts only, as a display filter. Same '
                   'packets as the BPF version.',
         'teach': 'Compare the two spellings side by side. The display filter '
                  'reads like a sentence; the capture filter is bit '
                  'arithmetic, because it has to compile to something a '
                  'kernel will run per packet.'},
        {'id': 'td-dis-rst', 'type': 'display', 'answer': 'tcp.flags.reset == 1',
         'prompt': 'Select the refused connection, as a display filter.',
         'teach': 'Note the field is `reset`, not `rst`. Display filter field '
                  'names are their own vocabulary and tab completion in '
                  'Wireshark is how people actually learn them.'},
        {'id': 'td-dis-http', 'type': 'display', 'answer': 'http.request',
         'prompt': 'Select HTTP requests. Try to write this as a capture '
                   'filter afterwards and see how far you get.',
         'teach': 'This is the filter with no BPF equivalent. A capture '
                  'filter sees one packet at a time in the kernel with no '
                  'reassembly and no idea what HTTP is.'},
        {'id': 'td-dis-tls', 'type': 'display', 'answer': 'tls.handshake',
         'prompt': 'Select the TLS handshake.',
         'teach': 'Also unavailable to BPF, and for the same reason: it '
                  'requires knowing what the bytes mean, not merely where '
                  'they sit.'},
        {'id': 'td-dis-src', 'type': 'display',
         'answer': 'ip.src == 192.168.50.4',
         'prompt': 'Select traffic from 192.168.50.4, as a display filter.',
         'teach': '`ip.src` and `ip.addr` are the pair to keep straight: '
                  '`ip.addr` is either direction, and reaching for it when '
                  'you meant `ip.src` is the display-filter version of '
                  'forgetting `src`.'},
        {'id': 'td-cmd-list-if', 'type': 'command',
         'answer': 'tcpdump -D',
         'prompt': 'List the interfaces available to capture on.',
         'teach': 'The first live stumble is which interface to name, and this answers it without guessing.'},
        {'id': 'td-cmd-ascii', 'type': 'command',
         'answer': 'tcpdump -r capture.pcap -A',
         'prompt': 'Print packet payloads as ASCII while reading a capture.',
         'teach': '-A is ASCII and -X is hex with ASCII beside it. Both show payload, which the default header line does not.'},
    ],

    'challenges': [
        {
            'id': 'td-capture-narrow',
            'title': 'Capture broadly, narrow afterwards',
            'goal': 'Practise the workflow on real traffic. The trainer cannot '
                    'check this: capturing needs privileges and an interface, '
                    'which D1 puts out of reach.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'Capture 50 packets on any interface to a file, '
                                'with no filter at all.',
                 'hint': 'sudo tcpdump -i any -nn -s0 -c 50 -w cap.pcap'},
                {'instruction': 'Read it back as an ordinary user and confirm '
                                'you see traffic.',
                 'hint': 'tcpdump -nn -r cap.pcap'},
                {'instruction': 'Re-filter the same file down to one host, then '
                                'to one port.',
                 'hint': "tcpdump -nn -r cap.pcap 'host X and port Y'"},
                {'instruction': 'Find a handshake and read its flags: who sent '
                                '[S], who answered [S.].'},
            ],
            'free': 'Capture unfiltered to a file, then answer three '
                    'progressively narrower questions by re-filtering that one '
                    'file rather than capturing again.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
        {
            'id': 'td-translate',
            'title': 'Translate between the two languages',
            'goal': 'Write the same five intents in both BPF and Wireshark '
                    'display syntax, on paper. Nothing to run.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'Traffic to or from 10.0.0.5, both ways.',
                 'hint': 'host 10.0.0.5   /   ip.addr == 10.0.0.5'},
                {'instruction': 'TCP to port 443 only.',
                 'hint': 'dst port 443   /   tcp.dstport == 443'},
                {'instruction': 'Everything except SSH.',
                 'hint': 'mind the not precedence in BPF'},
                {'instruction': 'Connection attempts only.'},
                {'instruction': 'HTTP requests. Notice one of these cannot be '
                                'written as a capture filter at all.',
                 'hint': 'that is the point of the exercise'},
            ],
            'free': 'Write all five intents in both languages and identify '
                    'which one has no BPF equivalent, and why.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
        {
            'id': 'td-read-file',
            'title': 'Read a capture without guessing at anything',
            'goal': 'Open the capture with the four flags that make output '
                    'readable and reproducible, and save what you see.',
            'setup': {'kind': 'pcapbox'},
            'solution': {'shell': 'tcpdump -r capture.pcap -nn > all.txt '
                                  '2>/dev/null && '
                                  'tcpdump -r capture.pcap -nn -c 3 > first3.txt '
                                  '2>/dev/null'},
            'steps': [
                {'instruction': 'Read capture.pcap with no name resolution at '
                                'all, saving every line to all.txt.',
                 'hint': 'tcpdump -r capture.pcap -nn > all.txt'},
                {'instruction': 'Do it again limited to the first three '
                                'packets, into first3.txt.',
                 'hint': 'tcpdump -r capture.pcap -nn -c 3 > first3.txt'},
                {'instruction': 'Note that -nn suppressed both host and port '
                                'lookups. On current tcpdump a single -n does '
                                'the same; -nn is a habit from other tools.'},
            ],
            'free': 'Produce all.txt holding every packet in capture.pcap '
                    'with no name resolution, and first3.txt holding only the '
                    'first three.',
            'verify': {'kind': 'pcapbox', 'expect': {
                'file_contains': {'all.txt': ['93.184.216.34.443',
                                              '10.0.0.5.50000'],
                                  'first3.txt': 'Flags [S]'},
                'file_lacks': {'first3.txt': 'ICMP'}}},
            'fallback': 'self',
        },
        {
            'id': 'td-filter-file',
            'title': 'Apply a capture filter to a saved file',
            'goal': 'The same BPF you would use live, applied while reading, '
                    'which is how you narrow a capture you already have.',
            'setup': {'kind': 'pcapbox'},
            'solution': {'shell':
                'tcpdump -r capture.pcap -nn "tcp port 443" > https.txt '
                '2>/dev/null && '
                'tcpdump -r capture.pcap -nn "icmp" > icmp.txt 2>/dev/null && '
                'tcpdump -r capture.pcap -nn "udp port 53" > dns.txt '
                '2>/dev/null'},
            'steps': [
                {'instruction': 'Select only the TCP traffic on port 443 into '
                                'https.txt.',
                 'hint': 'tcpdump -r capture.pcap -nn "tcp port 443"'},
                {'instruction': 'Select only ICMP into icmp.txt.'},
                {'instruction': 'Select only DNS, which is UDP port 53, into '
                                'dns.txt.'},
                {'instruction': 'Note that the filter is the same language '
                                'whether you are reading or capturing.'},
            ],
            'free': 'Produce https.txt, icmp.txt and dns.txt by applying '
                    'three capture filters while reading capture.pcap.',
            'verify': {'kind': 'pcapbox', 'expect': {
                'file_contains': {'https.txt': '443',
                                  'icmp.txt': 'ICMP echo',
                                  'dns.txt': 'example.com'},
                'file_lacks': {'https.txt': 'ICMP',
                               'icmp.txt': '443'}}},
            'fallback': 'self',
        },
        {
            'id': 'td-flags-hunt',
            'title': 'Find the connection that was refused',
            'goal': 'Use a TCP flag filter to separate a handshake that '
                    'completed from one that was reset.',
            'setup': {'kind': 'pcapbox'},
            'solution': {'shell':
                'tcpdump -r capture.pcap -nn "tcp[tcpflags] & tcp-rst != 0" '
                '> resets.txt 2>/dev/null && '
                'tcpdump -r capture.pcap -nn "tcp[tcpflags] & tcp-syn != 0 '
                'and tcp[tcpflags] & tcp-ack == 0" > syns.txt 2>/dev/null'},
            'steps': [
                {'instruction': 'Select every packet with the RST flag set '
                                'into resets.txt.',
                 'hint': 'tcpdump -r capture.pcap -nn "tcp[tcpflags] & '
                         'tcp-rst != 0"'},
                {'instruction': 'Select the opening SYNs only, meaning SYN '
                                'set and ACK clear, into syns.txt.',
                 'hint': 'tcp[tcpflags] & tcp-syn != 0 and tcp[tcpflags] & '
                         'tcp-ack == 0'},
                {'instruction': 'Compare the two. Which SYN never got a '
                                'handshake, and what answered it instead?'},
            ],
            'free': 'Produce resets.txt containing the RST packets and '
                    'syns.txt containing only the opening SYNs, using flag '
                    'filters rather than reading by eye.',
            'verify': {'kind': 'pcapbox', 'expect': {
                'file_contains': {'resets.txt': '10.0.0.9.22',
                                  'syns.txt': ['50000', '445']},
                'file_lacks': {'syns.txt': 'Flags [S.]'}}},
            'fallback': 'self',
        },
        {
            'id': 'td-host-net',
            'title': 'Narrow by host, then by network',
            'goal': 'Use the host, net and direction primitives, which are '
                    'the ones that make a large capture manageable.',
            'setup': {'kind': 'pcapbox'},
            'solution': {'shell':
                'tcpdump -r capture.pcap -nn "host 93.184.216.34" > one-host.txt '
                '2>/dev/null && '
                'tcpdump -r capture.pcap -nn "src net 192.168.50.0/24" '
                '> from-net.txt 2>/dev/null && '
                'tcpdump -r capture.pcap -nn "dst port 22 or dst port 445" '
                '> to-services.txt 2>/dev/null'},
            'steps': [
                {'instruction': 'Select everything to or from 93.184.216.34 '
                                'into one-host.txt.',
                 'hint': 'tcpdump -r capture.pcap -nn "host 93.184.216.34"'},
                {'instruction': 'Select only traffic whose source is in '
                                '192.168.50.0/24, into from-net.txt.',
                 'hint': '"src net 192.168.50.0/24"'},
                {'instruction': 'Select traffic destined for either port 22 '
                                'or port 445, into to-services.txt.'},
            ],
            'free': 'Produce one-host.txt, from-net.txt and to-services.txt '
                    'using host, src net, and dst port with an or.',
            'verify': {'kind': 'pcapbox', 'expect': {
                'file_contains': {'one-host.txt': '93.184.216.34',
                                  'from-net.txt': '192.168.50.4',
                                  'to-services.txt': ['10.0.0.9.22',
                                                      '10.0.0.5.445']},
                'file_lacks': {'from-net.txt': 'ICMP'}}},
            'fallback': 'self',
        },
        {
            'id': 'td-extract',
            'title': 'Turn a capture into a list you can act on',
            'goal': 'Pipe tcpdump output through the text tools to answer a '
                    'question, rather than reading packets one at a time.',
            'setup': {'kind': 'pcapbox'},
            'solution': {'shell':
                'tcpdump -r capture.pcap -nn "tcp" 2>/dev/null | '
                "awk '{print $3}' | cut -d. -f1-4 | sort -u > talkers.txt && "
                'tcpdump -r capture.pcap -nn 2>/dev/null | wc -l > count.txt'},
            'steps': [
                {'instruction': 'Read every TCP packet and pull out the '
                                'source field, which is the third column.',
                 'hint': "tcpdump -r capture.pcap -nn tcp | awk '{print $3}'"},
                {'instruction': 'Strip the port off the end so you are left '
                                'with addresses, then sort them unique into '
                                'talkers.txt.',
                 'hint': 'cut -d. -f1-4 | sort -u'},
                {'instruction': 'Separately, count every packet in the file '
                                'into count.txt.',
                 'hint': 'tcpdump -r capture.pcap -nn | wc -l > count.txt'},
            ],
            'free': 'Produce talkers.txt listing each unique TCP source '
                    'address once, and count.txt holding the total packet '
                    'count.',
            'verify': {'kind': 'pcapbox', 'expect': {
                'file_contains': {'talkers.txt': ['10.0.0.5', '93.184.216.34'],
                                  'count.txt': '15'},
                'file_lacks': {'talkers.txt': '50000'}}},
            'fallback': 'self',
        },
        {
            'id': 'td-write-subset',
            'title': 'Write a smaller capture out of a bigger one',
            'goal': 'Use -w to carve a subset, which is what you actually '
                    'hand to someone else or open in Wireshark.',
            'setup': {'kind': 'pcapbox'},
            'solution': {'shell':
                'tcpdump -r capture.pcap -w tcp-only.pcap "tcp" 2>/dev/null && '
                'tcpdump -r tcp-only.pcap -nn > tcp-only.txt 2>/dev/null && '
                'tcpdump -r capture.pcap -nn -X "icmp" > icmp-hex.txt '
                '2>/dev/null'},
            'steps': [
                {'instruction': 'Read the capture, keep only TCP, and write '
                                'the result to tcp-only.pcap.',
                 'hint': 'tcpdump -r capture.pcap -w tcp-only.pcap "tcp"'},
                {'instruction': 'Read your new file back as text into '
                                'tcp-only.txt to prove it worked.'},
                {'instruction': 'Separately, dump the ICMP packets with their '
                                'payload in hex and ASCII, into icmp-hex.txt.',
                 'hint': 'tcpdump -r capture.pcap -nn -X "icmp"'},
            ],
            'free': 'Produce tcp-only.pcap containing only the TCP packets, '
                    'tcp-only.txt proving what is in it, and icmp-hex.txt '
                    'showing ICMP payloads in hex.',
            'verify': {'kind': 'pcapbox', 'expect': {
                'is_file': ['tcp-only.pcap'],
                'file_contains': {'tcp-only.txt': 'Flags',
                                  'icmp-hex.txt': ['ICMP echo', '0x0000']},
                'file_lacks': {'tcp-only.txt': 'ICMP'}}},
            'fallback': 'self',
        },
    ],

    'quiz': [
        {'id': 'tdq-two', 'type': 'mcq',
         'prompt': 'Which of these is a tcpdump capture filter?',
         'answer': 'tcp port 443',
         'distractors': ['tcp.port == 443', 'tcp.port eq 443',
                         'filter tcp port 443'],
         'teach': 'Spaces and words are BPF; dots and double equals are '
                  'Wireshark display syntax.'},

        {'id': 'tdq-wrong-box', 'type': 'mcq',
         'prompt': 'You paste `tcp.port == 443` into tcpdump. What happens?',
         'answer': 'A syntax error, because that is display filter syntax.',
         'distractors': ['It works; the syntaxes are interchangeable.',
                         'It captures nothing, silently.',
                         'It captures everything, ignoring the filter.'],
         'teach': 'The dangerous direction is the other one: a subtly wrong BPF '
                  'filter often matches nothing and looks like absent traffic.'},

        {'id': 'tdq-not', 'type': 'mcq',
         'prompt': 'What does `not port 22 and tcp` select?',
         'answer': 'TCP traffic that is not on port 22, because not binds '
                   'tighter than and.',
         'distractors': ['Nothing on port 22, and nothing that is TCP.',
                         'Everything, since the two halves cancel out.',
                         'It is a syntax error.'],
         'teach': '`tcp port 22` is a single primitive, so `not tcp port 22` '
                  'negates all of it and does mean "everything except TCP port '
                  '22". The trap is precedence: not outranks and, so this reads '
                  'as `(not port 22) and tcp`. Parenthesise anything with more '
                  'than two terms.'},

        {'id': 'tdq-nn', 'type': 'mcq',
         'prompt': 'Why use -nn rather than -n?',
         'answer': 'Habit: on current tcpdump -n already stops port names too, '
                   'so the second n changes nothing.',
         'distractors': ['The second n also stops port names being resolved.',
                         'It doubles the verbosity.',
                         'It disables promiscuous mode.'],
         'teach': '-n turns off all name resolution, so you already see 443 '
                  'rather than https. The -n versus -nn distinction is real in '
                  'some other tools, which is where the habit comes from, and '
                  'it costs nothing to keep.'},

        {'id': 'tdq-flags', 'type': 'mcq',
         'prompt': 'What does `Flags [S.]` mean?',
         'answer': 'SYN-ACK: the dot is the ACK bit.',
         'distractors': ['SYN followed by a reset.',
                         'A SYN with no payload.',
                         'A partial SYN, fragmented.'],
         'teach': 'The dot for ACK is the notation people find most opaque, and '
                  'it is the one you read most.'},

        {'id': 'tdq-syn-only', 'type': 'mcq',
         'prompt': 'Why is `tcp[tcpflags] & tcp-syn != 0` not "connection '
                   'attempts"?',
         'answer': 'It also matches SYN-ACK, which is the reply rather than the '
                   'attempt.',
         'distractors': ['It misses attempts that are retransmitted.',
                         'It only matches the first packet of a capture.',
                         'It matches UDP as well.'],
         'teach': 'Add `and tcp[tcpflags] & tcp-ack == 0` to narrow it.'},

        {'id': 'tdq-read-priv', 'type': 'mcq',
         'prompt': 'What needs root: capturing, reading a pcap, or both?',
         'answer': 'Capturing only.',
         'distractors': ['Both.', 'Reading only.', 'Neither, on modern Linux.'],
         'teach': 'Which is why you can hand a colleague a pcap and they can '
                  'analyse it as an ordinary user.'},

        {'id': 'tdq-empty', 'type': 'mcq',
         'prompt': 'Your capture shows nothing. What is the most likely cause?',
         'answer': 'The filter is wrong.',
         'distractors': ['The interface is down.',
                         'You need -s0 to see packets.',
                         'The traffic is encrypted.'],
         'teach': 'Remove the filter before concluding there was no traffic. '
                  'This is the most common tcpdump mistake.'},

        {'id': 'tdq-http', 'type': 'mcq',
         'prompt': 'Why can you not write a capture filter for "HTTP requests"?',
         'answer': 'BPF runs per packet in the kernel with no stream '
                   'reassembly.',
         'distractors': ['HTTP is encrypted.',
                         'BPF cannot match on port 80.',
                         'It can; the syntax is http.request.'],
         'teach': 'Anything about a stream rather than a packet belongs in a '
                  'display filter, over a pcap you already captured.'},

        {'id': 'tdq-workflow', 'type': 'mcq',
         'prompt': 'What is the right order when something will not connect?',
         'answer': 'Capture broadly to a file, then narrow by re-filtering it.',
         'distractors': ['Write the most precise filter you can, first.',
                         'Capture to the terminal so you see it live.',
                         'Use a display filter for capture, since it is more '
                         'expressive.'],
         'teach': 'You cannot go back and capture the packet you discarded, and '
                  'a precise filter written first is often simply wrong.'},
    ],
}
