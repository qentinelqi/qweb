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
"""Keywords for table elements.

Table elements are used to show many kinds of data. Tables have cells in
contain rows and columns. Cells can contain all kinds of elements. Cells
are usually refenced by coordinates or unique neighbouring values.
"""
from typing import Union, List, Optional

from selenium.webdriver.remote.webelement import WebElement
from robot.api.deco import keyword
from QWeb.internal import decorators, actions, util
from QWeb.internal.exceptions import QWebInstanceDoesNotExistError, \
    QWebTimeoutError, QWebValueError, QWebElementNotFoundError
from QWeb.internal.table import Table
from QWeb.internal.config_defaults import CONFIG

ACTIVE_TABLE: Table = None  # type: ignore[assignment]


@keyword(tags=["Tables"])
@decorators.timeout_decorator
def use_table(
        locator: str,
        anchor: str = "1",
        timeout: Union[int, float, str] = 0,  # pylint: disable=unused-argument
        parent: bool = False,
        child: bool = False,
        level: int = 1,
        index: int = 1) -> None:
    r"""Define table for all other table keywords.

    Sets active table for other keywords.

    Examples
    --------
    .. code-block:: robotframework

         UseTable       Calendar    Qentinel
         UseTable       Calendar    parent=True # Use parent table of Calendar
         UseTable       Calendar    child=True  # Use child table of Calendar


    Parameters
    ----------
    locator : str
        Text that locates the table. The table that is closest
        to the text is selected. Also one can use xpath by adding xpath= prefix
        and then the xpath. Error is raised if the xpath matches to multiple
        elements. When using XPaths, the equal sign "=" must be escaped with a "\\".
    anchor : str
        Index number or text near the input field's locator element.
        If the page contains many places where the locator is then anchor is used
        to select the wanted item. Index number selects the item from the list
        of matching entries starting with 1. Text selects the entry with the closest
        distance.
    timeout : str | int
        How long we search before failing. Default = Search Strategy default timeout (10s)
    parent : bool
        Use when correct table is parent of located table
    child : bool
        Use when correct table is child of located table
    level : int
        If wanted parent table is not the first one use level to pick correct one.
        For example level=2 means parent table of parent table etc.
    index : int
        If multiple childtables exists. Use index to pick correct one.

    Related keywords
    ----------------
    \`ClickCell\`, \`GetCellText\`, \`GetTableRow\`, \`VerifyTable\`
    """
    global ACTIVE_TABLE  # pylint:disable=global-statement
    ACTIVE_TABLE = Table.from_table_instance(locator, anchor, parent, child, level, index)


@keyword(tags=("Tables", "Verification"))
@decorators.timeout_decorator
def verify_table(coordinates: str,
                 expected: str,
                 anchor: str = "1",
                 timeout: Union[int, float, str] = 0) -> None:
    r"""Verify text in table coordinates.

    Reads cell value from coordinates in active table and verifies it
    against expected value.

    Examples
    --------
    .. code-block:: robotframework

         VerifyTable            r2c3    Qentinel


    Parameters
    ----------
    coordinates : str
        Row and column coordinates in table. R specifies row and c column.
        Order does not matter.
    expected : str
        Expected value that needs to be found in table.
    anchor : str
        Index number or text near the input field's locator element.
        If the page contains many places where the locator is then anchor is used
        to select the wanted item. Index number selects the item from the list
        of matching entries starting with 1. Text selects the entry with the closest
        distance.
    timeout : str | int
        How long we search before failing. Default = Search Strategy default timeout (10s)

    Raises
    ------
    QWebValueMismatchErr
        If the table is not defined by UseTable keyword

    Related keywords
    ----------------
    \`ClickCell\`, \`GetCellText\`, \`GetTableRow\`, \`UseTable\`
    """
    table = Table.ACTIVE_TABLE.update_table()
    if isinstance(ACTIVE_TABLE, Table) is False:
        raise QWebInstanceDoesNotExistError('Table has not been defined with UseTable keyword')
    table_cell = table.ACTIVE_TABLE.get_table_cell(coordinates, anchor)
    actions.get_element_text(table_cell, expected=expected, timeout=timeout)


