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

from typing import Optional

from robot.api import logger
from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn
from QWeb.internal import javascript
from QWeb.internal.exceptions import QWebValueError


@keyword(tags=("Javascript", "Interaction"))
def execute_javascript(script: str, variable_name: Optional[str] = None) -> None:
    """Execute javascript and save the result to suite variable.

    Examples
    --------
    .. code-block:: robotframework

        ExecuteJavascript   document.getElementsByTagName("p")[0].innerText="Write text";
        ExecuteJavascript   return document.title;     $TITLE

    Parameters
    ----------
    script : str
        Javascript code.
    variable_name : str
        Robot framework variable name without {}. (Default None)
    """
    output = javascript.execute_javascript(script)
    logger.info('Output of execution:\n{}'.format(output))
    if variable_name:
        try:
            BuiltIn().set_suite_variable(variable_name, output)
        except Exception as e:
            logger.warn(e.__str__())
            raise QWebValueError("Invalid variable syntax '{}'.".format(variable_name)) from e
