---
tags:
  - hone
  - project-plan
  - learning
created: 2026-08-12
updated: 2026-08-12
---

# hone: Build Plan and Progress Log

> Resumable build plan for **hone**. **Read this file first** when picking the project back up. Every locked decision and every completed step is recorded here so work can pause and resume without re-deriving context.

> [!tip] Picking this back up: START HERE
> [!success] **THE D17 FINISH LINE IS REACHED.** Phases 0 through 5 are complete. The priority four all ship, all four verified by real adapters, across all four engines, with a cross-module review queue over the lot. **The project is a complete, useful thing at this point and can sit here indefinitely without being unfinished.** Phases 6 onward are for later learning and for other people, and should be picked up when the tool in question is the tool actually being learned, not worked through as a checklist.
>
> [!success] **THE ROSTER IS COMPLETE.** All fifteen modules ship, across all eleven phases. There is no next phase.
>
> **State as of 2026-08-12.** `python3 validate.py` clean with **zero warnings**, `python3 test.py` green at **2983 checks** and stable across repeat runs, `./build.sh` produces a `dist/hone.pyz` that runs standalone with nothing installed, and `--per-tool` emits one file per tool. D4a is real.
>
> **The project was named `hone` on 2026-08-12**, replacing the "CLI Trainer" placeholder. To sharpen a blade: you do not hone something you have never touched, you hone something you already have and want sharper, which is this app's exact relationship to the tools you already use. The Python package, the command, the build outputs and the folder were all renamed together while nothing linked to them.
>
> | Tool | Lessons | Drills | Challenges | Quiz | Adapter |
> |---|---|---|---|---|---|
> | vim / neovim | 10 | 39 | 5 | 9 | nvim, verified |
> | Doom Emacs | 8 | 26 | 3 | 9 | emacs, verified |
> | org-mode | 9 | 20 | 4 | 9 | emacs, verified |
> | regex | 8 | 25 | 4 | 9 | nvim, verified |
> | Linux Basics | 8 | 22 | 4 | 9 | sandbox, verified |
> | bash | 8 | 20 | 4 | 11 | sandbox, verified |
> | Linux Advanced | 8 | 31 | 4 | 11 | sandbox, verified |
> | Linux Utilities | **0** | 37 | 3 | 8 | sandbox, verified |
> | awk and jq | 8 | 31 | 4 | 10 | sandbox, verified |
> | git | 8 | 26 | 5 | 10 | git, verified |
> | Remote access | 8 | 24 | 5 | 10 | sandbox, partly verified |
> | tcpdump | 6 | **40** | 2 | 10 | **pcap, verified** |
> | Python | 7 | 23 | 3 | 10 | sandbox, verified |
> | PowerShell | 6 | **34** | 2 | 10 | **pwsh, partly verified** |
> | tmux | 8 | 30 | 4 | 8 | tmux, verified |
>
> vim owns the `modal-grammar` pack; Doom consumes it per D9 and teaches only the Doom layer; org builds on Doom. regex is the prerequisite that unlocks Phases 7 and 10. **Linux Utilities has zero lessons on purpose**: it is openly a drill deck, and its Walkthrough view says so rather than being hidden, which is the D16 rule 1 empty state with real content behind it at last.
>
> **All three D8 tiers are now exercised.** `verified` by six adapters, `graded` by `grading.py` running your regex against strings it must match and must not, and `self` where nothing can be read back.
>
> **The app verifies real work.** Build a three-pane layout in real tmux and it reads `tmux list-panes` back. Edit a buffer in real nvim and it reads the buffer back, and it can tell *"the edit is right, but you left without saving it"* from *"the edit is wrong"*. **Every adapter-verified challenge carries its own solution and `test.py` plays it through the real tool**, so the harness proves content is solvable rather than merely parseable.
>
> **Scope note.** The roster's rationale leans on security and DFIR examples in places, because that is where several of these tools pay off hardest for this author. **hone is a general command-line trainer**, not a security course, and future modules should be judged on the boundary rule alone.
>
> **There is nothing left to build from the plan.** What remains is use, and the maintenance that use produces: content fixes as you find them, and new modules only if a tool earns its way onto the roster under the boundary rule. **All fifteen modules now have a real adapter.** The last two fell on 2026-08-12: `tcpdump` grades both filter languages against a capture file the app *writes* rather than captures, and `PowerShell` runs your pipeline in a real `pwsh`. What each still cannot check, it still says: live capture needs privileges, and `Get-WinEvent` needs Windows.
>
> **The totals:** 109 lessons, 429 drills, 56 challenges, 143 quiz items. About 20,400 lines, of which roughly two thirds is content. Eight verification paths: tmux, nvim, emacs, sandbox, git, pcap, pwsh, and the in-process regex grader.
>
> **Eight adapters now exist**: tmux, nvim, emacs, sandbox, git, pcap, pwsh, and the in-process regex grader. The **sandbox** one is the most reusable and requires nothing installed, because the tool it verifies is the filesystem, and **git subclasses it**, which is the pattern to follow for anything filesystem-shaped. **pcap and pwsh are a second shape**, sharing `_oracle.py`: rather than watching you work and reading the end state, they take an answer you typed, run it, and compare what it produced against what the reference produces. That is `grading.py`'s behavioural argument applied to an external tool, and it is the pattern to follow for anything whose answer is an expression rather than an action.
>
> Phase 0 built the harness. Phase 1 added the lesson reader, text-mode drills and tmux. Phase 2 added the tmux adapter, challenge, quiz and review screens. Phase 3 added `hone/adapters/nvim.py` and `hone/content/vim.py`. Phase 4 added `hone/adapters/emacs.py` and `hone/content/doom.py`, and extracted `hone/adapters/_buffer.py`. Phase 5 added `hone/content/org.py` and needed no new adapter. Phase 6 added `grading.py`, the `regex` drill type, and `hone/content/regex.py`. Phase 7 added `hone/adapters/sandbox.py`, a working directory on the D21 handoff, and `hone/content/linux.py` plus `hone/content/bash.py`. Phase 8 added `hone/adapters/git.py` and `hone/content/git.py` plus `hone/content/remote.py`. Phase 9 added `hone/content/linuxadv.py` and `hone/content/linuxutils.py`, and list windowing plus a height backstop in the screen layer. Phase 10 added `hone/content/awkjq.py` and `hone/content/tcpdump.py`, and renamed the project to `hone`. Phase 11 added `hone/content/python.py` and `hone/content/powershell.py`, completing the roster. Gamification added `achievements.py` and `hone/screens/stats.py` under **D22**.
>
> **Five things worth knowing before touching this code.**
>
> 1. **Screens never emit escape codes.** They build `Text` from styled spans and semantic glyph names, so a line's width is knowable without rendering it. That is the only reason the per-rung overflow assertions are possible.
> 2. **`hints()` takes `caps`.** Hints contain glyphs, and hardcoded non-ASCII in a constant leaked into the ASCII rung three separate times during Phase 0. `test.py` now asserts ASCII purity permanently.
> 3. **The Kitty probe is strict.** A malformed reply reads as *unsupported*, because a false positive tells the student an ambiguous chord works when their terminal cannot send it, which is the exact failure D11 exists to prevent.
> 4. **`escape_key`, not Esc.** D19 rule 2 is expressed as "every screen names its own way out", because a drill legitimately takes `Esc` as an answer. Capture screens return D19a's reserved chord instead. This kept the contract uniform rather than carving out an exception the harness has to know about.
> 5. **Time is always injected.** Nothing reads the clock; `now` is a parameter. That is what makes the scheduler deterministic in tests.
>
> The default palette is lifted from `~/.config/doom/themes/doom-cyberpunk-neon-theme.el`, including its own 16-colour fallbacks, so the trainer matches ghostty, tmux, fish, Doom, and neovim rather than approximating them.
>
> **This is a terminal application written in Python, stdlib only.** It was planned as an offline HTML page for most of a day and pivoted on 2026-08-12; see the session log entry (e) for what changed and why. Anything you remember about a browser, a single `.html` file, or `localStorage` is stale.
>
> **This is a wholly separate project from Waypoint.** Different folder, different app, different subject, no shared code and no shared content. See D15, which exists for a reason. Where this document cites Waypoint it is citing **prior art**, the same way it would cite any other project that already solved a problem, and nothing more.
>
> **The author's priority four are tmux, vim, Doom Emacs, and org-mode.** Everything else in the roster is for later learning and for other people, and is deliberately scheduled after them. Phases 1 through 5 deliver exactly those four, and **Phase 5 is a legitimate finish line**: the project is a complete, useful thing at that point and can sit there indefinitely without being unfinished. See D17.
>
> **After any change, run both:** `python3 validate.py` and `python3 test.py`.

---

## Running it

```bash
cd "$HOME/Documents/Main/hone"
python3 -m hone                  # from the source tree
python3 -m hone --list           # what is installed, and what can be verified
python3 -m hone --doctor         # the whole capability story, including the mode
python3 -m hone --mode read      # D26: launch nothing, just read and drill
python3 -m hone --mode checked   # D26: back to running the real tools
python3 -m hone --export out.json
```

Build the distributable single file:

```bash
./build.sh                          # python -m zipapp, stdlib only
python3 dist/hone.pyz        # what you hand to someone else
```

Check content and behaviour after any change:

```bash
python3 validate.py
python3 test.py
```

---

## Scope

An offline terminal trainer for the command-line tools worth real practice. Each tool is a module. Each module teaches through some combination of a **walkthrough**, **keystroke drills**, **challenges** at three scaffolding levels, and a **quiz** that feeds a spaced-repetition review queue spanning every module.

Where the tool being taught exposes a control interface, the trainer **verifies what you actually did** rather than taking your word for it. That is the central advantage of being a terminal application and it is why the project is one.

**Primary user:** the author, learning Doom Emacs, org-mode, vim, and tmux.
**Secondary user:** anyone handed the file. It must run with no install and no third-party packages.

**Audience floor:** someone who has never opened tmux should be able to work the tmux module start to finish and come out able to build a three-pane layout from muscle memory.

**Explicit non-goal:** this is not a replacement for the real tool. The trainer coaches and checks; the real tmux, the real nvim, and the real Emacs are where the work happens. See D1.

---

## Locked decisions

These are settled. Do not relitigate them without a reason recorded here.

