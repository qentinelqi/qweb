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
from __future__ import annotations
from typing import Optional, Union
from selenium.webdriver.remote.webelement import WebElement

from robot.api import logger
from QWeb.internal.exceptions import QWebElementNotFoundError
from QWeb.internal import element, text, javascript, frame
from QWeb.internal.config_defaults import CONFIG


class List:

    ACTIVE_LIST: List

    def __init__(self,
                 web_list: list[str],
                 web_element_list: list[WebElement],
                 locator: str,
                 anchor: str,
                 parent: Optional[str] = None,
                 child: Optional[str] = None,
                 **kwargs) -> None:
        self.web_list = web_list
        self.web_element_list = web_element_list
        self.locator = locator
        self.anchor = anchor
        self.parent = parent
        self.child = child
        self.kwargs = kwargs
        List.ACTIVE_LIST = self

    @classmethod
    @frame.all_frames
    def from_list_instance(cls,
                           locator: str,
                           anchor: str = "1",
                           parent: Optional[str] = None,
                           child: Optional[str] = None,
                           **kwargs) -> List:
        """Find list and create list instance

        Parameters
        ----------
        locator : str
            Text that locates the table. The table that is closest
            to the text is selected. Also one can use xpath by adding xpath= prefix
            and then the xpath. Error is raised if the xpath matches to multiple
            elements.
        anchor : str
            Text near the table's locator element. If the page contains
            many places where the locator is then anchor is used to get the
            one that is closest to it.
        kwargs:
            tag : html_tag
                When finding list by text which is inside of it use tag to point
                out wanted parent element.
                For example ul, ol etc. if parameter is not given, uses default = UL.
        """
        # TODO  How to type cls argument properly?
        web_list, web_element_list = cls.create_list(
            cls,  # type: ignore[arg-type]
            locator,
            anchor,
            parent=parent,
            child=child,
            **kwargs)
        return List(web_list, web_element_list, locator, anchor, parent, child, **kwargs)

    def create_list(self, locator: str, anchor: str, **kwargs
                    ) -> tuple[list[str], list[WebElement]]:
        web_elements: Union[WebElement, list[WebElement]]
        if locator.startswith('//') or locator.startswith('xpath='):
            if locator.startswith('xpath='):
                locator = locator.split("=", 1)[1]
            web_elements = self.get_elements_by_locator_xpath_and_tag_name(
                locator, anchor, **kwargs)
        else:
            web_elements = self.get_elements_by_locator_text_and_tag_name(locator, anchor, **kwargs)
            logger.debug('webelems: {}'.format(web_elements))
        if web_elements:
            if CONFIG['SearchMode']:
                element.draw_borders(web_elements)
            web_list = self.get_texts(web_elements)
            if isinstance(web_elements, WebElement):
                return web_list, [web_elements]
            return web_list, web_elements
        raise QWebElementNotFoundError('Suitable elements not found')

    @staticmethod
    def get_elements_by_locator_text_and_tag_name(locator: str,
                                                  anchor: str,
                                                  index: int = 1,
                                                  **kwargs) -> Union[WebElement, list[WebElement]]:
        web_element: Optional[WebElement]
        locator_element: Optional[WebElement]

        index = int(index) - 1
        if 'tag' in kwargs:
            tag_name = kwargs.get('tag')
        elif 'parent' in kwargs and kwargs['parent']:
            tag_name = kwargs['parent']
        elif 'child' in kwargs and kwargs['child']:
            tag_name = kwargs['child']
        else:
            tag_name = 'ul'

        web_element = text.get_element_by_locator_text(locator, anchor)
        if 'parent' in kwargs and kwargs['parent'] and web_element is not None:
            tag = kwargs['parent']
            locator_element = element.get_parent_list_element(web_element, tag)
        elif 'child' in kwargs and kwargs['child'] and web_element is not None:
            tag = kwargs['child']
            locator_element = element.get_element_from_childnodes(web_element,
                                                                  tag,
                                                                  dom_traversing=False)[index]
            if tag_name not in ["ul", "ol", "dl", "UL", "OL", "DL"]:
                return locator_element
        else:
            locator_element = text.get_element_by_locator_text(locator, anchor)

        if tag_name not in ["ul", "ol", "dl", "UL", "OL", "DL"]:
            web_elements = javascript.execute_javascript(
                'return arguments[0].querySelectorAll("{}")'.format(tag_name), locator_element)
        else:
            web_elements = javascript.execute_javascript(
                'return arguments[0].closest("{}").querySelectorAll("li, dt, dd")'.format(tag_name),
                locator_element)
        return web_elements

    @staticmethod
    def get_elements_by_locator_xpath_and_tag_name(locator: str,
                                                   index: Union[int, str] = 1,
                                                   **kwargs) -> list[WebElement]:
        index = int(index) - 1
        if 'tag' in kwargs:
            tag_name = kwargs.get('tag')
        elif 'parent' in kwargs and kwargs['parent']:
            tag_name = kwargs['parent']
        elif 'child' in kwargs and kwargs['child']:
            tag_name = kwargs['child']
        else:
            tag_name = 'ul'
        if 'parent' in kwargs and kwargs['parent']:
            web_element = element.get_unique_element_by_xpath(locator, index=index)
            css = kwargs.get('parent')
            web_element = element.get_parent_list_element(web_element, str(css))
            if tag_name not in ["ul", "ol", "dl", "UL", "OL", "DL"]:
                web_elements = javascript.execute_javascript(
                    'return arguments[0].querySelectorAll("{}")'.format(tag_name), web_element)
            else:
                web_elements = javascript.execute_javascript(
                    'return arguments[0].closest("{}").querySelectorAll("li, dt, dd")'.format(
                        tag_name), web_element)
        elif 'child' in kwargs and kwargs['child']:
            web_element = element.get_unique_element_by_xpath(locator)
            css = kwargs.get('child')
            web_elements = element.get_element_from_childnodes(web_element,
                                                               str(css),
                                                               dom_traversing=False)[index]
            if tag_name not in ["ul", "ol", "dl", "UL", "OL", "DL"]:
                web_elements = javascript.execute_javascript(
                    'return arguments[0].querySelectorAll("{}")'.format(tag_name), web_element)
            else:
                web_elements = javascript.execute_javascript(
                    'return arguments[0].closest("{}").querySelectorAll("li, dt, dd")'.format(
                        tag_name), web_element)
        else:
            web_elements = element.get_webelements_in_active_area(locator)

        return web_elements

    @staticmethod
    def get_texts(web_elements: Union[WebElement, list[WebElement]]) -> list[str]:
        texts = []
        if isinstance(web_elements, list):
            for elem in web_elements:
                texts.append(elem.text)
        else:
            texts.append(web_elements.text)
        return texts

    def contains(self, expected_match: str, index: Optional[int]) -> bool:
        if index is None:
            if expected_match in self.web_list:
                return True
        else:
            if expected_match in str(self.web_list[int(index)]).replace('\n', '').strip():
                return True
        return False

    def update_list(self) -> List:
        active_list = self.from_list_instance(self.locator, self.anchor, self.parent, self.child,
                                              **self.kwargs)
        return active_list
