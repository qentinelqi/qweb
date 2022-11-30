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

import os
from pathlib import Path
import re
import time
from robot.libraries.BuiltIn import BuiltIn
from robot.api import logger
from selenium import webdriver

from QWeb.internal import browser, platform
from QWeb.internal.exceptions import QWebFileNotFoundError

start_epoch: float


def get_downloads_dir() -> str:
    """Get downloads directory.

    Assuming downloads directory is in the home directory of the current user.

    Returns
    -------
    str
        Downloads directory's path.
    """
    home_dir = platform.get_home_dir()
    download_dir = Path(home_dir) / 'Downloads'
    logger.debug('Downloads directory is {}'.format(download_dir))
    return str(download_dir)


def get_modified_files(directory: str, epoch: float) -> list[str]:
    """Get modified files in directory that were modified after given epoch.

    Parameters
    ----------
    directory : str
        Directory that is inspected.
    epoch : float
        Get files that were modified after this epoch.

    Returns
    -------
    list
        List of str filepaths.
    """
    modified_files = []
    try:
        filenamelist = os.listdir(directory)
    except IOError:
        return []
    for filename in filenamelist:
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            modification_epoch = os.path.getmtime(filepath)
            if modification_epoch > epoch:
                modified_files.append(filepath)
    epoch_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epoch))
    logger.debug('Files that were altered after {} were {}'.format(epoch_str, modified_files))
    return modified_files


def remove_win_temp(modified_files: list[str]) -> list[str]:
    """Remove Windows temporary files from modified files list
    """
    exp = '.{8}-.{4}-.{4}-.{4}-.{12}\\.tmp'
    for f in modified_files:
        if len(re.findall(exp, f)) == 1:
            logger.debug('Removing Windows temp file: {}'.format(f))
            modified_files.remove(f)
    return modified_files


def is_tmp_file(filepath: str) -> bool:
    """Is downloaded file a temporary file.

    When a file is being downloaded at least some browsers download it to a
    different name. When the file has been fully downloaded the file is renamed
    to the correct one.

    Parameters
    ----------
    filepath : str

    Returns
    -------
    bool
    """
    driver = browser.get_current_browser()
    if isinstance(driver, webdriver.Chrome):
        partial_download_suffix = 'crdownload'
    elif isinstance(driver, webdriver.Firefox):
        partial_download_suffix = '.part'
    elif isinstance(driver, webdriver.Edge):
        partial_download_suffix = 'crdownload'
    else:
        raise ValueError('Unknown browser {}'.format(driver.name))
    return filepath.endswith(partial_download_suffix)


def get_path(filename: str) -> Path:
    if Path(filename).exists():
        return Path(filename)
    files = Path(BuiltIn().get_variable_value('${SUITE SOURCE}')).parent.parent / 'files' / filename
    images = Path(
        BuiltIn().get_variable_value('${SUITE SOURCE}')).parent.parent / 'images' / filename
    downloads = Path(get_downloads_dir()) / filename
    exec_dir = BuiltIn().get_variable_value('${EXECDIR}')
    files_exec_dir = Path(f"{get_exec_subdir(exec_dir, 'files')}/{filename}")
    images_exec_dir = Path(f"{get_exec_subdir(exec_dir, 'images')}/{filename}")
    paths = [downloads, files, images, files_exec_dir, images_exec_dir]

    for path in paths:
        logger.debug(path)
        if path.exists():
            logger.debug(f"Path exists: {path}")
            return path
    try:
        base_path = BuiltIn().get_variable_value('${base_image_path}')
        full_path = os.path.join(base_path, "{}".format(filename.lower()))
        return Path(full_path)
    except TypeError as e:
        raise QWebFileNotFoundError(
            'File not found from default folders. Set variable for base image path') from e


def get_exec_subdir(base_path: str, target_dir: str) -> str:
    """Finds a "special" subdirectory under execution dir.

    Returns full path to special dir if found.
    Returns base_path if special dir is not found.

    Parameters
    ----------
    base_path : str
    target_dir: str

    Returns
    -------
    str
    """
    # pylint: disable=unused-variable
    d = None
    for root, dirs, files in os.walk(base_path):
        for d in dirs:
            if d.lower() == target_dir:
                return os.path.join(root, d)

    return os.path.join(base_path, target_dir)
