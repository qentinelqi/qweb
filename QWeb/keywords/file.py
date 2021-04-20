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

from QWeb.internal.file import File
from QWeb.internal import download
from QWeb.internal.exceptions import QWebInstanceDoesNotExistError, QWebValueMismatchError,\
    QWebUnexpectedConditionError, QWebValueError, QWebFileNotFoundError
from zipfile import ZipFile
from os.path import basename
import os
import shutil
from robot.api import logger

ACTIVE_FILE = None


def use_pdf(filename):
    """Define pdf file for all other pdf keywords.

    Sets active file for other keywords.

    Examples
    --------
    .. code-block:: robotframework

        UsePdf            foobar.pdf
        UsePdf            some/existing/path/file.pdf

    Parameters
    ----------
    filename : str
        Default folders = users/downloads and project_dir/files.
        Path is not needed if file is in default folder.
    """
    global ACTIVE_FILE  # pylint:disable=global-statement
    ACTIVE_FILE = File.create_pdf_instance(filename)


def use_file(filename):
    """Define text file for all other file keywords.

    Sets active file for other keywords.

    Examples
    --------
    .. code-block:: robotframework

        UsePdf            foobar..txt
        UsePdf            some/existing/path/file.txt

    Parameters
    ----------
    filename : str
        Default folders = users/downloads and project_dir/files.
        Path is not needed if file is in default folder.
    """
    global ACTIVE_FILE  # pylint:disable=global-statement
    ACTIVE_FILE = File.create_text_file_instance(filename)


def get_pdf_text(**kwargs):
    """Get text from pdf file.

    Examples
    --------
    .. code-block:: robotframework

        ${text}      GetPdfText     #returns whole content
        ${text}      GetPdfText     xyz   10  #returns 10 chars. Starting from text xyz.

    Parameters
    ----------
    locator : str
        Starting point for substring (Locator text is returned by default)
    post_text : str
        Ending point for substring (post_text is not returned by default)
    chars : int
        length of wanted string
    include_locator : bool
        if set to False returns chars after locator text.
    exclude_post : bool
        if set to False returned string includes post_text
    """
    _file_exists()
    return ACTIVE_FILE.get(**kwargs)


def get_file_text(**kwargs):
    """Get text from pdf file.

    Examples
    --------
    .. code-block:: robotframework

        ${text}      GetFileText     #returns whole content
        ${text}      GetFileText     xyz   10  #returns 10 chars. Starting from text xyz.

    Parameters
    ----------
    locator : str
        Starting point for substring (Locator text is returned by default)
    post_text : str
        Ending point for substring (post_text is not returned by default)
    chars : int
        length of wanted string
    include_locator : bool
        if set to False returns chars after locator text.
    exclude_post : bool
        if set to False returned string includes post_text
    """
    _file_exists()
    return ACTIVE_FILE.get(**kwargs)


def verify_pdf_text(text, normalize=False):
    """Verify text from pdf file.

    Examples
    --------
    .. code-block:: robotframework

        VerifyPdfText     Test Automation

    Parameters
    ----------
    text : str
        Text to verify
    normalize : bool
        Remove extra newlines (\\n)
    """
    _file_exists()
    ACTIVE_FILE.verify(text, normalize)


def verify_file_text(text, normalize=False):
    """Verify text from pdf file.

    Examples
    --------
    .. code-block:: robotframework

        VerifyPdfText     Test Automation

    Parameters
    ----------
    text : str
        Text to verify
    normalize : bool
        Remove extra newlines (\\n)
    """
    _file_exists()
    ACTIVE_FILE.verify(text, normalize)


def verify_no_pdf_text(text, normalize=False):
    """Verify text not exists in pdf-file.

    Examples
    --------
    .. code-block:: robotframework

        VerifyNoPdfText     Robot

    Parameters
    ----------
    text : str
        Text that should not exist.
    normalize : bool
        Remove extra newlines (\\n)
    """
    _file_exists()
    try:
        if ACTIVE_FILE.verify(text, normalize) is True:
            raise QWebUnexpectedConditionError('Text {} exists in pdf file'.format(text))
    except QWebValueMismatchError:
        return


