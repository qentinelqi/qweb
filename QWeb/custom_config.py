from typing import Callable, Any
from QWeb.internal import element, frame


def set_wait_function(function: Callable[..., Any]) -> Callable[..., Any]:
    """Set custom wait function that is run at the beginning of keywords.

    **Note**: Not meant to be used as robot framework keyword but as a helper
    function to extend / customize QWeb via Python.

    Examples
    --------
     .. code-block:: python

        from QWeb.custom_config import set_wait_function

        def my_wait_function():
            # your own wait logic here
            ...

        # This will make QWeb use "my_wait_function" as wait function
        # instead of the default one
        set_wait_function(my_wait_function)


    Parameters
    ----------
    function : function
        Function that does not need to return anything.
    """
    previous = frame.wait_page_loaded
    if callable(function):
        frame.wait_page_loaded = function
    else:
        raise ValueError("Argument needs to be callable: {}".format(function))
    return previous


def set_active_area_function(function: Callable[..., Any]):
    """Set function that sets active area where elements are searched.

    Parameters
    ----------
    function : function
        Function that returns WebElement under which elements are searched.
    """
    element.ACTIVE_AREA_FUNCTION = function
