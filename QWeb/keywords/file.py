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
from pathlib import Path

from QWeb.internal.file import File
from QWeb.internal import download
from QWeb.internal.exceptions import QWebInstanceDoesNotExistError, QWebValueMismatchError, \
    QWebUnexpectedConditionError, QWebValueError, QWebFileNotFoundError
from zipfile import ZipFile
from os.path import basename as _basename
import os
import shutil
from robot.api import logger
from robot.api.deco import keyword

ACTIVE_FILE: File = None  # type: ignore[assignment]


@keyword(tags=["File"])
def use_pdf(filename: str) -> None:
    r"""Define pdf file for all other pdf keywords.

    Sets active file for other keywords.

    Examples
    --------
    .. code-block:: robotframework

        UsePdf            foobar.pdf
        UsePdf            some/existing/path/file.pdf

    Parameters
    ----------
    filename : str
        Default folders = users/downloads, project_dir/files or ${EXECDIR}/\*\*/files.
        Path is not needed if file is in default folder.

    Related keywords
    ----------------
    \`GetPdfText\`, \`RemovePdf\`, \`UseFile\`, \`VerifyPdfText\`
    """
    global ACTIVE_FILE  # pylint:disable=global-statement
    ACTIVE_FILE = File.create_pdf_instance(filename)


@keyword(tags=["File"])
def use_file(filename: str) -> None:
    r"""Define text file for all other file keywords.

    Sets active file for other keywords.

    Examples
    --------
    .. code-block:: robotframework

        UseFile            foobar..txt
        UseFile            some/existing/path/file.txt

    Parameters
    ----------
    filename : str
        Default folders = users/downloads, project_dir/files or ${EXECDIR}/\*\*/files.
        Path is not needed if file is in default folder.

    Related keywords
    ----------------
    \`GetFileText\`, \`RemoveFile\`, \`SaveFile\`, \`UploadFile\`,
    \`VerifyAll\`, \`VerifyFileDownload\`, \`VerifyFileText\`
    """
    global ACTIVE_FILE  # pylint:disable=global-statement
    ACTIVE_FILE = File.create_text_file_instance(filename)


@keyword(tags=("File", "Getters"))
def get_pdf_text(**kwargs) -> str:
    r"""Get text from pdf file.

    Examples
    --------
    .. code-block:: robotframework

        ${text}    GetPdfText    #returns whole content
        ${text}    GetPdfText    locator=xyz   chars=10  #returns 10 chars, starting from text xyz.

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

    Note that you must use named arguments with this keyword, i.e. use
    ``argument_name=value`` format!

    Related keywords
    ----------------
    \`RemovePdf\`, \`UsePdf\`, \`VerifyPdfText\`
    """
    _file_exists()
    return str(ACTIVE_FILE.get(**kwargs))


@keyword(tags=("File", "Getters"))
def get_file_text(**kwargs) -> str:
    r"""Get text from pdf file.

    Examples
    --------
    .. code-block:: robotframework

        ${text}    GetFileText    #returns whole content
        ${text}    GetFileText    xyz   10  #returns 10 chars, starting from text xyz.

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

    Note that you must use named arguments with this keyword, i.e. use
    ``argument_name=value`` format!

    Related keywords
    ----------------
    \`RemoveFile\`, \`UseFile\`, \`VerifyFileText\`
    """
    _file_exists()
    return str(ACTIVE_FILE.get(**kwargs))


@keyword(tags=("File", "Verification"))
def verify_pdf_text(text: str, normalize: bool = False) -> None:
    r"""Verify text from pdf file.

    Examples
    --------
    .. code-block:: robotframework

        VerifyPdfText     Test Automation
        VerifyPdfText     Test Automation    normalize=True

    Parameters
    ----------
    text : str
        Text to verify
    normalize : bool
        Remove extra newlines (\\\\n)

    Related keywords
    ----------------
    \`GetPdfText\`,\`RemovePdf\`, \`UsePdf\`
    """
    _file_exists()
    ACTIVE_FILE.verify(text, normalize)


@keyword(tags=("File", "Verification"))
def verify_file_text(text: str, normalize: bool = False) -> None:
    r"""Verify text from pdf file.

    Examples
    --------
    .. code-block:: robotframework

        VerifyFileText     Test Automation

    Parameters
    ----------
    text : str
        Text to verify
    normalize : bool
        Remove extra newlines (\\\\n)

    Related keywords
    ----------------
    \`GetFileText\`,\`RemoveFile\`, \`UseFile\`
    """
    _file_exists()
    ACTIVE_FILE.verify(text, normalize)


