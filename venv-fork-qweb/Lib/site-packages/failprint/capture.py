"""Enumeration of possible output captures."""

import enum
from typing import Optional, Union


class Capture(enum.Enum):
    """An enum to store the different possible output types."""

    STDOUT: str = "stdout"  # noqa: WPS115
    STDERR: str = "stderr"  # noqa: WPS115
    BOTH: str = "both"  # noqa: WPS115
    NONE: str = "none"  # noqa: WPS115

    def __str__(self):
        return self.value.lower()  # noqa: E1101 (false-positive)


def cast_capture(value: Optional[Union[str, bool, Capture]]) -> Capture:
    """
    Cast a value to an actual Capture enumeration value.

    Arguments:
        value: The value to cast.

    Returns:
        A Capture enumeration value.
    """
    if value is None:
        return Capture.BOTH
    if value is True:
        return Capture.BOTH
    if value is False:
        return Capture.NONE
    if isinstance(value, Capture):
        return value
    # consider it's a string
    # let potential errors bubble up
    return Capture(value)
