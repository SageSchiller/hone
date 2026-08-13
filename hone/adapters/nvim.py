"""The nvim adapter: real edits, in real nvim, checked afterwards.

The browser plan needed a normal-mode emulator to grade vim at all, and it was
the single largest engineering item in it. This file replaces that emulator
with a launch command and one autocmd, because the student can just use nvim
and the trainer can read what happened. The muscle memory transfers because it
*is* the real thing, and there is no fidelity gap to maintain.

Everything structural lives in `_buffer.BufferAdapter`. What is nvim's own is
here: how to start it, and the `VimLeavePre` autocmd that dumps the buffer and
the final cursor into the sandbox on the way out.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from ._buffer import EXPECT_KEYS, BufferAdapter, check  # noqa: F401

TIMEOUT = 10.0


def _vim_str(s) -> str:
    """Quote a path for a Vim command. Single quotes double themselves."""
    return "'" + str(s).replace("'", "''") + "'"


def leave_hook(scratch: Path, buf_path: Path, cur_path: Path) -> str:
    """The one `-c` command this adapter injects.

    Writes only into the sandbox, registers nothing persistent, and touches no
    part of the user's configuration. See D1.

    The buffer is addressed **by number, not by "current"**. `getline()` reads
    whichever buffer happens to be focused at exit, so opening any other file
    before quitting dumped the wrong text and failed a student who had done
    the work correctly.
    """
    n = f"bufnr({_vim_str(scratch)})"
    return (f"autocmd VimLeavePre * call writefile(getbufline({n}, 1, '$'), "
            f"{_vim_str(buf_path)}) | call writefile("
            f"[line('.').' '.col('.')], {_vim_str(cur_path)})")


def status_text(s: str) -> str:
    """Escape a reminder for use as a statusline.

    A statusline is a format string: a bare `%` in the task text would be read
    as an item and either vanish or expand into something baffling.
    """
    return ' '.join(str(s).split()).replace('%', '%%')


def reminder(text: str) -> list[str]:
    """`-c` arguments that keep the task visible for the whole session.

    Three places, on purpose. A statusline is the obvious home and is also the
    thing every configured nvim replaces with a plugin, so the winbar is a
    second chance and `:messages` a third that nothing overwrites. All three
    are `silent!` so an older nvim without winbar still launches.

    Assignment through `&l:statusline` rather than `:set` because a `:set`
    argument cannot contain unescaped spaces, and the task is a sentence.
    """
    t = status_text(text)
    return ['-c', 'silent! set laststatus=2',
            '-c', f"silent! let &l:statusline = {_vim_str(t)}",
            '-c', f"silent! let &l:winbar = {_vim_str(t)}",
            '-c', f"silent! echomsg {_vim_str(text)}"]


class NvimAdapter(BufferAdapter):
    name = 'nvim'
    requires = ('nvim',)
    description = 'reads the buffer you actually edited'
    editor = 'nvim'
    return_hint = 'press Esc, then type :wq and Enter'

    def probe(self) -> tuple[bool, str]:
        if not shutil.which('nvim'):
            return False, 'nvim not installed'
        try:
            r = subprocess.run(['nvim', '--version'], capture_output=True,
                               text=True, timeout=TIMEOUT)
        except (OSError, subprocess.SubprocessError):
            return False, 'nvim is installed but not answering'
        return (True, '') if r.returncode == 0 else (False, 'nvim failed to start')

    def launch(self, scratch: Path, buf: Path, cur: Path,
               brief: str = '') -> list[str]:
        # The leave hook stays at argv[-2] and the file at argv[-1]: the
        # convention in _buffer.py, which the solution replayer relies on.
        head = ['nvim'] + (reminder(brief) if brief else [])
        return head + ['-c', leave_hook(scratch, buf, cur), str(scratch)]
