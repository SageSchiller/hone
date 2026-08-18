"""LaTeX: a markup language that compiles into a document.

A .tex file is a recipe, not a finished page. You write structure and meaning;
pdflatex (or another engine) turns that into a PDF. That split is why a
formula stays a formula after you change the margins, and why a missing brace
is an error instead of a crooked paragraph.

Sandbox-verified by reading the source the student writes. Compiling to a PDF
is honestly self-marked: the trainer can check the .tex file, not the look of
a page, and D1 forbids shipping a TeX tree. pdflatex is the engine this module
names; if it is missing the walkthrough still stands and practice degrades.

linux is the prerequisite: a shell, a file, and a command that writes another
file.
"""

MODULE = {
    'id': 'latex',
    'title': 'LaTeX',
    'group': 'Text processing',
    'blurb': 'A first document, math, floats, packages, and reading the log.',
    'context': 'You are at a shell with a .tex file, about to compile it.',
    'needs': ('pdflatex',),
    'prereqs': ['linux'],
    'adapter': 'sandbox',
    'estimate': '4-5 hours',
    'order': 34,

    'lessons': [
        {
            'id': 'tx-what',
            'title': 'What LaTeX is, and what it is not',
            'next': 'tx-first',
            'concept': (
                'A word processor is a finished page you poke at. LaTeX is a '
                'markup language: you describe the document, and a compiler '
                'lays it out. The file you edit is a `.tex` source. The file '
                'you read is a PDF the compiler wrote.\n\n'
                'That split is the whole reason to learn it. Change the paper '
                'size and every page reflows. Number a new section and every '
                'cross-reference updates. Write a fraction once and it stays '
                'a fraction after you change the font. A word processor will '
                'do those things, and it will do them by hand, badly, the '
                'third time the margins move.\n\n'
                '**What it is good at.** Papers, notes with real mathematics, '
                'a CV that must look the same on every machine, anything '
                'where the structure matters more than dragging a box. '
                'Journals and many universities still ask for a `.tex` file, '
                'not a `.docx`.\n\n'
                '**What it is not.** It is not a way to paint a poster. It is '
                'not Markdown with extra backslashes, though Markdown is the '
                'closer cousin: both are source you compile. It is not WYSIWYG. '
                'The first hour feels like programming because it is: a missing '
                'brace is an error, not a crooked paragraph.\n\n'
                'A first session fails in a boring way: the source looks '
                'right in the editor and the PDF is last week\'s build, '
                'because nobody ran the compiler after the edit. The habit '
                'is edit, compile, look at the PDF, in that order, every '
                'time.\n\n'
                'The next lesson is the smallest file that compiles, and the '
                'command that turns it into a PDF.'
            ),
            'examples': [
                {
                    'label': 'Two files, two jobs',
                    'code': ('notes.tex     what you edit\n'
                             'notes.pdf     what you read\n'
                             '\n'
                             'pdflatex notes.tex\n'
                             '  writes notes.pdf, and some helper files'),
                    'note': 'You never send the helper files. The .tex is the '
                            'source. The PDF is the product.',
                },
                {
                    'label': 'A sentence of markup',
                    'code': ('The energy is $E = mc^{2}$.\n'
                             '\n'
                             'source: letters, plus a formula in dollars\n'
                             'PDF:    the same sentence, the formula set'),
                    'note': 'The dollars are not decoration. They switch into '
                            'math mode, which is a later lesson and the reason '
                            'most people stay.',
                },
            ],
            'misconceptions': [
                'LaTeX is not a word processor with a funny save format. The '
                'source is the document; the PDF is a build product.',
                'You do not need to learn every package on day one. A first '
                'paper is a class, some sections, and some math.',
            ],
            'try_it': [
                'Open any PDF you have and imagine the source: headings, '
                'paragraphs, a formula. That inventory is the rest of this '
                'module.',
            ],
        },
        {
            'id': 'tx-first',
            'title': 'A first document, and how it becomes a PDF',
            'next': 'tx-structure',
            'concept': (
                '`\\documentclass` and `pdflatex` are how a `.tex` file '
                'becomes a PDF. That is why the four-line skeleton is the '
                'first thing to type.\n\n'
                'Three lines wrap everything. `\\documentclass{article}` picks '
                'the kind of document. `\\begin{document}` starts the body. '
                '`\\end{document}` ends it. Words between those two are the '
                'text. Anything after `\\end{document}` is ignored, which is '
                'how people stash notes they do not want on the page.\n\n'
                '`pdflatex notes.tex` reads the source and writes `notes.pdf`. '
                'It also writes `notes.aux` and `notes.log`. The log is the '
                'transcript. The aux file is memory: labels, references, the '
                'table of contents. A document with cross-references needs a '
                'second run so the aux from the first run can fill the '
                'numbers. That is not a bug. That is how the compiler knows '
                'what page a label landed on.\n\n'
                'If `pdflatex` is missing, the package is a TeX Live install: '
                'large, one-time, and then the command is just there. Until '
                'it is, the source is still worth writing.\n\n'
                'The first compile of an empty-looking file often fails '
                'because the class name is misspelt, or because the file was '
                'saved as `notes.txt`. The engine only reads `.tex`. Rename '
                'it, or pass the full name: `pdflatex notes.txt` will not '
                'find a document.\n\n'
                'The next lesson is what goes in the body: a title, sections, '
                'and why a blank line is a paragraph.'
            ),
            'examples': [
                {
                    'label': 'The smallest file',
                    'code': ('\\documentclass{article}\n'
                             '\\begin{document}\n'
                             'Hello, world.\n'
                             '\\end{document}'),
                    'note': 'article is the default class. letter, report and '
                            'book exist; start with article.',
                },
                {
                    'label': 'Compile, then look',
                    'code': ('pdflatex notes.tex\n'
                             '  notes.pdf   the document\n'
                             '  notes.log   what the compiler said\n'
                             '  notes.aux   labels and references\n'
                             '\n'
                             'pdflatex notes.tex\n'
                             '  second run fills in \\ref from the aux'),
                    'note': 'Delete the pdf, aux and log any time. They come '
                            'back from the source. The .tex is the only file '
                            'to keep in git.',
                },
            ],
            'misconceptions': [
                'A first compile that says "Rerun to get cross-references '
                'right" is not a failure. Run it again.',
                'Opening the .tex in a PDF viewer shows source, not a page. '
                'Open the .pdf.',
            ],
            'try_it': [
                'Write the four-line file, run `pdflatex` on it, and open the '
                'PDF. Then change one word, compile again, and watch the page '
                'update.',
            ],
        },
        {
            'id': 'tx-structure',
            'title': 'Title, sections, and what a blank line means',
            'next': 'tx-text',
            'concept': (
                'Title and section commands are how a document grows a spine. '
                'That is why the table of contents and the PDF outline can '
                'number themselves.\n\n'
                '`\\title{...}`, `\\author{...}` and `\\date{...}` go before '
                '`\\begin{document}`. They store the values. `\\maketitle` '
                'inside the body prints them. Forgetting `\\maketitle` is why '
                'a file that "has a title" produces a blank header.\n\n'
                'Headings are a ladder: `\\section`, `\\subsection`, '
                '`\\subsubsection`. They number themselves. `\\section*` '
                'drops the number, which is how you get an unnumbered '
                'Introduction. Do not fake a heading with bold text. A real '
                'section is what the table of contents and the PDF outline '
                'read.\n\n'
                'A blank line starts a new paragraph. A single newline does '
                'not. That is the opposite of Markdown, and it is the first '
                'habit to retrain. Two spaces at the end of a line do '
                'nothing. `\\\\` forces a line break without a new paragraph, '
                'which is almost never what you want in prose and is the '
                'right tool in a table or a title.\n\n'
                'A document with sections and no `\\maketitle` still compiles. '
                'The title sits in memory and never reaches the page, which '
                'is why the PDF looks like it started mid-thought. Add the '
                'one command, compile again, and the header appears.\n\n'
                'The next lesson is the characters that are not letters: the '
                'backslash, the dollar, and the ones that must be escaped.'
            ),
            'examples': [
                {
                    'label': 'A title and two headings',
                    'code': ('\\documentclass{article}\n'
                             '\\title{Notes}\n'
                             '\\author{Ada}\n'
                             '\\date{\\today}\n'
                             '\\begin{document}\n'
                             '\\maketitle\n'
                             '\\section{Setup}\n'
                             'A paragraph.\n'
                             '\n'
                             'Another paragraph.\n'
                             '\\section{Results}\n'
                             '\\end{document}'),
                    'note': '\\today prints the compile date. Freeze a date '
                            'by writing it out if the PDF must not move.',
                },
                {
                    'label': 'A blank line is a paragraph',
                    'code': ('These two sentences\n'
                             'stay in one paragraph.\n'
                             '\n'
                             'This one starts another.\n'
                             '\n'
                             '\\\\ is a line break, not a paragraph.'),
                    'note': 'Pressing Enter once wraps the source so it is '
                            'readable. It does not wrap the page.',
                },
            ],
            'misconceptions': [
                '\\title does not print anything. \\maketitle does, and it '
                'has to sit inside the document environment.',
                'A new line in the source is not a new paragraph. Only a '
                'blank line is.',
            ],
            'try_it': [
                'Add a title, an author, and two sections to the first file. '
                'Compile twice if the PDF outline looks empty on the first '
                'run.',
            ],
        },
        {
            'id': 'tx-text',
            'title': 'Special characters, and changing the voice',
            'next': 'tx-math',
            'concept': (
                'Escapes and font commands are how you print a special '
                'character or change the voice. That is why a stray `%` eats a '
                'sentence and a `_` in a file name kills the compile.\n\n'
                'These ten are special: `\\ { } $ & % # _ ^ ~`. A backslash '
                'starts a command. Braces group. `$` enters math. `&` is a '
                'column in a table. `%` starts a comment to the end of the '
                'line, which is why a forgotten percent eats the rest of a '
                'sentence and the PDF looks fine except that sentence is '
                'gone. `#` is a command argument. `_` and `^` are sub and '
                'super in math. `~` is a space that will not break a line.\n\n'
                'To print one of those characters, escape it: `\\%`, `\\$`, '
                '`\\&`, `\\#`, `\\_`, `\\{`, `\\}`. A literal backslash is '
                '`\\textbackslash`. A literal tilde is `\\textasciitilde`.\n\n'
                '`\\textbf{bold}`, `\\textit{italic}`, `\\emph{this}` for '
                'emphasis that flips inside italics. `\\texttt{code}` is a '
                'monospaced word. Quotes are two backticks and two '
                'apostrophes for doubles, or one of each for singles, not '
                'the straight " key, which prints two identical marks.\n\n'
                'A file name with an underscore is the first compile that '
                'dies on a line you thought was plain English. Escape the '
                'underscore, or put the name in `\\texttt` after escaping, '
                'or keep names free of the ten specials until they are '
                'boring.\n\n'
                'The next lesson is math mode, which is why those dollars '
                'were reserved.'
            ),
            'examples': [
                {
                    'label': 'Escape, or lose the sentence',
                    'code': ('Costs were 10\\% of the budget.\n'
                             'See table 2 \\& table 3.\n'
                             'file\\_name.txt\n'
                             '\n'
                             '% this line never reaches the PDF'),
                    'note': 'A stray % is the quietest bug in LaTeX. The '
                            'compile succeeds. The sentence does not.',
                },
                {
                    'label': 'Voice',
                    'code': ('\\textbf{bold}  \\textit{italic}  \\emph{emph}\n'
                             '\\texttt{ls -l}\n'
                             '``quoted\'\'     not "quoted"\n'
                             'Ada~Lovelace   no line break in the name'),
                    'note': '\\emph is the one to prefer in prose. It still '
                            'reads as emphasis when it sits inside italics.',
                },
            ],
            'misconceptions': [
                'The " key is not a pair of quotes. It is two identical ticks. '
                'Opening quotes are backticks.',
                'An unescaped _ outside math is an error, not an underscore. '
                'Inside a file name that is the usual first compile failure.',
            ],
            'try_it': [
                'Write a sentence that contains a percent, a dollar amount, '
                'and a file_name. Compile it. Then comment out one sentence '
                'with % and compile again.',
            ],
        },
        {
            'id': 'tx-math',
            'title': 'Math mode: inline, display, and a few commands',
            'next': 'tx-floats',
            'concept': (
                'Math mode is how you write a formula that stays a formula. '
                'That is why a paper with fractions and sums is a LaTeX job '
                'rather than a screenshot.\n\n'
                '`$...$` is inline math: a formula that sits in a sentence. '
                '`\\[ ... \\]` is display math: a formula on its own line, '
                'centred. `$$` is an older display form that still works and '
                'is worth recognising, not writing. Numbered equations use '
                'the `equation` environment, which also makes a `\\label` '
                'you can `\\ref` later.\n\n'
                'Inside math, letters are variables. Ordinary words look '
                'wrong: `$of$` is three variables, not the word of. Use '
                '`\\mathrm{of}` or step out of math. Superscript is `^`, '
                'subscript is `_`, and more than one character needs braces: '
                '`$x^{10}$`, `$a_{i,j}$`. `\\frac{a}{b}` is a fraction. '
                '`\\sqrt{x}` is a root. `\\sum`, `\\int`, `\\infty`, '
                '`\\alpha`, `\\leq`, `\\times` cover most of a first paper.\n\n'
                'An unmatched `$` is the error that looks like it is on a '
                'later line. The compiler keeps reading in the wrong mode '
                'until something else breaks. If a log blames a random '
                'command, count the dollars first.\n\n'
                'Display math that still sits in a sentence is almost always '
                'a missing closer: one `$` opened, none closed, and the rest '
                'of the paragraph is typeset as variables. Look at the PDF. '
                'If a whole paragraph went italic and spaced like algebra, '
                'count the dollars.\n\n'
                'The next lesson is lists, tables, figures, and the labels '
                'that point at them.'
            ),
            'examples': [
                {
                    'label': 'In a sentence, and on its own line',
                    'code': ('The energy is $E = mc^{2}$.\n'
                             '\n'
                             '\\[\n'
                             '  E = mc^{2}\n'
                             '\\]\n'
                             '\n'
                             '\\begin{equation}\n'
                             '  E = mc^{2} \\label{eq:emc}\n'
                             '\\end{equation}'),
                    'note': 'Use \\ref{eq:emc} later. Compile twice so the '
                            'number appears.',
                },
                {
                    'label': 'The commands that pay for the lesson',
                    'code': ('$\\frac{a}{b}$     $\\sqrt{x+1}$\n'
                             '$x_{i}^{2}$       $\\sum_{i=1}^{n} i$\n'
                             '$\\alpha, \\beta$   $\\leq \\geq \\neq$\n'
                             '$\\int_{0}^{1} x \\, dx$'),
                    'note': '\\, is a thin space. Put it before dx so the d '
                            'is not a variable sitting on x.',
                },
            ],
            'misconceptions': [
                'Letters in math mode are variables. The word of inside '
                'dollars is three italic letters, not an English word.',
                'An unmatched $ is often reported many lines later. Search '
                'upward for the missing closer before editing the line the '
                'log named.',
            ],
            'try_it': [
                'Typeset E = mc^2 inline and as a numbered equation. Then '
                'write a fraction and a sum with limits.',
            ],
        },
        {
            'id': 'tx-floats',
            'title': 'Lists, tables, figures, and pointing at them',
            'next': 'tx-preamble',
            'concept': (
                'The previous lesson put a formula on the page. This one puts '
                'the other three things a first paper needs: a list, a table, '
                'and a picture, each with a number you can point at.\n\n'
                '`itemize` is bullets. `enumerate` is numbers. `\\item` starts '
                'each entry. Nested lists are just environments inside '
                'environments.\n\n'
                '`tabular` is a table. The argument `{lcr}` is one column '
                'left, one centred, one right. `&` moves to the next column. '
                '`\\\\` ends the row. `\\hline` draws a rule. Wrap it in a '
                '`table` environment with `\\caption` and `\\label` if you '
                'want it numbered and movable. LaTeX will slide a table to '
                'where it fits. That is a float, and it is why the table is '
                'not always where you typed it.\n\n'
                'A figure is the same shape: `figure` environment, '
                '`\\includegraphics{plot.pdf}`, caption, label. '
                '`\\includegraphics` needs the `graphicx` package from the '
                'next lesson. `\\ref{fig:plot}` prints the number. Compile '
                'twice.\n\n'
                '`\\includegraphics` without `graphicx` is an undefined '
                'control sequence. The log names the command. The fix is '
                'not a typo in the filename, it is a missing '
                '`\\usepackage` in the preamble, which is the next lesson.\n\n'
                'The next lesson is the preamble: the packages that make '
                'figures, nicer math, and links actually work.'
            ),
            'examples': [
                {
                    'label': 'A list and a small table',
                    'code': ('\\begin{itemize}\n'
                             '  \\item first\n'
                             '  \\item second\n'
                             '\\end{itemize}\n'
                             '\n'
                             '\\begin{tabular}{lr}\n'
                             '  name & n \\\\\n'
                             '  \\hline\n'
                             '  ada  & 2 \\\\\n'
                             '\\end{tabular}'),
                    'note': 'The {lr} string is one letter per column. Add a '
                            'letter, add a column, or the extra & is an error.',
                },
                {
                    'label': 'A numbered figure you can point at',
                    'code': ('\\begin{figure}[ht]\n'
                             '  \\centering\n'
                             '  \\includegraphics[width=0.8\\textwidth]{plot.pdf}\n'
                             '  \\caption{A run of the experiment.}\\label{fig:run}\n'
                             '\\end{figure}\n'
                             '\n'
                             'See Figure~\\ref{fig:run}.'),
                    'note': '[ht] means try here, then the top of a page. '
                            'Leave the placement to LaTeX before fighting it.',
                },
            ],
            'misconceptions': [
                'A table environment is not the same as tabular. tabular '
                'draws the grid. table makes it float and take a caption.',
                '\\label must come after \\caption, or the number it stores '
                'is the previous one. That is the usual off-by-one in refs.',
            ],
            'try_it': [
                'Add an itemize list and a two-column tabular to the notes '
                'file. Then wrap the table in table, give it a caption and '
                'a label, and \\ref it from the text.',
            ],
        },
        {
            'id': 'tx-preamble',
            'title': 'The preamble, and the packages you actually need',
            'next': 'tx-cite',
            'concept': (
                'The preamble is how you load the packages a document needs. '
                'That is why `\\includegraphics` is undefined until `graphicx` '
                'is listed between `\\documentclass` and `\\begin{document}`.\n\n'
                '`\\usepackage{graphicx}` unlocks `\\includegraphics`. '
                '`\\usepackage{amsmath}` unlocks `align`, `\\text` inside '
                'math, and a better set of operators. `\\usepackage{geometry}` '
                'with `\\geometry{margin=1in}` is how you set margins without '
                'fighting the class. `\\usepackage{hyperref}` makes '
                '`\\ref` and URLs into clicks, and wants to be loaded last '
                'because it rewrites other commands.\n\n'
                'That is enough for a first paper. A CV class, a journal '
                'template, or `biblatex` can wait. Adding a package you do '
                'not understand is how two packages fight over the same '
                'command and the error names neither of them.\n\n'
                '`inputenc` and `fontenc` show up in old templates. On a '
                'modern pdflatex they are usually already handled. If a file '
                'from 2012 starts with those two lines, leave them; they are '
                'not the interesting part.\n\n'
                'A journal template will ship its own class and a list of '
                'packages. Use that list. Mixing a template with a pile of '
                'packages from a blog post is how two commands with the same '
                'name fight, and the error names a third command you never '
                'wrote.\n\n'
                'The next lesson is citations: a key in the source, a .bib '
                'file, and why [?] means another run.'
            ),
            'examples': [
                {
                    'label': 'A preamble that will carry a first paper',
                    'code': ('\\documentclass[11pt,a4paper]{article}\n'
                             '\\usepackage{graphicx}\n'
                             '\\usepackage{amsmath}\n'
                             '\\usepackage{geometry}\n'
                             '\\geometry{margin=1in}\n'
                             '\\usepackage{hyperref}\n'
                             '\\begin{document}'),
                    'note': 'Options on the class sit in the first square '
                            'brackets: 11pt and a4paper are the usual pair '
                            'outside the US.',
                },
                {
                    'label': 'align, from amsmath',
                    'code': ('\\begin{align}\n'
                             '  a &= b + c \\\\\n'
                             '    &= d\n'
                             '\\end{align}'),
                    'note': '& marks the alignment point, usually the equals. '
                            '\\\\ still ends the line. This environment needs '
                            'amsmath.',
                },
            ],
            'misconceptions': [
                'usepackage goes in the preamble, not in the body. A package '
                'loaded after \\begin{document} is an error.',
                'hyperref wants to load last. Loaded early, it misses commands '
                'other packages define, and links silently do nothing.',
            ],
            'try_it': [
                'Add graphicx, amsmath, geometry and hyperref to the first '
                'file. Set a one-inch margin. Compile and check the page '
                'looks less like 1995.',
            ],
        },
        {
            'id': 'tx-cite',
            'title': 'Citations: a key, a .bib, and another run',
            'next': 'tx-errors',
            'concept': (
                'A citation is a key you type and a record that lives in a '
                '`.bib` file. That is why `\\cite{knuth84}` prints `[?]` until '
                'the bibliography has been built: the aux file has the key, '
                'bibtex (or biber) fills the list, and a second pdflatex '
                'puts the number in. `latexmk` does those runs for you.\n\n'
                'The record is ordinary text. `@article{knuth84, author = '
                '{Knuth, Donald}, title = {Literate Programming}, year = '
                '{1984}}` is enough. The key `knuth84` is what `\\cite` '
                'names. `\\bibliography{refs}` and `\\bibliographystyle'
                '{plain}` go before `\\end{document}`, and the file is '
                '`refs.bib`. No extension on `\\bibliography`.\n\n'
                '`biblatex` plus `\\printbibliography` is the other family. '
                'It wants biber, not bibtex. A first paper can stay with '
                '`\\cite` and `\\bibliography`. Mixing both in one file is '
                'how you get two empty lists and a log that names neither.\n\n'
                'A `[?]` that survives `latexmk` is a key that is not in '
                'the `.bib`, or a typo in one of the two spellings. The '
                'log line is `Citation knuth84 on page 1 undefined`. That '
                'is a missing record, not a missing package.\n\n'
                'The next lesson is the rest of the log, and the habit of '
                'letting latexmk finish the extra runs.'
            ),
            'examples': [
                {
                    'label': 'The two files',
                    'code': ('% notes.tex\n'
                             'See \\cite{knuth84}.\n'
                             '\\bibliography{refs}\n'
                             '\\bibliographystyle{plain}\n'
                             '\n'
                             '% refs.bib\n'
                             '@article{knuth84,\n'
                             '  author = {Knuth, Donald},\n'
                             '  title  = {Literate Programming},\n'
                             '  year   = {1984}}'),
                    'note': 'The key must match exactly. latexmk -pdf '
                            'notes.tex runs bibtex when it sees cite.',
                },
                {
                    'label': 'What [?] is saying',
                    'code': ('first pdflatex    writes knuth84 into aux\n'
                             'bibtex            fills the list from refs.bib\n'
                             'pdflatex again    [1] appears\n'
                             '\n'
                             'still [?]?        the key is not in the .bib'),
                    'note': 'latexmk is those three steps. Running pdflatex '
                            'once is why a first paper looks uncited.',
                },
            ],
            'misconceptions': [
                '[?] after one pdflatex is normal. The bibliography is a '
                'second program, not a package you forgot.',
                '\\bibliography{refs} names refs.bib. Writing refs.bib '
                'inside the braces looks for refs.bib.bib.',
            ],
            'try_it': [
                'Add one \\cite and a one-record .bib to the first file, '
                'run latexmk -pdf, and confirm [?] becomes a number.',
            ],
        },
        {
            'id': 'tx-errors',
            'title': 'Reading the log, and a workflow that survives',
            'concept': (
                'The previous lessons assumed the file compiled. This one is '
                'what you do when it does not, which is most of the first '
                'week.\n\n'
                'The log is `notes.log`, and the useful line starts with `!`. '
                'Read that line, then the line number under `l.`. The real '
                'mistake is often a few lines above: a missing `}`, an extra '
                '`{`, an unmatched `$`, a `%` that ate a brace. If the error '
                'names a command you did not write, look upward for an '
                'unclosed group.\n\n'
                '`Overfull \\hbox` is not an error. It is a line that stuck '
                'out of the margin, usually a long word or a URL. '
                '`\\url{...}` from hyperref is the fix for URLs. Rewriting '
                'the sentence is the fix for a word.\n\n'
                '`latexmk -pdf notes.tex` reruns pdflatex (and bibtex, later) '
                'until the aux file stops changing. That is the command to '
                'build a habit around. `latexmk -c` deletes the helper files '
                'and keeps the PDF. A missing citation is usually "you have '
                'not run it enough times", not a missing `.bib`.\n\n'
                'Keep the `.tex` in git. Ignore `*.aux *.log *.out *.toc '
                '*.pdf` unless the PDF is the thing you ship. The source is '
                'the document. The rest is a build.\n\n'
                'When a file from someone else will not compile, read the '
                'first `!` line before adding packages. Most of those files '
                'fail because a package they assumed is not on this machine, '
                'or because they were written for XeLaTeX and this module '
                'is running pdflatex. The engine is a fact about the file, '
                'not a preference.'
            ),
            'examples': [
                {
                    'label': 'What the log is actually saying',
                    'code': ('! Undefined control sequence.\n'
                             'l.12 \\includegraphic{plot.pdf}\n'
                             '      a typo, graphicx is not the bug\n'
                             '\n'
                             '! Missing $ inserted.\n'
                             'l.20 _\n'
                             '      an underscore outside math'),
                    'note': 'The command it names is a symptom. The cause is '
                            'the nearest unclosed group or mode switch above.',
                },
                {
                    'label': 'A build you can repeat',
                    'code': ('latexmk -pdf notes.tex    until aux is stable\n'
                             'latexmk -c                drop aux and log\n'
                             '\n'
                             '# .gitignore\n'
                             '*.aux *.log *.out *.toc *.fls *.fdb_latexmk'),
                    'note': 'latexmk is part of TeX Live. If it is missing, '
                            'running pdflatex twice is the same idea.',
                },
            ],
            'misconceptions': [
                'The line the log names is where it gave up, not always where '
                'the mistake is. Search upward.',
                'A citation that prints as [?] is usually a missing extra '
                'run, not a missing bibliography file.',
            ],
            'try_it': [
                'Break the file on purpose: drop a closing brace, compile, '
                'and find the ! line. Then restore it and run latexmk -pdf '
                'once.',
            ],
        },
    ],

    'drills': [
        {'id': 'txd-pdflatex', 'type': 'command',
         'answer': 'pdflatex notes.tex',
         'prompt': 'Compile notes.tex to a PDF with pdflatex.',
         'teach': 'The engine reads the source and writes notes.pdf, plus a '
                  'log and an aux file.'},
        {'id': 'txd-latexmk', 'type': 'command',
         'answer': 'latexmk -pdf notes.tex',
         'prompt': 'Compile notes.tex, rerunning until references settle.',
         'teach': 'latexmk keeps calling pdflatex until the aux file stops '
                  'changing.'},
        {'id': 'txd-latexmk-c', 'type': 'command',
         'answer': 'latexmk -c',
         'prompt': 'Delete helper files and keep the PDF.',
         'teach': '-c is clean. The .tex and the .pdf stay.'},
        {'id': 'txd-class', 'type': 'command',
         'answer': '\\documentclass{article}',
         'prompt': 'Write the line that picks the article class.',
         'teach': 'This is the first line of almost every file. letter, report '
                  'and book are other classes.'},
        {'id': 'txd-begin', 'type': 'command',
         'answer': '\\begin{document}',
         'prompt': 'Start the document body.',
         'teach': 'Everything before this is the preamble. Everything after '
                  'is the page.'},
        {'id': 'txd-end', 'type': 'command',
         'answer': '\\end{document}',
         'prompt': 'End the document body.',
         'teach': 'Anything after this line is ignored, which is a fine place '
                  'for notes to yourself.'},
        {'id': 'txd-maketitle', 'type': 'command',
         'answer': '\\maketitle',
         'prompt': 'Print the stored title, author and date.',
         'teach': '\\title stores. \\maketitle prints. Forgetting this is why '
                  'the header is empty.'},
        {'id': 'txd-section', 'type': 'command',
         'answer': '\\section{Setup}',
         'prompt': 'Start a numbered section called Setup.',
         'teach': '\\section* drops the number. Do not fake a heading with '
                  'bold text.'},
        {'id': 'txd-textbf', 'type': 'command',
         'answer': '\\textbf{bold}',
         'prompt': 'Make the word bold bold.',
         'teach': 'Braces group the argument. Missing them bolds only the '
                  'next character.'},
        {'id': 'txd-emph', 'type': 'command',
         'answer': '\\emph{this}',
         'prompt': 'Emphasise the word this.',
         'teach': '\\emph flips inside italics. \\textit does not.'},
        {'id': 'txd-percent', 'type': 'command',
         'answer': '10\\%',
         'prompt': 'Write 10 percent so the percent sign reaches the PDF.',
         'teach': 'An unescaped % comments out the rest of the line.'},
        {'id': 'txd-inline', 'type': 'command',
         'answer': '$E = mc^{2}$',
         'prompt': 'Write E = mc squared as inline math.',
         'teach': 'Dollars switch into math. Braces group the superscript.'},
        {'id': 'txd-frac', 'type': 'command',
         'answer': '$\\frac{a}{b}$',
         'prompt': 'Write the fraction a over b in inline math.',
         'teach': '\\frac takes two braced arguments: numerator, denominator.'},
        {'id': 'txd-item', 'type': 'command',
         'answer': '\\item',
         'prompt': 'Start one entry in an itemize or enumerate list.',
         'teach': 'The environment numbers or bullets. \\item is each row.'},
        {'id': 'txd-include', 'type': 'command',
         'answer': '\\includegraphics{plot.pdf}',
         'prompt': 'Insert plot.pdf as a figure, given graphicx is loaded.',
         'teach': 'graphicx is a preamble package. Without it this command '
                  'is undefined.'},
        {'id': 'txd-ref', 'type': 'command',
         'answer': '\\ref{fig:run}',
         'prompt': 'Print the number of the label fig:run.',
         'teach': 'Compile twice. The first run writes the aux; the second '
                  'fills the number.'},
        {'id': 'txd-usepack', 'type': 'command',
         'answer': '\\usepackage{graphicx}',
         'prompt': 'Load the package that provides includegraphics.',
         'teach': 'Packages go in the preamble, before \\begin{document}.'},
        {'id': 'txd-cite', 'type': 'command',
         'answer': '\\cite{knuth84}',
         'prompt': 'Cite the bibliography key knuth84.',
         'teach': 'The key must match a record in the .bib. [?] means another run, or a typo.'},
        {'id': 'txd-bib', 'type': 'command',
         'answer': '\\bibliography{refs}',
         'prompt': 'Include the bibliography stored in refs.bib.',
         'teach': 'No .bib in the braces. \\bibliographystyle{plain} sits next to it.'},
    ],

    'challenges': [
        {
            'id': 'txc-minimal',
            'title': 'Write a file that can compile',
            'goal': 'The four lines that make a document. Everything else in '
                    'the module hangs off this shape.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {}},
            'solution': {
                'shell': (
                    "cat > hello.tex <<'END'\n"
                    "\\documentclass{article}\n"
                    "\\begin{document}\n"
                    "Hello, world.\n"
                    "\\end{document}\n"
                    "END"
                ),
            },
            'steps': [
                {'instruction': 'Create hello.tex.'},
                {'instruction': 'Pick the article class on the first line.',
                 'hint': '\\documentclass{article}'},
                {'instruction': 'Open and close the document environment, '
                                'with one sentence of text in between.'},
            ],
            'free': 'Write hello.tex: article class, a document environment, '
                    'and the sentence Hello, world.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_contains': {
                        'hello.tex': [
                            '\\documentclass{article}',
                            '\\begin{document}',
                            'Hello, world.',
                            '\\end{document}',
                        ],
                    },
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'txc-structure',
            'title': 'Title, two sections, two paragraphs',
            'goal': 'A document with a spine. The blank line between '
                    'paragraphs is the part people skip.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {}},
            'solution': {
                'shell': (
                    "cat > notes.tex <<'END'\n"
                    "\\documentclass{article}\n"
                    "\\title{Notes}\n"
                    "\\author{Ada}\n"
                    "\\begin{document}\n"
                    "\\maketitle\n"
                    "\\section{Setup}\n"
                    "First paragraph.\n"
                    "\n"
                    "Second paragraph.\n"
                    "\\section{Results}\n"
                    "\\end{document}\n"
                    "END"
                ),
            },
            'steps': [
                {'instruction': 'Create notes.tex as an article.'},
                {'instruction': 'Store a title Notes and an author Ada, then '
                                'print them with maketitle.',
                 'hint': '\\title, \\author, then \\maketitle inside the body'},
                {'instruction': 'Add a Setup section with two paragraphs '
                                'separated by a blank line, then a Results '
                                'section.'},
            ],
            'free': 'Write notes.tex with title Notes, author Ada, maketitle, '
                    'sections Setup and Results, and two paragraphs under '
                    'Setup.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_contains': {
                        'notes.tex': [
                            '\\title{Notes}',
                            '\\author{Ada}',
                            '\\maketitle',
                            '\\section{Setup}',
                            '\\section{Results}',
                        ],
                    },
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'txc-fix',
            'title': 'Fix the source the compiler will reject',
            'goal': 'Two quiet bugs: a percent that eats a sentence, and an '
                    'underscore outside math. The log will name the second. '
                    'The first it will not.',
            'setup': {
                'kind': 'sandbox',
                'shell': 'bash',
                'tree': {
                    'broken.tex': (
                        '\\documentclass{article}\n'
                        '\\begin{document}\n'
                        'Costs were 10% of the budget this year.\n'
                        'See file_name.txt for the raw numbers.\n'
                        '\\end{document}\n'
                    ),
                },
            },
            'solution': {
                'shell': (
                    "cat > fixed.tex <<'END'\n"
                    "\\documentclass{article}\n"
                    "\\begin{document}\n"
                    "Costs were 10\\% of the budget this year.\n"
                    "See file\\_name.txt for the raw numbers.\n"
                    "\\end{document}\n"
                    "END"
                ),
            },
            'steps': [
                {'instruction': 'Read broken.tex. One sentence is a comment. '
                                'One underscore is an error.'},
                {'instruction': 'Write fixed.tex with both characters escaped.',
                 'hint': '\\% and \\_'},
            ],
            'free': 'Write fixed.tex that prints 10% and file_name.txt.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_contains': {
                        'fixed.tex': ['10\\%', 'file\\_name.txt'],
                    },
                    'file_lacks': {
                        'fixed.tex': ['10% of', 'file_name'],
                    },
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'txc-math',
            'title': 'Put a formula in a sentence and on its own line',
            'goal': 'Inline math and display math are different modes. A '
                    'first paper needs both.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {}},
            'solution': {
                'shell': (
                    "cat > energy.tex <<'END'\n"
                    "\\documentclass{article}\n"
                    "\\begin{document}\n"
                    "The energy is $E = mc^{2}$.\n"
                    "\\[\n"
                    "E = mc^{2}\n"
                    "\\]\n"
                    "\\end{document}\n"
                    "END"
                ),
            },
            'steps': [
                {'instruction': 'Create energy.tex as an article.'},
                {'instruction': 'Write a sentence that contains E = mc^2 as '
                                'inline math.',
                 'hint': '$E = mc^{2}$'},
                {'instruction': 'Repeat the same formula as display math.',
                 'hint': '\\[ E = mc^{2} \\]'},
            ],
            'free': 'Write energy.tex with E = mc^2 inline and in display math.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_contains': {
                        'energy.tex': ['$E = mc^{2}$', '\\[', '\\]'],
                    },
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'txc-cite',
            'title': 'A citation and the .bib it names',
            'goal': 'A paper cites a key. The record lives in a second file. '
                    'The trainer checks the source, not the numbered PDF.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {}},
            'solution': {
                'shell': (
                    "cat > notes.tex <<'END'\n"
                    "\\documentclass{article}\n"
                    "\\begin{document}\n"
                    "See \\cite{knuth84}.\n"
                    "\\bibliography{refs}\n"
                    "\\bibliographystyle{plain}\n"
                    "\\end{document}\n"
                    "END\n"
                    "cat > refs.bib <<'END'\n"
                    "@article{knuth84,\n"
                    "  author = {Knuth, Donald},\n"
                    "  title  = {Literate Programming},\n"
                    "  year   = {1984}}\n"
                    "END"
                ),
            },
            'steps': [
                {'instruction': 'Write notes.tex that cites knuth84 and '
                                'includes bibliography refs.',
                 'hint': '\\cite{knuth84} and \\bibliography{refs}'},
                {'instruction': 'Write refs.bib with an @article record '
                                'whose key is knuth84.',
                 'hint': '@article{knuth84, author, title, year}'},
            ],
            'free': 'notes.tex cites knuth84. refs.bib defines that key.',
            'verify': {
                'kind': 'sandbox',
                'expect': {
                    'file_contains': {
                        'notes.tex': ['\\cite{knuth84}',
                                      '\\bibliography{refs}'],
                        'refs.bib': ['@article{knuth84', 'Knuth'],
                    },
                },
            },
            'fallback': 'self',
        },
        {
            'id': 'txc-compile',
            'title': 'Compile a file and open the PDF',
            'goal': 'The trainer can read the source. Looking at the page is '
                    'yours, because a PDF viewer is not a sandbox.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'Take any .tex file from this module, or the '
                                'four-line hello document.'},
                {'instruction': 'Compile it with pdflatex, or latexmk -pdf.',
                 'hint': 'pdflatex hello.tex'},
                {'instruction': 'Open the PDF. Change one word in the source, '
                                'compile again, and confirm the page moved.'},
                {'instruction': 'Read the .log and find the output written '
                                'line, so the log is a file you have seen '
                                'when it is not failing.'},
            ],
            'free': 'On this machine: compile a .tex file and open the PDF.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
    ],

    'quiz': [
        {
            'id': 'txq-what',
            'type': 'mcq',
            'prompt': 'What is a .tex file, relative to the PDF?',
            'answer': 'The source you edit. The PDF is a build product the compiler writes.',
            'distractors': [
                'A binary preview of the PDF.',
                'The same file as the PDF, with a different extension.',
                'A style sheet the PDF viewer reads.',
            ],
            'teach': 'Edit the .tex. Ship the PDF. Keep the .tex in git.',
        },
        {
            'id': 'txq-blank',
            'type': 'mcq',
            'prompt': 'In the source, what starts a new paragraph?',
            'answer': 'A blank line.',
            'distractors': [
                'A single newline, as in Markdown.',
                'Two spaces at the end of the line.',
                'A tab at the start of the next line.',
            ],
            'teach': 'A single newline only wraps the source so you can read it.',
        },
        {
            'id': 'txq-percent',
            'type': 'mcq',
            'prompt': 'A sentence vanished from the PDF but the compile succeeded. Why?',
            'answer': 'An unescaped % commented out the rest of that line.',
            'distractors': [
                'pdflatex drops the last sentence of every paragraph.',
                'The sentence used a UTF-8 character.',
                '\\maketitle was missing.',
            ],
            'teach': '% starts a comment. Write \\% when you mean a percent sign.',
        },
        {
            'id': 'txq-dollar',
            'type': 'mcq',
            'prompt': 'What do the dollars in $E = mc^{2}$ do?',
            'answer': 'They switch into math mode for that formula.',
            'distractors': [
                'They print dollar signs around the formula.',
                'They make the formula a numbered equation.',
                'They mark a comment, like in bash.',
            ],
            'teach': 'Inline math is $...$. Display math is \\[ ... \\].',
        },
        {
            'id': 'txq-aux',
            'type': 'mcq',
            'prompt': 'Why does a document with \\ref need a second pdflatex run?',
            'answer': 'The first run writes the aux file; the second run reads the numbers from it.',
            'distractors': [
                'The PDF viewer caches the first page.',
                '\\ref is ignored until hyperref is loaded twice.',
                'pdflatex always discards the first compile.',
            ],
            'teach': 'latexmk -pdf keeps running until the aux file stops changing.',
        },
        {
            'id': 'txq-cite',
            'type': 'mcq',
            'prompt': 'A citation prints as [?]. What is the usual cause after one pdflatex?',
            'answer': 'The bibliography has not been built yet. latexmk (or bibtex plus another pdflatex) fills it.',
            'distractors': [
                'graphicx is missing from the preamble.',
                'The .bib file must be named notes.bib.',
                'Citations only work with XeLaTeX.',
            ],
            'teach': '[?] after one run is normal. A [?] after latexmk is a key that is not in the .bib.',
        },
        {
            'id': 'txq-label',
            'type': 'mcq',
            'prompt': 'A \\ref prints the previous figure number. What went wrong?',
            'answer': 'The \\label was written before the \\caption, so it stored the last number.',
            'distractors': [
                'The label name contained a colon.',
                'graphicx was loaded after hyperref.',
                'The figure used [ht] placement.',
            ],
            'teach': 'Put \\label after \\caption, inside the same float.',
        },
        {
            'id': 'txq-log',
            'type': 'mcq',
            'prompt': 'The log blames a line you did not change. Where is the mistake?',
            'answer': 'Usually a few lines above: a missing brace or an unmatched $.',
            'distractors': [
                'Always on the first line of the file.',
                'In the PDF viewer settings.',
                'In a package you did not load.',
            ],
            'teach': 'The line the log names is where it gave up, not always where it went wrong.',
        },
    ],
}
