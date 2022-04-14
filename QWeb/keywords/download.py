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
import time

from robot.api import logger
from robot.api.deco import keyword
from robot.utils import timestr_to_secs as _timestr_to_secs

from QWeb.internal import download, frame
from QWeb.internal.config_defaults import CONFIG, SHORT_DELAY


@keyword(tags=("Browser", "Verification"))
def verify_file_download(timeout: Union[int, float, str] = 0) -> str:
    r"""Verify file has been downloaded and return file path.

    Examples
    --------
    .. code-block:: robotframework

        ExpectFileDownload
        ClickText               Download
        VerifyFileDownload      timeout=20s     # file should be downloaded in 20 seconds

    Parameters
    ----------
    timeout : str | int
        Timeout for the download.

    Raises
    ------
    ValueError
        Found more than one file or did not found files at all

    Returns
    -------
    text : downloaded file path

    Related keywords
    ----------------
    \`ExpectFileDownload\`, \`SaveFile\`, \`UploadFile\`
    """
    frame.wait_page_loaded()
    download_dir = download.get_downloads_dir()
    if timeout == 0:
        timeout = CONFIG["DefaultTimeout"]
    timeout_int = _timestr_to_secs(timeout)
    start = time.time()
    previous_message = None
    while time.time() < start + timeout_int:
        modified_files = download.get_modified_files(download_dir, download.start_epoch)
        modified_files = download.remove_win_temp(modified_files)
        if len(modified_files) == 1:
            if not download.is_tmp_file(modified_files[0]):
                logger.info('Found downloaded file {}'.format(modified_files[0]))
                return modified_files[0]
        elif not modified_files:
            message = 'Could not find any modified files'
            if previous_message != message:
                logger.info(message)
                previous_message = message
        else:
            message = 'Modified files\n{}'.format('\n'.join(modified_files))
            if previous_message != message:
                logger.info(message)
                previous_message = message
            if all(not download.is_tmp_file(modified_file) for modified_file in modified_files):
                raise ValueError('Found more than one file that was modified')
        time.sleep(SHORT_DELAY)
    raise ValueError('Could not find any modified files after {}s'.format(timeout_int))


@keyword(tags=("Browser", "Verification"))
def expect_file_download() -> None:
    r"""Turns on polling for time after which file download should happen.

    Run this keyword everytime before \`VerifyFileDownload\` and the action that
    starts download process.

    Examples
    --------
    .. code-block:: robotframework

        ExpectFileDownload
        ClickText               Download
        VerifyFileDownload      timeout=20s     # file should be downloaded in 20 seconds

    Related keywords
    ----------------
    \`SaveFile\`, \`UploadFile\`, \`VerifyFileDownload\`
    """
    now = time.time()
    logger.info('The time has been set to {}'.format(
        time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(now))))
    download.start_epoch = now