@keyword(tags=("Tables", "Getters"))
@decorators.timeout_decorator
def get_cell_text(coordinates: str,
                  anchor: str = "1",
                  timeout: Union[int, float, str] = 0,
                  **kwargs) -> Union[str, int, float]:
    r"""Get cell text to variable.

    Locates cell by coordinates from active table and return value

    Examples
    --------
    .. code-block:: robotframework

        ${value}    GetCellText  r2c3
        ${value}    GetCellText  r-2c5       #Row is second to last. Get value from cell c5
        ${value}    GetCellText  r?Robot/c5  #Row contains text Robot. Get value from cell c5
        ${value}    GetCellText  r?Robot/c-1  #Row contains text Robot. Get value from last cell

    Parameters
    ----------
    coordinates : str
      Row and column coordinates in table. R specifies row and c column.
      r1 = first row, r-1 = last row, r?Qentinel/ = row that contains word Qentinel
    anchor : str
      If row is located by text which is not unique, use anchor to point correct one.
      Anchor can be some other text in same row or index. Default = 1
    timeout : str | int
      How long we search before failing. Default = Search Strategy default timeout (10s)
    kwargs :
        |  Accepted kwargs:
        |       between : str/int - Start???End - Return all chars between texts Start and End.
        |       from_start : int - Return x amount of chars. Starting from first char
        |       from_end : int - Return x amount of chars. Starting from last char
        |       include_locator : True - Starting text is part of returned string
        |       exclude_post : False - Ending text is part of returned string
        |       int : True - Return integer instead of string
        |       float : int - Return float instead of string

    Raises
    ------
    QWebValueError
        If the table is not defined by UseTable keyword

    Related keywords
    ----------------
    \`ClickCell\`, \`GetTableRow\`, \`UseTable\`, \`VerifyTable\`
    """
    table = Table.ACTIVE_TABLE.update_table()
    if isinstance(ACTIVE_TABLE, Table) is False:
        raise QWebInstanceDoesNotExistError('Table has not been defined with UseTable keyword')
    table_cell = table.get_table_cell(coordinates, anchor)
    try:
        text = actions.get_element_text(table_cell, timeout=timeout)
        return util.get_substring(text, **kwargs)
    except QWebTimeoutError:
        return ""


@keyword(tags=("Tables", "Interaction"))
@decorators.timeout_decorator
def click_cell(
        coordinates: str,
        anchor: str = "1",
        timeout: Union[int, float, str] = 0,  # pylint: disable=unused-argument
        index: int = 1,
        **kwargs) -> None:
    r"""Click table cell.

    Locates cell by coordinates or text from active table and clicks it

    Examples
    --------
    .. code-block:: robotframework

       ClickCell    r2c3
       ClickCell    r-1c-1                  #Last row, last cell
       ClickCell    r?SomeText/c3           #Click cell 3 in row that contains text SomeText
       ClickCell    r?Robot/c3      Hello   #Click cell 3 in row with words Robot and Hello in it
       ClickCell    r1c1            tag=a   #Clicks first child element with a tag
       ClickCell    r?Robot/c3      index=2  tag=input  #Clicks the second child element of cell 3

    Parameters
    ----------
    coordinates : str
      Row and column coordinates in table or some text that locates in preferred row.
      R specifies row and c column.
      r1 = first row, r-1 = last row, r?Qentinel/ = row that contains word Qentinel
    anchor : str
      If row is located by text which is not unique, use anchor to point correct one.
      Anchor can be some other text in same row or index. Default = 1
    timeout : str | int
       How long we search before failing. Default = Search Strategy default timeout (10s)
    index : int
       Use index when table cell contains more than one clickable element and preferred one
       is not the first one. Requires the use of tag and value should be > 0, default = 1.

    Raises
    ------
    QWebValueError
       If the table is not defined by UseTable keyword

    Related keywords
    ----------------
    \`GetCellText\`, \`GetTableRow\`, \`UseTable\`, \`VerifyTable\`
    """
    table = Table.ACTIVE_TABLE.update_table()
    if isinstance(ACTIVE_TABLE, Table) is False:
        raise QWebInstanceDoesNotExistError('Table has not been defined with UseTable keyword')
    table_cell = table.get_clickable_cell(coordinates, anchor, index, **kwargs)
    actions.execute_click_and_verify_condition(table_cell, **kwargs)


