"""The netlab adapter: a scan target the trainer builds out of its own sockets.

**Why this exists.** D1 says the trainer never touches a target on a network,
and that rule is not negotiable: a training tool that quietly makes outbound
connections is not a tool you can hand to a stranger. Read literally it also
makes an nmap module unverifiable, which was the argument for skipping nmap
entirely in the first draft of the roster.

The way out is the same one the sandbox adapter already uses for the
filesystem. D1's second clause permits the trainer to **create and destroy its
own sandbox**, so rather than pointing you at someone else's host, the trainer
*becomes* the host: it opens listening sockets on 127.0.0.1, tells you which
ports they are on, and reads your scan output back afterwards. Nothing leaves
the machine, the target is made of sockets this process owns, and they are all
closed on teardown.

That turns nmap from the roster's least verifiable module into one of its most
verifiable, because a port state is an unusually crisp thing to check: the
trainer knows exactly which ports it opened, so it knows exactly what a correct
scan must have found.

**Why the output file rather than the terminal.** The trainer cannot see what
scrolled past in the handover, so challenges ask for `-oN scan.txt` in the
sandbox and grade the file. That is not a workaround dressed up as teaching:
`-oN` / `-oX` / `-oG` and the reasons to keep scan output are real nmap
practice, and a scan you cannot show anyone afterwards is a scan you did twice.

**Ports are dynamic, expectations are not.** A fixed port number is a port that
is occupied on someone's machine one day in fifty. Setup asks for the ports the
challenge wants and falls back to whatever the kernel gives when one is taken,
then `check` substitutes the real numbers into the expectation, so content can
say `{p1}` and mean "the first port we actually opened".

**Unprivileged by design.** A SYN scan needs root, and this adapter never asks
for it. Against loopback listeners an unprivileged connect scan is exactly as
informative, and the difference between `-sS` and `-sT` is taught as content
rather than demonstrated by escalating a trainer's privileges.
"""

from __future__ import annotations

import shutil
import socket
import threading

from .sandbox import EXPECT_KEYS, SandboxAdapter
from . import Observation

#: What each listener says when something connects, so `-sV` has something to
#: chew on. Deliberately not an imitation of a real service version string:
#: the point is to show that a banner is where version detection gets most of
#: its confidence, not to fake a vulnerable daemon.
DEFAULT_BANNER = 'hone-lab service, this port is a socket the trainer opened\r\n'

#: Ports a challenge gets when it does not care which. High, odd and unlikely
#: to collide with anything a developer runs.
DEFAULT_PORTS = (9101, 9102, 9103)

#: Long enough for a slow scan of a handful of ports, short enough that a
#: forgotten thread cannot outlive the challenge by much.
ACCEPT_TIMEOUT = 0.5


class _Listener:
    """One loopback socket, accepting and greeting until it is closed.

    Accepting matters for two of the three things nmap can tell you here. A
    bare listening socket is enough for the kernel to answer a connect scan,
    so the port reads `open` either way, but `-sV` needs something to read and
    a connection that is never accepted stalls the scan instead of finishing
    it.
    """

    def __init__(self, port: int, banner: str) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('127.0.0.1', port))
        self.sock.listen(8)
        self.sock.settimeout(ACCEPT_TIMEOUT)
        self.port = self.sock.getsockname()[1]
        self.banner = banner
        self.hits = 0
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()

    def _serve(self) -> None:
        while not self._stop.is_set():
            try:
                conn, _ = self.sock.accept()
            except (OSError, socket.timeout):
                continue
            self.hits += 1
            try:
                conn.settimeout(ACCEPT_TIMEOUT)
                conn.sendall(self.banner.encode())
            except OSError:
                pass
            finally:
                try:
                    conn.close()
                except OSError:
                    pass

    def close(self) -> None:
        self._stop.set()
        try:
            self.sock.close()
        except OSError:
            pass
        self._thread.join(timeout=2.0)


