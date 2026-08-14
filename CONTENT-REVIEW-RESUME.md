# Content review: closed

The deep review of every module, and the backlog it produced, are **both
finished**. Nothing here is outstanding. Kept as the record of what was found
and what was decided, because the reasoning is worth more than the diff.

Tree state at close: 50 modules, `validate.py --lint` clean, `test.py` 11000
checks green, dist rebuilt, pushed to `SageSchiller/hone`.

---

## What the review was

Nine cold-reader agents read all 46 modules (as it then was) against four
dimensions: clear, accurate, beginner-friendly, fun. Each ran the real tools
rather than judging from the text. sqlite, tcpdump, tshark, nft, iptables,
strace, pwsh, jq, git, openssl, gpg, coreutils and a throwaway volatility3
install were all exercised; one agent read the author's actual Doom and magit
source.

## The worst class of finding, and it recurred

**Seven quizzes keyed a false answer as correct** while a distractor was true,
which trains a diligent student into the misconception. In tcpdump (x2), sql
(x2), firewall, vim and org. All re-keyed, along with the lesson prose,
examples and drill teaches that repeated the same falsehood.

The load-bearing ones were re-verified by hand rather than taken on trust:
`tcpdump -d` proves `not tcp port 22` and `not (tcp port 22)` compile
identically; a single `-n` already suppresses port names; `org-metaright`
demotes a heading and orphans its children while `org-shiftmetaright` carries
the subtree; `git restore` reads from the index and `--source=HEAD` from HEAD.

## Four commands graded correct that failed when run

firewall's `dnat to` needs the `ip` keyword in the inet family; its canonical
ruleset matched IPv4 ICMP only and so broke IPv6 under `policy drop`; its
`at`-armed escape hatch ran unprivileged and silently did not exist; docker's
multistage build ran `go build .` with no go.mod. Plus **every** taught
gobuster `-s` command aborted on current gobuster, which ships a 404 blacklist
and refuses `-s` alongside it (confirmed later against the real binary, with
the exact error text predicted).

## Two challenges that taught the opposite of their lesson

The sandbox could only write UTF-8 text, so magic-byte fixtures were mangled: a
PNG's `0x89` became `C2 89`, and a learner ran `file` on a "PNG" and saw
*Unicode text*. Grading passed green because the checks only read the ASCII
tail. Fixed at the root with a `b64` tree value written as raw bytes; the file
and xxd challenges now carry a real PNG and a real ZIP.

## A latent bug class, now permanently guarded

Five dead duplicate `next` keys had accumulated across bash, linux, python,
doom and org, each the signature of a lesson inserted after the fact. Python
keeps the last value silently, so nothing could see them and the chains
happened to still work. `validate.py` gained `check_duplicate_keys`, which
parses the source with `ast`. It caught the last two while the first three were
being fixed, and later caught a second `examples` key being added to a dig
lesson.

## The backlog, all closed

- **sql's capstone-blocking gap**: the browser-history payoff needed a
  timestamp conversion the module never taught. Now all three epochs, three
  drills, and a challenge that converts a Chrome time as if it were Firefox so
  the resulting 2394 date is recognised as a units bug rather than evidence.
- **Eight duplicate challenge pairs** cut (bash, linux, vim, doom, org x2,
  tmux, git). Each was the same exercise twice with cosmetic differences.
- **Security group renumbered 70 to 94** in one deliberate pass, checked
  against the prereq graph so dfirwin now precedes mimikatz, which declares it.
  An earlier spot fix had to be reverted for creating fresh collisions.
- **Roughly thirty content gaps and corrections**: ssh (`-R`, `-i`, no-agent,
  and a challenge that now checks the file its steps asked for), scp/rsync
  (`--exclude`, the `-P` collision, the slash rule being rsync's alone), dig
  (`status:` and `;; SERVER:`, a documentation-range address), awk
  (sub/gsub/printf/-v), jq (interpolation, sort_by, group_by), hashing (md5sum),
  stat (`%a`), firewall (rule deletion, conntrack), tcpdump (`-D`, `-A`, the
  `-W` ring claim), docker (`cp`, `start`, 0.0.0.0 binding), powershell
  (Import-Csv), openssl (`-legacy`), ldapsearch (objectCategory), smbenum
  (placeholder SID), netexec (ntpdate), msf (an unverifiable prefix removed),
  plus jargon definitions in ncsocat, xfreerdp and doom.

Every new drill answer was run against the real tool before it went in.

## Verified clean, no action needed

**openssl** and **gpg** were machine-verified end to end as exemplary: zero
accuracy issues between them. **strace** and **mimikatz** came back clean.
**regex** and **git** quizzes were checked item by item and are sound. The
house voice was judged to be working everywhere: no agent found a lifeless
stretch, so it was not sanded.

## Still knowledge-verified only

**netexec** and **msf** could not be exercised offline. Their flag sets and
output formats are from knowledge, not execution, and would benefit from a live
pass on a lab domain.
