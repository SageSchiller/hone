"""openssl: key material, certificate files, and what is inside them.

Most of openssl is about a fact people never learn deliberately:
**certificates and keys are files in specific formats, and almost every TLS
problem is a question about those files.** The `s_client` subcommand is the
exception that reaches out over the network to see what a live server actually
serves, and it lives here too, because it is an openssl subcommand and the
place it used to sit, the Remote access module, has been split into its tools.

Why it earns a module under the boundary rule: the mental model genuinely
changes how you think. Before it, PEM and DER and PKCS12 are interchangeable
mysteries and a certificate is an opaque blob you either have or lack. After
it, a certificate is a signed statement with fields you can read, a private key
is a separate file that must mathematically correspond to it, and a chain is an
ordered list whose order matters. Those three facts resolve most of the
support tickets in the category.

**Verified work is offline.** Every verified challenge generates its own key
material in the sandbox and inspects it. Nothing connects to anything, which
keeps D1 intact and means the graded part of the module works on a machine
with no network at all. The `s_client` lesson and the one challenge that reads
a real certificate reach a live service, so they are marked self and say so.

**On the keys you generate here.** They are throwaway, they live in a temp
directory the trainer deletes, and the module says so. Do not reuse them.
"""

MODULE = {
    'id': 'openssl',
    'title': 'openssl: certs and keys',
    'group': 'Security',
    'blurb': 'PEM and DER, x509 fields, CSRs, chains, and proving a key matches.',
    'context': 'You are at a shell prompt with openssl installed, working on throwaway key material.',
    'needs': ['openssl'],
    'prereqs': ['linux', 'ssh'],
    'adapter': 'sandbox',
    'estimate': '3-4 hours',
    'order': 73,

    'lessons': [
        {
            'id': 'os-formats',
            'title': 'PEM, DER, and why files look different',
            'concept':
                'There is one underlying structure and several ways to write '
                'it down, and confusing the encoding with the content is the '
                'commonest beginner mistake here.\n\n'
                'DER is the binary encoding. It is what the structure '
                'actually is, and a DER file looks like nothing in a text '
                'editor.\n\n'
                'PEM is DER, base64 encoded, wrapped in BEGIN and END lines. '
                'That is all it is. The header line names what is inside, and '
                'reading it saves an enormous amount of confusion: BEGIN '
                'CERTIFICATE is a certificate, BEGIN PRIVATE KEY is a key, '
                'BEGIN CERTIFICATE REQUEST is a CSR, BEGIN PUBLIC KEY is a '
                'public key on its own.\n\n'
                'The file extension tells you nothing reliable. .crt, .cer '
                'and .pem all commonly hold PEM certificates; .der and '
                'sometimes .cer hold binary; .key usually holds a private key '
                'and sometimes holds PEM certificates too, because someone '
                'was in a hurry.\n\n'
                'PKCS#12, written .p12 or .pfx, is a different thing again: '
                'a single encrypted container holding a key, its certificate '
                'and usually the chain. Windows and Java want it; most Unix '
                'software wants separate PEM files; converting between them '
                'is a routine chore.',
            'examples': [
                {'label': 'What is actually in this file',
                 'code': 'head -1 mystery.crt',
                 'note': 'The BEGIN line names it. Faster than any tool, and '
                         'right more often than the extension.'},
                {'label': 'PEM to DER and back',
                 'code': 'openssl x509 -in cert.pem -outform DER -out cert.der\n'
                         'openssl x509 -inform DER -in cert.der -out cert.pem',
                 'note': 'Same certificate, two encodings. -inform and '
                         '-outform are the only difference.'},
                {'label': 'Bundle a key and cert for Windows or Java',
                 'code': 'openssl pkcs12 -export -inkey key.pem -in cert.pem '
                         '-certfile chain.pem -out bundle.p12',
                 'note': 'One encrypted file with everything in it. It will '
                         'ask for an export password.'},
                {'label': 'Take a p12 apart again',
                 'code': 'openssl pkcs12 -in bundle.p12 -nodes -out all.pem',
                 'note': '-nodes leaves the private key unencrypted, which is '
                         'convenient and worth thinking about first.'},
            ],
            'misconceptions': [
                'PEM and DER are not different kinds of certificate. They are '
                'the same bytes, one base64 encoded.',
                'The extension is a convention, not a format. Read the first '
                'line instead.',
                'A .p12 is not a certificate file you can hand to a web '
                'server directly. Most Unix servers want the PEM pieces.',
            ],
            'try_it': [
                'Run head -1 on every certificate and key file you can find '
                'and match the header to the content.',
                'Convert a PEM certificate to DER, check the size difference, '
                'and convert it back.',
            ],
            'next': 'os-x509',
        },
        {
            'id': 'os-x509',
            'title': 'Reading a certificate: the fields that matter',
            'concept':
                'A certificate is a signed statement. Someone, the issuer, '
                'asserts that a public key belongs to a subject, for a period '
                'of time, for certain uses, and signs that assertion. Every '
                'field is one part of that sentence.\n\n'
                'Subject is who it is about. Issuer is who signed it. When '
                'the two are identical, the certificate is self-signed, which '
                'is the definition rather than a property you have to look '
                'up.\n\n'
                'Not Before and Not After are validity. Expiry is the single '
                'most common cause of a sudden TLS outage, and checking it '
                'takes one command.\n\n'
                'Subject Alternative Name is the field that actually decides '
                'whether a browser accepts the certificate for a hostname. '
                'The Common Name in the subject has been ignored for host '
                'matching for years, and expecting it to work is a reliable '
                'way to produce a certificate that fails for reasons the '
                'error message describes badly.\n\n'
                'Key Usage and Extended Key Usage constrain what the '
                'certificate may be used for, and Basic Constraints says '
                'whether it may sign other certificates, which is what makes '
                'something a CA. The serial number and the fingerprint are '
                'how you refer to a specific certificate unambiguously.',
            'examples': [
                {'label': 'Everything, readably',
                 'code': 'openssl x509 -in cert.pem -noout -text',
                 'note': '-noout suppresses re-printing the encoded '
                         'certificate, which is otherwise most of the output.'},
                {'label': 'Just the questions you usually have',
                 'code': 'openssl x509 -in cert.pem -noout -subject -issuer '
                         '-dates',
                 'note': 'Who, from whom, and until when, in three lines.'},
                {'label': 'Which hostnames does it actually cover',
                 'code': 'openssl x509 -in cert.pem -noout -ext '
                         'subjectAltName',
                 'note': 'SAN is what matters. CN has not been used for host '
                         'matching in years.'},
                {'label': 'Has it expired, without reading dates',
                 'code': 'openssl x509 -in cert.pem -noout -checkend 604800',
                 'note': 'Exit status says whether it expires within that '
                         'many seconds. A week here. Made for monitoring.'},
                {'label': 'Identify it unambiguously',
                 'code': 'openssl x509 -in cert.pem -noout -fingerprint '
                         '-sha256 -serial',
                 'note': 'The fingerprint is a hash of the whole certificate, '
                         'and is how humans compare two of them.'},
            ],
            'misconceptions': [
                'Common Name does not decide hostname matching. Subject '
                'Alternative Name does, and a certificate without a SAN fails '
                'in every current browser.',
                'Self-signed is not a separate format or a flag. It means the '
                'issuer and subject are the same.',
                'A valid certificate is not necessarily a trusted one. '
                'Validity is about dates and signature, trust is about the '
                'chain.',
            ],
            'try_it': [
                'Read the subject, issuer, dates and SAN of a certificate '
                'from a site you use.',
                'Run -checkend on it with a large number and read the exit '
                'status with echo $?.',
            ],
            'next': 'os-keys',
        },
        {
            'id': 'os-keys',
            'title': 'Private keys, public keys, and proving they match',
            'concept':
                'A private key and its certificate are two files that must '
                'correspond. Nothing enforces this. You can put any '
                'certificate next to any key in a server config, and the '
                'server will start and then fail in a way whose error message '
                'rarely says "these do not match".\n\n'
                'The check is mechanical. The public key inside the '
                'certificate and the public part of the private key must be '
                'identical, so hashing both and comparing the hashes settles '
                'it in two commands. For RSA the traditional form compares '
                'the modulus; the modern general form extracts the public key '
                'from each and compares those, and it works for elliptic '
                'curve keys too.\n\n'
                'Key types matter less than people expect and more than they '
                'think in one respect: RSA 2048 or 4096 is the safe default '
                'everywhere, and EC keys with prime256v1 are smaller and '
                'faster and not universally supported by old software.\n\n'
                'Encrypted private keys are worth knowing about because they '
                'are the thing that makes a service fail to start unattended. '
                'A key with a passphrase must have it typed at boot, which is '
                'why so many production keys are stored unencrypted with '
                'filesystem permissions doing the work instead.',
            'examples': [
                {'label': 'Does this key go with this certificate',
                 'code': 'openssl x509 -in cert.pem -noout -pubkey | '
                         'openssl sha256\n'
                         'openssl pkey -in key.pem -pubout | openssl sha256',
                 'note': 'Identical hashes mean they match. Works for RSA and '
                         'EC alike.'},
                {'label': 'The RSA-only classic',
                 'code': 'openssl x509 -in cert.pem -noout -modulus | '
                         'openssl sha256',
                 'note': 'Same idea, RSA only, and the form you will see in '
                         'every older write-up.'},
                {'label': 'Generate a key on its own',
                 'code': 'openssl genrsa -out key.pem 4096',
                 'note': 'genpkey is the modern general command; genrsa is '
                         'the one everyone types.'},
                {'label': 'An elliptic curve key instead',
                 'code': 'openssl ecparam -genkey -name prime256v1 -out ec.pem',
                 'note': 'Smaller and faster. Check what has to consume it '
                         'before choosing.'},
                {'label': 'Remove a passphrase from a key',
                 'code': 'openssl rsa -in encrypted.pem -out plain.pem',
                 'note': 'Asks for the passphrase, writes it without one. '
                         'What unattended services need, and a decision.'},
            ],
            'misconceptions': [
                'Nothing checks that a key and certificate belong together '
                'until the software fails, and the failure message is usually '
                'about something else.',
                'A public key file is not a certificate. It carries no '
                'subject, no dates and no signature.',
                'Removing a passphrase does not weaken the key itself. It '
                'moves the protection entirely onto file permissions.',
            ],
            'try_it': [
                'Generate a key and a self-signed certificate, then prove '
                'they match with the hash comparison.',
                'Generate a second key and prove that it does not match the '
                'same certificate.',
            ],
            'next': 'os-csr',
        },
        {
            'id': 'os-csr',
            'title': 'CSRs and self-signed certificates',
            'concept':
                'A certificate signing request is a small package containing '
                'a public key and the details you want asserted about it, '
                'signed by the corresponding private key to prove you hold '
                'it. You send it to a CA; the private key never leaves your '
                'machine. That last point is the whole design.\n\n'
                'The interactive prompts are famously tedious, and -subj '
                'skips them entirely with a slash separated string. -addext '
                'adds extensions, which is how you get a SAN into the request '
                'rather than discovering later that the issued certificate '
                'covers nothing.\n\n'
                'A self-signed certificate is the same operation with the '
                'CA step removed: you sign your own request with your own '
                'key. `openssl req -x509` does the key generation, the '
                'request and the signing in one command, which is why it is '
                'the line everyone has memorised for test certificates.\n\n'
                'Always read the CSR back before sending it. `openssl req '
                '-in req.csr -noout -text` shows exactly what you asked for, '
                'and catching a typo there costs a second, while catching it '
                'after issuance costs a reissue.',
            'examples': [
                {'label': 'A request, without the twenty questions',
                 'code': 'openssl req -new -key key.pem -out req.csr '
                         '-subj "/CN=www.example.com/O=Example Ltd"',
                 'note': '-subj is a slash separated list of fields. The '
                         'prompts are optional, not mandatory.'},
                {'label': 'With the SAN that actually matters',
                 'code': 'openssl req -new -key key.pem -out req.csr '
                         '-subj "/CN=example.com" '
                         '-addext "subjectAltName=DNS:example.com,DNS:www.example.com"',
                 'note': 'Without this the issued certificate may cover no '
                         'hostname at all.'},
                {'label': 'Read it back before you send it',
                 'code': 'openssl req -in req.csr -noout -text -verify',
                 'note': '-verify checks the self-signature, which proves the '
                         'request was made by the holder of the key.'},
                {'label': 'Key and self-signed certificate in one line',
                 'code': 'openssl req -x509 -newkey rsa:2048 -keyout key.pem '
                         '-out cert.pem -days 365 -nodes -subj "/CN=test.local"',
                 'note': '-nodes means no passphrase on the key. The standard '
                         'test certificate line.'},
            ],
            'misconceptions': [
                'A CSR does not contain your private key. It contains the '
                'public key and a signature made with the private one.',
                'The CN in a CSR does not become a working hostname on its '
                'own. Put the names in a SAN extension.',
                '-nodes is not "nodes". It is "no DES", meaning do not '
                'encrypt the private key.',
            ],
            'try_it': [
                'Generate a CSR with -subj and read it back with -text, '
                'checking every field.',
                'Make a self-signed certificate with a SAN and confirm the '
                'SAN survived into the certificate.',
            ],
            'next': 'os-chain',
        },
        {
            'id': 'os-chain',
            'title': 'Chains, trust, and why the browser disagrees',
            'concept':
                'A certificate is trusted because something you already trust '
                'signed it, or signed something that signed it. That path is '
                'the chain, and it ends at a root certificate in a trust '
                'store you did not choose individually.\n\n'
                'Servers must send their own certificate plus every '
                'intermediate, in order, leaf first. They must not send the '
                'root, because the client already has it. The single '
                'commonest TLS misconfiguration in the world is a missing '
                'intermediate: it works in your browser, which cached the '
                'intermediate from another site, and fails on a fresh machine '
                'or a command line client, which did not.\n\n'
                '`openssl verify` checks a chain offline. Given the CA file '
                'and the untrusted intermediates it will tell you whether the '
                'path builds, and its error messages are specific: unable to '
                'get local issuer certificate means the chain is incomplete, '
                'self signed certificate in certificate chain means the root '
                'is being sent or is not trusted, certificate has expired '
                'means what it says.\n\n'
                'Order matters in a bundle file. Leaf, then intermediates '
                'towards the root. A bundle assembled in the wrong order is '
                'accepted by some software and rejected by other software, '
                'which is the worst kind of bug to chase.',
            'examples': [
                {'label': 'Does this chain build',
                 'code': 'openssl verify -CAfile root.pem -untrusted '
                         'intermediate.pem leaf.pem',
                 'note': 'Entirely offline. The error messages are precise '
                         'and worth reading literally.'},
                {'label': 'Split a bundle back into its parts',
                 'code': 'openssl crl2pkcs7 -nocrl -certfile bundle.pem | '
                         'openssl pkcs7 -print_certs -noout',
                 'note': 'Lists subject and issuer of every certificate in a '
                         'concatenated file, in order.'},
                {'label': 'Verify a certificate against the system store',
                 'code': 'openssl verify cert.pem',
                 'note': 'With no -CAfile it uses the default trust store, '
                         'which is what a client would do.'},
                {'label': 'Check a hostname would be accepted',
                 'code': 'openssl verify -verify_hostname www.example.com '
                         '-CAfile chain.pem cert.pem',
                 'note': 'Applies the SAN matching rules rather than making '
                         'you read them yourself.'},
            ],
            'misconceptions': [
                '"It works in my browser" is not evidence the chain is '
                'complete. Browsers cache intermediates from other sites.',
                'The root certificate should not be sent by the server. '
                'Sending it is harmless but pointless, and often signals a '
                'bundle assembled by hand.',
                'openssl verify checks a path, not a service. A perfect chain '
                'file says nothing about what the server actually sends.',
            ],
            'try_it': [
                'Build a two level chain yourself and verify the leaf against '
                'your own root.',
                'Delete the intermediate from the verify command and read the '
                'exact error you get.',
            ],
            'next': 'os-sclient',
        },
        {
            'id': 'os-sclient',
            'title': 'Reaching a live service with s_client',
            'concept':
                'Everything so far reads a file. `s_client` is the one '
                'subcommand that opens a real TLS connection, and it answers '
                'the question a file never can: what is this server actually '
                'sending right now.\n\n'
                '`openssl s_client -connect host:443 -servername host` does '
                'the handshake and prints it. The `-servername` matters more '
                'than it looks: without it you may get the default '
                'certificate rather than the one for the name you asked '
                'about, because one address often serves many names by SNI, '
                'and the whole point of the check is usually to see the right '
                'one.\n\n'
                'It hangs waiting for input after the handshake, so feed it '
                '`</dev/null` to close cleanly, and pipe the result into '
                '`x509` to read the certificate it returned: `openssl '
                's_client -connect host:443 -servername host </dev/null '
                '2>/dev/null | openssl x509 -noout -dates`. That one line '
                'answers "has the cert on this server expired" without '
                'saving anything.\n\n'
                '`-showcerts` prints every certificate the server sent, which '
                'is how you catch the commonest TLS misconfiguration there '
                'is: a missing intermediate. The server that works in your '
                'browser and fails on a fresh machine is almost always '
                'sending only its leaf, and `-showcerts` shows you the chain '
                'stops one short.',
            'examples': [
                {'label': 'What is this server serving',
                 'code': 'openssl s_client -connect example.com:443 '
                         '-servername example.com',
                 'note': 'Prints the whole handshake. -servername picks the '
                         'name by SNI, or you get the default certificate.'},
                {'label': 'Just the dates, without saving the cert',
                 'code': 'openssl s_client -connect example.com:443 '
                         '-servername example.com </dev/null 2>/dev/null | '
                         'openssl x509 -noout -dates',
                 'note': '</dev/null closes the connection that otherwise '
                         'hangs, and the pipe reads the returned certificate.'},
                {'label': 'Did it send the intermediates',
                 'code': 'openssl s_client -connect example.com:443 '
                         '-showcerts </dev/null 2>/dev/null',
                 'note': 'One certificate where you expected two or three is '
                         'the missing-intermediate bug.'},
            ],
            'misconceptions': [
                'Without -servername you may see the wrong certificate '
                'entirely, because the server picks by the SNI name and you '
                'sent none.',
                's_client hangs after connecting because it is waiting for '
                'you to type. Feed it </dev/null so it finishes and the pipe '
                'gets the output.',
                'A chain that verifies in your browser is not proof the '
                'server sends it. -showcerts reads what actually came down '
                'the wire, browsers cache intermediates.',
            ],
            'try_it': [
                'Run the dates one-liner against a site you use and read when '
                'its certificate expires, without saving a file.',
                'Add -showcerts and count how many certificates the server '
                'sends before the chain stops.',
            ],
            'next': 'os-digest',
        },
        {
            'id': 'os-digest',
            'title': 'Signing, verifying, and encrypting a file',
            'concept':
                'The same key material does three separable things, and '
                'keeping them separate is most of the understanding.\n\n'
                '**Hashing** proves content is unchanged and involves no keys '
                'at all. `openssl dgst -sha256` is `sha256sum` with different '
                'output formatting.\n\n'
                '**Signing** proves who produced something. You sign with a '
                'private key and anyone verifies with the matching public '
                'key. That direction is fixed, and getting it backwards is '
                'the classic confusion: if it could be done with the public '
                'key, everyone could forge it.\n\n'
                '**Encrypting** protects content. Public key encryption is '
                'the other direction: encrypt with the public key so that '
                'only the private key holder can read it. In practice raw '
                'public key encryption is limited to small payloads, so real '
                'systems encrypt the data with a symmetric key and encrypt '
                'only that key asymmetrically. That is what `openssl smime` '
                'and `cms` do for you, and what TLS does on the wire.\n\n'
                '`openssl enc` is the symmetric one, and it deserves a '
                'warning: its defaults have been poor historically, and for '
                'anything real you should reach for age or gpg rather than '
                'hand-rolling with enc.',
            'examples': [
                {'label': 'Hash a file',
                 'code': 'openssl dgst -sha256 report.pdf',
                 'note': 'Same value as sha256sum, different layout.'},
                {'label': 'Sign with the private key',
                 'code': 'openssl dgst -sha256 -sign key.pem -out report.sig '
                         'report.pdf',
                 'note': 'Only the holder of the private key can produce '
                         'this, which is the entire point.'},
                {'label': 'Verify with the public key',
                 'code': 'openssl dgst -sha256 -verify pub.pem -signature '
                         'report.sig report.pdf',
                 'note': 'Prints Verified OK, and a non-zero exit status when '
                         'it is not.'},
                {'label': 'Pull the public key out of a certificate',
                 'code': 'openssl x509 -in cert.pem -pubkey -noout > pub.pem',
                 'note': 'How you verify a signature when all you were given '
                         'is the certificate.'},
                {'label': 'Random bytes, properly',
                 'code': 'openssl rand -base64 32',
                 'note': 'A perfectly good password or key generator, and '
                         'better than most things people reach for.'},
            ],
            'misconceptions': [
                'You do not sign with a public key. Signing is private, '
                'verifying is public, and reversing them makes signatures '
                'forgeable by anyone.',
                'openssl dgst -verify wants a public key file, not a '
                'certificate. Extract the key from the certificate first.',
                'openssl enc is not a good default for encrypting files. Use '
                'gpg or age unless you know exactly why you are not.',
            ],
            'try_it': [
                'Sign a file, verify it, change one byte, and verify again.',
                'Extract a public key from a certificate and verify a '
                'signature with it rather than with the key file.',
            ],
            'next': 'os-practice',
        },
        {
            'id': 'os-practice',
            'title': 'The commands you will actually reach for',
            'concept':
                'openssl has hundreds of subcommands and you will use about '
                'ten. It is worth naming which ten, and the shape of the '
                'command line, because the interface is famously '
                'inconsistent.\n\n'
                'The pattern is `openssl <subcommand> <options>`, where the '
                'subcommand decides what the options mean. `x509` reads and '
                'writes certificates. `req` handles requests and self-signed '
                'certificates. `pkey`, `rsa` and `ec` handle keys. `verify` '
                'checks chains. `dgst` hashes and signs. `s_client` connects. '
                '`pkcs12` converts bundles. `rand` generates randomness. '
                '`enc` does symmetric encryption. `crl` and `ocsp` handle '
                'revocation.\n\n'
                'Two habits pay for themselves. First, `-noout` on anything '
                'that reads a file, unless you actually want the encoded '
                'object printed again. Second, reading the error message '
                'literally: openssl errors are terse and specific, and "unable '
                'to load certificate" almost always means you passed a key, a '
                'DER file without -inform, or a file with something before '
                'the BEGIN line.\n\n'
                'The version matters more than in most tools. OpenSSL 3.x '
                'moved several things, deprecated some algorithms outright, '
                'and changed default behaviours, so a recipe from an old '
                'write-up may fail for reasons that are about the version and '
                'not about you.',
            'examples': [
                {'label': 'Which version, which is worth knowing first',
                 'code': 'openssl version -a',
                 'note': '1.1.1 and 3.x differ enough that old recipes fail '
                         'confusingly.'},
                {'label': 'What can this subcommand do',
                 'code': 'openssl x509 -help',
                 'note': 'Per subcommand help. There is no useful global '
                         'help beyond a list of commands.'},
                {'label': 'The file will not load',
                 'code': 'head -1 mystery.pem; file mystery.pem',
                 'note': 'Nine times in ten the answer is that it is a key, '
                         'or DER, or has junk before the BEGIN line.'},
            ],
            'misconceptions': [
                'Options are not global. -in means something different to '
                'x509 and to enc, and there is no shared convention to lean '
                'on.',
                'An "unable to load" error is usually about the file being a '
                'different thing than you told openssl it was.',
                'Copying a recipe from an old post and having it fail is '
                'often the 1.1.1 to 3.x change rather than a mistake.',
            ],
            'try_it': [
                'Run openssl version -a and note which major version you are '
                'on before following any tutorial.',
                'Deliberately pass a private key to openssl x509 and read the '
                'error, so you recognise it later.',
            ],
            'next': None,
        },
    ],

    'drills': [
        {'id': 'osd-text', 'type': 'command',
         'prompt': 'Print everything in cert.pem in readable form.',
         'answer': 'openssl x509 -in cert.pem -noout -text',
         'teach': 'Without -noout you also get the base64 certificate printed '
                  'again, which is most of the output.'},
        {'id': 'osd-subject', 'type': 'command',
         'prompt': 'Show the subject, issuer and validity dates of cert.pem.',
         'answer': 'openssl x509 -in cert.pem -noout -subject -issuer -dates',
         'teach': 'Who, from whom, until when. When subject equals issuer the '
                  'certificate is self-signed.'},
        {'id': 'osd-san', 'type': 'command',
         'prompt': 'Show which hostnames cert.pem actually covers.',
         'answer': 'openssl x509 -in cert.pem -noout -ext subjectAltName',
         'teach': 'SAN decides host matching. Common Name has not been used '
                  'for it in years.'},
        {'id': 'osd-checkend', 'type': 'command',
         'prompt': 'Check whether cert.pem expires within the next week.',
         'answer': 'openssl x509 -in cert.pem -noout -checkend 604800',
         'teach': 'The answer is the exit status, which is what makes it '
                  'usable from monitoring.'},
        {'id': 'osd-fingerprint', 'type': 'command',
         'prompt': 'Print the SHA-256 fingerprint of cert.pem.',
         'answer': 'openssl x509 -in cert.pem -noout -fingerprint -sha256',
         'teach': 'A hash of the whole certificate, and how two people '
                  'confirm they are looking at the same one.'},
        {'id': 'osd-serial', 'type': 'command',
         'prompt': 'Print the serial number of cert.pem.',
         'answer': 'openssl x509 -in cert.pem -noout -serial',
         'teach': 'Unique per issuer, and what a revocation list refers to.'},
        {'id': 'osd-pem2der', 'type': 'command',
         'prompt': 'Convert cert.pem to binary DER in cert.der.',
         'answer': 'openssl x509 -in cert.pem -outform DER -out cert.der',
         'teach': 'Same certificate, different encoding. PEM is base64 DER '
                  'with header lines.'},
        {'id': 'osd-der2pem', 'type': 'command',
         'prompt': 'Convert the DER file cert.der back to PEM in cert.pem.',
         'answer': 'openssl x509 -inform DER -in cert.der -out cert.pem',
         'teach': '-inform tells openssl what it is reading. Omitting it on a '
                  'DER file is the classic "unable to load" error.'},
        {'id': 'osd-p12-export', 'type': 'command',
         'prompt': 'Bundle key.pem and cert.pem into bundle.p12.',
         'answer': 'openssl pkcs12 -export -inkey key.pem -in cert.pem -out '
                   'bundle.p12',
         'teach': 'One encrypted container, which is what Windows and Java '
                  'want and what most Unix servers do not.'},
        {'id': 'osd-p12-extract', 'type': 'command',
         'prompt': 'Extract everything from bundle.p12 into all.pem unencrypted.',
         'answer': 'openssl pkcs12 -in bundle.p12 -nodes -out all.pem',
         'teach': '-nodes leaves the private key unencrypted in the output, '
                  'which is convenient and a decision.'},
        {'id': 'osd-genrsa', 'type': 'command',
         'prompt': 'Generate a 4096 bit RSA private key into key.pem.',
         'answer': 'openssl genrsa -out key.pem 4096',
         'teach': 'genpkey is the modern general command; genrsa is the one '
                  'everybody types.'},
        {'id': 'osd-genec', 'type': 'command',
         'prompt': 'Generate a prime256v1 elliptic curve key into ec.pem.',
         'answer': 'openssl ecparam -genkey -name prime256v1 -out ec.pem',
         'teach': 'Smaller and faster than RSA, and not universally supported '
                  'by old software.'},
        {'id': 'osd-pubout', 'type': 'command',
         'prompt': 'Write the public key of key.pem to pub.pem.',
         'answer': 'openssl pkey -in key.pem -pubout -out pub.pem',
         'teach': 'The public half is derived from the private key, never the '
                  'other way round.'},
        {'id': 'osd-cert-pubkey', 'type': 'command',
         'prompt': 'Extract the public key from cert.pem into pub.pem.',
         'answer': 'openssl x509 -in cert.pem -pubkey -noout > pub.pem',
         'teach': 'How you verify a signature when all you were given is the '
                  'certificate.'},
        {'id': 'osd-match-cert', 'type': 'command',
         'prompt': 'Hash the public key inside cert.pem so it can be compared.',
         'answer': 'openssl x509 -in cert.pem -noout -pubkey | openssl sha256',
         'teach': 'Half of the match test. The other half is the same hash '
                  'taken from the private key.'},
        {'id': 'osd-match-key', 'type': 'command',
         'prompt': 'Hash the public key derived from key.pem for comparison.',
         'answer': 'openssl pkey -in key.pem -pubout | openssl sha256',
         'teach': 'Identical hashes mean the key and certificate correspond. '
                  'Nothing else checks this until software fails.'},
        {'id': 'osd-modulus', 'type': 'command',
         'prompt': 'Print the RSA modulus of cert.pem for the classic match test.',
         'answer': 'openssl x509 -in cert.pem -noout -modulus',
         'teach': 'RSA only, and the form you will see in every older '
                  'write-up. The pubkey comparison works for EC too.'},
        {'id': 'osd-rmpass', 'type': 'command',
         'prompt': 'Write an unencrypted copy of the encrypted key encrypted.pem.',
         'answer': 'openssl rsa -in encrypted.pem -out plain.pem',
         'teach': 'What unattended services need, and it moves the protection '
                  'entirely onto file permissions.'},
        {'id': 'osd-csr', 'type': 'command',
         'prompt': 'Create a CSR for www.example.com from key.pem without prompts.',
         'answer': 'openssl req -new -key key.pem -out req.csr -subj '
                   '"/CN=www.example.com"',
         'teach': '-subj is a slash separated field list. The twenty '
                  'questions are optional.'},
        {'id': 'osd-csr-san', 'type': 'command',
         'prompt': 'Add a SAN for example.com to a new CSR from key.pem.',
         'answer': 'openssl req -new -key key.pem -out req.csr -subj '
                   '"/CN=example.com" -addext '
                   '"subjectAltName=DNS:example.com"',
         'teach': 'Without the SAN the issued certificate may cover no '
                  'hostname that any browser accepts.'},
        {'id': 'osd-csr-read', 'type': 'command',
         'prompt': 'Read back req.csr and check its self-signature.',
         'answer': 'openssl req -in req.csr -noout -text -verify',
         'teach': 'Catching a typo here costs a second. Catching it after '
                  'issuance costs a reissue.'},
        {'id': 'osd-selfsigned', 'type': 'command',
         'prompt': 'Make a key and a one year self-signed cert for test.local.',
         'answer': 'openssl req -x509 -newkey rsa:2048 -keyout key.pem -out '
                   'cert.pem -days 365 -nodes -subj "/CN=test.local"',
         'teach': 'The line everyone has memorised. -nodes means no '
                  'passphrase, not "nodes".'},
        {'id': 'osd-verify', 'type': 'command',
         'prompt': 'Verify leaf.pem against root.pem with intermediate.pem.',
         'answer': 'openssl verify -CAfile root.pem -untrusted '
                   'intermediate.pem leaf.pem',
         'teach': 'Entirely offline. Read its error messages literally: they '
                  'are terse and precise.'},
        {'id': 'osd-verify-store', 'type': 'command',
         'prompt': 'Verify cert.pem against the system trust store.',
         'answer': 'openssl verify cert.pem',
         'teach': 'With no -CAfile it uses the default store, which is what a '
                  'client on this machine would do.'},
        {'id': 'osd-bundle-list', 'type': 'command',
         'prompt': 'List the subject and issuer of every cert in bundle.pem.',
         'answer': 'openssl crl2pkcs7 -nocrl -certfile bundle.pem | openssl '
                   'pkcs7 -print_certs -noout',
         'teach': 'Chain order matters, and this is how you read the order a '
                  'bundle is actually in.'},
        {'id': 'osd-dgst', 'type': 'command',
         'prompt': 'Compute the SHA-256 digest of report.pdf with openssl.',
         'answer': 'openssl dgst -sha256 report.pdf',
         'teach': 'Same value as sha256sum, laid out differently.'},
        {'id': 'osd-sign', 'type': 'command',
         'prompt': 'Sign report.pdf with key.pem into report.sig.',
         'answer': 'openssl dgst -sha256 -sign key.pem -out report.sig report.pdf',
         'teach': 'Signing is private, verifying is public. Reversed, anyone '
                  'could forge it.'},
        {'id': 'osd-verify-sig', 'type': 'command',
         'prompt': 'Verify report.sig against report.pdf using pub.pem.',
         'answer': 'openssl dgst -sha256 -verify pub.pem -signature '
                   'report.sig report.pdf',
         'teach': 'Wants a public key file, not a certificate. Extract the '
                  'key from the certificate first.'},
        {'id': 'osd-rand', 'type': 'command',
         'prompt': 'Generate 32 random bytes as base64.',
         'answer': 'openssl rand -base64 32',
         'teach': 'A perfectly good password generator, and better than most '
                  'of what people reach for instead.'},
        {'id': 'osd-version', 'type': 'command',
         'prompt': 'Show the openssl version and its build details.',
         'answer': 'openssl version -a',
         'teach': '1.1.1 and 3.x differ enough that an old recipe failing is '
                  'often the version rather than you.'},
        {'id': 'osd-sclient', 'type': 'command',
         'prompt': 'Open a TLS connection and print the handshake and chain.',
         'answer': 'openssl s_client -connect example.com:443',
         'teach': 'Shows the certificate the server actually serves. Add '
                  '-servername to pick the right name by SNI.'},
        {'id': 'osd-sclient-dates', 'type': 'command',
         'prompt': 'Read the expiry of a live server certificate in one line.',
         'answer': 'openssl s_client -connect example.com:443 -servername '
                   'example.com </dev/null 2>/dev/null | openssl x509 -noout '
                   '-dates',
         'teach': '</dev/null closes the connection that would otherwise hang, '
                  'and the pipe reads the returned certificate.'},
    ],

    'challenges': [
        {
            'id': 'osc-selfsigned',
            'title': 'Make a certificate and read it back',
            'goal': 'Generate a key and a self-signed certificate in one '
                    'command, then prove you can read every field that '
                    'matters out of it.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {'.keep': ''}},
            'solution': {'shell': 'openssl req -x509 -newkey rsa:2048 '
                                  '-keyout key.pem -out cert.pem -days 365 '
                                  '-nodes -subj "/CN=hone.lab" 2>/dev/null && '
                                  'openssl x509 -in cert.pem -noout -subject '
                                  '-issuer -dates > fields.txt'},
            'steps': [
                {'instruction': 'Generate a 2048 bit key and a one year '
                                'self-signed certificate for CN=hone.lab, '
                                'with no passphrase.',
                 'hint': 'openssl req -x509 -newkey rsa:2048 -keyout key.pem '
                         '-out cert.pem -days 365 -nodes -subj "/CN=hone.lab"'},
                {'instruction': 'Write the subject, issuer and dates into '
                                'fields.txt.',
                 'hint': 'openssl x509 -in cert.pem -noout -subject -issuer '
                         '-dates > fields.txt'},
                {'instruction': 'Read fields.txt. Subject and issuer are the '
                                'same, which is what self-signed means.'},
            ],
            'free': 'Produce key.pem, cert.pem for CN=hone.lab, and '
                    'fields.txt holding its subject, issuer and dates.',
            'verify': {'kind': 'sandbox', 'expect': {
                'is_file': ['key.pem', 'cert.pem', 'fields.txt'],
                'file_contains': {'cert.pem': 'BEGIN CERTIFICATE',
                                  'key.pem': 'PRIVATE KEY',
                                  'fields.txt': ['subject=CN=hone.lab',
                                                 'issuer=CN=hone.lab',
                                                 'notAfter']}}},
            'fallback': 'self',
        },
        {
            'id': 'osc-match',
            'title': 'Prove which key goes with the certificate',
            'goal': 'Two keys, one certificate. Establish mechanically which '
                    'key belongs to it rather than guessing from filenames.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {'.keep': ''}},
            'solution': {'shell': 'openssl req -x509 -newkey rsa:2048 '
                                  '-keyout real.key -out cert.pem -days 30 '
                                  '-nodes -subj "/CN=match.test" 2>/dev/null && '
                                  'openssl genrsa -out other.key 2048 '
                                  '2>/dev/null && '
                                  'openssl x509 -in cert.pem -noout -pubkey | '
                                  'openssl sha256 > from-cert.txt && '
                                  'openssl pkey -in real.key -pubout | '
                                  'openssl sha256 > from-real.txt && '
                                  'openssl pkey -in other.key -pubout | '
                                  'openssl sha256 > from-other.txt'},
            'steps': [
                {'instruction': 'Make a self-signed cert with real.key, and '
                                'separately generate an unrelated other.key.',
                 'hint': 'openssl req -x509 -newkey rsa:2048 -keyout real.key '
                         '-out cert.pem -days 30 -nodes -subj "/CN=match.test"'},
                {'instruction': 'Hash the public key inside the certificate '
                                'into from-cert.txt.',
                 'hint': 'openssl x509 -in cert.pem -noout -pubkey | openssl '
                         'sha256 > from-cert.txt'},
                {'instruction': 'Do the same for both private keys, into '
                                'from-real.txt and from-other.txt.',
                 'hint': 'openssl pkey -in real.key -pubout | openssl sha256 '
                         '> from-real.txt'},
                {'instruction': 'Compare the three. One matches and one does '
                                'not, and now you can always tell.',
                 'hint': 'diff from-cert.txt from-real.txt'},
            ],
            'free': 'Produce from-cert.txt, from-real.txt and from-other.txt: '
                    'public key hashes proving which of two keys belongs to '
                    'the certificate.',
            'verify': {'kind': 'sandbox', 'expect': {
                'is_file': ['cert.pem', 'real.key', 'other.key',
                            'from-cert.txt', 'from-real.txt', 'from-other.txt']}},
            'fallback': 'self',
        },
        {
            'id': 'osc-csr',
            'title': 'Build a CSR with a SAN that survives',
            'goal': 'Request a certificate for more than one hostname, and '
                    'read the request back to confirm the names are in it.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {'.keep': ''}},
            'solution': {'shell': 'openssl genrsa -out site.key 2048 '
                                  '2>/dev/null && '
                                  'openssl req -new -key site.key -out '
                                  'site.csr -subj "/CN=example.test" -addext '
                                  '"subjectAltName=DNS:example.test,'
                                  'DNS:www.example.test" 2>/dev/null && '
                                  'openssl req -in site.csr -noout -text '
                                  '> csr.txt'},
            'steps': [
                {'instruction': 'Generate a 2048 bit key called site.key.',
                 'hint': 'openssl genrsa -out site.key 2048'},
                {'instruction': 'Create site.csr for CN=example.test with a '
                                'SAN covering example.test and '
                                'www.example.test.',
                 'hint': 'openssl req -new -key site.key -out site.csr -subj '
                         '"/CN=example.test" -addext '
                         '"subjectAltName=DNS:example.test,DNS:www.example.test"'},
                {'instruction': 'Dump the request to csr.txt and confirm both '
                                'names are actually in it.',
                 'hint': 'openssl req -in site.csr -noout -text > csr.txt'},
            ],
            'free': 'Produce site.key, site.csr covering example.test and '
                    'www.example.test in a SAN, and csr.txt showing them.',
            'verify': {'kind': 'sandbox', 'expect': {
                'is_file': ['site.key', 'site.csr', 'csr.txt'],
                'file_contains': {'site.csr': 'CERTIFICATE REQUEST',
                                  'csr.txt': ['example.test',
                                              'www.example.test']}}},
            'fallback': 'self',
        },
        {
            'id': 'osc-formats',
            'title': 'Convert between the formats without losing anything',
            'goal': 'Take one certificate through PEM, DER and back, and '
                    'prove the round trip changed nothing.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {'.keep': ''}},
            'solution': {'shell': 'openssl req -x509 -newkey rsa:2048 '
                                  '-keyout k.pem -out cert.pem -days 30 '
                                  '-nodes -subj "/CN=convert.test" '
                                  '2>/dev/null && '
                                  'openssl x509 -in cert.pem -outform DER '
                                  '-out cert.der && '
                                  'openssl x509 -inform DER -in cert.der '
                                  '-out roundtrip.pem && '
                                  'openssl x509 -in cert.pem -noout '
                                  '-fingerprint -sha256 > fp1.txt && '
                                  'openssl x509 -in roundtrip.pem -noout '
                                  '-fingerprint -sha256 > fp2.txt'},
            'steps': [
                {'instruction': 'Make a throwaway self-signed certificate as '
                                'cert.pem.',
                 'hint': 'openssl req -x509 -newkey rsa:2048 -keyout k.pem '
                         '-out cert.pem -days 30 -nodes -subj "/CN=convert.test"'},
                {'instruction': 'Convert it to DER as cert.der, then back to '
                                'PEM as roundtrip.pem.',
                 'hint': 'openssl x509 -in cert.pem -outform DER -out cert.der'},
                {'instruction': 'Fingerprint both PEM files into fp1.txt and '
                                'fp2.txt. They must be identical.',
                 'hint': 'openssl x509 -in cert.pem -noout -fingerprint '
                         '-sha256 > fp1.txt'},
            ],
            'free': 'Produce cert.pem, cert.der, roundtrip.pem, and matching '
                    'fingerprints in fp1.txt and fp2.txt.',
            'verify': {'kind': 'sandbox', 'expect': {
                'is_file': ['cert.pem', 'cert.der', 'roundtrip.pem',
                            'fp1.txt', 'fp2.txt'],
                'file_contains': {'roundtrip.pem': 'BEGIN CERTIFICATE',
                                  'fp1.txt': 'Fingerprint'}}},
            'fallback': 'self',
        },
        {
            'id': 'osc-sign-verify',
            'title': 'Sign a file, then break the signature',
            'goal': 'Sign with a private key, verify with the public one, '
                    'then change a byte and watch verification fail.',
            'setup': {'kind': 'sandbox', 'shell': 'bash',
                      'tree': {'report.txt': 'the quarterly figures\n'}},
            'solution': {'shell': 'openssl genrsa -out signer.key 2048 '
                                  '2>/dev/null && '
                                  'openssl pkey -in signer.key -pubout -out '
                                  'signer.pub && '
                                  'openssl dgst -sha256 -sign signer.key -out '
                                  'report.sig report.txt && '
                                  'openssl dgst -sha256 -verify signer.pub '
                                  '-signature report.sig report.txt > ok.txt && '
                                  'cp report.txt tampered.txt && '
                                  'echo "and a forged line" >> tampered.txt && '
                                  'openssl dgst -sha256 -verify signer.pub '
                                  '-signature report.sig tampered.txt '
                                  '> bad.txt 2>&1; true'},
            'steps': [
                {'instruction': 'Generate signer.key and write its public '
                                'half to signer.pub.',
                 'hint': 'openssl pkey -in signer.key -pubout -out signer.pub'},
                {'instruction': 'Sign report.txt into report.sig, then verify '
                                'it and save the result in ok.txt.',
                 'hint': 'openssl dgst -sha256 -sign signer.key -out '
                         'report.sig report.txt'},
                {'instruction': 'Copy the file to tampered.txt, change it, '
                                'and verify the old signature against it into '
                                'bad.txt.',
                 'hint': 'openssl dgst -sha256 -verify signer.pub -signature '
                         'report.sig tampered.txt > bad.txt 2>&1'},
            ],
            'free': 'Produce report.sig, ok.txt showing a good verification, '
                    'and bad.txt showing the same signature failing against a '
                    'modified file.',
            'verify': {'kind': 'sandbox', 'expect': {
                'is_file': ['signer.key', 'signer.pub', 'report.sig'],
                'file_contains': {'ok.txt': 'Verified OK'},
                'file_lacks': {'bad.txt': 'Verified OK'}}},
            'fallback': 'self',
        },
        {
            'id': 'osc-chain',
            'title': 'Build a chain, then break it on purpose',
            'goal': 'Act as your own CA, issue a leaf, and see exactly what '
                    '"unable to get local issuer certificate" means.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {'.keep': ''}},
            'solution': {'shell':
                'openssl req -x509 -newkey rsa:2048 -keyout ca.key -out '
                'ca.pem -days 365 -nodes -subj "/CN=hone Test CA" '
                '2>/dev/null && '
                'openssl genrsa -out leaf.key 2048 2>/dev/null && '
                'openssl req -new -key leaf.key -out leaf.csr -subj '
                '"/CN=leaf.test" 2>/dev/null && '
                'openssl x509 -req -in leaf.csr -CA ca.pem -CAkey ca.key '
                '-CAcreateserial -out leaf.pem -days 30 2>/dev/null && '
                'openssl verify -CAfile ca.pem leaf.pem > good.txt 2>&1; '
                'openssl verify leaf.pem > bad.txt 2>&1; true'},
            'steps': [
                {'instruction': 'Make your own CA: a self-signed certificate '
                                'ca.pem with key ca.key.',
                 'hint': 'openssl req -x509 -newkey rsa:2048 -keyout ca.key '
                         '-out ca.pem -days 365 -nodes -subj "/CN=hone Test CA"'},
                {'instruction': 'Make a key and CSR for leaf.test, then sign '
                                'the CSR with your CA into leaf.pem.',
                 'hint': 'openssl x509 -req -in leaf.csr -CA ca.pem -CAkey '
                         'ca.key -CAcreateserial -out leaf.pem -days 30'},
                {'instruction': 'Verify the leaf against your CA into '
                                'good.txt.',
                 'hint': 'openssl verify -CAfile ca.pem leaf.pem > good.txt 2>&1'},
                {'instruction': 'Now verify it without naming the CA, into '
                                'bad.txt, and read the error carefully.',
                 'hint': 'openssl verify leaf.pem > bad.txt 2>&1'},
            ],
            'free': 'Produce ca.pem, leaf.pem signed by it, good.txt showing '
                    'a successful verify, and bad.txt showing the failure '
                    'when the issuer is not available.',
            'verify': {'kind': 'sandbox', 'expect': {
                'is_file': ['ca.pem', 'leaf.pem', 'good.txt', 'bad.txt'],
                'file_contains': {'good.txt': 'OK',
                                  'bad.txt': 'local issuer'}}},
            'fallback': 'self',
        },
        {
            'id': 'osc-real-cert',
            'title': 'Read a certificate from something you use',
            'goal': 'Everything above was generated. Take a real certificate '
                    'off a real service and read it the same way.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'Fetch the certificate a site presents and '
                                'save it.',
                 'hint': 'openssl s_client -connect example.com:443 '
                         '-servername example.com < /dev/null 2>/dev/null | '
                         'openssl x509 > site.pem'},
                {'instruction': 'Read its subject, issuer, dates and SAN. '
                                'Does the SAN cover the name you typed?'},
                {'instruction': 'Look at the chain the server sent, and check '
                                'whether it included the intermediates.',
                 'hint': 'openssl s_client -connect example.com:443 '
                         '-showcerts < /dev/null'},
                {'instruction': 'Check how long you have before it expires.',
                 'hint': 'openssl x509 -in site.pem -noout -checkend 2592000'},
            ],
            'free': 'On your own machine and network: fetch a real '
                    'certificate, read its fields, inspect the chain the '
                    'server sent, and check its remaining lifetime.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
    ],

    'quiz': [
        {'id': 'osq-pem', 'type': 'mcq',
         'prompt': 'What is the relationship between PEM and DER?',
         'answer': 'PEM is DER, base64 encoded, with BEGIN and END lines '
                   'added.',
         'distractors': ['They are different certificate standards.',
                         'DER holds the key and PEM holds the certificate.',
                         'PEM is newer and supports more algorithms.'],
         'teach': 'One structure, two encodings. -inform and -outform are the '
                  'whole conversion.'},
        {'id': 'osq-san', 'type': 'mcq',
         'prompt': 'A certificate has CN=www.example.com and no SAN. A browser '
                   'rejects it. Why?',
         'answer': 'Hostname matching uses Subject Alternative Name, and '
                   'browsers stopped falling back to CN.',
         'distractors': ['The CN must be a bare domain, not a subdomain.',
                         'The certificate needs an Extended Key Usage of '
                         'serverAuth to be matched.',
                         'CN matching only works for certificates from a '
                         'public CA.'],
         'teach': 'Put the names in a SAN with -addext. A missing SAN is the '
                  'commonest reason a hand-made certificate fails.'},
        {'id': 'osq-selfsigned', 'type': 'mcq',
         'prompt': 'How do you tell a self-signed certificate from its fields?',
         'answer': 'Subject and issuer are identical.',
         'distractors': ['It has no serial number.',
                         'Its validity period is under 90 days.',
                         'The Basic Constraints extension is absent.'],
         'teach': 'Self-signed is a description of the relationship, not a '
                  'separate format or a flag stored in the file.'},
        {'id': 'osq-match', 'type': 'mcq',
         'prompt': 'A server starts but TLS fails oddly. You suspect the key '
                   'does not match the certificate. How do you check?',
         'answer': 'Hash the public key from each and compare the two hashes.',
         'distractors': ['Check that the two files have the same modification '
                         'time.',
                         'Run openssl verify on the certificate.',
                         'Compare the fingerprints of the certificate and the '
                         'key.'],
         'teach': 'openssl x509 -pubkey against openssl pkey -pubout, both '
                  'piped to sha256. Works for RSA and EC alike.'},
        {'id': 'osq-intermediate', 'type': 'mcq',
         'prompt': 'A site works in your browser and fails with curl on a '
                   'fresh machine. What is the usual cause?',
         'answer': 'The server is not sending its intermediate certificate, '
                   'and your browser had cached it.',
         'distractors': ['The certificate has expired but browsers allow a '
                         'grace period.',
                         'curl does not support the cipher the server chose.',
                         'The system clock on the fresh machine is wrong.'],
         'teach': 'Send leaf plus intermediates, in order, and not the root. '
                  'This is the most common TLS misconfiguration there is.'},
        {'id': 'osq-nodes', 'type': 'mcq',
         'prompt': 'What does -nodes do in openssl req?',
         'answer': 'Writes the private key without a passphrase.',
         'distractors': ['Creates the certificate without extensions.',
                         'Disables the interactive subject prompts.',
                         'Omits the DN nodes from the subject.'],
         'teach': 'It is "no DES", meaning do not encrypt the key. -subj is '
                  'the one that skips the prompts.'},
        {'id': 'osq-signdir', 'type': 'mcq',
         'prompt': 'Which key signs, and which key verifies?',
         'answer': 'The private key signs and the public key verifies.',
         'distractors': ['The public key signs and the private key verifies.',
                         'Either can do both, since they are a pair.',
                         'The certificate signs and the private key verifies.'],
         'teach': 'If a public key could sign, everyone holding it could '
                  'forge signatures. The direction is the whole point.'},
        {'id': 'osq-unable-load', 'type': 'mcq',
         'prompt': 'openssl x509 -in server.crt says "unable to load '
                   'certificate". Most likely cause?',
         'answer': 'The file is DER, or is actually a key, or has text before '
                   'the BEGIN line.',
         'distractors': ['The certificate uses an algorithm this build '
                         'lacks.',
                         'The file permissions are too restrictive.',
                         'The certificate has expired.'],
         'teach': 'Read the first line with head -1. That answers it nine '
                  'times in ten.'},
        {'id': 'osq-checkend', 'type': 'mcq',
         'prompt': 'How does openssl x509 -checkend report its answer?',
         'answer': 'Through the exit status, which is why it suits '
                   'monitoring.',
         'distractors': ['By printing the expiry date in ISO format.',
                         'By writing to stderr when the certificate is '
                         'valid.',
                         'By returning the number of days remaining.'],
         'teach': 'It also prints a line, but the exit status is the part a '
                  'script uses.'},
        {'id': 'osq-p12', 'type': 'mcq',
         'prompt': 'What is inside a .p12 file?',
         'answer': 'A private key, its certificate and usually the chain, in '
                   'one encrypted container.',
         'distractors': ['A certificate only, in binary DER form.',
                         'A certificate chain with no private key.',
                         'A PKCS#10 signing request awaiting issuance.'],
         'teach': 'Windows and Java want this shape; most Unix servers want '
                  'the PEM pieces, so converting is a routine chore.'},
    ],
}
