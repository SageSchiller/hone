# Content quality plan

> **CLOSED 2026-08-15. Kept as the record of what the pass found and fixed, and
> as the rationale for `quality.py`, which stays as a re-runnable audit.** Every
> tier below is now empty: `quality.py` reports all 56 modules ok, with **0
> lessons under 900 characters** (was 98 of 318) and a median lesson length of
> ~1,457 chars. Nothing here is outstanding; re-run `quality.py` after adding a
> module and it will flag anything that regresses.

**Written 2026-08-15, after the author reported that modules still do not flow
and are not clear about what a tool is for.** The specific observation was that
newer lessons read long and clear while older ones are short and too direct.
That turned out to be measurable, and measuring it changed what the work is.

`quality.py` is the audit. Run it any time; the tiers below come straight out
of it.

---

## What the audit found

Four faults, in descending order of how much they hurt.

### 1. A third of all lessons are reference cards, not walkthroughs

**98 of 318 lessons are under 900 characters.** Below that a lesson states what
is true and moves on. That is the correct shape for a cheat sheet and the wrong
shape for the first time someone meets an idea.

The split is not random. It falls almost exactly along authorship age:

| | median lesson | thin lessons |
|---|---|---|
| Editors, Terminal, Linux, Text processing (oldest) | 600–770 chars | most of them |
| Security group (newest, written to one arc) | 1250–1530 chars | none |

`vim` has 10 of its 12 lessons under 900 characters. `doom` has 8 of 10. `org`
has 8 of 11. Those are the three modules the author actually sat down with.

### 2. Modules read as a list of facts, not a course

**36 of 51 modules contain zero cross-lesson references.** Not one lesson says
"now that you have a key", or "the next lesson is where that pays off", or
"this is the problem the previous lesson left open".

Every lesson begins cold, as though the reader arrived from nowhere. That is
the "does not flow" complaint exactly, and it is invisible to every check the
project had, because each lesson is individually fine.

### 3. The prose asserts more than it explains

Measured as causal connectives per thousand characters (`because`, `which is
why`, `the reason`, `rather than`, and so on). The roster averages **2.0**. The
lessons written this week average **5 to 7**, and read, by the author's own
account, noticeably better.

This is the difference between:

> `-a` preserves permissions and timestamps.

and

> `-a` preserves permissions and timestamps, **because** a copy whose metadata
> is subtly wrong is a copy you find out about much later.

Same fact. One of them teaches.

### 4. A beginner meets the roster in the wrong order

Groups are displayed in `order` sequence, which currently reads:

1. **Editors** (emacs, vim, doom, org)
2. Terminal (tmux)
3. Text processing (regex, awk, jq, sql)
4. **Linux** (linux, bash, …)
5. Version control · 6. Network · 7. Scripting · 8. Containers · 9. Security

Someone who has never opened a terminal is shown **Emacs first and Linux Basics
fourth**. The module that teaches what a prompt is sits below three groups that
assume it.

One hard violation alongside it: **`sql` (order 33) declares `linux` (order 40)
as a prereq**, so its stated prerequisite appears after it.

---

## The production standard

A module is production quality when all of this is true. These are the
thresholds `quality.py` enforces, so "done" is checkable rather than a matter
of opinion.

**Per lesson**
- At least 900 characters of concept prose; 1200–1800 is the target.
- At least 2 worked examples, 2 named misconceptions, 1 try-it line.
- Explanation density of 5 or better: the prose says why, not only what.

**Per module**
- Spread (longest lesson ÷ shortest) no worse than 2.5. A module where one
  lesson is five times another has been edited rather than written, and reads
  like it.
- Opens with a lesson that assumes nothing: what the tool is, what problem it
  solves, and what it is not.
- Ends on a capstone that is genuinely past the basics.
- Unbroken `next` chain covering every lesson, no orphans.
- **At least one explicit handoff per three lessons.** A lesson ends by naming
  the question it leaves open; the next one opens by answering it. This is the
  single cheapest fix for flow and nothing currently does it.
- At least 3 challenges and 4 quiz cards.

**Per curriculum**
- No module's prereq may have a higher `order` than the module itself.
- Group order follows dependency, not authorship.

---

## The work, in the order to do it

### Phase 0 — Curriculum order (small, do first)

Everything else is per module; this is the one change that alters what a
beginner sees on first launch.

- Renumber groups so the sequence is **Linux → Terminal → Text processing →
  Editors → Version control → Network → Scripting → Containers → Security**.
  Linux Basics becomes the first thing on the home screen.
- Fix `sql` (33) so it sits after `linux`.
- Re-run `audit.py` and `ramp.py`, which are order-sensitive through prereqs.

*Cost: an afternoon. Risk: low, it is `order` fields and a test update.*

### Phase 1 — The foundational thirteen (REWRITE)

These carry a beginner from nothing and are the worst written in the roster,
which is the whole problem in one sentence. They are also, with one exception,
the modules with no prereqs or only `linux`, so they are what a new student
meets first.