@keyword(tags=("Tables", "Getters"))
@decorators.timeout_decorator
def get_table_row(
        locator: str,
        anchor: str = "1",
        timeout: Union[int, float, str] = 0,  # pylint: disable=unused-argument
        **kwargs) -> Union[WebElement, int]:
    r"""Get row (index) from current table.

    Get table row by some visible text or value.

    Examples
    --------
    .. code-block:: robotframework

       ${row}       GetTableRow     //last          #returns table length(last row)
       ${row}       GetTableRow     Qentinel        #return first row which contain text Qentinel
       ${row}       GetTableRow     Qentinel    2     #second row with text Qentinel
       ${row}       GetTableRow     Qentinel    Sepi  #row contains texts Qentinel & Sepi
       ${row}       GetTableRow     Qentinel    skip_header=True  #start counting from first tc row

    Parameters
    ----------
    locator : str
      Text or value which is presented in wanted row or //last = last row of the table
    anchor : str
      If locator is not unique use anchor to tell which is correct. Anchor can be some text/value
      in same row than locator text or index. 1=first match etc. Default = 1
    timeout : str | int
       How long we search before failing. Default = Search Strategy default timeout (10s)

    Raises
    ------
    ValueError
       If the table is not defined by UseTable keyword

    Related keywords
    ----------------
    \`ClickCell\`, \`GetCellText\`, \`UseTable\`, \`VerifyTable\`
    """
    table = Table.ACTIVE_TABLE.update_table()
    if isinstance(ACTIVE_TABLE, Table) is False:
        raise QWebInstanceDoesNotExistError('Table has not been defined with UseTable keyword')
    return table.get_row(locator, anchor, row_index=True, **kwargs)


@keyword(tags=("Tables", "Getters"))
def get_col_header_count() -> int:
    r"""Get Count of column headers in current active table.

    Note: only visible columns may be counted in some dynamic tables.

    Examples
    --------
    .. code-block:: robotframework

        UseTable    my_table
        ${count}    GetColHeaderCount

    Raises
    ------
    QWebInstanceDoesNotExistError
       If the table is not defined by UseTable keyword

    Related keywords
    ----------------
    \`GetColHeader\`, \`VerifyColHeader\`, \`UseTable\`, \`VerifyTable\`
    """
    if not isinstance(ACTIVE_TABLE, Table):
        raise QWebInstanceDoesNotExistError('Table has not been defined with UseTable keyword')
    table = Table.ACTIVE_TABLE.update_table()
    return len(table.get_columns())


@keyword(tags=("Tables", "Getters"))
def get_col_header(index: Optional[int] = None) -> Union[str, List[str]]:
    r"""Get column header names/text as a list.

    Note: only visible columns may be counted in some dynamic tables.

    Note2: If column header has attribute 'aria-label', it's value is returned.
    If not and 'title' attirbute exists, then 'title' value is returned.
    If neither aria-label or title exists, then full text of column element is returned.
    This is done due to fact that in many web applications header element text contains other texts
    than what is visible to end users.

    Examples
    --------
    .. code-block:: robotframework

        UseTable    my_table
        # Get all column headers as list
        ${columns}  GetColHeader
        # -> ['col1', 'col2', 'col3']
        # Get column header by index
        ${column_at_index_2}    GetColHeader  2
        # -> 'col2 header'

    Parameters
    ----------
    index : int
      Column index. If given, gets the header text of the given column.
      If not given or if 0 is given, returns all column headers as a list.


    Raises
    ------
    QWebInstanceDoesNotExistError
       If the table is not defined by UseTable keyword.
    QWebElementNotFoundError
        If the given index value is out of range.
    ValueError
        Index argument is not an integer.

    Related keywords
    ----------------
    \`GetColHeaderCount\`, \`VerifyColHeader\`, \`GetColHeader\`, \`UseTable\`, \`VerifyTable\`
    """
    if not isinstance(ACTIVE_TABLE, Table):
        raise QWebInstanceDoesNotExistError('Table has not been defined with UseTable keyword')
    table = Table.ACTIVE_TABLE.update_table()
    columns = table.get_columns()

    column_texts = _get_column_header_texts(columns)

    if not index:
        return column_texts

    if not str(index).isdigit():
        raise QWebValueError('Column index should be a positive integer')

    if len(columns) < index:
        raise QWebValueError(f'Column index out of range: {index=}, {len(columns)=}')

    return column_texts[index - 1]