| # | Decision | Rationale |
|---|---|---|
| D1 | **The trainer never acts on your behalf and never touches anything it did not create.** It may *read* state from tools you are running (`tmux list-panes`, an `emacsclient --eval` query, an nvim RPC call) and it may *create and destroy its own sandbox* (a scratch tmux session it named, a temp file it wrote). It never edits your files, never changes your config, never runs a command you did not perform yourself, and never touches a target on a network. **Restated 2026-08-12 (e).** | The browser-era wording was "never executes anything", which a verifying trainer cannot honour and which was really protecting two different things: that the app cannot damage you, and that the app cannot claim credit for work you did not do. Both survive in the restatement. The line that matters is **read your state, write only your own sandbox**. |
| D2 | **Python 3, standard library only.** No pip install, no virtualenv, no third-party packages, no network. Distributed as a single executable `.pyz` built with `zipapp`, which is itself stdlib. **Restated 2026-08-12 (e).** | The stated goal is that others can download it and use it on their desktops, and every dependency is a way that fails on a machine you cannot see. Python 3 is present by default on essentially every Linux and macOS install, which is the audience for a tmux and Doom trainer. `zipapp` gives back the single-file distribution the HTML plan had: one file, `python3 hone.pyz`, nothing to install. |
| D2a | **Rendering is plain ANSI escapes and the input layer is written directly against `termios`. `curses` is deliberately not used.** | Two reasons, and the second got stronger once D19 landed. First, `curses` fights you on exact key decoding (D11), which is not optional for this app, and once you own the input layer `curses` is mostly in the way. Second, `curses` has a palette-index colour model that handles truecolour badly, and D19 requires truecolour. Recorded as considered and rejected rather than never evaluated. |
| D3 | Content and UI are organized **by tool**. A module is a tool. | How people actually reach for this: you sit down to learn tmux, so you open tmux and find everything tmux in one place. Organizing by skill type would force the user to filter a global Drills list by tool, which is worse. |
| D4 | Engines are **shared code across modules**, invisible to the user. One program, not one per tool. | The drill, challenge, and quiz machinery gets written once rather than once per tool. The decisive user-facing reason for one program is D10: a review queue fragmented across nine binaries is a queue you stop opening. |
| D4a | The build can emit **per-tool `.pyz` files** from the same source. | Gives both: one app for the author, `tmux-trainer.pyz` for someone who only wants that. Nearly free if the module loader is clean from the start, expensive to retrofit. |
| D5 | Four engines: **walkthrough**, **keystroke drill**, **challenge**, **quiz and review**. A module uses whichever it needs; none is mandatory. | Not every tool needs every engine. `tar` is almost pure drill. `git` is almost pure mental model. Forcing all four on every module would pad content with filler. |
| D6 | Scaffolding is a **mode, not separate content**: `Guided` (steps gated, hints shown), `Coached` (hints on request, warns), `Free` (task statement only). | Guided practice and unguided practice are the same task at different friction, not two pieces of content. Authoring a challenge once and letting the mode decide how much scaffolding shows cuts content cost by roughly a third and guarantees the two versions never drift apart. |
| D7 | **State is a JSON file on disk** at `$XDG_DATA_HOME/cli-trainer/state.json`, with explicit export and import for moving between machines. **Restated 2026-08-12 (e).** | This decision previously existed to work around `localStorage` being unreliable when an HTML file is opened directly, which was the single largest technical risk in the browser plan. Moving to a terminal app deletes the problem outright rather than mitigating it. Export and import survive because they are still useful, not because anything is at risk. |
| D8 | Every task is **labeled verified, machine-graded, or self-marked** in the UI, and never blurs them. | The trainer can now verify a great deal that a browser could not, which makes the remaining honour-system tasks *more* important to mark honestly, not less. A user who cannot tell which is which learns false confidence, and that is the specific failure mode of most CLI tutorials. |
| D9 | Modules declare **prerequisites** and may **share content packs**. | Doom's evil bindings *are* vim bindings, so the vim module owns modal grammar and Doom links to it rather than duplicating it. Same for regex feeding grep, sed, awk, and Python's `re`. Tool-organized navigation does not require tool-duplicated content. |
| ~~D10~~ | ~~One **spaced-repetition review queue spanning every module**, surfaced as "what is due today".~~ **Reversed 2026-08-12 by D24.** | The reasoning was that spacing makes bindings stick, which is true, and that a habit is what the app should build, which the author rejected on first real use. See D24. |
| D11 | Keystroke drills read the terminal in **raw mode**, enabling the **Kitty keyboard protocol** where the terminal supports it and falling back to legacy decoding with a **documented list of chords it cannot distinguish**. **Restated 2026-08-12 (e).** | Legacy terminal encoding cannot tell `Ctrl+I` from `Tab`, `Ctrl+M` from `Enter`, `Ctrl+[` from `Escape`, or `Ctrl+Shift+X` from `Ctrl+X`. The Kitty protocol resolves all of these and is supported by ghostty, which is what the author runs, as well as kitty, WezTerm and foot. Detect it, use it, and when it is absent say so in the drill rather than silently marking a correct answer wrong. |
| D12 | `validate.py` and `test.py` exist **from Phase 0**, before any content. | Content-heavy apps rot, and a harness retrofitted onto existing content never catches up: by the time it exists there is too much to bring up to standard, so it gets pointed at new content only and the old content stays unchecked forever. Fifteen modules across four engines is more than enough for that to happen here. |
| D13 | **Desktop only.** No phone or tablet support, and none is possible or wanted. | Decided 2026-08-12 and reinforced by the pivot. The highest-value engine is keystroke production drills, which need a physical keyboard. |
| D14 | Lives at `~/Documents/Main/hone/`, top-level in the vault, with a `!/hone/` exception added to the vault `.gitignore`. | Not all of the roster is security work (vim, tmux, org-mode, Python), so nesting it under `Cyber Security Study and Reference/` would misfile it. That folder was the only tracked path, hence the one-line exception. |
| D15 | **This is a completely separate project from Waypoint.** Separate folder, separate app, separate subject. **No shared files, no imports, no build dependency, no runtime dependency, and no shared content in either direction.** Techniques may be **copied**, never linked: if a pattern is worth reusing, the code is copied into this project and owned here from that moment on. Every reference to Waypoint in this document is a **prior-art citation**, carrying no coupling and no obligation. | Stated 2026-08-12 at the author's explicit and emphatic instruction. The two projects share an author, a machine, and some proven UI patterns, and that is the entire relationship. Waypoint is a finished, validated exam tool; nothing here may create a reason to touch it, and nothing there may become a dependency of this. The failure mode being prevented is the slow drift where "we already have that in Waypoint" turns two clean projects into one tangled one. |
| D16 | **Navigation is tool-first, then activity.** Home shows the cross-module review queue and a picker of every module. Inside a module there are exactly three views, always in this order: **Walkthrough**, **Practice**, **Drill**. | Set 2026-08-12 at the author's request. This is how people actually reach for the thing: you decide you want to learn tmux, so you open tmux, and then you decide whether you are reading, practising, or drilling. Any organisation that makes the user filter a global Drills list by tool is worse. |
| D17 | **The author's priority four are tmux, vim, Doom Emacs, and org-mode**, built first, in Phases 1 through 5. The remaining eleven modules are explicitly for later learning and for other users. **Phase 5 is a legitimate finish line.** | Set 2026-08-12. The stated purpose of the other eleven is future learning and other people, which is real but not urgent, and scheduling them earlier would risk the project stalling before it delivers what it was actually built for. Naming a finish line matters more here than in most projects: a fifteen-module trainer is large enough that "unfinished forever" is the default outcome unless a point is designated where stopping is a success. |
| **D18** | **Verification is an optional capability tier, never the foundation.** The trainer is fully usable on content alone. When it detects `tmux`, `nvim`, or a live `emacsclient`, the modules that can use them unlock real checking. A module whose adapter is missing **degrades to self-marked and says so**; it never errors and never hides the content. | Added 2026-08-12 (e). Instrumenting three tools through three different interfaces is the genuine fragility risk in this pivot, and this is what keeps it from becoming a foundation risk. It also means Phase 0 and Phase 1 do not have to solve any integration, and that a stranger with no nvim installed still gets a working trainer rather than a stack trace. |
| **D23** | **The program is self-contained. No vault cross-linking, ever.** Content may *mention* a note or a tool in prose, and may compare ideas to Obsidian where that teaches something, but nothing in the app resolves a vault path, emits an `obsidian://` URL, or reads a file outside its own sandbox and state directory. The only two exceptions are the XDG state path, which is the app's own, and the Doom config read behind `config_contains`, which is a documented D1 read the student was explicitly asked to make. | Decided 2026-08-12 at the author's instruction, and it **supersedes the softer suggestion recorded against Open question 2**, which had proposed inline vault display as a nicety that no-ops when absent. Self-contained is the stronger and simpler rule: D2 exists so a stranger can run the `.pyz` and have it work, and a feature that silently does nothing for most users is a feature that is untested for most users. A trainer that behaves differently on the author's machine than on anyone else's is one that only the author can trust. |
| **D24** | **No schedule, no streak, no queue, no score.** Nothing is ever due, nothing is owed on any day, and the app keeps no clock on the student. Every module stands alone and is entered in whatever order suits. Progress is shown as how much of a tool you have met, never as a deadline or a debt. | Added 2026-08-12 at the author's instruction, reversing D10 and D22. The habit machinery was built well and worked, and it was the wrong thing to build: it turned a shelf of tools you were curious about into a set of obligations with a number attached, and the first thing a returning user saw was what they owed. A trainer for tools you *chose* to learn should survive being put down for a month without mentioning it. What is kept is the part that was never about compliance: what you have read, what you have passed, how each drill has gone, and the notes you left yourself. |
| ~~**D22**~~ | ~~**Gamification rewards evidence of learning, never volume.** Achievements grouped as retention, fluency, coverage, habit and craft.~~ **Reversed 2026-08-12 by D24.** | The rule itself was right and the implementation honoured it: no badge for volume, and one for admitting you had not done something. It was removed anyway, because the author's objection was not that the scoring was unfair but that there should be no scoring. See D24. |
| **D25** | **The trainer may run an answer you typed, in order to grade it, and must say so before you type it.** Bounded by a timeout and killed on expiry; run in a sandbox the app created and will destroy; never passed through a shell, so the answer reaches the tool as one argument in the tool's own language. PowerShell is the one case where the answer *is* a program, and that adapter says so on screen. | Added 2026-08-12 at the author's instruction to make tcpdump and PowerShell check work. D1's "never runs a command you did not perform yourself" was written for a trainer that could only watch, and read literally it forbids the only honest way to grade a filter. The restatement keeps both things D1 was protecting: the app still cannot damage you, and it still cannot claim credit for work you did not do, because the work *is* the answer you typed. It is also strictly smaller than a capability the app already had: **D21 hands you a real interactive shell** with no timeout and no sandbox, and nobody thought that was a violation. What would violate D1 is running something you did not write, and nothing here does. |
| **D26** | **Checking is a mode the student controls, not only a capability the machine happens to have.** `checked` runs the real tools; `read` launches nothing at all: no handover, no sandbox, no subprocess, anywhere. Lessons, drills and quizzes are unaffected, because none of them leaves the process. Every degrade carries its reason, so a task that would have been verified says it was not, and why. | Added 2026-08-12 at the author's request. D18 already made verification optional, but only in the sense that a *missing tool* turned it off, which meant the only way to stop the app spawning tmux sessions and temp directories was to uninstall something. The two states already had names the app was using in the picker, "checks your work" and "read and drill only", so this makes the label a switch. The honesty rule is the load-bearing part and is the same one D8 has always enforced: an oracle drill in read mode still grades, by comparing text, and says in as many words that it was not run. A trainer that silently downgraded its checking would be worse than one that never checked. |
| **D19** | **One contained, attractive, beginner-safe TUI.** Full-screen framed layout, arrow-navigable menus with a highlighted selection, a permanent key-hint footer on every screen, and a restrained neon palette. **Beginner rules, all enforceable by `test.py`:** every screen names its own exits, `Esc` always goes back, no screen is ever blank or hint-free, and nothing needs a keybinding you were never shown. Arrow keys and `j`/`k` both work, and `1`-`9` jump directly. | Added 2026-08-12 (f) at the author's request: the student should get one contained experience that looks good, not a research project in how to drive it. A terminal UI is where beginner-hostile design hides most easily, because the author already knows the keys. The rules above exist so "discoverable" is a testable property rather than an intention. |
| **D19a** | **A keystroke-capture screen is visually unmistakable and always has an escape hatch that is not a captured key.** Distinct border colour, an explicit CAPTURING banner, and one reserved chord (documented on screen) that always exits. | The one genuinely dangerous thing this app does to a novice is take over the keyboard. A drill that captures `Esc`, `q`, and `Ctrl-C` because they are all legitimate answers can trap someone who does not know how to get out, and "close the terminal window" is not an acceptable answer for a teaching tool. |
| **D20** | **Looks degrade down a capability ladder, detected at startup with a manual override.** Colour: truecolour → 256 → 16 → none. Glyphs: Nerd Font → Unicode box drawing → pure ASCII. `NO_COLOR` and a non-TTY stdout are honoured. | Same shape as D18 and for the same reason. The author runs ghostty with Nerd Fonts installed and will see the intended design; a stranger running the `.pyz` in a bare `xterm` must get something plain and correct rather than a screen of tofu boxes and escape codes. Detect and step down rather than assuming, and let `--theme` and `--ascii` force it for anyone whose terminal lies about its capabilities. |
| **D21** | **When a challenge needs the real tool, the trainer suspends, hands over the terminal cleanly, and resumes to grade.** Restore the terminal state, run the tool, return. When it is already running inside tmux it may instead open the practice session in a second pane, as an enhancement, never as a requirement. | Added 2026-08-12 (f). This is what makes "one contained experience" true even though the actual work happens in real nvim and real tmux: the student never arranges windows, never opens a second terminal, and never wonders whether the trainer noticed. It is the pattern `git` already uses to hand you `$EDITOR`, which means it is familiar and it works everywhere. The tmux-split version is nicer when available and is also the single most confusing thing to debug when it misbehaves, so it stays optional. Supersedes Open question 4. |