@keyword(tags=("File", "Verification"))
def verify_no_pdf_text(text: str, normalize: bool = False) -> None:
    r"""Verify text not exists in pdf-file.

    Examples
    --------
    .. code-block:: robotframework

        VerifyNoPdfText     Robot

    Parameters
    ----------
    text : str
        Text that should not exist.
    normalize : bool
        Remove extra newlines (\\\\n)

    Related keywords
    ----------------
    \`VerifyPdfText\`,\`VerifyFileText\`
    """
    _file_exists()
    try:
        if ACTIVE_FILE.verify(text, normalize) is True:
            raise QWebUnexpectedConditionError('Text {} exists in pdf file'.format(text))
    except QWebValueMismatchError:
        return


@keyword(tags=("File", "Verification"))
def verify_no_file_text(text: str, normalize: bool = False) -> None:
    r"""Verify text not exists in pdf-file.

    Examples
    --------
    .. code-block:: robotframework

        VerifyNoFileText     Robot

    Parameters
    ----------
    text : str
        Text that should not exist.
    normalize : bool
        Remove extra newline (\\\\n)

    Related keywords
    ----------------
    \`VerifyFileText\`, \`VerifyPdfText\`
    """
    _file_exists()
    try:
        if ACTIVE_FILE.verify(text, normalize) is True:
            raise QWebUnexpectedConditionError('Text {} exists in file'.format(text))
    except QWebValueMismatchError:
        return


@keyword(tags=("File", "Interaction"))
def remove_file(file: Optional[str] = None) -> None:
    r"""Remove a file.

    Examples
    --------
    .. code-block:: robotframework

       UseFile        yoink.pdf
       RemoveFile

       RemoveFile    C:/Users/pace/Desktop/yoink.pdf

    Related keywords
    ----------------
    \`MoveFiles\`, \`RemovePdf\`, \`SaveFile\`, \`VerifyFile\`
    """
    if not file:
        _file_exists()
        ACTIVE_FILE.remove()
    else:
        if os.path.isfile(file):
            os.remove(file)


@keyword(tags=("File", "Interaction"))
def remove_pdf() -> None:
    r"""Remove a file.

    Examples
    --------
    .. code-block:: robotframework

       UseFile        yoink.pdf
       RemoveFile

       RemoveFile    C:/Users/pace/Desktop/yoink.pdf

    Related keywords
    ----------------
    \`MoveFiles\`, \`RemoveFile\`, \`SaveFile\`, \`UsePdf\`
    """
    _file_exists()
    ACTIVE_FILE.remove()


def _file_exists(file_path: Optional[File] = None) -> bool:
    if not file_path:
        if isinstance(ACTIVE_FILE, File) is False:
            raise QWebInstanceDoesNotExistError('File has not been defined with UsePdf keyword')
        return True
    if isinstance(file_path, File) is False:
        raise QWebInstanceDoesNotExistError('Could not locate file {}'.format(file_path))
    return True


@keyword(tags=("File", "Interaction"))
def zip_files(name_of_zip: str, files_to_zip: str) -> None:
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
                file = str(download.get_path(file.strip()))
                if os.path.isdir(file):
                    for root, _, files2 in os.walk(file):
                        for file2 in files2:
                            zipped.write(os.path.join(root, file2))
                else:
                    zipped.write(file, _basename(file))
    except OSError as e:
        raise QWebValueError('\nFile name "{}" contained illegal characters.'
                             '\nError message: {}'.format(name_of_zip, str(e))) from e
    logger.info('Zipped files {} into the file {}'.format(str(files), name_of_zip),
                also_console=True)


@keyword(tags=("File", "Interaction"))
def move_files(files_to_move: str, destination_folder: str) -> None:
    r"""Move files.

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

    Related keywords
    ----------------
    \`RemoveFile\`, \`SaveFile\`, \`UploadFile\`, \`VerifyFile\`
    """
    if not os.path.isdir(destination_folder):
        raise QWebValueError('Destination folder does not exist.')
    files = files_to_move.split(',')
    for file in files:
        file = str(download.get_path(file.strip()))
        shutil.move(file, destination_folder)


@keyword(tags=("File", "Verification"))
def verify_file(filename: str) -> Path:
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
    except QWebFileNotFoundError as e:
        raise QWebFileNotFoundError('File not found from default folders. '
                                    'It may not exists or you may need a full path.') from e
