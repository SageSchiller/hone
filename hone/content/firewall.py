"""nftables and iptables: filtering packets, and the model underneath.

A firewall earns a module because the mental model genuinely reframes how you
see a machine on a network. Before it, "the port is blocked" is a mystery.
After it, a packet is a thing that walks a defined path through the kernel,
gets checked against an ordered list of rules at fixed points on that path, and
is accepted, dropped or rejected by the first rule that matches or by a default
policy if none do. That path-and-rules picture is the whole subject.

The single most important idea is **stateful filtering**: the kernel tracks
connections, so "allow the replies to connections I started" is one rule, and
you only ever explicitly permit *new* inbound connections. Almost every real
firewall is that one idea plus a short list of allowed services.

**iptables and nftables.** Both are front-ends to the same kernel framework,
netfilter. iptables is the one you will still meet everywhere; nftables is the
modern replacement that unifies IPv4 and IPv6, loads rules atomically, and adds
sets and maps. This module teaches the nftables model and shows the iptables
you will still have to read.

**Verification.** Loading rules into the kernel needs root, which the trainer
does not have, so per D8 the split is honest: writing a correct ruleset is a
file, so those challenges are verified in the sandbox by reading the ruleset
back; loading and testing it live is self-marked. The commands are drilled as
typed text.
"""