| module | group | lessons | median | thin | why it is here |
|---|---|---|---|---|---|
| `vim` | Editors | 12 | 617 | 10 | worst in roster; 12 lessons of assertions |
| `doom` | Editors | 10 | 600 | 8 | the module the author tested and bounced off |
| `org` | Editors | 11 | 677 | 8 | longest module, thinnest lessons |
| `bash` | Terminal | 10 | 630 | 8 | foundational, and terse throughout |
| `git` | Version control | 9 | 722 | 7 | model is good, explanation is not |
| `linux` | Linux | 10 | 698 | 7 | **the entry point to everything** |
| `python` | Scripting | 8 | 795 | 7 | reads as a reference for people who know Python |
| `regex` | Text processing | 8 | 637 | 6 | spread 4.4: two rewritten lessons beside six old ones |
| `linuxadv` | Linux | 7 | 823 | 7 | every lesson thin, none rewritten |
| `tcpdump` | Network | 7 | 749 | 6 | new opener sits on six terse lessons |
| `powershell` | Scripting | 7 | 824 | 5 | same shape |
| `tmux` | Terminal | 8 | 771 | 4 | two lessons deepened, six not |
| `jq` | Text processing | 5 | 734 | 4 | shortest of the Text group |

**Per module, the pass is:**

1. Bring every thin lesson to 1200+ characters by explaining the *why* that is
   currently assumed. Not padding: each thin lesson has a missing paragraph,
   and it is usually the mechanism ("what actually happens when you press
   this") or the failure mode ("here is how this goes wrong and what it looks
   like when it does").
2. Add the handoff sentences. Each lesson ends naming what it leaves open; the
   next opens by picking it up.
3. Top up examples to 2 minimum, misconceptions to 2, try-it to 1.
4. Bring challenges to 3 and quiz to 4 where short.
5. Re-run `quality.py` and confirm the module drops out of REWRITE.

*Cost: roughly half a day per module, so about a week of sessions. Do them in
the order listed: `linux` and `bash` first if the goal is the beginner path,
`vim`/`doom`/`org` first if the goal is fixing what was actually reported.*

**Recommended: `linux`, `bash`, `vim`, `doom` first.** That is the real
first-hour path for a new student, and it is where the reported confusion was.

### Phase 2 — DEEPEN (5 modules)

`ssh`, `awk`, `nmap`, `john`, `xfreerdp`.

Partly rewritten already and inconsistent as a result: `ssh` has a spread of
3.9 because two lessons were deepened this week and three were not. Same pass
as Phase 1 but only on the lessons still under 900, plus the handoffs.

*Cost: two to three hours each.*

### Phase 3 — POLISH (20 modules)

`linuxutils` `mimikatz` `emacs` `gobuster` `hydra` `hashing` `scprsync` `file`
`stat` `dig` `hashcat` `smbenum` `strace` `strings` `curl` `ffuf` `gpg`
`openssl` `sql` `xxd`

Depth is fine. What they lack is connective tissue and, in a few cases,
examples. `mimikatz` has 7 lessons and 7 of them carry fewer than two examples,
which is the worst example coverage in the roster. `linuxutils` has 5 such
lessons.

*Cost: an hour each, mostly adding handoffs and examples.*

### Phase 4 — The thirteen already at standard

`dfirwin` `docker` `firewall` `impacket` `ldapsearch` `msf` `ncsocat` `netexec`
`sleuthkit` `systemd` `vol` `yara` `linuxdfir`

Add handoffs only. These are the Security modules written last to a consistent
arc, and they are the proof that the standard above is achievable, because they
already meet all of it except flow.

---

## How this gets verified

`quality.py` prints the tier for every module. The gate for "production
quality" is **no module in REWRITE or DEEPEN**, and it should be run alongside
the existing three:

```
python validate.py   # structure, lint, no em dashes, no duplicate keys
python audit.py      # entry, exit and notation arrive in time
python ramp.py       # nothing is drilled that no lesson teaches
python quality.py    # depth, explanation, consistency, flow
python test.py       # 11452 checks, every solution replayed for real
```

Two things `quality.py` deliberately does **not** claim to measure, and which
still need a human read:

- Whether an explanation is any good, as opposed to present and long enough.
- Whether the order inside a module builds or merely accumulates.

Character counts and connective density find the modules worth reading. They
cannot do the reading.

---

## Two flow bugs this audit already caught

Both were mine, from inserting lessons mid-module earlier the same day, and
both were invisible to `validate.py` until the reachability check existed:

- **`awk`**: the new types lesson existed in the module and nothing pointed at
  it. The `next` chain ran straight past it, so a student walking the module
  in order never saw it.
- **`xxd`**: the same, and worse, because `tr-hex` already carried a `next` key
  further down its dict. My added key was dead code and Python kept the later
  one silently. `validate.py`'s duplicate-key check caught that one.

Both are fixed. The lesson for the plan: **inserting a lesson means updating
the previous lesson's `next`**, and `quality.py` now fails the module if you
forget.
