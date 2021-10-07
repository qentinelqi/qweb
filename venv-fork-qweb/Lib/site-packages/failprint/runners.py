"""Functions to run commands and capture output."""

import os
import shutil
import sys
import textwrap
import traceback
from contextlib import contextmanager
from io import StringIO
from typing import Callable, Optional, Tuple, Union

from ansimarkup import ansiprint
from jinja2 import Environment

from failprint import WINDOWS
from failprint.capture import Capture, cast_capture
from failprint.formats import DEFAULT_FORMAT, accept_custom_format, formats, printable_command
from failprint.process import run_pty_subprocess, run_subprocess
from failprint.types import CmdFuncType, CmdType


class StdBuffer:
    """A simple placeholder for two memory buffers."""

    def __init__(self, out=None, err=None):
        """
        Initialize the object.

        Arguments:
            out: A buffer for standard output.
            err: A buffer for standard error.
        """
        self.out = out or StringIO()
        self.err = err or StringIO()


@contextmanager
def stdbuffer():
    """
    Capture output in a `with` statement.

    Yields:
        An instance of `StdBuffer`.
    """
    old_stdout = sys.stdout
    old_stderr = sys.stderr

    buffer = StdBuffer()

    sys.stdout = buffer.out
    sys.stderr = buffer.err

    yield buffer

    sys.stdout = old_stdout
    sys.stderr = old_stderr

    buffer.out.close()
    buffer.err.close()


def run(  # noqa: WPS231 (high complexity)
    cmd: CmdFuncType,
    args=None,
    kwargs=None,
    number: int = 1,
    capture: Optional[Union[str, bool, Capture]] = None,
    title: Optional[str] = None,
    fmt: Optional[str] = None,
    pty: bool = False,
    progress: bool = True,
    nofail: bool = False,
    quiet: bool = False,
    silent: bool = False,
) -> int:
    """
    Run a command in a subprocess or a Python function, and print its output if it fails.

    Arguments:
        cmd: The command to run.
        args: Arguments to pass to the callable.
        kwargs: Keyword arguments to pass to the callable.
        number: The command number.
        capture: The output to capture.
        title: The command title.
        fmt: The output format.
        pty: Whether to run in a PTY.
        progress: Whether to show progress.
        nofail: Whether to always succeed.
        quiet: Whether to not print the command output.
        silent: Don't print anything.

    Returns:
        The command exit code, or 0 if `nofail` is True.
    """
    format_name: str = fmt or os.environ.get("FAILPRINT_FORMAT", DEFAULT_FORMAT)  # type: ignore
    format_name = accept_custom_format(format_name)
    format_obj = formats.get(format_name, formats[DEFAULT_FORMAT])

    env = Environment(autoescape=False)  # noqa: S701 (no HTML: no need to escape)
    env.filters["indent"] = textwrap.indent

    command = printable_command(cmd, args, kwargs)

    if not silent and progress and format_obj.progress_template:
        progress_template = env.from_string(format_obj.progress_template)
        ansiprint(progress_template.render({"title": title, "command": command}), end="\r")

    capture = cast_capture(capture)

    if callable(cmd):
        code, output = run_function(cmd, args, kwargs, capture)
    else:
        code, output = run_command(cmd, capture, format_obj.accept_ansi, pty)

    if not silent:
        template = env.from_string(format_obj.template)
        ansiprint(
            template.render(
                {
                    "title": title,
                    "command": command,
                    "code": code,
                    "success": code == 0,
                    "failure": code != 0,
                    "number": number,
                    "output": output,
                    "nofail": nofail,
                    "quiet": quiet,
                    "silent": silent,
                },
            ),
        )

    return 0 if nofail else code


def run_command(
    cmd: CmdType,
    capture: Capture = Capture.BOTH,
    ansi: bool = False,
    pty: bool = False,
) -> Tuple[int, str]:
    """
    Run a command.

    Arguments:
        cmd: The command to run.
        capture: The output to capture.
        ansi: Whether to accept ANSI sequences.
        pty: Whether to run in a PTY.

    Returns:
        The exit code and the command output.
    """
    shell = isinstance(cmd, str)

    # if chosen format doesn't accept ansi, or on Windows, don't use pty
    if pty and (not ansi or WINDOWS):
        pty = False

    # pty can only combine, so only use pty when combining
    if pty and capture in {Capture.BOTH, Capture.NONE}:
        if shell:
            cmd = ["sh", "-c", cmd]  # type: ignore  # we know cmd is str
        return run_pty_subprocess(cmd, capture)  # type: ignore  # we made sure cmd is a list

    # we are on Windows
    if WINDOWS:
        # make sure the process can find the executable
        if not shell:
            cmd[0] = shutil.which(cmd[0]) or cmd[0]  # type: ignore  # we know cmd is a list
        return run_subprocess(cmd, capture, shell=shell)  # noqa: S604 (shell=True)

    return run_subprocess(cmd, capture, shell=shell)  # noqa: S604 (shell=True)


def run_function(func, args=None, kwargs=None, capture: Capture = Capture.BOTH) -> Tuple[int, str]:
    """
    Run a function.

    Arguments:
        func: The function to run.
        args: Positional arguments passed to the function.
        kwargs: Keyword arguments passed to the function.
        capture: The output to capture.

    Returns:
        The exit code and the function output.
    """
    args = args or []
    kwargs = kwargs or {}

    if capture == Capture.NONE:
        return run_function_get_code(func, sys.stderr, args, kwargs), ""

    with stdbuffer() as buffer:
        if capture == Capture.BOTH:
            # combining stdout and stderr
            # -> redirect stderr to stdout
            buffer.err = buffer.out
            sys.stderr = buffer.out

        code = run_function_get_code(func, buffer.err, args, kwargs)

        if capture == Capture.STDERR:
            output = buffer.err.getvalue()
        else:
            output = buffer.out.getvalue()

    return code, output


def run_function_get_code(func: Callable, stderr, args=None, kwargs=None) -> int:  # noqa: WPS212 (return statements)
    """
    Run a function and return a exit code.

    Arguments:
        func: The function to run.
        stderr: A file descriptor to write potential tracebacks.
        args: Positional arguments passed to the function.
        kwargs: Keyword arguments passed to the function.

    Returns:
        An exit code.
    """
    try:
        result = func(*args, **kwargs)
    except Exception:  # noqa: W0703 (catching Exception on purpose)
        stderr.write(traceback.format_exc() + "\n")
        return 1

    # first check True and False
    # because int(True) == 1 and int(False) == 0
    if result is True:
        return 0
    if result is False:
        return 1
    try:
        return int(result)
    except (ValueError, TypeError):
        if result is None or bool(result):
            return 0
        return 1
