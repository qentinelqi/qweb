"""Output-printing formats."""

from typing import Callable, Dict, List, Optional

from failprint.types import CmdFuncType

DEFAULT_FORMAT = "pretty"


class Format:
    """Class to define a display format."""

    def __init__(self, template: str, progress_template: Optional[str] = None, accept_ansi: bool = True) -> None:
        """
        Initialize the object.

        Arguments:
            template: The main template.
            progress_template: The template to show progress.
            accept_ansi: Whether to accept ANSI sequences.
        """
        self.template = template
        self.progress_template = progress_template
        self.accept_ansi = accept_ansi


formats: Dict[str, Format] = {
    "pretty": Format(
        "{% if success %}<green>✓</green>"
        "{% elif nofail %}<yellow>✗</yellow>"
        "{% else %}<red>✗</red>{% endif %} "
        "<bold>{{ title or command }}</bold>"
        "{% if failure %} ({{ code }}){% endif %}"
        "{% if failure and output and not quiet %}\n"
        "{{ ('  > ' + command + '\n') if title else '' }}"
        "{{ output|indent(2 * ' ') }}{% endif %}",
        progress_template="> {{ title or command }}",
    ),
    "tap": Format(
        "{% if failure %}not {% endif %}ok {{ number }} - {{ title or command }}"
        "{% if failure and output %}\n  ---\n  "
        "{{ ('command: ' + command + '\n  ') if title else '' }}"
        "output: |\n{{ output|indent(4 * ' ') }}\n  ...{% endif %}",
        accept_ansi=False,
    ),
}


def accept_custom_format(string: str) -> str:
    """
    Store the value in `formats` if it starts with custom.

    Arguments:
        string: A format name.

    Returns:
        The format name, or `custom` if it started with `custom=`.
    """
    if string.startswith("custom="):
        formats["custom"] = Format(string[7:])
        return "custom"
    return string


def printable_command(cmd: CmdFuncType, args=None, kwargs=None) -> str:
    """
    Transform a command or function into a string.

    Arguments:
        cmd: The command or function to transform.
        args: Positional arguments passed to the function.
        kwargs: Keyword arguments passed to the function.

    Returns:
        A shell command or python statement string.
    """
    if isinstance(cmd, str):
        return cmd
    if callable(cmd):
        return as_python_statement(cmd, args, kwargs)
    return as_shell_command(cmd)


def as_shell_command(cmd: List[str]) -> str:  # noqa: WPS231 (not that complex)
    """
    Rebuild a command line from system arguments.

    Arguments:
        cmd: The command as a list of strings.

    Returns:
        A printable and shell-runnable command.
    """
    parts = []
    for part in cmd:
        if not part:
            parts.append('""')
            continue
        has_spaces = " " in part
        has_double_quotes = '"' in part
        has_single_quotes = "'" in part
        if has_double_quotes and not has_single_quotes:
            # double quotes, no single quotes
            # -> wrap in single quotes
            part = f"'{part}'"
        elif has_single_quotes and has_double_quotes:
            # double and single quotes
            # -> escape double quotes, wrap in double quotes
            part = part.replace('"', r"\"")
            part = f'"{part}"'
        elif has_single_quotes or has_spaces:
            # spaces or single quotes
            # -> wrap in double quotes
            part = f'"{part}"'
        parts.append(part)
    return " ".join(parts)


def as_python_statement(func: Callable, args=None, kwargs=None) -> str:
    """
    Transform a callable and its arguments into a Python statement string.

    Arguments:
        func: The callable to transform.
        args: Positional arguments passed to the function.
        kwargs: Keyword arguments passed to the function.

    Returns:
        A Python statement.
    """
    args = [repr(arg) for arg in args] if args else []
    kwargs = [f"{k}={v!r}" for k, v in kwargs.items()] if kwargs else []  # noqa: WPS111,WPS221 (short name, complexity)
    args_str = ", ".join(args + kwargs)
    return f"{func.__name__}({args_str})"