class NetlabAdapter(SandboxAdapter):
    """A sandbox directory, plus loopback ports for something to scan."""

    name = 'netlab'
    requires = ('nmap',)
    description = 'scans ports the trainer opened on loopback, and reads the result'
    #: The sandbox keys, plus one of our own: `scanned` asserts that traffic
    #: actually arrived, which is the only way to tell a real scan from a
    #: hand-written output file.
    expect_keys = EXPECT_KEYS | frozenset({'scanned'})

    def __init__(self) -> None:
        super().__init__()
        self.listeners: list[_Listener] = []

    def probe(self) -> tuple[bool, str]:
        """Check for nmap, rather than inheriting the sandbox's always-yes.

        The sandbox needs nothing installed because the tool it verifies is
        the filesystem. This one genuinely needs nmap, and inheriting the
        cheerful answer meant the picker promised verification on a machine
        that could not deliver it: the precise failure D18 exists to prevent.
        """
        missing = [b for b in self.requires if not shutil.which(b)]
        if missing:
            return False, f'{", ".join(missing)} not installed'
        return True, ''

    # -- lifecycle ---------------------------------------------------------

    def opens(self, spec: dict) -> str:
        n = len(spec.get('ports') or DEFAULT_PORTS)
        return (f'Enter hands you a shell in a throwaway directory. The '
                f'trainer has opened {n} listening '
                f'port{"" if n == 1 else "s"} on 127.0.0.1 for you to scan, '
                f'and targets.txt lists them. Nothing leaves this machine.')

    def setup(self, spec: dict) -> None:
        super().setup(spec)
        self._open_ports(spec)
        self._write_targets()

    def _open_ports(self, spec: dict) -> None:
        self._close_ports()
        banner = str(spec.get('banner') or DEFAULT_BANNER)
        for want in (spec.get('ports') or DEFAULT_PORTS):
            try:
                self.listeners.append(_Listener(int(want), banner))
            except OSError:
                # Occupied, or refused. Take whatever the kernel offers: the
                # challenge is about reading a scan, not about a magic number.
                try:
                    self.listeners.append(_Listener(0, banner))
                except OSError:
                    continue

    def _write_targets(self) -> None:
        """Tell the student what the trainer opened.

        In the sandbox rather than only on the brief screen, because the brief
        is gone by the time you are typing the scan, and a target list you
        have to remember is a target list you get wrong.
        """
        if self.dir is None:
            return
        lines = ['# Ports the trainer opened on 127.0.0.1 for this challenge.',
                 '# They are sockets in the hone process. Nothing else is a target.']
        lines += [str(l.port) for l in self.listeners]
        (self.dir / 'targets.txt').write_text('\n'.join(lines) + '\n',
                                              encoding='utf-8')

    def ports(self) -> list[int]:
        return [l.port for l in self.listeners]

    def teardown(self) -> None:
        self._close_ports()
        super().teardown()

    def _close_ports(self) -> None:
        for l in self.listeners:
            l.close()
        self.listeners = []

    # -- observation -------------------------------------------------------

    def observe(self) -> Observation:
        obs = super().observe()
        data = dict(obs.data)
        data['ports'] = self.ports()
        data['connections'] = sum(l.hits for l in self.listeners)
        return Observation(obs.ok, data, obs.detail)

    def check(self, expect: dict, data: dict) -> tuple[bool, str]:
        """Substitute the real port numbers, then grade as a sandbox.

        Content writes `{p1}` and gets whichever port actually opened first,
        so an expectation stays honest on a machine where 9101 was taken.
        """
        ports = data.get('ports') or []
        expect = _substitute(expect, ports)

        # A scan that never reached us cannot have produced a real result, and
        # a file the student pasted by hand would otherwise pass. This is the
        # netlab equivalent of the pcap adapter refusing an empty selection.
        if expect.pop('scanned', False) and not data.get('connections'):
            return False, ('nothing connected to the lab ports, so no scan '
                           'reached them: was the target 127.0.0.1?')
        return super().check(expect, data)


def _substitute(value, ports: list[int]):
    """Replace `{pN}` placeholders anywhere inside an expectation."""
    if isinstance(value, str):
        for i, port in enumerate(ports, start=1):
            value = value.replace('{p%d}' % i, str(port))
        return value
    if isinstance(value, dict):
        return {k: _substitute(v, ports) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_substitute(v, ports) for v in value]
    return value
