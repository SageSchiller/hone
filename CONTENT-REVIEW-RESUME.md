# Content review: what is left (2026-08-13)

The review itself is **COMPLETE**. All 46 modules were read by cold-reader agents
against four dimensions (clear, accurate, beginner-friendly, fun), each running the
real tools. Every accuracy defect found is FIXED and recorded in HONE-PLAN.md (aj).

Tree state: `validate.py --lint` clean, `test.py` 9997 green, dist rebuilt.

What follows is the deliberately deferred remainder: no factual errors, no broken
commands. These are gaps, duplication and one structural chore.

---

## 1. Duplicate challenge pairs (a merge artifact, seven of them)
Same exercise twice with only cosmetic differences. Cut one of each, or repoint the
survivor at something uncovered (suggestions in the last column).

| Module | Pair | Repoint idea |
|---|---|---|
| bash | `sh-spaces` / `sh-quoting-spaces` | an unquoted variable in a `[ ]` test |
| linux | `lx-redirect` / `lx-streams` | `>>` or `2>&1` |
| vim | `vim-swap-lines` / `vim-reorder` | `"+y` system clipboard, or `%` / `d%` |
| doom | `doom-multi-line` / `doom-macro-region` | workspaces, `SPC h k`, popup rules |
| org | `org-task-states` / `org-todo-cycle` | refile `C-c C-w`: drilled, no challenge |
| org | `org-checklist` / `org-checkboxes` | archive: drilled, no challenge |
| tmux | `tmux-window-workflow` / `tmux-named-windows` | sessions (`C-b s`, `tmux new -d`) |
| git | `g-branch-merge` / `g-branch-and-merge` | fast-forward vs `--no-ff` (taught, never exercised) |

## 2. Content gaps (a core feature a beginner needs, never taught)
- **ssh**: `ssh-keygen -R host` (the sanctioned known_hosts delete: told twice not to do
  it by reflex, never shown the right way); the no-agent case (`eval "$(ssh-agent -s)"`);
  `ssh -i key.pem` (the cloud-VM key, the first key most beginners are handed).
  Also `rm-known-hosts` requires meaning.txt in its steps but never checks it.
- **scprsync**: `--exclude` (the first real sync has .git/node_modules); the scp `-P`
  (port) vs rsync `-P` (progress) collision, and how rsync takes a port at all
  (`-e 'ssh -p 2222'`); "resumes" oversells plain rsync (needs `-P`); the scp `-r site/`
  example uses a source slash scp ignores, inside a module built on the slash rule.
- **dig**: reading `status:` (NXDOMAIN vs NOERROR+ANSWER:0) and the `;; SERVER:` footer,
  which literally answers the module's own recurring question; the example.com IP is
  stale (use 203.0.113.10); "class is always IN" one-liner.
- **sql**: timestamp conversion is capstone-blocking. The browser-history payoff needs
  `datetime(visit/1000000,'unixepoch')` plus the Chrome 1601-epoch offset, and the only
  example writes a literal ellipsis. Also `AS when` is a reserved-word parse error
  (use `AS visited`); sqlite silently uses the first row of a multi-row scalar subquery
  (the misconception claims it errors); `--csv` header handling only applies when the
  table does not exist yet; `LIKE` is ASCII-case-insensitive and never says so.
- **awk**: no substitution anywhere (`sub`/`gsub`/`printf`/`-v`) though `aj-awk-real`
  promises "reformat a line".
- **jq**: string interpolation `"\(.x)"` is load-bearing in four of six challenges and
  taught nowhere; `sort_by`/`group_by` appear in hints, never in a lesson. The module
  leans on awk as its reference frame but lists only regex as a prereq.
- **hydra**: no `http-post-form` drill (its hardest syntax, shown once); never teaches
  the `S=`/`F=` success-vs-failure rule, which is the fix for the very mistake it
  diagnoses; `^USER^`/`^PASS^` never explained as substitution tokens.
- **ffuf**: `wd-model`'s `-fs 0` only filters zero-byte responses, so it undercuts its
  own note (use a measured size); "no default filter" conflates filter with matcher
  (ffuf ships a default matcher, so the noise is soft-404s answering 200).
- **docker**: published ports bind 0.0.0.0, not "the host" (`-p 127.0.0.1:8080:80` is
  the localhost-only form), and Docker punches past host firewall INPUT rules, which the
  firewall module should note too; `dkc-dockerfile` requires exec-form `CMD [` without
  saying so; `docker cp` and `docker start` are never drilled.
