"""The weblab adapter: a small website the trainer serves to itself.

Same argument as `netlab`, one layer up. Web content discovery is learned by
pointing a tool at a site and reading what comes back, and D1 forbids pointing
anything at a site the trainer does not own. So the trainer owns one: an
`http.server` bound to 127.0.0.1, serving a tree this adapter wrote, torn down
with the challenge.

**What the tree is for.** A content discovery exercise is only meaningful if
there is something to discover, and if the responses differ in the ways the
tools filter on. So the site is built with deliberate structure: paths that
exist and paths that do not, a directory that lists and one that is forbidden,
a page whose size and word count differ from the 404 body, and a virtual host
that only answers to the right `Host:` header. Each of those exists because it
is what one of `ffuf`'s filters is *for*, and a lab where every wrong answer
looks identical teaches nothing about filtering.

**Why the 404 body is padded.** The single most common beginner failure with
`ffuf` and `gobuster` is a site that returns 200 for everything, where the only
way through is filtering by size or word count. Serving a chunky, constant-size
404 makes `-fs` and `-fw` demonstrable rather than theoretical.

**Availability.** Unlike the other adapters this one does not require the tool
being taught, because the thing that must exist is the *server*, and that is
stdlib. It needs some HTTP client to be installed to be useful at all, so it
probes for any of the three the module names. `curl` is present nearly
everywhere, which means the module still verifies real work on a machine with
no fuzzer installed: you find the paths by hand, more slowly, which is a
legitimate way to learn what the fuzzer is doing for you.
"""

from __future__ import annotations

import shutil
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from .sandbox import EXPECT_KEYS, SandboxAdapter
from . import Observation

#: Clients that can drive this lab, in the order the content prefers them.
CLIENTS = ('ffuf', 'gobuster', 'curl')

#: Served from `www/` inside the sandbox. Everything outside `www/` is the
#: student's working directory, so output files never collide with content.
ROOT = 'www'

#: Padded so its size and word count differ visibly from a real page, which is
#: what makes `-fs`, `-fw` and `-fc` teachable.
NOT_FOUND_BODY = (
    '<html><head><title>Not Found</title></head><body>\n'
    '<h1>404</h1><p>The page you asked for is not on this server.</p>\n'
    '<p>This is a lab served by hone on loopback. Nothing here is real.</p>\n'
    '<p>Filtering practice: every miss returns exactly this body.</p>\n'
    '</body></html>\n'
)

DEFAULT_SITE = {
    'index.html': '<html><body><h1>hone lab</h1></body></html>\n',
    'robots.txt': 'User-agent: *\nDisallow: /admin\nDisallow: /backup\n',
    'admin/index.html': '<html><body><h1>admin</h1><p>secret</p></body></html>\n',
    'backup/notes.txt': 'db password rotation is overdue\n',
    'uploads/': None,
}

#: Answers only when the Host header matches. The trainer serves it from a
#: separate subtree so the vhost lesson is a real behavioural difference
#: rather than a claim in the prose.
DEFAULT_VHOST = 'dev.hone.lab'
VHOST_BODY = ('<html><body><h1>dev</h1><p>virtual host only</p></body></html>\n')


class _Handler(SimpleHTTPRequestHandler):
    """Serves the tree, with the response variety the lesson needs."""

    def __init__(self, *args, vhost: str = '', hits=None, **kw) -> None:
        self._vhost = vhost
        self._hits = hits if hits is not None else []
        super().__init__(*args, **kw)

    def log_message(self, fmt, *args) -> None:
        """Silent: the trainer owns this terminal and a request log would
        scribble over whatever the student is reading."""

    def _record(self) -> None:
        self._hits.append(self.path)

    def _special(self, body_too: bool) -> bool:
        """Handle the two responses the lesson needs. True if we answered.

        Shared by GET and HEAD deliberately. When this lived only in do_GET,
        `curl -I` on the forbidden path fell through to the ordinary handler
        and returned 200, so the module's own "403 means it is really there"
        challenge failed against its own lab. A student would have read that
        as their mistake.
        """
        host = (self.headers.get('Host') or '').split(':')[0]
        if self._vhost and host == self._vhost:
            body = VHOST_BODY.encode()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            if body_too:
                self.wfile.write(body)
            return True
        # A forbidden path is a distinct status, which is what makes -fc and
        # -mc worth teaching: 403 usually means the path is real.
        if self.path.rstrip('/').endswith('/uploads'):
            self.send_error(403, 'Forbidden')
            return True
        return False

    def do_GET(self) -> None:  # noqa: N802 (stdlib naming)
        self._record()
        if self._special(body_too=True):
            return
        super().do_GET()

    def do_HEAD(self) -> None:  # noqa: N802 (stdlib naming)
        self._record()
        if self._special(body_too=False):
            return
        super().do_HEAD()

    def send_error(self, code, message=None, explain=None) -> None:
        if code == 404:
            body = NOT_FOUND_BODY.encode()
            self.send_response(404)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            try:
                self.wfile.write(body)
            except OSError:
                pass
            return
        super().send_error(code, message, explain)