MODULE = {
    'id': 'firewall',
    'title': 'nftables and iptables',
    'group': 'Network',
    'blurb': 'The packet-filter model, stateful rules, NAT, and reading a ruleset.',
    'context': 'You are at a shell prompt on a Linux host, writing and reading firewall rules.',
    'needs': ['nft', 'iptables'],
    'prereqs': ['linux', 'ssh'],
    'adapter': 'sandbox',
    'estimate': '4-5 hours',
    'order': 56,

    'lessons': [
        {
            'id': 'fw-model',
            'title': 'Filtering packets: hooks, rules, and verdicts',
            'next': 'fw-shift',
            'concept': (
                'A firewall is a decision made per packet: accept it, drop it, '
                'or reject it. The machinery that makes that decision lives in '
                'the Linux kernel and is called netfilter, and understanding '
                'three things about it removes most of the mystery.\n\n'
                'First, **hooks**. A packet does not appear at one gate; it '
                'passes fixed points on its way through the kernel, and rules '
                'attach to those points. The ones that matter are `input` '
                '(packets destined for this host), `output` (packets this host '
                'sends), and `forward` (packets routed *through* this host, '
                'which is what a router or a container host does). A rule for '
                'protecting your own machine lives on the input hook; a rule '
                'for traffic passing through lives on forward. Putting a rule '
                'on the wrong hook is why it seems to do nothing.\n\n'
                'Second, **rules in order**. At each hook the packet is checked '
                'against a list of rules from top to bottom, and the first rule '
                'that matches decides its fate. Order is therefore meaning: a '
                'broad drop above a specific accept blocks the thing you meant '
                'to allow. If nothing matches, a **default policy** applies, '
                'and the safe default for an input chain is to drop, then allow '
                'only what you name.\n\n'
                'Third, **drop versus reject**. Drop discards the packet '
                'silently, so the sender waits and times out, which is what you '
                'want facing the internet because it gives an attacker nothing. '
                'Reject sends back an error saying no, which is friendlier on a '
                'trusted network because a client fails fast instead of '
                'hanging. Same block, two manners.'
            ),
            'examples': [
                {
                    'label': 'Where rules attach',
                    'code': ('a packet for THIS host   -> input hook\n'
                             'a packet FROM this host  -> output hook\n'
                             'a packet routed THROUGH  -> forward hook\n'
                             '\n'
                             'at each hook: rules top to bottom, first match '
                             'wins,\n'
                             '              then the default policy'),
                    'note': 'Protecting your own machine is the input hook. '
                            'A wrong-hook rule silently does nothing.',
                },
                {
                    'label': 'The two ways to say no',
                    'code': ('drop     discard silently, sender times out\n'
                             'reject   send back an error, sender fails fast\n'
                             '\n'
                             'facing the internet:  drop (give nothing away)\n'
                             'on a trusted LAN:     reject (fail fast)'),
                    'note': 'Same block. Drop is quiet, reject is polite. The '
                            'choice is about who is on the other side.',
                },
            ],
            'misconceptions': [
                'Rule order is not cosmetic. First match wins, so a broad drop '
                'placed above a specific accept blocks the traffic you meant to '
                'permit.',
                'A rule on the wrong hook does nothing useful. Traffic to your '
                'host is filtered on input, not on forward, which only sees '
                'routed traffic.',
                'Drop and reject both block, but a dropped packet leaves the '
                'sender hanging while a rejected one gets a fast error. Facing '
                'the internet, silence is usually better.',
            ],
            'try_it': [
                'On a machine you own, run `sudo nft list ruleset` (or `sudo '
                'iptables -L -n`) and just read what hooks and default policies '
                'are already in place.',
            ],
        },
        {
            'id': 'fw-shift',
            'title': 'iptables and nftables: two front-ends, one framework',
            'next': 'fw-rules',
            'concept': (
                'Both iptables and nftables are ways to write rules for the '
                'same kernel framework, and you will meet both, so it is worth '
                'knowing how they differ and why the world is moving.\n\n'
                '**iptables** is the old one and still everywhere. Its model is '
                'a fixed set of tables (`filter` for allow/deny, `nat` for '
                'address translation, `mangle` for packet edits) each with '
                'built-in chains named in capitals (`INPUT`, `OUTPUT`, '
                '`FORWARD`). You append a rule with `-A`, match with flags like '
                '`-p tcp --dport 22`, and set the verdict with `-j ACCEPT`. IPv4 '
                'and IPv6 are separate commands, `iptables` and `ip6tables`, '
                'which means every rule is written twice.\n\n'
                '**nftables** replaces all of that with one command, `nft`, and '
                'one framework. You create your own tables and chains rather '
                'than living inside fixed ones, an `inet` family handles IPv4 '
                'and IPv6 together, rules load atomically so a half-applied '
                'ruleset cannot lock you out mid-change, and it adds sets and '
                'maps that iptables never had. Under the hood, modern '
                '`iptables` is itself a compatibility shim that talks to the '
                'nftables engine.\n\n'
                'The practical stance: learn the nftables model, because it is '
                'the one the kernel actually uses now and the one new systems '
                'are written in. Keep enough iptables to read the rules you '
                'will inherit on older machines, and know that `iptables-'
                'translate` will convert a line for you when you need it.'
            ),
            'examples': [
                {
                    'label': 'The same rule, both dialects',
                    'code': ('iptables:\n'
                             '  iptables -A INPUT -p tcp --dport 22 -j ACCEPT\n'
                             '\n'
                             'nftables:\n'
                             '  nft add rule inet filter input tcp dport 22 '
                             'accept'),
                    'note': 'Same effect. iptables lives in fixed chains; '
                            'nftables uses tables and chains you created.',
                },
                {
                    'label': 'What nftables unifies',
                    'code': ('iptables + ip6tables    two commands, v4 and v6\n'
                             'nft, family inet         one ruleset, both\n'
                             '\n'
                             'iptables-translate -A INPUT -p tcp --dport 22 '
                             '-j ACCEPT\n'
                             '  -> prints the nft equivalent'),
                    'note': 'iptables-translate converts a line to nftables, '
                            'which is how you migrate a ruleset a piece at a '
                            'time.',
                },
            ],
            'misconceptions': [
                'nftables is not a different firewall from iptables. Both drive '
                'the same netfilter engine; modern iptables is a shim over the '
                'nft one.',
                'iptables treats IPv4 and IPv6 as separate worlds, so a rule '
                'set that only uses `iptables` leaves IPv6 wide open. The inet '
                'family in nftables fixes that.',
                'You do not have to pick one and rewrite everything. Read '
                'iptables where you find it, write nftables where you can, and '
                'translate between them.',
            ],
            'try_it': [
                'Run `iptables-translate -A INPUT -p tcp --dport 443 -j ACCEPT` '
                'and read the nftables line it prints.',
            ],
        },
        {
            'id': 'fw-rules',
            'title': 'Writing nftables rules',
            'next': 'fw-stateful',
            'concept': (
                'An nftables ruleset is built from three things, and you create '
                'all of them yourself rather than filling in fixed ones. A '
                '**table** is a container, named and given a family: `inet` for '
                'IPv4 and IPv6 together is the usual choice. A **chain** holds '
                'rules; a base chain also declares a hook, a priority, and a '
                'policy, which is what connects it to the packet path. A '
                '**rule** is a set of matches followed by a verdict.\n\n'
                'So a minimal firewall is: create an inet table, add a chain to '
                'it that hooks `input` with `policy drop`, and add rules that '
                '`accept` the specific traffic you want. Everything not '
                'accepted falls through to the drop policy. The chain '
                'declaration reads `type filter hook input priority 0; policy '
                'drop;`, and while that line looks dense, it is just saying '
                '"this chain filters packets arriving for this host, and blocks '
                'by default".\n\n'
                'Matches are how a rule selects packets. The common ones are '
                '`ip saddr` and `ip daddr` for source and destination address, '
                '`tcp dport` and `udp dport` for ports, `iifname` and `oifname` '
                'for the interface a packet came in or is leaving on, and '
                '`icmp type` for ping and friends. Matches on the same rule are '
                'ANDed together, so `tcp dport 22 ip saddr 10.0.0.0/8 accept` '
                'means SSH, but only from that network.\n\n'
                'Verdicts end a rule: `accept`, `drop`, `reject`, or `jump '
                'chainname` to hand off to a chain of your own for '
                'organisation. `counter` before a verdict tallies how many '
                'packets hit the rule, which is invaluable when you are working '
                'out whether a rule is doing anything.'
            ),
            'examples': [
                {
                    'label': 'A ruleset, top to bottom',
                    'code': ('table inet filter {\n'
                             '  chain input {\n'
                             '    type filter hook input priority 0; policy '
                             'drop;\n'
                             '    iif lo accept\n'
                             '    tcp dport 22 accept\n'
                             '    tcp dport { 80, 443 } accept\n'
                             '  }\n'
                             '}'),
                    'note': 'Create the table and chain, hook input, drop by '
                            'default, then accept the few things you want. A '
                            'set { 80, 443 } is one rule.',
                },
                {
                    'label': 'Matches are ANDed; counter helps',
                    'code': ('tcp dport 22 ip saddr 10.0.0.0/8 accept\n'
                             '  SSH, but only from that network\n'
                             '\n'
                             'tcp dport 3306 counter drop\n'
                             '  block MySQL and count the attempts'),
                    'note': 'Matches on one rule combine with AND. counter '
                            'tallies hits, which is how you see if a rule '
                            'fires.',
                },
            ],
            'misconceptions': [
                'A base chain needs a hook and a policy, or it filters nothing. '
                'A chain with no `hook` line is a regular chain you jump to, '
                'not one packets traverse on their own.',
                'Matches on the same rule are ANDed, not ORed. For "port 80 or '
                '443" use a set, `tcp dport { 80, 443 }`, not two conditions on '
                'one rule.',
                '`priority 0` is not arbitrary. Lower numbers run earlier, and '
                'the number is how nftables orders chains that share a hook.',
            ],
            'try_it': [
                'Write the input ruleset above into a file, then read it back '
                'and trace which packets each line would accept.',
            ],
        },
        {
            'id': 'fw-stateful',
            'title': 'Stateful filtering: connection tracking',
            'next': 'fw-nat',
            'concept': (
                'This is the idea that makes a firewall practical, and it is '
                'the one to hold above all the syntax. The kernel tracks '
                'connections, a facility called conntrack, so it knows whether '
                'a packet is starting a new connection, is part of one already '
                'established, is related to one, or is invalid. That lets you '
                'write the rule that almost every real firewall opens with: '
                'accept anything that belongs to a connection this host already '
                'allowed.\n\n'
                'Why that matters is subtle until you see it. When your machine '
                'makes a request out, the reply comes back *inbound*. Without '
                'connection tracking you would have to write a rule allowing '
                'that reply, for every service, guessing at ports, and it would '
                'be both huge and insecure. With it, one rule, `ct state '
                'established,related accept`, allows every reply to everything '
                'you started, and you never think about return traffic again. '
                'From then on your input chain only needs to permit **new** '
                'inbound connections, which is a short and deliberate list.\n\n'
                'So the canonical input chain has a shape worth memorising. '
                'Accept established and related first, because most packets '
                'match it and it is cheap. Accept loopback, because your own '
                'machine talks to itself constantly. Drop invalid packets. Then '
                'the specific new-connection allows: SSH, a web port, whatever '
                'this host serves. And the policy is drop, so anything else is '
                'silently refused.\n\n'
                '`related` is the quietly clever part: it covers connections '
                'that a tracked one spawns, like an FTP data channel or an ICMP '
                'error about an existing flow, which is why you accept it '
                'alongside established.'
            ),
            'examples': [
                {
                    'label': 'The canonical input chain',
                    'code': ('chain input {\n'
                             '  type filter hook input priority 0; policy '
                             'drop;\n'
                             '  ct state established,related accept\n'
                             '  ct state invalid drop\n'
                             '  iif lo accept\n'
                             '  tcp dport 22 accept\n'
                             '  meta l4proto { icmp, ipv6-icmp } accept\n'
                             '}'),
                    'note': 'Established first because most packets match it. '
                            'After that you only allow NEW inbound connections.',
                },
            ],
            'misconceptions': [
                'Without `ct state established,related accept`, replies to '
                'connections you started are blocked inbound, and it looks like '
                'the network is broken when it is your own firewall.',
                'You do not write a rule for return traffic per service. '
                'Connection tracking handles all of it with one line, so your '
                'rules only cover new inbound connections.',
                '`ct state invalid drop` is worth having: invalid packets are '
                'not part of any tracked connection and are almost always '
                'noise or an attack.',
            ],
            'try_it': [
                'Write an input chain that accepts established and related, '
                'accepts loopback, allows SSH, and drops everything else, then '
                'read it back and confirm return traffic is covered by one '
                'line.',
            ],
        },
        {
            'id': 'fw-nat',
            'title': 'NAT, sets, and what nftables does better',
            'next': 'fw-manage',
            'concept': (
                'Beyond allow and deny, a firewall rewrites addresses, and this '
                'is where the forward hook and the `nat` chains come in. '
                '**Masquerade** is the everyday one: it rewrites the source '
                'address of outbound packets to the machine\'s own, which is '
                'how many devices share one public address, and it is what a '
                'router or a container host does. **DNAT** rewrites the '
                'destination, which is port forwarding: traffic arriving on the '
                'host\'s port 8080 is sent on to an internal server. **SNAT** '
                'is masquerade with a fixed address. NAT rules live in chains '
                'hooked at `prerouting` (for DNAT, before the routing decision) '
                'and `postrouting` (for masquerade and SNAT, after it).\n\n'
                '**Sets** are the feature that most changes how you write '
                'rules. A set is a named group of addresses, ports or '
                'interfaces that a rule can match against, and you can update '
                'the set without touching the rules. So a `blocklist` set of '
                'addresses, matched by one rule, is maintained by adding and '
                'removing elements, which is how a fail2ban-style ban list '
                'works cleanly. Sets can be `dynamic`, updated by the ruleset '
                'itself, and can carry a timeout so entries expire on their '
                'own.\n\n'
                '**Maps** go one step further and associate a key with a '
                'value, including a verdict. A verdict map can say "port 80 '
                'goes to this chain, port 443 to that one" in a single rule, '
                'replacing a stack of jumps. Together, sets and maps are why an '
                'nftables ruleset for a complex setup is far shorter and more '
                'readable than the iptables equivalent, and they are the honest '
                'reason to prefer nftables beyond it simply being newer.'
            ),
            'examples': [
                {
                    'label': 'Sharing an address, and forwarding a port',
                    'code': ('chain postrouting {\n'
                             '  type nat hook postrouting priority 100;\n'
                             '  oifname "eth0" masquerade\n'
                             '}\n'
                             'chain prerouting {\n'
                             '  type nat hook prerouting priority -100;\n'
                             '  tcp dport 8080 dnat ip to 10.0.0.5:80\n'
                             '}'),
                    'note': 'masquerade on the way out shares an address; dnat '
                            'on the way in forwards a port to an internal host.',
                },
                {
                    'label': 'A blocklist as a set',
                    'code': ('set blocklist {\n'
                             '  type ipv4_addr\n'
                             '  flags timeout\n'
                             '}\n'
                             'chain input {\n'
                             '  ip saddr @blocklist drop\n'
                             '}\n'
                             '\n'
                             'nft add element inet filter blocklist '
                             '{ 1.2.3.4 timeout 1h }'),
                    'note': 'One rule matches the set; you add and remove '
                            'addresses without editing rules, and timeout '
                            'expires them.',
                },
            ],
            'misconceptions': [
                'DNAT belongs on prerouting and masquerade on postrouting, '
                'because one rewrites the destination before routing and the '
                'other the source after. Swapping them does nothing.',
                'A set is not just a shorthand. It can be updated live and can '
                'expire entries on a timeout, which is how a ban list is '
                'maintained without reloading the ruleset.',
                'Enabling forwarding in the firewall is not enough for a router '
                'to route: `net.ipv4.ip_forward` also has to be turned on in '
                'the kernel.',
            ],
            'try_it': [
                'Write a ruleset with a timeout-flagged blocklist set and a '
                'rule that drops its members, then add an element with a '
                'one-hour timeout.',
            ],
        },
        {
            'id': 'fw-manage',
            'title': 'Loading, persisting, and not locking yourself out',
            'next': 'fw-reading',
            'concept': (
                'Rules exist in two places: the running kernel, and a file on '
                'disk. `nft list ruleset` prints the whole running '
                'configuration, which is the first thing to run on any machine. '
                '`nft -f rules.nft` loads a ruleset file atomically, replacing '
                'or adding as the file says, and atomic means the whole file '
                'applies or none of it does, so you never end up half-blocked. '
                '`nft flush ruleset` clears everything, which is the reset '
                'button.\n\n'
                'Persistence is separate from loading. A ruleset loaded with '
                '`nft -f` is gone on reboot unless something reloads it, and '
                'the standard mechanism is the `nftables.service`, which loads '
                '`/etc/nftables.conf` at boot. So the workflow is: write your '
                'ruleset into that file, enable the service, and it survives a '
                'restart. iptables has the equivalent in `iptables-save` and a '
                'persistence package.\n\n'
                'The lesson that costs people a server is remote lockout. If '
                'you are configuring a firewall over SSH and your ruleset drops '
                'SSH, or you `flush` before you reload, the connection dies and '
                'you cannot get back in. The habit that saves you is a '
                'timeout: schedule a flush a couple of minutes out before you '
                'apply the risky change, so that if you lock yourself out the '
                'machine reverts on its own and you reconnect. `at now + 2 '
                'minutes` running an `nft flush ruleset`, cancelled once you '
                'confirm the new rules work, is the classic form. Never edit a '
                'remote firewall without an escape hatch already armed.'
            ),
            'examples': [
                {
                    'label': 'The load-and-persist workflow',
                    'code': ('nft list ruleset            what is running now\n'
                             'nft -f /etc/nftables.conf   load a file '
                             'atomically\n'
                             'nft flush ruleset           clear everything\n'
                             '\n'
                             'systemctl enable --now nftables\n'
                             '  loads /etc/nftables.conf at every boot'),
                    'note': 'Loading is not persisting. The service reloading '
                            'the file at boot is what makes rules survive.',
                },
                {
                    'label': 'An escape hatch before a risky change',
                    'code': ('echo "nft flush ruleset" | sudo at now + 2 minutes\n'
                             '  arm a revert\n'
                             'nft -f new-rules.nft\n'
                             '  apply the change; if you get locked out,\n'
                             '  the at job flushes in 2 minutes and you '
                             'reconnect\n'
                             'atrm <job>   cancel it once you confirm SSH still '
                             'works'),
                    'note': 'Never edit a remote firewall without a revert '
                            'already scheduled. This is the single most '
                            'expensive lesson to learn the hard way.',
                },
            ],
            'misconceptions': [
                'Loading a ruleset does not make it survive a reboot. Something '
                'has to reload the file at boot, which is what the nftables '
                'service does.',
                '`nft flush ruleset` on a remote machine with a default-drop '
                'policy can lock you out instantly, because it removes the rule '
                'allowing your SSH. Arm a revert first.',
                'nftables loads atomically, so a syntax error in the file '
                'leaves the running ruleset unchanged rather than half-applied. '
                'That is a safety feature worth relying on.',
            ],
            'try_it': [
                'On a local machine only, `nft list ruleset`, then load a small '
                'file with `nft -f`, then `nft flush ruleset`. Do this on a '
                'remote box only with an `at` revert armed.',
            ],
        },
        {
            'id': 'fw-reading',
            'title': 'Reading a firewall you inherited',
            'concept': (
                'Most of the time you are not writing a firewall from scratch, '
                'you are reading one someone else left, and the skill is '
                'turning a wall of rules into an understanding of what is '
                'allowed.\n\n'
                'For nftables, `nft list ruleset` is the whole thing, tables '
                'and chains and rules, and you read it the way you wrote it: '
                'find the base chains, note their hooks and default policies, '
                'then read the accepts. For iptables you will see `iptables -L '
                '-n -v --line-numbers`, where `-n` stops slow name lookups, '
                '`-v` shows the packet and byte counters, and the line numbers '
                'let you insert or delete a specific rule. `iptables-save` '
                'dumps the whole configuration in the format that reloads it, '
                'which is the honest full picture. The counters are the '
                'underused part: a rule with zero packets has never matched, '
                'which either means it is dead or that something above it is '
                'catching the traffic first.\n\n'
                'The question to answer when reading any firewall is short: '
                'what new inbound connections are permitted? Everything else is '
                'usually the established-and-related rule and the default drop. '
                'So you scan for the default policy, then for the accepts on '
                'the input or forward hook, and that list is the machine\'s '
                'exposed surface.\n\n'
                'And the framing that matters for a blue-team reader: a host '
                'firewall is defence in depth, not the whole defence. It '
                'reduces what an attacker can reach, it does not make the host '
                'safe on its own, and a service that must be exposed is exposed '
                'firewall or not. The firewall is one layer, and reading it '
                'tells you which layer of exposure you are actually looking at.'
            ),
            'examples': [
                {
                    'label': 'Reading both dialects',
                    'code': ('nft list ruleset            the whole nftables '
                             'config\n'
                             '\n'
                             'iptables -L -n -v --line-numbers\n'
                             '  -n no DNS, -v counters, line numbers to edit\n'
                             'iptables-save               the reloadable dump'),
                    'note': 'A rule with a zero packet counter has never '
                            'matched: either dead, or shadowed by a rule above '
                            'it.',
                },
            ],
            'misconceptions': [
                'A rule existing does not mean it fires. A zero counter means '
                'no packet ever matched it, often because an earlier rule '
                'caught them first.',
                '`iptables -L` without `-n` does reverse DNS on every address '
                'and can hang for a minute. Always add `-n` when reading.',
                'A host firewall is not the whole security story. It limits '
                'reachability; it does not patch the service behind an open '
                'port.',
            ],
            'try_it': [
                'On any machine, list the ruleset, find the default policy on '
                'the input hook, and write down the complete list of new '
                'inbound connections it allows.',
            ],
        },
    ],

    'drills': [
        # nftables
        {'id': 'fwd-nft-list', 'type': 'command', 'answer': 'nft list ruleset',
         'prompt': 'Print the entire running nftables configuration.',
         'teach': 'The first thing to run on any machine: every table, chain '
                  'and rule currently loaded.'},
        {'id': 'fwd-nft-addtable', 'type': 'command',
         'answer': 'nft add table inet filter',
         'prompt': 'Create an inet-family table called filter.',
         'teach': 'The inet family covers IPv4 and IPv6 together, which is why '
                  'it is the usual choice.'},
        {'id': 'fwd-nft-addchain', 'type': 'command',
         'answer': 'nft add chain inet filter input '
                   '{ type filter hook input priority 0 \\; policy drop \\; }',
         'prompt': 'Add an input base chain to inet filter that hooks input '
                   'and drops by default.',
         'teach': 'A base chain declares a hook, a priority and a policy. '
                  'Without a hook it filters nothing.'},
        {'id': 'fwd-nft-ssh', 'type': 'command',
         'answer': 'nft add rule inet filter input tcp dport 22 accept',
         'prompt': 'Add a rule accepting new SSH connections on port 22.',
         'teach': 'Matches then a verdict. This is the nftables equivalent of '
                  'iptables -A INPUT -p tcp --dport 22 -j ACCEPT.'},
        {'id': 'fwd-nft-ctstate', 'type': 'command',
         'answer': 'nft add rule inet filter input ct state '
                   'established,related accept',
         'prompt': 'Add the rule that accepts replies to connections this host '
                   'started.',
         'teach': 'The single most important firewall rule. Put it first, '
                  'because most packets match it.'},
        {'id': 'fwd-nft-set-ports', 'type': 'command',
         'answer': 'nft add rule inet filter input tcp dport { 80, 443 } accept',
         'prompt': 'Accept new connections on both port 80 and port 443 in one '
                   'rule.',
         'teach': 'An anonymous set { 80, 443 } is one rule. Two conditions on '
                  'one rule would be an AND, which matches nothing.'},
        {'id': 'fwd-nft-saddr', 'type': 'command',
         'answer': 'nft add rule inet filter input ip saddr 10.0.0.0/8 '
                   'tcp dport 22 accept',
         'prompt': 'Accept SSH, but only from the 10.0.0.0/8 network.',
         'teach': 'Matches on one rule are ANDed, so this is SSH and that '
                  'source network together.'},
        {'id': 'fwd-nft-lo', 'type': 'command',
         'answer': 'nft add rule inet filter input iif lo accept',
         'prompt': 'Accept all traffic on the loopback interface.',
         'teach': 'Your own machine talks to itself constantly. Forgetting '
                  'this rule breaks local services in confusing ways.'},
        {'id': 'fwd-nft-counter', 'type': 'command',
         'answer': 'nft add rule inet filter input tcp dport 3306 counter drop',
         'prompt': 'Drop connections to MySQL and count how many are '
                   'attempted.',
         'teach': 'counter before the verdict tallies hits, which is how you '
                  'tell whether a rule is doing anything.'},
        {'id': 'fwd-nft-reject', 'type': 'command',
         'answer': 'nft add rule inet filter input tcp dport 23 reject',
         'prompt': 'Reject telnet connections, sending back an error rather '
                   'than dropping silently.',
         'teach': 'reject fails the sender fast; drop leaves them hanging. The '
                  'choice depends on who is on the other side.'},
        {'id': 'fwd-nft-masq', 'type': 'command',
         'answer': 'nft add rule inet nat postrouting oifname "eth0" masquerade',
         'prompt': 'Masquerade outbound traffic leaving on eth0 so several '
                   'hosts share its address.',
         'teach': 'masquerade rewrites the source address on the way out, on '
                  'the postrouting hook. It is what a router does.'},
        {'id': 'fwd-nft-dnat', 'type': 'command',
         'answer': 'nft add rule inet nat prerouting tcp dport 8080 '
                   'dnat ip to 10.0.0.5:80',
         'prompt': 'Forward traffic arriving on port 8080 to port 80 on the '
                   'internal host 10.0.0.5.',
         'teach': 'DNAT rewrites the destination, on prerouting, before the '
                  'routing decision. This is port forwarding.'},
        {'id': 'fwd-nft-addset', 'type': 'command',
         'answer': 'nft add element inet filter blocklist { 1.2.3.4 timeout 1h }',
         'prompt': 'Add the address 1.2.3.4 to a blocklist set, expiring after '
                   'an hour.',
         'teach': 'A set is updated without editing rules, and a timeout '
                  'expires entries on their own. This is how a ban list works.'},
        {'id': 'fwd-nft-load', 'type': 'command',
         'answer': 'nft -f /etc/nftables.conf',
         'prompt': 'Load a ruleset from the file /etc/nftables.conf.',
         'teach': 'nft -f loads atomically: the whole file applies or none of '
                  'it does, so you cannot end up half-blocked.'},
        {'id': 'fwd-nft-flush', 'type': 'command',
         'answer': 'nft flush ruleset',
         'prompt': 'Clear the entire running ruleset.',
         'teach': 'The reset button. On a remote machine with a drop policy '
                  'this can lock you out; arm a revert first.'},

        # iptables, which you will still meet
        {'id': 'fwd-ipt-list', 'type': 'command',
         'answer': 'iptables -L -n -v --line-numbers',
         'prompt': 'List the iptables filter rules without DNS lookups, with '
                   'counters and line numbers.',
         'teach': '-n stops slow name lookups, -v shows counters, line numbers '
                  'let you insert or delete a specific rule.'},
        {'id': 'fwd-ipt-accept', 'type': 'command',
         'answer': 'iptables -A INPUT -p tcp --dport 22 -j ACCEPT',
         'prompt': 'Append an iptables rule accepting SSH on the INPUT chain.',
         'teach': '-A appends, --dport matches the port, -j sets the verdict. '
                  'The chains are fixed and named in capitals.'},
        {'id': 'fwd-ipt-established', 'type': 'command',
         'answer': 'iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED '
                   '-j ACCEPT',
         'prompt': 'Append the iptables rule accepting established and related '
                   'connections.',
         'teach': 'The same stateful idea as nftables, spelled with -m state. '
                  'It belongs at the top of INPUT.'},
        {'id': 'fwd-ipt-policy', 'type': 'command',
         'answer': 'iptables -P INPUT DROP',
         'prompt': 'Set the default policy of the INPUT chain to DROP.',
         'teach': '-P sets the policy for packets that match no rule. Set it '
                  'to DROP only once your accept rules are in place.'},
        {'id': 'fwd-ipt-save', 'type': 'command',
         'answer': 'iptables-save',
         'prompt': 'Dump the whole iptables configuration in reloadable form.',
         'teach': 'The honest full picture, and the format iptables-restore '
                  'reads back.'},
        {'id': 'fwd-ipt-translate', 'type': 'command',
         'answer': 'iptables-translate -A INPUT -p tcp --dport 22 -j ACCEPT',
         'prompt': 'Convert an iptables SSH-accept rule to its nftables form.',
         'teach': 'How you migrate a ruleset a line at a time rather than '
                  'rewriting it all at once.'},

        # the safety habit
        {'id': 'fwd-escape-hatch', 'type': 'command',
         'answer': 'echo "nft flush ruleset" | sudo at now + 2 minutes',
         'prompt': 'Arm a revert that will flush the ruleset in two minutes, '
                   'before a risky remote change.',
         'teach': 'If a change locks you out over SSH, this flushes the '
                  'firewall and lets you reconnect. Cancel it with atrm once '
                  'the change is confirmed.'},
        {'id': 'fwd-ipforward', 'type': 'command',
         'answer': 'sysctl -w net.ipv4.ip_forward=1',
         'prompt': 'Turn on IPv4 forwarding in the kernel so this host can '
                   'route.',
         'teach': 'A forward-hook firewall rule is not enough on its own; the '
                  'kernel also has to be told it may forward packets.'},
        {'id': 'fwd-nft-handles', 'type': 'command',
         'answer': 'nft -a list ruleset',
         'prompt': 'List the ruleset with the handles needed to delete a rule.',
         'teach': 'Without -a there are no handles, and a handle is the only way to name one rule for deletion.'},
        {'id': 'fwd-nft-delete', 'type': 'command',
         'answer': 'nft delete rule inet filter input handle 7',
         'prompt': 'Delete one rule by its handle, leaving the rest alone.',
         'teach': 'The third real task after add and list. Get the handle from nft -a list ruleset first.'},
        {'id': 'fwd-ipt-delete', 'type': 'command',
         'answer': 'iptables -D INPUT 3',
         'prompt': 'Delete rule number 3 from the iptables INPUT chain.',
         'teach': 'Numbers shift as soon as you delete one, so re-read with --line-numbers between deletions.'},
    ],

    'challenges': [
        {
            'id': 'fwc-host-firewall',
            'title': 'Write a sane host firewall',
            'goal': 'The ruleset almost every server wants: default drop, '
                    'stateful accept, loopback, and a couple of services.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {'.keep': ''}},
            'solution': {'shell':
                'cat > host.nft <<\'EOF\'\n'
                'table inet filter {\n'
                '  chain input {\n'
                '    type filter hook input priority 0; policy drop;\n'
                '    ct state established,related accept\n'
                '    ct state invalid drop\n'
                '    iif lo accept\n'
                '    meta l4proto { icmp, ipv6-icmp } accept\n'
                '    tcp dport 22 accept\n'
                '    tcp dport { 80, 443 } accept\n'
                '  }\n'
                '  chain forward { type filter hook forward priority 0; '
                'policy drop; }\n'
                '  chain output { type filter hook output priority 0; '
                'policy accept; }\n'
                '}\n'
                'EOF'},
            'steps': [
                {'instruction': 'Create an inet filter table with an input '
                                'chain hooked input and policy drop.',
                 'hint': 'type filter hook input priority 0; policy drop;'},
                {'instruction': 'Put the stateful accept first, then drop '
                                'invalid, then accept loopback and icmp.',
                 'hint': 'ct state established,related accept'},
                {'instruction': 'Accept new connections on SSH and on 80 and '
                                '443, the latter as a set.',
                 'hint': 'tcp dport { 80, 443 } accept'},
                {'instruction': 'Add forward (drop) and output (accept) base '
                                'chains so every hook is covered.'},
            ],
            'free': 'Produce host.nft: an inet filter table whose input chain '
                    'drops by default, accepts established/related first, '
                    'accepts loopback, and allows SSH plus 80 and 443.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'host.nft': [
                    'table inet filter', 'hook input', 'policy drop',
                    'established,related accept', 'iif lo accept',
                    'tcp dport 22 accept', '{ 80, 443 }']}}},
            'fallback': 'self',
        },
        {
            'id': 'fwc-blocklist',
            'title': 'A blocklist you can update without editing rules',
            'goal': 'Use a set so that banning an address is adding an '
                    'element, not rewriting the ruleset.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {'.keep': ''}},
            'solution': {'shell':
                'cat > block.nft <<\'EOF\'\n'
                'table inet filter {\n'
                '  set blocklist {\n'
                '    type ipv4_addr\n'
                '    flags timeout\n'
                '  }\n'
                '  chain input {\n'
                '    type filter hook input priority 0; policy drop;\n'
                '    ct state established,related accept\n'
                '    iif lo accept\n'
                '    ip saddr @blocklist drop\n'
                '    tcp dport 22 accept\n'
                '  }\n'
                '}\n'
                'EOF'},
            'steps': [
                {'instruction': 'Declare a set named blocklist of ipv4_addr '
                                'with the timeout flag so entries can expire.',
                 'hint': 'set blocklist { type ipv4_addr; flags timeout; }'},
                {'instruction': 'In the input chain, drop any packet whose '
                                'source is in the set.',
                 'hint': 'ip saddr @blocklist drop'},
                {'instruction': 'Note that banning an address is now `nft add '
                                'element ... blocklist { 1.2.3.4 timeout 1h }`, '
                                'with no rule change.'},
            ],
            'free': 'Produce block.nft with a timeout-flagged blocklist set '
                    'and an input rule that drops any source address in it.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'block.nft': ['set blocklist',
                                                'type ipv4_addr',
                                                'flags timeout',
                                                'ip saddr @blocklist drop']}}},
            'fallback': 'self',
        },
        {
            'id': 'fwc-portforward',
            'title': 'Forward a port and share an address',
            'goal': 'The NAT half: masquerade outbound traffic and DNAT an '
                    'inbound port to an internal host.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {'.keep': ''}},
            'solution': {'shell':
                'cat > nat.nft <<\'EOF\'\n'
                'table inet nat {\n'
                '  chain prerouting {\n'
                '    type nat hook prerouting priority -100;\n'
                '    tcp dport 8080 dnat ip to 10.0.0.5:80\n'
                '  }\n'
                '  chain postrouting {\n'
                '    type nat hook postrouting priority 100;\n'
                '    oifname "eth0" masquerade\n'
                '  }\n'
                '}\n'
                'EOF'},
            'steps': [
                {'instruction': 'Create a nat table with a prerouting chain '
                                'that DNATs port 8080 to 10.0.0.5:80.',
                 'hint': 'type nat hook prerouting priority -100; then dnat '
                         'to 10.0.0.5:80'},
                {'instruction': 'Add a postrouting chain that masquerades '
                                'traffic leaving on eth0.',
                 'hint': 'type nat hook postrouting priority 100; oifname '
                         '"eth0" masquerade'},
                {'instruction': 'Note that routing this traffic also needs '
                                'net.ipv4.ip_forward turned on in the kernel.'},
            ],
            'free': 'Produce nat.nft with a prerouting DNAT of port 8080 to '
                    '10.0.0.5:80 and a postrouting masquerade on eth0.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'nat.nft': ['hook prerouting',
                                              'dnat ip to 10.0.0.5:80',
                                              'hook postrouting',
                                              'masquerade']}}},
            'fallback': 'self',
        },
        {
            'id': 'fwc-translate',
            'title': 'Read an iptables ruleset and port it',
            'goal': 'You inherited iptables rules. Read them, and write the '
                    'nftables equivalent by hand.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'old-rules.txt':
                    '# inherited iptables ruleset\n'
                    'iptables -P INPUT DROP\n'
                    'iptables -A INPUT -m state --state ESTABLISHED,RELATED '
                    '-j ACCEPT\n'
                    'iptables -A INPUT -i lo -j ACCEPT\n'
                    'iptables -A INPUT -p tcp --dport 22 -j ACCEPT\n'
                    'iptables -A INPUT -p tcp --dport 443 -j ACCEPT\n'}},
            'solution': {'shell':
                'cat > new.nft <<\'EOF\'\n'
                'table inet filter {\n'
                '  chain input {\n'
                '    type filter hook input priority 0; policy drop;\n'
                '    ct state established,related accept\n'
                '    iif lo accept\n'
                '    tcp dport 22 accept\n'
                '    tcp dport 443 accept\n'
                '  }\n'
                '}\n'
                'EOF'},
            'steps': [
                {'instruction': 'Read old-rules.txt and note the default '
                                'policy and each accept.',
                 'hint': 'cat old-rules.txt'},
                {'instruction': 'Write new.nft as an inet filter input chain '
                                'that reproduces every one of those decisions.',
                 'hint': 'policy drop, established/related, loopback, then the '
                         'two ports'},
                {'instruction': 'Confirm nothing was lost: same default, same '
                                'stateful rule, same allowed ports.'},
            ],
            'free': 'Produce new.nft, an nftables input chain that exactly '
                    'reproduces the inherited iptables ruleset in '
                    'old-rules.txt.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'new.nft': ['policy drop',
                                              'established,related accept',
                                              'iif lo accept',
                                              'tcp dport 22 accept',
                                              'tcp dport 443 accept']}}},
            'fallback': 'self',
        },
        {
            'id': 'fwc-live',
            'title': 'Load a firewall live, safely',
            'goal': 'The sandbox only checked the file. Loading it into the '
                    'kernel needs root, so this is on a machine you own, with '
                    'an escape hatch armed.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'On a LOCAL machine, or a remote one only with '
                                'a revert armed, first read the current '
                                'ruleset so you can restore it.',
                 'hint': 'sudo nft list ruleset > before.nft'},
                {'instruction': 'If remote, arm the escape hatch NOW, before '
                                'anything else.',
                 'hint': 'echo "nft flush ruleset" | sudo at now + 2 minutes'},
                {'instruction': 'Load your host firewall file atomically and '
                                'confirm it is running.',
                 'hint': 'sudo nft -f host.nft; sudo nft list ruleset'},
                {'instruction': 'From another machine, confirm the allowed '
                                'ports answer and a blocked one does not '
                                '(a scan from the nmap module is the check).'},
                {'instruction': 'Confirm SSH still works, then cancel the '
                                'revert with atrm. Persist it by putting it in '
                                '/etc/nftables.conf and enabling the service.'},
            ],
            'free': 'On your own machine: arm a revert, load a ruleset live, '
                    'verify allowed and blocked ports from outside, then '
                    'persist it and cancel the revert.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
    ],

    'quiz': [
        {'id': 'fwq-hook', 'type': 'mcq',
         'prompt': 'You want to filter traffic destined for this host. Which '
                   'hook?',
         'answer': 'input',
         'distractors': ['forward', 'output', 'prerouting'],
         'teach': 'input is traffic for this host, output is from it, forward '
                  'is routed through it. A wrong-hook rule does nothing.'},
        {'id': 'fwq-order', 'type': 'mcq',
         'prompt': 'A specific accept rule for port 22 seems ignored. What is '
                   'the likely cause?',
         'answer': 'A broader drop rule sits above it, and first match wins.',
         'distractors': ['Port 22 is reserved and cannot be matched.',
                         'The rule needs to be on the output hook.',
                         'nftables evaluates rules bottom to top.'],
         'teach': 'Rules are checked top to bottom and the first match decides. '
                  'Order is meaning.'},
        {'id': 'fwq-stateful', 'type': 'mcq',
         'prompt': 'What does `ct state established,related accept` let you '
                   'avoid writing?',
         'answer': 'A rule for the return traffic of every connection you '
                   'start.',
         'distractors': ['The default drop policy.',
                         'Rules for outbound connections.',
                         'The loopback accept.'],
         'teach': 'Connection tracking handles all return traffic in one line, '
                  'so your rules only cover new inbound connections.'},
        {'id': 'fwq-drop-reject', 'type': 'mcq',
         'prompt': 'Why prefer drop over reject on an internet-facing input '
                   'chain?',
         'answer': 'Drop is silent, so an attacker learns nothing; reject '
                   'confirms the host is there.',
         'distractors': ['Drop is faster to process.',
                         'Reject is not valid on the input hook.',
                         'Drop also blocks outbound traffic.'],
         'teach': 'Same block, different manner. Silence gives a scanner '
                  'nothing; a fast error is friendlier on a trusted network.'},
        {'id': 'fwq-set', 'type': 'mcq',
         'prompt': 'Why match a blocklist with a set rather than one drop rule '
                   'per address?',
         'answer': 'A set can be updated live and can expire entries, without '
                   'touching the rules.',
         'distractors': ['A set is faster to type once.',
                         'Rules cannot match IP addresses directly.',
                         'Sets are the only thing that works with drop.'],
         'teach': 'One rule matches the set; adding and removing addresses is '
                  'separate, which is how a ban list is maintained cleanly.'},
        {'id': 'fwq-inet', 'type': 'mcq',
         'prompt': 'A ruleset written only with `iptables` protects IPv4. What '
                   'about IPv6?',
         'answer': 'It is unprotected; iptables and ip6tables are separate, and '
                   'nftables\' inet family is what covers both.',
         'distractors': ['IPv6 is covered automatically.',
                         'IPv6 does not need a firewall.',
                         'iptables blocks IPv6 by default.'],
         'teach': 'This is a real and common gap: a v4-only ruleset leaves v6 '
                  'wide open.'},
        {'id': 'fwq-nat-hook', 'type': 'mcq',
         'prompt': 'Where does a DNAT (port forward) rule belong?',
         'answer': 'prerouting, so the destination is rewritten before the '
                   'routing decision.',
         'distractors': ['postrouting, after routing.',
                         'input, since it changes incoming traffic.',
                         'output, since it changes where traffic goes.'],
         'teach': 'DNAT rewrites the destination on prerouting; masquerade and '
                  'SNAT rewrite the source on postrouting.'},
        {'id': 'fwq-atomic', 'type': 'mcq',
         'prompt': 'A ruleset file loaded with `nft -f` has a syntax error '
                   'halfway down. What happens?',
         'answer': 'Nothing changes; the load is atomic, so a bad file leaves '
                   'the running ruleset untouched.',
         'distractors': ['The rules above the error apply and the rest do '
                         'not.',
                         'The whole ruleset is flushed.',
                         'The error is skipped and loading continues.'],
         'teach': 'Atomic loading is a safety feature: you cannot end up '
                  'half-configured from a typo.'},
        {'id': 'fwq-lockout', 'type': 'mcq',
         'prompt': 'What does `nft flush ruleset` leave a remote machine in?',
         'answer': 'No firewall at all: it removes every table, drop policies '
                   'included.',
         'distractors': ['Locked out, because your SSH accept rule is gone.',
                         'Its saved ruleset from /etc/nftables.conf.',
                         'Exactly what it had, until you reload.'],
         'teach': 'Flush takes the drop policy with everything else, which is '
                  'why it works as the escape hatch and why it is not what '
                  'locks you out. The classic lockout is `iptables -F`, which '
                  'deletes your accepts and keeps the DROP policy.'},
        {'id': 'fwq-counter', 'type': 'mcq',
         'prompt': 'A rule in an inherited ruleset has a zero packet counter. '
                   'What does that tell you?',
         'answer': 'No packet has ever matched it: it is dead, or a rule above '
                   'catches the traffic first.',
         'distractors': ['The rule is disabled.',
                         'The counter is broken.',
                         'The rule matches only outbound traffic.'],
         'teach': 'Counters are the underused part of reading a firewall. Zero '
                  'means the rule never fired.'},
    ],
}