---

## The four engines

**1. Walkthrough.** Prose, worked examples, named misconceptions, and "now go do it for real" callouts. Mostly linear with prerequisites.

**2. Keystroke drill.** Prompt an intent ("delete inside the parentheses"), read the actual keystroke in raw mode, grade exactly, record latency. Feeds D10's queue.

**3. Challenge.** A multi-step task at one of D6's three scaffolding levels, verified by whichever of these applies:

| Verification | Meaning |
|---|---|
| `verified` | An adapter observed the real end state. This is the good one and it only exists because the app is a terminal app |
| `graded` | Deterministic in-process check: a regex run against intended matches and against negatives, a predict-the-output answer, a jq filter evaluated |
| `self` | You did it somewhere the trainer cannot see, and you marked it. Always labeled, never dressed up as more |

**4. Quiz and review.** Mixed recall, predict-the-output, and mental-model questions. A scorecard names the weakest areas and links straight to the drills that fix them.

### Which engine applies per priority module

This is not uniform and pretending otherwise would produce bad content.

- **tmux.** Keystroke drills are **recall type, not production type**: the trainer must not try to capture `C-b` itself, because if it is running inside tmux then tmux takes the prefix first, and even outside tmux a captured prefix teaches the binding without the context. Production practice happens instead through **verified challenges**: the trainer creates a detached scratch session, you drive real tmux in another pane, and it checks `tmux list-panes`. This is better teaching than capture would have been, so the constraint costs nothing.
- **vim / neovim.** Both apply. Keystroke drills capture directly, since you are not inside vim while inside the trainer. Challenges verify through nvim's RPC socket, reading the real buffer and the real cursor position after you perform the edit in real nvim. **This deletes the normal-mode buffer emulator** the browser plan needed, which was the single largest engineering item in it.
- **Doom Emacs.** Both apply. `emacsclient --eval` is the richest adapter of the four: buffer contents, point, and even what a key is actually bound to in the user's own config. Requires the Emacs server to be running, which Doom users generally have.
- **org-mode.** Verification is trivial and needs no adapter protocol, because org files are text. Did the refile land in the right place, is the TODO state right: read the file.

---

## Navigation

The shape D16 locks, and the rules that follow from it.

**Home**

- **Due today.** The cross-module review queue of D10, first thing on the screen, spanning every module the user has touched. This is the only place content from different tools mixes.
- **Pick a tool.** Every module as a row: name, one-line blurb, progress, prereqs, and whether its verification adapter is available on this machine.

**Inside a module: three views, always in this order**

| View | Contains |
|---|---|
| **Walkthrough** | The lessons, in order. Read this to learn the thing |
| **Practice** | Challenges at `Guided` / `Coached` / `Free` per D6, plus this module's quiz items as a check |
| **Drill** | Keystroke and recall drills. Everything answered here feeds the home review queue |

**Rules that follow**

1. **All three views always render, even when a module has nothing for one.** A module that is a drill deck by design says so in its Walkthrough. Hiding a view makes a deliberate choice look like a bug, and the user cannot tell the difference from the outside.
2. **Quiz is one engine with two surfaces**, not a fourth view: inside Practice as a module-level check, and in the home queue as spaced repetition. A Quiz view would split the same content across two places and contradict D16's "exactly three".
3. **Prereqs are shown, never enforced.** The Doom row names vim because the grammar is taught there; it does not lock. Gating an offline self-study tool insults the user.
4. **Adapter status is shown on the picker, not discovered mid-challenge.** Per D18 a missing adapter is a degraded mode, not an error, and the user should know before starting rather than at the moment of grading.
5. **Progress is per module and visible on the picker**, so the answer to "where was I" is on the first screen rather than three levels in.

---

## Look and feel

What D19 and D20 mean concretely. The target is "slightly hacker cool", which means a restrained neon palette on a dark ground, box drawing, and a wordmark, not animated ASCII rain.

**Home screen, at the top of the capability ladder**

```
  ╭──────────────────────────────────────────────────────────────╮
  │   ▄████  ██     ██                                           │
  │  ██      ██     ██     C L I   T R A I N E R                 │
  │  ██      ██     ██                                           │
  │   ▀████  ██████ ██     fifteen tools · one habit             │
  ╰──────────────────────────────────────────────────────────────╯

   DUE TODAY                                            17 items
   ▸ tmux                                              8 drills
     vim                                               9 drills

   mode   checked   runs the real tools and checks your work

   PICK A TOOL
   ▸ tmux              ████████░░  78%   ✓ checks your work
     vim               ███░░░░░░░  31%   ✓ checks your work
     Doom Emacs        ░░░░░░░░░░   0%   ✓ checks your work
     org-mode          ░░░░░░░░░░   0%   ✓ checks your work
     git               ░░░░░░░░░░   0%   ✓ checks your work
     tcpdump           ░░░░░░░░░░   0%   ✓ checks your work
     Linux Basics      ░░░░░░░░░░   0%   ✓ checks your work

  ╭──────────────────────────────────────────────────────────────╮
  │  ↑↓ move  ⏎ select  m mode  esc back  ? help  q quit         │
  ╰──────────────────────────────────────────────────────────────╯
```

The footer is permanent and its contents change per screen. That single element carries most of D19's beginner promise: there is never a moment where the student has to guess what is possible.

**Drill screen, per D19a**

The border changes colour and the banner is explicit, because this is the one screen that has taken the keyboard:

```
  ┏━ CAPTURING KEYS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ F10 to leave ━┓
  ┃                                                              ┃
  ┃   tmux · drill 4 of 12                          ●●●○○○○○○○   ┃
  ┃                                                              ┃
  ┃   Split the current pane top and bottom.                     ┃
  ┃                                                              ┃
  ┃   > _                                                        ┃
  ┃                                                              ┃
  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

`F10` is the reserved exit chord, settled in Phase 0 and recorded in `hone/config.py`. It is shown on screen always, `validate.py` refuses any drill that claims it, and `--exit-key` overrides it.

**Palette.** Default to the author's existing `doom-cyberpunk-neon` colours, which already match ghostty, tmux, fish, Doom, and neovim on this machine, so the trainer looks like part of the environment rather than a visitor. Ship one neutral fallback theme for everyone else, and a `--theme ansi` mode that uses the terminal's own sixteen colours and therefore inherits whatever the user already likes.

**What degrades, per D20**

| Rung | Effect |
|---|---|
| No truecolour | Palette maps to the nearest 256 or 16 colours. Layout unchanged |
| No Nerd Font | `✓` and `▸` become Unicode equivalents; the wordmark falls back to plain block text |
| No Unicode | Box drawing becomes `+`, `-`, `|`; progress bars become `[####------]` |
| `NO_COLOR` or not a TTY | Monochrome, structure preserved through spacing and rules |

**First run.** A short guided tour rather than dropping the student on the home screen cold. Three or four cards: what the three views are for, what the review queue does, how to leave a drill. Skippable, and never shown again unless asked.

---

## Content schema

Settled before authoring, because migrating content later is expensive. Content lives in `hone/content/<module>.py` as plain dicts, loaded additively: a new module is a new file plus a line in the loader.

```python
# content/tmux.py
MODULE = {
    'id': 'tmux',
    'title': 'tmux',
    'blurb': 'Sessions, windows, panes, and the prefix key.',
    'prereqs': [],                    # module ids, per D9
    'provides': [],                   # shared packs this module owns, e.g. 'modal-grammar'
    'adapter': 'tmux',                # None means content-only, per D18
    'estimate': '3-4 hours',
    'lessons': [...], 'challenges': [...], 'drills': [...], 'quiz': [...],
}
```

```python
# Lesson (walkthrough engine)
{
    'id': 'tmux-model',
    'title': 'Sessions, windows, panes',
    'concept': 'Prose. What this is and why it is shaped this way.',
    'examples': [{'label': ..., 'code': ..., 'note': ...}],
    'misconceptions': ['A window is not a terminal window.'],
    'try_it': ['Run `tmux new -s scratch`, then detach with the prefix and `d`.'],
    'next': 'tmux-prefix',
}
```

```python
# Drill (keystroke engine)
{
    'id': 'tmux-split-v',
    'type': 'keys',                   # 'keys' | 'recall' | 'predict'
    'prompt': 'Split the current pane top and bottom.',
    'keys': ['C-b', '"'],             # expected sequence
    'accepts': [['C-b', 'S-\'']],     # equivalent sequences also marked correct
    'teach': 'The " key is a horizontal divider on its side. % is the vertical one.',
    'needs_kitty': False,             # True when legacy decoding cannot express this chord
}
```

```python
# Challenge (three scaffolding levels from one definition, per D6)
{
    'id': 'tmux-three-pane',
    'title': 'Build a three-pane dev layout',
    'goal': 'A named session: one tall pane left, two stacked right. Detach and reattach.',
    'setup': {'kind': 'tmux', 'session': 'trainer-drill'},
    'steps': [{'instruction': ..., 'hint': ...}],   # Guided walks these, Coached hides hints
    'free': 'Make a named session with a 3-pane layout, detach, reattach.',
    'verify': {'kind': 'tmux', 'expect': 'panes==3 and layout==main-vertical'},
    'fallback': 'self',               # per D18, when the adapter is unavailable
}
```

```python
# Quiz item
{'id': ..., 'type': 'predict' | 'mcq' | 'short', 'prompt': ..., 'given': ...,
 'answer': ..., 'distractors': [...], 'teach': ...}
```

### Adapter interface

One small class per tool, in `hone/adapters/`. Everything about being fragile lives behind this boundary.

```python
class Adapter:
    name = 'tmux'
    def available(self) -> bool: ...      # is the tool installed and reachable
    def setup(self, spec) -> None: ...    # create ONLY our own sandbox, per D1
    def observe(self) -> dict: ...        # read real state, never mutate
    def teardown(self) -> None: ...       # destroy only what setup created
```

**There are two shapes of adapter, and they answer different questions.**

*Watchers* are the original: they hand you the real tool, let you work, and read
the end state afterwards. tmux, nvim, emacs, sandbox and git are all watchers,
and `observe` is where their work happens. Use one when the answer is an
**action** whose result is visible in something durable, a pane layout, a
buffer, a tree of files, a commit graph.

*Oracles* came later (session (aa)) and share `adapters/_oracle.py`. They take
an answer you **typed**, run it, and compare what it produced against what the
reference answer produces, so `setup` builds a fixture and `evaluate` does the
work. pcap and pwsh are oracles. Use one when the answer is an **expression**
rather than an action, and when many different spellings are equally correct:
that is precisely the case `grading.py` already argued for regex, and the
argument does not change just because the judge is an external binary.

Oracles are bound by **D25**: bounded by a timeout, sandboxed, never through a
shell, and disclosed on screen before the student types.

---

## Tool roster

Selected on **useful × hard to learn**. A tool that is easy (`cd`, `cat`, `ls`) does not need a trainer, and a tool that is hard but irrelevant to this user's work is a distraction. "Hard" here means one of: a hidden mental model, cryptic or inconsistent syntax, poor discoverability, or a high pure-memorization load.

> [!important] Module boundary rule, set 2026-08-12
> A tool earns **its own module only if learning it changes how you think.** If the difficulty is "I know what I want and cannot remember the flags," it is not a module, it is a **drill deck**.
>
> This rule collapsed a first draft of roughly twenty units into the fifteen below. Applying it killed a "system and service" pack outright (all of it is really just using Linux), folded `grep` / `rg` / `sed` into regex where they belong as applications of the pattern language, and folded the `cut` / `sort` / `uniq` / `tr` vocabulary into bash where pipelines are already being taught.
>
> **Linux is three modules, not one.** Absorbing the system pack made a single Linux module far too big for one sitting, and the three splits have genuinely different jobs: Basics and Advanced each teach a mental model, while **Utilities is openly a drill deck**.

### The fifteen modules

Listed in reading order rather than by priority. The **Adapter** column is D18: what unlocks real verification, and blank means content-only.

| Module | Covers | Hard because | Adapter | Priority |
|---|---|---|---|---|
| **Linux Basics** | Filesystem hierarchy and what `/etc`, `/var`, `/proc`, `/usr` actually are. Paths, users and groups, ownership, `rwx` and octal, `umask`, `chmod` / `chown`. Hardlinks vs symlinks. Redirection and pipes, `stdin` / `stdout` / `stderr`. Environment and `PATH`. Processes, jobs, `kill`. `man` / `apropos` as the way to find things out | What you need to be functional. Concept and tool are taught together (permissions *with* `chmod`), so no skill is split across modules | sandbox dir | High |
| **Linux Advanced** | setuid, setgid, the sticky bit, ACLs, capabilities. Signals in depth, the process tree, orphans and zombies, `nohup` / `disown`, `/proc`. File descriptors properly, including **`2>&1` ordering**, here-docs and here-strings. Mounts and filesystems. systemd units, timers vs cron, `journalctl`. Local network state: `ip`, `ss -tulpn`, routes, the resolution path | The deep model, and where the pentest-relevant material lives. `2>&1` ordering and the setuid family are two of the most commonly half-understood things in Linux | sandbox dir | Medium |
| **Linux Utilities** | `find` + `xargs` (predicate ordering, `-exec ;` vs `+`, the `-print0` safety lesson), `lsof`, `tar`, `less`, `stat`, `df` / `du`, `watch`, `tee`, `ln`, `which` / `type`, `xxd` / `strings` / `file` | **Openly a drill deck, not a course.** Minimal walkthrough, almost pure recall drills feeding D10's queue. Cheapest content in the project and probably the highest daily annoyance reduction. `lsof` finds deleted-but-still-held files, which is DFIR gold. `less` reuses vi keys, so it reinforces the vim module for free | sandbox dir | Medium |
| **bash** | Quoting, word splitting, expansion, `"$@"` vs `$@`, IFS, subshells, exit codes, pipelines, and the `cut` / `sort` / `uniq` / `tr` / `wc` vocabulary | **Quoting and expansion is the hard core** and gets top billing, not an appendix. Also carries the `fish` vs `bash` contrast: the author's daily shell is deliberately not POSIX, so daily typing does *not* reinforce this module | sandbox shell | High |
| **regex** | The pattern language, then `grep`, `rg`, `sed`, and vim search as its applications | Dense syntax, greedy vs lazy, anchors, classes, lookaround. Prerequisite for four other modules | in-process `re` | High |
| **vim / neovim** | Verbs, motions, text objects, counts, registers, macros | Compositional grammar you cannot see. **Owns `modal-grammar`** per D9 | nvim RPC | High |
| **Doom Emacs** | The `SPC` tree, workspaces, buffers and windows the Doom way, popup rules. Vanilla `C-x` / `C-c` bindings arrive as a **late lesson**, framed as the layer underneath | Discoverability is the whole problem. Layered on `modal-grammar` from vim per D9. Teaching vanilla keys as a co-equal track alongside evil is a reliable way to learn neither | emacsclient | High |
| **org-mode** | Document model, TODO states, capture, refile, agenda | Enormous surface area. Worth its own module rather than being buried in Doom | org files | Medium |
| **tmux** | Sessions, windows, panes, the prefix, copy mode | Prefix-key indirection plus a three-level object model people collapse into one | tmux | High |
| **git** | The commit DAG, refs, the index, detached HEAD, rebase vs merge, reflog, bisect | The hardest tool in common daily use: a clean model behind an inconsistent CLI. Also the model magit assumes you already have | scratch repo | High |
| **Remote access and network tooling** | Reach the service: `dig`, `ping` / `traceroute` / `mtr`, `nc`, `curl`, `openssl s_client`. Get a session: `ssh` (keys, `~/.ssh/config`, the agent, `ProxyJump`), `xfreerdp`. Move data and traffic: `scp`, `rsync`, `sshfs`, then `-L` / `-R` / `-D`, `proxychains`, `socat`. **Written out in full below** | One arc through three progressively harder questions, each consuming the previous answer, with port forwarding as the climax | partial | High |
| **awk and jq** | `awk`: pattern-action, the implicit loop, fields, `NR`/`NF`, `BEGIN`/`END`. `jq`: `select`, `map`, `to_entries`, `-r`, `-s` | Two small filter languages doing the same job on different data shapes, columns versus JSON. Taught together so the contrast does work. Both look like utilities and are actually languages | real binaries | High |
| **tcpdump** | BPF filter syntax, reading output, and the **capture-filter versus display-filter contrast** | `tcp port 443` versus `tcp.port == 443` are two different languages and nobody teaches that explicitly, which makes it the most common failure. **Scope is drawn tightly at filters:** protocol analysis is Wireshark's course. Generating traffic is still out of scope per D1, so the capture file is **written by `pcapgen` rather than captured**, and both languages are graded against it | generated pcap | Medium |
| **Python** | Basics only, per the original ask | Not hard so much as broad | subprocess | Medium |
| **PowerShell** | Object pipeline, verb-noun discipline, `Get-Member` as the way in, `Get-WinEvent` with XPath filters | Objects instead of text is a real reframe. `Get-WinEvent` XPath is hard and pure DFIR. **`pwsh` is not installed on this machine**, so content can be authored and predict-graded but not practiced live | none | Medium |

### Deliberate skips

Recorded so they are not rediscovered as gaps.

| Skipped | Why |
|---|---|
| `nmap`, Metasploit, and pentest tooling generally | Engagement workflow is a different subject from tool proficiency, and this project teaches tool proficiency. Fails the scope test recorded under Remote access: it is not worth knowing with no engagement in progress |
| Modern replacements pack: `bat`, `eza`, `zoxide`, `atuin` | Useful but easy. They fail the "hard to learn" half of the filter, and a cheat-sheet note serves better than a trainer |
| `ffmpeg`, `screen`, `ed`, `make` | Hard, but not relevant to this user's work |
| `volatility` | On-brand for DFIR but too heavy for v1. Revisit if memory forensics becomes a focus |
| `fzf` | Transformative for daily speed but easy to learn. Fails the "hard" half of the filter |
| `sqlite3` | Real DFIR value (browser history, app artifacts) but the actual skill being taught would be SQL, which is a different course |
| `strace`, `gpg`, `yara` | Hard and genuinely useful, but niche enough to defer. ~~Revisit once the fifteen modules exist~~ **That condition is now met (2026-08-12).** They are the only named candidates for a sixteenth module, and each must still earn its place under the boundary rule: own module only if learning it changes how you think, otherwise a drill deck entry. `strace` is the strongest of the three for this user's work |
| `tshark` | Absorbed into **tcpdump** as the display-filter half of that module's central contrast, rather than standing alone |

---

## Module detail: Remote access and network tooling

> The first module written out in full. The others get the same treatment when their phase is reached.

**Why these belong together.** This is not a leftovers bin. It is one arc through three progressively harder questions, and each stage consumes the previous stage's answer.

**1. Can I reach the service?**
`dig` (record types, `+short`, `+trace`, reverse lookups), `ping` / `traceroute` / `mtr`, `nc` for a raw connection and a banner, `curl` for HTTP (methods, headers, cookies, `-d` variants, redirects, `-k`), and `openssl s_client` for TLS. Closes with the PEM / DER / PKCS12 concept section and `x509` inspection, which is the only genuinely conceptual part of openssl.

**2. Can I get a session?**
`ssh` properly: key types, `ssh-keygen` and `ssh-copy-id`, `~/.ssh/config` as the thing that makes every later command short, `ssh-agent` and specifically why agent forwarding is dangerous, and `ProxyJump` for bastions. Then `xfreerdp` for the Windows side, taught as a contrast with ssh rather than bolted on.

**3. Can I move data and traffic?**
`scp` and `rsync` (trailing-slash semantics, `-a`, `--delete`, and `--dry-run` taught as a habit rather than a flag), `sshfs`. Then the climax: port forwarding, `-L` versus `-R` versus `-D`, and `proxychains` consuming the SOCKS proxy that `-D` creates. `socat` comes last as the general case that `nc` only gestures at.

**Why port forwarding is the climax.** It is the hardest material in the module, the worst taught anywhere else, and the highest payoff in this user's actual work. It also only makes sense once stages 1 and 2 are solid, which is the argument for the arc rather than an alphabetical tool list.

**Verification, per D8 and D18.** This module is the weakest of the roster for adapters, and the plan should not pretend otherwise.

| Kind | Content |
|---|---|
| `verified` | Only the local, offline parts: parsing a `~/.ssh/config` the user wrote, checking a keypair they generated in the sandbox, `rsync` run against sandbox directories where the trainer owns both sides |
| `graded` | `dig` and `curl` predict-the-output against canned responses. **`rsync` trailing-slash prediction** (given this source and destination, which files land where), which is precisely the misconception. Direction of `-L` versus `-R` given a stated scenario |
| `self` | Anything needing a second machine or a live network, which is most of stages 1 and 3. A throwaway container is the cheap lab and the module should say so rather than pretending the trainer can verify it |

D1 forbids the trainer from touching anything on a network, so `dig` and `curl` exercises are canned rather than live even though running them would be technically easy. That constraint is deliberate: a training tool that quietly makes outbound connections is not a tool you can hand to a stranger.

**Prereqs:** Linux Basics. Deliberately not bash, so this module can be taken early.

**Scope boundary: the tool, never the engagement.** This module teaches *how the tool works*, never *when to reach for it during a pentest*. It teaches what `ssh -D 1080` does and how proxychains consumes the SOCKS proxy it opens. It does not teach that pivoting is the right move at some point on a box. The test for anything proposed here, and for this project generally: **would it still be worth knowing with no engagement in progress?** If not, it does not belong. Per D15 this is a rule about this project's own scope, not a coordination agreement with any other project.

---

## Build phases

### Phase 0: Foundation and harness
No content. Entry point and screen loop, the `termios` input layer with Kitty protocol detection per D11, the **render layer with the capability ladder of D20**, the framed layout and permanent footer of D19, the module loader, state on disk per D7, the adapter interface and registry per D18 with **zero adapters implemented**, `validate.py`, `test.py`, and `build.sh` producing the `.pyz` of D2 and the per-tool exports of D4a. **Do not start Phase 1 before this is green.**

The render layer belongs here rather than being retrofitted: D20's ladder has to be a property of how every screen is drawn, and bolting degradation onto screens that assumed truecolour and Nerd Fonts is the same retrofit trap D12 exists to prevent.

`validate.py` checks the content graph: every prereq and every `next` resolves, ids are unique, every `accepts` alternative is distinct from the others, every `verify.kind` names a registered adapter, and every module declares something for all three views or explicitly declares one empty.

`test.py` checks behaviour with no terminal: plays every challenge against a fake adapter, checks every quiz question the content can generate, round-trips key sequences through the encoder and decoder, exercises the review scheduler, round-trips state export and import, and asserts that a module whose adapter is unavailable **degrades to self-marked rather than raising**, which is D18's whole promise.

It also asserts D19's beginner rules, which is why they were written as rules rather than intentions: **every screen declares a non-empty footer, every screen handles `Esc`, no screen renders empty, and no drill claims the reserved exit chord of D19a.** Render every screen at each rung of D20's ladder and assert none of them loses a line or overflows eighty columns.

### Phase 1: Walkthrough and keystroke engines, content = tmux
tmux first because it is the cheapest complete vertical slice: roughly 25 bindings for the drill engine, a clean three-level model for the quiz, and real procedures for the challenges.

Ship the legacy-decoding fallback of D11 in this phase, not later, including the documented list of chords it cannot express.

Note the tmux constraint recorded under the engines: drills here are **recall type**, and production practice arrives in Phase 2 with the adapter.

### Phase 2: Challenge and quiz engines, review queue, first adapter
Completes tmux to all four engines, lands D10's cross-module queue, and implements the **first adapter**, which is tmux and is the easiest of the four because tmux is designed to be scripted. At the end of this phase the app verifies real work, which is the entire argument for it being a terminal app, and it is the first point worth handing to anyone.

### Phase 3: vim / neovim
Adds the nvim RPC adapter and authors the shared `modal-grammar` pack.

**This is Doom preparation, not a detour.** Doom runs `(evil +everywhere)`, so its normal-mode grammar *is* vim's grammar. Teaching it once here and consuming it in Phase 4 per D9 is strictly less work than teaching it twice, and it is why vim precedes Doom despite Doom being the more wanted module.

### Phase 4: Doom Emacs
Adds the `emacsclient` adapter, the richest of the four. Covers only the Doom-specific layer: the `SPC` tree, workspaces, buffers and windows the Doom way, popup rules, and where evil diverges from vim inside Emacs. Vanilla `C-x` / `C-c` bindings land as a late lesson, never as a parallel track.

### Phase 5: org-mode
Document model, TODO states, capture, refile, agenda. Needs no adapter protocol: org files are text, so verification is reading the file.

> [!success] Finish line, per D17
> **The priority four are done at the end of this phase.** tmux, vim, Doom, and org-mode all exist across Walkthrough, Practice, and Drill, three adapters verify real work, and a cross-module review queue runs over the lot.
>
> Everything past here is for later learning and for other users. It is worth building, but the project is a complete and useful thing at this line and stopping here is a success rather than an abandonment. Phases 6 onward should be picked up when the tool in question is the tool actually being learned, not worked through as a checklist.

### Phase 6: regex
The natural first pick-up after the finish line: self-contained, high value, and it proves the in-process grading path by running the user's pattern against intended matches and against negatives that must not match. Python's `re` makes this better than the browser plan could have been, because it is closer to what the user will actually type. Also the prerequisite that unlocks Phases 7 and 10.

### Phase 7: Linux Basics, then bash
Basics before bash, because bash assumes the filesystem, permissions, and redirection model that Basics teaches. Introduces the **sandbox directory adapter**, which is the most reusable of them all: a temp tree the trainer creates, the user operates on, and the trainer inspects. Quoting and expansion gets top billing per the roster note.

### Phase 8: git, then Remote access and network tooling
The two highest-payoff modules for the author's working life as opposed to the author's editor. Git verification is a scratch repo the trainer creates, which makes it one of the best-verified modules in the roster. Git may move ahead of Phase 4 if magit turns out to be the reason Doom is worth learning; see Open question 3.

### Phase 9: Linux Advanced, then Linux Utilities
Advanced needs Basics. Utilities is a drill deck rather than a course, so it can be authored incrementally in the background at any point after Basics and does not have to be a discrete phase at all.

### Phase 10: awk and jq, then tcpdump
Both benefit from regex (Phase 6) already being in place. awk and jq can be verified by running the real binaries against sandbox input, which makes them unusually well suited to this app.

### Phase 11: Python, PowerShell
PowerShell last. It is the least immediately useful of the fifteen. It shipped content-only because `pwsh` was not installed; installing it in session (aa) made the object half checkable, and only the Windows-only cmdlets remain unverifiable. See D25.

---

## Open questions

1. ~~**Project name.**~~ **Answered 2026-08-12: `hone`.** To sharpen a blade, which is exact for a tool that improves your use of tools you already have. Folder, file, package, command, build outputs and the vault `.gitignore` exception were all renamed together while nothing linked to them.
2. ~~**Vault cross-linking.**~~ **Answered 2026-08-12 by D23: no, never.** The program is self-contained. Prose may mention a note; nothing resolves a path. Verified at the time of deciding that no content referenced the vault and that the only reads outside a sandbox were the app's own state directory and the documented Doom config read.
3. ~~**Whether `git` should precede `Doom`.**~~ **Moot as of 2026-08-12:** both shipped, git in Phase 8 and Doom in Phase 4. The underlying question survives only as a study-order preference, which the app does not enforce anyway: D16 rule 3 shows prereqs and never gates them.
4. ~~**Whether the trainer should manage its own tmux layout.**~~ **Answered by D21 and built 2026-08-12.** Suspend-and-hand-over remains the base behaviour everywhere; the split runs only when the trainer is already inside tmux, and `--no-split` disables it. Lives in `hone/handoff.py`.
5. ~~**Which chord is reserved as the drill exit, per D19a.**~~ **Settled in Phase 0 as `F10`**, recorded in `hone/config.py` with its reasoning and one accepted caveat: vanilla Emacs binds F10 to `menu-bar-open`, which is not plausible drill content. `validate.py` enforces that no drill claims it, and `--exit-key` overrides it. All 429 drills were authored against it, so changing it now would invalidate `accepts` lists.

---

## Session log

| Date | What happened |
|---|---|
| 2026-08-12 (aa) | **The last two content-only modules now check your work, and checking became a mode.** Prompted by the author installing `tcpdump`, `wireshark-cli` and `powershell-bin` and asking the obvious question: if the tools are here, why is the app still only reading at me. The answer for tcpdump was embarrassing on inspection. The module was content-only because D1 forbids capturing traffic, which is true, and that reasoning had quietly assumed **the only way to get a capture file is to capture one**. You can also write the bytes: `pcapgen.py` builds a fifteen-packet fixture from `struct` alone, with an HTTPS session, DNS, a refused SSH connection, cleartext HTTP from a second host, a ping and one packet from another subnet, each chosen so that some filter distinguishes it from its neighbour. Nothing opens an interface, nothing needs a privilege, and `dumpcap` being root-only never comes up because it is never invoked. **Both filter languages are now graded in the tool that owns each**, `tcpdump -r` and `tshark -r -Y`, which turns the module's central claim from an assertion into a demonstration: type `tcp.port == 443` into a capture drill and tcpdump refuses it in its own words, type it into the next drill and it passes. The two tools are reduced to a common packet identity (tshark reports `frame.number`; tcpdump only knows clocks, so its timestamps map back through the spacing `pcapgen` applied), which is what lets a drill ask for *the same packets in the other language*. **PowerShell splits honestly in two**: the object pipeline runs for real in `pwsh -NoProfile`, and `Get-WinEvent` is not faked, because the entire lesson of that content is that filtering belongs at the source when the source has millions of records, and a fifty-row imitation teaches the opposite by making both approaches feel instant. Three real bugs surfaced while building it, all found by running the thing rather than by reading it: PowerShell colours its errors even into a pipe, so escape codes were reaching the comparison and making identical outputs differ; PowerShell **drops the aliases that would shadow real binaries on Linux**, so `sort Length -Desc` silently ran `/usr/bin/sort` and complained about a flag, which is an error message pointing at the wrong universe, and is now detected and explained; and the logon fixture had `admin` and `jsmith` tied at three failures, so "which account failed most" had two defensible answers and whichever student's sort broke the tie the other way was marked wrong for someone else's implementation detail. **Grading is behavioural throughout**, the argument `grading.py` already made for regex: `tcp port 443`, `port 443 and tcp` and `tcp and port 443` are one filter with three spellings. `validate.py` runs every reference answer at build time and additionally rejects a reference that selects *no* packets, since an untestable drill passes every equally empty answer. **D25** was recorded for running text the student typed, and it is strictly smaller than a capability D21 already had, since a challenge handover is a real interactive shell with no timeout. **D26** made checking a switch: `checked` and `read`, `m` on the home screen or `--mode`, with every degrade carrying its reason so an oracle drill in read mode still says in as many words that it was compared as text and not run. Also this session, all from use: the **splash now waits for a key** instead of vanishing on a timer, since the one screen carrying the app's name was the one screen nobody got to look at; the **tagline** stopped counting modules (`fifteen tools · your pace` goes stale every time the roster moves) and became `read it · run it · prove it`, which is D16's three views and D8's three tiers; **RIGOR** on the practice screen became a heading rather than dim text flush against three chips, where it read as a fourth chip you could select; and rigor is now **arrow-selectable and defaults to `free`**, because handing someone the steps before they have tried the task answers a question they have not asked. 399 drills to **429**, `test.py` 4449 to **4673** green. |
| 2026-08-12 (z) | **D24: the habit machinery removed, and the interface rebuilt around free exploration.** The author's call after using it: *"I don't think the due, next and streak systems are really necessary. I want the student to feel free to explore whatever tool they are interested in, in any order, on their own pace and time, and each module should be clear and stand on its own."* That reverses **D10** (the cross-module review queue) and **D22** (gamification) outright, and both are struck through above rather than quietly edited, because the reasoning behind them was sound and the decision that overrode it was about what the app is *for*. Deleted: `schedule.py` (SM-2, intervals, ease, due dates), `achievements.py`, `suggest.py`, `screens/review.py`, `screens/stats.py`. An answer now records two counters, `seen` and `correct`, and nothing else: there is no interval to compute and no date to write down, because an attempt is evidence about the item rather than about the day you had. State went to **version 2** with a migration that keeps everything you actually did (`seen`, `correct`, `done`, notes) and strips every scheduler field, so a v1 file opens with its progress intact and its streak quietly forgotten, which is the honest outcome: the streak was never evidence of anything. The **home screen** is now a shelf: tools grouped under headings (Editors, Terminal, Text processing, Linux, Version control, Network, Scripting), a progress bar that is a description rather than a deadline, and nothing above it. Found while building it: **the cursor indexed registry order while the display followed group order**, so Enter opened a different tool from the highlighted one the moment a group was not contiguous; the cursor now indexes what you are looking at, and a test walks every row asserting the highlight and the action agree. The third column no longer says `✓ verified`, which is D8's word for *a task you completed under real verification* and was being printed beside tools nobody had opened: it now says `✓ checks your work` or `· needs nvim`, which is a statement about the machine, not about you. Notes survived the cull and moved: `n` on the home screen for all of them, `n` inside a tool for that tool's. Drill decks gained `s` to shuffle, since a deck always met in the same order teaches the order. Tagline retired from "one habit" to "your pace". `test.py` 4452 green with six whole sections deleted and one added that asserts the scheduler is gone and cannot come back by accident. |
| 2026-08-12 (y) | **First outside use, and the four things it broke on.** Reported after one session with the vim module: "it launched nvim on top of hone and I had no idea what to do." **The handover was a cliff.** Everything the student needed was on the screen they had just left, and D21 hands the terminal over without a word. `hone/handover.py` now treats a handover as a transition that has to say three things. *What is about to happen*: every adapter answers `opens()`, and the brief screen shows it under WHEN YOU PRESS RET, along with the **starting state** derived from the challenge's own `setup` (the seeded lines, the seeded files, the seeded commits), so all 56 challenges gained it without a word being rewritten. *What you are trying to do* and *how you get back* travel **into** the tool: an nvim statusline and winbar (plus `:messages`, because a configured nvim will replace a statusline), an Emacs `header-line-format`, a tmux `display-message`, and for shell handovers the whole brief printed, since a shell does not clear the screen. Every adapter now declares `return_hint`, because the way out of nvim is not guessable from the way out of tmux and guessing wrong loses the work. Found while building it: **the nvim leave hook read the current buffer**, so opening any other file before quitting dumped the wrong text and failed a student who had done the work correctly; it now addresses the scratch buffer by number. Both the statusline and the buffer targeting were verified against real nvim, and the header line against real Emacs. **Getting home took too many keys.** `H` unwinds the stack to the home screen from any depth, declared in every footer where it works and deliberately absent from the two places where keys are answers (capture drills, the note editor) and from a half-answered self-mark. **There was no way to start over.** `hone --reset [tool]` erases progress, keeps preferences, writes a timestamped backup *before* the prompt, deletes that backup if you decline, and refuses entirely without a tty unless `--yes`. `--import` puts it back. **Drills were abstract.** A capture drill is the least oriented screen in the app: no file, no cursor, no shell. Every module now carries a one-line `context` saying what world its drills assume (validate makes it a requirement for any module with drills), and capture mode draws **empty slots for the keystrokes it is waiting for**: it grades the moment the last key arrives, so hiding the count meant being graded at a moment you could not predict. `test.py` 4212 green. |
| 2026-08-12 (x) | **Deep audit: eleven real bugs fixed, every one regression-tested, then four features.** The bugs, worst first. **Quiz answers never counted toward progress**: `counts()` looked for `done` and quiz cards carry `seen`, so no module with quiz content could reach 100%; drills were counted by `reps`, which resets on a lapse, so progress *dropped* when you missed something you had held for a month. Both now count by `seen`, and generated `rev:` cards are excluded so they cannot stand in for authored questions. **Reads created records**: `evaluate()` on the stats screen created a module record for every installed module, rendering a module list created an empty item for every row scrolled past, and reading a note created the item it was reading; the empty records then counted as evidence the drill engine had been used (Full circuit). `State.peek()` now exists, and reads go through it; only writes create. **Quitting mid-challenge leaked the sandbox**: `_release` was wired to Esc, and `q` bypassed it; `Screen.close()` is now a lifecycle hook the app calls on pop, replace, and shutdown. **tmux challenges inside tmux never worked**: a nested `tmux attach` is refused outright, so the split pane died instantly and the student was graded on an empty session; attach handoffs inside tmux now go through `switch-client` and hone waits for the drill session to have no clients. **The git sandbox inherited the user's global config**: a global commit hook could fail the seeded history, `commit.gpgsign` could hang setup, and a global excludes file could hide a student's untracked file and flunk work they did; every git call now carries neutralising `-c` flags (repo `.gitignore` still honoured, which is the part challenges teach). **The Alt decode path swallowed keys**: `ESC a b` in one read emitted `M-a` and dropped `b`. **Structurally broken state crashed later**: valid JSON with a list where a module record belongs passed `load()` and crashed at use; `_migrate` now drops malformed records, and naive timestamps get UTC attached rather than poisoning comparisons. **D8 labels could be overstated on latent paths**: an unknown `fallback` became a `Plan.kind` that crashes `LABELS`, and a `graded` challenge with no adapter recorded `graded` on a self-marked answer; both collapse to `self` and validate rejects the shapes. **Home's due counts included stale cards** the review screen would skip, so the number a student checks daily could lie; counts, the Next line and the queue now agree through `schedule.resolvable`. **SIGTERM/SIGHUP bypassed every finally**, leaving raw mode + alt screen and unsaved answers: both now raise SystemExit. **The idle loop repainted twice a second forever**: it now redraws only on input or resize. Also fixed: `box_top` clamps instead of tearing the frame on a long title, `export_to` writes atomically like `save`, lesson end-of-scroll records once per visit not per repaint. **The features**: `hone --doctor` prints the whole capability story (terminal rungs, Kitty, every adapter probe, state health, sync status) for the support conversation D18/D20 make necessary; a one-line **quit summary** closes the session with evidence ("14 answered, 12 right. queue clear, next due tomorrow."); the record screen gains a seven-day **due forecast** (today / tomorrow / this week); and **notes are browsable**: `n` on the record screen lists every note you have left yourself, stale ones hidden, Enter re-drills the noted item on the spot. `test.py` 4126 green, both validate passes zero, artifacts rebuilt. |
| 2026-08-12 (w) | **All 181 missing teach lines, written.** The lint's one honest finding is closed and then some: the ratio rule had only flagged the eight modules where over half the drills were bare (133 lines), and the remaining 48 sat invisibly under its threshold in vim, Doom, org, and the two other Linux modules, so both batches were written and **every one of the 399 drills now carries a `teach` line**. House rule applied throughout: a teach line explains the mechanism or names the trap, and never restates the answer already on screen above it. With coverage at 100% the lint was tightened from the per-module ratio to naming each bare drill individually, so a regression is one precise warning rather than a statistic, and `test.py` now asserts the shipped content lints fully clean with no exemption. The insertion itself was done by AST position rather than text surgery (`ast.parse`, walk to each drill dict by its `id`, insert before the dict's own `end_col_offset`, bottom-up so positions stay valid), because text surgery on these files ate three closing braces earlier in the session and the AST knows exactly where a dict ends. Both `validate.py` runs at **zero warnings**, `test.py` 4010 green, both artifact sets rebuilt. |
| 2026-08-12 (v) | **Seven improvements, and a lint that found real content bugs.** The app now answers *what should I do now* on the home screen instead of showing fifteen tools and a progress bar: `hone/suggest.py` picks one action in a fixed order (anything due, then whatever you last opened, then the first module you have not started) and `space` does it. Reviews interleave by default, so a session no longer clears all of tmux and then all of vim; `schedule.interleave` round-robins largest-bucket-first while preserving hardest-first order inside each module, and `settings['interleave']` turns it off. `ReviewScreen` gained two more session modes over the same machinery: **weak spots** (`schedule.weak_items`, ordered by accuracy and deliberately ignoring the due date, because *what will you forget soonest* and *what do you keep getting wrong* are different questions) and **recognition**, generated by inverting drills you have already met. Reverse items are real scheduled cards under a `rev:` id prefix, with `Module.item()` synthesising them so the queue does not treat them as stale content, and their distractors are other prompts from the same module, written by the same hand and therefore plausible for free. **Per-drill notes**: `n` during feedback attaches a line that comes back on the prompt every time the drill does, which is where the useful thought actually is: the moment you get something wrong you know why, and thirty seconds later you do not. That forced capture-mode feedback to stop advancing on *any key*, since `n` is a letter, and the footer now says `⏎ next  n note  F10 leave`. `--sync` remembers a file and rewrites it on every exit; it is explicitly **not** a merge engine, because merging two SM-2 schedules means inventing an answer about what you knew, and `sync.check` only ever *tells* you the remembered file is newer. **`validate.py --lint`** adds prose and consistency checks behind a flag so the default run stays at zero warnings: a validator that always prints ten complaints you have decided to ignore is one you stop reading. It immediately found a double space, six drill prompts that described instead of instructing, and fourteen over-long ones, all now fixed; its first draft also linted shell commands as if they were sentences, which is why `PROSE_FIELDS` lists the prose fields per kind rather than guessing. The eight warnings left are one honest finding: over half the drills in eight modules have no `teach` line, so a wrong answer explains nothing. `test.py` at 4009 checks, and `walk_screens` now walks a drill's feedback and note phases too, since those are screens the student sees. |
| 2026-08-12 (u) | **The D21 split enhancement, plus two promises the app had been breaking.** `hone/handoff.py` now owns the whole handover decision: inside tmux the tool opens in a pane beside the trainer, everywhere else it suspends and hands over the terminal, and `--no-split` forces the latter. Two things learned building it, both the hard way. **`tmux wait-for` is the wrong primitive**: it is elegant and it blocks forever if the pane dies without signalling, which hung a terminal for two minutes; polling for the pane id is robust to every way a pane can end. And **never name a window index**: `session:0` does not exist wherever `base-index` is 1, which is exactly the fragility this project's own tmux module teaches. **Two D19 promises were being broken.** `?` was advertised in nearly every footer and did nothing at all for the entire build, which is precisely the rule 4 failure the footer contract exists to prevent, and `state.settings['seen_tour']` was reserved in Phase 0 for a first-run tour that was never written. Both now exist as one paged-card screen: `?` opens help from anywhere, and a fresh install gets three cards first. The `?` bug survived nine phases because `test.py` only ever checked that `esc`, `q` and `tab` were live and exempted everything else; that hole is closed, and every advertised key is now checked on every screen. Capture-mode drills deliberately do not offer `?`, because there it is an answer. Final gate: **3142 checks**, stable across repeats. |
| 2026-08-12 (t) | **PHASE 11 COMPLETE, AND THE ROSTER IS FINISHED.** All fifteen modules ship. **Python** is framed deliberately as the answer to the question the regex module ends on, which is what to do when a problem outgrows a pipeline, so lesson one is about knowing when you have crossed that line and is explicit that a short clear pipeline is better engineering than a thirty-line script doing the same thing. Basics only, per the original ask: no classes, no decorators, no async, and instead the data types, files, and six standard-library modules a working script actually uses. Fully verified, because a Python script writes files and the sandbox reads files. **PowerShell is content-only and says so**, per D18: `pwsh` is not installed and there is no offline sandbox for Windows semantics. The entire module is one reframe, that the pipeline carries objects rather than text, with `Get-Member` taught as the habit that makes the rest discoverable. Its DFIR payoff is `Get-WinEvent` and the difference between filtering at the source and filtering afterwards, which on a real Security log is the difference between a useful tool and an abandoned one. Final gate: **2983 checks**, stable across repeats, fifteen `.pyz` files, nothing left behind. |
| 2026-08-12 (s) | **Renamed to `hone`, and PHASE 10 COMPLETE.** The "CLI Trainer" placeholder was becoming actively confusing, since the app is itself a CLI tool that teaches CLI tools. `hone` means to sharpen a blade, which is exact: you do not hone something you have never touched. Renamed together while nothing linked to any of it: the folder, this file, the Python package, `APP_NAME` and `APP_TITLE`, every import, the build outputs (`hone.pyz` and `hone-<tool>.pyz`), the tmux scratch session, the temp-directory prefixes, the git identity, and the vault `.gitignore` exception. The test suite caught nothing broken, which is what a 2426-check suite is for. **D23** was recorded at the same time: **the program is self-contained, no vault cross-linking ever**, superseding the softer suggestion in Open question 2. Verified at the time that no content referenced the vault and the only reads outside a sandbox were the app's own state directory and the documented Doom config read. **awk and jq** ship as one module, taught together because both are small filter languages doing the same job on different data shapes, and the last challenge deliberately pipes jq into awk to make that concrete. Fully verified with no new adapter, since both are ordinary programs that read a file and write to stdout. **tcpdump is content-only and says so**: capturing needs privileges and an interface, which D1 puts out of reach, and `tcpdump` is not installed here either. Its scope is drawn tightly at filter syntax, built around the contrast nobody teaches on purpose, which is that `tcp port 443` and `tcp.port == 443` are two different languages. Final gate: **2712 checks**, stable across repeats, thirteen `.pyz` files, nothing left behind. |
| 2026-08-12 (r) | **PHASE 9 COMPLETE: Linux Advanced and Linux Utilities, and a real layout bug.** Advanced finishes what Basics deliberately left out: the fourth permission digit and the setuid family, ACLs and capabilities, file descriptors properly including the `2>&1` ordering, signals with orphans and zombies, mounts and why `df` and `du` disagree, systemd with the start-versus-enable trap, and local network state with `ss -tulpn`. **Utilities is the first module with zero lessons**, which is deliberate and which finally puts real content behind the D16 rule 1 empty state written in Phase 0: the Walkthrough view says "this tool is a drill deck, by design" and sends you to Drill. Its teaching lives in each drill's `teach`, where it is read at the moment it is relevant, which is the right shape for `tar`. **The bug that phase found is the important part.** Thirty-seven drills rendered as thirty-seven rows and ran straight off the bottom of an eighteen-row terminal, because `ListScreen` had no windowing and `test.py` had only ever asserted **width**. Every module now has more items than a small terminal has lines, so this was not an edge case. Fixed in two places: `ListScreen` windows its rows around the cursor with an above/below indicator, and `Screen.render` gained a **hard height backstop** so the invariant holds once, centrally, regardless of what any screen does. Verified from eight rows upward. `test.py` now asserts height alongside width everywhere, plus a dedicated case with sixty drills across four terminal sizes. Final gate: **2426 checks**, stable across repeats, twelve `.pyz` files. |
| 2026-08-12 (q) | **PHASE 8 COMPLETE: git and Remote access.** `hone/adapters/git.py` subclasses the sandbox one, because a repository **is** a directory and every file assertion already worked; it adds only what a directory cannot show, which is the commit graph and the index. It seeds a repo from a declared history so challenges start somewhere known, sets identity and default branch locally so nothing depends on or touches your global config, and filters `.git` out of the file listing so file assertions stay readable. git is now the best-verified module in the roster: branch, commit count, subjects, staged, untracked, tags and detached HEAD all have exact plumbing answers. The content teaches **the model first**, because git's problem is a small clean model hidden behind an inconsistent CLI, and someone holding "commits are snapshots, refs are pointers, branches are labels" can derive `reset --hard` while someone who memorised `reset --hard` can derive nothing. **Remote access is honest about being the weakest module for verification**, exactly as the plan's own detail section predicted. D1 forbids touching a network, so the split is visible: writing an ssh config, generating a real keypair with the modes ssh insists on, running rsync between two local directories, and building and inspecting a certificate are all **verified and entirely offline**; the trailing-slash and `-L` versus `-R` misconceptions are **graded** as predictions; and one challenge needing a second machine is **self-marked and says so** rather than pretending. **One bug:** `test.py`'s solution replayer dispatched on adapter name, so the arrival of `git` meant its challenges silently replayed nothing and reported as unsolvable. It now dispatches on the shape of the solution, which no future adapter can break. Final gate: **1838 checks**, stable across repeats, ten `.pyz` files, nothing left behind. |
| 2026-08-12 (p) | **PHASE 7 COMPLETE: Linux Basics, bash, and the sandbox adapter.** `hone/adapters/sandbox.py` is the most reusable of the five and the only one **requiring nothing installed**, because the tool it verifies is the filesystem: build a small tree, hand over a real shell standing in it, then walk the tree and compare. It reads files, contents, modes, symlinks and directories, and every failure message names the path and what was actually there. Two supporting changes: the D21 handoff grew a **working directory**, which no adapter had needed until the point of one was standing inside the tree; and `_resolve` **refuses any content path that escapes the sandbox**, so a stray `../` in a hand-authored content file cannot become a mistake on someone's disk. It also takes a shell selector, and the bash module asks for **bash specifically** rather than the author's fish, because running bash challenges in fish would teach the wrong thing. Linux Basics is deliberately first, since bash assumes its filesystem, permission and descriptor model, and it teaches concept with tool throughout: permissions arrive with `chmod`, redirection with the stream numbers, processes with signals. bash puts **quoting and expansion first**, because nobody's script breaks on a `for` loop and everybody's breaks on a filename with a space, and lesson one names the fish gap outright. Predict-the-output lives in the quiz rather than the drills, per the plan's own guidance that "write a pipeline that does X" has too many correct answers to grade honestly. All eight challenges played through a real shell. Final gate: **1581 checks**, stable across repeats, eight `.pyz` files, nothing left behind. |
| 2026-08-12 (o) | **PHASE 6 COMPLETE: regex, and the `graded` tier finally exists.** `grading.py` implements the third D8 tier, which had been declared since Phase 0 and never used. **Patterns are graded by behaviour, never by string comparison**: the pattern runs against strings it must match and strings it must not, so `^ERROR` and `^(ERROR|FATAL)` both pass, and the negatives catch the failure a positives-only check cannot see, which is a pattern that works by matching far too much. Execution is bounded, and **hitting the bound is a lesson rather than an error**: `(a+)+$` reports catastrophic backtracking by name. Verified first that CPython's regex engine yields to signals under the usual pathological patterns, so no subprocess was needed, and the timer is disarmed on every path including the exception one. New `regex` drill type renders its match and reject sets on screen, because nobody can write a pattern blind. Challenges are real `:%s` and `:v//d` transformations in nvim, which is one of the module's own stated applications, so no new adapter was needed either. **`validate.py` ran every reference answer through the grader and found one of mine wrong**: `\b\d{1,3}(\.\d{1,3}){3}\b` still finds `1.2.3.4` inside `1.2.3.4.5.6.7`, because a dot is already a non-word character so the boundary sits happily in the middle. Split into an easy drill about escaping dots and a strict one that needs lookaround, which is a better pair than the broken single. Final gate: **1333 checks**, stable across repeats, six `.pyz` files, nothing left behind. |
| 2026-08-12 (n) | **PHASE 5 COMPLETE, AND THE D17 FINISH LINE IS REACHED.** org-mode shipped with no new adapter, exactly as planned: org files are text, so `hone/adapters/emacs.py` already read them and the only change was a `.org` scratch name so the major mode turns on. Fixed a latent bug found while doing that: `scratch_name` was set on the shared adapter instance and leaked into the next challenge, so a `.org` scratch could turn on a major mode a plain-text challenge never asked for. The module is **written for someone who already keeps notes in Obsidian**, because that is the honest situation: every lesson names the Obsidian equivalent where one exists, and the last lesson answers the question the rest keep raising, which is whether org replaces the vault or sits beside it. The recorded answer is that it should not replace it, that migrating costs weeks and loses the graph, and that one inbox file plus an agenda is a complete org install. **`validate.py` caught a real content bug on its first run** (an `accepts` alternative duplicating its own answer) and the fix exposed a second class it could not yet see: two drills with **identical keystrokes but different prompts**, which the student cannot possibly tell apart and which the scheduler would treat as a permanent weakness. `check_drill_collisions` now warns on that. Final gate: **1185 checks**, stable across repeats, five `.pyz` files built, nothing left behind. |
| 2026-08-12 (m) | **PHASE 4 COMPLETE: Doom Emacs and the Emacs adapter.** Extracted `hone/adapters/_buffer.py` first, because nvim and Emacs verify identically and differ only in how you launch them and how you ask for a buffer dump on exit; org-mode will be the third case. The shared base fixed a convention while it was cheap: **the leave hook is `argv[-2]` and the file `argv[-1]`** for every buffer adapter, since editors put their flags in different places and indexing from the front means every caller has to know which editor it is holding. `hone/adapters/emacs.py` deliberately **requires only `emacs`, not `emacsclient`**: this machine has no server running, and a verification tier that works for half of Doom's users is not a tier. It launches `emacs -nw` on the sandbox file with a `kill-emacs-hook` attached by `--eval`, so nothing persists and no daemon gets a stray buffer. When a server *is* running, `emacsclient --eval` is available opportunistically. It also adds `config_contains`, which reads `~/.config/doom/*.el` to verify a challenge that asked you to change your own configuration: D1 permits reading your state and forbids only writing outside the sandbox. `hone/content/doom.py` **teaches no modal editing at all**, because Doom runs evil and the vim module owns that grammar; teaching it twice would let the copies drift. Instead: the `SPC` tree and why discoverability is the design, files versus buffers versus projects, workspaces, where evil is not vim, search as navigation, the `doom sync` trap, and vanilla `C-x`/`C-c` as the last lesson rather than a parallel track. All three challenges verified through real Emacs. **One bug, mine twice over:** I indexed `argv` wrong when hand-driving both nvim and Emacs in throwaway tests, which is exactly what the `argv[-2]`/`argv[-1]` convention now prevents. Final gate: **1067 checks**, stable across repeats, nothing left behind. |
| 2026-08-12 (l) | **Gamification: stats, streaks and achievements (D22).** Added at the author's request, with the design rule stated first: reward evidence of learning, never volume. There is no badge for answering N things or for time spent. Thirteen achievements across retention, fluency, coverage, habit and craft, all pure functions of stored state so a badge can never disagree with its own evidence. The retention ones are the point, because recall after three weeks away is something a spaced-repetition tool can measure and a quiz app cannot. **A self-marked completion cannot earn the verified badge**, and there is an achievement for marking a self-marked task *not done*, which is D8 stated positively. Cards now keep `best_ms`, `max_interval` and `first_try`, because none of the three can be recomputed once an interval resets or a latency is overwritten. State keeps a per-day activity log, which is what streaks read. **Two bugs fixed:** the scorecard reported "weakest" items at 100% accuracy, because sorting ascending and taking the top three always returns something, so `weakest` now has a threshold and the screen says "nothing is weak yet" when nothing qualifies; and a tmux test was flaky because killing the last session stops the server and the very next `new-session` can fail outright rather than merely be slow, so the helper now retries the creation instead of polling for it. Final gate: **947 checks**, stable across three consecutive runs. |
| 2026-08-12 (k) | **PHASE 3 COMPLETE: vim / neovim and the nvim adapter.** `hone/adapters/nvim.py` replaces the browser plan's normal-mode emulator, which was its largest engineering item, with about a hundred lines: seed a scratch file in a sandbox, hand the terminal to real nvim, and read what happened. One `-c` command registers a `VimLeavePre` autocmd that dumps the buffer and final cursor into the sandbox, so **the adapter can tell "made the edit and forgot to save" from "never made the edit"** and say so. The student's own config is used deliberately, because a trainer running `-u NONE` grades an nvim nobody has. `hone/content/vim.py` owns the **`modal-grammar` pack** that Doom consumes per D9, ordered so lesson 3 makes the rest guessable, and carries the **first capture-mode drills**: nothing eats vim's keys, so `ciw` is graded as an actual keystroke. **Three real bugs.** A challenge began with the cursor already on the first match, so `/oldname` skipped it and the challenge's own steps could never reach its stated goal, found only by playing it for real. A tmux solution hardcoded window index 0, which fails wherever `base-index` is 1, a fragility this module's own lesson warns about. And most seriously, **a stale tmux session with three panes would have made "build three panes" pass without the student touching a key**; the adapter now records whether the sandbox pre-existed and refuses to grade what it cannot attribute, degrading to self-marked with the reason rather than handing out a false pass. Challenges now carry a `solution` and `test.py` plays every adapter-verified one through the real tool, which is the strongest guarantee the harness can give about content. |
| 2026-08-12 (j) | **PHASE 2 COMPLETE: the app verifies real work.** `hone/adapters/tmux.py` reads sessions through `has-session`, `list-panes` and `list-windows`, all read-only. **D1 is the shape of that file**: setup creates the scratch session only if it does not already exist and records whether it was the creator, and teardown kills it **only if setup created it**, so a session you already had by that name survives. Verified live. `hone/screens/challenge.py` renders one definition at three frictions (D6), decides and displays how it will be checked before you start (D16 rule 4), hands the terminal over with D21's suspend-and-resume, and on failure **keeps the sandbox for a retry** rather than making you rebuild from nothing. `hone/screens/quiz.py` shuffles options deterministically per attempt, seeded from the item id and its seen count, so order varies between attempts and replays identically in tests. `hone/screens/review.py` walks the cross-module queue of D10 by owning one sub-engine at a time and forwarding to it, which keeps the drill and quiz engines unaware they are being used this way. **Three bugs, two of them real.** A challenge's `verify.expect` had been authored as a prose string where a dict belonged; D18 caught it at runtime and degraded honestly rather than crashing, but `validate.py` should have caught it earlier, so adapters now declare `expect_keys` and validate rejects both a non-dict expect and any key the adapter cannot read. The review queue **silently skipped whatever item followed a quiz**, because the quiz replaces `self.sub` through `on_finish` and the drill-advance check then ran against the new sub while holding the old phase. And `reset()` stopped producing an empty registry once builtins auto-registered, making "no adapters installed" untestable. Final gate: **722 checks green**, validate clean with zero warnings, no stray tmux sessions left behind. |
| 2026-08-12 (i) | **PHASE 1 COMPLETE: walkthrough and drill engines, tmux content.** `hone/screens/lesson.py` renders concept prose, worked examples, misconceptions and try-it callouts, scrolls, and marks a lesson read when you reach the bottom, which is the only thing about reading the app can honestly observe (D8). **Drills now come in two modes.** Capture mode grades real keystrokes and is what vim and Doom will use. Text mode was added because tmux needs it: tmux binds `C-b`, so a trainer running inside tmux never sees the prefix and one running outside drills the chord stripped of its context. Recall answers are graded by **parsing the typed text back into keys**, so `C-b "` and `C-b S-'` both pass and one authored `keys` list serves both modes with nothing written twice. Command drills grade a typed shell command against normalised alternatives. **Two bugs the harness caught immediately:** text mode's footer advertised `q quit` while `q` is a letter you need to type, which is the D19 rule 4 trap again in a new place; and `Text.truncate` defaulted to a `…` ellipsis that would have leaked non-ASCII the moment any real line was long enough to clip, so the ellipsis moved into the glyph set. tmux content: **8 lessons, 30 drills, 4 challenges, 8 quiz items**, ordered so the session/window/pane model is built first and every later binding reads as a verb applied to one of those three nouns. Quiz items test the model rather than the bindings, because the drills already cover recall. `test.py` gained a **real-content pass** that the fixtures cannot do: every drill must accept its own answer and every declared alternative, junk must be rejected, every lesson must render and fit and have its `next` resolve, and every quiz answer must not appear among its own distractors. Final gate: **669 checks green**, and `--per-tool` produces `tmux-trainer.pyz`, making D4a real. |
| 2026-08-12 (h) | **PHASE 0 COMPLETE.** Core, adapters, screens and harness all landed on top of (g). `state.py` writes atomically and never raises on load: a corrupt file is quarantined with its bytes intact rather than overwritten. `schedule.py` is SM-2 with one addition, that **latency feeds the quality score**, so a slow-but-correct answer earns less ease and returns sooner than a fast one; verified along with the cross-module ordering D10 requires (hardest first, spanning tools). `loader.py` discovers additively and is fault tolerant: a deliberately broken content file is recorded as an error while the app stays up. `hone/adapters/` ships the interface, registry and degrade path with **zero real adapters**, and the fake enforces the D1 contract in tests (observe refuses before setup, teardown is idempotent, a failing teardown never masks the result). Screens made D19 structural: `ListScreen` owns both its navigation keys and the hints describing them, so rule 4 holds by construction. **Four real bugs were found by testing, not by reading:** the root footer advertised `esc quit` while Esc did nothing there; `q` was handled without ever being declared; the footer rendered below a closed box and looked detached; and hardcoded glyphs leaked non-ASCII into the ASCII rung from three separate constants. The last one is now a permanent test. Reformulated D19 rule 2 as `Screen.escape_key` so the drill screen's reserved chord satisfies the same contract as Esc elsewhere rather than being an exception. Final gate: **539 checks green**, validate clean, and a 107K `.pyz` that runs from a directory with no source tree. |
| 2026-08-12 (g) | **Phase 0 started; terminal and render layers built and verified.** `keys.py` carries both the authoring notation and the byte decoder in one module because they must agree exactly, with `S-` folding into shifted characters so `S-'` and `"` are the same key. Verified the D11 payoff directly: under Kitty `CSI u`, `C-i` decodes distinctly from `TAB`, `C-m` from `RET`, and `C-[` from `ESC`; under legacy they collapse, and `AMBIGUOUS_LEGACY` names every collision so a drill can say so. `term.py` quarantines everything needing a TTY, so `test.py` can stay headless. Verified against a real PTY that raw mode engages, termios is restored exactly, and restoration survives an exception unwinding through the context manager. Two hardening fixes found by testing: the Kitty reply parser was accepting a malformed `CSI ? u` with no flag digits, now strict because a false positive is the expensive direction; and a slow DA1 reply could have leaked into the key stream as phantom keystrokes at startup, now drained. `theme.py` takes its default palette from the author's own Doom theme, which already ships per-rung fallbacks. `render.py` holds the whole D20 ladder, with screens building styled spans rather than escape codes so line widths are knowable without rendering. Proved the ladder by drawing one frame at truecolour, 256, 16 and none, and at Unicode and ASCII: fourteen lines every time, zero overflow, and the ASCII rung readable rather than merely functional. |
| 2026-08-12 (f) | **Presentation locked.** The student gets one contained, attractive, beginner-safe experience. **D19** sets the frame: full-screen layout, arrow-navigable menus, a permanent key-hint footer, and four beginner rules written so `test.py` can enforce them rather than leaving "discoverable" as an intention. **D19a** covers the one genuinely dangerous thing this app does to a novice, which is taking the keyboard: capture screens get a distinct border, an explicit banner, and a reserved exit chord no drill may claim. **D20** puts looks on the same capability ladder as verification, stepping truecolour → 256 → 16 → none and Nerd Font → Unicode → ASCII, honouring `NO_COLOR`, so a stranger in a bare `xterm` gets something plain and correct instead of tofu. **D21** answers what "contained" means when the real work happens in real nvim: suspend, hand over the terminal, resume to grade, the same pattern `git` uses for `$EDITOR`, with the tmux-managed split demoted to an optional enhancement. This **supersedes Open question 4** and adds a new question 5, the reserved exit chord, which must be settled in Phase 1 before drill content exists. Added a Look and feel section with screen mocks and the degradation table, moved the render layer into Phase 0 so the ladder is not retrofitted, and reinforced **D2a**: `curses` has a palette-index colour model that handles truecolour badly, which is now a second independent reason to avoid it. Default palette is the author's existing `doom-cyberpunk-neon`, so the trainer matches ghostty, tmux, fish, Doom, and neovim on this machine. |
| 2026-08-12 (e) | **Pivoted from a browser app to a terminal app** and rewrote this plan on that basis. The trigger was recognising that the D17 priority four are all locally installed, scriptable tools, which means the trainer can **verify what the user actually did** rather than accepting it: `tmux list-panes`, nvim RPC, `emacsclient --eval`, and org files being plain text. That collapses most of D8's self-marked bucket, and it **deletes the normal-mode buffer emulator** that was the largest engineering item in the browser plan. The keyboard-fidelity argument that originally favoured the browser was re-weighted and found bounded: it affects a short list of chords, and the Kitty keyboard protocol resolves them in ghostty, which the author runs. Restated **D1** (never acts on your behalf, reads your state, writes only its own sandbox), **D2** (Python 3 stdlib only, `zipapp` for single-file distribution), **D7** (state is a file, and the `localStorage` risk that made this decision necessary is simply gone), and **D11** (raw `termios` plus Kitty protocol with a documented legacy fallback). Added **D2a** (no `curses`, recorded as considered and rejected) and **D18** (verification is an optional capability tier that degrades to self-marked, never a foundation). Everything else survived untouched: D3 through D6, D8 through D10, and D12 through D17, plus the fifteen modules, the three views, the review queue, and the phase order. Added a per-module engine breakdown, an adapter interface, adapters to the roster table, and a fourth open question. |
| 2026-08-12 (d) | Three decisions added and the phases reordered. D15 states this is a completely separate project from Waypoint: no shared files, imports, or content, techniques copied rather than linked, and every Waypoint reference downgraded to a prior-art citation. The Remote access "boundary against Waypoint" was rewritten as a rule about this project's own scope (the tool, never the engagement), and the pentest-tooling skip no longer defers to another project. D16 locks navigation as tool-first then activity, with exactly three views, all always rendered, quiz as one engine with two surfaces, and prereqs shown but never enforced. D17 names the priority four and makes Phase 5 a legitimate finish line. Phases reordered to deliver those four first. |
| 2026-08-12 (c) | Remote access and network tooling written out in full, the first module to get a detail section. Structured as one arc through three questions (reach the service, get a session, move data and traffic) with port forwarding as the climax. Added `nc`, `socat`, `proxychains`, `sshfs`, and `ping` / `traceroute` / `mtr`, all earning their place by composing with `ssh -D`. |
| 2026-08-12 (b) | Roster consolidated and then re-split. Added the module boundary rule (own module only if learning it changes how you think; otherwise a drill deck), which killed the system-and-service pack into Linux, folded `grep` / `rg` / `sed` into regex and the pipeline vocabulary into bash, merged `awk` and `jq` into one contrast module, and grouped the remote-access tools under one module. `git` promoted to its own module and `tcpdump` accepted, both scoped tightly. Linux then split into Basics / Advanced / Utilities. Net: roughly twenty candidate units down to fifteen modules. Six new deliberate skips recorded. |
| 2026-08-12 (a) | Project scoped and first plan written. Placement decided (top-level in the vault, `.gitignore` exception added) because the roster is not all security work. |