class WeblabAdapter(SandboxAdapter):
    """A sandbox directory, plus a site on loopback to point a tool at."""

    name = 'weblab'
    requires = ()
    description = 'serves a site on loopback and reads what you found'
    expect_keys = EXPECT_KEYS | frozenset({'requested', 'not_requested'})

    def __init__(self) -> None:
        super().__init__()
        self.server: ThreadingHTTPServer | None = None
        self.thread: threading.Thread | None = None
        self.port = 0
        self.hits: list[str] = []

    def probe(self) -> tuple[bool, str]:
        if not any(shutil.which(c) for c in CLIENTS):
            return False, f'none of {", ".join(CLIENTS)} installed'
        return True, ''

    def opens(self, spec: dict) -> str:
        return (f'Enter hands you a shell in a throwaway directory. The '
                f'trainer is serving a small site at http://127.0.0.1:{self.port}/ '
                f'from that directory. It is loopback only: nothing leaves '
                f'this machine.')

    # -- lifecycle ---------------------------------------------------------

    def setup(self, spec: dict) -> None:
        tree = dict(spec.get('tree') or {})
        site = spec.get('site')
        site = DEFAULT_SITE if site is None else site
        for rel, what in site.items():
            tree[f'{ROOT}/{rel}'] = what
        super().setup({**spec, 'tree': tree})
        self._serve(spec)
        self._write_target()

    def _serve(self, spec: dict) -> None:
        self._stop_server()
        if self.dir is None:
            return
        self.hits = []
        handler = partial(_Handler,
                          directory=str(self.dir / ROOT),
                          vhost=str(spec.get('vhost') or DEFAULT_VHOST),
                          hits=self.hits)
        try:
            self.server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
        except OSError:
            self.server = None
            return
        self.server.daemon_threads = True
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever,
                                       kwargs={'poll_interval': 0.2},
                                       daemon=True)
        self.thread.start()

    def _write_target(self) -> None:
        if self.dir is None:
            return
        (self.dir / 'target.txt').write_text(
            f'http://127.0.0.1:{self.port}/\n'
            f'# Served by hone from ./{ROOT}. Loopback only.\n'
            f'# A virtual host answers on this port too: {DEFAULT_VHOST}\n',
            encoding='utf-8')

    def handoff_env(self, spec: dict) -> dict[str, str]:
        """Hand the URL over as `$TARGET` as well as in the file.

        A fuzzer command line is long enough already, and a student retyping a
        random high port is a student debugging a typo instead of a filter.
        """
        env = dict(super().handoff_env(spec))
        env['TARGET'] = f'http://127.0.0.1:{self.port}'
        return env

    def teardown(self) -> None:
        self._stop_server()
        super().teardown()

    def _stop_server(self) -> None:
        if self.server is not None:
            try:
                self.server.shutdown()
                self.server.server_close()
            except Exception:
                pass
            self.server = None
        if self.thread is not None:
            self.thread.join(timeout=2.0)
            self.thread = None

    # -- observation -------------------------------------------------------

    def observe(self) -> Observation:
        obs = super().observe()
        data = dict(obs.data)
        data['hits'] = list(self.hits)
        data['port'] = self.port
        return Observation(obs.ok, data, obs.detail)

    def check(self, expect: dict, data: dict) -> tuple[bool, str]:
        """Grade the files you saved, and what the server actually saw.

        The request log is the half a file cannot fake. A challenge that only
        checked the saved output would pass for a student who guessed the
        answer and typed it into a text file, which is precisely the honesty
        problem D8 exists to prevent.
        """
        expect = dict(expect)
        hits = data.get('hits') or []
        for path in _as_list(expect.pop('requested', None)):
            if not any(path in h for h in hits):
                return False, (f'nothing ever requested {path}: the server '
                               f'saw {len(hits)} request(s)')
        for path in _as_list(expect.pop('not_requested', None)):
            if any(path in h for h in hits):
                return False, f'{path} was requested, and this task asked you not to'
        return super().check(expect, data)


def _as_list(v) -> list[str]:
    if v is None:
        return []
    return [str(v)] if isinstance(v, str) else [str(x) for x in v]
