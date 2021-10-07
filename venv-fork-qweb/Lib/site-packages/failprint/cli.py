# Why does this file exist, and why not put this in `__main__`?
#
# You might be tempted to import things from `__main__` later,
# but that will cause problems: the code will get executed twice:
#
# - When you run `python -m failprint` python will execute
#   `__main__.py` as a script. That means there won't be any
#   `failprint.__main__` in `sys.modules`.
# - When you import `__main__` it will get executed again (as a module) because
#   there's no `failprint.__main__` in `sys.modules`.

"""Module that contains the command line application."""

import argparse
from typing import List, Optional, Sequence

from failprint.capture import Capture
from failprint.formats import accept_custom_format, formats
from failprint.runners import run


class ArgParser(argparse.ArgumentParser):
    """A custom argument parser with a helper method to add boolean flags."""

    def add_bool_argument(
        self,
        truthy: Sequence[str],
        falsy: Sequence[str],
        truthy_help: str = "",
        falsy_help: str = "",
        **kwargs,
    ) -> None:
        """
        Add a boolean flag/argument to the parser.

        Arguments:
            truthy: Values that will store true in the destination.
            falsy: Values that will store false in the destination.
            truthy_help: Help for the truthy arguments.
            falsy_help: Help for the falsy arguments.
            **kwargs: Remaining keyword arguments passed to `argparse.ArgumentParser.add_argument`.
        """
        truthy_kwargs = {**kwargs, "help": truthy_help, "action": "store_true"}
        falsy_kwargs = {**kwargs, "help": falsy_help, "action": "store_false"}

        mxg = self.add_mutually_exclusive_group()
        mxg.add_argument(*truthy, **truthy_kwargs)  # type: ignore  # mypy is confused by arguments position
        mxg.add_argument(*falsy, **falsy_kwargs)  # type: ignore


def add_flags(parser, set_defaults=True) -> ArgParser:
    """
    Add some boolean flags to the parser.

    We made this method separate and public
    for its use in [duty](https://github.com/pawamoy/duty).

    Arguments:
        parser: The parser to add flags to.
        set_defaults: Whether to set default values on arguments.

    Returns:
        The augmented parser.
    """
    # IMPORTANT: the arguments destinations should match
    # the parameters names of the failprint.runners.run function.
    # As long as names are consistent between the two,
    # it' s very easy to pass CLI args to the function,
    # and it also allows to avoid duplicating the parser arguments
    # in dependent projects like duty (https://github.com/pawamoy/duty) :)
    parser.add_argument(
        "-c",
        "--capture",
        choices=list(Capture),
        type=Capture,
        help="Which output to capture. Colors are supported with 'both' only, unless the command has a 'force color' option.",
    )
    parser.add_argument(
        "-f",
        "--fmt",
        "--format",
        dest="fmt",
        choices=formats.keys(),
        type=accept_custom_format,
        default=None,
        help="Output format. Pass your own Jinja2 template as a string with '-f custom=TEMPLATE'. "
        "Available variables: command, title (command or title passed with -t), code (exit status), "
        "success (boolean), failure (boolean), number (command number passed with -n), "
        "output (command output), nofail (boolean), quiet (boolean), silent (boolean). "
        "Available filters: indent (textwrap.indent).",
    )
    parser.add_bool_argument(
        ["-y", "--pty"],
        ["-Y", "--no-pty"],
        dest="pty",
        default=True if set_defaults else None,
        truthy_help="Enable the use of a pseudo-terminal. PTY doesn't allow programs to use standard input.",
        falsy_help="Disable the use of a pseudo-terminal. PTY doesn't allow programs to use standard input.",
    )
    parser.add_bool_argument(
        ["-p", "--progress"],
        ["-P", "--no-progress"],
        dest="progress",
        default=True if set_defaults else None,
        truthy_help="Print progress while running a command.",
        falsy_help="Don't print progress while running a command.",
    )
    parser.add_bool_argument(
        ["-q", "--quiet"],
        ["-Q", "--no-quiet"],
        dest="quiet",
        default=False if set_defaults else None,
        truthy_help="Don't print the command output, even if it failed.",
        falsy_help="Print the command output when it fails.",
    )
    parser.add_bool_argument(
        ["-s", "--silent"],
        ["-S", "--no-silent"],
        dest="silent",
        default=False if set_defaults else None,
        truthy_help="Don't print anything.",
        falsy_help="Print output as usual.",
    )
    parser.add_bool_argument(
        ["-z", "--zero", "--nofail"],
        ["-Z", "--no-zero", "--strict"],
        dest="nofail",
        default=False if set_defaults else None,
        truthy_help="Don't fail. Always return a success (0) exit code.",
        falsy_help="Return the original exit code.",
    )
    return parser


def get_parser() -> ArgParser:
    """
    Return the CLI argument parser.

    Returns:
        An argparse parser.
    """
    parser = add_flags(ArgParser(prog="failprint"))
    parser.add_argument("-n", "--number", type=int, default=1, help="Command number. Useful for the 'tap' format.")
    parser.add_argument("-t", "--title", help="Command title. Default is the command itself.")
    parser.add_argument("cmd", metavar="COMMAND", nargs="+")
    return parser


def main(args: Optional[List[str]] = None) -> int:
    """
    Run the main program.

    This function is executed when you type `failprint` or `python -m failprint`.

    Arguments:
        args: Arguments passed from the command line.

    Returns:
        An exit code.
    """
    parser = get_parser()
    opts = parser.parse_args(args).__dict__.items()  # noqa: WPS609
    return run(**{_: value for _, value in opts if value is not None})
