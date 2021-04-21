# -*- coding: utf-8 -*-
# --------------------------
# Copyright © 2014 -            Qentinel Group.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ---------------------------

from QWeb.internal import browser
from QWeb.internal.input_handler import INPUT_HANDLER as input_handler
from QWeb.internal.exceptions import QWebValueMismatchError, QWebUnexpectedConditionError
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
import json
import re


def par2bool(s):
    """
    Returns boolean (True, False) from given parameter.
    Accepts booleans, strings or integers.
    """
    if isinstance(s, str):
        s = s.lower()
    return s in ["true", "1", "on", True, 1]


def xpath_validator(locator):
    """Checks if given locator is an xpath and returns boolean (True, False)
    """
    # TODO: Make this more reliable
    if locator.lower().startswith(('xpath=', '/html', '//')):
        return True
    return False


def url_validator(url):
    """Checks if given url is valid and returns boolean (True, False)
    """
    regex = re.compile(
        # Django url validation regex
        r'^(?:http|ftp)s?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None


def calculate_interval(timeout_int):
    """Calculates interval based on timeout.

    Some customers require long timeouts and polling every 0.1s results
    very longs logs. Poll less often if timeout is large.
    """
    if timeout_int > 60:
        interval = 3
    elif timeout_int > 10:
        interval = 1
    else:
        interval = 0.1
    return interval


def set_window_size(pixels):
    width, height = _parse_pixels(pixels)
    width = int(width)
    height = int(height)
    driver = browser.get_current_browser()
    driver.set_window_size(width, height)
    return width, height


def _parse_pixels(pixels, split='x'):
    pixel_list = pixels.lower().split(split)
    if len(pixel_list) == 1:
        raise ValueError("Pixels needs to be given with '1920x1080' syntax")
    return pixel_list[0], pixel_list[1]


def set_input_handler(input_method):
    input_handler.input_method = input_method.lower()
    return input_method.lower()


def set_line_break(key):
    if key == '\ue000':
        current_browser = browser.get_current_browser().capabilities['browserName']
        if current_browser == 'firefox':
            key = ''
            input_handler.line_break_key = key
            logger.info('\n\\ue000 line break does not work with Firefox, using empty string'
                        ' instead. It is recommended to use None instead of \\ue000.')
        else:
            input_handler.line_break_key = key
    elif key.lower() in ('none', 'empty', 'null'):
        key = ''
        input_handler.line_break_key = key
    else:
        input_handler.line_break_key = key
    return key


def set_clear_key(key):
    if key.lower() == 'none':
        key = None
    input_handler.clear_key = key
    return key


def get_substring(text, **kwargs):
    if '\xa0' in text:
        text = text.replace('\xa0', ' ')
    start, end = kwargs.get('between', '{}???{}').format(0, len(text)).split('???')
    include_start = kwargs.get('include_locator', False)
    exclude_end = kwargs.get('exclude_post', True)
    start = get_index_of(text, start, include_start)
    end = get_index_of(text, end, exclude_end)
    if end == 0:
        end = len(text)
    if 'from_start' in kwargs:
        end = start + int(kwargs.get('from_start'))
    if 'from_end' in kwargs:
        start = end - int(kwargs.get('from_end'))
    logger.debug('substring start: {}'.format(start))
    logger.debug('substring end: {}'.format(end))
    text = str(text[start:end]).strip().replace('\n', "")
    try:
        if 'int' in kwargs:
            num = float(text.replace(' ', '').replace(',', '.'))
            return int(num)
        if 'float' in kwargs:
            return float(text.replace(' ', '').replace(',', '.'))
    except ValueError as e:
        raise QWebValueMismatchError('Unable to convert. Got exception: {}'.format(e))
    return text


def get_index_of(text, locator, condition):
    try:
        return int(locator.strip())
    except ValueError:
        if locator.startswith('\\'):
            locator.replace('\\', "")
    index = text.find(locator.strip())
    if index > -1:
        if par2bool(condition) is False:
            index += len(locator)
        return index
    raise QWebValueMismatchError('File did not contain the text "{}"'.format(locator))


def prefs_to_dict(prefs):
    if isinstance(prefs, dict):
        d = prefs
    else:
        prefs_j = "{" + prefs + "}"
        try:
            d = json.loads(prefs_j)
        except json.decoder.JSONDecodeError:
            try:
                d = _handle_old_style_prefs(prefs)
            except QWebUnexpectedConditionError:
                raise QWebUnexpectedConditionError(
                    'Invalid argument! Experimental opts should given in robot dict '
                    'or string in format: key1:value1, key2:value2')
    return d


def _handle_old_style_prefs(prefs):
    d = {}
    separated = prefs.split(',')
    for s in separated:
        splitted = s.split(':', maxsplit=1)
        if len(splitted) == 2:
            logger.warn('Prefs keys and values without quotes is deprecated.')
            key = splitted[0].strip()
            if 'true' in splitted[1].lower() or 'false' in splitted[1].lower():
                val = par2bool(splitted[1].strip())
            else:
                val = splitted[1].strip()
            d[key] = val
        else:
            raise QWebUnexpectedConditionError
    return d


def validate_run_before(value):
    valid = ['verify_', 'verify_no']
    if any(x in value for x in valid):
        return value
    logger.warn('Invalid value. Only Verify PW:s are accepted.')
    return None


def initial_logging(capabilities):
    """Log version numbers at the start of test runs."""
    logger.debug(capabilities)
    try:
        b_n, b_v = capabilities['browserName'], capabilities['browserVersion']
        logger.info('Browser: {}'.format(b_n), also_console=True)
        logger.info('Browser version: {}'.format(b_v), also_console=True)
        if b_n == 'firefox':
            logger.info('Geckodriver version: {}'.format(
                capabilities['moz:geckodriverVersion']), also_console=True)
        if b_n == 'chrome':
            logger.info('Chromedriver version: {}'.format(
                capabilities['chrome']['chromedriverVersion']), also_console=True)
    except KeyError:
        logger.debug('Could not get browser/driver version data.')


def option_handler(options):
    options2 = []
    if options:
        options2 += options.split(',')
    if BuiltIn().get_variable_value('${BROWSER_OPTIONS}'):
        options2 += BuiltIn().get_variable_value('${BROWSER_OPTIONS}').split(',')
    return options2


def get_callable(pw):
    """Return function by Paceword name if exists."""
    lib = BuiltIn().get_library_instance('QWeb')
    pacewords = lib.__dir__()
    for paceword in pacewords:
        if not paceword.startswith('__'):
            if str(pw).replace(' ', '').lower() == paceword.replace('_', ''):
                fn = lib.__getattribute__(paceword)
                return fn
    raise QWebUnexpectedConditionError('Paceword {} not found'.format(pw))
