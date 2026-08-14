"""Python: where you go when the pipeline stops being readable.

**Basics only**, per the original ask, and framed deliberately as the next step
after bash, awk and regex rather than as a general programming course. The
regex module ends by saying that some problems want a real language; this is
that language, and the first lesson is about knowing when you have crossed the
line.

That framing decides the content. No classes, no decorators, no async. Instead:
the data types you need to hold a log file in memory, the control flow to walk
it, files and paths, and the six standard-library modules that cover almost
everything a working script does.

Fully verified. A Python script writes files, and the sandbox adapter reads
files, so a challenge is "write a script that produces this" and the check is
exact. Predict-the-output lives in the quiz, where Python's genuinely
surprising semantics belong.
"""

MODULE = {
    'id': 'python',
    'title': 'Python',
    'group': 'Scripting',
    'blurb': 'The language you reach for when the pipeline stops being readable.',
    'context': 'You are writing Python 3, either a line at the REPL or a line inside a script.',
    'needs': ('python3',),
    'prereqs': ['bash'],
    'adapter': 'sandbox',
    'estimate': '6-8 hours',
    'order': 60,

    'lessons': [
        {
            'id': 'py-when',
            'title': 'When to stop writing a pipeline',
            'next': 'py-running',
            'concept': (
                'A shell pipeline is the right answer far more often than '
                'people who like Python admit. It is shorter, it streams, and '
                'it needs no file. Reach for Python when one of four things is '
                'true.\n\n'
                '**The data is nested.** JSON with arrays inside objects, or '
                'anything you would need to count brackets to parse. jq handles '
                'a lot of this; past a point Python is clearer.\n\n'
                '**You need to hold state across records.** Correlating two '
                'files, following a session across lines, building a lookup '
                'table. awk can do some of it and stops being readable '
                'quickly.\n\n'
                '**The logic has more than two branches.** A pipeline with '
                'three greps and a conditional sed is a program that has not '
                'admitted it yet.\n\n'
                '**Someone will read it again.** Including you, in six months. '
                'A named function beats a clever one-liner every time the '
                'clever one-liner has to be modified.'
            ),
            'examples': [
                {
                    'label': 'Still a pipeline',
                    'code': ("awk '{c[$1]++} END {for (k in c) print c[k], k}' \\\n"
                             '  access.log | sort -rn | head\n'
                             '\n'
                             'short, streams, no file needed'),
                    'note': 'Rewriting this in Python is longer and worse. Know '
                            'when you have won already.',
                },
                {
                    'label': 'Now it is Python',
                    'code': ('correlate two files by a key, keep the ones\n'
                             'where the second file has a status over 400,\n'
                             'group by hour, and write a JSON summary\n'
                             '\n'
                             'four joins of state. A pipeline can do it and\n'
                             'nobody will be able to change it afterwards.'),
                    'note': 'The tell is holding state across records while '
                            'branching on more than one condition.',
                },
            ],
            'misconceptions': [
                'Python is not the grown-up choice. A pipeline that fits on one '
                'line and reads clearly is better engineering than a script '
                'that does the same thing in thirty.',
                'You do not need to pick one. `jq -r ... | python3 script.py` is '
                'a perfectly good design, and so is calling `subprocess` from '
                'Python.',
                'Python is slower to start than awk and often faster once '
                'running. Neither fact matters at the sizes most people work '
                'at.',
            ],
            'try_it': [
                'Find a pipeline in your own history with three or more stages '
                'and a conditional. Decide honestly whether it is still a '
                'pipeline.',
            ],
        },
        {
            'id': 'py-running',
            'title': 'Running it, and the environment',
            'next': 'py-data',
            'concept': (
                'Four ways to run Python, and knowing which is which saves '
                'confusion. `python3` alone is the REPL, which is the right '
                'place to try something. `python3 script.py` runs a file. '
                '`python3 -c \'...\'` runs a string, which is the shell-friendly '
                'form. `python3 -m module` runs an installed module, which is '
                'how `python3 -m http.server` works.\n\n'
                'A script gets a shebang, `#!/usr/bin/env python3`, and `chmod '
                '+x`, exactly as in bash.\n\n'
                'The environment question people trip on is that installing a '
                'package system-wide is now usually blocked, and correctly so. '
                'A **virtual environment** is a directory holding its own '
                'interpreter and packages: `python3 -m venv .venv`, then '
                '`source .venv/bin/activate`. Everything installed after that '
                'lands in the directory and nowhere else, and deleting the '
                'directory undoes all of it.'
            ),
            'examples': [
                {
                    'label': 'Four ways',
                    'code': ('python3                      the REPL\n'
                             'python3 script.py            a file\n'
                             "python3 -c 'print(1+1)'      a string\n"
                             'python3 -m http.server 8000  an installed module\n'
                             'python3 -m json.tool < f     pretty-print JSON'),
                    'note': '`python3 -m json.tool` is a jq you already have on '
                            'any machine with Python.',
                },
                {
                    'label': 'A venv',
                    'code': ('python3 -m venv .venv\n'
                             'source .venv/bin/activate\n'
                             'pip install requests\n'
                             'deactivate\n'
                             '\n'
                             'rm -rf .venv     undoes everything'),
                    'note': 'One venv per project. They are disposable and cost '
                            'nothing to recreate.',
                },
            ],
            'misconceptions': [
                '`python` may not exist, or may be Python 2 on an old machine. '
                'Say `python3` in anything you will keep.',
                'A venv is not isolation from the system. It is a directory of '
                'packages plus a modified PATH; it does not sandbox anything.',
                '"externally-managed-environment" from pip is not a bug. It is '
                'the distribution telling you to use a venv, and it is right.',
            ],
            'try_it': [
                'Run `python3 -m json.tool` on any JSON file you have. That is '
                'a formatter you did not know you had installed.',
            ],
        },
        {
            'id': 'py-data',
            'title': 'The four types you actually need',
            'next': 'py-control',
            'concept': (
                'Strings, lists, dicts and sets cover nearly everything a '
                'script does. Numbers behave as you expect with one exception '
                'worth knowing now: `/` always produces a float, and `//` is '
                'integer division.\n\n'
                'A **list** is an ordered sequence, indexed from zero, and '
                'slicing `x[1:3]` takes a range. Negative indexes count from the '
                'end, so `x[-1]` is the last item.\n\n'
                'A **dict** maps keys to values, and is the workhorse: '
                '`counts[key] = counts.get(key, 0) + 1` is the Python of '
                '`c[$1]++`. `collections.Counter` does it in one line and is '
                'worth importing.\n\n'
                'A **set** holds unique things and tests membership fast, which '
                'is how you ask "have I seen this before" without a linear '
                'scan.\n\n'
                'The mutability rule that catches everyone: lists, dicts and '
                'sets are **mutable**, so passing one to a function and changing '
                'it changes the caller\'s copy. Strings, numbers and tuples are '
                'not.'
            ),
            'examples': [
                {
                    'label': 'The four',
                    'code': ('s = "hello"        s.upper(), s.split(","),\n'
                             '                   s.strip(), s.startswith("h")\n'
                             'xs = [1, 2, 3]     xs.append(4), xs[-1], xs[1:3]\n'
                             'd = {"a": 1}       d["a"], d.get("b", 0),\n'
                             '                   d.items(), "a" in d\n'
                             'seen = set()       seen.add(x), x in seen'),
                    'note': '`d.get(key, default)` is the one that stops a '
                            'KeyError killing your script on ragged data.',
                },
                {
                    'label': 'Counting, three ways',
                    'code': ('counts = {}\n'
                             'for line in lines:\n'
                             '    k = line.split()[0]\n'
                             '    counts[k] = counts.get(k, 0) + 1\n'
                             '\n'
                             'from collections import Counter\n'
                             'counts = Counter(l.split()[0] for l in lines)\n'
                             'counts.most_common(5)'),
                    'note': 'Counter also gives you the ranking, which is the '
                            'whole `sort -rn | head` in one call.',
                },
            ],
            'misconceptions': [
                '`5 / 2` is `2.5`, not `2`. Use `//` when you want the integer.',
                'A list passed to a function is not copied. Mutating it inside '
                'changes it outside, which is the single most common surprise '
                'coming from shell.',
                '`d[key]` on a missing key raises. `d.get(key)` returns None. '
                'Choosing the wrong one is why scripts die on the one weird '
                'line in the file.',
                'Strings are immutable. `s.upper()` returns a new string and '
                'does not change `s`, which people expect to work like a list '
                'method.',
            ],
            'try_it': [
                'In the REPL, make a list, pass it to a function that appends '
                'to it, and print it afterwards.',
            ],
        },
        {
            'id': 'py-control',
            'title': 'Control flow, truthiness and comprehensions',
            'concept': (
                'Indentation is the block structure, which means there are no '
                'braces and no `end`. Four spaces, consistently. Mixing tabs '
                'and spaces inconsistently inside one block is a TabError '
                'in Python 3, so pick one and let your editor enforce it.\n\n'
                '`if`, `for` and `while` behave as expected. The Python-specific '
                'part is **truthiness**: empty things are false. An empty '
                'string, list, dict or set, plus zero and None, are all falsy, '
                'so `if items:` reads as "if there are any items" and is '
                'idiomatic. You almost never write `if len(items) > 0`.\n\n'
                'A **comprehension** builds a list from a loop in one '
                'expression: `[x.strip() for x in lines if x.strip()]`. Used '
                'for one map and one filter it is clearer than the loop. Two '
                'nested comprehensions with a conditional is a loop that should '
                'have stayed a loop.'
            ),
            'examples': [
                {
                    'label': 'Idiomatic shapes',
                    'code': ('for line in lines:\n'
                             '    if not line.strip():\n'
                             '        continue\n'
                             '    ...\n'
                             '\n'
                             'for i, line in enumerate(lines, 1):\n'
                             '    print(f"{i}: {line}")\n'
                             '\n'
                             'for key, value in d.items():\n'
                             '    ...'),
                    'note': '`enumerate` with a start value is how you number '
                            'lines, and `f"{...}"` is the string formatting to '
                            'use.',
                },
                {
                    'label': 'Comprehensions',
                    'code': ('nums   = [int(x) for x in fields]\n'
                             'errors = [l for l in lines if "ERROR" in l]\n'
                             'lookup = {row[0]: row[1] for row in rows}\n'
                             '\n'
                             'too far:\n'
                             '  [f(y) for x in a for y in x if p(y) and q(x)]'),
                    'note': 'One map or one filter: a comprehension. More than '
                            'that: write the loop.',
                },
            ],
            'misconceptions': [
                'Indentation is not style, it is syntax. An editor set to tabs '
                'in a spaces file will produce errors that look like nothing is '
                'wrong.',
                '`if x:` and `if x is not None:` are different. An empty list '
                'is falsy but is not None, and conflating them is a real bug '
                'when zero or empty is a legitimate value.',
                '`for i in range(len(xs))` is almost always wrong. Iterate the '
                'thing, or use `enumerate` if you need the index.',
            ],
            'try_it': [
                'Rewrite one of your awk one-liners as a Python loop and decide '
                'which you would rather read next year.',
            ],
            'next': 'py-functions',
        },
        {
            'id': 'py-functions',
            'title': 'Functions, and handling what goes wrong',
            'next': 'py-files',
            'concept': (
                'A function is `def name(args):` and an indented body, and the '
                'moment a script does one job more than once it wants to become '
                'one. Arguments can be positional or passed by name, and a '
                'default value makes an argument optional: `def greet(name, '
                'punct="!"):` can be called `greet("Sam")` or `greet("Sam", '
                'punct=".")`. A function hands a value back with `return`, and a '
                'function that never returns hands back `None`, which is a real '
                'value you can accidentally use.\n\n'
                'One trap is worth stating early because it bites everyone: **do '
                'not use a mutable default**. `def f(items=[])` shares one list '
                'across every call, so it fills up over time. Write '
                '`def f(items=None):` and build the list inside. Variables '
                'assigned inside a function are local to it, which is what keeps '
                'functions from stepping on each other.\n\n'
                'Errors in Python are **exceptions**, and the model is to try '
                'the thing and catch the failure rather than check first. '
                '`int("nope")` raises `ValueError`, opening a missing file '
                'raises `FileNotFoundError`, and a `try`/`except` block catches '
                'exactly the type you name. Catch the specific error, not a bare '
                '`except:`, because a bare except also swallows the Ctrl-C you '
                'pressed to stop it and the typo in your own code.\n\n'
                'The full shape is `try` / `except` / `else` / `finally`: the '
                '`else` runs only if nothing was raised, and the `finally` runs '
                'no matter what, which is where cleanup goes. You raise your own '
                'with `raise ValueError("message")` when an argument makes no '
                'sense, and that is how a function refuses bad input instead of '
                'limping on.'
            ),
            'examples': [
                {
                    'label': 'Defining and calling',
                    'code': ('def newest(paths, limit=1):\n'
                             '    ordered = sorted(paths, reverse=True)\n'
                             '    return ordered[:limit]\n'
                             '\n'
                             'newest(files)              # limit defaults to 1\n'
                             'newest(files, limit=3)     # by name\n'
                             '\n'
                             'def f(items=None):         # NOT items=[]\n'
                             '    if items is None:\n'
                             '        items = []'),
                    'note': 'A mutable default is shared across calls, which is '
                            'the single most common Python surprise.',
                },
                {
                    'label': 'try, except, and raising',
                    'code': ('try:\n'
                             '    value = int(text)\n'
                             'except ValueError:\n'
                             '    value = 0            # a sensible default\n'
                             'else:\n'
                             '    log("parsed ok")     # only if no error\n'
                             'finally:\n'
                             '    cleanup()            # always\n'
                             '\n'
                             'if n < 0:\n'
                             '    raise ValueError("n must be non-negative")'),
                    'note': 'Catch the specific type. A bare except also traps '
                            'Ctrl-C and your own typos.',
                },
            ],
            'misconceptions': [
                'A function with no `return` returns `None`, not the last value '
                'it computed. Forgetting the return is why a caller gets None.',
                'A default argument is evaluated once, when the function is '
                'defined, so a mutable default like `[]` or `{}` persists '
                'between calls.',
                'A bare `except:` is almost always a bug. It hides the error '
                'you did not expect, including KeyboardInterrupt and your own '
                'mistakes. Name the exception.',
                'Checking before acting is not the Python style. Try the '
                'operation and catch the failure; it is both faster and less '
                'racy than looking first.',
            ],
            'try_it': [
                'Write a function that divides two numbers and returns 0 on a '
                'ZeroDivisionError, then call it both ways.',
            ],
        },
        {
            'id': 'py-files',
            'title': 'Files, paths and the with-statement',
            'next': 'py-stdlib',
            'concept': (
                'Always open files with `with`. It closes the file however the '
                'block ends, including on an exception, and there is no reason '
                'to write it any other way.\n\n'
                'Iterating a file object gives you one line at a time and does '
                'not load the whole thing into memory, which matters on a log '
                'you did not size first. `f.read()` gives the whole thing as one '
                'string and is fine for small files.\n\n'
                '`pathlib` is the modern way to handle paths, and it removes '
                'most of the string-joining that used to go wrong. '
                '`Path("logs") / "app.log"` builds a path correctly on any '
                'platform, and `p.read_text()`, `p.exists()`, `p.glob("*.log")` '
                'do what they say.'
            ),
            'examples': [
                {
                    'label': 'Reading and writing',
                    'code': ('with open("in.log") as f:\n'
                             '    for line in f:          one at a time\n'
                             '        process(line.rstrip("\\n"))\n'
                             '\n'
                             'with open("out.txt", "w") as f:\n'
                             '    f.write("done\\n")\n'
                             '\n'
                             '"r" read  "w" truncate  "a" append'),
                    'note': 'Lines keep their newline, which is why `rstrip` '
                            'appears in almost every loop like this.',
                },
                {
                    'label': 'pathlib',
                    'code': ('from pathlib import Path\n'
                             '\n'
                             'p = Path("logs") / "app.log"\n'
                             'p.exists()      p.stat().st_size\n'
                             'p.read_text()   p.write_text("x")\n'
                             'Path(".").glob("**/*.log")\n'
                             'p.name  p.stem  p.suffix  p.parent'),
                    'note': '`p.stem` is the filename without its extension, '
                            'which saves a great deal of string surgery.',
                },
            ],
            'misconceptions': [
                'Opening with `"w"` truncates immediately, before you write '
                'anything, which is the same trap as `>` in the shell.',
                'Iterating a file gives lines with their newline attached. '
                'Forgetting to strip is why output has blank lines between '
                'everything.',
                'A file opened without `encoding=` uses the platform default, '
                'which is why a script works on your machine and mangles '
                'characters elsewhere. Say `encoding="utf-8"`.',
            ],
            'try_it': [
                'Write a five-line script that counts non-blank lines in a file '
                'and prints the number.',
            ],
        },
        {
            'id': 'py-stdlib',
            'title': 'The batteries worth knowing',
            'next': 'py-script',
            'concept': (
                'Python ships an enormous standard library and about six '
                'modules cover almost everything a working script does. All of '
                'these are already installed everywhere.\n\n'
                '`json` reads and writes JSON, and `json.loads` on a string '
                'plus `json.load` on a file is the whole interface. `re` is the '
                'regex module you already know the language of. `collections` '
                'gives you `Counter` and `defaultdict`. `pathlib` handles '
                'paths. `subprocess` runs other programs. `argparse` builds a '
                'real command-line interface.\n\n'
                'The one to be careful with is `subprocess`. Use a **list of '
                'arguments**, never a string with `shell=True`, unless you '
                'genuinely need a shell. A list means no quoting, no word '
                'splitting, and no injection through a filename someone else '
                'controls.'
            ),
            'examples': [
                {
                    'label': 'The six',
                    'code': ('import json, re, subprocess\n'
                             'from pathlib import Path\n'
                             'from collections import Counter, defaultdict\n'
                             '\n'
                             'data = json.loads(text)\n'
                             'm = re.search(r"(\\d+)", line)\n'
                             'top = Counter(hosts).most_common(5)\n'
                             'groups = defaultdict(list)'),
                    'note': '`defaultdict(list)` lets you append to a key that '
                            'does not exist yet, which removes a great deal of '
                            'checking.',
                },
                {
                    'label': 'Running other programs',
                    'code': ('r = subprocess.run(["ls", "-l", path],\n'
                             '                   capture_output=True,\n'
                             '                   text=True, timeout=10)\n'
                             'r.returncode   r.stdout   r.stderr\n'
                             '\n'
                             'never:  subprocess.run(f"ls {path}", shell=True)'),
                    'note': 'A list of arguments is safe by construction. The '
                            'string form re-introduces every quoting bug the '
                            'bash module warned about.',
                },
            ],
            'misconceptions': [
                '`json.loads` takes a string and `json.load` takes a file '
                'object. The missing `s` is the most common typo in the '
                'module.',
                '`shell=True` with an interpolated filename is a command '
                'injection, not a convenience.',
                '`subprocess.run` without `timeout` can hang forever if the '
                'child does, which will happen at the worst possible moment.',
            ],
            'try_it': [
                'Write four lines that read a JSON file and print the five most '
                'common values of one key.',
            ],
        },
        {
            'id': 'py-script',
            'title': 'A script someone else can run',
            'concept': (
                'Four habits turn a working file into a tool, and they mirror '
                'the bash module exactly.\n\n'
                'A **shebang** and `chmod +x`. An **argparse** interface rather '
                'than reading `sys.argv` by hand, because argparse gives you '
                '`--help`, type checking and error messages for free. An '
                '**exit code**, because a script that always exits zero cannot '
                'be used in `&&`. And the `if __name__ == "__main__":` guard, '
                'which lets the file be imported without running.\n\n'
                'That last one looks like ceremony and is not: without it, '
                'importing your script to reuse one function runs the whole '
                'thing, which is surprising exactly once and then never '
                'forgotten.'
            ),
            'examples': [
                {
                    'label': 'The skeleton',
                    'code': ('#!/usr/bin/env python3\n'
                             '"""One line saying what this does."""\n'
                             'import argparse, sys\n'
                             '\n'
                             'def main() -> int:\n'
                             '    p = argparse.ArgumentParser()\n'
                             '    p.add_argument("path")\n'
                             '    p.add_argument("-n", type=int, default=10)\n'
                             '    args = p.parse_args()\n'
                             '    ...\n'
                             '    return 0\n'
                             '\n'
                             'if __name__ == "__main__":\n'
                             '    sys.exit(main())'),
                    'note': 'Returning from main and passing it to sys.exit is '
                            'how the exit code gets set without scattering '
                            'exits through the code.',
                },
            ],
            'misconceptions': [
                'Reading `sys.argv` by hand costs you `--help` and every error '
                'message. argparse is four lines and gives all of it.',
                'An uncaught exception exits with code 1 and prints a '
                'traceback, which is often the right behaviour and occasionally '
                'not what you want a user to see.',
                'Without the `__main__` guard, importing the file to test one '
                'function runs the entire script.',
            ],
            'try_it': [
                'Take the counting script from the previous lesson and give it '
                'an argparse interface with a `--top N` flag.',
            ],
        },
    ],

    'drills': [
        {'id': 'py-cmd-repl', 'type': 'command', 'answer': 'python3',
         'prompt': 'Start an interactive Python session.',
         'teach': 'On current distributions plain python is either missing or '
                  'Python 2, so anything you write down should say python3.'},
        {'id': 'py-cmd-c', 'type': 'command', 'answer': "python3 -c 'print(1+1)'",
         'prompt': 'Run a one-line Python program from the shell.',
         'teach': 'Single quotes keep the shell out of it. This is how you '
                  'use Python as a calculator or a one-off filter without '
                  'writing a file.'},
        {'id': 'py-cmd-m', 'type': 'command', 'answer': 'python3 -m http.server 8000',
         'prompt': 'Serve the current directory over HTTP on port 8000, using '
                   'only the standard library.',
         'teach': '-m runs a module as a script. This is the fastest way to '
                  'move a file off a machine that has Python and nothing '
                  'else.'},
        {'id': 'py-cmd-jsontool', 'type': 'command', 'answer': 'python3 -m json.tool',
         'prompt': 'Pretty-print JSON using a formatter that is already on any '
                   'machine with Python.',
         'teach': 'Worth remembering for a machine where jq is not installed '
                  'and you are not allowed to install it.'},
        {'id': 'py-cmd-venv', 'type': 'command', 'answer': 'python3 -m venv .venv',
         'prompt': 'Create a virtual environment in the current directory.',
         'teach': 'venv is in the standard library, so there is nothing to '
                  'install first. The directory name is a convention, not a '
                  'requirement.'},
        {'id': 'py-cmd-activate', 'type': 'command', 'answer': 'source .venv/bin/activate',
         'prompt': 'Activate a virtual environment in bash.',
         'teach': 'Activating only edits PATH in the current shell. Running '
                  '.venv/bin/python directly works without activating '
                  'anything.'},
        {'id': 'py-cmd-shebang', 'type': 'command', 'answer': '#!/usr/bin/env python3',
         'prompt': 'Write the first line of a Python script so it finds the interpreter wherever it lives.',
         'teach': 'A hardcoded path breaks the moment the script meets a '
                  'virtual environment, which is the whole reason env exists.'},
        {'id': 'py-cmd-guard', 'type': 'command',
         'answer': 'if __name__ == "__main__":',
         'prompt': 'Write the guard that lets a script be imported without running.',
         'teach': 'Without it, importing the file to reuse one function runs '
                  'the entire script. Writing a test is how most people '
                  'discover this.'},
        {'id': 'py-cmd-open', 'type': 'command',
         'answer': 'with open("in.log", encoding="utf-8") as f:',
         'prompt': 'Open a file for reading so it closes however the block ends, whatever the platform encoding.',
         'teach': 'with closes the file on an exception too. Naming the '
                  "encoding matters because the default follows the machine's "
                  'locale, so the same script reads differently elsewhere.'},
        {'id': 'py-cmd-get', 'type': 'command', 'answer': 'd.get(key, 0)',
         'prompt': 'Read a dict key that may not exist, with a default, without '
                   'raising.',
         'teach': 'Subscript syntax raises KeyError on a missing key. get '
                  'returns the default instead, and None if you do not give '
                  'one.'},
        {'id': 'py-cmd-counter', 'type': 'command',
         'answer': 'Counter(items).most_common(5)',
         'prompt': 'Count occurrences and take the five most frequent, in one '
                   'expression.',
         'teach': 'The whole of sort | uniq -c | sort -rn | head, in one call.'},
        {'id': 'py-cmd-defaultdict', 'type': 'command',
         'answer': 'groups = defaultdict(list)',
         'prompt': 'Make a dict you can append to without checking whether the '
                   'key exists yet.',
         'teach': 'The factory is called for a missing key, so appending '
                  'works the first time. Merely reading a missing key creates '
                  'it, which catches people out.'},
        {'id': 'py-cmd-enumerate', 'type': 'command',
         'answer': 'for i, line in enumerate(lines, 1):',
         'prompt': 'Loop over lines with a line number starting at one.',
         'teach': 'The second argument is the start value. Line numbers are '
                  'one-based and almost nothing else in Python is.'},
        {'id': 'py-cmd-comprehension', 'type': 'command',
         'answer': '[l for l in lines if "ERROR" in l]',
         'prompt': 'Build a list of the lines containing ERROR, in one '
                   'expression.',
         'teach': 'It reads as a filter and builds the whole list in memory. '
                  'Swap the brackets for parentheses to get a generator '
                  'instead.'},
        {'id': 'py-cmd-fstring', 'type': 'command', 'answer': 'print(f"{i}: {line}")',
         'prompt': 'Print a number and a line together using modern string '
                   'formatting.',
         'teach': 'The braces hold real expressions, and an equals sign '
                  'inside them prints the name and the value together, which '
                  'is a fast substitute for a debugger.'},
        {'id': 'py-cmd-json-loads', 'type': 'command', 'answer': 'json.loads(text)',
         'prompt': 'Parse JSON held in a string.',
         'teach': 'json.loads takes a string, json.load takes a file object. '
                  'The missing s is the most common typo in the module.'},
        {'id': 'py-cmd-json-dump', 'type': 'command',
         'answer': 'json.dump(data, f, indent=2)',
         'prompt': 'Write a data structure to an open file as readable JSON.',
         'teach': 'dump writes to a file and dumps returns a string. Missing '
                  'that s is the most common mistake in the whole module.'},
        {'id': 'py-cmd-pathlib', 'type': 'command', 'answer': 'Path("logs") / "app.log"',
         'prompt': 'Build a path from two parts, correctly, without string '
                   'concatenation.',
         'teach': 'The slash operator is overloaded on Path and gets the '
                  'separator right on every platform. It also avoids the '
                  'doubled slash that string joining produces.'},
        {'id': 'py-cmd-glob', 'type': 'command', 'answer': 'Path(".").glob("**/*.log")',
         'prompt': 'Find every .log file recursively, using pathlib.',
         'teach': 'The double star matches across directories, and glob '
                  'returns a generator, so it starts producing results before '
                  'it has walked everything.'},
        {'id': 'py-cmd-subprocess', 'type': 'command',
         'answer': 'subprocess.run(["ls", "-l"], capture_output=True, text=True)',
         'prompt': 'Run another program safely and capture its output as text.',
         'teach': 'A list of arguments is safe by construction. The string form '
                  'with shell=True reintroduces every quoting bug.'},
        {'id': 'py-cmd-argparse', 'type': 'command',
         'answer': 'p = argparse.ArgumentParser()',
         'prompt': 'Start building a real command-line interface rather than '
                   'reading sys.argv by hand.',
         'teach': 'It gives you --help, type checking and error messages for '
                  'free. The moment a script takes two arguments this is '
                  'cheaper than parsing them yourself.'},
        {'id': 'py-cmd-exit', 'type': 'command', 'answer': 'sys.exit(main())',
         'prompt': 'Run main and use its return value as the process exit code.',
         'teach': 'Returning an int from main and passing it here is how a '
                  'script gets a real exit code, which is what makes it '
                  'usable in a shell if.'},
        {'id': 'py-cmd-intdiv', 'type': 'command', 'answer': 'total // count',
         'prompt': 'Divide two integers and get an integer back.',
         'teach': 'A single slash always produces a float in Python 3.'},

        # functions and exceptions
        {'id': 'py-cmd-def', 'type': 'command',
         'answer': 'def double(n): return n * 2',
         'prompt': 'Define a one-line function double that returns its '
                   'argument times two.',
         'teach': 'A function with no return hands back None, which a caller '
                  'can accidentally use.'},
        {'id': 'py-cmd-default', 'type': 'command',
         'answer': 'def greet(name, punct="!"): return name + punct',
         'prompt': 'Define greet(name, punct) where punct defaults to "!", '
                   'returning the two joined.',
         'teach': 'A default makes an argument optional. Never default it to a '
                  'mutable like [] or {}: that one list is shared across '
                  'calls.'},
        {'id': 'py-cmd-except', 'type': 'command',
         'answer': 'except FileNotFoundError as e:',
         'prompt': 'Write the except clause that catches a missing-file error '
                   'and binds it to e.',
         'teach': 'Catch the specific type, not a bare except, which also '
                  'swallows Ctrl-C and your own typos.'},
        {'id': 'py-cmd-raise', 'type': 'command',
         'answer': 'raise ValueError("n must be non-negative")',
         'prompt': 'Raise a ValueError complaining that n must be '
                   'non-negative.',
         'teach': 'Raising is how a function refuses bad input rather than '
                  'limping on with it.'},
    ],

    'challenges': [
        {
            'id': 'py-count-script',
            'title': 'Count and rank, in Python',
            'goal': 'Write the script that does what your awk one-liner did, and '
                    'decide afterwards which you prefer.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'access.log': ('10.0.0.1 GET\n10.0.0.2 GET\n10.0.0.1 POST\n'
                               '10.0.0.3 GET\n10.0.0.1 GET\n10.0.0.2 POST\n'),
            }},
            'solution': {'shell': (
                "cat > rank.py <<'EOF'\n"
                "#!/usr/bin/env python3\n"
                "from collections import Counter\n"
                "from pathlib import Path\n"
                "lines = Path('access.log').read_text(encoding='utf-8').splitlines()\n"
                "counts = Counter(l.split()[0] for l in lines if l.strip())\n"
                "with open('ranked.txt', 'w', encoding='utf-8') as f:\n"
                "    for host, n in counts.most_common():\n"
                "        f.write(f'{n} {host}\\n')\n"
                "EOF\n"
                "python3 rank.py")},
            'steps': [
                {'instruction': 'Write rank.py that reads access.log.',
                 'hint': 'Path("access.log").read_text().splitlines()'},
                {'instruction': 'Count the first field of each line.',
                 'hint': 'Counter(l.split()[0] for l in lines if l.strip())'},
                {'instruction': 'Write "count host" per line to ranked.txt, most '
                                'frequent first.',
                 'hint': 'counts.most_common() is already sorted'},
                {'instruction': 'Run it.', 'hint': 'python3 rank.py'},
            ],
            'free': 'Write and run rank.py so that ranked.txt contains each '
                    'client and its count, most frequent first.',
            'verify': {'kind': 'sandbox', 'expect': {
                'exists': ['rank.py', 'ranked.txt'],
                'file_contains': {'ranked.txt': ['3 10.0.0.1', '2 10.0.0.2',
                                                 '1 10.0.0.3']}}},
            'fallback': 'self',
        },
        {
            'id': 'py-json-summary',
            'title': 'Reshape JSON with the standard library',
            'goal': 'Do the jq challenge in Python, which is the right call the '
                    'moment the logic grows a second condition.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'events.json': ('[{"client":"10.0.0.1","status":200,"size":512},'
                                '{"client":"10.0.0.2","status":404,"size":128},'
                                '{"client":"10.0.0.3","status":500,"size":2048}]'),
            }},
            'solution': {'shell': (
                "cat > summarise.py <<'EOF'\n"
                "#!/usr/bin/env python3\n"
                "import json\n"
                "from pathlib import Path\n"
                "events = json.loads(Path('events.json').read_text(encoding='utf-8'))\n"
                "bad = [{'host': e['client'], 'code': e['status']}\n"
                "       for e in events if e['status'] >= 400]\n"
                "with open('failures.json', 'w', encoding='utf-8') as f:\n"
                "    json.dump(bad, f, indent=2)\n"
                "EOF\n"
                "python3 summarise.py")},
            'steps': [
                {'instruction': 'Read and parse events.json.',
                 'hint': 'json.loads(Path("events.json").read_text())'},
                {'instruction': 'Keep the events with status 400 or more, '
                                'reshaped to host and code.',
                 'hint': 'a comprehension with a condition'},
                {'instruction': 'Write them to failures.json as readable JSON.',
                 'hint': 'json.dump(bad, f, indent=2)'},
            ],
            'free': 'Write and run summarise.py so failures.json holds a JSON '
                    'array of {host, code} for every event with status 400 or '
                    'more.',
            'verify': {'kind': 'sandbox', 'expect': {
                'exists': ['summarise.py', 'failures.json'],
                'file_contains': {'failures.json': ['host', 'code', '404',
                                                    '500', '10.0.0.2']},
                'file_lacks': {'failures.json': ['10.0.0.1', 'size']}}},
            'fallback': 'self',
        },
        {
            'id': 'py-cli',
            'title': 'A script with a real interface',
            'goal': 'Give a script argparse, an exit code and the main guard, '
                    'so someone else can run it.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'words.txt': 'alpha\nbravo\ncharlie\ndelta\necho\n',
            }},
            'solution': {'shell': (
                "cat > head.py <<'EOF'\n"
                "#!/usr/bin/env python3\n"
                '"""Print the first N lines of a file."""\n'
                "import argparse, sys\n"
                "from pathlib import Path\n"
                "\n"
                "def main() -> int:\n"
                "    p = argparse.ArgumentParser()\n"
                "    p.add_argument('path')\n"
                "    p.add_argument('-n', type=int, default=10)\n"
                "    args = p.parse_args()\n"
                "    lines = Path(args.path).read_text(encoding='utf-8').splitlines()\n"
                "    Path('out.txt').write_text('\\n'.join(lines[:args.n]) + '\\n',\n"
                "                               encoding='utf-8')\n"
                "    return 0\n"
                "\n"
                "if __name__ == '__main__':\n"
                "    sys.exit(main())\n"
                "EOF\n"
                "chmod +x head.py && python3 head.py words.txt -n 3")},
            'steps': [
                {'instruction': 'Write head.py with a shebang and the main '
                                'guard.', 'hint': 'if __name__ == "__main__":'},
                {'instruction': 'Give it an argparse interface taking a path and '
                                'an -n option defaulting to 10.'},
                {'instruction': 'Have it write the first n lines to out.txt.'},
                {'instruction': 'Make it executable and run it with -n 3.',
                 'hint': 'chmod +x head.py && python3 head.py words.txt -n 3'},
            ],
            'free': 'Write an executable head.py with argparse, the main guard '
                    'and an exit code, then run it so out.txt holds the first '
                    'three words.',
            'verify': {'kind': 'sandbox', 'expect': {
                'executable': ['head.py'],
                'file_contains': {'head.py': ['argparse', '__main__',
                                              'sys.exit']},
                'file_equals': {'out.txt': 'alpha\nbravo\ncharlie'}}},
            'fallback': 'self',
        },
        {
            'id': 'py-comprehensions',
            'title': 'Write the loop as an expression',
            'goal': 'List, dict and set comprehensions, and the moment one '
                    'stops being clearer than the loop it replaces.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'words.txt': 'alpha\nbravo\ncharlie\ndelta\necho\nalpha\n',
            }},
            'solution': {'shell':
                'cat > comp.py <<\'EOF\'\n'
                'words = [w.strip() for w in open("words.txt")]\n'
                'long_words = [w for w in words if len(w) > 4]\n'
                'lengths = {w: len(w) for w in words}\n'
                'initials = {w[0] for w in words}\n'
                'with open("out.txt", "w") as f:\n'
                '    f.write("long: " + ",".join(long_words) + "\\n")\n'
                '    f.write("count: %d\\n" % len(lengths))\n'
                '    f.write("initials: " + ",".join(sorted(initials)) + "\\n")\n'
                'EOF\n'
                'python3 comp.py'},
            'steps': [
                {'instruction': 'Read words.txt into a list, stripping each '
                                'line, with a list comprehension.',
                 'hint': '[w.strip() for w in open("words.txt")]'},
                {'instruction': 'Build a filtered list of words longer than '
                                'four characters.',
                 'hint': '[w for w in words if len(w) > 4]'},
                {'instruction': 'Build a dict of word to length, and a set of '
                                'first letters. Note that both collapse '
                                'duplicates differently.',
                 'hint': '{w: len(w) for w in words} and {w[0] for w in words}'},
                {'instruction': 'Write all three results to out.txt.'},
            ],
            'free': 'Produce comp.py using a list, a dict and a set '
                    'comprehension, and out.txt reporting the long words, the '
                    'number of distinct words, and the distinct initials.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'comp.py': ['for w in', 'if len(w)'],
                                  'out.txt': ['long: alpha,bravo,charlie,delta',
                                              'count: 5',
                                              'initials: a,b,c,d,e']}}},
            'fallback': 'self',
        },
        {
            'id': 'py-errors',
            'title': 'Handle the error you expected, not all of them',
            'goal': 'try, except with a named exception, else and finally, '
                    'and why a bare except is the wrong habit.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'nums.txt': '10\n20\nnot-a-number\n30\n',
            }},
            'solution': {'shell':
                'cat > safe.py <<\'EOF\'\n'
                'total = 0\n'
                'bad = []\n'
                'for line in open("nums.txt"):\n'
                '    line = line.strip()\n'
                '    try:\n'
                '        value = int(line)\n'
                '    except ValueError:\n'
                '        bad.append(line)\n'
                '    else:\n'
                '        total += value\n'
                'try:\n'
                '    missing = open("nope.txt")\n'
                'except FileNotFoundError as e:\n'
                '    note = "FileNotFoundError: %s" % e.filename\n'
                'finally:\n'
                '    pass\n'
                'with open("result.txt", "w") as f:\n'
                '    f.write("total: %d\\n" % total)\n'
                '    f.write("skipped: %s\\n" % ",".join(bad))\n'
                '    f.write(note + "\\n")\n'
                'EOF\n'
                'python3 safe.py'},
            'steps': [
                {'instruction': 'Sum the numbers in nums.txt, catching only '
                                'ValueError for the line that is not a '
                                'number.',
                 'hint': 'except ValueError:'},
                {'instruction': 'Use an else block for the case where no '
                                'exception was raised, so the add only '
                                'happens on success.'},
                {'instruction': 'Separately, try to open a file that does not '
                                'exist and catch FileNotFoundError, keeping '
                                'the filename from the exception object.',
                 'hint': 'except FileNotFoundError as e: e.filename'},
                {'instruction': 'Write the total, the skipped lines and the '
                                'error note to result.txt.'},
            ],
            'free': 'Produce safe.py catching ValueError and '
                    'FileNotFoundError by name, and result.txt holding the '
                    'total, the skipped line and the error note.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'safe.py': ['except ValueError',
                                              'except FileNotFoundError'],
                                  'result.txt': ['total: 60',
                                                 'skipped: not-a-number',
                                                 'FileNotFoundError']},
                'file_lacks': {'safe.py': 'except:'}}},
            'fallback': 'self',
        },
        {
            'id': 'py-pathlib',
            'title': 'Work with paths as objects',
            'goal': 'pathlib replaces most of os.path and all of the string '
                    'concatenation people still write.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'tree/a.txt': 'one\n',
                'tree/b.log': 'two\n',
                'tree/sub/c.txt': 'three\n',
            }},
            'solution': {'shell':
                'cat > paths.py <<\'EOF\'\n'
                'from pathlib import Path\n'
                'root = Path("tree")\n'
                'txt = sorted(p.as_posix() for p in root.rglob("*.txt"))\n'
                'sizes = {p.name: p.stat().st_size for p in root.rglob("*") '
                'if p.is_file()}\n'
                'Path("found.txt").write_text("\\n".join(txt) + "\\n")\n'
                'Path("sizes.txt").write_text(\n'
                '    "\\n".join("%s %d" % (k, sizes[k]) for k in sorted(sizes))\n'
                '    + "\\n")\n'
                'Path("out").mkdir(exist_ok=True)\n'
                'Path("out/copy.txt").write_text(Path("tree/a.txt").read_text())\n'
                'EOF\n'
                'python3 paths.py'},
            'steps': [
                {'instruction': 'Use Path and rglob to find every .txt file '
                                'under tree, and write their posix paths to '
                                'found.txt, sorted.',
                 'hint': 'Path("tree").rglob("*.txt")'},
                {'instruction': 'Build a mapping of filename to size for '
                                'every regular file, and write it to '
                                'sizes.txt.',
                 'hint': 'p.stat().st_size, guarded by p.is_file()'},
                {'instruction': 'Make an out directory that does not fail if '
                                'it already exists, and copy a file into it '
                                'with read_text and write_text.',
                 'hint': 'Path("out").mkdir(exist_ok=True)'},
            ],
            'free': 'Produce paths.py using pathlib, found.txt listing the '
                    'txt files under tree, sizes.txt with each filename and '
                    'size, and out/copy.txt.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'paths.py': ['pathlib', 'rglob'],
                                  'found.txt': ['tree/a.txt', 'tree/sub/c.txt'],
                                  'sizes.txt': 'b.log'},
                'file_equals': {'out/copy.txt': 'one'},
                'file_lacks': {'found.txt': 'b.log'}}},
            'fallback': 'self',
        },
        {
            'id': 'py-csv-module',
            'title': 'Use the csv module rather than split on comma',
            'goal': 'The reason the module exists is one quoted field with a '
                    'comma in it, and this challenge contains exactly that.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'people.csv': 'name,role,note\n'
                              'alice,engineer,"likes tea, strongly"\n'
                              'bob,analyst,plain\n'
                              'carol,engineer,"reports to alice, mostly"\n',
            }},
            'solution': {'shell':
                'cat > readcsv.py <<\'EOF\'\n'
                'import csv\n'
                'rows = list(csv.DictReader(open("people.csv", newline="")))\n'
                'engineers = [r for r in rows if r["role"] == "engineer"]\n'
                'with open("engineers.csv", "w", newline="") as f:\n'
                '    w = csv.DictWriter(f, fieldnames=["name", "note"])\n'
                '    w.writeheader()\n'
                '    for r in engineers:\n'
                '        w.writerow({"name": r["name"], "note": r["note"]})\n'
                'naive = open("people.csv").readlines()[1].split(",")\n'
                'with open("why.txt", "w") as f:\n'
                '    f.write("naive fields: %d\\n" % len(naive))\n'
                '    f.write("csv fields: %d\\n" % len(rows[0]))\n'
                'EOF\n'
                'python3 readcsv.py'},
            'steps': [
                {'instruction': 'Read people.csv with csv.DictReader and keep '
                                'the engineers.',
                 'hint': 'csv.DictReader(open("people.csv", newline=""))'},
                {'instruction': 'Write their name and note to engineers.csv '
                                'with DictWriter, including a header row.',
                 'hint': 'csv.DictWriter(f, fieldnames=["name", "note"])'},
                {'instruction': 'Now split the same data line naively on '
                                'commas and record both field counts in '
                                'why.txt. They will differ, and that is the '
                                'whole argument for the module.'},
            ],
            'free': 'Produce engineers.csv containing only the engineers with '
                    'their notes intact, and why.txt comparing the field '
                    'count from a naive split against the csv module.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'readcsv.py': ['import csv', 'DictReader'],
                                  'engineers.csv': ['alice', 'carol',
                                                    'likes tea, strongly'],
                                  'why.txt': ['naive fields: 4',
                                              'csv fields: 3']},
                'file_lacks': {'engineers.csv': 'bob'}}},
            'fallback': 'self',
        },
        {
            'id': 'py-modules',
            'title': 'Split it into two files and import one',
            'goal': 'The import machinery, the name equals main guard, and '
                    'why a module runs its top level code exactly once.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {'.keep': ''}},
            'solution': {'shell':
                'cat > helpers.py <<\'EOF\'\n'
                'LOADED = "helpers imported"\n'
                '\n'
                '\n'
                'def shout(text):\n'
                '    return text.upper() + "!"\n'
                '\n'
                '\n'
                'if __name__ == "__main__":\n'
                '    print("helpers run directly")\n'
                'EOF\n'
                'cat > main.py <<\'EOF\'\n'
                'import helpers\n'
                'from helpers import shout\n'
                '\n'
                'with open("out.txt", "w") as f:\n'
                '    f.write(shout("hello") + "\\n")\n'
                '    f.write(helpers.LOADED + "\\n")\n'
                '    f.write("name in main: %s\\n" % __name__)\n'
                'EOF\n'
                'python3 main.py && python3 helpers.py > direct.txt'},
            'steps': [
                {'instruction': 'Write helpers.py with a constant, a function '
                                'shout that uppercases and appends an '
                                'exclamation mark, and a main guard that '
                                'prints something.',
                 'hint': 'if __name__ == "__main__":'},
                {'instruction': 'Write main.py that imports helpers both ways '
                                'and writes three lines to out.txt: the '
                                'shouted text, the constant, and its own '
                                '__name__.'},
                {'instruction': 'Run main.py, then run helpers.py directly '
                                'into direct.txt, and compare what the guard '
                                'did in each case.'},
            ],
            'free': 'Produce helpers.py and main.py, out.txt showing the '
                    'imported function and constant plus __main__, and '
                    'direct.txt showing what the guard prints when run '
                    'directly.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'helpers.py': '__name__',
                                  'out.txt': ['HELLO!', 'helpers imported',
                                              'name in main: __main__'],
                                  'direct.txt': 'helpers run directly'}}},
            'fallback': 'self',
        },
        {
            'id': 'py-subprocess',
            'title': 'Run a command without a shell',
            'goal': 'subprocess.run with a list, capture_output, check, and '
                    'the reason shell equals True is the wrong default.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'data.txt': 'gamma\nalpha\nbeta\nalpha\n',
                'weird name.txt': 'has a space in the name\n',
            }},
            'solution': {'shell':
                'cat > runner.py <<\'EOF\'\n'
                'import subprocess\n'
                'r = subprocess.run(["sort", "-u", "data.txt"],\n'
                '                   capture_output=True, text=True, check=True)\n'
                'open("sorted.txt", "w").write(r.stdout)\n'
                'open("rc.txt", "w").write("returncode: %d\\n" % r.returncode)\n'
                'w = subprocess.run(["wc", "-l", "weird name.txt"],\n'
                '                   capture_output=True, text=True)\n'
                'open("spaced.txt", "w").write(w.stdout)\n'
                'try:\n'
                '    subprocess.run(["false"], check=True)\n'
                'except subprocess.CalledProcessError as e:\n'
                '    open("failed.txt", "w").write("raised: %d\\n" '
                '% e.returncode)\n'
                'EOF\n'
                'python3 runner.py'},
            'steps': [
                {'instruction': 'Run sort -u over data.txt with a list of '
                                'arguments, capturing the output, and write '
                                'it to sorted.txt.',
                 'hint': 'subprocess.run(["sort", "-u", "data.txt"], '
                         'capture_output=True, text=True)'},
                {'instruction': 'Record the return code in rc.txt.'},
                {'instruction': 'Run wc -l on the file whose name has a space '
                                'in it. With a list there is nothing to '
                                'quote, which is the whole point.',
                 'hint': '["wc", "-l", "weird name.txt"]'},
                {'instruction': 'Run something that fails with check=True and '
                                'catch CalledProcessError, writing its return '
                                'code to failed.txt.'},
            ],
            'free': 'Produce runner.py using subprocess with argument lists, '
                    'and sorted.txt, rc.txt, spaced.txt and failed.txt as its '
                    'output.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'runner.py': ['subprocess.run',
                                                'capture_output'],
                                  'sorted.txt': ['alpha', 'beta', 'gamma'],
                                  'rc.txt': 'returncode: 0',
                                  'spaced.txt': 'weird name.txt',
                                  'failed.txt': 'raised: 1'},
                'file_lacks': {'runner.py': 'shell=True'}}},
            'fallback': 'self',
        },
    ],

    'quiz': [
        {'id': 'pyq-when', 'type': 'mcq',
         'prompt': 'Which of these is the clearest sign a pipeline should '
                   'become a Python script?',
         'answer': 'You need to hold state across records while branching more '
                   'than once.',
         'distractors': ['It is longer than eighty characters.',
                         'It uses more than two commands.',
                         'It processes more than a million lines.'],
         'teach': 'A short clear pipeline is better engineering than a thirty '
                  'line script that does the same thing.'},

        {'id': 'pyq-div', 'type': 'mcq',
         'prompt': 'What does `5 / 2` evaluate to?',
         'answer': '2.5',
         'distractors': ['2', '2.0', 'A TypeError'],
         'teach': 'A single slash always produces a float in Python 3. Use // '
                  'for integer division.'},

        {'id': 'pyq-mutable', 'type': 'mcq',
         'prompt': 'You pass a list to a function and the function appends to '
                   'it. What does the caller see?',
         'answer': 'The appended item; lists are mutable and not copied.',
         'distractors': ['The original list, unchanged.',
                         'An error, since arguments are read only.',
                         'It depends on whether the function returns it.'],
         'teach': 'The single most common surprise coming from shell, where '
                  'everything is a string being passed around.'},

        {'id': 'pyq-get', 'type': 'mcq',
         'prompt': 'What is the difference between `d[k]` and `d.get(k)` on a '
                   'missing key?',
         'answer': 'The first raises KeyError; the second returns None.',
         'distractors': ['They are the same.',
                         'The first returns None; the second raises.',
                         'The second creates the key.'],
         'teach': 'Choosing wrong is why a script dies on the one weird line in '
                  'the file.'},

        {'id': 'pyq-truthy', 'type': 'mcq',
         'prompt': 'Which of these is falsy in Python?',
         'answer': 'An empty list.',
         'distractors': ['The string "0".', 'The list [0].',
                         'The string "False".'],
         'teach': 'Empty things are false, which is why `if items:` reads as '
                  '"if there are any". A non-empty string is always truthy.'},

        {'id': 'pyq-strings', 'type': 'mcq',
         'prompt': 'You call `s.upper()`. What happens to `s`?',
         'answer': 'Nothing; strings are immutable and a new one is returned.',
         'distractors': ['It is converted in place.',
                         'It raises, since strings have no methods.',
                         'It depends on whether s was a literal.'],
         'teach': 'People expect it to behave like a list method, which mutates '
                  'in place.'},

        {'id': 'pyq-shell-true', 'type': 'mcq',
         'prompt': 'Why avoid `subprocess.run(f"ls {path}", shell=True)`?',
         'answer': 'A path containing shell metacharacters becomes command '
                   'injection.',
         'distractors': ['It is slower than the list form.',
                         'shell=True is deprecated.',
                         'It cannot capture output.'],
         'teach': 'The list form is safe by construction: no quoting, no word '
                  'splitting, nothing to inject through.'},

        {'id': 'pyq-open-w', 'type': 'mcq',
         'prompt': 'When does `open("f", "w")` truncate the file?',
         'answer': 'Immediately, before you write anything.',
         'distractors': ['When you first call write.',
                         'When the with block exits.',
                         'Only if the file already had content.'],
         'teach': 'The same trap as `>` in the shell, which is why `sort f > f` '
                  'empties the file.'},

        {'id': 'pyq-main-guard', 'type': 'mcq',
         'prompt': 'What does `if __name__ == "__main__":` prevent?',
         'answer': 'The script running when the file is imported.',
         'distractors': ['The script running twice.',
                         'Name collisions with the standard library.',
                         'Errors when there are no arguments.'],
         'teach': 'Surprising exactly once: you import your script to reuse one '
                  'function and the whole thing executes.'},

        {'id': 'pyq-loads', 'type': 'mcq',
         'prompt': 'You have JSON in a string. Which function parses it?',
         'answer': 'json.loads',
         'distractors': ['json.load', 'json.parse', 'json.decode'],
         'teach': 'loads takes a string, load takes a file object. The missing '
                  's is the most common typo in the module.'},
    ],
}