def verify_no_file_text(text, normalize=False):
    """Verify text not exists in pdf-file.

    Examples
    --------
    .. code-block:: robotframework

        VerifyNoFileText     Robot

    Parameters
    ----------
    text : str
        Text that should not exist.
    normalize : bool
        Remove extra newline (\\n)
    """
    _file_exists()
    try:
        if ACTIVE_FILE.verify(text, normalize) is True:
            raise QWebUnexpectedConditionError('Text {} exists in file'.format(text))
    except QWebValueMismatchError:
        return


def remove_file(file=None):
    """Remove a file.

    Examples
    --------
    .. code-block:: robotframework

       UseFile        yoink.pdf
       RemoveFile

       RemoveFile    C:/Users/pace/Desktop/yoink.pdf
    """
    if not file:
        _file_exists()
        ACTIVE_FILE.remove()
    else:
        if os.path.isfile(file):
            os.remove(file)


def remove_pdf():
    """Remove a file.

    Examples
    --------
    .. code-block:: robotframework

       UseFile        yoink.pdf
       RemoveFile

       RemoveFile    C:/Users/pace/Desktop/yoink.pdf
    """
    _file_exists()
    ACTIVE_FILE.remove()


def _file_exists(file_path=None):
    if not file_path:
        if isinstance(ACTIVE_FILE, File) is False:
            raise QWebInstanceDoesNotExistError('File has not been defined with UsePdf keyword')
        return True
    if isinstance(file_path, File) is False:
        raise QWebInstanceDoesNotExistError('Could not locate file {}'.format(file_path))
    return True


def zip_files(name_of_zip, files_to_zip):
    """Zip files.

    Examples
    --------
    .. code-block:: robotframework

       ZipFiles           my_zip_file      rabbit.txt
       ZipFiles           my_zip_file_2    dog.txt
       ZipFiles           my_zip_file_3    rabbit.txt, dog.txt
       ZipFiles           my_zip_file_4    C:/Users/pace/secrets/cat.txt
       ZipFiles           my_zip_file_5    C:/Users/pace/secrets/cat.txt, C:/automation/kangaroo.txt

    Parameters
    ----------
    name_of_zip : str
        Name of the zip file created.
    files_to_zip : str
        Files to be zipped, separated by "," in case of multiple files.
    """
    if not name_of_zip.endswith('.zip'):
        name_of_zip += '.zip'
    files = files_to_zip.split(',')
    try:
        with ZipFile(name_of_zip, 'w') as zipped:
            for file in files:
                file = download.get_path(file.strip())
                if os.path.isdir(file):
                    for root, _, files2 in os.walk(file):
                        for file2 in files2:
                            zipped.write(os.path.join(root, file2))
                else:
                    zipped.write(file, basename(file))
    except OSError as e:
        raise QWebValueError('\nFile name "{}" contained illegal characters.'
                             '\nError message: {}'.format(name_of_zip, str(e)))
    logger.info('Zipped files {} into the file {}'
                .format(str(files), name_of_zip), also_console=True)


def move_files(files_to_move, destination_folder):
    """Move files.

    Examples
    --------
    .. code-block:: robotframework

       MoveFiles           cat1.jpg      C:/secret_cat_pictures
       MoveFiles           cat1.jpg, cat666.jpg, cat4.jpg      C:/secret_cat_pictures

    Parameters
    ----------
    files_to_move : str
        Files to move, separated by "," in case of multiple files.
    destination_folder : str
        Destination folder of the moved files.
    """
    if not os.path.isdir(destination_folder):
        raise QWebValueError('Destination folder does not exist.')
    files = files_to_move.split(',')
    for file in files:
        file = str(download.get_path(file.strip()))
        shutil.move(file, destination_folder)


def verify_file(filename):
    """Verify file exists.

    If reference file are not in default folders (images, files, downloads) then
    path should be defined. Returns path.

    Examples
    --------
    .. code-block:: robotframework

       VerifyFile          cat1.jpg
       VerifyFile          C:/this/is/path/to/cat1.jpg
       ${path}             VerifyFile          dog.jpg

    Parameters
    ----------
    filename : str
        Filename or path to find.
    """
    try:
        path = download.get_path(filename)
        logger.info('File found. Filepath is {}'.format(path))
        return path
    except QWebFileNotFoundError:
        raise QWebFileNotFoundError(
            'File not found from default folders. It\'s not exists or you may need a full path.')
