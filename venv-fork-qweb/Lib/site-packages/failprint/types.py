"""
Special types.

Attributes:
    CmdType: Type for a command.
    CmdFuncType: Type for a command or function.
"""

from typing import Callable, List, Union

CmdType = Union[str, List[str]]  # noqa: E1136 (bug on Python 3.9)
CmdFuncType = Union[CmdType, Callable]  # noqa: E1136 (bug on Python 3.9)
