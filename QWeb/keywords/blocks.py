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
from typing import Any, Union

from robot.api import logger
from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn
from QWeb.internal import decorators, blocks
from QWeb.internal.exceptions import QWebElementNotFoundError, QWebUnexpectedConditionError


@keyword(tags=("Config", "Error handling"))
def run_block(block: str, *args, timeout: Union[int, float, str] = 0, **kwargs) -> None:  # pylint: disable=unused-argument
    r"""Run Action word as decorated block.

    Block (usually set of keywords) is handled as one
    independent action. If any keyword inside of block fails block
    will retry itself until it passes or given time is up. Retrying is
    starting from first line of executable block.

    This feature is meant to be used with RPA-cases where FAIL
    is not an option. Think twice before using with Test Automation
    projects to avoid situations where we have green test even that
    in real life our user interface in SUT might be almost unusable.

    Examples
    --------
    .. code-block:: robotframework

        RunBlock       Poll    timeout=15
        #with arguments:
        RunBlock       Login    ${USER}   ${PASS}   timeout=50
        #with "teardown":
        RunBlock       Login    ${USER}   ${PASS}   timeout=50  exp_handler=RebootBrowser
        #Example blocks:
        POLL
            ClickText   Click Counter
            VerifyText  10 clicks   timeout=1

        # POLL is retried until VerifyText passes (ten times)

        Login
            [Arguments]     ${USER}     ${PASS}
            Goto        https://www.qentinel.com
            TypeText    Username     ${USER}
            TypeText    Password     ${PASS}
            ClickText   Login
            VerifyText  Welcome, ${USER}

        # If for example VerifyText  Welcome, ${USER} fails, RunBlock
        # tries again, starting from first paceword (Goto).

        RebootBrowser
            CloseAllBrowsers
            OpenBrowser     about:blank     chrome

    Parameters
    ----------
    block : str
        Action word/Block to execute
    args : any
        Possible args for block
    timeout : str
        How long we try to get is passed before failing. Default 10 (seconds)
    kwargs: any
        |  Accepted kwargs:
        |       exp_handler : Use any Action Word as a teardown. If
        |       defined, this will be executed after every failed try
        |       before retrying

    Related keywords
    ----------------
    \`Appstate\`, \`SetConfig\`
    """
    step = [{'paceword': block, 'args': args, 'kwargs': {}}]
    _execute_block(step, timeout=timeout, **kwargs)


@keyword(tags=("Config", "Error handling"))
def appstate(block: str, *args) -> None:
    r"""Appstate is a pre-condition of a test case.

    It sets Application(s) under test to correct, known state.
    First keyword of every test case is Appstate.
    It is a navigation system across different states in system under test,
    or between separate applications.
    They are typically set under resources folder, keywords.robot file.

    Examples
    --------
    .. code-block:: robotframework

        Appstate       Login
        #with arguments:
        Appstate       Login    fenix   rising123

        #Example block:
        Login
            [Arguments]     ${USER}=username     ${PASS}=password
            Goto        https://www.qentinel.com
            TypeText    Username     ${USER}
            TypeText    Password     ${PASS}
            ClickText   Login
            VerifyText  Welcome, ${USER}

    Parameters
    ----------
    block : str
        Action word/Block to execute
    args : any
        Possible args for block

    Related keywords
    ----------------
    \`RunBlock\`, \`SetConfig\`
    """
    status, res = BuiltIn().run_keyword_and_ignore_error(block, *args)
    if status == 'FAIL':
        raise QWebUnexpectedConditionError(
            'Unable to set correct pre-condition for test due error: {}'.format(res))


@decorators.timeout_decorator
def _execute_block(steps: list[dict[str, Any]], timeout: Union[int, float, str] = 0, **kwargs):  # pylint: disable=unused-argument
    logger.trace('Timeout for block: {}'.format(timeout))
    logger.trace(steps)
    for step in steps:
        fn = step.get('paceword')
        var_name = step.get('variable', None)
        args = blocks.set_robot_args(*step.get('args', []), **step.get('kwargs', {}))
        status, res = BuiltIn().run_keyword_and_ignore_error(fn, *args)
        logger.trace('status: {}, res: {}'.format(status, res))
        if status == 'FAIL':
            teardown = kwargs.get('exp_handler', None)
            if teardown:
                BuiltIn().run_keyword_and_ignore_error(teardown)
            raise QWebElementNotFoundError('Err from block {}'.format(res))
        if var_name:
            BuiltIn().set_suite_variable('{}'.format(var_name), res)