- **firewall**: deleting a single rule is never taught in either dialect
  (`nft -a list ruleset` then `nft delete rule ... handle N`; `iptables -D`), though
  `fw-reading` sells `--line-numbers` as letting you do exactly that.
  `fwd-ipt-established` uses the legacy `-m state --state` spelling.
- **tcpdump**: `-W` with `-G` limits the file count and exits, it is not a ring (the ring
  is `-C`+`-W`; a rolling day comes free from `%H` wrap); `greater 1000` is >= not >;
  `-D` (list interfaces) and `-A`/`-X` are never introduced.
- **hashing**: md5sum/sha1sum never typed though half the lesson is about MD5; the
  `sha256sum *` drill globs SHA256SUMS into itself on a rerun.
- **stat**: never shows `%a` octal permissions, the most common scripting use.
- **powershell**: Import-Csv and Set-Content carry many drills, no lesson introduces them.
- **file**: `trd-exiftool` is an orphan drill (exiftool taught nowhere, not in `needs`).
- **openssl**: `pkcs12 -export` on 3.x defaults to AES-256/PBKDF2 that old Windows and
  Java (the named consumers) cannot import: note `-legacy`. `osd-san` prints a misleading
  "No extensions in certificate" on a cert with other extensions but no SAN, which the
  module's own generated certs hit. `osd-modulus` shows only the cert side of the match
  test. `osd-rmpass` has a doubled word.
- **ldapsearch**: `(objectClass=user)` in AD also returns computer accounts; narrow with
  `(&(objectCategory=person)(objectClass=user))`.
- **smbenum**: `sa-rpc` uses a placeholder domain SID; get the real one via
  `rpcclient -c lsaquery` first. `sad-smb-get` shows `;`-joined commands as if typed at
  the interactive prompt, but that is a `-c` feature.
- **netexec**: `ntpdate` is deprecated and absent on modern distros. The whole module is
  knowledge-verified only (nxc was not installable here): it wants a live pass.
- **msf**: `[%]` is probably not a real msfconsole prefix; verify on a live console.

## 3. Clarity / jargon (undefined at first use)
ssh "bastion"; ncsocat "reverse shell", "pty", "raw mode", static vs dynamic linking,
"SOCKS"; xfreerdp `+x`/`-x` vs `/opt:value` sigil; dig "resolver", "TLD",
"split-horizon"; gpg never warns that interactive examples trigger a pinentry prompt;
doom describes `Tab` as "fold" where it expands, and shows `SPC s s` and `SPC s b` as two
capabilities when both are bound to the same command; tmux argues twice against rebinding
the prefix to `C-a` and then grades a challenge requiring it; hashcat restates the
`-m` vs `-a` warning about five times; awk's `aj-awk-accumulate` misconception is garbled
("not the data") and its single-quote misconception repeats across two consecutive
lessons; linuxutils has "newest sorted" (nothing there is about age), a drill saying three
timestamps where the lesson says four, and an xxd-offset note that invites the wrong
inference that `-s` wants hex; strings' `trc-strings` fixture has doubled backslashes;
python's `py-control` "tabs and spaces always a syntax error and always has been" is
overstated (Py3 raises TabError only on inconsistent mixing; Py2 allowed it); org's
`org-capture` shows `\'((` with a stray backslash (invalid elisp) and its priority drill
says "cycles" where `C-c ,` prompts; org's `<s` tempo hint may not work at all, since
org-tempo is not in the author's Doom install.

## 4. Structural chore
**`order` collisions across the whole Security group.** Not just the artifact cluster:
openssl/gpg, hashcat, dfirwin, hydra/yara, ldapsearch/smbenum and msf/netexec all share
numbers, and the loader tie-breaks alphabetically. I tried a spot fix and it created new
collisions, so this needs one deliberate renumber of the entire group in teaching order.
Reverted to the shipped state for now.

---

## Verified clean, no action
**openssl** and **gpg** were machine-verified end to end as exemplary: zero accuracy
issues between them. **strace** and **mimikatz** came back clean. **regex** and **git**
quizzes were checked item by item and are sound. The house voice was judged to be working
everywhere: no agent found a lifeless stretch, so do not sand it.

## Guard added
`validate.py` now runs `check_duplicate_keys`, which parses the content source with `ast`
and fails on any dict literal that sets the same key twice. Five dead `next` keys had
accumulated and nothing could see them, because Python keeps the last value silently.
