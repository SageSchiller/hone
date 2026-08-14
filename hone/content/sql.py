"""SQL and sqlite: querying tables, the third data-wrangling language.

The roster already teaches two ways to pull answers out of data: awk for
columns and jq for JSON. SQL is the third and the one that changes how you
think the most, because it is **declarative**. You do not write the loop that
finds the rows; you describe the rows you want and the engine works out how to
get them. That reframe, from "how do I iterate" to "what do I want", is the
whole reason SQL earns a module rather than a cheat sheet.

**Why sqlite specifically.** SQLite is the most deployed database in the world
and you are already carrying dozens of them. Browser history, cookies and
bookmarks, phone apps, mail clients, note apps, and a great deal of endpoint
security tooling all store their data in a `.sqlite` file. For DFIR that makes
SQL a forensic skill: the artifact is a database, and reading it is a query.

**Fully verified, with nothing installed.** SQLite ships as a single small
binary that is present nearly everywhere, and even Python's standard library
carries its own copy, so this module honors the offline, no-dependency rule
better than most. Every challenge here runs a real `sqlite3` in the sandbox and
reads the result back, so the SQL you write is graded by running it, not by
comparing it to a reference spelling.
"""

MODULE = {
    'id': 'sql',
    'title': 'SQL and sqlite',
    'group': 'Text processing',
    'blurb': 'Tables, SELECT, joins, grouping, and querying the databases you already carry.',
    'context': 'You are at a shell prompt with sqlite3, working on a database file.',
    'needs': ['sqlite3'],
    'prereqs': ['linux'],
    'adapter': 'sandbox',
    'estimate': '4-5 hours',
    'order': 33,

    'lessons': [
        {
            'id': 'sq-model',
            'title': 'Tables, rows, and thinking in sets',
            'next': 'sq-sqlite',
            'concept': (
                'A relational database is tables, and a table is rows of typed '
                'columns, like a spreadsheet with rules. The rules are the '
                'point: every row has the same columns, each column has a type, '
                'and a table usually has a column that uniquely names each row, '
                'the primary key.\n\n'
                'The shift that makes SQL worth learning is that it is '
                '**declarative**. In awk or Python you write a loop that walks '
                'the rows and keeps the ones you want. In SQL you write a '
                'sentence that describes the rows you want, and the database '
                'decides how to find them, including which index to use and in '
                'what order. `SELECT name FROM users WHERE dept = \'eng\'` is '
                'not instructions, it is a description. Learning to think in '
                'those descriptions, in sets of rows rather than one row at a '
                'time, is the actual skill.\n\n'
                'This is the third data language in the roster and the contrast '
                'is the lesson. awk filters columns of text, jq filters trees '
                'of JSON, and SQL filters tables. The same instinct, "keep the '
                'rows that match and reshape what comes out", expressed three '
                'ways for three shapes of data.\n\n'
                'And it is not abstract. SQLite is a database that lives in a '
                'single file with no server, and you are surrounded by them: a '
                'browser keeps its history in one, a phone app keeps its state '
                'in one, endpoint tooling keeps its telemetry in one. Knowing '
                'SQL means those files stop being opaque and become something '
                'you can question.'
            ),
            'examples': [
                {
                    'label': 'A table, and a description of what you want',
                    'code': ('users\n'
                             '  id | name  | dept  | last_login\n'
                             '  ---+-------+-------+-----------\n'
                             '  1  | alice | eng   | 2026-08-01\n'
                             '  2  | bob   | sales | 2026-08-12\n'
                             '  3  | carol | eng   | 2026-07-30\n'
                             '\n'
                             "SELECT name FROM users WHERE dept = 'eng';\n"
                             '  -> alice, carol'),
                    'note': 'You described the rows (dept is eng) and the '
                            'column (name). You did not say how to find them.',
                },
            ],
            'misconceptions': [
                'SQL is not a loop. You do not iterate rows; you describe the '
                'set you want and the engine plans the work.',
                'SQLite is not a lesser database for beginners. It is the most '
                'widely deployed one there is, and the SQL transfers to '
                'Postgres and MySQL almost unchanged.',
                'A database is not a spreadsheet. The rules, one type per '
                'column and a key per row, are what make queries reliable.',
            ],
            'try_it': [
                'Find a `.sqlite` file on your machine (a browser profile is '
                'the easy one) and just note that it exists. You will query it '
                'by the end of this module.',
            ],
        },
        {
            'id': 'sq-sqlite',
            'title': 'Getting data in and out with sqlite3',
            'next': 'sq-select',
            'concept': (
                'The `sqlite3` command is your way into a database file, and it '
                'has two kinds of input: SQL statements, which end in a '
                'semicolon, and dot-commands, which control the tool itself and '
                'do not. Confusing the two is the first stumble: `.tables` '
                'lists tables and takes no semicolon, `SELECT ...;` runs a '
                'query and needs one.\n\n'
                '`sqlite3 mydata.db` opens (or creates) the file and drops you '
                'at a prompt. `.tables` shows what is in it, `.schema '
                'tablename` shows how a table is built, and `.quit` leaves. The '
                'dot-commands worth knowing early are the output ones: `.mode '
                'column` and `.headers on` make results readable, `.mode csv` '
                'produces CSV, and `.mode json` produces JSON you can hand to '
                'jq.\n\n'
                'For scripting, you do not need the prompt at all. `sqlite3 '
                'mydata.db "SELECT ..."` runs one query and exits, which is how '
                'SQL fits into a pipeline. `sqlite3 mydata.db < queries.sql` '
                'runs a whole file. And `.import --csv file.csv tablename` '
                'loads a CSV straight into a table, which is often how data '
                'gets in in the first place.\n\n'
                'One safety habit for forensics: open an evidence database '
                'read-only so you cannot change it. `sqlite3 -readonly '
                'evidence.db` or opening `file:evidence.db?mode=ro` does that, '
                'and it is the difference between examining an artifact and '
                'altering it.'
            ),
            'examples': [
                {
                    'label': 'At the prompt',
                    'code': ('sqlite3 app.db        open or create the file\n'
                             '.tables               list tables (no semicolon)\n'
                             '.schema users         how the table is built\n'
                             '.mode column          readable output\n'
                             '.headers on           show column names\n'
                             'SELECT * FROM users;  a query (needs semicolon)\n'
                             '.quit                 leave'),
                    'note': 'Dot-commands drive the tool and take no semicolon; '
                            'SQL statements end in one.',
                },
                {
                    'label': 'From the shell, for scripts',
                    'code': ('sqlite3 app.db "SELECT count(*) FROM users;"\n'
                             'sqlite3 app.db < report.sql\n'
                             'sqlite3 -csv app.db "SELECT * FROM users;" > u.csv\n'
                             'sqlite3 app.db ".import --csv data.csv events"\n'
                             'sqlite3 -readonly evidence.db "SELECT ..."'),
                    'note': 'One-shot queries and -readonly are how SQL joins a '
                            'pipeline and how you examine evidence safely.',
                },
            ],
            'misconceptions': [
                'A dot-command is not SQL and takes no semicolon. `.tables;` is '
                'an error, and `SELECT 1` without a semicolon just waits for '
                'more.',
                'Opening a database that does not exist does not fail. sqlite3 '
                'creates an empty one, which is why a typo in the filename '
                'gives you a blank database rather than an error.',
                'Reading a forensic database with the default mode can update '
                'its timestamps or a write-ahead log. Use -readonly on '
                'anything you must not alter.',
            ],
            'try_it': [
                'Run `sqlite3 test.db` and create a tiny table by hand, then '
                '`.tables`, `.schema`, and a `SELECT`, then `.quit` and note '
                'that test.db is now a real file.',
            ],
        },
        {
            'id': 'sq-select',
            'title': 'SELECT, WHERE, and ORDER BY',
            'next': 'sq-aggregate',
            'concept': (
                'Every query is the same shape, and once you have it the rest '
                'is vocabulary. `SELECT` names the columns you want, `FROM` '
                'names the table, `WHERE` filters the rows, `ORDER BY` sorts '
                'the result, and `LIMIT` caps how many come back. They are '
                'always written in that order, and `SELECT *` means every '
                'column.\n\n'
                'The `WHERE` clause is where the thinking is. Comparisons are '
                'the obvious `=`, `!=`, `<`, `>`, and note that string equality '
                'uses single quotes: `WHERE name = \'alice\'`. Beyond those, a '
                'few operators do most of the real work. `LIKE` matches a '
                'pattern where `%` is any run of characters, so `WHERE url LIKE '
                '\'%github%\'`. `IN (...)` matches any of a list. `BETWEEN a AND '
                'b` is an inclusive range. And `IS NULL` tests for a missing '
                'value, because a NULL is not equal to anything, not even '
                'itself, which is the single most surprising rule in SQL.\n\n'
                'Conditions combine with `AND`, `OR` and `NOT`, and parentheses '
                'group them exactly as you would expect. `ORDER BY col DESC` '
                'sorts high to low, and you can sort by several columns. '
                '`SELECT DISTINCT` removes duplicate rows from the result, '
                'which is how you answer "what are the distinct values here".'
            ),
            'examples': [
                {
                    'label': 'The shape, filled in',
                    'code': ('SELECT name, last_login\n'
                             'FROM users\n'
                             "WHERE dept = 'eng' AND last_login > '2026-07-31'\n"
                             'ORDER BY last_login DESC\n'
                             'LIMIT 10;'),
                    'note': 'Always SELECT, FROM, WHERE, ORDER BY, LIMIT, in '
                            'that order. Read it top to bottom as a sentence.',
                },
                {
                    'label': 'The operators that earn their keep',
                    'code': ("WHERE url LIKE '%login%'      pattern, % is any\n"
                             "WHERE status IN (301, 302)    any of a list\n"
                             'WHERE ts BETWEEN 100 AND 200  inclusive range\n'
                             'WHERE referrer IS NULL        a missing value\n'
                             'SELECT DISTINCT dept          unique values'),
                    'note': 'NULL is not equal to anything, so test it with IS '
                            'NULL, never with = NULL.',
                },
            ],
            'misconceptions': [
                'String literals use single quotes. Double quotes mean a column '
                'name in standard SQL, so `WHERE name = "alice"` may silently '
                'compare a column to itself.',
                '`= NULL` never matches, because NULL is not equal to anything. '
                'Use `IS NULL` and `IS NOT NULL`.',
                '`LIKE` uses `%` and `_` as wildcards, not the shell\'s `*` and '
                '`?`. `LIKE \'*.log\'` matches a literal asterisk.',
            ],
            'try_it': [
                'On a table with a text column, write a query with a `LIKE` '
                'filter and an `ORDER BY ... DESC`, then add a `LIMIT`.',
            ],
        },
        {
            'id': 'sq-aggregate',
            'title': 'Counting and grouping',
            'next': 'sq-join',
            'concept': (
                'A great many real questions are "how many" and "how much per", '
                'and those are aggregates. The aggregate functions collapse '
                'many rows into one number: `COUNT(*)` counts rows, `SUM(col)` '
                'adds a column, `AVG`, `MIN` and `MAX` do what they say. On '
                'their own they turn a whole table into a single row.\n\n'
                '`GROUP BY` is what makes them powerful. It splits the rows '
                'into groups that share a value and applies the aggregate to '
                'each group, so `SELECT dept, COUNT(*) FROM users GROUP BY '
                'dept` gives one row per department with its head count. This '
                'is exactly the "count by key" idiom you met in awk and jq, and '
                'it is cleaner here because the language was built for it.\n\n'
                'The rule that trips everyone is filtering. `WHERE` filters '
                'rows **before** they are grouped; `HAVING` filters groups '
                '**after** they are aggregated. So "departments with more than '
                'five people" is a `HAVING COUNT(*) > 5`, because the count '
                'does not exist until the grouping has happened. Trying to put '
                'that in a `WHERE` is the classic beginner error.\n\n'
                'One more piece completes the shape: any column you `SELECT` '
                'alongside an aggregate must either be in the `GROUP BY` or be '
                'inside an aggregate itself, because otherwise the database '
                'would not know which row of the group to show.'
            ),
            'examples': [
                {
                    'label': 'Count by key, and filter the groups',
                    'code': ('SELECT dept, COUNT(*) AS n\n'
                             'FROM users\n'
                             "WHERE last_login > '2026-01-01'\n"
                             'GROUP BY dept\n'
                             'HAVING n > 5\n'
                             'ORDER BY n DESC;'),
                    'note': 'WHERE filters rows before grouping; HAVING filters '
                            'groups after. The order of clauses reflects that.',
                },
                {
                    'label': 'The aggregates',
                    'code': ('COUNT(*)          how many rows\n'
                             'COUNT(DISTINCT x) how many distinct values\n'
                             'SUM(bytes)        total\n'
                             'AVG(duration)     mean\n'
                             'MIN(ts), MAX(ts)  earliest and latest'),
                    'note': 'AS gives the computed column a name, which HAVING '
                            'and ORDER BY can then refer to.',
                },
            ],
            'misconceptions': [
                'A count of groups goes in `HAVING`, not `WHERE`. The count '
                'does not exist until after grouping, so `WHERE COUNT(*) > 5` '
                'is an error.',
                'A `SELECT` column next to an aggregate must be in the '
                '`GROUP BY`, or the result is ambiguous and, in stricter '
                'databases, an error.',
                'COUNT(*) counts rows including NULLs; COUNT(column) skips '
                'rows where that column is NULL, which is occasionally the bug.',
            ],
            'try_it': [
                'On any table, write a `GROUP BY` that counts rows per '
                'category, then add a `HAVING` to keep only the busy '
                'categories.',
            ],
        },
        {
            'id': 'sq-join',
            'title': 'Joining tables',
            'next': 'sq-subquery',
            'concept': (
                'Data is split across tables on purpose. Instead of repeating a '
                'user\'s name on every one of their thousand log rows, you '
                'store users in one table and events in another, and the event '
                'row carries just a user id. That is normalization, and it '
                'keeps the data small and consistent. The cost is that '
                'answering a real question means putting the tables back '
                'together, which is a **join**.\n\n'
                'A join matches rows from two tables on a condition, almost '
                'always a key. `SELECT e.ts, u.name FROM events e JOIN users u '
                'ON e.user_id = u.id` reads each event and attaches the '
                'matching user\'s name. The `ON` clause is how it knows which '
                'rows go together, and the short table aliases (`e`, `u`) keep '
                'the column references clear.\n\n'
                'The kind of join decides what happens to rows with no match. '
                'An `INNER JOIN`, the default, keeps only rows that match on '
                'both sides. A `LEFT JOIN` keeps every row from the left table '
                'and fills the right side with NULL where there is no match, '
                'which is how you find the gaps: "users who have never logged '
                'an event" is a `LEFT JOIN` with a `WHERE e.id IS NULL`.\n\n'
                'The danger to respect is forgetting the `ON`. A join with no '
                'condition pairs every row with every row, a cross product, and '
                'on two thousand-row tables that is a million rows. If a query '
                'suddenly returns far too much, a missing or wrong `ON` is the '
                'first thing to check.'
            ),
            'examples': [
                {
                    'label': 'Matching rows across tables',
                    'code': ('SELECT e.ts, u.name, e.action\n'
                             'FROM events e\n'
                             'JOIN users u ON e.user_id = u.id\n'
                             "WHERE u.dept = 'eng'\n"
                             'ORDER BY e.ts;'),
                    'note': 'The ON says which rows pair up. Aliases e and u '
                            'keep the column names unambiguous.',
                },
                {
                    'label': 'Finding the gaps with LEFT JOIN',
                    'code': ('SELECT u.name\n'
                             'FROM users u\n'
                             'LEFT JOIN events e ON e.user_id = u.id\n'
                             'WHERE e.id IS NULL;\n'
                             '  -> users who never did anything'),
                    'note': 'LEFT JOIN keeps every user; the NULL on the right '
                            'is exactly the ones with no matching event.',
                },
            ],
            'misconceptions': [
                'A join with no `ON` is a cross product: every row paired with '
                'every row. A query returning millions of rows usually has a '
                'missing join condition.',
                'INNER JOIN drops rows that do not match on both sides, so a '
                'join can silently lose data. LEFT JOIN keeps the left side and '
                'shows the gaps.',
                'Column names that exist in both tables must be qualified, like '
                '`u.id` and `e.id`, or the query is ambiguous.',
            ],
            'try_it': [
                'With two related tables, write an INNER JOIN, then change it '
                'to a LEFT JOIN and add `WHERE ... IS NULL` to find the '
                'unmatched rows.',
            ],
        },
        {
            'id': 'sq-subquery',
            'title': 'Subqueries and common table expressions',
            'next': 'sq-mutate',
            'concept': (
                'A subquery is a query used inside another query, and it is how '
                'you answer a question whose answer depends on another '
                'question. The commonest form feeds a list into an `IN`: '
                '`SELECT * FROM events WHERE user_id IN (SELECT id FROM users '
                'WHERE dept = \'eng\')` reads as "events by anyone in '
                'engineering", where the inner query supplies the list of '
                'ids.\n\n'
                'Subqueries also work as a single value (`WHERE ts > (SELECT '
                'AVG(ts) FROM events)`, everything later than average) and as a '
                'derived table you select from. They are powerful and they get '
                'unreadable quickly when nested, which is what the next tool '
                'fixes.\n\n'
                'A **common table expression**, or CTE, is a subquery given a '
                'name at the top of the query with `WITH`. `WITH eng AS '
                '(SELECT id FROM users WHERE dept = \'eng\') SELECT * FROM '
                'events WHERE user_id IN (SELECT id FROM eng)` does the same '
                'thing but reads top to bottom, and you can define several and '
                'build on them. For anything beyond a trivial subquery, a CTE '
                'is the difference between a query you can read next month and '
                'one you rewrite from scratch.\n\n'
                'The habit worth forming is to reach for a CTE the moment a '
                'query has more than one idea in it. Named steps beat nested '
                'parentheses every time.'
            ),
            'examples': [
                {
                    'label': 'A subquery feeding an IN',
                    'code': ('SELECT ts, action FROM events\n'
                             'WHERE user_id IN (\n'
                             "  SELECT id FROM users WHERE dept = 'eng'\n"
                             ');'),
                    'note': 'The inner query produces a list of ids; the outer '
                            'one keeps events whose user is in that list.',
                },
                {
                    'label': 'The same thing, readable, as a CTE',
                    'code': ('WITH eng AS (\n'
                             "  SELECT id FROM users WHERE dept = 'eng'\n"
                             ')\n'
                             'SELECT ts, action FROM events\n'
                             'WHERE user_id IN (SELECT id FROM eng);'),
                    'note': 'WITH names a step. Several CTEs stack, and the '
                            'query reads top to bottom instead of inside out.',
                },
            ],
            'misconceptions': [
                'A subquery that returns more than one row cannot be used where '
                'a single value is expected. Use `IN` for a list, `=` only for '
                'a scalar subquery.',
                'A CTE is not slower than a subquery in sqlite; it is the same '
                'query, named. Reach for it for readability without a '
                'performance worry.',
                'A correlated subquery, one that refers to the outer row, runs '
                'once per outer row and can be slow. A join is often the '
                'faster shape.',
            ],
            'try_it': [
                'Write a query with a subquery in an `IN`, then rewrite it as a '
                'CTE with `WITH` and decide which you would rather read.',
            ],
        },
        {
            'id': 'sq-mutate',
            'title': 'Changing data, and transactions',
            'next': 'sq-schema',
            'concept': (
                'Reading is most of what you do, but you will create and change '
                'data too, and the write statements are the sharp tools in the '
                'drawer. `INSERT INTO t (a, b) VALUES (1, 2)` adds a row. '
                '`UPDATE t SET a = 5 WHERE id = 3` changes existing rows. '
                '`DELETE FROM t WHERE id = 3` removes them. `CREATE TABLE` and '
                '`DROP TABLE` make and destroy tables.\n\n'
                'The rule that saves you is the same one `rm` teaches: the '
                '`WHERE` is not optional in practice. `UPDATE t SET status = '
                '\'done\'` with no `WHERE` sets every row in the table, and '
                '`DELETE FROM t` empties it. There is no undo once it is '
                'committed. The habit is to write the `WHERE` first, or to run '
                'the same condition as a `SELECT` to see exactly which rows you '
                'are about to change, before turning it into an `UPDATE`.\n\n'
                'Transactions are the real safety net. `BEGIN` starts one, and '
                'nothing you do is permanent until `COMMIT`. If it looks wrong, '
                '`ROLLBACK` undoes everything since the `BEGIN` as though it '
                'never happened. Wrapping a risky change in a transaction means '
                'you can look before you leap: run the update, `SELECT` to '
                'check it, and only then commit. Transactions also make a group '
                'of changes atomic, so either all of them happen or none do, '
                'which is what keeps data consistent when something fails '
                'halfway.'
            ),
            'examples': [
                {
                    'label': 'The write statements',
                    'code': ("INSERT INTO users (name, dept) VALUES ('dan', 'eng');\n"
                             "UPDATE users SET dept = 'ops' WHERE name = 'dan';\n"
                             "DELETE FROM users WHERE name = 'dan';\n"
                             'CREATE TABLE notes (id INTEGER PRIMARY KEY, body TEXT);'),
                    'note': 'Every UPDATE and DELETE needs a WHERE, or it acts '
                            'on the whole table with no undo.',
                },
                {
                    'label': 'Look before you leap',
                    'code': ('BEGIN;\n'
                             "UPDATE accounts SET balance = balance - 10 "
                             "WHERE id = 1;\n"
                             'SELECT * FROM accounts WHERE id = 1;   -- check\n'
                             'COMMIT;    -- or ROLLBACK to undo it all'),
                    'note': 'Between BEGIN and COMMIT nothing is permanent, so '
                            'you can verify the change and back out if wrong.',
                },
            ],
            'misconceptions': [
                'An `UPDATE` or `DELETE` with no `WHERE` hits every row, and '
                'once committed there is no undo. Write the `WHERE` first.',
                'Changes are not necessarily saved the instant you type them, '
                'but by default sqlite auto-commits each statement. Use `BEGIN` '
                'to take control and gain `ROLLBACK`.',
                'A transaction is not just for safety. It also makes several '
                'statements atomic, so a failure halfway does not leave the '
                'data half-changed.',
            ],
            'try_it': [
                'In a scratch database, `BEGIN`, `DELETE` some rows, `SELECT` '
                'to see them gone, then `ROLLBACK` and confirm they are back.',
            ],
        },
        {
            'id': 'sq-schema',
            'title': 'Schema, types, indexes, and reading a real database',
            'concept': (
                'To read a database you did not build, start with its shape. '
                '`.tables` lists the tables and `.schema` prints the '
                '`CREATE TABLE` statements, which tell you the columns, their '
                'types, the primary keys and the foreign keys that connect '
                'tables. That schema is the map, and reading it first saves '
                'guessing.\n\n'
                'SQLite has one genuine oddity worth knowing: its typing is '
                'dynamic. A column has a declared type, but SQLite will store '
                'text in an integer column if you tell it to, and it treats '
                'several type names as the same underlying kind. In practice '
                'this rarely bites, but it explains why a value that "should" '
                'be a number sometimes sorts like text. When it matters, '
                '`CAST(x AS INTEGER)` forces the issue.\n\n'
                'Performance comes down to indexes. A query with a `WHERE` on '
                'an unindexed column has to read every row to find the matches, '
                'a full scan, which is fine on a thousand rows and painful on '
                'ten million. `CREATE INDEX idx ON events(user_id)` builds a '
                'lookup structure so that filtering or joining on that column '
                'is fast. `EXPLAIN QUERY PLAN` in front of any query tells you '
                'whether it is scanning or using an index, which is how you '
                'find out why a query is slow rather than guessing.\n\n'
                'Put it together on something real. A browser keeps its history '
                'in a SQLite file with a `urls` table and a `visits` table; a '
                'single join and a timestamp conversion turns it into a '
                'readable browsing timeline. That query, run read-only on a '
                'copy, is a genuine forensic technique, and it is only the '
                'ordinary SELECT, JOIN and ORDER BY from the lessons before.'
            ),
            'examples': [
                {
                    'label': 'Read the shape, then index for speed',
                    'code': ('.schema urls              how the table is built\n'
                             '.indexes urls             what is already indexed\n'
                             'CREATE INDEX i_visit_url\n'
                             '  ON visits(url_id);       make a join fast\n'
                             'EXPLAIN QUERY PLAN\n'
                             '  SELECT ...;              scan, or use an index?'),
                    'note': 'A WHERE or JOIN on an unindexed column scans every '
                            'row. EXPLAIN QUERY PLAN tells you which is '
                            'happening.',
                },
                {
                    'label': 'A browser history, as an ordinary query',
                    'code': ('SELECT datetime(v.visit_time, ...) AS when,\n'
                             '       u.url\n'
                             'FROM visits v\n'
                             'JOIN urls u ON u.id = v.url_id\n'
                             'ORDER BY v.visit_time DESC\n'
                             'LIMIT 50;'),
                    'note': 'Just SELECT, JOIN, ORDER BY and a timestamp '
                            'conversion. The forensic part is the read-only '
                            'copy, not the SQL.',
                },
            ],
            'misconceptions': [
                'SQLite typing is dynamic, so a number stored as text sorts as '
                'text. `CAST(x AS INTEGER)` fixes a value that sorts or '
                'compares wrongly.',
                'An index is not free. It speeds up reads on that column and '
                'slightly slows writes, so you index the columns you filter and '
                'join on, not every column.',
                'A slow query is a question with an answer. `EXPLAIN QUERY '
                'PLAN` shows whether it scans the table or uses an index, so '
                'you fix the cause rather than guess.',
            ],
            'try_it': [
                'Copy a browser history database, open it `-readonly`, read its '
                '`.schema`, and write a join that lists your recent URLs with '
                'their visit times.',
            ],
        },
    ],

    'drills': [
        # the sqlite3 tool
        {'id': 'sqd-open', 'type': 'command', 'answer': 'sqlite3 app.db',
         'prompt': 'Open (or create) the database file app.db at a prompt.',
         'teach': 'If the file does not exist, sqlite3 creates an empty one, '
                  'which is why a typo gives you a blank database.'},
        {'id': 'sqd-tables', 'type': 'command', 'answer': '.tables',
         'prompt': 'List the tables in the open database.',
         'teach': 'A dot-command drives the tool and takes no semicolon, '
                  'unlike a SQL statement.'},
        {'id': 'sqd-schema', 'type': 'command', 'answer': '.schema users',
         'prompt': 'Show how the users table is built.',
         'teach': 'The schema is the map: columns, types, keys. Read it first '
                  'on a database you did not make.'},
        {'id': 'sqd-mode', 'type': 'command', 'answer': '.mode column',
         'prompt': 'Switch output to readable aligned columns.',
         'teach': '.headers on adds the column names. .mode csv and .mode json '
                  'are the machine-readable forms.'},
        {'id': 'sqd-oneshot', 'type': 'command',
         'answer': 'sqlite3 app.db "SELECT count(*) FROM users;"',
         'prompt': 'From the shell, count the rows in users without opening a '
                   'prompt.',
         'teach': 'A one-shot query runs and exits, which is how SQL joins a '
                  'shell pipeline.'},
        {'id': 'sqd-import', 'type': 'command',
         'answer': 'sqlite3 app.db ".import --csv data.csv events"',
         'prompt': 'Load data.csv into a table called events.',
         'teach': 'This is how data usually gets in. The first row becomes '
                  'column names with --csv on a headered file.'},
        {'id': 'sqd-readonly', 'type': 'command',
         'answer': 'sqlite3 -readonly evidence.db "SELECT * FROM urls;"',
         'prompt': 'Query evidence.db without any chance of altering it.',
         'teach': 'Read-only is the forensic habit: examine an artifact '
                  'without touching its timestamps or write-ahead log.'},

        # SELECT / WHERE / ORDER
        {'id': 'sqd-select-all', 'type': 'command',
         'answer': 'SELECT * FROM users;',
         'prompt': 'Select every column of every row in users.',
         'teach': 'A star means all columns. Every SQL statement ends in a '
                  'semicolon.'},
        {'id': 'sqd-select-cols', 'type': 'command',
         'answer': 'SELECT name, dept FROM users;',
         'prompt': 'Select just the name and dept columns from users.',
         'teach': 'Naming columns rather than * keeps output readable and '
                  'makes intent clear.'},
        {'id': 'sqd-where', 'type': 'command',
         'answer': "SELECT name FROM users WHERE dept = 'eng';",
         'prompt': 'Select the names of users whose dept is eng.',
         'teach': 'String literals use single quotes. Double quotes mean a '
                  'column name in standard SQL.'},
        {'id': 'sqd-like', 'type': 'command',
         'answer': "SELECT url FROM history WHERE url LIKE '%login%';",
         'prompt': 'Select URLs from history that contain the text login.',
         'teach': 'In LIKE, % is any run of characters and _ is one. It is not '
                  'the shell glob.'},
        {'id': 'sqd-in', 'type': 'command',
         'answer': 'SELECT * FROM events WHERE status IN (301, 302, 307);',
         'prompt': 'Select events whose status is any of 301, 302 or 307.',
         'teach': 'IN matches any value in the list, cleaner than a stack of '
                  'ORs.'},
        {'id': 'sqd-null', 'type': 'command',
         'answer': 'SELECT * FROM events WHERE referrer IS NULL;',
         'prompt': 'Select events that have no referrer.',
         'teach': 'NULL is not equal to anything, so test it with IS NULL, '
                  'never = NULL.'},
        {'id': 'sqd-order', 'type': 'command',
         'answer': 'SELECT * FROM users ORDER BY last_login DESC;',
         'prompt': 'Select all users, newest login first.',
         'teach': 'DESC sorts high to low. You can order by several columns.'},
        {'id': 'sqd-distinct', 'type': 'command',
         'answer': 'SELECT DISTINCT dept FROM users;',
         'prompt': 'List the distinct departments in users.',
         'teach': 'DISTINCT removes duplicate rows from the result.'},
        {'id': 'sqd-limit', 'type': 'command',
         'answer': 'SELECT * FROM events ORDER BY ts DESC LIMIT 10;',
         'prompt': 'Select the ten most recent events.',
         'teach': 'LIMIT caps the rows returned, and pairs with ORDER BY to '
                  'mean "top ten".'},

        # aggregates
        {'id': 'sqd-count', 'type': 'command',
         'answer': 'SELECT COUNT(*) FROM users;',
         'prompt': 'Count how many rows are in users.',
         'teach': 'COUNT(*) counts rows including NULLs; COUNT(col) skips rows '
                  'where col is NULL.'},
        {'id': 'sqd-groupby', 'type': 'command',
         'answer': 'SELECT dept, COUNT(*) FROM users GROUP BY dept;',
         'prompt': 'Count users per department.',
         'teach': 'The count-by-key idiom, and cleaner here than in awk or jq '
                  'because SQL was built for it.'},
        {'id': 'sqd-having', 'type': 'command',
         'answer': 'SELECT dept, COUNT(*) AS n FROM users GROUP BY dept '
                   'HAVING n > 5;',
         'prompt': 'Show only departments with more than five users.',
         'teach': 'HAVING filters groups after aggregation; WHERE filters rows '
                  'before it. The count does not exist until grouping.'},
        {'id': 'sqd-sum', 'type': 'command',
         'answer': 'SELECT user_id, SUM(bytes) FROM events GROUP BY user_id;',
         'prompt': 'Total the bytes column per user.',
         'teach': 'SUM, AVG, MIN and MAX collapse each group to one number.'},

        # joins
        {'id': 'sqd-join', 'type': 'command',
         'answer': 'SELECT e.ts, u.name FROM events e JOIN users u '
                   'ON e.user_id = u.id;',
         'prompt': 'List each event time alongside the name of the user who '
                   'caused it.',
         'teach': 'The ON says which rows pair up. Aliases keep the column '
                  'references unambiguous.'},
        {'id': 'sqd-leftjoin', 'type': 'command',
         'answer': 'SELECT u.name FROM users u LEFT JOIN events e '
                   'ON e.user_id = u.id WHERE e.id IS NULL;',
         'prompt': 'Find users who have never caused an event.',
         'teach': 'LEFT JOIN keeps every user; the NULL on the right is exactly '
                  'the ones with no match.'},

        # subqueries and CTEs
        {'id': 'sqd-subquery', 'type': 'command',
         'answer': "SELECT * FROM events WHERE user_id IN "
                   "(SELECT id FROM users WHERE dept = 'eng');",
         'prompt': 'Select events caused by anyone in the eng department, '
                   'using a subquery.',
         'teach': 'The inner query supplies the list of ids the outer IN '
                  'matches against.'},
        {'id': 'sqd-cte', 'type': 'command',
         'answer': "WITH eng AS (SELECT id FROM users WHERE dept = 'eng') "
                   "SELECT * FROM events WHERE user_id IN (SELECT id FROM eng);",
         'prompt': 'Rewrite the eng-events subquery to name the inner part '
                   'with a CTE.',
         'teach': 'WITH names a step so the query reads top to bottom rather '
                  'than inside out.'},

        # mutation and schema
        {'id': 'sqd-insert', 'type': 'command',
         'answer': "INSERT INTO users (name, dept) VALUES ('dan', 'eng');",
         'prompt': 'Add a user dan in the eng department.',
         'teach': 'Name the columns you set; the rest take their defaults or '
                  'NULL.'},
        {'id': 'sqd-update', 'type': 'command',
         'answer': "UPDATE users SET dept = 'ops' WHERE name = 'dan';",
         'prompt': 'Move the user dan into the ops department.',
         'teach': 'The WHERE is not optional in practice: without it, every '
                  'row changes and there is no undo.'},
        {'id': 'sqd-delete', 'type': 'command',
         'answer': "DELETE FROM users WHERE name = 'dan';",
         'prompt': 'Remove the user dan.',
         'teach': 'DELETE FROM users with no WHERE empties the table. Write the '
                  'WHERE first.'},
        {'id': 'sqd-begin', 'type': 'command',
         'answer': 'BEGIN;',
         'prompt': 'Start a transaction so you can undo the next changes.',
         'teach': 'Nothing is permanent until COMMIT; ROLLBACK undoes '
                  'everything since BEGIN.'},
        {'id': 'sqd-createtable', 'type': 'command',
         'answer': 'CREATE TABLE notes (id INTEGER PRIMARY KEY, body TEXT);',
         'prompt': 'Create a notes table with an integer primary key id and a '
                   'text body.',
         'teach': 'INTEGER PRIMARY KEY is the special rowid column and '
                  'auto-increments.'},
        {'id': 'sqd-index', 'type': 'command',
         'answer': 'CREATE INDEX idx_events_user ON events(user_id);',
         'prompt': 'Build an index so filtering events by user_id is fast.',
         'teach': 'A WHERE or JOIN on an unindexed column scans every row. An '
                  'index turns that scan into a lookup.'},
        {'id': 'sqd-explain', 'type': 'command',
         'answer': 'EXPLAIN QUERY PLAN SELECT * FROM events WHERE user_id = 5;',
         'prompt': 'Ask whether a query uses an index or scans the whole table.',
         'teach': 'The plan says SCAN or SEARCH. This is how you diagnose a '
                  'slow query rather than guessing.'},
    ],

    'challenges': [
        {
            'id': 'sqc-first-query',
            'title': 'Load a table and ask it a question',
            'goal': 'Create a database, put some rows in it, and answer a '
                    'filtered, sorted question from the shell.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {'.keep': ''}},
            'solution': {'shell':
                'sqlite3 app.db "CREATE TABLE users(id INTEGER PRIMARY KEY, '
                "name TEXT, dept TEXT, logins INTEGER); "
                "INSERT INTO users(name,dept,logins) VALUES "
                "('alice','eng',12),('bob','sales',3),('carol','eng',20),"
                "('dan','sales',7);\" && "
                'sqlite3 app.db "SELECT name FROM users WHERE dept=\'eng\' '
                'ORDER BY logins DESC;" > eng.txt && '
                'sqlite3 app.db "SELECT COUNT(*) FROM users;" > total.txt'},
            'steps': [
                {'instruction': 'Create app.db with a users table (id, name, '
                                'dept, logins) and insert four users.',
                 'hint': 'sqlite3 app.db "CREATE TABLE users(...); INSERT ..."'},
                {'instruction': 'Write the eng users, most logins first, to '
                                'eng.txt.',
                 'hint': "SELECT name FROM users WHERE dept='eng' ORDER BY "
                         'logins DESC'},
                {'instruction': 'Write the total user count to total.txt.'},
            ],
            'free': 'Produce eng.txt listing the engineering users sorted by '
                    'logins descending (carol before alice), and total.txt '
                    'holding 4.',
            'verify': {'kind': 'sandbox', 'expect': {
                'is_file': ['app.db'],
                'file_equals': {'eng.txt': 'carol\nalice', 'total.txt': '4'}}},
            'fallback': 'self',
        },
        {
            'id': 'sqc-import-group',
            'title': 'Import a CSV and count by key',
            'goal': 'Real data usually arrives as CSV. Load it, then answer a '
                    'group-and-count question.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'access.csv': 'ip,method,status\n'
                              '10.0.0.1,GET,200\n10.0.0.2,GET,404\n'
                              '10.0.0.1,POST,200\n10.0.0.3,GET,200\n'
                              '10.0.0.1,GET,500\n10.0.0.2,GET,200\n'}},
            'solution': {'shell':
                'sqlite3 log.db ".import --csv access.csv hits" && '
                'sqlite3 log.db "SELECT ip, COUNT(*) AS n FROM hits '
                'GROUP BY ip ORDER BY n DESC;" > byip.txt && '
                'sqlite3 log.db "SELECT COUNT(*) FROM hits WHERE status=\'200\';" '
                '> ok.txt'},
            'steps': [
                {'instruction': 'Import access.csv into a table called hits.',
                 'hint': 'sqlite3 log.db ".import --csv access.csv hits"'},
                {'instruction': 'Count hits per ip, busiest first, into '
                                'byip.txt.',
                 'hint': 'GROUP BY ip ORDER BY COUNT(*) DESC'},
                {'instruction': 'Count how many hits returned status 200, into '
                                'ok.txt.'},
            ],
            'free': 'Produce byip.txt with a count of hits per ip (10.0.0.1 '
                    'highest at 3) and ok.txt holding the number of 200s.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'byip.txt': ['10.0.0.1', '3'],
                                  'ok.txt': '4'}}},
            'fallback': 'self',
        },
        {
            'id': 'sqc-join',
            'title': 'Join two tables to answer a real question',
            'goal': 'Data split across tables has to be put back together. '
                    'Join events to users and filter on the user side.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'seed.sql':
                    'CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT, '
                    'dept TEXT);\n'
                    "INSERT INTO users VALUES (1,'alice','eng'),"
                    "(2,'bob','sales'),(3,'carol','eng'),(4,'dan','sales');\n"
                    'CREATE TABLE events(id INTEGER PRIMARY KEY, user_id '
                    'INTEGER, action TEXT);\n'
                    "INSERT INTO events VALUES (1,1,'login'),(2,2,'login'),"
                    "(3,1,'export'),(4,3,'login'),(5,1,'delete');\n"}},
            'solution': {'shell':
                'sqlite3 app.db < seed.sql && '
                'sqlite3 app.db "SELECT u.name, e.action FROM events e '
                'JOIN users u ON e.user_id=u.id WHERE u.dept=\'eng\' '
                'ORDER BY e.id;" > eng-actions.txt && '
                'sqlite3 app.db "SELECT u.name FROM users u LEFT JOIN events e '
                'ON e.user_id=u.id WHERE e.id IS NULL;" > idle.txt'},
            'steps': [
                {'instruction': 'Build the database from seed.sql. Four users, '
                                'one of whom (dan) causes no events.',
                 'hint': 'sqlite3 app.db < seed.sql'},
                {'instruction': 'List each eng user with each action they '
                                'took, into eng-actions.txt, using a JOIN.',
                 'hint': 'JOIN users u ON e.user_id = u.id WHERE u.dept=\'eng\''},
                {'instruction': 'Find any user who caused no events at all, '
                                'into idle.txt, using a LEFT JOIN.',
                 'hint': 'LEFT JOIN ... WHERE e.id IS NULL'},
            ],
            'free': 'Produce eng-actions.txt pairing eng users with their '
                    'actions (alice and carol, not bob), and idle.txt naming '
                    'the user with no events (dan).',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'eng-actions.txt': ['alice|login',
                                                      'carol|login',
                                                      'alice|delete']},
                'file_equals': {'idle.txt': 'dan'},
                'file_lacks': {'eng-actions.txt': 'bob'}}},
            'fallback': 'self',
        },
        {
            'id': 'sqc-cte',
            'title': 'Name the steps with a CTE',
            'goal': 'A two-idea question, written once as a nested subquery '
                    'and once as a readable CTE, both giving the same answer.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'seed.sql':
                    'CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT, '
                    'dept TEXT);\n'
                    "INSERT INTO users VALUES (1,'alice','eng'),"
                    "(2,'bob','sales'),(3,'carol','eng'),(4,'dan','eng');\n"
                    'CREATE TABLE events(id INTEGER PRIMARY KEY, user_id '
                    'INTEGER);\n'
                    'INSERT INTO events VALUES (1,1),(2,1),(3,3),(4,2),(5,1),'
                    '(6,4),(7,4);\n'}},
            'solution': {'shell':
                'sqlite3 app.db < seed.sql && '
                'sqlite3 app.db "WITH eng AS (SELECT id FROM users WHERE '
                'dept=\'eng\') SELECT COUNT(*) FROM events WHERE user_id IN '
                '(SELECT id FROM eng);" > eng-events.txt && '
                'sqlite3 app.db "SELECT u.name, COUNT(e.id) AS n FROM users u '
                'JOIN events e ON e.user_id=u.id GROUP BY u.id '
                'HAVING n >= 2 ORDER BY n DESC;" > busy.txt'},
            'steps': [
                {'instruction': 'Build the database from seed.sql.',
                 'hint': 'sqlite3 app.db < seed.sql'},
                {'instruction': 'Using a CTE named eng, count how many events '
                                'were caused by eng users, into '
                                'eng-events.txt.',
                 'hint': "WITH eng AS (SELECT id FROM users WHERE dept='eng')"},
                {'instruction': 'List users with at least two events, busiest '
                                'first, into busy.txt.',
                 'hint': 'GROUP BY u.id HAVING COUNT(e.id) >= 2'},
            ],
            'free': 'Produce eng-events.txt holding the count of events by eng '
                    'users (6), and busy.txt listing users with two or more '
                    'events, most first.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_equals': {'eng-events.txt': '6'},
                'file_contains': {'busy.txt': ['alice', 'dan']},
                'file_lacks': {'busy.txt': 'carol'}}},
            'fallback': 'self',
        },
        {
            'id': 'sqc-transaction',
            'title': 'Change data safely inside a transaction',
            'goal': 'Make a risky change, verify it, and prove a rollback '
                    'really undoes everything.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'seed.sql':
                    'CREATE TABLE accounts(id INTEGER PRIMARY KEY, owner TEXT, '
                    'balance INTEGER);\n'
                    "INSERT INTO accounts VALUES (1,'a',100),(2,'b',50);\n"}},
            'solution': {'shell':
                'sqlite3 app.db < seed.sql && '
                # a committed transfer
                'sqlite3 app.db "BEGIN; UPDATE accounts SET balance=balance-30 '
                'WHERE id=1; UPDATE accounts SET balance=balance+30 WHERE id=2; '
                'COMMIT;" && '
                'sqlite3 app.db "SELECT balance FROM accounts ORDER BY id;" '
                '> after-commit.txt && '
                # a rolled-back mistake
                'sqlite3 app.db "BEGIN; UPDATE accounts SET balance=0; '
                'ROLLBACK;" && '
                'sqlite3 app.db "SELECT balance FROM accounts ORDER BY id;" '
                '> after-rollback.txt'},
            'steps': [
                {'instruction': 'Build the accounts database from seed.sql.'},
                {'instruction': 'In one transaction, move 30 from account 1 to '
                                'account 2 and commit it. Record the balances '
                                'in after-commit.txt.',
                 'hint': 'BEGIN; UPDATE ...; UPDATE ...; COMMIT;'},
                {'instruction': 'Now begin a transaction that zeroes every '
                                'balance, then ROLLBACK it, and record the '
                                'balances again in after-rollback.txt.',
                 'hint': 'BEGIN; UPDATE accounts SET balance=0; ROLLBACK;'},
                {'instruction': 'The rollback should leave the committed '
                                'balances untouched.'},
            ],
            'free': 'Produce after-commit.txt showing 70 and 80, and '
                    'after-rollback.txt still showing 70 and 80 because the '
                    'zeroing was rolled back.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_equals': {'after-commit.txt': '70\n80',
                                'after-rollback.txt': '70\n80'}}},
            'fallback': 'self',
        },
        {
            'id': 'sqc-index',
            'title': 'Prove an index changes the query plan',
            'goal': 'Build a table, see it get scanned, add an index, and see '
                    'the plan switch to a search.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {'.keep': ''}},
            'solution': {'shell':
                'sqlite3 app.db "CREATE TABLE events(id INTEGER PRIMARY KEY, '
                'user_id INTEGER, action TEXT);" && '
                # a recursive CTE fills the table without any shell quoting
                'sqlite3 app.db "WITH RECURSIVE c(x) AS (SELECT 1 UNION ALL '
                'SELECT x+1 FROM c WHERE x<2000) INSERT INTO '
                'events(user_id,action) SELECT x%50, \'x\' FROM c;" && '
                'sqlite3 app.db "EXPLAIN QUERY PLAN SELECT * FROM events '
                'WHERE user_id=7;" > before.txt && '
                'sqlite3 app.db "CREATE INDEX idx_user ON events(user_id);" && '
                'sqlite3 app.db "EXPLAIN QUERY PLAN SELECT * FROM events '
                'WHERE user_id=7;" > after.txt'},
            'steps': [
                {'instruction': 'Create an events table and fill it with a '
                                'couple of thousand rows. A recursive CTE is '
                                'the neat way to generate them.',
                 'hint': 'WITH RECURSIVE c(x) AS (SELECT 1 UNION ALL SELECT '
                         'x+1 FROM c WHERE x<2000) INSERT INTO events ... '
                         'SELECT x%50, \'x\' FROM c'},
                {'instruction': 'Record the query plan for a filter on '
                                'user_id, before any index, into before.txt.',
                 'hint': 'EXPLAIN QUERY PLAN SELECT * FROM events WHERE '
                         'user_id=7'},
                {'instruction': 'Create an index on user_id, then record the '
                                'plan again into after.txt.',
                 'hint': 'CREATE INDEX idx_user ON events(user_id)'},
                {'instruction': 'before.txt should say SCAN; after.txt should '
                                'say SEARCH using the index.'},
            ],
            'free': 'Produce before.txt showing a full table SCAN and '
                    'after.txt showing a SEARCH that uses the index on '
                    'user_id.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'before.txt': 'SCAN',
                                  'after.txt': ['SEARCH', 'idx_user']}}},
            'fallback': 'self',
        },
        {
            'id': 'sqc-real-artifact',
            'title': 'Query a database you did not build',
            'goal': 'The sandbox databases were yours. This is a real artifact '
                    'on your own machine, read the way a forensic examiner '
                    'would.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'Find a SQLite artifact you own: a browser '
                                'history (Firefox places.sqlite, Chrome '
                                'History), a note app, anything.'},
                {'instruction': 'Copy it first, and open the copy read-only so '
                                'you cannot alter the evidence.',
                 'hint': 'cp History /tmp/h.db; sqlite3 -readonly /tmp/h.db'},
                {'instruction': 'Read its .schema and find the tables that '
                                'hold the interesting data.'},
                {'instruction': 'Write a join across two of its tables and '
                                'order by a timestamp to build a readable '
                                'timeline.'},
                {'instruction': 'Note that this was only SELECT, JOIN and '
                                'ORDER BY. The forensic part was the read-only '
                                'copy, not the SQL.'},
            ],
            'free': 'On your own machine: copy a real SQLite artifact, open '
                    'the copy read-only, read its schema, and join two of its '
                    'tables into a timeline.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
    ],

    'quiz': [
        {'id': 'sqq-declarative', 'type': 'mcq',
         'prompt': 'What does it mean that SQL is declarative?',
         'answer': 'You describe the rows you want; the engine decides how to '
                   'find them.',
         'distractors': ['You must declare every variable before using it.',
                         'You write the loop that walks the rows yourself.',
                         'The schema must be declared before any query runs.'],
         'teach': 'The shift from "how do I iterate" to "what do I want" is the '
                  'whole reason SQL changes how you think.'},
        {'id': 'sqq-dot', 'type': 'mcq',
         'prompt': 'You type `SELECT 1` and press Enter. Why is there no result?',
         'answer': 'A SQL statement needs a semicolon, so sqlite3 is still '
                   'waiting for the rest of it.',
         'distractors': ['SELECT needs a FROM clause to run at all.',
                         'The database has no tables yet.',
                         'Bare values have to be printed with .print.'],
         'teach': 'Dot-commands control the tool and need no semicolon; SQL '
                  'statements end in one. Forget it and you sit at a '
                  'continuation prompt wondering what broke.'},
        {'id': 'sqq-null', 'type': 'mcq',
         'prompt': 'Why does `WHERE referrer = NULL` never match anything?',
         'answer': 'NULL is not equal to anything, not even itself; use IS '
                   'NULL.',
         'distractors': ['NULL means the column does not exist.',
                         'The referrer column is indexed.',
                         'NULL only works in an ORDER BY.'],
         'teach': 'This is the single most surprising rule in SQL. Test a '
                  'missing value with IS NULL and IS NOT NULL.'},
        {'id': 'sqq-havingwhere', 'type': 'mcq',
         'prompt': 'You want departments with more than five people. Where '
                   'does `COUNT(*) > 5` go?',
         'answer': 'In HAVING, because the count exists only after grouping.',
         'distractors': ['In WHERE, like any other condition.',
                         'In the SELECT list.',
                         'In ORDER BY.'],
         'teach': 'WHERE filters rows before grouping; HAVING filters groups '
                  'after aggregation.'},
        {'id': 'sqq-quotes', 'type': 'mcq',
         'prompt': 'Why can double quotes round a value go wrong in SQL?',
         'answer': 'Double quotes mean an identifier, so the value is read as '
                   'a column name rather than as text.',
         'distractors': ['Nothing; single and double quotes are the same.',
                         'It is a syntax error every time.',
                         'It matches case-insensitively.'],
         'teach': 'String literals use single quotes. Modern sqlite catches the '
                  'usual case and even suggests single quotes, but `WHERE name '
                  '= "name"` is a column compared to itself, which quietly '
                  'matches every row.'},
        {'id': 'sqq-crossjoin', 'type': 'mcq',
         'prompt': 'A join suddenly returns a million rows from two '
                   'thousand-row tables. What is the likely cause?',
         'answer': 'A missing or wrong ON, so every row paired with every row.',
         'distractors': ['The tables are corrupt.',
                         'An index is missing.',
                         'LEFT JOIN was used instead of INNER JOIN.'],
         'teach': 'A join with no condition is a cross product. It is the first '
                  'thing to check when a result explodes.'},
        {'id': 'sqq-leftjoin', 'type': 'mcq',
         'prompt': 'How do you find users who have no matching event?',
         'answer': 'LEFT JOIN events and keep rows where the event side IS '
                   'NULL.',
         'distractors': ['INNER JOIN events and count the results.',
                         'A subquery with EXISTS is the only way.',
                         'GROUP BY user and look for a count of zero.'],
         'teach': 'LEFT JOIN keeps every left row; the NULL on the right is '
                  'exactly the unmatched ones.'},
        {'id': 'sqq-transaction', 'type': 'mcq',
         'prompt': 'You ran an UPDATE inside a transaction and it looks wrong. '
                   'What undoes it?',
         'answer': 'ROLLBACK, which reverts everything since BEGIN.',
         'distractors': ['A second UPDATE to put the values back.',
                         'COMMIT, then edit the rows again.',
                         'Nothing; committed or not, it is permanent.'],
         'teach': 'Between BEGIN and COMMIT nothing is permanent, which is why '
                  'wrapping a risky change in a transaction is the safety net.'},
        {'id': 'sqq-index', 'type': 'mcq',
         'prompt': 'A query filtering on an unindexed column is slow on ten '
                   'million rows. Why?',
         'answer': 'With no index it scans every row to find the matches.',
         'distractors': ['The database file is fragmented.',
                         'sqlite cannot handle ten million rows.',
                         'The SELECT returns too many columns.'],
         'teach': 'CREATE INDEX turns the scan into a lookup. EXPLAIN QUERY '
                  'PLAN shows which is happening.'},
        {'id': 'sqq-readonly', 'type': 'mcq',
         'prompt': 'Why open a forensic database with -readonly?',
         'answer': 'So examining it cannot alter its timestamps or write a '
                   'journal, which would change the evidence.',
         'distractors': ['Read-only queries run faster.',
                         'It is the only way to run a SELECT.',
                         'It decrypts the database automatically.'],
         'teach': 'Examine the artifact, do not change it. Copy first, open the '
                  'copy read-only.'},
    ],
}
