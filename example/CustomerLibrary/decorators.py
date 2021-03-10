import traceback
from functools import wraps
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn


def log_screenshot(keyword_method):
    """Decorator method for keywords.

    If keyword fails then this method executes Log Screenshot keyword
    """

    @wraps(keyword_method)  # Preserves docstring of the original method.
    def inner(*args):
        try:
            return keyword_method(*args)
        except Exception as e:
            logger.debug(traceback.format_exc())
            BuiltIn().run_keyword(u"Log Screenshot")
            raise e

    return inner
