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
from typing import Union

from robot.api.deco import keyword
from QWeb.internal import alert
from QWeb.internal.exceptions import QWebDriverError, QWebValueError


@keyword(tags=("Alert", "Interaction"))
def close_alert(action: str, timeout: Union[int, float, str] = 0) -> None:
    r"""Close popup alert.

    Examples
    --------
    .. code-block:: robotframework

        Close Alert    Accept    10s
        Close Alert    Dismiss
        Close Alert    Nothing

    Parameters
    ----------
    action : str
        What is done for popup. Options are:
        ACCEPT: accept alert
        DISMISS: dismiss alert
        NOTHING: don't close alert

    timeout : str | int
        How long we wait for text to disappear before failing. Default 10 (seconds)

    Related keywords
    ----------------
    \`IsAlert\`, \`TypeAlert\`, \`GetAlertText\`, \`VerifyAlertText\`
    """
    alert_ = alert.wait_alert(timeout=timeout)
    alert.close_alert(alert_, action)


@keyword(tags=("Alert", "Verification"))
def is_alert(timeout: Union[int, float, str] = "0.1s") -> bool:
    r"""Return True/False if alert is found on the screen.

    Used to get alert presence to variable. This keyword returns after alert is found.

    Returns True if alert is found. Returns False if alert is not found within timeout.

    If timeout is not set, keyword returns immediately.

    Examples
    --------
    .. code-block:: robotframework

        IsAlert     2s

    Parameters
    ----------
    timeout : str | int
        How long we wait for text to disappear before failing. Default 10 (seconds)

    Related keywords
    ----------------
    \`CloseAlert\`, \`TypeAlert\`, \`GetAlertText\`, \`VerifyAlertText\`
    """
    try:
        return bool(alert.wait_alert(timeout=timeout))
    except QWebDriverError:
        return False


@keyword(tags=("Alert", "Interaction", "Input"))
def type_alert(text: str, action: str = "Accept", timeout: Union[int, float, str] = 0):
    r"""Type and close popup alert.

    Examples
    --------
    .. code-block:: robotframework

        TypeAlert      Qentinel
        TypeAlert      Qentinel     Nothing   10s

    Parameters
    ----------
    text : str
        Text to type
    action : str (default = Accept)
        What is done for popup. Options are:
        ACCEPT: accept alert
        DISMISS: dismiss alert
        NOTHING: don't close alert
    timeout : str | int
        How long we wait for text to disappear before failing. Default 10 (seconds)

    Related keywords
    ----------------
    \`CloseAlert\`, \`IsAlert\`, \`GetAlertText\`, \`VerifyAlertText\`
    """
    alert_ = alert.wait_alert(timeout=timeout)
    alert.type_alert(alert_, text, timeout=timeout)
    alert.close_alert(alert_, action)


@keyword(tags=("Alert", "Getters"))
def get_alert_text(timeout: Union[int, float, str] = 0) -> str:
    r"""Get alert text to variable.

    Examples
    --------
    .. code-block:: robotframework

        ${TEXT}        GetAlertText

    Parameters
    ----------
    timeout : str | int
        How long we wait for text to disappear before failing. Default 10 (seconds)

    Related keywords
    ----------------
    \`CloseAlert\`, \`IsAlert\`, \`TypeAlert\`, \`VerifyAlertText\`
    """
    alert_ = alert.wait_alert(timeout=timeout)
    return alert_.text


@keyword(tags=("Alert", "Verification"))
def verify_alert_text(text: str, timeout: Union[int, float, str] = 0) -> None:
    r"""Verify alert text.

    Examples
    --------
    .. code-block:: robotframework

        VerifyAlertText     Qentinel

    Parameters
    ----------
    text : str | int
        Text to Verify
    timeout : str | int
        How long we wait for text to disappear before failing. Default 10 (seconds)

    Related keywords
    ----------------
    \`CloseAlert\`, \`GetAlertText\`, \`IsAlert\`, \`TypeAlert\`
    """
    alert_ = alert.wait_alert(timeout=timeout)
    if text in alert_.text:
        return
    raise QWebValueError('Text {} is not presented in Alert'.format(text))
