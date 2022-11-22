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

import fnmatch
import re
from robot.api import logger
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from QWeb.internal.exceptions import QWebElementNotFoundError, QWebValueError
from QWeb.internal import element, text, javascript, frame, util
from QWeb.internal.config_defaults import CONFIG


class Table:

    ACTIVE_TABLE: Table = None  # type: ignore[assignment]

    def __init__(self,
                 table: WebElement,
                 locator: str,
                 anchor: str,
                 parent: bool = False,
                 child: bool = False,
                 level: int = 1,
                 index: int = 1) -> None:
        self.table = table
        self.locator = locator
        self.anchor = anchor
        self.parent = parent
        self.child = child
        self.level = level
        self.index = index
        Table.ACTIVE_TABLE = self

    @classmethod
    @frame.all_frames
    def from_table_instance(cls,
                            locator: str,
                            anchor: str,
                            parent: bool = False,
                            child: bool = False,
                            level: int = 1,
                            index: int = 1) -> Table:
        """Create table instance by finding table based on locator

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
        """
        if CONFIG["CssSelectors"] and not util.xpath_validator(locator):
            table_element = cls.get_table_element_by_css(locator, anchor)
        else:
            table_element = cls.get_table_element(cls, locator, index)  # type: ignore[arg-type]
        if table_element is None:
            raise QWebElementNotFoundError("Could not find Table Element!")
        if not parent and not child:
            if CONFIG['SearchMode']:
                element.draw_borders(table_element)
            return Table(table_element, locator, anchor, parent, child, level, index)
        table_element = cls.get_table_by_locator_table(table_element, parent, child, level, index)
        if CONFIG['SearchMode']:
            element.draw_borders(table_element)
        return Table(table_element, locator, anchor, parent, child, level, index)

    @staticmethod
    def get_table_by_locator_table(locator: WebElement,
                                   parent: bool = False,
                                   child: bool = False,
                                   level: int = 1,
                                   index: int = 1) -> WebElement:
        if parent:
            script = ".parentElement.closest('table')" * int(level)
            parent_table = javascript.execute_javascript("return arguments[0]{}".format(script),
                                                         locator)
            if parent_table:
                if not child:
                    return parent_table
                locator = parent_table
            else:
                raise QWebElementNotFoundError('No parent table found')
        if child:
            script = ".querySelectorAll('table')[{}]".format(int(index) - 1)
            child_table = javascript.execute_javascript("return arguments[0]{}".format(script),
                                                        locator)
            if child_table:
                return child_table
            raise QWebElementNotFoundError('No child table found')
        raise QWebElementNotFoundError('Sub/parent table not found')

    def get_table_element(self, locator: str, anchor: str) -> WebElement:
        if util.xpath_validator(locator):
            index = util.anchor_to_index(anchor)
            table_element = element.get_unique_element_by_xpath(locator, index=index)
        else:  # Search using text
            table_xpath = "//*[text()= '{0}']/ancestor::table".format(locator)
            table_elements = element.get_webelements_in_active_area(table_xpath)
            if table_elements and len(table_elements) == 1:
                table_element = table_elements[0]
            elif not table_elements:  # Find table element using locator
                locator_element = text.get_text_using_anchor(locator, anchor)
                table_elements = self._get_all_table_elements()
                table_element = element.get_closest_element(locator_element, table_elements)
            else:  # Found many
                table_element = text.get_element_using_anchor(table_elements, anchor)
        if table_element:
            return table_element
        raise QWebElementNotFoundError('Table element not found by locator {}'.format(locator))

    def get_table_cell(self, coordinates: str, anchor: str, **kwargs) -> WebElement:  # pylint: disable=unused-argument
        cell = None
        try:
            if '/' in coordinates:
                cell = self.get_using_text_in_coordinates(coordinates, anchor)
            else:
                row, column = self._convert_coordinates(coordinates)
                try:
                    cell = self.table.find_element(By.XPATH,
                                                   './/tr[{0}]//td[{1}]'.format(row, column))
                except AttributeError as e:
                    logger.debug('exception {}'.format(e))
                    self.update_table()
            if cell:
                if CONFIG['SearchMode']:
                    element.draw_borders(cell)
                return cell
        except (StaleElementReferenceException, NoSuchElementException) as e:
            logger.debug('exception {}'.format(e))
            self.update_table()
        raise QWebElementNotFoundError('Cell for coords {} not found after'.format(coordinates))

    def get_using_text_in_coordinates(self, coordinates: str, anchor: str) -> WebElement:
        row: Optional[int]
        column: Optional[int]
        row_elem = None
        cell = None
        locator = coordinates.split('/')
        if locator[0].startswith('r?'):
            row_elem = self.get_row(locator[0][2:], anchor)
        else:
            row, _ = self._convert_coordinates(locator[0])
        if locator[1].startswith('c?'):
            column = self.get_cell_by_locator(locator[1][2:])
        else:
            _, column = self._convert_coordinates(locator[1])
        if row_elem:
            cell = javascript.execute_javascript(
                'return arguments[0].cells[{}]'.format(column - 1),  # type:ignore[operator]
                row_elem)
        else:
            cell = javascript.execute_javascript('return arguments[0].rows[{}].cells[{}]'.format(
                row - 1, column - 1), self.table)  # type:ignore[operator]
        return cell

    def get_clickable_cell(self,
                           coordinates: str,
                           anchor: str,
                           index: int = 1,
                           **kwargs) -> WebElement:
        if int(index) < 1:
            raise QWebValueError('Index should be greater than 0.')
        table_cell = self.get_table_cell(coordinates, anchor)
        if 'tag' in kwargs:
            clickable_child = element.get_element_from_childnodes(table_cell,
                                                                  str(kwargs.get('tag')),
                                                                  dom_traversing=False)
            if int(index) > len(clickable_child):
                raise QWebValueError('Index exceeds the number of clickable elements in cell.')
            return clickable_child[int(index) - 1]
        return table_cell

    def get_cell_by_locator(self, locator: str) -> int:
        rows = self.get_all_rows()
        for i, r in enumerate(rows):  # pylint: disable=unused-variable
            cells = self.get_cells_from_row(r)
            for index, c in enumerate(cells):
                cell_text = ""
                if c.text:
                    cell_text += c.text
                elif javascript.execute_javascript(
                        'return arguments[0].querySelector("input, textarea")', c):
                    value = javascript.execute_javascript('return arguments[0].value', c)
                    if value:
                        cell_text += str(value)
                if locator in cell_text:
                    return index + 1
        raise QWebValueError('Matching table cell not found for locator {}.'.format(locator))

    def get_row(self, locator: str, anchor: str, row_index: bool = False, **kwargs
                ) -> Union[WebElement, int]:
        skip_header = util.par2bool(kwargs.get('skip_header', False))
        rows = self.get_all_rows()
        if locator.startswith('//last'):
            if skip_header:
                return len(rows) - 1
            return len(rows)
        matches, index = self._get_row_by_locator_text(rows, locator, anchor)
        if row_index:
            if skip_header:
                return index
            return index + 1
        if matches:
            return matches
        raise QWebValueError('Matching table row not found for locator {}.'.format(locator))

    def get_all_rows(self) -> list[WebElement]:
        return javascript.execute_javascript('return arguments[0].rows', self.table)

    @staticmethod
    def get_cells_from_row(row: WebElement) -> list[WebElement]:
        return javascript.execute_javascript('return arguments[0].cells', row)

    @staticmethod
    def _get_row_by_locator_text(rows: list[WebElement], locator: str,
                                 anchor: Union[str, int]) -> tuple[WebElement, int]:
        matches = []
        input_elements = []
        row_index = []
        anchor_text = ""
        try:
            anchor = int(anchor) - 1
        except ValueError:
            anchor_text = str(anchor)
        for index, row in enumerate(rows):
            row_content = row.text
            if locator == 'EMPTY' and row_content.strip() == '':
                return row, index
            input_elements = javascript.execute_javascript(
                'return arguments[0].querySelectorAll("input, textarea")', row)
            for elem in input_elements:
                row_content += str(javascript.execute_javascript('return arguments[0].value', elem))
            if locator in row_content:
                if anchor_text and anchor_text in row_content:
                    return row, index
                row_index.append(index)
                matches.append(row)
        if matches and not anchor_text:
            return matches[int(anchor)], row_index[int(anchor)]
        raise QWebElementNotFoundError('Row that includes texts {} and {} not found'.format(
            locator, anchor_text))

    def _convert_coordinates(self, coordinate_str: str) -> tuple[Optional[int], Optional[int]]:
        """Return row and column from coordinate string."""
        try:
            row = int(re.findall('r([+-]?[0-9]+)', coordinate_str)[0])
            if row < 0:
                last_row = self.get_row('//last', self.anchor)
                if isinstance(last_row, int):
                    row = last_row + (row + 1)
        except IndexError:
            row = None
        try:
            col = int(re.findall('c([+-]?[0-9]+)', coordinate_str)[0])
            if col < 0:
                row_index = row - 1  # type: ignore[operator]
                col = int(
                    javascript.execute_javascript(
                        ' return arguments[0].rows[{0}].cells.length'.format(row_index),
                        self.table)) + (col + 1)
        except IndexError:
            col = None
        return row, col

    @staticmethod
    def get_table_element_by_css(locator: str, anchor: Union[str, int]) -> Optional[WebElement]:
        table_element = javascript.execute_javascript(
            'return document.querySelectorAll(\'table[summary^="{0}"], '
            'table[name^="{0}"], table[title^="{0}"], th[title^="{0}"], '
            'tr[title^="{0}"], td[title^="{0}"]\')'.format(locator))
        if table_element:
            try:
                anchor = int(anchor) - 1
                if table_element[int(anchor)].tag_name == 'table':
                    return table_element[int(anchor)]
                table_element = javascript.execute_javascript(
                    'return arguments[0].closest("table")', table_element[anchor])
                return table_element
            except (ValueError, TypeError):
                raise IndexError(  # pylint: disable=W0707
                    'Element found by it\'s attribute. When using CSS Selectors'
                    ' for finding table, anchor has to be index when anchor is not '
                    'related to separate locator element')
            except StaleElementReferenceException:
                logger.debug('Staling element..Retrying')
                return None
        try:
            locator_element = text.get_text_using_anchor(locator, str(anchor))
            table_element = javascript.execute_javascript('return arguments[0].closest("table")',
                                                          locator_element)
        except (ValueError, NoSuchElementException, StaleElementReferenceException):
            return None
        if table_element:
            return table_element
        return None

    @staticmethod
    def _get_all_table_elements() -> list[WebElement]:
        return element.get_webelements_in_active_area('//table')

    @staticmethod
    def is_table_coordinates(locator: str) -> bool:
        if '/' in locator:
            parts = locator.split('/')
            if parts[0].startswith('r') and parts[1].startswith('c'):
                return True
        elif fnmatch.fnmatch(locator, "r[-0-9]*c[-0-9]*"):
            return True
        return False

    def update_table(self) -> Table:
        table = self.from_table_instance(self.locator, self.anchor, self.parent, self.child,
                                         self.level, self.index)
        return table