@keyword(tags=("Tables", "Verification"))
def verify_col_header(expected: str,
                      index: Optional[int] = None,
                      **kwargs) -> bool:
    r"""Verifies that a column header with given index matches the expected text.

    Note: only visible columns may be counted in some dynamic tables.

    Note2: If column header has attribute 'aria-label', it's value is considered as expected value.
    If not and 'title' attirbute exists, then title is considered as expected value.
    If neither aria-label or title exists, then column text is considered as expected value.
    This is done due to fact that in many web applications header element text contains other texts
    than what is visible to end users.

    Examples
    --------
    .. code-block:: robotframework

        # Verifies that second column's text is Year
        UseTable    my_table
        # Verifies that table includes column "Year" at any position
        VerifyColHeader    Year
        VerifyColHeader    Year    0  # 0 = any column
        # Verifies that table includes column "Year" at position 2
        VerifyColHeader    Year    2
        VerifyColHeader    Year    index=2

    Parameters
    ----------
    expected : str
      Text or value which should be in the column
    index : int
      Column index. If given, expected text is verified against the given column.
      If not given or if 0 is given, expected text is verified against any column
      (i.e. column text must exist at any position)
    Accepted kwargs:
        partial_match: Allow partial match of expected text. Defaults to True unless default value
        has been changed with SetConfig    PartialMatch

    Raises
    ------
    QWebInstanceDoesNotExistError
       If the table is not defined by UseTable keyword
    QWebValueError
        If the given index value is out of range
    ValueError
        Index argument is not an integer.
    QWebElementNotFoundError
        If the expected text does not match the actual column text


    Related keywords
    ----------------
    \`GetColHeaderCount\`, \`GetColHeader\`, \`UseTable\`, \`VerifyTable\`
    """
    if not isinstance(ACTIVE_TABLE, Table):
        raise QWebInstanceDoesNotExistError('Table has not been defined with UseTable keyword')
    table = Table.ACTIVE_TABLE.update_table()
    columns = table.get_columns()
    column_texts = _get_column_header_texts(columns)
    partial = kwargs.get('partial_match', CONFIG['PartialMatch'])

    # If index is not specified, verify that the expected text is in any column
    if not index:
        # accept partial match
        if util.par2bool(partial):
            found = found = any(expected in c for c in column_texts)
        # full match
        else:
            found = expected in column_texts
        if found:
            return True

        raise QWebElementNotFoundError(f'Column text "{expected}" does not exist.')

    if not str(index).isdigit():
        raise QWebValueError('Column index should be a positive integer')

    if len(columns) < index:
        raise QWebValueError(f'Column index out of range: {index=}, {len(columns)=}')

    actual = column_texts[index - 1]
    # accept partial match
    if util.par2bool(partial) and expected in actual:
        return True

    # full match
    if actual == expected:
        return True

    raise QWebElementNotFoundError(f'Column "{index}" "{actual}" does not match "{expected}".')


def _get_column_header_texts(columns: List[WebElement]) -> List[str]:
    # prefer using title, then aria-label, then text
    column_texts = [
        c.get_attribute("title")
        or c.get_attribute("aria-label")
        or c.text
        for c in columns
    ]

    return column_texts
