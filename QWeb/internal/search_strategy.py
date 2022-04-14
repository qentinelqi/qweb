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
from typing import Any
# pylint: disable=line-too-long
import re
import string


class SearchStrategies:
    ALL_INPUT_ELEMENTS: str = '//input[@type="text" or @type="email" or @type="password" or @type="tel"]|//textarea'

    MATCHING_INPUT_ELEMENT: str = '//*[(self::input or self::textarea) and (normalize-space(@placeholder)="{0}" or normalize-space(@value)="{0}")]'
    CONTAINING_INPUT_ELEMENT: str = '//*[(self::input or self::textarea) and (contains(normalize-space(@placeholder),"{0}") or contains(normalize-space(@value),"{0}"))]'

    ACTIVE_AREA_XPATH: str = '//body'

    TEXT_MATCH: str = '//*[not(self::script) and normalize-space(translate(., "\u00a0", " "))="{0}" and not(descendant::*[normalize-space(translate(., "\u00a0", " "))="{0}"])]|//input[(@type="button" or @type="reset" or @type="submit" or @type="checkbox") and normalize-space(translate(@value, "\u00a0", " "))="{0}"]'

    CONTAINING_TEXT_MATCH_CASE_SENSITIVE: str = (
        '//*[not(self::script) and contains(normalize-space(translate(., "\u00a0", " ")), "{0}") '
        'and not(descendant::*[contains(normalize-space(translate(., "\u00a0", " ")), "{0}")])]| '
        '//input[(@type="button" or @type="reset" or @type="submit") and contains(normalize-space(translate(@value, "\u00a0", " ")), "{0}")]'
    )

    # ToDo: Will use lower-case to replace translate in xpath when it is ready.

    CONTAINING_TEXT_MATCH_CASE_INSENSITIVE: str = '//*[not(self::script) and contains(translate(normalize-space(translate(., "\u00a0", " ")), "ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÅ", \
                            "abcdefghijklmnopqrstuvwxyzäöå"), translate("{0}", "ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÅ", "abcdefghijklmnopqrstuvwxyzäöå"))  \
                            and not(descendant::*[contains(translate(normalize-space(translate(., "\u00a0", " ")), "ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÅ", \
                            "abcdefghijklmnopqrstuvwxyzäöå"), translate("{0}", "ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÅ", "abcdefghijklmnopqrstuvwxyzäöå"))])]| \
                            //input[(@type="button" or @type="reset" or @type="submit") and contains(translate(normalize-space(translate(@value, "\u00a0", " ")), \
                            "ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÅ", "abcdefghijklmnopqrstuvwxyzäöå"), \
                            translate("{0}", "ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÅ", "abcdefghijklmnopqrstuvwxyzäöå"))]'

    IS_MODAL_XPATH = '//body'

    @staticmethod
    def active_area_xpath_validation(xpath: str) -> str:
        return SearchStrategies.clear_xpath(xpath)

    @staticmethod
    def all_input_elements_validation(xpath: str) -> str:
        return SearchStrategies.clear_xpath(xpath)

    @staticmethod
    def matching_input_element_validation(xpath: str) -> str:
        if xpath == 'containing input element':
            xpath = SearchStrategies.CONTAINING_INPUT_ELEMENT
        SearchStrategies.verify_format_string(xpath, 1)
        return SearchStrategies.clear_xpath(xpath)

    @staticmethod
    def text_match_validation(xpath: str) -> str:
        return SearchStrategies.clear_xpath(xpath)

    @staticmethod
    def containing_text_match_validation(xpath: str) -> str:
        return SearchStrategies.clear_xpath(xpath)

    @staticmethod
    def clear_xpath(xpath: str) -> str:
        if re.match("xpath *=", xpath, re.IGNORECASE):
            return ''.join(xpath.split('=')[1:])
        return xpath

    @staticmethod
    def search_direction_validation(direction: str) -> str:
        """ Validates the search direction configuration """
        valid_directions = ["up", "down", "left", "right", "closest"]
        direction = direction.lower()
        if direction not in valid_directions:
            raise ValueError("Wrong search direction")
        return direction

    @staticmethod
    def _continuous_set(s: set, num: int) -> bool:
        """Verifies that a set has given number of continous values
           starting from 0. E.g. 0,1,2,3 is 4 continuous values whereas
           0,1,3,4 is not.
        """

        return set.intersection(s, set(range(num))) == set(range(num))

    @staticmethod
    def default_timeout_validation(timeout: Any) -> Any:
        return timeout

    @staticmethod
    def xhr_timeout_validation(timeout: Any) -> Any:
        return timeout

    @staticmethod
    def verify_format_string(s: str, placeholder_num: int) -> None:
        """Verify that string contains placeholders.

        Throws ValueError if string doesn't contain required amount
        of empty placeholders "{}" or position placeholders "{<int>}".
        Position placeholders can be repeated, e.g. "foo {0} {1} {0}"
        is valid when placeholder_num is 2.
        """

        # Parse format string to a list of elements
        parsed = list(string.Formatter().parse(s))
        empty_placeholders = 0
        index_placeholders = set()
        continuous = False
        for elem in parsed:
            # field_name '' matches {}
            if elem[1] == '':
                empty_placeholders += 1
            # field_name '0' matches {0} etc.
            elif elem[1] and elem[1].isnumeric():
                index_placeholders.add(int(elem[1]))

        # Position placeholders are in a set. They must start from zero
        # so that we have {0}'s, {1}'s etc.
        if index_placeholders:
            continuous = SearchStrategies._continuous_set(index_placeholders, placeholder_num)

        if placeholder_num != (empty_placeholders + len(index_placeholders)):
            raise ValueError("xpath has invalid number of placeholders, got {}, {}".format(
                empty_placeholders, len(index_placeholders)))

        if empty_placeholders == placeholder_num or \
           len(index_placeholders) == placeholder_num and continuous:
            pass
        else:
            raise ValueError("xpath should contain {} placeholders, got {}, {}, {}".format(
                placeholder_num, empty_placeholders, len(index_placeholders), continuous))
