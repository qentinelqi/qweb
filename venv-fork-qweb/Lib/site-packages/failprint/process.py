"""Functions related to subprocesses."""

import locale
import re
import subprocess  # noqa: S404 (we don't mind the security implication)
from typing import List, Optional, Tuple

from failprint import WINDOWS
from failprint.capture import Capture
from failprint.formats import printable_command
from failprint.types import CmdType

if not WINDOWS:
    from ptyprocess import PtyProcessUnicode


# Note: we could maybe use `universal_newlines` when running the process
# to get str instead of bytes, avoiding to decode it ourselves?
# maybe Python knows better how to decode it
def get_windows_encoding() -> str:
    """
    Return the encoding on a Windows system.

    On Windows, the console (cmd.exe) might use another encoding
    than UTF-8 but also another one that the system preferred locale.

    This function runs the console tool `chcp` to get the code page.
    If it fails to get the code page, it returns the locale preferred encoding.

    Returns:
        The number returned by `chcp` in a Windows console.
    """
    # contrary to locale, code page does not lose characters
    # example: é -> ,
    _, chcp_output = run_subprocess_raw("chcp", capture=Capture.BOTH, shell=True)  # noqa: S604 (shell=True)
    try:
        code = re.search(rb"(\d+)\s*$", chcp_output).group(1)  # type: ignore  # attribute error caught
    except AttributeError:
        return locale.getpreferredencoding()
    return re.sub(r"\\x..", "", str(code)).strip("b'\"")


class OSDecoder:
    """A locale-dependent decoder."""

    def __init__(self) -> None:
        """Initialize the object."""
        self._encoding: Optional[str] = None

    @property
    def encoding(self) -> str:
        """
        Return the encoding that should be used to decode.

        Returns:
            An encoding identifier.
        """
        if self._encoding is None:
            if WINDOWS:
                self._encoding = get_windows_encoding()
            else:
                self._encoding = locale.getpreferredencoding()
        return self._encoding

    def decode(self, byte_string: bytes) -> str:
        """
        Decode bytes into a string.

        Arguments:
            byte_string: The bytes to decode.

        Returns:
            The decoded bytes.
        """
        if not self.encoding:
            return str(byte_string)[2:-1]
        try:
            return byte_string.decode(self.encoding)
        except (LookupError, UnicodeDecodeError):
            return str(byte_string)[2:-1]


decoder = OSDecoder()


def run_subprocess(
    cmd: CmdType,
    capture: Capture = Capture.BOTH,
    shell: bool = False,
) -> Tuple[int, str]:
    """
    Run a command in a subprocess.

    Arguments:
        cmd: The command to run.
        capture: The output to capture.
        shell: Whether to run the command in a shell.

    Returns:
        The exit code and the command output.
    """
    code, raw_output = run_subprocess_raw(cmd, capture, shell)

    if raw_output:
        try:
            output = raw_output.decode("utf8")
        except UnicodeDecodeError:
            output = decoder.decode(raw_output)
    else:
        output = ""

    return code, output


def run_subprocess_raw(
    cmd: CmdType,
    capture: Capture = Capture.BOTH,
    shell: bool = False,
) -> Tuple[int, bytes]:
    """
    Run a command in a subprocess, returning raw output (bytes).

    Arguments:
        cmd: The command to run.
        capture: The output to capture.
        shell: Whether to run the command in a shell.

    Returns:
        The exit code and the command raw output.
    """
    if capture == Capture.NONE:
        stdout_opt = None
        stderr_opt = None

    else:
        stdout_opt = subprocess.PIPE

        if capture == Capture.BOTH:
            stderr_opt = subprocess.STDOUT
        else:
            stderr_opt = subprocess.PIPE

    if shell and not isinstance(cmd, str):
        cmd = printable_command(cmd)

    process = subprocess.run(  # noqa: S603,W1510 (we trust the input, and don't want to "check")
        cmd,
        stdout=stdout_opt,
        stderr=stderr_opt,
        shell=shell,  # noqa: S602 (shell=True)
    )

    if capture == Capture.NONE:
        output = b""
    elif capture == Capture.STDERR:
        output = process.stderr
    else:
        output = process.stdout

    return process.returncode, output


def run_pty_subprocess(cmd: List[str], capture: Capture = Capture.BOTH) -> Tuple[int, str]:
    """
    Run a command in a PTY subprocess.

    Arguments:
        cmd: The command to run.
        capture: The output to capture.

    Returns:
        The exit code and the command output.
    """
    process = PtyProcessUnicode.spawn(cmd)

    pty_output: List[str] = []

    while True:
        try:
            output_data = process.read()
        except EOFError:
            break
        if capture == Capture.NONE:
            print(output_data, end="", flush=True)  # noqa: WPS421 (print)
        else:
            pty_output.append(output_data)

    process.close()

    output = "".join(pty_output)
    code = process.exitstatus

    return code, output
