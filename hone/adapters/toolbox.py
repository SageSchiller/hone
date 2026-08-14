"""Sandboxes that also need a particular binary installed.

Structurally this is the smallest adapter in the project, and it exists for a
reason worth writing down. The sandbox adapter answers "is it available" with
an unconditional yes, because the tool it verifies is the filesystem. Any
subclass whose challenges actually run a program inherits that yes and
therefore *promises verification it cannot deliver*: the challenge is planned
as verified, the solution fails because the binary is missing, and the student
is told their correct answer was wrong.

D18 says a module whose adapter is missing degrades to self-marked and says so.
This class is what makes that true for a filesystem-shaped module whose work
happens to be done by an external binary. `netlab` fixed the same bug for nmap
by overriding `probe`; this is that fix, named, so the next such module is
three lines rather than a rediscovery.
"""

from __future__ import annotations

import shutil

from .sandbox import SandboxAdapter


class ToolSandbox(SandboxAdapter):
    """A sandbox whose availability depends on `requires` being installed."""

    def probe(self) -> tuple[bool, str]:
        missing = [b for b in self.requires if not shutil.which(b)]
        if missing:
            return False, f'{", ".join(missing)} not installed'
        return True, ''


class YaraLabAdapter(ToolSandbox):
    name = 'yaralab'
    requires = ('yara',)
    description = 'runs your rules against sample files and reads the matches'

    def opens(self, spec: dict) -> str:
        return ('Enter hands you a shell in a throwaway directory holding '
                'the sample files. Write your rule there and run yara '
                'against them yourself.')


class PcapBoxAdapter(ToolSandbox):
    """A sandbox holding a capture file, for reading rather than grading.

    Distinct from the `pcap` oracle, which takes a filter you typed and
    compares what it selects against a reference. This one seeds the sandbox
    with the generated capture and hands you a shell, so a challenge can ask
    you to *work*: run tcpdump with the flags that make output readable, save
    what you found, and pipe it into something else. That is the half of the
    tcpdump module that a filter oracle cannot reach, and it is why both
    existed as self-marked challenges until now.

    The capture is written by `pcapgen`, not captured, per the tcpdump
    module's own scope note: generating traffic is out of scope, so the
    trainer writes the file it is going to ask you about.
    """

    name = 'pcapbox'
    requires = ('tcpdump',)
    description = 'reads what you pulled out of a capture file'

    def setup(self, spec: dict) -> None:
        super().setup(spec)
        if self.dir is None:
            return
        from .. import pcapgen
        pcapgen.write(self.dir / (spec.get('capture') or 'capture.pcap'))

    def opens(self, spec: dict) -> str:
        name = spec.get('capture') or 'capture.pcap'
        return (f'Enter hands you a shell in a throwaway directory holding '
                f'{name}, a capture the trainer wrote. Reading it needs no '
                f'privileges, and nothing is captured from your network.')


class PwshBoxAdapter(ToolSandbox):
    """A sandbox for work done in PowerShell rather than in a Unix shell.

    Distinct from the `pwsh` oracle adapter, which takes a pipeline you typed
    and compares its output against a reference. This one hands you a shell
    and reads the files you produced, which is the right shape when the task
    is "filter this event log and save what you found" rather than "write the
    one correct expression".
    """

    name = 'pwshbox'
    requires = ('pwsh',)
    description = 'runs your PowerShell in a sandbox and reads what it wrote'

    def handoff(self, spec: dict) -> list[str]:
        return ['pwsh', '-NoLogo', '-NoProfile']

    def opens(self, spec: dict) -> str:
        return ('Enter hands you a PowerShell prompt in a throwaway '
                'directory holding the sample data. Nothing outside it is '
                'touched.')
