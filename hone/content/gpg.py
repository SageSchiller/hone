"""gpg: keys you hold, signatures you can check, and trust you decide.

The mental model that changes here is asymmetry, and it is worth the module on
its own. Almost everyone meets encryption first as a password: one secret,
shared by everyone who needs access. Public key cryptography breaks that in
half, and once it lands, four operations that looked interchangeable become
obviously distinct: sign, verify, encrypt, decrypt. Two use your private key
and two use somebody else's public key, and knowing which is which is the
whole skill.

The second thing this module teaches is that **trust in gpg is a decision you
record, not a fact the tool discovers.** A downloaded key is just bytes until
you decide it belongs to who it claims to. That is uncomfortable, it is the
honest design, and it is why signature verification failures are so widely
misread: "Good signature" plus a trust warning means the maths checked out and
nobody has vouched for the key, which is two separate statements.

**D1 and your real keyring.** This module never touches `~/.gnupg`. The
sandbox creates a throwaway `GNUPGHOME` inside itself, mode 700, and hands it
to the shell in the environment, so every key you generate here lives and dies
with the challenge. That is structural rather than a warning in the prose,
which is the only version of this promise worth making.
"""

MODULE = {
    'id': 'gpg',
    'title': 'gpg',
    'group': 'Security',
    'blurb': 'Key pairs, signing and verifying, encryption, keyrings and trust.',
    'context': 'You are at a shell prompt with gpg installed, working in a throwaway keyring.',
    'needs': ['gpg'],
    'prereqs': ['linux'],
    'adapter': 'sandbox',
    'estimate': '3-4 hours',
    'order': 78,

    'lessons': [
        {
            'id': 'gp-model',
            'title': 'Two keys, four operations',
            'concept':
                'gpg is how you sign, verify, encrypt, and decrypt with a '
                'key pair instead of a shared password. That is why sending '
                'a file only they can read, or proving a release came from '
                'you, does not need a secret both of you already hold. '
                'A key pair is two mathematically linked halves. The private '
                'half you keep and never send anywhere. The public half you '
                'give to everyone, including people you do not trust: '
                'it is not a secret.\n\n'
                'Four operations fall out of that, and they pair up in the '
                'opposite directions to the way people first guess.\n\n'
                '**You sign with your private key. Anyone verifies with your '
                'public key.** This proves the message came from the holder '
                'of the private key and has not changed since. If a public '
                'key could sign, everyone who had it could forge your '
                'signature, which is why the direction is fixed.\n\n'
                '**They encrypt with your public key. Only you decrypt with '
                'your private key.** This protects the content and says '
                'nothing at all about who sent it.\n\n'
                'Those are independent. A signed message is readable by '
                'anyone and provably from you. An encrypted message is '
                'unreadable by others and, on its own, from nobody in '
                'particular. Doing both is normal and is two operations, not '
                'one.\n\n'
                'In practice gpg does not encrypt your file with the public '
                'key directly. It generates a random symmetric session key, '
                'encrypts the data with that, and encrypts the session key '
                'to each recipient. That is why encrypting to five people '
                'costs almost nothing extra.\n\n'
                'Four operations, one pair. The next lesson is making '
                'that pair and looking after it, because none of the '
                'four works without a key you hold.',
            'examples': [
                {'label': 'Prove it came from you',
                 'code': 'gpg --detach-sign --armor report.pdf',
                 'note': 'Writes report.pdf.asc. The file itself is '
                         'unchanged and still readable by anyone.'},
                {'label': 'Protect it from everyone but them',
                 'code': 'gpg --encrypt --recipient alice@example.com report.pdf',
                 'note': 'Only Alice can read it. This says nothing about '
                         'who sent it.'},
                {'label': 'Both, which is the usual thing',
                 'code': 'gpg --sign --encrypt --recipient alice@example.com '
                         'report.pdf',
                 'note': 'Two operations in one command. Alice learns both '
                         'that it is private and that it is yours.'},
                # gpg with no file reads standard input and waits, silently
                # and forever. It looks exactly like a hang, it is the first
                # thing a beginner hits, and this module never mentioned it.
                {'label': 'When gpg appears to hang',
                 'code': ('gpg --clearsign          no file named\n'
                          '\n'
                          'it is reading what you type. Not frozen.\n'
                          'Ctrl-D    finish the input, run the command\n'
                          'Ctrl-C    abandon it'),
                 'note': 'Give gpg a filename and it never does this. The '
                          'silence is the standard Unix "reading stdin", and '
                          'gpg is quieter about it than most.'},
            ],
            'misconceptions': [
                'Encrypting a file does not sign it. An encrypted file with '
                'no signature could have been written by anyone.',
                'Signing does not hide anything. A signed file is as readable '
                'as it was before.',
                'You never encrypt with your own public key to send to '
                'someone else. You encrypt with theirs.',
            ],
            'try_it': [
                'Sign a file, then open it in an editor and confirm it is '
                'unchanged.',
                'Encrypt a file to yourself and look at the size difference '
                'and the header.',
            ],
            'next': 'gp-keys',
        },
        {
            'id': 'gp-keys',
            'title': 'Making and looking after a key',
            'concept':
                '`gpg --quick-generate-key` is how you make the pair the four '
                'operations need, and how you set an expiry so a lost key '
                'stops being a liability. That is why the first real gpg '
                'work is generating and backing up, not signing.\n\n'
                'A modern gpg key is not one key. It is a primary key, which '
                'certifies and is the identity, plus subkeys for the actual '
                'work, usually one for signing and one for encryption. That '
                'structure exists so the primary key can be kept offline '
                'while day to day subkeys live on your machine.\n\n'
                '`--full-generate-key` asks every question. '
                '`--quick-generate-key` takes them on the command line, which '
                'is what you want in a script and for learning, because the '
                'interactive flow hides the shape of what is being made.\n\n'
                'Expiry is a feature, not a nuisance. A key that expires is a '
                'key that stops being a liability if you lose control of it, '
                'and extending the expiry is a single command you run while '
                'you still hold it. Setting no expiry is the choice that '
                'cannot be undone later.\n\n'
                'The revocation certificate is generated at the same time as '
                'the key, automatically, and it is the thing to save '
                'somewhere else immediately. It is how you announce that a '
                'key is dead when you can no longer use the key to say so.\n\n'
                'Key IDs come in lengths, and short ones are not safe: '
                '32-bit key IDs can be collided deliberately, which has been '
                'demonstrated publicly. Refer to keys by full fingerprint '
                'whenever it matters.',
            'examples': [
                {'label': 'Make a key without the interview',
                 'code': 'gpg --quick-generate-key "Ada <ada@example.com>" '
                         'default default 2y',
                 'note': 'Algorithm, usage, expiry. The defaults are good and '
                         'give you a signing primary with an encryption '
                         'subkey.'},
                {'label': 'What do I have',
                 'code': 'gpg --list-keys --keyid-format long',
                 'note': 'Public keys. --list-secret-keys for the ones you '
                         'can actually sign with.'},
                {'label': 'The identifier that is safe to quote',
                 'code': 'gpg --fingerprint ada@example.com',
                 'note': 'Full fingerprint. Short key IDs have been collided '
                         'in public, so they are not identifiers.'},
                {'label': 'Push the expiry out',
                 'code': 'gpg --quick-set-expire FINGERPRINT 1y',
                 'note': 'Run it while you still hold the key. That is the '
                         'entire argument for setting an expiry at all.'},
                {'label': 'Back up the secret key properly',
                 'code': 'gpg --export-secret-keys --armor ada@example.com '
                         '> secret.asc',
                 'note': 'This file is the key. Treat it exactly as you would '
                         'treat the keyring itself.'},
            ],
            'misconceptions': [
                'An expired key does not become unreadable. Signatures made '
                'while it was valid stay verifiable, and you can extend the '
                'expiry afterwards if you hold the key.',
                'Deleting a key from your keyring does not revoke it. Only a '
                'revocation certificate does that, and only where it is '
                'published.',
                'A short key ID is not a safe way to name a key. Collisions '
                'have been generated deliberately.',
            ],
            'try_it': [
                'Generate a key with a two year expiry and list it with long '
                'key IDs.',
                'Find the revocation certificate gpg wrote for you, and read '
                'the first lines of it.',
            ],
            'next': 'gp-sign',
        },
        {
            'id': 'gp-sign',
            'title': 'Three kinds of signature',
            'concept':
                '`gpg --detach-sign`, `--clear-sign`, and `--sign` are how '
                'you prove a file came from the holder of a key, in three '
                'shapes that put the signature in different places. That is '
                'why a software release ships a small `.asc` next to an '
                'untouched tarball, and an announcement keeps the text '
                'readable.\n\n'
                '**Detached**, with --detach-sign, writes a separate small '
                'file. The original is untouched. This is what software '
                'releases use, because the tarball has to stay byte for byte '
                'what it was.\n\n'
                '**Clear signed**, with --clear-sign, wraps a text file in '
                'readable armour with the signature appended. The content '
                'stays human readable, which is why it suits emails and '
                'announcements.\n\n'
                '**Inline**, with --sign, produces a new binary file '
                'containing both content and signature. Verifying it gives '
                'you the content back. Add --armor to get base64 text '
                'instead of binary.\n\n'
                'Verification output is two statements and people read it as '
                'one. "Good signature from ..." means the maths checked out: '
                'this data was signed by the key with this fingerprint. The '
                'warning that follows, "This key is not certified with a '
                'trusted signature", means nobody has vouched that the key '
                'belongs to that person. Both can be true at once, and '
                'usually are.\n\n'
                'A failed verify is louder than a trust warning, and it '
                'looks different. Change one byte of the tarball and '
                '`gpg --verify` prints `BAD signature`, not a warning. Swap '
                'the two arguments and you get a parse error rather than a '
                'clear no, because gpg tried to treat the tarball as the '
                'signature. The two-argument form, signature first, is the '
                'one that fails in a way you can read.',
            'examples': [
                {'label': 'Detached, for a release artefact',
                 'code': 'gpg --armor --detach-sign app-1.2.tar.gz',
                 'note': 'Writes app-1.2.tar.gz.asc next to it. Verify with '
                         'both files present.'},
                {'label': 'Verify a detached signature',
                 'code': 'gpg --verify app-1.2.tar.gz.asc app-1.2.tar.gz',
                 'note': 'Signature first, then the file. Getting them the '
                         'wrong way round is a common error.'},
                {'label': 'Clear signed, still readable',
                 'code': 'gpg --clear-sign announcement.txt',
                 'note': 'The text stays readable inside the armour, which is '
                         'the point.'},
                {'label': 'Who signed this, without having the key',
                 'code': 'gpg --verify file.asc 2>&1 | grep "using"',
                 'note': 'Names the key id even when you cannot verify, which '
                         'tells you what to fetch.'},
            ],
            'misconceptions': [
                '"Good signature" plus a trust warning is not a failure. The '
                'maths passed; nobody has vouched for the key.',
                '--verify with a detached signature takes the signature file '
                'first and the data file second.',
                'Signing a tarball with --sign rather than --detach-sign '
                'produces a different file, which is not what a release '
                'wants.',
            ],
            'try_it': [
                'Sign the same file all three ways and compare what appears '
                'on disk.',
                'Verify a good signature, then change one byte of the file '
                'and verify again.',
            ],
            'next': 'gp-encrypt',
        },
        {
            'id': 'gp-encrypt',
            'title': 'Encrypting, to others and to yourself',
            'concept':
                '`gpg --encrypt --recipient` is how you make a file only '
                'named key holders can read. That is why a backup for '
                'yourself, or a file for a colleague, does not need a '
                'password you then have to deliver. You need their public '
                'key in your keyring, and you can repeat `--recipient`: '
                'every recipient gets the session key encrypted to them, '
                'and any one of them can decrypt.\n\n'
                'The trap is encrypting to someone and not to yourself. gpg '
                'will happily produce a file you cannot read, and there is no '
                'recovery. --encrypt-to in your config, or naming yourself as '
                'a recipient, is the fix, and it is the setting worth '
                'changing on day one. The file you cannot read fails '
                'immediately. Decrypt prints `decryption failed: No secret '
                'key` and writes nothing useful. There is no later '
                'recovery: the session key is inside the file, wrapped only '
                'to the recipients you named. Re-encrypting from the '
                'ciphertext is impossible; the plaintext has to still '
                'exist.\n\n'
                '--symmetric is the other mode: no keys at all, one '
                'passphrase, anyone with the passphrase can decrypt. It is '
                'the right tool for encrypting a backup for yourself and the '
                'wrong tool for sending to someone else, because delivering '
                'the passphrase safely is the problem you were trying to '
                'solve.\n\n'
                '--armor turns binary output into base64 text so it survives '
                'email and copy-paste. It makes the file about a third '
                'bigger, and for anything going through a text channel that '
                'is a good trade.\n\n'
                'Decryption needs no flags to say which key: gpg reads which '
                'keys the file was encrypted to and reaches for the right '
                'secret key itself.',
            'examples': [
                {'label': 'To someone else, and to yourself',
                 'code': 'gpg --encrypt --recipient alice@example.com '
                         '--recipient me@example.com report.pdf',
                 'note': 'Leaving yourself off produces a file you cannot '
                         'read, permanently.'},
                {'label': 'Text-safe output',
                 'code': 'gpg --encrypt --armor --recipient alice@example.com '
                         'notes.txt',
                 'note': 'Writes notes.txt.asc, base64, safe to paste into '
                         'an email.'},
                {'label': 'Just a passphrase, no keys',
                 'code': 'gpg --symmetric --cipher-algo AES256 backup.tar',
                 'note': 'Good for yourself. Bad for sending, because the '
                         'passphrase has the same delivery problem.'},
                {'label': 'Read it back',
                 'code': 'gpg --decrypt --output report.pdf report.pdf.gpg',
                 'note': 'No need to say which key: gpg works out which one '
                         'the file was encrypted to.'},
            ],
            'misconceptions': [
                'Encrypting to a recipient does not include you. Add yourself '
                'explicitly or set encrypt-to in gpg.conf.',
                '--symmetric is not weaker cryptography. It is a different '
                'key distribution problem, and usually the wrong one.',
                'Decryption does not need --recipient. That flag is for '
                'encryption only.',
            ],
            'try_it': [
                'Encrypt a file to yourself, decrypt it, and diff the result '
                'against the original.',
                'Encrypt with --armor and look at the first line of the '
                'output.',
            ],
            'next': 'gp-keyring',
        },
        {
            'id': 'gp-keyring',
            'title': 'Keyrings: importing, exporting, keyservers',
            'concept':
                'Your keyring is a local database of public keys you have '
                'collected, plus the secret keys you hold. Everything about '
                'working with other people is moving keys in and out of it.\n\n'
                '--export writes a public key out, and --armor makes it '
                'pasteable. --import reads one in. A key you import is '
                'usable immediately for verification and for encryption; '
                'importing does not imply you believe anything about it.\n\n'
                'Keyservers are the traditional distribution network and they '
                'have aged badly. The old SKS network was vulnerable to '
                'anyone uploading anything, including spam signatures on '
                'other people\'s keys, and much of it is gone. keys.openpgp.org '
                'is the modern replacement and only distributes identities '
                'that have been confirmed by email.\n\n'
                'Web Key Directory is the quieter successor: the key is '
                'published at a well known HTTPS path on the domain of the '
                'email address, so fetching it is an ordinary web request to '
                'the organisation that owns the address. `--locate-keys` uses '
                'it automatically.\n\n'
                'Deleting is asymmetric on purpose. --delete-keys removes a '
                'public key; --delete-secret-keys is a separate command and '
                'must be run first if you hold both, which is a guard against '
                'destroying a secret key by mistake.\n\n'
                'Importing a key does not mean you believe it. The next '
                'lesson is trust, which is the decision the keyring '
                'will not make for you.',
            'examples': [
                {
                    'label': 'Keeping a keyring somewhere other than your own',
                    'code': 'gpg --homedir ./ring --list-keys\ngpg --homedir ./ring --import theirs.asc\n\ndefault is ~/.gnupg, and you rarely want\nan experiment landing in it',
                    'note': '--homedir points every operation at a different directory. It is how you try something without your real keyring becoming a museum of it.',
                },
                {'label': 'Give someone your public key',
                 'code': 'gpg --armor --export ada@example.com > ada.asc',
                 'note': 'Safe to publish anywhere. It is not a secret.'},
                {'label': 'Take someone else in',
                 'code': 'gpg --import colleague.asc',
                 'note': 'Immediately usable. Importing implies no trust '
                         'decision at all.'},
                {'label': 'Fetch by address, the modern way',
                 'code': 'gpg --locate-keys alice@example.com',
                 'note': 'Uses Web Key Directory: an ordinary HTTPS request '
                         'to the domain that owns the address.'},
                {'label': 'From a keyserver by fingerprint',
                 'code': 'gpg --keyserver keys.openpgp.org --recv-keys '
                         'FINGERPRINT',
                 'note': 'Always by full fingerprint. Short ids are not '
                         'identifiers.'},
                {'label': 'What did I actually import',
                 'code': 'gpg --show-keys colleague.asc',
                 'note': 'Reads a key file without importing it. Worth doing '
                         'first.'},
            ],
            'misconceptions': [
                'Importing a key is not trusting it. It only puts it in the '
                'keyring where you can use and inspect it.',
                'Keyservers do not verify anything about identity, apart from '
                'keys.openpgp.org confirming the email address.',
                'A key on a keyserver cannot be deleted. Revocation is the '
                'only way to retire one.',
            ],
            'try_it': [
                'Export your public key, delete it from a scratch keyring, '
                'and import it back.',
                'Run --show-keys on a key file before importing and read what '
                'it says.',
            ],
            'next': 'gp-trust',
        },
        {
            'id': 'gp-trust',
            'title': 'Trust is a decision you record',
            'concept':
                '`gpg --sign-key` and `--lsign-key` are how you record that '
                'a key belongs to the person named on it. That is why a '
                'Good signature with a trust warning is two statements: the '
                'maths passed, and nobody has vouched for the name.\n\n'
                'gpg separates two questions. Is this signature '
                'mathematically valid, which the tool answers on its own. And '
                'does this key really belong to the person named on it, which '
                'the tool cannot answer and will not pretend to.\n\n'
                'You answer the second by certifying a key: checking the '
                'fingerprint through some channel that is not the same one '
                'that delivered the key, then signing it with your own key. '
                'That is what --sign-key does, and it is why fingerprints get '
                'read out loud at conferences. The same-channel check is the '
                'failure that looks like care. Someone emails you a key and, '
                'in the same email, a fingerprint to compare. Matching them '
                'proves the email is consistent, not that it came from them. '
                'The check has to travel a different path: a voice call, a '
                'site you already trust, a sticker on a laptop.\n\n'
                'Owner trust is a third and separate thing: how much you '
                'trust that person to certify keys for others. Setting it '
                'with --edit-key trust is what makes the web of trust '
                'transitive, and it is the mechanism that never really '
                'scaled.\n\n'
                'For everyday use, --lsign-key is often the right tool: it '
                'certifies locally, so your keyring believes it and the '
                'signature is never published. And --tofu-policy offers the '
                'ssh-style alternative, trust on first use, which is weaker '
                'in theory and much closer to what people actually do.',
            'examples': [
                {'label': 'Certify, after checking the fingerprint elsewhere',
                 'code': 'gpg --sign-key alice@example.com',
                 'note': 'Your signature says you checked. Publish it or '
                         'not, deliberately.'},
                {'label': 'Certify locally and quietly',
                 'code': 'gpg --lsign-key alice@example.com',
                 'note': 'Never leaves your keyring. Usually what you '
                         'actually want.'},
                {'label': 'Set how much you trust them to vouch for others',
                 'code': 'gpg --edit-key alice@example.com trust',
                 'note': 'Owner trust, which is a separate question from '
                         'whether the key is really hers.'},
                {'label': 'See what your keyring believes',
                 'code': 'gpg --list-keys --with-colons | grep "^pub"',
                 'note': 'The trust field in the colon format is the '
                         'machine-readable version of the warnings.'},
            ],
            'misconceptions': [
                'A trust warning does not mean the signature is bad. It means '
                'nobody has vouched for the key.',
                'Signing a key is not the same as trusting its owner to sign '
                'other keys. Those are two separate settings.',
                'Checking a fingerprint over the same channel that sent you '
                'the key proves nothing, because whoever could swap one could '
                'swap both.',
            ],
            'try_it': [
                'Verify a signature from a key you have not certified and '
                'read both parts of the output.',
                'Locally sign that key and verify again, watching the warning '
                'disappear.',
            ],
            'next': 'gp-practice',
        },
        {
            'id': 'gp-practice',
            'title': 'Where gpg actually shows up',
            'concept':
                '`gpg --verify` is how a package manager, a release tarball, '
                'and a signed git tag all prove who produced the bytes. That '
                'is why an expired repository key, a `.asc` next to a '
                'download, and `git tag -s` are the same operation in '
                'different clothes.\n\n'
                '**Package management.** Every apt, dnf, pacman and rpm '
                'repository is signed, and the package manager verifies with '
                'gpg before installing. The "key expired" errors people work '
                'around with insecure flags are exactly this system doing its '
                'job. A package manager that refuses to install is usually '
                'this check, not a broken mirror. The error names an expired '
                'or unknown key. Forcing the install with an insecure flag '
                'does not fix the key; it turns the verify off. Refreshing '
                'the keyring, or installing the new key the project '
                'published, is the actual repair.\n\n'
                '**Release artefacts.** Tarballs and installers ship with '
                'detached signatures, and checking one is two commands: fetch '
                'the signing key by fingerprint from the project site, then '
                'verify.\n\n'
                '**Git commit and tag signing.** git uses gpg underneath for '
                '-S. A signed tag is how a release is attested, and the '
                'verification is the same gpg operation.\n\n'
                '**Password stores.** pass is a directory of gpg-encrypted '
                'files, which is why it is scriptable and syncable.\n\n'
                'The habit worth building around all of these is small: when '
                'a project publishes a fingerprint, get the key by '
                'fingerprint rather than by search, and verify before you run '
                'the thing.',
            'examples': [
                {'label': 'Verify a release properly',
                 'code': 'gpg --recv-keys FINGERPRINT_FROM_PROJECT_SITE\n'
                         'gpg --verify tool-2.0.tar.gz.asc tool-2.0.tar.gz',
                 'note': 'The fingerprint has to come from somewhere other '
                         'than the download page for this to mean much.'},
                {'label': 'Sign a git tag',
                 'code': 'git tag -s v1.0 -m "release 1.0"',
                 'note': 'git calls gpg. git tag -v checks it.'},
                {'label': 'Which key does git use',
                 'code': 'git config --global user.signingkey FINGERPRINT',
                 'note': 'Full fingerprint, for the same reason as everywhere '
                         'else.'},
            ],
            'misconceptions': [
                'Verifying a signature with a key you downloaded from the '
                'same page as the file proves very little on its own.',
                'A package manager key expiring is not a bug in the package '
                'manager. It is the expiry design working.',
                'git commit signing does not prove the code is good. It '
                'proves who committed it.',
            ],
            'try_it': [
                'Verify the signature on something you have downloaded '
                'recently, fetching the key by fingerprint.',
                'Sign a git tag in a scratch repository and verify it.',
            ],
            'next': None,
        },
    ],

    'drills': [
        {'id': 'gpd-quickgen', 'type': 'command',
         'prompt': 'Generate a key for Ada with default settings and two year '
                   'expiry.',
         'answer': 'gpg --quick-generate-key "Ada <ada@example.com>" default '
                   'default 2y',
         'teach': 'Name, algorithm, usage, expiry. The defaults give a '
                  'signing primary plus an encryption subkey.'},
        {'id': 'gpd-fullgen', 'type': 'command',
         'prompt': 'Start the interactive key generation that asks every '
                   'question.',
         'answer': 'gpg --full-generate-key',
         'teach': 'Fine once. The quick form is better for learning because '
                  'it shows the shape of what is made.'},
        {'id': 'gpd-list', 'type': 'command',
         'prompt': 'List public keys with long key IDs.',
         'answer': 'gpg --list-keys --keyid-format long',
         'teach': 'Short ids have been collided in public, so long is the '
                  'minimum and fingerprints are the real answer.'},
        {'id': 'gpd-list-secret', 'type': 'command',
         'prompt': 'List the secret keys you actually hold.',
         'answer': 'gpg --list-secret-keys',
         'teach': 'The difference between keys you can verify with and keys '
                  'you can sign with.'},
        {'id': 'gpd-fingerprint', 'type': 'command',
         'prompt': 'Show the full fingerprint of the key for ada@example.com.',
         'answer': 'gpg --fingerprint ada@example.com',
         'teach': 'The only identifier safe to quote. Read it out loud, '
                  'compare it in person.'},
        {'id': 'gpd-export', 'type': 'command',
         'prompt': 'Export the public key for ada@example.com as text to '
                   'ada.asc.',
         'answer': 'gpg --armor --export ada@example.com > ada.asc',
         'teach': 'Not a secret. Safe to publish anywhere at all.'},
        {'id': 'gpd-export-secret', 'type': 'command',
         'prompt': 'Export the secret key for ada@example.com as text to '
                   'secret.asc.',
         'answer': 'gpg --armor --export-secret-keys ada@example.com > '
                   'secret.asc',
         'teach': 'This file is the key. Treat it exactly as you treat the '
                  'keyring.'},
        {'id': 'gpd-import', 'type': 'command',
         'prompt': 'Import the public key in colleague.asc.',
         'answer': 'gpg --import colleague.asc',
         'teach': 'Usable at once, and it implies no trust decision '
                  'whatsoever.'},
        {'id': 'gpd-showkeys', 'type': 'command',
         'prompt': 'Read what is in colleague.asc without importing it.',
         'answer': 'gpg --show-keys colleague.asc',
         'teach': 'Worth doing first, so you know what you are about to add.'},
        {'id': 'gpd-locate', 'type': 'command',
         'prompt': 'Fetch the key for alice@example.com by web key directory.',
         'answer': 'gpg --locate-keys alice@example.com',
         'teach': 'An ordinary HTTPS request to the domain that owns the '
                  'address, which is why WKD aged better than keyservers.'},
        {'id': 'gpd-recv', 'type': 'command',
         'prompt': 'Fetch key 0xDEADBEEF from keys.openpgp.org.',
         'answer': 'gpg --keyserver keys.openpgp.org --recv-keys 0xDEADBEEF',
         'teach': 'Use a full fingerprint in real life. The old SKS network '
                  'is largely gone for good reasons.'},
        {'id': 'gpd-detach', 'type': 'command',
         'prompt': 'Make an armored detached signature of app.tar.gz.',
         'answer': 'gpg --armor --detach-sign app.tar.gz',
         'teach': 'Writes app.tar.gz.asc and leaves the tarball byte for '
                  'byte unchanged, which is what a release needs.'},
        {'id': 'gpd-verify', 'type': 'command',
         'prompt': 'Verify app.tar.gz against its detached signature.',
         'answer': 'gpg --verify app.tar.gz.asc app.tar.gz',
         'teach': 'Signature first, data second. Reversing them is a common '
                  'and confusing error.'},
        {'id': 'gpd-clearsign', 'type': 'command',
         'prompt': 'Sign announcement.txt so the text stays readable.',
         'answer': 'gpg --clear-sign announcement.txt',
         'teach': 'Armour wrapped around readable content, which is what '
                  'suits an email or a notice.'},
        {'id': 'gpd-sign-inline', 'type': 'command',
         'prompt': 'Produce a single signed file containing notes.txt.',
         'answer': 'gpg --sign notes.txt',
         'teach': 'Content and signature in one binary file. Add --armor for '
                  'the text version.'},
        {'id': 'gpd-encrypt', 'type': 'command',
         'prompt': 'Encrypt report.pdf to alice@example.com.',
         'answer': 'gpg --encrypt --recipient alice@example.com report.pdf',
         'teach': 'Nothing here says who sent it. Add --sign for that.'},
        {'id': 'gpd-encrypt-self', 'type': 'command',
         'prompt': 'Encrypt report.pdf to alice@example.com and to '
                   'me@example.com.',
         'answer': 'gpg --encrypt --recipient alice@example.com --recipient '
                   'me@example.com report.pdf',
         'teach': 'Leaving yourself off produces a file you can never read '
                  'again. Set encrypt-to in gpg.conf and stop worrying.'},
        {'id': 'gpd-encrypt-armor', 'type': 'command',
         'prompt': 'Encrypt notes.txt to alice@example.com as pasteable text.',
         'answer': 'gpg --encrypt --armor --recipient alice@example.com '
                   'notes.txt',
         'teach': 'About a third bigger, and it survives email and '
                  'copy-paste, which is usually worth it.'},
        {'id': 'gpd-sign-encrypt', 'type': 'command',
         'prompt': 'Sign and encrypt report.pdf to alice@example.com.',
         'answer': 'gpg --sign --encrypt --recipient alice@example.com '
                   'report.pdf',
         'teach': 'Two operations in one command, and they answer two '
                  'different questions.'},
        {'id': 'gpd-symmetric', 'type': 'command',
         'prompt': 'Encrypt backup.tar with a passphrase and AES256, no keys.',
         'answer': 'gpg --symmetric --cipher-algo AES256 backup.tar',
         'teach': 'Right for yourself, wrong for sending: delivering the '
                  'passphrase is the problem you were solving.'},
        {'id': 'gpd-decrypt', 'type': 'command',
         'prompt': 'Decrypt report.pdf.gpg back to report.pdf.',
         'answer': 'gpg --decrypt --output report.pdf report.pdf.gpg',
         'teach': 'No recipient flag needed: gpg works out which key the file '
                  'was encrypted to.'},
        {'id': 'gpd-signkey', 'type': 'command',
         'prompt': 'Certify that the key for alice@example.com is really hers.',
         'answer': 'gpg --sign-key alice@example.com',
         'teach': 'Do it after checking the fingerprint through a different '
                  'channel from the one that delivered the key.'},
        {'id': 'gpd-lsignkey', 'type': 'command',
         'prompt': 'Certify alice@example.com only in your own keyring.',
         'answer': 'gpg --lsign-key alice@example.com',
         'teach': 'Never published. Usually what you actually want.'},
        {'id': 'gpd-edit-trust', 'type': 'command',
         'prompt': 'Set how far you trust alice@example.com to certify others.',
         'answer': 'gpg --edit-key alice@example.com trust',
         'teach': 'Owner trust, which is a separate question from whether her '
                  'key is really hers.'},
        {'id': 'gpd-expire', 'type': 'command',
         'prompt': 'Extend key ABC123 to expire one year from now.',
         'answer': 'gpg --quick-set-expire ABC123 1y',
         'teach': 'Run it while you still hold the key. That is the whole '
                  'argument for setting an expiry.'},
        {'id': 'gpd-delete-secret', 'type': 'command',
         'prompt': 'Delete the secret key for old@example.com.',
         'answer': 'gpg --delete-secret-keys old@example.com',
         'teach': 'Must happen before deleting the public key, which is a '
                  'guard against destroying a secret key by accident.'},
        {'id': 'gpd-delete-public', 'type': 'command',
         'prompt': 'Delete the public key for old@example.com.',
         'answer': 'gpg --delete-keys old@example.com',
         'teach': 'Removing it locally is not revocation. Nothing anywhere '
                  'else learns about it.'},
        {'id': 'gpd-colons', 'type': 'command',
         'prompt': 'List keys in the machine-readable colon format.',
         'answer': 'gpg --list-keys --with-colons',
         'teach': 'Stable fields for scripts, unlike the human output which '
                  'changes between versions.'},
        {'id': 'gpd-homedir', 'type': 'command',
         'prompt': 'List keys from the keyring in ./ring rather than your own.',
         'answer': 'gpg --homedir ./ring --list-keys',
         'teach': 'The flag form of GNUPGHOME, and the safe way to '
                  'experiment without touching your real keyring.'},
    ],

    'challenges': [
        {
            'id': 'gpc-generate',
            'title': 'Make a key in a keyring of your own',
            'goal': 'Generate a key pair in the throwaway keyring and prove '
                    'you can read its fingerprint back.',
            'setup': {'kind': 'sandbox', 'shell': 'bash',
                      'tree': {'ring': {'dir': True, 'mode': '700'}},
                      'env': {'GNUPGHOME': '{dir}/ring'}},
            'solution': {'shell':
                'gpg --batch --passphrase "" --quick-generate-key '
                '"Hone Student <student@hone.lab>" default default 1y '
                '2>/dev/null; '
                'gpg --fingerprint student@hone.lab > fingerprint.txt 2>&1; '
                'gpg --list-secret-keys > secret-keys.txt 2>&1; true'},
            'steps': [
                {'instruction': 'Generate a key for Hone Student '
                                '<student@hone.lab> with a one year expiry. '
                                'In batch mode, pass an empty passphrase.',
                 'hint': 'gpg --batch --passphrase "" --quick-generate-key '
                         '"Hone Student <student@hone.lab>" default default 1y'},
                {'instruction': 'Write its full fingerprint into '
                                'fingerprint.txt.',
                 'hint': 'gpg --fingerprint student@hone.lab > fingerprint.txt'},
                {'instruction': 'List your secret keys into secret-keys.txt '
                                'and note the primary plus subkey structure.',
                 'hint': 'gpg --list-secret-keys > secret-keys.txt'},
            ],
            'free': 'Produce fingerprint.txt and secret-keys.txt for a key '
                    'you generated for student@hone.lab in this keyring.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'fingerprint.txt': 'student@hone.lab',
                                  'secret-keys.txt': ['sec', 'student@hone.lab']}}},
            'fallback': 'self',
        },
        {
            'id': 'gpc-sign-verify',
            'title': 'Sign a file, then catch a tampered one',
            'goal': 'Make a detached signature, verify it, then modify the '
                    'file and capture the verification failing.',
            'setup': {'kind': 'sandbox', 'shell': 'bash',
                      'tree': {'ring': {'dir': True, 'mode': '700'},
                               'release.txt': 'version 1.0 of the thing\n'},
                      'env': {'GNUPGHOME': '{dir}/ring'}},
            'solution': {'shell':
                'gpg --batch --passphrase "" --quick-generate-key '
                '"Signer <signer@hone.lab>" default default 1y 2>/dev/null; '
                'gpg --batch --yes --armor --detach-sign release.txt '
                '2>/dev/null; '
                'gpg --verify release.txt.asc release.txt > good.txt 2>&1; '
                'echo "sneaky addition" >> release.txt; '
                'gpg --verify release.txt.asc release.txt > bad.txt 2>&1; '
                'true'},
            'steps': [
                {'instruction': 'Generate a signing key for Signer '
                                '<signer@hone.lab>.',
                 'hint': 'gpg --batch --passphrase "" --quick-generate-key '
                         '"Signer <signer@hone.lab>" default default 1y'},
                {'instruction': 'Make an armored detached signature of '
                                'release.txt.',
                 'hint': 'gpg --armor --detach-sign release.txt'},
                {'instruction': 'Verify it, saving the output to good.txt.',
                 'hint': 'gpg --verify release.txt.asc release.txt > good.txt 2>&1'},
                {'instruction': 'Append a line to release.txt and verify '
                                'again into bad.txt.',
                 'hint': 'echo "sneaky addition" >> release.txt'},
            ],
            'free': 'Produce release.txt.asc, good.txt showing a good '
                    'signature, and bad.txt showing the same signature '
                    'failing after the file changed.',
            'verify': {'kind': 'sandbox', 'expect': {
                'is_file': ['release.txt.asc'],
                'file_contains': {'good.txt': 'Good signature',
                                  'bad.txt': 'BAD signature'}}},
            'fallback': 'self',
        },
        {
            'id': 'gpc-encrypt',
            'title': 'Encrypt to yourself, and read it back',
            'goal': 'Encrypt a file with armour, decrypt it, and prove the '
                    'round trip is exact.',
            'setup': {'kind': 'sandbox', 'shell': 'bash',
                      'tree': {'ring': {'dir': True, 'mode': '700'},
                               'secret.txt': 'the account number is 12345\n'},
                      'env': {'GNUPGHOME': '{dir}/ring'}},
            'solution': {'shell':
                'gpg --batch --passphrase "" --quick-generate-key '
                '"Holder <holder@hone.lab>" default default 1y 2>/dev/null; '
                'gpg --batch --yes --encrypt --armor --recipient '
                'holder@hone.lab --output secret.asc secret.txt 2>/dev/null; '
                'gpg --batch --yes --decrypt --output roundtrip.txt '
                'secret.asc 2>/dev/null; true'},
            'steps': [
                {'instruction': 'Generate a key for Holder '
                                '<holder@hone.lab>.',
                 'hint': 'gpg --batch --passphrase "" --quick-generate-key '
                         '"Holder <holder@hone.lab>" default default 1y'},
                {'instruction': 'Encrypt secret.txt to that key, with armour, '
                                'into secret.asc.',
                 'hint': 'gpg --encrypt --armor --recipient holder@hone.lab '
                         '--output secret.asc secret.txt'},
                {'instruction': 'Look at the first line of secret.asc, then '
                                'decrypt it into roundtrip.txt.',
                 'hint': 'gpg --decrypt --output roundtrip.txt secret.asc'},
            ],
            'free': 'Produce secret.asc, an armored encrypted copy of '
                    'secret.txt, and roundtrip.txt decrypted back from it.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'secret.asc': 'BEGIN PGP MESSAGE',
                                  'roundtrip.txt': 'account number is 12345'},
                'file_lacks': {'secret.asc': 'account number'}}},
            'fallback': 'self',
        },
        {
            'id': 'gpc-export-import',
            'title': 'Move a public key between keyrings',
            'goal': 'Export a public key, import it into a second keyring, '
                    'and encrypt to it from there.',
            'setup': {'kind': 'sandbox', 'shell': 'bash',
                      'tree': {'ring': {'dir': True, 'mode': '700'},
                               'other': {'dir': True, 'mode': '700'},
                               'message.txt': 'meet at the usual place\n'},
                      'env': {'GNUPGHOME': '{dir}/ring'}},
            'solution': {'shell':
                'gpg --batch --passphrase "" --quick-generate-key '
                '"Recipient <rx@hone.lab>" default default 1y 2>/dev/null; '
                'gpg --armor --export rx@hone.lab > rx.asc 2>/dev/null; '
                'gpg --homedir ./other --batch --import rx.asc 2>/dev/null; '
                'gpg --homedir ./other --batch --list-keys > imported.txt '
                '2>&1; '
                'gpg --homedir ./other --batch --yes --trust-model always '
                '--encrypt --armor --recipient rx@hone.lab --output '
                'message.asc message.txt 2>/dev/null; true'},
            'steps': [
                {'instruction': 'Generate a key for Recipient <rx@hone.lab> '
                                'in the default keyring.',
                 'hint': 'gpg --batch --passphrase "" --quick-generate-key '
                         '"Recipient <rx@hone.lab>" default default 1y'},
                {'instruction': 'Export its public half to rx.asc.',
                 'hint': 'gpg --armor --export rx@hone.lab > rx.asc'},
                {'instruction': 'Import it into the separate keyring ./other '
                                'and list what landed there, into '
                                'imported.txt.',
                 'hint': 'gpg --homedir ./other --import rx.asc'},
                {'instruction': 'From that second keyring, encrypt '
                                'message.txt to rx. It has no trust path, so '
                                'you will need --trust-model always.',
                 'hint': 'gpg --homedir ./other --trust-model always '
                         '--encrypt --armor --recipient rx@hone.lab --output '
                         'message.asc message.txt'},
            ],
            'free': 'Produce rx.asc, imported.txt showing the key present in '
                    './other, and message.asc encrypted from that keyring.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'rx.asc': 'BEGIN PGP PUBLIC KEY BLOCK',
                                  'imported.txt': 'rx@hone.lab',
                                  'message.asc': 'BEGIN PGP MESSAGE'}}},
            'fallback': 'self',
        },
        {
            'id': 'gpc-symmetric',
            'title': 'Encrypt with a passphrase and nothing else',
            'goal': 'Use the keyless mode, and see what it does and does not '
                    'solve.',
            'setup': {'kind': 'sandbox', 'shell': 'bash',
                      'tree': {'ring': {'dir': True, 'mode': '700'},
                               'notes.txt': 'passphrase only, no keys here\n'},
                      'env': {'GNUPGHOME': '{dir}/ring'}},
            'solution': {'shell':
                'gpg --batch --yes --passphrase "correct horse" --symmetric '
                '--cipher-algo AES256 --armor --output notes.asc notes.txt '
                '2>/dev/null; '
                'gpg --batch --yes --passphrase "correct horse" --decrypt '
                '--output back.txt notes.asc 2>/dev/null; true'},
            'steps': [
                {'instruction': 'Encrypt notes.txt symmetrically with AES256 '
                                'and armour, into notes.asc. In batch mode '
                                'the passphrase goes on the command line.',
                 'hint': 'gpg --batch --passphrase "correct horse" '
                         '--symmetric --cipher-algo AES256 --armor --output '
                         'notes.asc notes.txt'},
                {'instruction': 'Decrypt it back into back.txt with the same '
                                'passphrase.',
                 'hint': 'gpg --batch --passphrase "correct horse" --decrypt '
                         '--output back.txt notes.asc'},
                {'instruction': 'Ask yourself how you would have given that '
                                'passphrase to someone else safely. That '
                                'question is why key pairs exist.'},
            ],
            'free': 'Produce notes.asc encrypted symmetrically, and back.txt '
                    'decrypted from it, using no keys at all.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'notes.asc': 'BEGIN PGP MESSAGE',
                                  'back.txt': 'passphrase only'},
                'file_lacks': {'notes.asc': 'no keys here'}}},
            'fallback': 'self',
        },
        {
            'id': 'gpc-real-verify',
            'title': 'Verify something you actually downloaded',
            'goal': 'Leave the sandbox and check a real signature, in the '
                    'order that makes the check mean something.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'Find a project you use that publishes a '
                                'signing key fingerprint on its site.'},
                {'instruction': 'Fetch the key by fingerprint, not by '
                                'searching for a name.',
                 'hint': 'gpg --locate-keys them@project.org  # or --recv-keys '
                         'FINGERPRINT'},
                {'instruction': 'Download the artefact and its detached '
                                'signature, and verify.',
                 'hint': 'gpg --verify thing.tar.gz.asc thing.tar.gz'},
                {'instruction': 'Read both halves of the output: the good '
                                'signature line, and whatever it says about '
                                'trust. Decide whether to certify the key.'},
            ],
            'free': 'On your own machine: fetch a project signing key by '
                    'fingerprint, verify a real release signature with it, '
                    'and read both parts of what gpg tells you.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
    ],

    'quiz': [
        {'id': 'gpq-direction', 'type': 'mcq',
         'prompt': 'You want to send Alice a file only she can read. Whose '
                   'key do you use, and which half?',
         'answer': 'Alice\'s public key.',
         'distractors': ['Your own private key.',
                         'Your own public key.',
                         'Alice\'s private key.'],
         'teach': 'Encrypt with theirs, decrypt with yours. Sign with yours, '
                  'verify with theirs. Those are the only four combinations.'},
        {'id': 'gpq-sign-direction', 'type': 'mcq',
         'prompt': 'You want everyone to be able to prove a file came from '
                   'you. Which key signs it?',
         'answer': 'Your private key, and anyone verifies with your public '
                   'key.',
         'distractors': ['Your public key, since everyone has it.',
                         'A shared key you publish alongside the file.',
                         'The recipient\'s public key.'],
         'teach': 'If the public key could sign, anyone holding it could '
                  'forge your signature. The direction cannot be swapped.'},
        {'id': 'gpq-trust-warning', 'type': 'mcq',
         'prompt': 'gpg prints "Good signature" and then a warning that the '
                   'key is not certified. What does that mean?',
         'answer': 'The maths checked out, and nobody has vouched that the '
                   'key belongs to that person.',
         'distractors': ['The signature is invalid and should be rejected.',
                         'The key has expired but the signature predates it.',
                         'The file was modified after signing.'],
         'teach': 'Two separate statements. Certify the key, ideally after '
                  'checking the fingerprint through another channel, and the '
                  'warning goes away.'},
        {'id': 'gpq-encrypt-self', 'type': 'mcq',
         'prompt': 'You encrypt a file to Alice only, then delete the '
                   'original. What have you got?',
         'answer': 'A file you cannot read, permanently.',
         'distractors': ['A file you can decrypt with your own private key.',
                         'A file gpg will decrypt after asking for your '
                         'passphrase.',
                         'A file that Alice must re-encrypt to you.'],
         'teach': 'Add yourself as a recipient, or set encrypt-to in '
                  'gpg.conf. This is the mistake worth preventing on day one.'},
        {'id': 'gpq-detached', 'type': 'mcq',
         'prompt': 'Why do software releases use detached signatures rather '
                   'than inline ones?',
         'answer': 'The artefact stays byte for byte unchanged, so hashes and '
                   'mirrors still match.',
         'distractors': ['Detached signatures are cryptographically '
                         'stronger.',
                         'Inline signatures cannot be verified without the '
                         'private key.',
                         'Detached signatures do not expire with the key.'],
         'teach': 'A tarball has to stay what it was. The signature travels '
                  'beside it as a second small file.'},
        {'id': 'gpq-verify-order', 'type': 'mcq',
         'prompt': 'Which order do the files go in for gpg --verify with a '
                   'detached signature?',
         'answer': 'Signature first, then the data file.',
         'distractors': ['Data file first, then the signature.',
                         'Either order: gpg detects which is which.',
                         'Only the signature, since it names the file.'],
         'teach': 'gpg --verify thing.tar.gz.asc thing.tar.gz. Reversing them '
                  'produces a confusing error rather than a clear one.'},
        {'id': 'gpq-import-trust', 'type': 'mcq',
         'prompt': 'What does importing a public key tell gpg about whether '
                   'you trust it?',
         'answer': 'Nothing. Importing and trusting are separate steps.',
         'distractors': ['That you trust it fully, since you chose to import '
                         'it.',
                         'That you trust it marginally until you say '
                         'otherwise.',
                         'That you trust it to certify other keys.'],
         'teach': 'Trust is a decision you record with --sign-key or '
                  '--lsign-key, and owner trust is a third setting again.'},
        {'id': 'gpq-symmetric', 'type': 'mcq',
         'prompt': 'When is --symmetric the right choice?',
         'answer': 'Encrypting something for yourself, such as a backup.',
         'distractors': ['Sending a file to a colleague securely.',
                         'Signing a release artefact.',
                         'Encrypting to several recipients at once.'],
         'teach': 'It removes key management and replaces it with the problem '
                  'of delivering a passphrase, which is usually the harder '
                  'one.'},
        {'id': 'gpq-shortid', 'type': 'mcq',
         'prompt': 'Why should you not identify a key by its short key ID?',
         'answer': 'Short IDs can be collided deliberately, and have been in '
                   'public.',
         'distractors': ['Short IDs change when the key is extended.',
                         'Short IDs are not accepted by modern keyservers.',
                         'Short IDs do not survive an armored export.'],
         'teach': 'Use the full fingerprint anywhere the answer matters, '
                  'including in git config and in documentation.'},
        {'id': 'gpq-expiry', 'type': 'mcq',
         'prompt': 'Your key expires next week. What happens to signatures '
                   'you made last year?',
         'answer': 'They stay verifiable, because they were made while the '
                   'key was valid.',
         'distractors': ['They become invalid the moment the key expires.',
                         'They can only be verified with the revocation '
                         'certificate.',
                         'They must be re-signed with the extended key.'],
         'teach': 'Expiry limits future use. You can also extend it yourself '
                  'while you still hold the key, which is why an expiry costs '
                  'so little.'},
    ],
}
